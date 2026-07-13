"""Run legacy engines + LexWarrant against a class workspace."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path
from typing import Any, Optional

from .compile_specs import write_specs
from .settings import load_config, path_from_config
from .workspace import ClassWorkspace


def _ensure_legacy_paths() -> dict[str, Path]:
    cfg = load_config()
    paths = {
        "pulo_engine": Path(cfg["pulo_engine_dir"]),
        "onto_engine": Path(cfg["onto_engine_dir"]),
        "lexwarrant": Path(cfg["lexwarrant_dir"]),
        "pulo_sqlite": Path(cfg["pulo_sqlite"]),
        "onto_sqlite": Path(cfg["onto_sqlite"]),
    }
    for key in ("pulo_engine", "onto_engine", "lexwarrant"):
        if not paths[key].exists():
            raise FileNotFoundError(f"Legacy path missing ({key}): {paths[key]}")
    return paths


def _import_legacy(paths: dict[str, Path]):
    for d in (paths["pulo_engine"], paths["onto_engine"], paths["lexwarrant"]):
        s = str(d)
        if s not in sys.path:
            sys.path.insert(0, s)
    import phase0_pulo  # type: ignore
    import phase0_skos  # type: ignore
    import lexwarrant  # type: ignore
    return phase0_pulo, phase0_skos, lexwarrant


def _best_pulo_export(ws: ClassWorkspace) -> Optional[Path]:
    candidates = sorted(ws.exports.glob("*pulo*.json")) + sorted(
        ws.exports.glob("*.json")
    )
    for p in candidates:
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if obj.get("type") == "pulo_thesaurus_search":
            return p
    return None


def _relabel_result(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def _sideline_pulo_signals(result_path: Path, out_dir: Path) -> Path:
    """Copy a PULO result with sinalizacao moved aside (keeps concordance readable).

    PULO harvests unnamed relations (#NN) and off-axis similar-to into
    ``sinalizacao`` (~dozens of noise terms). LexWarrant lists them all.
    For daily work we park them in ``out/<class>.PULO.signals.json`` and
    merge a cleaned copy so the main concordance stays short.
    """
    data = json.loads(result_path.read_text(encoding="utf-8"))
    signals = data.get("sinalizacao") or {}
    class_id = data.get("class_id") or result_path.stem.split(".")[0]
    if signals:
        side = out_dir / f"{class_id}.PULO.signals.json"
        side.write_text(
            json.dumps(
                {
                    "class_id": class_id,
                    "count": len(signals),
                    "note": (
                        "PULO relation harvest (unnamed #NN / similar-to off-axis). "
                        "Not decisions — review only if something looks useful; "
                        "otherwise ignore."
                    ),
                    "sinalizacao": signals,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        # human-readable short list
        lines = [
            f"# PULO signals sidelined — {class_id}",
            "",
            f"{len(signals)} auto-harvested terms (not your UF/RT choices).",
            "Ignore by default. Full JSON: "
            f"`{class_id}.PULO.signals.json`.",
            "",
            "| term | reason |",
            "|---|---|",
        ]
        for key, info in sorted(signals.items(), key=lambda kv: kv[1].get("display") or kv[0]):
            term = info.get("display") or key
            reason = info.get("reason") or ""
            lines.append(f"| {term} | {reason} |")
        (out_dir / f"{class_id}.PULO.signals.md").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
    clean = dict(data)
    clean["sinalizacao"] = {}
    clean["_signals_sidelined"] = len(signals)
    clean_path = result_path.with_name(result_path.stem + ".for_merge.json")
    clean_path.write_text(
        json.dumps(clean, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return clean_path


def run_class(class_id: str, policy: Optional[str] = None,
              engines: Optional[list[str]] = None,
              hide_pulo_signals: bool = True) -> dict[str, Any]:
    """Compile specs → run engines → LexWarrant merge. Returns summary dict."""
    ws = ClassWorkspace.open(class_id)
    ws.ensure()
    cfg = load_config()
    policy = policy or cfg.get("default_policy") or "conservative"
    if "hide_pulo_signals" in cfg:
        hide_pulo_signals = bool(cfg["hide_pulo_signals"])
    engines = engines or ["pulo", "onto"]
    paths = _ensure_legacy_paths()
    phase0_pulo, phase0_skos, lexwarrant = _import_legacy(paths)

    spec_paths = write_specs(ws)
    summary: dict[str, Any] = {
        "class_id": ws.class_id,
        "specs": {k: str(v) for k, v in spec_paths.items()},
        "results": {},
        "errors": [],
    }

    # --- PULO ---
    if "pulo" in engines and "pulo" in spec_paths:
        export = _best_pulo_export(ws)
        if export is None:
            summary["errors"].append(
                "PULO: no exports/*pulo*.json — search in the workbench first."
            )
        else:
            tmp_out = ws.results / "_pulo_run"
            if tmp_out.exists():
                shutil.rmtree(tmp_out)
            tmp_out.mkdir(parents=True, exist_ok=True)
            try:
                result = phase0_pulo.run_spec(
                    spec_paths["pulo"], tmp_out, export_path=export
                )
                produced = tmp_out / f"{ws.class_id}.result.json"
                dest = ws.results / f"{ws.class_id}.PULO.result.json"
                if produced.exists():
                    _relabel_result(produced, dest)
                    # also copy report/ttl
                    for suf in (".report.md", ".skos.ttl", ".whitelist.json"):
                        src = tmp_out / f"{ws.class_id}{suf}"
                        if src.exists():
                            shutil.copy2(src, ws.results / f"{ws.class_id}.PULO{suf}")
                    summary["results"]["PULO"] = str(dest)
                    summary["pulo_passed"] = bool(result.get("all_passed"))
                    n_sig = len((result.get("sinalizacao") or {}))
                    if n_sig:
                        summary["pulo_signals"] = n_sig
                else:
                    summary["errors"].append("PULO engine produced no result.json")
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(f"PULO engine: {exc}")

    # --- ONTO ---
    if "onto" in engines and "onto" in spec_paths:
        if not paths["onto_sqlite"].exists():
            summary["errors"].append(f"ONTO sqlite missing: {paths['onto_sqlite']}")
        else:
            tmp_out = ws.results / "_onto_run"
            if tmp_out.exists():
                shutil.rmtree(tmp_out)
            tmp_out.mkdir(parents=True, exist_ok=True)
            try:
                result = phase0_skos.run_spec(
                    spec_paths["onto"], paths["onto_sqlite"], tmp_out
                )
                produced = tmp_out / f"{ws.class_id}.result.json"
                dest = ws.results / f"{ws.class_id}.ONTO.result.json"
                if produced.exists():
                    _relabel_result(produced, dest)
                    for suf in (".report.md", ".skos.ttl", ".whitelist.json"):
                        src = tmp_out / f"{ws.class_id}{suf}"
                        if src.exists():
                            shutil.copy2(src, ws.results / f"{ws.class_id}.ONTO{suf}")
                    summary["results"]["ONTO"] = str(dest)
                    summary["onto_passed"] = bool(result.get("all_passed", True))
                else:
                    summary["errors"].append("ONTO engine produced no result.json")
            except Exception as exc:  # noqa: BLE001
                summary["errors"].append(f"ONTO engine: {exc}")

    # --- WordNet (faixa de corroboração; regenerada se houver facets + tabela) ---
    try:
        from .wordnet_track import build_wordnet_result
        wn_res = build_wordnet_result(ws.class_id)
        if wn_res.get("ok"):
            summary["wordnet_track"] = {
                "path": wn_res["path"], "convoked": wn_res["convoked"],
                "skipped": wn_res["skipped"],
                "n_sinalizacao": wn_res["n_sinalizacao"]}
        else:
            summary["wordnet_track"] = {"skipped_because": wn_res.get("error")}
    except Exception as exc:  # noqa: BLE001
        summary["errors"].append(f"WordNet track: {exc}")

    # --- Merge ---
    inputs = []
    pulo_r = ws.results / f"{ws.class_id}.PULO.result.json"
    onto_r = ws.results / f"{ws.class_id}.ONTO.result.json"
    wn_r = ws.results / f"{ws.class_id}.WordNet.result.json"
    if pulo_r.exists():
        if hide_pulo_signals:
            data = json.loads(pulo_r.read_text(encoding="utf-8"))
            n_sig = len(data.get("sinalizacao") or {})
            summary["pulo_signals"] = n_sig
            merge_pulo = _sideline_pulo_signals(pulo_r, ws.out)
            summary["pulo_signals_file"] = str(
                ws.out / f"{ws.class_id}.PULO.signals.md"
            )
            inputs.append(("PULO", merge_pulo))
        else:
            inputs.append(("PULO", pulo_r))
    if onto_r.exists():
        inputs.append(("ONTO", onto_r))
    if wn_r.exists():
        inputs.append(("WordNet", wn_r))

    if len(inputs) >= 2:
        try:
            import contextlib
            import io
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                doc = lexwarrant.run_report(inputs, ws.out, policy=policy)
            published = ws.publish_final_results(
                Path(doc["_md_path"]), Path(doc["_json_path"])
            )
            summary["concordance_md"] = published["md"]
            summary["concordance_json"] = published["json"]
            summary["final_results"] = published["folder"]
            summary["merge_ok"] = True
            note_bits = [
                f"FINAL RESULTS → {published['folder']}",
                "(Onto.PT + PULO concordance deliverable)",
            ]
            if hide_pulo_signals and summary.get("pulo_signals"):
                note_bits.append(
                    f"{summary['pulo_signals']} PULO signals sidelined in out/"
                )
            summary["note"] = " · ".join(note_bits)
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"LexWarrant: {exc}")
            summary["merge_ok"] = False
    elif len(inputs) == 1:
        summary["errors"].append(
            "Only one result.json — LexWarrant needs ≥2 sources. "
            "Mark senses in both PULO and ONTO, or import a second result."
        )
        summary["merge_ok"] = False
    else:
        summary["errors"].append("No engine results to merge.")
        summary["merge_ok"] = False

    summary["status"] = ws.status()
    return summary


def search_and_seed(class_id: str, query: str, source: str = "pulo",
                    mode: str = "Starts with", pos: Optional[str] = None,
                    limit: int = 80) -> dict:
    """Search lexicon, save export, seed undecided sense cards."""
    from .adapters import OntoStore, PuloStore
    from . import decisions as decmod

    ws = ClassWorkspace.open(class_id)
    ws.ensure()
    cfg = load_config()
    source = source.lower()
    if source == "pulo":
        store = PuloStore(Path(cfg["pulo_sqlite"]))
        export = store.export_search(query, pos=pos, mode=mode, limit=limit)
        store.close()
        fname = f"pulo_{query.strip().replace(' ', '_')}.json"
    elif source == "onto":
        store = OntoStore(Path(cfg["onto_sqlite"]))
        # Onto is dense — keep the workbench readable
        export = store.export_search(
            query, pos=pos, mode=mode, limit=min(limit, 40)
        )
        store.close()
        fname = f"onto_{query.strip().replace(' ', '_')}.json"
    else:
        raise ValueError("source must be 'pulo' or 'onto'")

    out_path = ws.exports / fname
    out_path.write_text(
        json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    existing = decmod.load_decisions(ws.decisions_json)
    existing["class_id"] = ws.class_id
    if source == "pulo":
        updated = decmod.from_pulo_export(export, existing)
    else:
        updated = decmod.from_onto_export(export, existing)
    decmod.save_decisions(ws.decisions_json, updated)
    return {
        "export": str(out_path),
        "count": export.get("count", 0),
        "senses_total": len(updated.get("senses", [])),
        "undecided": decmod.undecided_count(updated),
    }
