"""T15 — rastreabilidade adjudicação ↔ artefactos.

(a) cada item de vocabulário exportado (CONCEPT altLabel, blocos altLabel,
    TERMOS tabela F) rastreia a uma decisão UF/RT explícita DESTA classe;
(b) cada decisão UF/RT figura em ≥1 artefacto OU é listada em
    ``dropped_with_reason`` ao abrigo de uma regra de descarte declarada.

Corre no pipeline (run_class) logo após write_termos_pesquisa /
publish_class_concept, e retrospectivamente via CLI, sem re-executar
pipelines::

    python -m semantic.traceability <classe>
    python -m semantic.traceability --all
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Optional

from .decisions import load_decisions
from .normalize import normalize_word
from .settings import CLASSES_DIR
from .workspace import ClassWorkspace

# Declared drop rules — a drop is only legitimate if one of these matches.
# Future rules are ADDITIONS to this table, not code edits scattered
# elsewhere. Signature: rule(record, norm_form, ctx) -> bool.
KNOWN_DROP_RULES: tuple[tuple[str, Callable[[dict, str, dict], bool]], ...] = (
    ("onto_discovery_only",
     lambda s, m, ctx: (s.get("source") or "").lower() == "onto"),
    ("excluded_cili",
     lambda s, m, ctx: (s.get("cili") or s.get("ili")) in ctx["excluded_cili"]),
)


def build_t15(
    ws: ClassWorkspace,
    *,
    concordance_doc: dict[str, Any],
    blocks: dict[str, Any],
    termos_doc: dict[str, Any],
    concept_graph: dict[str, Any],
    decisions: dict[str, Any],
) -> dict[str, Any]:
    cid = ws.class_id
    # -- exported inventory, with provenance --------------------------------
    exported: dict[str, set[str]] = {}   # norm(form) -> {artefact names}

    def mark(form: Any, artefact: str) -> None:
        n = normalize_word(str(form or ""))
        if n:
            exported.setdefault(n, set()).add(artefact)

    for c in concordance_doc.get("concepts") or []:
        mark(c.get("term"), "matrix")
    for row in (blocks.get("vocabulario") or {}).get("altLabel") or []:
        mark(row.get("termo"), "blocos.altLabel")
    # RT decisions are exported as termoRelacionado, not altLabel — without
    # this surface every RT member would be falsely reported as "lost".
    for row in (blocks.get("vocabulario") or {}).get("termoRelacionado") or []:
        mark(row.get("termo"), "blocos.termoRelacionado")
    for row in termos_doc.get("F_vocabulario_pt") or []:
        mark(row.get("forma"), "termos.F")
    from .concept_model import _vocab_alt_labels
    for form in _vocab_alt_labels(concept_graph):
        mark(form, "concept.altLabel")

    # -- decision inventory (THIS class only) --------------------------------
    decided: dict[str, dict] = {}        # norm(form) -> decision record
    for s in decisions.get("senses") or []:
        if (s.get("decision") or "").strip() in ("UF", "RT"):
            for m in s.get("members") or []:
                decided.setdefault(normalize_word(m), s)
    for t in decisions.get("terms") or []:
        if (t.get("status") or "").strip() in ("UF", "RT"):
            decided.setdefault(normalize_word(t.get("term") or ""), t)
    # NB: manual_terms WITHOUT a status field are deliberately NOT decisions.

    validated = {
        normalize_word(x)
        for x in concept_graph.get("validated_alt_labels") or []
    }
    pref = normalize_word(concept_graph.get("pref_label") or cid)

    # (a) exported item with no decision behind it → violation
    untraceable = sorted(
        f"{n}→{'/'.join(sorted(arts))}"
        for n, arts in exported.items()
        if n not in decided and n not in validated and n != pref
        and "matrix" not in arts  # matrix rows are motor-side; T5 covers them
    )
    # (b) decision reaching no artefact and matching no declared drop rule
    excluded_cili = {
        e.get("cili") for e in concept_graph.get("excluded_cili") or []
        if isinstance(e, dict) and e.get("cili")
    }
    excluded_cili |= set(concept_graph.get("excluded_cili_ids") or [])
    ctx = {"excluded_cili": excluded_cili}
    lost: list[str] = []
    dropped_with_reason: list[dict[str, Any]] = []
    for n, rec in decided.items():
        if n in exported:
            continue
        reason = next(
            (name for name, rule in KNOWN_DROP_RULES if rule(rec, n, ctx)), None
        )
        if reason:
            dropped_with_reason.append({
                "forma": n, "reason": reason,
                "key": rec.get("key"), "source": rec.get("source"),
            })
        else:
            lost.append(f"{rec.get('source')}|{rec.get('key')}|{n}")

    passed = not untraceable and not lost
    return {
        "id": "T15",
        "text": ("Cada item exportado (altLabel/termoRelacionado/matriz/tabela F) "
                 "rastreia a uma decisão desta classe; cada decisão UF/RT figura "
                 "em ≥1 artefacto ou é listada como descartada com motivo "
                 "declarado."),
        "passed": passed,
        "evidence": ("OK" if passed else
                     f"sem_decisao={untraceable[:8]}; perdidos={sorted(lost)[:8]}"),
        "dropped_with_reason": dropped_with_reason,   # audit payload, always emitted
    }


# ---------------------------------------------------------------------------
# Disk-based construction (pipeline wiring + retrospective CLI)
# ---------------------------------------------------------------------------
def _read_json(path: Path) -> Optional[dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _artefact_paths(ws: ClassWorkspace) -> dict[str, Path]:
    fr = ws.final_results
    conc = fr / f"{ws.class_id}.concordance.json"
    if not conc.exists():
        conc = ws.out / f"{ws.class_id}.concordance.json"
    return {
        "concordance": conc,
        "blocos": fr / f"{ws.class_id}.blocos.json",
        "termos": fr / "TERMOS_PESQUISA.json",
        "concept": fr / "CONCEPT.json",
    }


def run_t15(ws: ClassWorkspace) -> Optional[dict[str, Any]]:
    """Build T15 from artefacts already on disk. None se faltarem artefactos."""
    paths = _artefact_paths(ws)
    docs = {name: _read_json(p) for name, p in paths.items()}
    if any(d is None for d in docs.values()):
        return None
    decisions = load_decisions(ws.decisions_json)
    return build_t15(
        ws,
        concordance_doc=docs["concordance"],
        blocks=docs["blocos"],
        termos_doc=docs["termos"],
        concept_graph=docs["concept"],
        decisions=decisions,
    )


def append_t15_to_concordance(
    json_path: Path, t15: dict[str, Any]
) -> None:
    """Anexa T15 ao JSON do concordance e reescreve a secção Markdown."""
    if not json_path.exists():
        return
    doc = _read_json(json_path)
    if doc is None:
        return
    asserts = [a for a in (doc.get("assertions") or []) if a.get("id") != "T15"]
    asserts.append(t15)
    doc["assertions"] = asserts
    doc["all_passed"] = all(a.get("passed") or a.get("pass") for a in asserts)
    json_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    from .assertions import rewrite_assertions_block
    rewrite_assertions_block(json_path)


# ---------------------------------------------------------------------------
# CLI — retrospective audit, no pipeline re-run
# ---------------------------------------------------------------------------
def _class_ids_all() -> list[str]:
    return sorted(
        p.name for p in CLASSES_DIR.iterdir()
        if p.is_dir() and (p / "decisions.json").exists()
    )


def main(argv: Optional[list[str]] = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(
        prog="python -m semantic.traceability",
        description="T15 — rastreabilidade adjudicação ↔ artefactos "
                    "(retrospectivo; não re-executa pipelines).",
    )
    ap.add_argument("class_id", nargs="?", help="classe a auditar")
    ap.add_argument("--all", action="store_true", help="auditar todas as classes")
    args = ap.parse_args(argv)
    if not args.all and not args.class_id:
        ap.error("indique uma classe ou --all")

    class_ids = _class_ids_all() if args.all else [args.class_id]
    rows: list[tuple[str, str, str]] = []
    any_fail = False
    for cid in class_ids:
        try:
            ws = ClassWorkspace.open(cid)
        except FileNotFoundError:
            rows.append((cid, "n/d", "classe não encontrada"))
            continue
        t15 = run_t15(ws)
        if t15 is None:
            rows.append((cid, "n/d", "artefactos em falta (classe não processada)"))
            continue
        if t15["passed"]:
            n_drop = len(t15.get("dropped_with_reason") or [])
            note = f"— ({n_drop} descartes declarados)" if n_drop else "—"
            rows.append((cid, "PASS", note))
        else:
            any_fail = True
            rows.append((cid, "FAIL", t15["evidence"]))

    w = max(len(r[0]) for r in rows) if rows else 10
    print(f"| {'classe'.ljust(w)} | T15  | violações |")
    print(f"|{'-' * (w + 2)}|------|-----------|")
    for cid, status, viol in rows:
        print(f"| {cid.ljust(w)} | {status:<4} | {viol} |")
    return 1 if any_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
