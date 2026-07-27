"""Faixas OEWN (WordNet) e OWN-PT na fusão — duas fontes, um export de facetas.

Disciplina:
  * **WordNet (OEWN)** — corroboração EN + relações tipadas (antonym / similar_to)
    em ``sinalizacao``; nunca ``provenance`` com estatuto admissivo.
  * **OWN-PT** — coluna própria: lemas PT obtidos via ILI (``own-pt:1.0.0``)
    como ``atestado`` (fundamento de entrada, NÃO estatuto UF/RT).
  * Só sentidos do eixo (ILIs em ``map`` human/cili da tabela de equivalência).
  * Nenhum ILI fabricado — usa-se o campo ``ili`` nativo do export.
"""

from __future__ import annotations

import json
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from .ili_bridge import is_human_row, load_table
from .settings import ROOT
from .workspace import ClassWorkspace

OWN_PT_FALLBACK_SPEC = "own-pt:1.0.0"


def _norm(w: str) -> str:
    nfkd = unicodedata.normalize("NFKD", w or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).casefold().strip()


def _own_pt_specifier() -> str:
    try:
        from .engines import load_oewn_backend
        from .settings import load_config

        cfg = load_config()
        pinned = cfg.get("own_pt")
        if pinned:
            return str(pinned)
        backend = load_oewn_backend()
        return getattr(backend, "OWN_PT_SPECIFIER", None) or OWN_PT_FALLBACK_SPEC
    except Exception:  # noqa: BLE001
        return OWN_PT_FALLBACK_SPEC


def find_facets_export(ws: ClassWorkspace) -> Optional[Path]:
    """Prefer class ``exports/*.facets.json``; only then WordNet/exports fallback."""
    pools: list[Path] = []
    pools += sorted(
        ws.exports.glob("*.facets.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    wn_exp = ROOT / "WordNet" / "exports"
    if wn_exp.exists():
        pools += sorted(
            wn_exp.rglob("*.facets.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
    for p in pools:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        syns = data.get("synsets") or []
        if not syns:
            continue
        if not str((syns[0] or {}).get("ili") or "").startswith("i"):
            continue
        tagged = (data.get("class_id") or "").strip()
        if tagged and tagged != ws.class_id and p.parent != ws.exports:
            continue
        return p
    return None


def adjudicated_ilis(ws: ClassWorkspace) -> dict[str, str]:
    """OEWN ILIs convocáveis from ``map``: human-adjudicated or CILI identity."""
    doc = load_table(ws)
    if not doc:
        return {}
    out: dict[str, str] = {}
    for r in doc.get("map", []) or []:
        ili = r.get("oewn_ili")
        if not ili:
            continue
        src = str(r.get("source", ""))
        if is_human_row(r) or src.startswith("cili:"):
            out[ili] = src
    return out


def build_wordnet_result(
    class_id: str, facets_path: Optional[Path] = None
) -> dict[str, Any]:
    """Backward-compatible wrapper — builds both WordNet and OWN-PT tracks."""
    return build_wordnet_and_ownpt_results(class_id, facets_path=facets_path)


def build_wordnet_and_ownpt_results(
    class_id: str, facets_path: Optional[Path] = None
) -> dict[str, Any]:
    """Emit ``*.WordNet.result.json`` and ``*.OWN-PT.result.json`` from one facets export."""
    ws = ClassWorkspace.open(class_id)
    ws.ensure()
    facets_path = facets_path or find_facets_export(ws)
    if facets_path is None:
        return {
            "ok": False,
            "error": "sem export de facetas OEWN (exports/*.facets.json)",
        }
    allowed = adjudicated_ilis(ws)
    if not allowed:
        return {
            "ok": False,
            "error": (
                "tabela ILI sem pares em map (human ou cili:) — use "
                "tabela ili_equivalence.json legada em out/ (junção runtime = CILI)"
            ),
        }

    data = json.loads(Path(facets_path).read_text(encoding="utf-8"))
    own_pt_lex = _own_pt_specifier()
    meta = ws.load_meta()
    pref = meta.get("pref_label") or ws.class_id
    generated = datetime.now().isoformat(timespec="seconds")

    wn_sina: dict[str, dict] = {}
    own_atest: dict[str, dict] = {}
    syn_block: list[dict] = []
    convoked, skipped = [], []

    for s in data.get("synsets", []) or []:
        ili = s.get("ili")
        if not ili:
            continue
        if ili not in allowed:
            skipped.append(ili)
            continue
        convoked.append(ili)
        pt_lemmas = list(s.get("pt_lemmas") or [])
        en_lemmas = list(s.get("lemmas") or [])
        syn_block.append({
            "name": s.get("name"),
            "ili": ili,
            "pos": s.get("pos"),
            "pt_lemmas": pt_lemmas,
            "lemmas": en_lemmas,
        })

        # --- OWN-PT column: Portuguese lemmas via ILI (attestation only) ---
        for w in pt_lemmas:
            nw = _norm(w)
            if not nw or nw in own_atest:
                continue
            own_atest[nw] = {
                "display": (w or "").replace("_", " "),
                "reason": (
                    f"atestado OWN-PT [{own_pt_lex}] via ILI {ili} · "
                    f"{s.get('name')}"
                ),
                "offsets_ili": [ili],
                "lexicon": own_pt_lex,
            }

        # --- WordNet/OEWN: English lemmas when no PT bridge; typed relations ---
        if not pt_lemmas:
            for w in en_lemmas:
                nw = _norm(w)
                if not nw or nw in wn_sina:
                    continue
                wn_sina[nw] = {
                    "display": (w or "").replace("_", " "),
                    "reason": (
                        f"atestado na WordNet [en_lemma (sem correspondência "
                        f"own-pt)] · {s.get('name')} · ILI {ili}"
                    ),
                    "offsets_ili": [ili],
                }

        rel = s.get("relations") or {}
        for kind, note in (
            ("antonym", "material de contraste (antonym)"),
            ("similar_to", "vizinho similar_to"),
        ):
            for tgt in rel.get(kind) or []:
                t_ili = tgt.get("ili")
                for w in tgt.get("words") or []:
                    nw = _norm(w)
                    if not nw or nw in wn_sina:
                        continue
                    wn_sina[nw] = {
                        "display": (w or "").replace("_", " "),
                        "reason": (
                            f"{note} de {ili} ({s.get('name')}) — "
                            "sem estatuto; adjudicação humana"
                        ),
                        "offsets_ili": [t_ili] if t_ili else [],
                    }

    wn_result = {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": "(faixa OEWN — corroboração EN / relações tipadas; sem adjudicação)",
        "generated": generated,
        "source": "WordNet (OEWN facets export)",
        "facets_export": str(facets_path),
        "convoked_ilis": convoked,
        "skipped_ilis": skipped,
        "provenance": [],
        "synsets": syn_block,
        "sinalizacao": wn_sina,
        "_note": (
            "Faixa OEWN: lemas EN e relações tipadas em sinalizacao. "
            "Lemas PT via ILI → ficheiro OWN-PT.result.json (coluna própria)."
        ),
    }
    wn_out = ws.results / f"{ws.class_id}.WordNet.result.json"
    wn_out.write_text(
        json.dumps(wn_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    own_result = {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": "(faixa OWN-PT — atestação PT via ILI; sem estatuto admissivo)",
        "generated": generated,
        "source": "OWN-PT (OpenWordNet-PT)",
        "lexicon": own_pt_lex,
        "facets_export": str(facets_path),
        "convoked_ilis": convoked,
        "skipped_ilis": skipped,
        "provenance": [],  # nunca UF/RT — só atestação
        "atestacao": own_atest,
        "sinalizacao": {},
        "_note": (
            "OpenWordNet-PT: fundamento de entrada (atestado) ancorado em ILI. "
            "NÃO atribui relação de vocabulário (UF/RT). "
            f"Léxico: {own_pt_lex}."
        ),
        "_pwn_derived": True,
    }
    own_out = ws.results / f"{ws.class_id}.OWN-PT.result.json"
    own_out.write_text(
        json.dumps(own_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    return {
        "ok": True,
        "path": str(wn_out),
        "ownpt_path": str(own_out),
        "lexicon": own_pt_lex,
        "convoked": convoked,
        "skipped": skipped,
        "n_sinalizacao": len(wn_sina),
        "n_atestacao": len(own_atest),
        "facets": str(facets_path),
    }
