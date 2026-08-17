"""PAPEL 3.5 — word–word relations as discovery (never LexWarrant admission).

Source: ``PAPEL.v.3.5_utf8/relacoes_final_*.txt``
Line form: ``palavra1 RELACAO palavra2 [:: registo;domínio;variante]``
"""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path
from typing import Any, Optional

from ..normalize import normalize_word, pretty_word

_LINE_RE = re.compile(
    r"^(\S+)\s+(\S+)\s+(\S+)(?:\s*::\s*(.*))?$"
)
_GROUP_FROM_NAME = re.compile(r"^relacoes_final_(.+)\.txt$", re.I)


def _parse_line(line: str) -> Optional[tuple[str, str, str, str]]:
    s = (line or "").strip()
    if not s or s.startswith("#"):
        return None
    m = _LINE_RE.match(s)
    if not m:
        return None
    w1, rel, w2, meta = m.group(1), m.group(2), m.group(3), (m.group(4) or "").strip()
    return w1, rel, w2, meta


def build_papel_sqlite(src_dir: Path, db_path: Path) -> dict[str, Any]:
    """Index all ``relacoes_final_*.txt`` into SQLite."""
    src_dir = Path(src_dir)
    db_path = Path(db_path)
    files = sorted(src_dir.glob("relacoes_final_*.txt"))
    # Prefer per-group files; fall back to monolithic relacoes_final.txt
    if not files:
        mono = src_dir / "relacoes_final.txt"
        files = [mono] if mono.exists() else []
    if not files:
        return {"ok": False, "error": f"no relacoes_final_*.txt under {src_dir}"}

    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()

    con = sqlite3.connect(str(db_path))
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.executescript(
        """
        CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE triple (
            id INTEGER PRIMARY KEY,
            w1 TEXT NOT NULL,
            w1_norm TEXT NOT NULL,
            rel TEXT NOT NULL,
            group_name TEXT NOT NULL,
            w2 TEXT NOT NULL,
            w2_norm TEXT NOT NULL,
            meta TEXT
        );
        """
    )
    n = 0
    by_group: dict[str, int] = {}
    batch: list[tuple] = []
    for fp in files:
        m = _GROUP_FROM_NAME.match(fp.name)
        group = (m.group(1) if m else "ALL").upper()
        with fp.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                parsed = _parse_line(line)
                if not parsed:
                    continue
                w1, rel, w2, meta = parsed
                batch.append((
                    w1, normalize_word(w1), rel, group,
                    w2, normalize_word(w2), meta,
                ))
                n += 1
                by_group[group] = by_group.get(group, 0) + 1
                if len(batch) >= 5000:
                    con.executemany(
                        "INSERT INTO triple "
                        "(w1,w1_norm,rel,group_name,w2,w2_norm,meta) "
                        "VALUES (?,?,?,?,?,?,?)",
                        batch,
                    )
                    batch.clear()
    if batch:
        con.executemany(
            "INSERT INTO triple "
            "(w1,w1_norm,rel,group_name,w2,w2_norm,meta) "
            "VALUES (?,?,?,?,?,?,?)",
            batch,
        )
    con.execute(
        "CREATE INDEX idx_papel_w1 ON triple(w1_norm)"
    )
    con.execute(
        "CREATE INDEX idx_papel_w2 ON triple(w2_norm)"
    )
    con.execute(
        "CREATE INDEX idx_papel_rel ON triple(rel)"
    )
    con.execute(
        "INSERT INTO meta(key,value) VALUES ('ready','1')"
    )
    con.execute(
        "INSERT INTO meta(key,value) VALUES (?,?)",
        ("source", str(src_dir.resolve())),
    )
    con.execute(
        "INSERT INTO meta(key,value) VALUES (?,?)",
        ("n_triples", str(n)),
    )
    con.commit()
    con.close()
    return {
        "ok": True,
        "path": str(db_path),
        "n_triples": n,
        "groups": by_group,
        "n_files": len(files),
    }


def annotate_papel_bucket(bucket: dict[str, Any], query: str) -> dict[str, Any]:
    """Marca focal / argumentos / direcção e restringe ``members``.

    SINONIMIA: members = focal + argumentos (são de facto sinónimos).
    Restantes grupos: members = só o focal; os outros ficam em
    ``papel_arguments``. Se nenhum argumento coincidir com a consulta,
    ``papel_focal`` é null e a direcção é ``unresolved`` — nunca se adivinha.
    """
    qn = normalize_word(query)
    g = str((bucket.get("relations") or {}).get("papel_group") or "")
    triples = list(bucket.pop("_triples", None) or [])
    if not triples:
        # Export antigo: só members planos. Recuperar focal/args pela consulta.
        words: list[str] = []
        for m in bucket.get("members") or []:
            w = m.get("word") if isinstance(m, dict) else str(m)
            if w:
                words.append(w)
        triples = []
        for w in words:
            if normalize_word(w) == qn:
                triples.append((w, ""))
            else:
                triples.append(("", w))

    focal: Optional[str] = None
    arguments: list[str] = []
    seen_args: set[str] = set()
    dirs: list[str] = []

    for w1, w2 in triples:
        n1, n2 = normalize_word(w1), normalize_word(w2)
        if n1 and n1 == qn:
            focal = pretty_word(w1)
            if n2:
                dirs.append("focal_to_argument")
            if n2 and n2 != qn and n2 not in seen_args:
                seen_args.add(n2)
                arguments.append(pretty_word(w2))
        elif n2 and n2 == qn:
            focal = pretty_word(w2)
            if n1:
                dirs.append("argument_to_focal")
            if n1 and n1 != qn and n1 not in seen_args:
                seen_args.add(n1)
                arguments.append(pretty_word(w1))
        else:
            for w, n in ((w1, n1), (w2, n2)):
                if n and n not in seen_args:
                    seen_args.add(n)
                    arguments.append(pretty_word(w))

    if focal is None:
        direction = "unresolved"
    elif dirs and all(d == dirs[0] for d in dirs):
        direction = dirs[0]
    elif dirs:
        direction = dirs[0]
    else:
        direction = "unresolved"

    bucket["papel_focal"] = focal
    bucket["papel_arguments"] = arguments
    bucket["papel_direction"] = direction

    if g.upper() == "SINONIMIA":
        ordered = ([focal] if focal else []) + arguments
        seen: set[str] = set()
        members = []
        for w in ordered:
            n = normalize_word(w)
            if n and n not in seen:
                seen.add(n)
                members.append({"word": w, "weight": 1.0})
        bucket["members"] = members
    else:
        bucket["members"] = (
            [{"word": focal, "weight": 1.0}] if focal else []
        )
    return bucket


def upgrade_papel_export(export: dict[str, Any]) -> dict[str, Any]:
    """Reaplica a estrutura argumental a um export PAPEL já gravado."""
    query = ""
    q = export.get("query")
    if isinstance(q, dict):
        query = str(q.get("query") or "")
    elif isinstance(q, str):
        query = q
    out = dict(export)
    out["synsets"] = [
        annotate_papel_bucket(dict(s), query) for s in (export.get("synsets") or [])
    ]
    return out


class PapelStore:
    """Read-only PAPEL index for discovery search."""

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"PAPEL sqlite missing: {self.db_path} "
                "(run: python sr.py resources --build-papel)"
            )
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

    def triple_count(self) -> int:
        return int(self.connect().execute("SELECT COUNT(*) FROM triple").fetchone()[0])

    def search(
        self,
        query: str,
        *,
        mode: str = "Starts with",
        group: Optional[str] = None,
        limit: int = 80,
    ) -> list[sqlite3.Row]:
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
            "SELECT id, w1, w1_norm, rel, group_name, w2, w2_norm, meta "
            "FROM triple "
            f"WHERE (w1_norm {op} ? OR w2_norm {op} ?) "
        )
        params: list[Any] = [pat, pat]
        if group:
            sql += "AND group_name=? "
            params.append(group.upper())
        sql += "ORDER BY (w1_norm=? OR w2_norm=?) DESC, group_name, rel LIMIT ?"
        params += [qn, qn, limit * 3]  # over-fetch; cluster below
        return c.execute(sql, params).fetchall()

    def export_search(
        self,
        query: str,
        *,
        mode: str = "Starts with",
        group: Optional[str] = None,
        limit: int = 80,
    ) -> dict[str, Any]:
        """Cluster matching triples into discovery 'synsets' (relation bundles)."""
        rows = self.search(query, mode=mode, group=group, limit=limit)
        qn = normalize_word(query)
        clusters: dict[tuple[str, str], dict[str, Any]] = {}
        for r in rows:
            g = r["group_name"] or "ALL"
            rel = r["rel"] or ""
            key = (g, rel)
            bucket = clusters.get(key)
            if bucket is None:
                bucket = {
                    "resource": "papel35",
                    "resource_label": f"PAPEL 3.5 / {g}",
                    "synset_id": f"{g}:{rel}:{qn or query}",
                    "pos": "",
                    "gloss": f"PAPEL {rel} ({g})",
                    "members": [],
                    "relations": {"papel_rel": rel, "papel_group": g},
                    "_triples": [],
                }
                clusters[key] = bucket
            bucket["_triples"].append((r["w1"], r["w2"]))
            if len(clusters) >= limit:
                break

        synsets = [annotate_papel_bucket(b, query) for b in clusters.values()]

        return {
            "type": "thesaurus_search",
            "source": "papel",
            "query": {"query": query, "mode": mode, "group": group},
            "count": len(synsets),
            "synsets": synsets,
            "_note": (
                "PAPEL 3.5 discovery only — word–word dictionary relations; "
                "never LexWarrant admission."
            ),
        }
