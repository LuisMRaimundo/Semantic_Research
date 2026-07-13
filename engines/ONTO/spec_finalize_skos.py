#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
spec_finalize_skos.py — validador/finalizador de specs Fase 0 (Onto.PT / CONTO.PT).

É um AUXILIAR DE CURADORIA, não um autor. O HUMANO preenche as decisões em branco
de um «<classe>.skos.spec.skeleton.json» (produzido pelo scaffolder do GUI). Este
script:
  (a) carrega o esqueleto preenchido;
  (b) corre verificações de consistência que apanham erros de curadoria (C1–C10);
  (c) emite uma spec «<class_id>.json» que o motor `phase0_skos.py` aceita — OU uma
      lista precisa do que ainda está errado.

NUNCA decide eixo, decisão (UF/RT/exclude), estatuto ou garantia. Não corrige
automaticamente: reporta e recusa. Não fabrica atestações.

Diferenças face ao PULO
-----------------------
O motor do Onto.PT distingue apenas estatutos {UF, RT, contraste} (não há
«atributo»), corrobora candidatos por uma porta difusa (CONTO.PT) e usa
`focus_stems` (não `axis_terms`). A exportação do Onto.PT não traz relações
tipadas, pelo que as verificações C6/C7 baseadas em relações do PULO não se
aplicam (C7 é omitida; C6 usa a pertença ao synset + garantia/contrast_reason).

Uso:
    python spec_finalize_skos.py <classe.skos.spec.skeleton.json> [--outdir fase0]

Importável (função `finalize`) + CLI. Sem dependências além da biblioteca padrão.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

ADMIT_DECISIONS = {"UF", "RT"}
DECISIONS = {"UF", "RT", "exclude"}
POSITIVE_STATUSES = {"UF", "RT"}
STATUSES = {"UF", "RT", "contraste"}
NONLEXICAL_GUARANTEES = {"dominio", "estipulativa"}

_PT_STOP = {
    "o", "a", "os", "as", "de", "do", "da", "dos", "das", "em", "no", "na",
    "ou", "e", "que", "com", "sem", "um", "uma", "ao", "aos", "à", "às",
    "por", "para", "se", "seu", "sua", "the", "of",
}


# ---------------------------------------------------------------------------
# Text helpers (standalone; do not couple to the engine)
# ---------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def fold(text: str) -> str:
    return strip_accents(text or "").casefold()


def norm_term(term: str) -> str:
    return fold(term).strip().replace("_", " ")


def content_tokens(text: str, min_len: int = 3) -> list[str]:
    toks = re.findall(r"[^\W\d_]+", fold(text), flags=re.UNICODE)
    return [t for t in toks if len(t) >= min_len and t not in _PT_STOP]


# ---------------------------------------------------------------------------
# Issues
# ---------------------------------------------------------------------------
@dataclass
class Issue:
    level: str      # "FAIL" | "WARN"
    code: str       # e.g. "C3"
    entry: str
    reason: str

    def as_dict(self) -> dict:
        return {"level": self.level, "code": self.code,
                "entry": self.entry, "reason": self.reason}


# ---------------------------------------------------------------------------
# Adjudication access (flexible key names)
# ---------------------------------------------------------------------------
def _adj_fields(item: dict) -> dict:
    def pick(*names):
        for n in names:
            if item.get(n) not in (None, ""):
                return item.get(n)
        return None
    guarantee = pick("guarantee", "garantia") or []
    if isinstance(guarantee, str):
        guarantee = [guarantee]
    return {
        "term": (pick("term", "termo") or "").strip(),
        "status": (pick("status", "estatuto") or "").strip(),
        "test": (pick("test", "teste_decisivo", "teste") or "").strip(),
        "guarantee": list(guarantee),
        "definition": (pick("definition", "definicao") or "").strip(),
        "structural": (pick("structural", "estrutural") or "").strip(),
        "contrast_reason": (pick("contrast_reason", "razao_contraste") or "").strip(),
    }


def _adjudication_list(skeleton: dict) -> list[dict]:
    raw = skeleton.get("adjudication", [])
    if isinstance(raw, dict):
        out = []
        for term, val in raw.items():
            merged = dict(val or {})
            merged.setdefault("term", term)
            out.append(_adj_fields(merged))
        return out
    return [_adj_fields(it) for it in (raw or []) if isinstance(it, dict)]


# ---------------------------------------------------------------------------
# Consistency checks (C1–C10; C7 omitted for Onto.PT)
# ---------------------------------------------------------------------------
def run_checks(skeleton: dict) -> tuple[list[Issue], dict]:
    issues: list[Issue] = []
    def fail(code, entry, reason): issues.append(Issue("FAIL", code, entry, reason))
    def warn(code, entry, reason): issues.append(Issue("WARN", code, entry, reason))

    whitelist = skeleton.get("stage1_whitelist", []) or []
    adj = _adjudication_list(skeleton)
    disjoint_with = skeleton.get("disjoint_with", []) or []
    axis = skeleton.get("axis", "") or ""

    def gloss_of(e):
        return (e.get("gloss") or e.get("glosa") or "")

    def members_of(e):
        return e.get("synonyms") or e.get("members") or []

    # C1 — required fields
    for field_ in ("class_id", "pref_label", "axis"):
        if not str(skeleton.get(field_, "") or "").strip():
            fail("C1", field_, "campo obrigatório em branco")
    stems = skeleton.get("focus_stems", []) or []
    if not (isinstance(stems, list) and len([s for s in stems if str(s).strip()]) >= 1):
        fail("C1", "focus_stems", "requer ≥1 radical (stem)")

    # C2 — every whitelist decision valid, no blanks
    for e in whitelist:
        d = str(e.get("decision", "") or "").strip()
        tag = e.get("ili_offset") or e.get("synset_offset") or "?"
        if not d:
            fail("C2", tag, "decisão em branco")
        elif d not in DECISIONS:
            fail("C2", tag, f"decisão inválida: {d!r} (esperado UF|RT|exclude)")

    member_terms: set[str] = set()
    exclude_member_terms: set[str] = set()
    for e in whitelist:
        d = str(e.get("decision", "") or "").strip()
        syns = {norm_term(s) for s in members_of(e)}
        if d in ADMIT_DECISIONS:
            member_terms |= syns
        elif d == "exclude":
            exclude_member_terms |= syns

    # C3 — UF/RT entries: expected_axis_phrase present AND its words occur in gloss
    for e in whitelist:
        d = str(e.get("decision", "") or "").strip()
        if d not in ADMIT_DECISIONS:
            continue
        tag = e.get("ili_offset") or e.get("synset_offset") or "?"
        phrase = str(e.get("expected_axis_phrase", "") or "").strip()
        gloss_fold = fold(gloss_of(e))
        if not phrase:
            fail("C3", tag, "expected_axis_phrase em branco para entrada admitida")
            continue
        missing = [t for t in content_tokens(phrase, min_len=2) if t not in gloss_fold]
        if missing:
            fail("C3", tag,
                 f"palavras de expected_axis_phrase ausentes da glosa: {missing}")

    # C4 — exclude entries must not contribute positive members downstream
    for a in adj:
        if a["status"] in POSITIVE_STATUSES:
            nt = norm_term(a["term"])
            if nt in exclude_member_terms and nt not in member_terms:
                fail("C4", a["term"],
                     f"membro de synset excluído (off-axis) roteado como {a['status']}")

    # C5 — WARN: UF entry gloss with no lexical overlap with axis
    axis_toks = set(content_tokens(axis))
    for e in whitelist:
        if str(e.get("decision", "") or "").strip() == "UF":
            g = set(content_tokens(gloss_of(e)))
            if axis_toks and not (axis_toks & g):
                tag = e.get("ili_offset") or e.get("synset_offset") or "?"
                warn("C5", tag,
                     "glosa UF sem sobreposição lexical com o eixo — rever decisão")

    # C6 — adjudication ↔ whitelist coherence (no relations in Onto.PT export)
    for a in adj:
        st, nt = a["status"], norm_term(a["term"])
        if st not in STATUSES:
            continue
        traced = (
            nt in member_terms
            or bool(NONLEXICAL_GUARANTEES & set(a["guarantee"]))
            or (st == "contraste" and bool(a["contrast_reason"]))
        )
        if not traced:
            fail("C6", a["term"],
                 f"{st} sem rasto a synset admitido e sem garantia não-lexical "
                 "(nem contrast_reason)")

    # C7 — (nomes de qualidade → attribute_bucket): NÃO se aplica ao Onto.PT.

    # C8 — contrast terms need a one-line human justification
    for a in adj:
        if a["status"] == "contraste" and not a["contrast_reason"]:
            warn("C8", a["term"],
                 "sem contrast_reason (armadilha «heterogéneo»: negação ortogonal ≠ contraste)")

    # C9 — estipulativa needs definition AND disjoint_with target
    for a in adj:
        if "estipulativa" in a["guarantee"]:
            if not a["definition"]:
                fail("C9", a["term"], "garantia estipulativa sem definition")
            if not (a["structural"] or disjoint_with):
                fail("C9", a["term"],
                     "garantia estipulativa sem alvo owl:disjointWith "
                     "(structural ou disjoint_with)")
            if a["structural"] and disjoint_with and a["structural"] not in disjoint_with:
                warn("C9", a["term"],
                     f"structural {a['structural']!r} não consta em disjoint_with")

    # C10 — integridade dos offsets: entrada admitida sem offset é inválida
    for e in whitelist:
        d = str(e.get("decision", "") or "").strip()
        off = str(e.get("ili_offset") or e.get("synset_offset") or "").strip()
        if d in ADMIT_DECISIONS and not off:
            fail("C10", "(entrada sem id)",
                 "synset admitido sem id (ili_offset/synset_offset) — não persiste")

    facts = {
        "member_terms": member_terms, "exclude_member_terms": exclude_member_terms,
        "adjudication": adj,
    }
    return issues, facts


# ---------------------------------------------------------------------------
# Build engine-ready spec (translate skeleton → phase0_skos schema; strip meta)
# ---------------------------------------------------------------------------
def build_engine_spec(skeleton: dict, facts: dict) -> dict:
    adj = facts["adjudication"]
    member_terms = facts["member_terms"]

    def gloss_of(e):
        return e.get("gloss") or e.get("glosa") or ""

    def members_of(e):
        return e.get("synonyms") or e.get("members") or []

    stage1 = []
    for e in skeleton.get("stage1_whitelist", []) or []:
        stage1.append({
            "ili_offset": e.get("ili_offset") or e.get("synset_offset") or "",
            "glosa": gloss_of(e),                          # gloss → glosa
            "decision": str(e.get("decision", "") or "").strip(),
            "members": list(members_of(e)),                # synonyms → members
        })

    adjudication: dict[str, dict] = {}
    manual_terms = []
    for a in adj:
        if not a["term"] or a["status"] not in STATUSES:
            continue
        adjudication[a["term"]] = {
            "status": a["status"], "test": a["test"], "guarantee": a["guarantee"],
            "definition": a["definition"], "structural": a["structural"],
        }
        nt = norm_term(a["term"])
        if nt not in member_terms and (NONLEXICAL_GUARANTEES & set(a["guarantee"])):
            manual_terms.append({
                "term": a["term"], "provenance": list(a["guarantee"]),
                "definition": a["definition"],
            })

    disjoint_classes = {name: [] for name in (skeleton.get("disjoint_with", []) or [])}
    gating = skeleton.get("gating", {}) or {}

    spec = {
        "class_id": skeleton.get("class_id", ""),
        "pref_label": skeleton.get("pref_label", ""),
        "axis": skeleton.get("axis", ""),
        "focus_stems": list(skeleton.get("focus_stems", []) or []),
        "gating": {
            "weight_min": float(gating.get("weight_min", 0.5)),
            "min_cooccurrence": int(gating.get("min_cooccurrence", 2)),
        },
        "fuzzy_resources": list(skeleton.get("fuzzy_resources", ["contopt"]) or ["contopt"]),
        "stage1_whitelist": stage1,
        "dictionary_attestations": list(skeleton.get("dictionary_attestations", []) or []),
        "manual_terms": manual_terms,
        "exclusion_patterns": list(skeleton.get("exclusion_patterns", []) or []),
        "adjudication": adjudication,
        "disjoint_classes": disjoint_classes,
        "_provenance": {
            "finalized_from": "skos.spec.skeleton",
            "finalizer": "spec_finalize_skos.py",
            "generated": datetime.now().isoformat(timespec="seconds"),
        },
    }
    if skeleton.get("pos"):
        spec["pos"] = skeleton["pos"]
    if skeleton.get("superclass"):
        spec["superclass"] = skeleton["superclass"]
    return spec


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def render_issues_md(class_id: str, issues: list[Issue]) -> str:
    fails = [i for i in issues if i.level == "FAIL"]
    warns = [i for i in issues if i.level == "WARN"]
    L = [f"# Fase 0 (Onto.PT) — problemas da spec **{class_id or '?'}**", "",
         f"- **FAIL:** {len(fails)}   ·   **WARN:** {len(warns)}",
         f"- **Gerado:** {datetime.now().isoformat(timespec='seconds')}", "",
         "> Nenhuma spec executável é emitida enquanto existir um FAIL. "
         "Este relatório não corrige nada — indica o que o humano deve rever.", "",
         "| nível | check | entrada | motivo |", "|-------|-------|---------|--------|"]
    for i in fails + warns:
        reason = i.reason.replace("|", "\\|")
        entry = str(i.entry).replace("|", "\\|")
        L.append(f"| {i.level} | {i.code} | {entry} | {reason} |")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# API + CLI
# ---------------------------------------------------------------------------
def finalize(skeleton_path: Path, outdir: Path) -> dict:
    skeleton = json.loads(Path(skeleton_path).read_text(encoding="utf-8"))

    issues, facts = run_checks(skeleton)
    fails = [i for i in issues if i.level == "FAIL"]
    class_id = str(skeleton.get("class_id", "") or "").strip() or Path(skeleton_path).stem

    outdir.mkdir(parents=True, exist_ok=True)
    result = {
        "class_id": class_id,
        "ready": not fails,
        "issues": [i.as_dict() for i in issues],
        "n_fail": len(fails),
        "n_warn": len(issues) - len(fails),
    }

    if fails:
        issues_path = outdir / f"{class_id}.skos.issues.md"
        issues_path.write_text(render_issues_md(class_id, issues), encoding="utf-8")
        result["issues_path"] = str(issues_path)
        return result

    spec = build_engine_spec(skeleton, facts)
    spec_path = outdir / f"{class_id}.json"
    spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    result["spec_path"] = str(spec_path)
    if any(i.level == "WARN" for i in issues):
        issues_path = outdir / f"{class_id}.skos.issues.md"
        issues_path.write_text(render_issues_md(class_id, issues), encoding="utf-8")
        result["issues_path"] = str(issues_path)
    return result


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(
        description="Validar e finalizar uma spec Fase 0 (Onto.PT) a partir de um esqueleto.")
    ap.add_argument("skeleton", help="ficheiro <classe>.skos.spec.skeleton.json preenchido")
    ap.add_argument("--outdir", default=str(here / "fase0"), help="pasta de saída")
    args = ap.parse_args()

    try:
        result = finalize(Path(args.skeleton), Path(args.outdir))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERRO: não foi possível ler o esqueleto: {exc}")
        return 2

    if result["ready"]:
        if result.get("issues_path"):
            print(f"Avisos (WARN): {result['n_warn']} — ver {result['issues_path']}")
        spec = result["spec_path"]
        print(f"SPEC READY — run: python phase0_skos.py {spec} --db ontopt.sqlite")
        return 0

    print(f"SPEC NÃO PRONTA — {result['n_fail']} FAIL, {result['n_warn']} WARN.")
    print(f"Problemas: {result['issues_path']}")
    for i in result["issues"]:
        if i["level"] == "FAIL":
            print(f"  [FAIL] {i['code']} {i['entry']}: {i['reason']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
