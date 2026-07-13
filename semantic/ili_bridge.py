"""Ponte ILI — gerar/adjudicar a tabela ili_equivalence.json a partir da GUI.

Regras preservadas do protocolo:
  * o gerador nunca escolhe entre candidatos ambíguos (ficam em `review`);
  * promover review→map é decisão HUMANA, registada com `source` explícito;
  * regenerar a tabela NUNCA apaga promoções humanas anteriores (são
    transportadas para o novo ficheiro).
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Optional

from .settings import ROOT, load_config
from .workspace import ClassWorkspace

HUMAN_SOURCE = "human-adjudicated (GUI Ponte ILI)"
AUTO_SOURCE_UNIQUE = "auto: shared-lemma (par único)"
AUTO_SOURCE_AMBIG = "auto: shared-lemma (ambíguo)"


def is_human_row(row: dict) -> bool:
    return str(row.get("source", "")).startswith("human")


def _lexwarrant_dir() -> Path:
    return Path(load_config()["lexwarrant_dir"])


def _import_builder():
    d = str(_lexwarrant_dir())
    if d not in sys.path:
        sys.path.insert(0, d)
    import build_ili_equivalence as bie  # type: ignore
    return bie


def table_path(ws: ClassWorkspace) -> Path:
    return ws.out / "ili_equivalence.json"


def load_table(ws: ClassWorkspace) -> Optional[dict]:
    p = table_path(ws)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_table(ws: ClassWorkspace, doc: dict) -> Path:
    p = table_path(ws)
    p.parent.mkdir(parents=True, exist_ok=True)
    doc["coverage"] = {"map": len(doc.get("map", [])),
                       "review": len(doc.get("review", [])),
                       "unmatched": len(doc.get("unmatched", []))}
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                 encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# Descoberta de exports
# ---------------------------------------------------------------------------
def _looks_wordnet(data: dict) -> bool:
    syns = data.get("synsets")
    if isinstance(syns, list) and syns:
        ili = str((syns[0] or {}).get("ili") or "")
        if ili.startswith("i") and ili[1:].isdigit():
            return True
    if isinstance(data.get("sinalizacao"), dict) and "WordNet" in str(
            data.get("source", "")):
        return True
    return False


def find_wordnet_export(ws: ClassWorkspace) -> Optional[Path]:
    """Procura um export WordNet utilizável: exports/ da classe, depois
    WordNet/exports/ (bundles mais recentes primeiro)."""
    pools: list[Path] = []
    pools += sorted(ws.exports.glob("*.json"))
    wn_exp = ROOT / "WordNet" / "exports"
    if wn_exp.exists():
        pools += sorted(wn_exp.rglob("*.json"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    for p in pools:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if _looks_wordnet(data):
            return p
    return None


def find_pulo_export(ws: ClassWorkspace) -> Optional[Path]:
    for p in sorted(ws.exports.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if data.get("type") == "pulo_thesaurus_search":
            return p
    return None


# ---------------------------------------------------------------------------
# Gerar (preservando promoções humanas)
# ---------------------------------------------------------------------------
def build_table(class_id: str, wordnet_path: Optional[Path] = None,
                pulo_path: Optional[Path] = None) -> dict[str, Any]:
    ws = ClassWorkspace.open(class_id)
    ws.ensure()
    wordnet_path = wordnet_path or find_wordnet_export(ws)
    pulo_path = pulo_path or find_pulo_export(ws)
    if wordnet_path is None:
        return {"ok": False, "error":
                "Nenhum export WordNet encontrado. Abra o WordNet "
                "(WordNet\\start_wordnet.bat), pesquise o termo em inglês e "
                "use «💾→ exports/» — depois volte a clicar Gerar."}
    if pulo_path is None:
        return {"ok": False, "error":
                "Nenhum export PULO em exports/ — pesquise primeiro no "
                "workbench (fonte PULO)."}

    bie = _import_builder()
    doc = bie.build_from_files(Path(wordnet_path), Path(pulo_path), ws.class_id)

    # POLÍTICA DA PONTE: o gerador PROPÕE, nunca decide.
    # 1) Toda a linha automática vai para `review` (mesmo os pares únicos, que
    #    o construtor legado colocava em map como "high") — só a mão humana
    #    promove para `map`.
    # 2) Cada linha leva proveniência explícita (auto vs human).
    proposals = []
    for r in doc.get("map", []):
        r = dict(r)
        r["confidence"] = "review"
        r.setdefault("source", AUTO_SOURCE_UNIQUE)
        proposals.append(r)
    for r in doc.get("review", []):
        r = dict(r)
        r.setdefault("source", AUTO_SOURCE_AMBIG)
        proposals.append(r)
    doc["map"] = []
    doc["review"] = proposals

    # 3) Preservar SEMPRE o `map` existente (merge, nunca overwrite):
    #    - linhas humanas: intocáveis, com a sua proveniência;
    #    - linhas legadas sem proveniência: transportadas e marcadas como
    #      «legacy» (a regeneração não rebaixa o que estava em vigor).
    #    A regeneração só mexe no que ainda está por decidir (review).
    old = load_table(ws)
    carried = 0
    if old:
        have = {(r["oewn_ili"], r["pulo_ili"]) for r in doc["map"]}
        for r in old.get("map", []):
            key = (r.get("oewn_ili"), r.get("pulo_ili"))
            if key in have:
                continue
            r = dict(r)
            if not r.get("source"):
                r["source"] = "legacy: tabela anterior (pré-proveniência)"
            doc["map"].append(r)
            have.add(key)
            carried += 1
        # promoções humanas que estivessem (por erro) em review também sobem
        for r in old.get("review", []):
            key = (r.get("oewn_ili"), r.get("pulo_ili"))
            if is_human_row(r) and key not in have:
                doc["map"].append(dict(r))
                have.add(key)
                carried += 1
        doc["review"] = [r for r in doc["review"]
                         if (r["oewn_ili"], r["pulo_ili"]) not in have]
        # um oewn_ili já mapeado (decisão humana) não é «unmatched»
        mapped_oewn = {r["oewn_ili"] for r in doc["map"]}
        doc["unmatched"] = [r for r in doc.get("unmatched", [])
                            if r.get("oewn_ili") not in mapped_oewn]

    path = save_table(ws, doc)
    return {"ok": True, "path": str(path),
            "wordnet": str(wordnet_path), "pulo": str(pulo_path),
            "carried_human": carried, "coverage": doc["coverage"]}


# ---------------------------------------------------------------------------
# Glosas PULO para adjudicação
# ---------------------------------------------------------------------------
def pulo_gloss(ili_offset: str) -> dict[str, Any]:
    cfg = load_config()
    db = sqlite3.connect(str(cfg["pulo_sqlite"]))
    db.row_factory = sqlite3.Row
    try:
        row = db.execute(
            "SELECT t.offset AS off, s.gloss AS gloss FROM to_ili t "
            "JOIN synset s ON s.offset=t.offset WHERE t.iliOffset=? LIMIT 1",
            (ili_offset,)).fetchone()
        if not row:
            return {"gloss": "", "members": []}
        words = [w["word"].replace("_", " ") for w in db.execute(
            "SELECT DISTINCT word FROM variant WHERE offset=? ORDER BY sense",
            (row["off"],))]
        return {"gloss": (row["gloss"] or "").strip(), "members": words}
    finally:
        db.close()


def candidates(class_id: str) -> dict[str, Any]:
    """Tabela + linhas review/map enriquecidas com glosa e membros PULO."""
    ws = ClassWorkspace.open(class_id)
    doc = load_table(ws)
    if doc is None:
        return {"exists": False, "path": str(table_path(ws)),
                "map": [], "review": [], "unmatched": []}

    def enrich(rows):
        out = []
        for r in rows:
            info = pulo_gloss(r.get("pulo_ili", ""))
            out.append({**r, "pulo_gloss": info["gloss"],
                        "pulo_members": info["members"]})
        return out

    return {"exists": True, "path": str(table_path(ws)),
            "generated": doc.get("generated"),
            "map": enrich(doc.get("map", [])),
            "review": enrich(doc.get("review", [])),
            "unmatched": doc.get("unmatched", [])}


def promote(class_id: str, pairs: list[tuple[str, str]],
            note: str = "") -> dict[str, Any]:
    """Move (oewn_ili, pulo_ili) de review→map (decisão humana, com source)."""
    ws = ClassWorkspace.open(class_id)
    doc = load_table(ws)
    if doc is None:
        return {"ok": False, "error": "Tabela inexistente — gere-a primeiro."}
    wanted = set(pairs)
    moved = []
    keep = []
    for r in doc.get("review", []):
        key = (r.get("oewn_ili"), r.get("pulo_ili"))
        if key in wanted:
            r = dict(r)
            r["confidence"] = "high"
            r["source"] = HUMAN_SOURCE + (f" — {note}" if note else "")
            doc.setdefault("map", []).append(r)
            moved.append(key)
        else:
            keep.append(r)
    doc["review"] = keep
    save_table(ws, doc)
    return {"ok": True, "moved": moved,
            "coverage": doc["coverage"], "path": str(table_path(ws))}


def add_pair(class_id: str, oewn_ili: str, pulo_ili: str,
             note: str = "") -> dict[str, Any]:
    """Adicionar um par adjudicado à mão (ex.: candidato que caiu em
    `unmatched` por falta de lemas PT). Sempre com proveniência humana —
    é a declaração de equivalência do adjudicador, nunca do código."""
    ws = ClassWorkspace.open(class_id)
    doc = load_table(ws) or {"class": ws.class_id, "map": [], "review": [],
                             "unmatched": []}
    key = (oewn_ili, pulo_ili)
    existing = {(r.get("oewn_ili"), r.get("pulo_ili")) for r in doc.get("map", [])}
    if key in existing:
        return {"ok": True, "moved": [], "note": "par já em map",
                "coverage": doc.get("coverage", {}),
                "path": str(table_path(ws))}
    info = pulo_gloss(pulo_ili)
    doc.setdefault("map", []).append({
        "oewn_ili": oewn_ili,
        "pulo_ili": pulo_ili,
        "evidence": {"shared_lemmas": info["members"][:6],
                     "pos": pulo_ili.rsplit("-", 1)[-1]},
        "confidence": "high",
        "source": HUMAN_SOURCE + (f" — {note}" if note else ""),
    })
    # se estava em review ou unmatched, retirar de lá
    doc["review"] = [r for r in doc.get("review", [])
                     if (r.get("oewn_ili"), r.get("pulo_ili")) != key]
    doc["unmatched"] = [r for r in doc.get("unmatched", [])
                        if r.get("oewn_ili") != oewn_ili]
    save_table(ws, doc)
    return {"ok": True, "moved": [key], "coverage": doc["coverage"],
            "path": str(table_path(ws))}
