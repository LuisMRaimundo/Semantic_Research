"""Human decisions — the only curated artefact researchers must edit."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Optional

DECISIONS = ("UF", "RT", "exclude", "atributo", "contraste", "")


def blank_decisions(class_id: str) -> dict[str, Any]:
    return {
        "class_id": class_id,
        "senses": [],
        "terms": [],
        "manual_terms": [],
        "exclude_terms": [],
    }


def load_decisions(path: Path) -> dict[str, Any]:
    if not path.exists():
        return blank_decisions(path.parent.name)
    return json.loads(path.read_text(encoding="utf-8"))


def save_decisions(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sense_key(source: str, key: str) -> str:
    return f"{source}|{key}"


def upsert_sense(decisions: dict[str, Any], sense: dict[str, Any]) -> dict[str, Any]:
    """Insert or update a sense card by (source, key)."""
    out = deepcopy(decisions)
    senses = out.setdefault("senses", [])
    src = sense["source"]
    key = sense["key"]
    for i, existing in enumerate(senses):
        if existing.get("source") == src and existing.get("key") == key:
            merged = dict(existing)
            merged.update(sense)
            senses[i] = merged
            return out
    senses.append(sense)
    return out


def set_decision(decisions: dict[str, Any], source: str, key: str,
                 decision: str, note: str = "") -> dict[str, Any]:
    out = deepcopy(decisions)
    for s in out.get("senses", []):
        if s.get("source") == source and s.get("key") == key:
            s["decision"] = decision
            if note:
                s["note"] = note
            return out
    raise KeyError(f"sense not found: {source}|{key}")


def upsert_term(decisions: dict[str, Any], term: str, status: str,
                note: str = "", guarantee: Optional[list] = None) -> dict[str, Any]:
    out = deepcopy(decisions)
    terms = out.setdefault("terms", [])
    for t in terms:
        if t.get("term") == term:
            t["status"] = status
            if note:
                t["note"] = note
            if guarantee is not None:
                t["guarantee"] = guarantee
            return out
    terms.append({
        "term": term,
        "status": status,
        "note": note,
        "guarantee": guarantee or ["lexical"],
    })
    return out


def undecided_count(decisions: dict[str, Any]) -> int:
    """Count undecided PULO/ONTO cards only (WordNet is corroboration, not UF/RT)."""
    return sum(
        1 for s in decisions.get("senses", [])
        if (s.get("source") or "").lower() in ("pulo", "onto")
        and not (s.get("decision") or "").strip()
    )


def from_pulo_export(export: dict[str, Any], existing: Optional[dict] = None
                     ) -> dict[str, Any]:
    """Seed sense cards from a PULO export (keeps prior decisions)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    seen = set()
    for syn in export.get("synsets", []):
        ili = None
        for item in syn.get("ili") or []:
            ili = (item.get("ili_offset") or "").strip() or ili
        key = ili or syn.get("synset_offset") or ""
        if not key:
            continue
        sk = sense_key("pulo", key)
        seen.add(sk)
        if sk in prior:
            continue
        senses.append({
            "source": "pulo",
            "key": key,
            "ili": ili,
            "local_id": syn.get("synset_offset"),
            "pos": syn.get("pos"),
            "gloss": syn.get("gloss") or "",
            "members": list(syn.get("synonyms") or []),
            "decision": "",
            "note": "",
        })
    out["senses"] = senses
    return out


def from_onto_export(export: dict[str, Any], existing: Optional[dict] = None
                     ) -> dict[str, Any]:
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        res = syn.get("resource") or syn.get("res") or ""
        sid = str(syn.get("synset_id") or syn.get("sid") or "")
        key = f"{res}:{sid}" if res and sid else sid
        if not key:
            continue
        sk = sense_key("onto", key)
        if sk in prior:
            continue
        members = []
        for m in syn.get("members") or []:
            if isinstance(m, dict):
                members.append(m.get("word") or "")
            else:
                members.append(str(m))
        senses.append({
            "source": "onto",
            "key": key,
            "ili": None,
            "local_id": key,
            "pos": syn.get("pos"),
            "gloss": syn.get("gloss") or "",
            "members": [m for m in members if m],
            "decision": "",
            "note": "",
        })
    out["senses"] = senses
    return out


def from_wordnet_export(export: dict[str, Any], existing: Optional[dict] = None
                        ) -> dict[str, Any]:
    """Seed read-only OEWN sense cards (corroboration / Ponte ILI — no UF/RT)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        ili = (syn.get("ili") or "").strip()
        key = ili or syn.get("name") or ""
        if not key:
            continue
        sk = sense_key("wordnet", key)
        if sk in prior:
            continue
        members = list(syn.get("lemmas") or [])
        pt = list(syn.get("pt_lemmas") or [])
        if pt:
            members = members + [f"PT: {w}" for w in pt]
        senses.append({
            "source": "wordnet",
            "key": key,
            "ili": ili,
            "local_id": syn.get("name") or "",
            "pos": syn.get("pos") or "",
            "gloss": syn.get("definition") or "",
            "members": members,
            "decision": "",  # not adjudicated here — corroboration only
            "note": "OEWN corroboration (Ponte ILI / WordNet track)",
        })
    out["senses"] = senses
    return out
