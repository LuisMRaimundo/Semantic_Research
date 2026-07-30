"""Corte 1 — Ponte ILI automática via CILI (sem adjudicação humana).

Resolve `ili-30-…` ↔ `i…` só pela tabela vendorizada. Pares humanos antigos
em `ili_equivalence.json` são migrados: os que o CILI confirma entram no map
automático; os que divergem ficam só no relatório (nunca aplicados).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .engines import cili_api, load_lexwarrant
from .workspace import ClassWorkspace


def _import_cili():
    version, counts, resolve, _ = cili_api()
    return version, counts, resolve


def _import_lexwarrant():
    return load_lexwarrant()


def collect_identifiers_from_results(ws: ClassWorkspace) -> list[str]:
    """Harvest raw ILI strings from class result / export artefacts + SenseIndex."""
    ids: list[str] = []
    seen: set[str] = set()

    def add(raw: Any) -> None:
        # Normalise nested / accidentally serialised ILI payloads.
        if isinstance(raw, (list, tuple)):
            for item in raw:
                add(item)
            return
        if isinstance(raw, dict):
            raw = raw.get("ili_offset") or raw.get("ili") or raw.get("ili_wn_id") or ""
        s = str(raw or "").strip()
        if not s:
            return
        # Stringified list/dict debris from older exports
        if (s.startswith("[") or s.startswith("{")) and "ili" in s.casefold():
            try:
                parsed = json.loads(s.replace("'", '"'))
            except json.JSONDecodeError:
                return
            add(parsed)
            return
        if s not in seen:
            seen.add(s)
            ids.append(s)

    try:
        from .sense_index import SenseIndex
        with SenseIndex() as si:
            for raw in si.identifiers_for_class(ws.class_id):
                add(raw)
    except Exception:  # noqa: BLE001
        pass

    for path in sorted(ws.results.glob(f"{ws.class_id}.*.result.json")):
        if ".for_merge" in path.name:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for p in data.get("provenance") or []:
            for o in p.get("offsets_ili") or []:
                add(o)
        sina = data.get("sinalizacao") or {}
        if isinstance(sina, dict):
            for info in sina.values():
                for o in info.get("offsets_ili") or info.get("offsets") or []:
                    add(o)
        for s in data.get("synsets") or []:
            add(s.get("ili"))
            add(s.get("ili_offset"))
            ili = s.get("ili")
            if isinstance(ili, list):
                for item in ili:
                    if isinstance(item, dict):
                        add(item.get("ili_offset"))

    for path in sorted(ws.exports.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for s in data.get("synsets") or []:
            add(s.get("ili"))
            add(s.get("ili_offset"))
            ili = s.get("ili")
            if isinstance(ili, list):
                for item in ili:
                    if isinstance(item, dict):
                        add(item.get("ili_offset"))

    # Sense cards (PULO ILI anchors)
    try:
        from .decisions import load_decisions
        dec = load_decisions(ws.decisions_json)
        for s in dec.get("senses") or []:
            add(s.get("ili") or s.get("key"))
    except Exception:  # noqa: BLE001
        pass

    return ids


def build_cili_equiv_map(identifiers: list[str]):
    """Build LexWarrant EquivMap from CILI identity only (no lemma inference)."""
    CILI_VERSION, cili_counts, cili_resolve = _import_cili()
    lwmod = _import_lexwarrant()
    EquivMap = lwmod.EquivMap
    canonical_ili = lwmod.canonical_ili

    m = EquivMap()
    m.source_path = f"cili:{CILI_VERSION}"
    by_cili: dict[str, set[str]] = {}
    unresolved: list[str] = []

    for raw in identifiers:
        can, ok = canonical_ili(raw)
        if not ok or not can:
            unresolved.append(raw)
            continue
        cid = cili_resolve(raw)
        if not cid:
            unresolved.append(raw)
            continue
        by_cili.setdefault(cid, set()).add(can)

    pairs = 0
    for cid, cans in sorted(by_cili.items()):
        cans_l = sorted(cans)
        if len(cans_l) < 2:
            continue
        # Unify every pair sharing the same CILI id (typically oewn-ili:iX ↔ pwn30-Y)
        root = cans_l[0]
        for other in cans_l[1:]:
            m.add_equiv(root, other)
            pairs += 1
    m.n_map = pairs
    m.n_review = 0
    m.n_unmatched = len(unresolved)
    m._cili_meta = {  # type: ignore[attr-defined]
        "version": CILI_VERSION,
        "counts": cili_counts(),
        "cili_ids_used": len(by_cili),
        "unresolved_sample": unresolved[:20],
    }
    return m


def migrate_human_ili_table(ws: ClassWorkspace) -> dict[str, Any]:
    """Compare legacy human ili_equivalence map against CILI; never auto-apply divergences."""
    _, _, cili_resolve = _import_cili()
    CILI_VERSION, _, _ = _import_cili()
    from .ili_bridge import find_table_file, is_human_row, load_table

    path = find_table_file(ws)
    doc = load_table(ws) if path else None
    report: dict[str, Any] = {
        "class_id": ws.class_id,
        "generated": datetime.now(timezone.utc).isoformat(),
        "cili_version": CILI_VERSION,
        "legacy_table": str(path) if path else None,
        "confirmed": [],
        "diverged": [],
        "legacy_without_cili": [],
        "note": (
            "Pares humanos confirmados pelo CILI são cobertos pelo map automático. "
            "Pares que divergem NÃO são aplicados — só listados aqui."
        ),
    }
    if not doc:
        report["note"] = "Sem ili_equivalence.json legado."
        return report

    for row in doc.get("map") or []:
        oewn = str(row.get("oewn_ili") or "").strip()
        pulo = str(row.get("pulo_ili") or "").strip()
        if not oewn or not pulo:
            continue
        entry = {
            "oewn_ili": oewn,
            "pulo_ili": pulo,
            "source": row.get("source") or "",
            "human": is_human_row(row),
        }
        c_oewn = cili_resolve(oewn)
        c_pulo = cili_resolve(pulo)
        if c_oewn and c_pulo and c_oewn == c_pulo:
            entry["cili_id"] = c_oewn
            report["confirmed"].append(entry)
        elif c_oewn or c_pulo:
            entry["cili_oewn"] = c_oewn
            entry["cili_pulo"] = c_pulo
            report["diverged"].append(entry)
        else:
            report["legacy_without_cili"].append(entry)
    return report


def write_migration_report(ws: ClassWorkspace, dest: Optional[Path] = None) -> Path:
    report = migrate_human_ili_table(ws)
    folder = Path(dest) if dest else ws.final_results
    folder.mkdir(parents=True, exist_ok=True)
    json_path = folder / "ili_migration_report.json"
    md_path = folder / "ili_migration_report.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        f"# Migração ILI humana → CILI — `{report['class_id']}`",
        "",
        f"- **CILI:** {report.get('cili_version')}",
        f"- **Tabela legada:** {report.get('legacy_table') or '—'}",
        f"- **Confirmados pelo CILI:** {len(report['confirmed'])}",
        f"- **Divergentes (NÃO aplicados):** {len(report['diverged'])}",
        f"- **Sem resolução CILI:** {len(report['legacy_without_cili'])}",
        "",
        report.get("note") or "",
        "",
        "## Confirmados",
        "",
    ]
    if report["confirmed"]:
        for e in report["confirmed"]:
            lines.append(
                f"- `{e['oewn_ili']}` ↔ `{e['pulo_ili']}` "
                f"(cili `{e.get('cili_id')}`) · {e.get('source') or '—'}"
            )
    else:
        lines.append("_(nenhum)_")
    lines += ["", "## Divergentes (não aplicados)", ""]
    if report["diverged"]:
        for e in report["diverged"]:
            lines.append(
                f"- `{e['oewn_ili']}` ↔ `{e['pulo_ili']}` · "
                f"cili_oewn={e.get('cili_oewn')} cili_pulo={e.get('cili_pulo')} · "
                f"{e.get('source') or '—'}"
            )
    else:
        lines.append("_(nenhum)_")
    lines += ["", "## Sem resolução CILI", ""]
    if report["legacy_without_cili"]:
        for e in report["legacy_without_cili"]:
            lines.append(
                f"- `{e['oewn_ili']}` ↔ `{e['pulo_ili']}` · {e.get('source') or '—'}"
            )
    else:
        lines.append("_(nenhum)_")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


def prepare_cili_for_run(ws: ClassWorkspace) -> dict[str, Any]:
    """Build CILI EquivMap + write migration report. Returns paths/meta for pipeline."""
    ids = collect_identifiers_from_results(ws)
    equiv = build_cili_equiv_map(ids)
    mig_path = write_migration_report(ws, dest=ws.out)
    # also copy migration into FINAL when it exists
    if ws.final_results.exists():
        write_migration_report(ws, dest=ws.final_results)
    # Persist a machine table that is CILI-only (for diagnostics / LexWarrant --map)
    CILI_VERSION, cili_counts, _ = _import_cili()
    table = {
        "class": ws.class_id,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source": f"cili:{CILI_VERSION}",
        "cili": cili_counts(),
        "map": [
            {"oewn_ili": a.replace("oewn-ili:", ""), "pulo_ili": b,
             "source": f"cili:{CILI_VERSION}", "confidence": "high"}
            if a.startswith("oewn-ili:") else
            {"oewn_ili": b.replace("oewn-ili:", ""), "pulo_ili": a,
             "source": f"cili:{CILI_VERSION}", "confidence": "high"}
            for a, b in equiv.pairs
        ],
        "review": [],
        "unmatched": [],
        "coverage": {
            "map": equiv.n_map,
            "review": 0,
            "unmatched": equiv.n_unmatched,
        },
        "policy": "cili-only (Corte 1) — sem adjudicação humana",
    }
    # Fix map rows properly
    map_rows = []
    for a, b in equiv.pairs:
        oewn = a.replace("oewn-ili:", "") if a.startswith("oewn-ili:") else (
            b.replace("oewn-ili:", "") if b.startswith("oewn-ili:") else None
        )
        pulo = None
        for cand in (a, b):
            if cand.startswith("pwn30-") or cand.startswith("ili-30-"):
                pulo = cand
                break
        if oewn and pulo:
            map_rows.append({
                "oewn_ili": oewn,
                "pulo_ili": pulo,
                "source": f"cili:{CILI_VERSION}",
                "confidence": "high",
            })
    table["map"] = map_rows
    table["coverage"]["map"] = len(map_rows)
    out_path = ws.out / "ili_equivalence.cili.json"
    out_path.write_text(
        json.dumps(table, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {
        "equiv": equiv,
        "map_path": out_path,
        "migration_md": mig_path,
        "n_identifiers": len(ids),
        "n_map": len(map_rows),
        "cili_version": CILI_VERSION,
    }
