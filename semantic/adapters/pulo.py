"""Thin PULO SQLite search → export JSON (no Tk GUI)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional

from ..normalize import normalize_word, pretty_word

POINTER_NAMES = {
    "@": "hypernym", "~": "hyponym",
    "#m": "member holonym", "#s": "substance holonym", "#p": "part holonym",
    "%m": "member meronym", "%s": "substance meronym", "%p": "part meronym",
    "=": "attribute", "*": "entailment", ">": "cause", "^": "see also",
    "$": "verb group", "&": "similar to", "!": "antonym",
    "+": "derivationally related form", "\\": "pertainym",
    ";c": "domain topic", "-c": "member of domain category",
    ";r": "domain region", "-r": "member of domain region",
    ";u": "domain usage", "-u": "member of domain usage",
}
RELATION_CODE = {
    1: ("=", "="), 2: (">", None), 4: ("\\", None),
    6: ("#s", "%s"), 7: ("#m", "%m"), 8: ("#p", "%p"),
    12: ("~", "@"), 19: ("*", None), 33: ("!", "!"),
    34: ("&", "&"), 49: ("^", "^"), 52: ("$", "$"),
    63: ("-c", ";c"), 64: ("+", "+"), 66: ("-r", ";r"), 68: ("-u", ";u"),
}
INVERSE_NAMES = {">": "is caused by", "\\": "has derived form", "*": "is entailed by"}


def _fwd_label(code: int) -> str:
    entry = RELATION_CODE.get(code)
    if entry is None:
        return f"relation #{code}"
    return POINTER_NAMES.get(entry[0], f"relation #{code}")


def _inv_label(code: int) -> str:
    entry = RELATION_CODE.get(code)
    if entry is None:
        return f"relation #{code} (inverse)"
    fwd, inv = entry
    if inv is not None:
        return POINTER_NAMES.get(inv, f"relation #{code} (inverse)")
    return INVERSE_NAMES.get(fwd, f"← {_fwd_label(code)}")


class PuloStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"PULO sqlite missing: {self.db_path}")
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def search(self, query: str, pos: Optional[str] = None,
               mode: str = "Starts with", limit: int = 200) -> list[sqlite3.Row]:
        conn = self.connect()
        qn = normalize_word(query)
        if not qn:
            return []
        if mode == "Exact":
            pattern, op = qn, "="
        elif mode == "Contains":
            pattern, op = f"%{qn}%", "LIKE"
        else:
            pattern, op = f"{qn}%", "LIKE"
        sql = (
            "SELECT v.word AS word, v.offset AS offset, v.pos AS pos, "
            "       v.sense AS sense, s.gloss AS gloss "
            "FROM variant v LEFT JOIN synset s ON s.offset = v.offset "
            f"WHERE v.word_norm {op} ? "
        )
        params: list[Any] = [pattern]
        if pos:
            sql += "AND v.pos = ? "
            params.append(pos)
        sql += "ORDER BY (v.word_norm = ?) DESC, v.word_norm, v.pos, v.sense LIMIT ?"
        params.extend([qn, limit])
        return conn.execute(sql, params).fetchall()

    def synonyms(self, offset: str) -> list[str]:
        rows = self.connect().execute(
            "SELECT DISTINCT word FROM variant WHERE offset = ? ORDER BY sense, word",
            (offset,),
        ).fetchall()
        return [r["word"] for r in rows]

    def ili(self, offset: str) -> list[dict]:
        rows = self.connect().execute(
            "SELECT iliOffset, iliWnId FROM to_ili WHERE offset = ?", (offset,)
        ).fetchall()
        return [{"ili_offset": r["iliOffset"], "ili_wn_id": r["iliWnId"]} for r in rows]

    def relations(self, offset: str) -> list[dict]:
        conn = self.connect()
        grouped: dict[str, list] = {}
        order: list[str] = []

        def add(label: str, target: str):
            words = self.synonyms(target)
            disp = ", ".join(pretty_word(w) for w in words) if words else "(no lemma)"
            row = conn.execute(
                "SELECT gloss FROM synset WHERE offset = ? LIMIT 1", (target,)
            ).fetchone()
            gl = (row["gloss"] if row else "") or ""
            if label not in grouped:
                grouped[label] = []
                order.append(label)
            grouped[label].append({"offset": target, "words": disp, "gloss": gl})

        for r in conn.execute(
            "SELECT relation, targetSynset FROM relation WHERE sourceSynset = ?",
            (offset,),
        ):
            add(_fwd_label(int(r["relation"])), r["targetSynset"])
        for r in conn.execute(
            "SELECT relation, sourceSynset FROM relation WHERE targetSynset = ?",
            (offset,),
        ):
            add(_inv_label(int(r["relation"])), r["sourceSynset"])
        return [{"relation": lab, "targets": grouped[lab]} for lab in order]

    def synset_dict(self, offset: str) -> dict[str, Any]:
        conn = self.connect()
        row = conn.execute(
            "SELECT offset, pos, gloss FROM synset WHERE offset = ? LIMIT 1", (offset,)
        ).fetchone()
        syns = [pretty_word(w) for w in self.synonyms(offset)]
        # reshape relations for phase0_pulo (expects targets with words/gloss)
        rels_raw = self.relations(offset)
        rels = []
        for block in rels_raw:
            targets = []
            for t in block["targets"]:
                targets.append({"words": t["words"], "gloss": t["gloss"]})
            rels.append({"relation": block["relation"], "targets": targets})
        return {
            "synset_offset": offset,
            "pos": (row["pos"] if row else "") or "",
            "gloss": (row["gloss"] if row else "") or "",
            "synonyms": syns,
            "ili": self.ili(offset),
            "relations": rels,
        }

    def export_search(self, query: str, pos: Optional[str] = None,
                      mode: str = "Starts with", limit: int = 200) -> dict[str, Any]:
        rows = self.search(query, pos=pos, mode=mode, limit=limit)
        seen: set[str] = set()
        synsets = []
        for r in rows:
            off = r["offset"]
            if off in seen:
                continue
            seen.add(off)
            synsets.append(self.synset_dict(off))
        return {
            "type": "pulo_thesaurus_search",
            "query": {"query": query, "pos": pos, "mode": mode},
            "count": len(synsets),
            "synsets": synsets,
        }
