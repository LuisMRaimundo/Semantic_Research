"""Thin Onto.PT SQLite search → export JSON (no Tk GUI)."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Optional

from ..normalize import normalize_word, pretty_word


class OntoStore:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Onto.PT sqlite missing: {self.db_path}")
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

    def resource_names(self) -> dict[str, str]:
        try:
            rows = self.connect().execute(
                "SELECT res, label FROM resource ORDER BY res"
            ).fetchall()
            return {r["res"]: r["label"] for r in rows}
        except sqlite3.Error:
            return {}

    def search(self, query: str, res: Optional[str] = None, pos: Optional[str] = None,
               mode: str = "Starts with", limit: int = 200) -> list[sqlite3.Row]:
        c = self.connect()
        qn = normalize_word(query)
        if not qn:
            return []
        if mode == "Exact":
            op, pat = "=", qn
        elif mode == "Contains":
            op, pat = "LIKE", f"%{qn}%"
        else:
            op, pat = "LIKE", f"{qn}%"
        sql = (
            "SELECT m.res AS res, m.sid AS sid, m.word AS word, m.weight AS weight, "
            "       s.pos AS pos, s.gloss AS gloss "
            "FROM member m JOIN synset s ON s.res=m.res AND s.sid=m.sid "
            f"WHERE m.word_norm {op} ? "
        )
        params: list[Any] = [pat]
        if res:
            sql += "AND m.res=? "
            params.append(res)
        if pos:
            sql += "AND s.pos=? "
            params.append(pos)
        sql += "ORDER BY (m.word_norm=?) DESC, m.res, m.word LIMIT ?"
        params += [qn, limit]
        return c.execute(sql, params).fetchall()

    def members(self, res: str, sid: str) -> list[dict]:
        rows = self.connect().execute(
            "SELECT word, weight FROM member WHERE res=? AND sid=? "
            "ORDER BY weight DESC, word",
            (res, sid),
        ).fetchall()
        return [{"word": pretty_word(r["word"]), "weight": r["weight"]} for r in rows]

    def synset_dict(self, res: str, sid: str, names: Optional[dict] = None) -> dict:
        names = names or self.resource_names()
        row = self.connect().execute(
            "SELECT pos, gloss FROM synset WHERE res=? AND sid=? LIMIT 1", (res, sid)
        ).fetchone()
        return {
            "resource": res,
            "resource_label": names.get(res, res),
            "synset_id": sid,
            "pos": (row["pos"] if row else "") or "",
            "gloss": (row["gloss"] if row else "") or "",
            "members": self.members(res, sid),
            "relations": {},
        }

    def export_search(self, query: str, res: Optional[str] = None,
                      pos: Optional[str] = None, mode: str = "Starts with",
                      limit: int = 200) -> dict[str, Any]:
        rows = self.search(query, res=res, pos=pos, mode=mode, limit=limit)
        names = self.resource_names()
        seen: set[tuple] = set()
        synsets = []
        for r in rows:
            key = (r["res"], r["sid"])
            if key in seen:
                continue
            seen.add(key)
            synsets.append(self.synset_dict(r["res"], r["sid"], names))
        return {
            "type": "thesaurus_search",
            "query": {"query": query, "resource": res, "pos": pos, "mode": mode},
            "count": len(synsets),
            "synsets": synsets,
        }
