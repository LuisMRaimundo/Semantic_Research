"""CILI ↔ OEWN (2024) / PULO coverage — make graph drift visible, never silent.

OEWN speaks native CILI ``i…``; PULO speaks PWN-3.0 ``pwn30-…`` (legacy ``ili-30-…``) offsets resolved
through the vendored 2016-era map. This module classifies every harvested id so
unmapped / OEWN-only / PULO-gap cases appear in FINAL_RESULTS.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .engines import cili_api
from .workspace import ClassWorkspace


def _cfg_pins() -> dict[str, str]:
    from .settings import load_config
    cfg = load_config()
    return {
        "oewn": str(cfg.get("oewn") or "oewn:2025"),
        "cili_commit": str(cfg.get("cili_commit") or ""),
        "cili_map": str(cfg.get("cili_map") or ""),
    }


def _is_cili_id(s: str) -> bool:
    return bool(s) and s.startswith("i") and s[1:].isdigit()


def _is_pwn30ish(s: str) -> bool:
    return "30-" in s or (len(s) >= 10 and s[-2] == "-" and s[-1].isalpha())


def classify_identifiers(identifiers: list[str]) -> dict[str, Any]:
    """Bucket raw identifiers by CILI resolvability."""
    _, counts_fn, resolve, offset_fn = cili_api()
    counts = counts_fn()
    pins = _cfg_pins()

    resolved: list[dict[str, str]] = []
    unresolved_oewn: list[str] = []
    unresolved_pulo: list[str] = []
    unresolved_other: list[str] = []
    by_cili: dict[str, list[str]] = {}

    for raw in identifiers:
        s = str(raw or "").strip()
        if not s:
            continue
        cid = resolve(s)
        if cid:
            resolved.append({"raw": s, "cili": cid})
            by_cili.setdefault(cid, []).append(s)
            continue
        if _is_cili_id(s):
            # Native OEWN ILI absent from the PWN-3.0 CILI dump → drift signal
            unresolved_oewn.append(s)
        elif _is_pwn30ish(s) or s.startswith("ili-") or s.startswith("por-"):
            unresolved_pulo.append(s)
        else:
            unresolved_other.append(s)

    # Cross-source join potential: CILI ids that gathered ≥2 distinct raw forms
    joinable = {
        cid: sorted(set(raws))
        for cid, raws in by_cili.items()
        if len(set(raws)) >= 2
    }
    singleton = {
        cid: raws[0]
        for cid, raws in by_cili.items()
        if len(set(raws)) == 1
    }

    return {
        "schema": "semantic_research.ili_coverage/1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pins": pins,
        "cili": {
            "version": counts.get("version"),
            "ili_ids": counts.get("ili_ids"),
            "note": (
                "Resolver loads PWN-3.0 + PWN-3.1 offset maps, and validates bare "
                "i… ids via wn.ili when missing from the TSVs. Unresolved ids are "
                "listed here — never silently dropped."
            ),
        },
        "n_identifiers": len(identifiers),
        "n_resolved": len(resolved),
        "n_unresolved_oewn_ili": len(unresolved_oewn),
        "n_unresolved_pulo_offset": len(unresolved_pulo),
        "n_unresolved_other": len(unresolved_other),
        "n_cili_joinable": len(joinable),
        "n_cili_singleton": len(singleton),
        "joinable_cili": [
            {"cili": cid, "raw": raws} for cid, raws in sorted(joinable.items())
        ][:200],
        "singleton_cili_sample": [
            {"cili": cid, "raw": raw}
            for cid, raw in sorted(singleton.items())[:80]
        ],
        "unresolved_oewn_ili": sorted(set(unresolved_oewn))[:200],
        "unresolved_pulo_offset": sorted(set(unresolved_pulo))[:200],
        "unresolved_other": sorted(set(unresolved_other))[:80],
        "resolved_sample": resolved[:80],
    }


def write_coverage_report(
    ws: ClassWorkspace,
    identifiers: Optional[list[str]] = None,
    dest: Optional[Path] = None,
) -> dict[str, Any]:
    from .cili_auto import collect_identifiers_from_results

    ids = list(identifiers) if identifiers is not None else collect_identifiers_from_results(ws)
    report = classify_identifiers(ids)
    report["class_id"] = ws.class_id
    folder = Path(dest) if dest else ws.out
    folder.mkdir(parents=True, exist_ok=True)
    json_path = folder / "ili_coverage.json"
    md_path = folder / "ili_coverage.md"
    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    lines = [
        f"# ILI / CILI coverage — `{ws.class_id}`",
        "",
        f"- **OEWN pin:** {report['pins'].get('oewn')}",
        f"- **CILI:** {report['cili'].get('version')} · "
        f"{report['cili'].get('ili_ids')} ids",
        f"- **Identifiers harvested:** {report['n_identifiers']}",
        f"- **Resolved via CILI map:** {report['n_resolved']}",
        f"- **Joinable CILI ids (≥2 raw forms):** {report['n_cili_joinable']}",
        f"- **Unresolved OEWN `i…` (drift / missing from PWN30 map):** "
        f"{report['n_unresolved_oewn_ili']}",
        f"- **Unresolved PULO/OMW offsets:** {report['n_unresolved_pulo_offset']}",
        "",
        report["cili"].get("note") or "",
        "",
        "## Unresolved OEWN ILIs (silent joins prevented)",
        "",
    ]
    if report["unresolved_oewn_ili"]:
        for x in report["unresolved_oewn_ili"][:60]:
            lines.append(f"- `{x}`")
    else:
        lines.append("_(none)_")
    lines += ["", "## Unresolved PULO / OMW offsets", ""]
    if report["unresolved_pulo_offset"]:
        for x in report["unresolved_pulo_offset"][:60]:
            lines.append(f"- `{x}`")
    else:
        lines.append("_(none)_")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    report["path_json"] = str(json_path)
    report["path_md"] = str(md_path)
    return report
