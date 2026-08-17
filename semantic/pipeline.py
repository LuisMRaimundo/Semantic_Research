"""Run engines + LexWarrant against a class workspace (R8 / ~95)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Optional

from .compile_specs import write_specs
from .engines import (
    ensure_engine_paths,
    load_lexwarrant,
    load_phase0_pulo,
    load_phase0_skos,
)
from .settings import load_config
from .workspace import ClassWorkspace


def _best_pulo_export(ws: ClassWorkspace) -> Optional[Path]:
    """Prefer the non-empty PULO export with the most synsets.

    Alphabetical first-hit wrongly picks empty probes (e.g. ``pulo_composed.json``
    before ``pulo_composição.json``).
    """
    candidates = sorted(ws.exports.glob("*pulo*.json")) + sorted(
        ws.exports.glob("*.json")
    )
    best: Optional[Path] = None
    best_n = -1
    fallback: Optional[Path] = None
    seen: set[Path] = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if obj.get("type") != "pulo_thesaurus_search":
            continue
        if fallback is None:
            fallback = p
        n = len(obj.get("synsets") or [])
        if int(obj.get("count") or 0) > n:
            n = int(obj.get("count") or 0)
        if n > best_n:
            best_n = n
            best = p
    if best is not None and best_n > 0:
        return best
    return fallback


def _relabel_result(src: Path, dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return dest


def _enrich_result_glosses(result_path: Path, class_id: str) -> None:
    """Attach SenseIndex glosses to provenance rows (enables gloss-gated weak joins)."""
    try:
        from .normalize import normalize_word
        from .sense_index import SenseIndex
    except Exception:  # noqa: BLE001
        return
    if not result_path.exists():
        return
    try:
        data = json.loads(result_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    changed = False
    with SenseIndex() as si:
        c = si.connect()
        for prov in data.get("provenance") or []:
            if prov.get("gloss"):
                continue
            term = prov.get("termo") or prov.get("term") or ""
            if not term:
                continue
            nw = normalize_word(term)
            row = c.execute(
                "SELECT gloss FROM sense WHERE class_id = ? AND lemmas_norm LIKE ? "
                "AND gloss IS NOT NULL AND gloss != '' LIMIT 1",
                (class_id, f'%"{nw}"%'),
            ).fetchone()
            if row and row["gloss"]:
                prov["gloss"] = row["gloss"]
                changed = True
    if changed:
        result_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


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


def _onto_source_status(ws: ClassWorkspace, onto_sqlite: Path) -> dict[str, Any]:
    """Real ONTO provenance flags (discovery-only source, never in the matrix).

    ``source_queried`` = the source was actually consulted: the ONTO engine
    produced a result for this class OR discovery cards were seeded into
    decisions.json from GUI searches. Not merely "a file exists".
    """
    from . import decisions as decmod

    onto_result = ws.results / f"{ws.class_id}.ONTO.result.json"
    engine_ran = onto_result.exists()
    engine_evidence = False
    if engine_ran:
        try:
            od = json.loads(onto_result.read_text(encoding="utf-8"))
            engine_evidence = bool(
                od.get("sinalizacao") or od.get("provenance") or od.get("stage5")
            )
        except (OSError, json.JSONDecodeError):
            engine_evidence = True
    try:
        dec = decmod.load_decisions(ws.decisions_json)
        onto_cards = [
            s for s in dec.get("senses") or []
            if (s.get("source") or "").lower() == "onto"
        ]
    except (OSError, json.JSONDecodeError):
        onto_cards = []
    return {
        "role": "discovery",
        "source_available": onto_sqlite.exists(),
        "source_queried": engine_ran or bool(onto_cards),
        "contributed_discovery_evidence": engine_evidence or bool(onto_cards),
        "contributed_concordance_results": False,
        "source_contributed_results": False,
        "n_discovery_cards": len(onto_cards),
    }


def _preflight(ws: ClassWorkspace, engines: list[str]) -> list[str]:
    """Human-readable blockers before engines run (empty axis, empty export…)."""
    problems: list[str] = []
    meta = ws.load_meta()
    if not (meta.get("axis") or "").strip():
        problems.append(
            "axis is empty — fill Meta «axis: …» and Guardar decisões "
            "(both PULO and ONTO engines require it)."
        )
    if "pulo" in engines:
        export = _best_pulo_export(ws)
        if export is None:
            problems.append(
                "No PULO export — search any lemma with source PULO "
                "(use a form attested in the lexicon)."
            )
        else:
            try:
                data = json.loads(export.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                data = {}
            if int(data.get("count") or 0) == 0 or not (data.get("synsets") or []):
                problems.append(
                    f"PULO export is empty ({export.name}, 0 synsets) — "
                    "re-search a lemma that hits the lexicon "
                    "(try a citation form / alternate spelling)."
                )
    return problems


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
    # Distinguish omitted arg (default both) from explicit engines=[] (merge-only).
    if engines is None:
        engines = ["pulo", "onto"]
    paths = ensure_engine_paths()
    phase0_pulo = load_phase0_pulo()
    phase0_skos = load_phase0_skos()
    lexwarrant = load_lexwarrant()

    summary: dict[str, Any] = {
        "class_id": ws.class_id,
        "specs": {},
        "results": {},
        "errors": [],
    }

    blockers = _preflight(ws, engines)
    if blockers:
        summary["errors"].extend(blockers)
        summary["merge_ok"] = False
        summary["status"] = ws.status()
        return summary

    spec_paths = write_specs(ws)
    summary["specs"] = {k: str(v) for k, v in spec_paths.items()}

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

    # --- WordNet (OEWN) + OWN-PT (duas colunas; regeneradas se houver facets) ---
    try:
        from .wordnet_track import build_wordnet_and_ownpt_results
        wn_res = build_wordnet_and_ownpt_results(ws.class_id)
        if wn_res.get("ok"):
            summary["wordnet_track"] = {
                "path": wn_res["path"],
                "ownpt_path": wn_res.get("ownpt_path"),
                "lexicon": wn_res.get("lexicon"),
                "convoked": wn_res["convoked"],
                "skipped": wn_res["skipped"],
                "n_sinalizacao": wn_res["n_sinalizacao"],
                "n_atestacao": wn_res.get("n_atestacao"),
            }
        else:
            summary["wordnet_track"] = {"skipped_because": wn_res.get("error")}
    except Exception as exc:  # noqa: BLE001
        summary["errors"].append(f"WordNet/OWN-PT track: {exc}")

    # --- SenseIndex (durable registry) + Onto→ILI proposals (review-only) ---
    if bool(cfg.get("sense_index_on_run", True)):
        try:
            from .onto_ili import propose_for_class
            from .sense_index import SenseIndex, ingest_class_exports

            with SenseIndex() as si:
                idx_info = ingest_class_exports(ws.class_id, index=si)
                prop = propose_for_class(ws.class_id, index=si, write_report=True)
            summary["sense_index"] = {
                "path": idx_info.get("index"),
                "ingested": {
                    k: idx_info.get(k) for k in ("pulo", "onto", "oewn", "own-pt", "files")
                },
                "stats": idx_info.get("stats"),
                "onto_ili_proposals": prop.get("n_proposals"),
                "onto_ili_report": prop.get("path"),
            }
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"SenseIndex: {exc}")

    # --- Merge ---
    inputs = []
    pulo_r = ws.results / f"{ws.class_id}.PULO.result.json"
    onto_r = ws.results / f"{ws.class_id}.ONTO.result.json"
    own_r = ws.results / f"{ws.class_id}.OWN-PT.result.json"
    wn_r = ws.results / f"{ws.class_id}.WordNet.result.json"
    for rp in (pulo_r, own_r, wn_r):
        if rp.exists():
            _enrich_result_glosses(rp, ws.class_id)
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
    # Corte 3: Onto.PT is discovery-only — do NOT feed admits into LexWarrant.
    if onto_r.exists():
        summary["onto_discovery_only"] = str(onto_r)
    if own_r.exists():
        inputs.append(("OWN-PT", own_r))
    if wn_r.exists():
        inputs.append(("WordNet", wn_r))
    # Onto→ILI: inventory signals only (never weak 'atestado' corroboration)
    try:
        from .onto_ili import apply_accepted_to_decisions, emit_onto_ili_result
        apply_accepted_to_decisions(ws.class_id)
        onto_ili_path = emit_onto_ili_result(ws.class_id)
        if onto_ili_path:
            summary["onto_ili_result"] = onto_ili_path
            summary["onto_ili_role"] = "sinalizacao_inventory"
    except Exception as exc:  # noqa: BLE001
        summary.setdefault("errors", []).append(f"Onto-ILI emit: {exc}")
        onto_ili_path = None
    onto_ili_r = ws.results / f"{ws.class_id}.ONTO-ILI.result.json"
    if onto_ili_r.exists():
        inputs.append(("ONTO-ILI", onto_ili_r))

    if len(inputs) >= 2:
        try:
            import contextlib
            import io
            from .cili_auto import prepare_cili_for_run
            from .ili_coverage import write_coverage_report
            cili_info = prepare_cili_for_run(ws)
            equiv = cili_info["equiv"]
            map_path = cili_info["map_path"]
            summary["ili_table"] = str(map_path)
            summary["cili_version"] = cili_info.get("cili_version")
            summary["ili_migration"] = str(cili_info.get("migration_md"))
            try:
                cov = write_coverage_report(ws, dest=ws.out)
                if ws.final_results.exists():
                    write_coverage_report(ws, dest=ws.final_results)
                summary["ili_coverage"] = {
                    "n_resolved": cov.get("n_resolved"),
                    "n_unresolved_oewn_ili": cov.get("n_unresolved_oewn_ili"),
                    "n_unresolved_pulo_offset": cov.get("n_unresolved_pulo_offset"),
                    "n_cili_joinable": cov.get("n_cili_joinable"),
                    "path": cov.get("path_md"),
                }
            except Exception as exc:  # noqa: BLE001
                summary.setdefault("errors", []).append(f"ILI coverage: {exc}")
            weak_mode = str(cfg.get("weak_term_mode") or "gloss_gated")
            gloss_min = float(cfg.get("gloss_min") or 0.12)
            # Keep decisions.json aligned with concept_mapping.excluded_cili
            try:
                from .mapping_policy import (
                    excluded_cili_ids,
                    sync_decisions_with_excluded_cili,
                )
                from . import decisions as decmod
                meta = ws.load_meta()
                dec = decmod.load_decisions(ws.decisions_json)
                dec2, flips = sync_decisions_with_excluded_cili(dec, meta)
                if flips:
                    decmod.save_decisions(ws.decisions_json, dec2)
                    summary["excluded_cili_sync"] = flips
                excl_ids = excluded_cili_ids(meta, dec2)
            except Exception as exc:  # noqa: BLE001
                summary.setdefault("errors", []).append(f"mapping sync: {exc}")
                excl_ids = set()
            # ONTO is discovery-only (never a LexWarrant input), so its real
            # status must be computed here and rendered with the report —
            # "queried" means the source was actually consulted (engine ran
            # OR discovery cards were seeded from the GUI), not merely that
            # a result file exists.
            onto_status = _onto_source_status(ws, paths["onto_sqlite"])
            summary["source_status_onto"] = onto_status
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                doc = lexwarrant.run_report(
                    inputs, ws.out, policy=policy,
                    map_path=map_path, equiv=equiv,
                    weak_term_mode=weak_mode, gloss_min=gloss_min,
                    excluded_cilis=excl_ids or None,
                    source_status_overrides={"ONTO": onto_status},
                )
            summary["weak_term_mode"] = weak_mode
            summary["gloss_min"] = gloss_min
            for line in buf.getvalue().splitlines():
                if "ili_equivalence" in line.lower() or "CILI" in line.upper():
                    summary.setdefault("ili_log", []).append(line)
            published = ws.publish_final_results(
                Path(doc["_md_path"]), Path(doc["_json_path"])
            )
            from .export_blocks import append_t12_to_concordance, write_export_blocks
            from .reconcile import reconcile_class
            from .termos_pesquisa import write_termos_pesquisa
            blocks = write_export_blocks(ws, dest_dir=ws.final_results)
            n_sup = int(blocks.get("n_alt_labels_suppressed") or 0)
            if n_sup:
                summary.setdefault("warnings", []).append(
                    f"{n_sup} candidatos UF suprimidos por validated_alt_labels"
                )
            # Attach T12 on every concordance JSON copy (FINAL__, short name, out/).
            t12_targets = {
                Path(published["json"]),
                ws.out / f"{ws.class_id}.concordance.json",
                ws.final_results / f"{ws.class_id}.concordance.json",
            }
            for target in t12_targets:
                if target.exists():
                    append_t12_to_concordance(target, blocks)
            termos = write_termos_pesquisa(ws, dest_dir=ws.final_results)
            if bool(cfg.get("publish_concept_model", True)):
                try:
                    from .concept_model import publish_class_concept
                    summary["concept_model"] = publish_class_concept(
                        ws.class_id, dest_dir=ws.final_results,
                    )
                    n_pend = int(
                        (summary["concept_model"] or {}).get("n_pending_ili") or 0
                    )
                    if n_pend:
                        summary.setdefault("warnings", []).append(
                            f"{n_pend} pares ILI humanos divergentes do CILI "
                            "por adjudicar"
                        )
                    # also keep coverage next to CONCEPT
                    from .ili_coverage import write_coverage_report as _cov
                    _cov(ws, dest=ws.final_results)
                except Exception as exc:  # noqa: BLE001
                    summary.setdefault("errors", []).append(
                        f"Concept model: {exc}"
                    )
            # T15 — adjudication ↔ artefact traceability (same targets as T12)
            try:
                from .traceability import append_t15_to_concordance, run_t15
                t15 = run_t15(ws)
                if t15 is not None:
                    for target in t12_targets:
                        if target.exists():
                            append_t15_to_concordance(target, t15)
                    summary["t15"] = {
                        "passed": t15["passed"],
                        "evidence": t15["evidence"],
                        "dropped_with_reason": t15["dropped_with_reason"],
                    }
            except Exception as exc:  # noqa: BLE001
                summary.setdefault("errors", []).append(f"T15: {exc}")
            engines_ran = {e for e in engines if e in ("pulo", "onto")}
            exec_meta = {
                "engines": list(engines),
                "engines_reexecutados": bool(engines_ran),
                "hide_pulo_signals": hide_pulo_signals,
                "onto_admission": bool(
                    (ws.results / f"{ws.class_id}.ONTO-ILI.result.json").exists()
                ),
                "ili_join": "cili-only",
                "weak_term_mode": weak_mode,
                "gloss_min": gloss_min,
            }
            recon = reconcile_class(
                ws,
                concordance_json=Path(published["json"]),
                execution=exec_meta,
            )
            # Keep short alias in sync with T12/R1 after reconcile.
            alias_json = ws.final_results / f"{ws.class_id}.concordance.json"
            if (
                alias_json.exists()
                and alias_json.resolve() != Path(published["json"]).resolve()
            ):
                try:
                    shutil.copy2(published["json"], alias_json)
                    alias_md = ws.final_results / f"{ws.class_id}.concordance.md"
                    pub_md = Path(published["md"])
                    if pub_md.exists():
                        shutil.copy2(pub_md, alias_md)
                except OSError:
                    pass
            from .manifest import build_version_manifest
            from . import settings as _settings
            manifest = build_version_manifest(root=_settings.ROOT)
            build_version_manifest(
                root=_settings.ROOT,
                dest=ws.final_results / "VERSION_MANIFEST.json",
            )
            summary["concordance_md"] = published["md"]
            summary["concordance_json"] = published["json"]
            summary["final_results"] = published["folder"]
            summary["blocos"] = blocks
            summary["termos_pesquisa"] = termos
            summary["version_manifest"] = manifest.get("_path")
            summary["reconciliacao"] = {
                "unidade": recon.get("unidade_contagem"),
                "acepcoes_sem_motor": recon.get("n_acepcoes_sem_motor"),
                "t14_removed": True,
                "json": recon.get("reconcile_json"),
                "md": recon.get("reconcile_md"),
            }
            summary["merge_ok"] = True
            summary["legacy_equivalence_loaded"] = bool(
                doc.get(
                    "legacy_equivalence_loaded",
                    doc.get("ili_equivalence_loaded"),
                )
            )
            summary["legacy_equivalence_counts"] = (
                doc.get("legacy_equivalence_counts")
                or doc.get("ili_equivalence_counts")
            )
            # MD and JSON are rendered from the same source_status dict
            # (ONTO included via source_status_overrides above) — no
            # post-hoc, JSON-only patching.
            summary["source_status"] = doc.get("source_status") or {}
            note_bits = [
                f"FINAL RESULTS → {published['folder']}",
                "Deliverable: TERMOS.html + TERMOS_PESQUISA.md/.csv",
                f"CILI {cili_info.get('cili_version')} · {cili_info.get('n_map', 0)} pares",
            ]
            if hide_pulo_signals and summary.get("pulo_signals"):
                note_bits.append(
                    f"{summary['pulo_signals']} PULO signals sidelined in out/"
                )
            for w in summary.get("warnings") or []:
                note_bits.append(f"AVISO: {w}")
            summary["note"] = " · ".join(note_bits)
        except Exception as exc:  # noqa: BLE001
            summary["errors"].append(f"LexWarrant: {exc}")
            summary["merge_ok"] = False
    elif len(inputs) == 1:
        summary["errors"].append(
            "Only one result.json — LexWarrant needs ≥2 sources "
            "(PULO + OWN-PT/WordNet). Onto.PT is discovery-only."
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
    from .adapters import OntoStore, PapelStore, PuloStore, WordNetStore
    from . import decisions as decmod
    from .resources import ensure_papel_index

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
    elif source == "papel":
        ensure_papel_index()
        store = PapelStore(Path(cfg["papel_sqlite"]))
        export = store.export_search(
            query, mode=mode, limit=min(limit, 40)
        )
        store.close()
        fname = f"papel_{query.strip().replace(' ', '_')}.json"
    elif source in ("wordnet", "oewn", "wn"):
        source = "wordnet"
        export = WordNetStore().export_search(
            query, class_id=ws.class_id, pos=pos, limit=min(limit, 40)
        )
        # *.facets.json so wordnet_track / CILI harvest find this class first
        safe = query.strip().replace(" ", "_")
        fname = f"wordnet_{safe}.facets.json"
    else:
        raise ValueError("source must be 'pulo', 'onto', 'papel', or 'wordnet'")

    out_path = ws.exports / fname
    out_path.write_text(
        json.dumps(export, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    existing = decmod.load_decisions(ws.decisions_json)
    existing["class_id"] = ws.class_id
    if source == "pulo":
        updated = decmod.from_pulo_export(export, existing)
    elif source == "onto":
        updated = decmod.from_onto_export(export, existing)
    elif source == "papel":
        updated = decmod.from_papel_export(export, existing)
    else:
        updated = decmod.from_wordnet_export(export, existing)
    decmod.save_decisions(ws.decisions_json, updated)
    return {
        "export": str(out_path),
        "count": export.get("count", 0),
        "senses_total": len(updated.get("senses", [])),
        "undecided": decmod.undecided_count(updated),
    }
