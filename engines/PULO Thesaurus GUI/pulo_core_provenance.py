#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A.1 — diagnose the PULO provenance of a class's CORE terms BEFORE admitting.

For each core term, list every PULO synset that contains it (as a headword/synonym
OR as a relation target's word), with synset_offset, canonical ili_offset, POS,
gloss, and the relation type through which it was reached — plus the glosa↔eixo
verdict (does the containing synset's gloss match the class axis?).

This is the human gate: a term is only whitelisted for admission if it sits in an
ON-AXIS synset. A term whose ONLY path is an unnamed relation with an off-axis gloss
is flagged "STOP — human review", never admitted on that evidence alone.

Importable (build_core_provenance) + CLI.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional

DEFAULT_CORE = ["constante", "invariável", "imutável", "inalterável",
                "constância", "invariabilidade", "imutabilidade", "uniforme"]


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def fold(text: str) -> str:
    return strip_accents(text or "").lower().strip()


def _canon_pwn(synset_offset: str, ili_field=None) -> str:
    """Local PWN 3.0 id for provenance (never fabricate CILI / ili-30-…).

    ``por-30-XXXXXXXX-p`` / legacy ``ili-30-XXXXXXXX-p`` → ``pwn30-XXXXXXXX-p``.
    Official CILI ``i…`` is resolved elsewhere via the CILI map / OEWN.
    """
    raw = ""
    if isinstance(ili_field, list) and ili_field:
        first = ili_field[0] if isinstance(ili_field[0], dict) else {}
        raw = (
            (first.get("pwn_id") or first.get("ili_offset") or "").strip()
        )
    for candidate in (raw, synset_offset or ""):
        m = re.match(
            r"^(?:pwn30-|ili-30-|[a-z]{2,4}-30-)(\d{8}-[a-z])$",
            candidate or "",
            re.I,
        )
        if m:
            return f"pwn30-{m.group(1).lower()}"
        m = re.match(r"^(\d{8}-[a-z])$", candidate or "", re.I)
        if m:
            return f"pwn30-{m.group(1).lower()}"
    return synset_offset or "?"


def build_core_provenance(export: dict, axis_terms: list[str],
                          core_terms: list[str]) -> dict:
    axis_folded = [fold(t) for t in axis_terms]

    def on_axis(gloss: str) -> bool:
        g = fold(gloss)
        return any(t and t in g for t in axis_folded)

    core_norm = {fold(t): t for t in core_terms}
    hits: dict[str, list[dict]] = {t: [] for t in core_terms}

    for syn in export.get("synsets", []):
        s_off = syn.get("synset_offset", "?")
        pwn = _canon_pwn(s_off, syn.get("ili"))
        pos = syn.get("pos", "")
        gloss = (syn.get("gloss") or "").strip()
        # headword synonyms
        for w in syn.get("synonyms", []) or []:
            key = fold(w)
            if key in core_norm:
                hits[core_norm[key]].append({
                    "synset_offset": s_off, "ili_offset": pwn, "pwn_id": pwn,
                    "pos": pos,
                    "gloss": gloss, "relation": "sinónimo (cabeça do synset)",
                    "on_axis": on_axis(gloss)})
        # relation-target words
        for rel in syn.get("relations", []) or []:
            label = rel.get("relation", "")
            for tgt in rel.get("targets", []) or []:
                t_off = tgt.get("synset_offset", s_off)
                t_pwn = _canon_pwn(t_off)
                t_gloss = (tgt.get("gloss") or "").strip()
                words = [w.strip() for w in re.split(r"[;,]", tgt.get("words", "")) if w.strip()]
                for w in words:
                    key = fold(w)
                    if key in core_norm:
                        hits[core_norm[key]].append({
                            "synset_offset": t_off, "ili_offset": t_pwn,
                            "pwn_id": t_pwn, "pos": "",
                            "gloss": t_gloss, "relation": f"alvo de «{label}»",
                            "on_axis": on_axis(t_gloss)})

    summary = {}
    for term, rows in hits.items():
        # dedupe by (synset_offset, relation)
        seen, uniq = set(), []
        for r in rows:
            k = (r["synset_offset"], r["relation"])
            if k in seen:
                continue
            seen.add(k)
            uniq.append(r)
        hits[term] = uniq
        any_on_axis = any(r["on_axis"] for r in uniq)
        summary[term] = {
            "present": bool(uniq),
            "any_on_axis": any_on_axis,
            "verdict": ("ADMISSÍVEL (tem synset on-axis)" if any_on_axis
                        else ("STOP — só off-axis/relação-não-nomeada" if uniq
                              else "AUSENTE do export PULO (não é membro de nenhum synset)")),
        }
    return {"core_terms": core_terms, "hits": hits, "summary": summary}


def render_md(doc: dict, class_id: str = "") -> str:
    L = []
    ap = L.append
    ap(f"# Proveniência PULO dos termos-núcleo — {class_id}".rstrip())
    ap("")
    ap("> Teste **glosa↔eixo**: um termo só é admissível se ocorrer num synset cuja "
       "glosa esteja no eixo da classe. Termos cujo único caminho é uma relação "
       "não-nomeada com glosa fora do eixo ficam **sinalizados** (nunca admitidos "
       "só por essa via).")
    ap("")
    ap("## Resumo")
    ap("")
    ap("| termo-núcleo | presente? | tem synset on-axis? | veredicto |")
    ap("|---|---|---|---|")
    for t in doc["core_terms"]:
        s = doc["summary"][t]
        ap(f"| {t} | {'sim' if s['present'] else 'não'} | "
           f"{'sim' if s['any_on_axis'] else 'não'} | {s['verdict']} |")
    ap("")
    for t in doc["core_terms"]:
        ap(f"## {t}")
        rows = doc["hits"][t]
        if not rows:
            ap("_Ausente do export PULO — não é sinónimo nem alvo de relação de "
               "nenhum synset desta pesquisa._")
            ap("")
            continue
        ap("| synset_offset | pwn_id (PWN 3.0) | POS | eixo? | relação | glosa |")
        ap("|---|---|---|---|---|---|")
        for r in rows:
            g = (r["gloss"] or "").replace("|", "\\|").replace("\n", " ").strip()
            pwn = r.get("pwn_id") or r.get("ili_offset") or "—"
            ap(f"| {r['synset_offset']} | {pwn} | {r['pos'] or '—'} | "
               f"{'ON' if r['on_axis'] else 'off'} | {r['relation']} | {g} |")
        ap("")
    return "\n".join(L)


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="A.1 — proveniência PULO dos termos-núcleo.")
    ap.add_argument("--pulo-export", required=True)
    ap.add_argument("--spec", default=None, help="spec PULO (para axis_terms/class_id)")
    ap.add_argument("--core", default=None, help="lista separada por vírgulas (opcional)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    export = json.loads(Path(args.pulo_export).read_text(encoding="utf-8"))
    axis_terms, class_id = [], ""
    if args.spec:
        spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
        axis_terms = spec.get("axis_terms", [])
        class_id = spec.get("class_id", "")
    core = [c.strip() for c in args.core.split(",")] if args.core else DEFAULT_CORE
    doc = build_core_provenance(export, axis_terms, core)
    Path(args.out).write_text(render_md(doc, class_id), encoding="utf-8")

    print(f"core_provenance: {args.out}")
    for t in core:
        s = doc["summary"][t]
        print(f"  {t}: {s['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
