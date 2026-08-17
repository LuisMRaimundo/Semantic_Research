"""Post-merge residual report (Corte 2).

The b1/b2/c1/c2/estipulações taxonomy is removed. Only lists sense adjudications
(UF/RT) that have no corresponding motor provenance row.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from .decisions import VOCABULARIO, load_decisions
from .normalize import normalize_word
from .workspace import ClassWorkspace


def _motor_lemmas(ws: ClassWorkspace) -> set[str]:
    out: set[str] = set()
    for path in (
        ws.results / f"{ws.class_id}.PULO.result.json",
        ws.results / f"{ws.class_id}.OWN-PT.result.json",
    ):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for p in data.get("provenance") or []:
            t = p.get("termo") or p.get("term") or ""
            if t:
                out.add(normalize_word(t))
    return out


def build_residual_report(
    ws: ClassWorkspace,
    execution: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    dec = load_decisions(ws.decisions_json)
    motor = _motor_lemmas(ws)
    orphans: list[dict[str, Any]] = []
    descartado_onto: list[dict[str, Any]] = []
    for s in dec.get("senses") or []:
        decision = (s.get("decision") or "").strip()
        if decision not in VOCABULARIO:
            continue
        src = (s.get("source") or "").lower()
        members = [m for m in (s.get("members") or []) if m]
        # Onto discovery-only: never in motor admission — declared, not silent
        if src == "onto":
            descartado_onto.append({
                "source": src,
                "key": s.get("key"),
                "ili": s.get("ili"),
                "decision": decision,
                "membros": members,
                "nota": "descartado (Onto.PT discovery-only — não admite na matriz)",
            })
            continue
        missing = [m for m in members if normalize_word(m) not in motor]
        if missing == members and members:
            orphans.append({
                "source": src,
                "key": s.get("key"),
                "ili": s.get("ili"),
                "decision": decision,
                "membros": members,
                "nota": "acepção adjudicada sem correspondência em motor",
            })
    return {
        "class_id": ws.class_id,
        "unidade_contagem": "acepção (sentido) com decisão UF/RT",
        "execution": execution or {},
        "acepcoes_sem_motor": orphans,
        "n_acepcoes_sem_motor": len(orphans),
        "descartado_onto_discovery": descartado_onto,
        "n_descartado_onto_discovery": len(descartado_onto),
        "taxonomy_removed": [
            "conflitos_planos",
            "divergencia_sentidos",
            "estipulacoes_termo",
            "adjudicados_c1_recuperavel",
            "adjudicados_c2_estrutural",
        ],
        "t14_ok": None,
        "t14_removed": True,
    }


def render_reconcile_markdown(report: dict[str, Any]) -> str:
    L: list[str] = []
    ap = L.append
    ap(f"# Relatório residual — `{report.get('class_id')}`")
    ap("")
    ap("Taxonomia de reconciliação (b1/b2/c1/c2/estipulações) **removida** (Corte 2).")
    ap("")
    ap("## Acepções adjudicadas sem correspondência em motor")
    ap("")
    orphans = report.get("acepcoes_sem_motor") or []
    if not orphans:
        ap("_(nenhuma)_")
    else:
        for o in orphans:
            mems = ", ".join(o.get("membros") or [])
            ap(
                f"- `{o.get('decision')}` · {o.get('source')}:{o.get('key')} · "
                f"{mems}"
            )
    ap("")
    ap("## Descartado (Onto.PT discovery-only)")
    ap("")
    ap("Acepções Onto.PT adjudicadas UF/RT — por desenho nunca entram na "
       "matriz LexWarrant (Corte 3). Listadas aqui para rastreabilidade.")
    ap("")
    dropped = report.get("descartado_onto_discovery") or []
    if not dropped:
        ap("_(nenhuma)_")
    else:
        for o in dropped:
            mems = ", ".join(o.get("membros") or [])
            ap(
                f"- `{o.get('decision')}` · {o.get('source')}:{o.get('key')} · "
                f"{mems}"
            )
    ap("")
    return "\n".join(L)


def reconcile_class(
    ws: ClassWorkspace,
    concordance_json: Optional[Path] = None,
    execution: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    report = build_residual_report(ws, execution=execution)
    ws.out.mkdir(parents=True, exist_ok=True)
    stem = f"{ws.class_id}.reconcile"
    primary = ws.final_results if ws.final_results.exists() else ws.out
    primary.mkdir(parents=True, exist_ok=True)
    for folder in {ws.out, primary}:
        (folder / f"{stem}.json").write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        (folder / f"{stem}.md").write_text(
            render_reconcile_markdown(report), encoding="utf-8"
        )

    if concordance_json and Path(concordance_json).exists():
        try:
            doc = json.loads(Path(concordance_json).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            doc = None
        if doc is not None:
            # Drop T14 if present; attach residual note
            asserts = [
                a for a in (doc.get("assertions") or [])
                if a.get("id") not in ("T14",)
            ]
            asserts.append({
                "id": "R1",
                "text": (
                    "Relatório residual: acepções UF/RT sem correspondência "
                    "em motor (taxonomia T14 removida)."
                ),
                "passed": True,
                "evidence": f"n={report['n_acepcoes_sem_motor']}",
            })
            doc["assertions"] = asserts
            doc["all_passed"] = all(
                a.get("passed") or a.get("pass") for a in asserts
            )
            doc["reconciliacao"] = {
                "t14_removed": True,
                "acepcoes_sem_motor": report["n_acepcoes_sem_motor"],
            }
            Path(concordance_json).write_text(
                json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            from .assertions import rewrite_assertions_block
            rewrite_assertions_block(Path(concordance_json))
            md_path = Path(concordance_json).with_suffix(".md")
            if md_path.exists():
                text = md_path.read_text(encoding="utf-8")
                if "## Reconciliação" in text:
                    text = text.split("## Reconciliação")[0].rstrip() + "\n"
                if "# Relatório residual" in text:
                    text = text.split("# Relatório residual")[0].rstrip() + "\n"
                md_path.write_text(
                    text.rstrip() + "\n\n" + render_reconcile_markdown(report),
                    encoding="utf-8",
                )

    report["reconcile_json"] = str(primary / f"{stem}.json")
    report["reconcile_md"] = str(primary / f"{stem}.md")
    return report
