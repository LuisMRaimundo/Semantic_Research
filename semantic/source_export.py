"""Relatório por fonte («Exportar fonte…» no workbench).

É um RELATÓRIO, não um deliverable: lê decisions.json (e o
VERSION_MANIFEST publicado, quando existe) e escreve
``<classe>/EXPORT_<FONTE>_<timestamp>/`` com um .md (tabela por cartão) e
um .json (um registo por acepção). Nunca toca na matriz, TERMOS, CONCEPT,
FINAL_RESULTS nem em decisions.json.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .decisions import load_decisions, sense_key
from .resource_links import links_for_sense
from .workspace import ClassWorkspace

SOURCES = {"pulo": "PULO", "onto": "ONTO", "papel": "PAPEL", "wordnet": "WORDNET"}

_SOURCE_TITLE = {
    "pulo": "PULO (ILI anchor)",
    "onto": "Onto.PT / CONTO.PT (discovery)",
    "papel": "PAPEL 3.5 (dictionary relations)",
    "wordnet": "WordNet (OEWN, corroboration)",
}

# VERSION_MANIFEST keys relevant per source (pin/version where available).
_PIN_KEYS = {
    "pulo": (("config_keys", "pulo_sqlite"),),
    "onto": (("config_keys", "onto_sqlite"),),
    "papel": (("config_keys", "papel_sqlite"), ("config_keys", "papel_dir")),
    "wordnet": (
        ("packages", "oewn_pin"), ("packages", "own_pt_pin"),
        ("packages", "wn"), ("packages", "cili"),
    ),
}


def _source_pins(ws: ClassWorkspace, src: str) -> dict[str, Any]:
    mf_path = ws.final_results / "VERSION_MANIFEST.json"
    try:
        manifest = json.loads(mf_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version_manifest": None}
    pins: dict[str, Any] = {
        "version_manifest": str(mf_path),
        "manifest_generated": manifest.get("generated"),
    }
    for section, key in _PIN_KEYS.get(src, ()):
        val = (manifest.get(section) or {}).get(key)
        if val:
            pins[key] = val
    return pins


def _sense_record(s: dict[str, Any]) -> dict[str, Any]:
    rec: dict[str, Any] = {
        "sense_key": sense_key(s["source"], s["key"]),
        "source": s.get("source"),
        "key": s.get("key"),
        "ili": s.get("ili"),
        "members": list(s.get("members") or []),
        "gloss": s.get("gloss") or "",
        "decision": (s.get("decision") or "").strip(),
    }
    if s.get("local_id"):
        rec["local_id"] = s["local_id"]
    for extra in ("migrado_de", "revisao_pendente", "note"):
        if s.get(extra):
            rec[extra] = s[extra]
    links = []
    for link in links_for_sense(s):
        url = getattr(link, "url", "") or ""
        if url.startswith(("http://", "https://")):
            links.append({
                "label": getattr(link, "label", ""),
                "url": url,
                "detail": getattr(link, "detail", ""),
            })
    if links:
        rec["links"] = links
    return rec


def _render_md(doc: dict[str, Any]) -> str:
    L: list[str] = []
    ap = L.append
    ap(f"# Exportação por fonte — {doc['source_label']}")
    ap("")
    ap(f"- **Classe:** {doc['class_id']}")
    ap(f"- **Fonte:** {doc['source_title']}")
    ap(f"- **Gerado:** {doc['generated']}")
    for k, v in (doc.get("source_version") or {}).items():
        if k == "version_manifest" and v is None:
            ap("- **Pin/versão:** VERSION_MANIFEST indisponível (classe sem Run)")
        elif v:
            ap(f"- **{k}:** {v}")
    counts = doc["counts"]
    ap(f"- **Cartões:** {counts['cards']} · **decididos:** {counts['decided']}")
    breakdown = " · ".join(
        f"{k or '—'}: {v}" for k, v in sorted(counts["by_status"].items())
    )
    ap(f"- **Por estado:** {breakdown or '—'}")
    ap("")
    ap("Relatório apenas — não altera matriz, TERMOS, CONCEPT, FINAL_RESULTS "
       "nem decisions.json.")
    ap("")
    for i, r in enumerate(doc["senses"], start=1):
        ap(f"## {i}. {r['key']}")
        ap("")
        ap("| campo | valor |")
        ap("|---|---|")
        ap(f"| decisão | {r['decision'] or '—'} |")
        ap(f"| membros | {', '.join(r['members']) or '—'} |")
        ap(f"| ILI | {r.get('ili') or '—'} |")
        if r.get("local_id"):
            ap(f"| id local | {r['local_id']} |")
        gloss = (r.get("gloss") or "").replace("|", "\\|").replace("\n", " ")
        ap(f"| gloss | {gloss or '—'} |")
        for extra in ("migrado_de", "revisao_pendente", "note"):
            if r.get(extra):
                ap(f"| {extra} | {r[extra]} |")
        for link in r.get("links") or []:
            ap(f"| ligação | [{link['label']}]({link['url']}) |")
        ap("")
    return "\n".join(L)


def export_source_report(ws: ClassWorkspace, source: str) -> dict[str, Any]:
    """Escreve EXPORT_<FONTE>_<timestamp>/ na pasta da classe. Devolve paths."""
    src = (source or "").lower()
    if src not in SOURCES:
        raise ValueError(f"fonte desconhecida: {source!r}")
    label = SOURCES[src]

    dec = load_decisions(ws.decisions_json)
    senses = [
        s for s in dec.get("senses") or []
        if (s.get("source") or "").lower() == src
    ]
    records = [_sense_record(s) for s in senses]
    by_status = Counter(r["decision"] for r in records)

    now = datetime.now(timezone.utc).astimezone()
    folder = ws.root / f"EXPORT_{label}_{now.strftime('%Y%m%d-%H%M%S')}"
    folder.mkdir(parents=True, exist_ok=True)

    doc = {
        "schema": "semantic_research.source_export/1",
        "class_id": ws.class_id,
        "source": src,
        "source_label": label,
        "source_title": _SOURCE_TITLE[src],
        "generated": now.isoformat(timespec="seconds"),
        "source_version": _source_pins(ws, src),
        "counts": {
            "cards": len(records),
            "decided": sum(1 for r in records if r["decision"]),
            "by_status": dict(by_status),
        },
        "senses": records,
    }
    json_path = folder / f"{ws.class_id}.{label}.export.json"
    md_path = folder / f"{ws.class_id}.{label}.export.md"
    json_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md_path.write_text(_render_md(doc), encoding="utf-8")
    return {
        "folder": str(folder),
        "md": str(md_path),
        "json": str(json_path),
        "cards": len(records),
        "decided": doc["counts"]["decided"],
    }
