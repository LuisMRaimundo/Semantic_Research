"""Unified SenseIndex — one row per source-local sense, optional CILI id.

Schema (SQLite):
  sense_key TEXT PK   — ``{source}:{local_id}``
  source    TEXT      — pulo | onto | oewn | own-pt
  local_id  TEXT      — offset / sid / oewn-… id
  ili       TEXT NULL — canonical CILI ``i…`` (never fabricated)
  ili_raw   TEXT NULL — original ILI / offset string before resolve
  pos       TEXT
  gloss     TEXT
  lemmas    TEXT      — JSON list (display forms)
  lemmas_norm TEXT    — JSON list (normalized)
  resource  TEXT NULL — Onto.PT resource code
  csco      REAL NULL — PULO confidence when present
  class_id  TEXT NULL — last class that touched this row (audit)
  updated   TEXT

Join discipline: LexWarrant / CILI still own identity joins. This index is the
durable registry so harvests do not depend on ad-hoc JSON soup alone.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional

from .engines import cili_api, engine_paths
from .normalize import normalize_word, pretty_word
from .settings import DATA_DIR, load_config

SCHEMA = """
CREATE TABLE IF NOT EXISTS sense (
  sense_key   TEXT PRIMARY KEY,
  source      TEXT NOT NULL,
  local_id    TEXT NOT NULL,
  ili         TEXT,
  ili_raw     TEXT,
  pos         TEXT,
  gloss       TEXT,
  lemmas      TEXT NOT NULL DEFAULT '[]',
  lemmas_norm TEXT NOT NULL DEFAULT '[]',
  resource    TEXT,
  csco        REAL,
  class_id    TEXT,
  updated     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sense_ili ON sense(ili);
CREATE INDEX IF NOT EXISTS idx_sense_source ON sense(source);
CREATE INDEX IF NOT EXISTS idx_sense_lemma_norm ON sense(lemmas_norm);
CREATE INDEX IF NOT EXISTS idx_sense_class ON sense(class_id);

CREATE TABLE IF NOT EXISTS onto_ili_proposal (
  onto_key    TEXT NOT NULL,
  ili         TEXT NOT NULL,
  score       REAL NOT NULL,
  method      TEXT NOT NULL,
  evidence    TEXT,
  class_id    TEXT,
  status      TEXT NOT NULL DEFAULT 'proposed',
  updated     TEXT NOT NULL,
  PRIMARY KEY (onto_key, ili)
);
"""


def default_index_path() -> Path:
    cfg = load_config()
    raw = cfg.get("sense_index")
    if raw:
        return Path(raw)
    return DATA_DIR / "sense_index.sqlite"


class SenseIndex:
    def __init__(self, path: Optional[Path] = None):
        self.path = Path(path) if path else default_index_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.path))
            self._conn.row_factory = sqlite3.Row
            self._conn.executescript(SCHEMA)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "SenseIndex":
        self.connect()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def stats(self) -> dict[str, Any]:
        c = self.connect()
        by_src = {
            r["source"]: r["n"]
            for r in c.execute(
                "SELECT source, COUNT(*) AS n FROM sense GROUP BY source"
            )
        }
        with_ili = c.execute(
            "SELECT COUNT(*) FROM sense WHERE ili IS NOT NULL AND ili != ''"
        ).fetchone()[0]
        proposals = c.execute("SELECT COUNT(*) FROM onto_ili_proposal").fetchone()[0]
        return {
            "path": str(self.path),
            "total": sum(by_src.values()),
            "by_source": by_src,
            "with_ili": with_ili,
            "onto_ili_proposals": proposals,
        }

    def upsert(self, row: dict[str, Any]) -> None:
        c = self.connect()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        lemmas = list(row.get("lemmas") or [])
        lemmas_norm = list(row.get("lemmas_norm") or [
            normalize_word(x) for x in lemmas if x
        ])
        c.execute(
            """
            INSERT INTO sense (
              sense_key, source, local_id, ili, ili_raw, pos, gloss,
              lemmas, lemmas_norm, resource, csco, class_id, updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(sense_key) DO UPDATE SET
              ili=excluded.ili,
              ili_raw=excluded.ili_raw,
              pos=excluded.pos,
              gloss=excluded.gloss,
              lemmas=excluded.lemmas,
              lemmas_norm=excluded.lemmas_norm,
              resource=excluded.resource,
              csco=excluded.csco,
              class_id=COALESCE(excluded.class_id, sense.class_id),
              updated=excluded.updated
            """,
            (
                row["sense_key"],
                row["source"],
                row["local_id"],
                row.get("ili"),
                row.get("ili_raw"),
                row.get("pos") or "",
                row.get("gloss") or "",
                json.dumps(lemmas, ensure_ascii=False),
                json.dumps(lemmas_norm, ensure_ascii=False),
                row.get("resource"),
                row.get("csco"),
                row.get("class_id"),
                now,
            ),
        )
        c.commit()

    def upsert_many(self, rows: Iterable[dict[str, Any]]) -> int:
        n = 0
        for row in rows:
            self.upsert(row)
            n += 1
        return n

    def identifiers_for_class(self, class_id: str) -> list[str]:
        """ILI / ili_raw strings for CILI harvest from indexed senses of a class."""
        c = self.connect()
        out: list[str] = []
        seen: set[str] = set()
        for r in c.execute(
            "SELECT ili, ili_raw FROM sense WHERE class_id = ?", (class_id,)
        ):
            for val in (r["ili"], r["ili_raw"]):
                s = (val or "").strip()
                if s and s not in seen:
                    seen.add(s)
                    out.append(s)
        return out

    def by_ili(self, ili: str) -> list[dict[str, Any]]:
        c = self.connect()
        rows = c.execute("SELECT * FROM sense WHERE ili = ?", (ili,)).fetchall()
        return [dict(r) for r in rows]

    def save_onto_proposal(
        self,
        onto_key: str,
        ili: str,
        score: float,
        method: str,
        evidence: dict[str, Any] | None = None,
        class_id: str | None = None,
        status: str = "proposed",
    ) -> None:
        c = self.connect()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        c.execute(
            """
            INSERT INTO onto_ili_proposal
              (onto_key, ili, score, method, evidence, class_id, status, updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(onto_key, ili) DO UPDATE SET
              score=excluded.score,
              method=excluded.method,
              evidence=excluded.evidence,
              class_id=COALESCE(excluded.class_id, onto_ili_proposal.class_id),
              status=excluded.status,
              updated=excluded.updated
            """,
            (
                onto_key, ili, float(score), method,
                json.dumps(evidence or {}, ensure_ascii=False),
                class_id, status, now,
            ),
        )
        c.commit()


def _resolve_ili(raw: str | None) -> tuple[Optional[str], Optional[str]]:
    """Return (canonical_ili, raw). Never fabricates."""
    if not raw:
        return None, None
    s = str(raw).strip()
    if not s:
        return None, None
    try:
        _, _, resolve, _ = cili_api()
        cid = resolve(s)
        if cid:
            return cid, s
        if s.startswith("i") and s[1:].isdigit():
            # already CILI form; accept only if in map
            return (s if resolve(s) else None), s
        return None, s
    except Exception:  # noqa: BLE001
        return None, s


def rows_from_pulo_export(export: dict[str, Any], class_id: str = "") -> list[dict]:
    rows = []
    for syn in export.get("synsets") or []:
        off = str(syn.get("synset_offset") or "").strip()
        if not off:
            continue
        ili_list = syn.get("ili") or []
        ili_raw = None
        if ili_list:
            first = ili_list[0]
            if isinstance(first, dict):
                ili_raw = first.get("ili_offset") or first.get("ili_wn_id")
            else:
                ili_raw = str(first)
        ili, raw = _resolve_ili(ili_raw)
        lemmas = [pretty_word(x) for x in (syn.get("synonyms") or [])]
        rows.append({
            "sense_key": f"pulo:{off}",
            "source": "pulo",
            "local_id": off,
            "ili": ili,
            "ili_raw": raw,
            "pos": syn.get("pos") or "",
            "gloss": syn.get("gloss") or "",
            "lemmas": lemmas,
            "class_id": class_id or None,
        })
    return rows


def rows_from_onto_export(export: dict[str, Any], class_id: str = "") -> list[dict]:
    rows = []
    for syn in export.get("synsets") or []:
        res = str(syn.get("resource") or "").strip()
        sid = str(syn.get("synset_id") or "").strip()
        if not res or not sid:
            continue
        lemmas = [
            pretty_word(m.get("word") if isinstance(m, dict) else m)
            for m in (syn.get("members") or [])
        ]
        rows.append({
            "sense_key": f"onto:{res}:{sid}",
            "source": "onto",
            "local_id": f"{res}:{sid}",
            "ili": None,
            "ili_raw": None,
            "pos": syn.get("pos") or "",
            "gloss": syn.get("gloss") or "",
            "lemmas": lemmas,
            "resource": res,
            "class_id": class_id or None,
        })
    return rows


def rows_from_wordnet_facets(export: dict[str, Any], class_id: str = "") -> list[dict]:
    rows = []
    for syn in export.get("synsets") or []:
        name = str(syn.get("name") or "").strip()
        if not name:
            continue
        ili_raw = syn.get("ili")
        ili, raw = _resolve_ili(str(ili_raw) if ili_raw else None)
        lemmas = list(syn.get("lemmas") or [])
        rows.append({
            "sense_key": f"oewn:{name}",
            "source": "oewn",
            "local_id": name,
            "ili": ili,
            "ili_raw": raw,
            "pos": syn.get("pos") or "",
            "gloss": syn.get("definition") or syn.get("gloss") or "",
            "lemmas": lemmas,
            "class_id": class_id or None,
        })
        pt = list(syn.get("pt_lemmas") or [])
        if pt and ili:
            rows.append({
                "sense_key": f"own-pt:{ili}",
                "source": "own-pt",
                "local_id": ili,
                "ili": ili,
                "ili_raw": ili,
                "pos": syn.get("pos") or "",
                "gloss": "",
                "lemmas": pt,
                "class_id": class_id or None,
            })
    return rows


def ingest_class_exports(class_id: str, index: Optional[SenseIndex] = None) -> dict[str, Any]:
    """Upsert all exports under ``classes/<id>/exports`` into the SenseIndex."""
    from .workspace import ClassWorkspace

    ws = ClassWorkspace.open(class_id)
    si = index or SenseIndex()
    owned = index is not None
    counts = {"pulo": 0, "onto": 0, "oewn": 0, "own-pt": 0, "files": 0}
    try:
        for path in sorted(ws.exports.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            counts["files"] += 1
            typ = (data.get("type") or "").lower()
            name = path.name.lower()
            if typ == "pulo_thesaurus_search" or name.startswith("pulo_"):
                n = si.upsert_many(rows_from_pulo_export(data, class_id))
                counts["pulo"] += n
            elif typ in ("thesaurus_search", "onto_thesaurus_search") or name.startswith("onto_"):
                n = si.upsert_many(rows_from_onto_export(data, class_id))
                counts["onto"] += n
            elif typ == "oewn_facets" or "facets" in name or name.startswith("wordnet_"):
                before = si.stats().get("by_source", {})
                n = si.upsert_many(rows_from_wordnet_facets(data, class_id))
                after = si.stats().get("by_source", {})
                counts["oewn"] += max(0, after.get("oewn", 0) - before.get("oewn", 0))
                counts["own-pt"] += max(0, after.get("own-pt", 0) - before.get("own-pt", 0))
                if n and not counts["oewn"]:
                    counts["oewn"] += n  # fallback accounting
        return {"class_id": class_id, "index": str(si.path), **counts, "stats": si.stats()}
    finally:
        if not owned:
            si.close()


def build_index_from_pulo_db(
    limit: Optional[int] = None,
    index: Optional[SenseIndex] = None,
) -> dict[str, Any]:
    """Bulk load PULO synsets (+ to_ili) into the SenseIndex (full lexicon)."""
    import sqlite3

    paths = engine_paths()
    db = paths["pulo_sqlite"]
    si = index or SenseIndex()
    owned = index is not None
    _, _, resolve, _ = cili_api()
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    sql = (
        "SELECT s.offset, s.pos, s.gloss, t.iliOffset "
        "FROM synset s LEFT JOIN to_ili t ON t.offset = s.offset"
    )
    if limit:
        sql += f" LIMIT {int(limit)}"
    n = 0
    try:
        for row in con.execute(sql):
            off = row["offset"]
            ili_raw = row["iliOffset"]
            ili = resolve(ili_raw) if ili_raw else None
            lemmas = [
                pretty_word(r[0])
                for r in con.execute(
                    "SELECT word FROM variant WHERE offset = ? ORDER BY sense, word",
                    (off,),
                )
            ]
            si.upsert({
                "sense_key": f"pulo:{off}",
                "source": "pulo",
                "local_id": off,
                "ili": ili,
                "ili_raw": ili_raw,
                "pos": row["pos"] or "",
                "gloss": row["gloss"] or "",
                "lemmas": lemmas,
            })
            n += 1
            if n % 5000 == 0:
                si.connect().commit()
        return {"loaded_pulo": n, "stats": si.stats()}
    finally:
        con.close()
        if not owned:
            si.close()
