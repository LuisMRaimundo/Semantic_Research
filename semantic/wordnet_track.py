"""Faixa WordNet na fusão — adapta o export OEWN (facets) a um result.json.

Disciplina (contrato Tarefa B):
  * a faixa CORROBORA/ancora — não admite nem reclassifica: todas as entradas
    saem como `sinalizacao` (nunca `provenance` com estatuto);
  * só são convocados os sentidos DO EIXO: os OEWN ILIs presentes em linhas
    `map` com `source: human-adjudicated…` da tabela ili_equivalence.json
    (i60712/vestuário e i33388/verbo ficam de fora por não terem adjudicação);
  * relações tipadas (antonym / similar_to) entram como material ancorado em
    ILI, sem forçar estatuto;
  * nenhum ILI é fabricado — usa-se apenas o campo `ili` nativo do export.
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


def _norm(w: str) -> str:
    nfkd = unicodedata.normalize("NFKD", w or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c)).casefold().strip()


def find_facets_export(ws: ClassWorkspace) -> Optional[Path]:
    """Prefer class ``exports/*.facets.json``; only then WordNet/exports fallback."""
    pools: list[Path] = []
    # Class-local FIRST — avoids picking a leftover «uniform» bundle for Compósita
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
        # If the export names a class_id, require a match when falling back
        tagged = (data.get("class_id") or "").strip()
        if tagged and tagged != ws.class_id and p.parent != ws.exports:
            continue
        return p
    return None


def adjudicated_ilis(ws: ClassWorkspace) -> dict[str, str]:
    """OEWN ILIs convocáveis from ``map``: human-adjudicated or CILI identity.

    CILI rows are canonical GWA identity (already allowed in ``map`` by the
    bridge); human rows are GUI promotions. Auto/review pairs never qualify.
    """
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


def build_wordnet_result(class_id: str,
                         facets_path: Optional[Path] = None) -> dict[str, Any]:
    ws = ClassWorkspace.open(class_id)
    ws.ensure()
    facets_path = facets_path or find_facets_export(ws)
    if facets_path is None:
        return {"ok": False, "error": "sem export de facetas OEWN "
                                      "(WordNet/exports/*.facets.json)"}
    allowed = adjudicated_ilis(ws)
    if not allowed:
        return {"ok": False, "error":
                "tabela ILI sem pares em map (human ou cili:) — use "
                "«5 · Ponte ILI…» (promova review→map) ou coloque "
                "ili_equivalence.json em out/"}

    data = json.loads(Path(facets_path).read_text(encoding="utf-8"))
    sina: dict[str, dict] = {}
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
        syn_block.append({"name": s.get("name"), "ili": ili,
                          "pos": s.get("pos"),
                          "pt_lemmas": list(s.get("pt_lemmas") or []),
                          "lemmas": list(s.get("lemmas") or [])})
        words = list(s.get("pt_lemmas") or [])
        via = "pt_lemma (ILI)"
        if not words:
            words = list(s.get("lemmas") or [])
            via = "en_lemma (sem correspondência own-pt)"
        for w in words:
            nw = _norm(w)
            if not nw or nw in sina:
                continue
            sina[nw] = {
                "display": (w or "").replace("_", " "),
                "reason": f"atestado na WordNet [{via}] · {s.get('name')} · ILI {ili}",
                "offsets_ili": [ili],
            }
        # relações tipadas: material ancorado em ILI, SEM estatuto forçado
        rel = s.get("relations") or {}
        for kind, note in (("antonym", "material de contraste (antonym)"),
                           ("similar_to", "vizinho similar_to")):
            for tgt in rel.get(kind) or []:
                t_ili = tgt.get("ili")
                for w in tgt.get("words") or []:
                    nw = _norm(w)
                    if not nw or nw in sina:
                        continue
                    sina[nw] = {
                        "display": (w or "").replace("_", " "),
                        "reason": (f"{note} de {ili} ({s.get('name')}) — "
                                   "sem estatuto; adjudicação humana"),
                        "offsets_ili": [t_ili] if t_ili else [],
                    }

    result = {
        "class_id": ws.class_id,
        "pref_label": ws.load_meta().get("pref_label") or ws.class_id,
        "axis": "(faixa WordNet — corroboração ancorada em ILI; sem adjudicação)",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source": "WordNet (OEWN facets export)",
        "facets_export": str(facets_path),
        "convoked_ilis": convoked,
        "skipped_ilis": skipped,       # ex.: i60712 (vestuário), i33388 (verbo)
        "provenance": [],              # WordNet não admite (sem protocolo UF/RT)
        "synsets": syn_block,
        "sinalizacao": sina,
        "_note": ("Faixa de CORROBORAÇÃO: só sentidos do eixo adjudicados na "
                  "tabela ILI; entradas em sinalizacao, nunca estatutos."),
    }
    out = ws.results / f"{ws.class_id}.WordNet.result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    return {"ok": True, "path": str(out), "convoked": convoked,
            "skipped": skipped, "n_sinalizacao": len(sina),
            "facets": str(facets_path)}
