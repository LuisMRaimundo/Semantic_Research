"""Relatório do inventário Onto→ILI (propor / aceitar / rejeitar).

Escreve ``<classe>/EXPORT_ONTO_ILI_<timestamp>/`` com .md + .json.
Não altera decisions.json, TERMOS, CONCEPT nem o SenseIndex.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from .onto_ili import list_proposals
from .resource_links import links_for_onto_ili
from .workspace import ClassWorkspace


def _row_record(r: dict[str, Any]) -> dict[str, Any]:
    onto_key = str(r.get("onto_key") or "")
    ili = str(r.get("ili") or "")
    rec: dict[str, Any] = {
        "onto_key": onto_key,
        "ili": ili,
        "status": r.get("status") or "",
        "score": float(r.get("score") or 0),
        "method": r.get("method") or "",
        "updated": r.get("updated") or "",
        "evidence": r.get("evidence") if isinstance(r.get("evidence"), dict) else {},
    }
    links = []
    for link in links_for_onto_ili(onto_key, ili):
        url = getattr(link, "url", "") or ""
        if url.startswith(("http://", "https://")):
            links.append({
                "label": getattr(link, "label", ""),
                "url": url,
                "detail": getattr(link, "detail", ""),
            })
    rec["links"] = links
    return rec


def _render_md(doc: dict[str, Any]) -> str:
    L: list[str] = []
    ap = L.append
    ap(f"# Onto→ILI — {doc['class_id']}")
    ap("")
    ap(f"- **Classe:** {doc['class_id']}")
    ap(f"- **Gerado:** {doc['generated']}")
    counts = doc["counts"]
    ap(
        f"- **Links:** {counts['total']} · **proposed:** {counts.get('proposed', 0)} · "
        f"**accepted:** {counts.get('accepted', 0)} · **rejected:** {counts.get('rejected', 0)}"
    )
    ap("")
    ap(
        "Relatório do inventário (propor / aceitar / rejeitar). "
        "Não altera decisions.json, TERMOS, CONCEPT nem o SenseIndex."
    )
    ap("")
    ap("| estado | score | onto | ili | ligações |")
    ap("|---|---|---|---|---|")
    for r in doc["rows"]:
        bits = [f"[{ln['label']}]({ln['url']})" for ln in r.get("links") or []]
        ap(
            f"| {r['status'] or '—'} | {r['score']:.2f} | "
            f"`{r['onto_key']}` | `{r['ili']}` | "
            f"{' · '.join(bits) or '—'} |"
        )
    ap("")
    return "\n".join(L)


def export_onto_ili_report(ws: ClassWorkspace) -> dict[str, Any]:
    """Write EXPORT_ONTO_ILI_<timestamp>/ under the class folder."""
    rows = [_row_record(r) for r in list_proposals(ws.class_id)]
    by_status = Counter(r["status"] for r in rows)
    now = datetime.now(timezone.utc).astimezone()
    folder = ws.root / f"EXPORT_ONTO_ILI_{now.strftime('%Y%m%d-%H%M%S')}"
    folder.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema": "semantic_research.onto_ili_export/1",
        "class_id": ws.class_id,
        "generated": now.isoformat(timespec="seconds"),
        "counts": {
            "total": len(rows),
            "proposed": int(by_status.get("proposed") or 0),
            "accepted": int(by_status.get("accepted") or 0),
            "rejected": int(by_status.get("rejected") or 0),
        },
        "rows": rows,
    }
    json_path = folder / f"{ws.class_id}.ONTO-ILI.export.json"
    md_path = folder / f"{ws.class_id}.ONTO-ILI.export.md"
    json_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md_path.write_text(_render_md(doc), encoding="utf-8")
    return {
        "folder": str(folder),
        "md": str(md_path),
        "json": str(json_path),
        "total": doc["counts"]["total"],
        "accepted": doc["counts"]["accepted"],
        "proposed": doc["counts"]["proposed"],
        "rejected": doc["counts"]["rejected"],
    }
