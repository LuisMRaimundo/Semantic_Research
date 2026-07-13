#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the OEWN↔PULO ILI equivalence table from LEMMA evidence (never string edits).

The WordNet export emits, per synset, an ILI (e.g. "i10771") and the Portuguese
lemmas obtained via ILI-mediated translate("own-pt"). The PULO export emits, per
synset, an `ili_offset` (ili-30-XXXXXXXX-<pos>), a `pos` and a `synonyms` list.
Two synsets denote the SAME interlingual concept when they share ≥1 lemma AND the
same POS. This module turns that evidence into a declared equivalence table that
LexWarrant (and only LexWarrant, read-only) uses to join across the two ILI
namespaces.

Rules (enforced):
  * Matching is by SHARED PT LEMMA + POS. Never by numeric offset similarity.
  * Every emitted row carries its shared_lemmas as evidence. No evidence → no row.
  * Exactly one PULO match  → confidence "high" (goes to `map`).
  * Several PULO matches     → confidence "review" (surfaced, NEVER auto-picked).
  * No PULO match            → the OEWN ILI is listed in `unmatched`.

Output (ili_equivalence.json):
  { "class": "...", "generated": "...",
    "map":       [ {oewn_ili, pulo_ili, evidence:{shared_lemmas, pos}, confidence:"high"} ],
    "review":    [ {oewn_ili, pulo_ili, evidence:{shared_lemmas, pos}, confidence:"review"} ],
    "unmatched": [ {oewn_ili, pos, lemmas:[...]} ],
    "coverage":  {"map": N, "review": N, "unmatched": N} }

Usage:
    python build_ili_equivalence.py --wordnet WN.result.json --pulo pulo_x.json
                                    [--class X] [--out ili_equivalence.json]

Sem dependências além da biblioteca padrão.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Optional

# CILI (catálogo canónico GWA, vendorizado) — identidade directa de ids.
# Sem CILI disponível, o construtor degrada para a inferência por lema.
try:
    from cili_resolver import CILI_VERSION, cili_resolve
except ImportError:  # pragma: no cover
    CILI_VERSION = None

    def cili_resolve(_id):  # type: ignore
        return None

_OEWN_ID_RE = re.compile(r"oewn-\d+-([a-z])\b")
_ILI_RE = re.compile(r"\b(i\d+)\b")


def strip_accents(text: str) -> str:
    nfkd = unicodedata.normalize("NFKD", text or "")
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def norm_lemma(w: str) -> str:
    """Diacritic-insensitive, casefolded lemma key for MATCHING only."""
    return strip_accents(w or "").casefold().strip().replace("_", " ")


def norm_pos(p: str) -> str:
    """Normalise POS; satellite adjectives ('s') collapse to adjective ('a')."""
    p = (p or "").strip().lower()
    return "a" if p == "s" else p


# ---------------------------------------------------------------------------
# Ingest
# ---------------------------------------------------------------------------
def load_wordnet_synsets(data: dict) -> list[dict]:
    """Return [{ili, pos, lemmas:[..]}] from a WordNet facets export OR result.json.

    Facets export: top-level `synsets` with `ili`, `pos`, `pt_lemmas`.
    result.json:  `sinalizacao` entries carrying `offsets_ili` and a `reason` that
                  embeds the oewn id (for POS) — grouped back into per-ILI synsets.
    Only PT lemmas are used as evidence (English lemmas can't match PULO anyway).
    """
    out: list[dict] = []
    if isinstance(data.get("synsets"), list):
        for s in data["synsets"]:
            ili = s.get("ili")
            if not ili:
                continue
            lemmas = list(s.get("pt_lemmas") or [])
            out.append({"ili": ili, "pos": norm_pos(s.get("pos")), "lemmas": lemmas})
        return out

    sina = data.get("sinalizacao")
    if isinstance(sina, dict):
        groups: dict[str, dict] = {}
        for _key, entry in sina.items():
            offs = entry.get("offsets_ili") or entry.get("offsets") or []
            if not offs:
                continue
            ili = offs[0]
            reason = entry.get("reason", "") or ""
            is_pt = "pt_lemma" in reason
            g = groups.setdefault(ili, {"ili": ili, "pos": "", "lemmas": []})
            if not g["pos"]:
                m = _OEWN_ID_RE.search(reason)
                if m:
                    g["pos"] = norm_pos(m.group(1))
            if is_pt:  # only Portuguese lemmas are usable evidence against PULO
                disp = (entry.get("display") or _key).strip()
                if disp:
                    g["lemmas"].append(disp)
        out = list(groups.values())
    return out


def load_pulo_synsets(data: dict) -> list[dict]:
    """Return [{ili_offset, pos, synonyms:[..]}] from a PULO thesaurus export."""
    out: list[dict] = []
    for s in data.get("synsets", []) or []:
        ili_offset = None
        ili = s.get("ili")
        if isinstance(ili, list) and ili:
            ili_offset = ili[0].get("ili_offset")
        elif isinstance(ili, str):
            ili_offset = ili
        ili_offset = ili_offset or s.get("ili_offset")
        if not ili_offset:
            continue
        out.append({
            "ili_offset": ili_offset,
            "pos": norm_pos(s.get("pos")),
            "synonyms": list(s.get("synonyms") or []),
        })
    return out


# ---------------------------------------------------------------------------
# Match
# ---------------------------------------------------------------------------
def build_equivalence(wn_synsets: list[dict], pulo_synsets: list[dict],
                      class_id: str = "") -> dict:
    pulo_index = []
    # índice por identidade CILI: cili_resolve(ili-30-…) -> "i…"
    pulo_by_cili: dict[str, dict] = {}
    for s in pulo_synsets:
        pulo_index.append((s, {norm_lemma(w) for w in s["synonyms"] if norm_lemma(w)}))
        ic = cili_resolve(s.get("ili_offset"))
        if ic and ic not in pulo_by_cili:
            pulo_by_cili[ic] = s

    map_rows: list[dict] = []
    review_rows: list[dict] = []
    unmatched: list[dict] = []

    for w in wn_synsets:
        w_pos = norm_pos(w["pos"])

        # --- passo CILI: identidade canónica id↔offset (substitui a
        # inferência por lema quando existe mapeamento autoritativo) ---
        ic = cili_resolve(w.get("ili"))
        if ic and ic in pulo_by_cili:
            s = pulo_by_cili[ic]
            w_norm0 = {norm_lemma(x) for x in w.get("lemmas", []) if norm_lemma(x)}
            shared_disp = sorted({syn for syn in s["synonyms"]
                                  if norm_lemma(syn) in w_norm0})
            map_rows.append({
                "oewn_ili": w["ili"],
                "pulo_ili": s["ili_offset"],
                "evidence": {"cili_identity": ic,
                             "shared_lemmas": shared_disp, "pos": w_pos},
                "confidence": "high",
                "source": f"cili:{CILI_VERSION}",
            })
            continue    # identidade autoritativa: sem candidatos por lema

        w_norm = {norm_lemma(x) for x in w["lemmas"] if norm_lemma(x)}
        if not w_norm:
            unmatched.append({"oewn_ili": w["ili"], "pos": w_pos, "lemmas": list(w["lemmas"]),
                              "why": "sem lemas PT para evidência"})
            continue

        candidates = []
        for s, s_norm in pulo_index:
            if w_pos and s["pos"] and s["pos"] != w_pos:
                continue
            shared = w_norm & s_norm
            if shared:
                # keep display-cased shared lemmas from PULO synonyms
                shared_disp = sorted({syn for syn in s["synonyms"]
                                      if norm_lemma(syn) in shared})
                candidates.append((s, shared_disp))

        if not candidates:
            unmatched.append({"oewn_ili": w["ili"], "pos": w_pos, "lemmas": list(w["lemmas"]),
                              "why": "nenhum synset PULO partilha lema+POS"})
        elif len(candidates) == 1:
            s, shared_disp = candidates[0]
            map_rows.append({
                "oewn_ili": w["ili"],
                "pulo_ili": s["ili_offset"],
                "evidence": {"shared_lemmas": shared_disp, "pos": w_pos},
                "confidence": "high",
                "source": "auto: shared-lemma (par único)",
            })
        else:  # ambiguous → surface each, never auto-pick
            for s, shared_disp in candidates:
                review_rows.append({
                    "oewn_ili": w["ili"],
                    "pulo_ili": s["ili_offset"],
                    "evidence": {"shared_lemmas": shared_disp, "pos": w_pos},
                    "confidence": "review",
                    "source": "auto: shared-lemma (ambíguo)",
                })

    from datetime import datetime
    return {
        "class": class_id,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "map": map_rows,
        "review": review_rows,
        "unmatched": unmatched,
        "coverage": {"map": len(map_rows), "review": len(review_rows),
                     "unmatched": len(unmatched)},
    }


def build_from_files(wordnet_path: Path, pulo_path: Path,
                     class_id: Optional[str] = None) -> dict:
    wn_data = json.loads(Path(wordnet_path).read_text(encoding="utf-8"))
    pulo_data = json.loads(Path(pulo_path).read_text(encoding="utf-8"))
    cls = class_id or wn_data.get("class_id") or wn_data.get("class") or ""
    wn_syn = load_wordnet_synsets(wn_data)
    pulo_syn = load_pulo_synsets(pulo_data)
    return build_equivalence(wn_syn, pulo_syn, cls)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(
        description="Constrói a tabela de equivalência ILI OEWN↔PULO (evidência por lema).")
    ap.add_argument("--wordnet", required=True, help="WordNet .result.json ou export de facetas")
    ap.add_argument("--pulo", required=True, help="export PULO (pulo_*.json)")
    ap.add_argument("--class", dest="class_id", default=None, help="id da classe (opcional)")
    ap.add_argument("--out", default="ili_equivalence.json", help="ficheiro de saída")
    args = ap.parse_args()

    doc = build_from_files(Path(args.wordnet), Path(args.pulo), args.class_id)
    Path(args.out).write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    cov = doc["coverage"]
    print(f"Tabela ILI OEWN↔PULO: {cov['map']} mapeados (high), "
          f"{cov['review']} para revisão, {cov['unmatched']} sem correspondência.")
    print(f"Saída: {args.out}")
    if doc["review"]:
        print("  Revisão (ambíguos, não resolvidos automaticamente):")
        for r in doc["review"]:
            print(f"    {r['oewn_ili']} ↔ {r['pulo_ili']}  ({', '.join(r['evidence']['shared_lemmas'])})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
