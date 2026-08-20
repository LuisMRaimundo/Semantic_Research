#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CILI lexicographical engine (read-only).

Promotes CILI from an identity-only layer to a queryable lexicographical
engine: definitions, multilingual lemma labels, ranked interlingual
equivalents, per-sense translations, and lexical gaps.

Identity is sacred
------------------
CILI ``i…`` numbers are canonical and never fabricated. CURIE prefixes are
contextual only. PWN-3.0 offsets are local ids (``pwn30-…``), never presented
as CILI. This engine never mints, guesses, or "repairs" an ILI id. Anything
unmappable is reported as unmapped (``None``), not approximated.
``ili_for_pwn30`` / ``pwn30_for_ili`` are thin exact lookups on the live
``ili-map-pwn30.tab`` (LexWarrant path). They do not flip a↔s.

Satellite normalisation
-----------------------
The stack treats a↔s as normalised for joins. Each concept exposes:

* ``pos`` — raw source POS as in ``ili.ttl`` / maps (``-a`` vs ``-s``)
* ``pos_norm`` — ``s→a`` (satellite adjectives join as adjectives)
* ``pos_name`` — display label; satellites still read "adjective (satellite)"

Every join with SenseIndex / LexWarrant uses ``pos_norm``.

The engine does not write to ``concept_mapping``, does not auto-accept, and
does not touch Onto→ILI proposals.
"""

from __future__ import annotations

import hashlib
import os
import re
import sqlite3
import time
from pathlib import Path
from threading import Lock
from typing import Any, Iterable, Optional

SCHEMA_VERSION = "sr-r9-1"
EXPECTED_CONCEPTS = 117_659
POS_NAMES = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective (satellite)",
    "r": "adverb",
}
POS_NORM = {"s": "a"}
_ILI_RE = re.compile(r"^i\d+$")
_OFFSET_RE = re.compile(r"^(\d{8}-[anvrs])$", re.I)
_PWN30_RE = re.compile(r"^pwn30-(\d{8}-[anvrs])$", re.I)

CONCEPT_RE = re.compile(
    r"<(i\d+)>\s+a\s+<(Concept|Instance)>\s*;(.*?)(?:\n\s*\n|\Z)", re.S
)
DEF_RE = re.compile(r'skos:definition\s+"((?:[^"\\]|\\.)*)"@(\w+)')
SRC_RE = re.compile(r"dc:source\s+([\w:.\-]+)")
STATUS_RE = re.compile(r"ili:status\s+ili:(\w+)")
SUPERSEDED_RE = re.compile(r"ili:supersededBy\s+<?(i\d+)>?")
MAP_RE = re.compile(
    r"ili:(i\d+)\s+owl:sameAs\s+([\w]+):([\w.\-]+)\s*\.\s*(?:#\s*(.*))?"
)

# Language hints for known mapping-file resources (files themselves are discovered).
_RESOURCE_LANG = {
    "wn31": "en",
    "wn30": "en",
    "pwn31": "en",
    "pwn30": "en",
    "odwn13": "nl",
}

CILI_RDF = "http://ili.globalwordnet.org/ili/{ili}"
CILI_PAGE = "https://globalwordnet.github.io/cili/{ili}"


def pos_norm(pos: str) -> str:
    """Normalise satellite adjectives ``s→a`` for joins."""
    p = (pos or "").strip().lower()
    return POS_NORM.get(p, p)


def is_ili_id(token: str | None) -> bool:
    """True iff *token* is a well-formed CILI id (does not mint one)."""
    return bool(token) and bool(_ILI_RE.fullmatch(str(token).strip()))


def canonical_ili(token: str | None) -> Optional[str]:
    """Return *token* unchanged when it is already a CILI id, else ``None``.

    Never constructs an ``i…`` id from an offset or any other spelling.
    """
    if token is None:
        return None
    s = str(token).strip()
    if s.startswith(("oewn-ili:", "ili:", "cili:")):
        s = s.rsplit(":", 1)[-1].strip()
    return s if is_ili_id(s) else None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_prefix(path: Path, n: int = 12) -> str:
    return sha256_file(path)[:n]


def fts_escape(q: str) -> Optional[str]:
    """Build a safe FTS5 MATCH expression (prefix search per token)."""
    tokens = re.findall(r"[\w'\-]+", q, re.UNICODE)
    if not tokens:
        return None
    return " ".join('"{}"*'.format(t.replace('"', "")) for t in tokens)


def fts5_available() -> bool:
    try:
        con = sqlite3.connect(":memory:")
        con.execute("CREATE VIRTUAL TABLE t USING fts5(x)")
        con.close()
        return True
    except sqlite3.OperationalError:
        return False


def discover_mapping_files(root: Path) -> list[tuple[str, Path, str]]:
    """``(resource, path, lang)`` for every ``ili-map-*.ttl`` under *root*."""
    maps: list[tuple[str, Path, str]] = []
    if not root.is_dir():
        return maps
    for path in sorted(root.glob("ili-map-*.ttl")):
        resource = path.stem.replace("ili-map-", "", 1)
        if not resource:
            continue
        lang = _RESOURCE_LANG.get(resource, resource[:2] if resource else "")
        maps.append((resource, path, lang))
    return maps


def discover_omw_files(omw_dir: Path, root: Path) -> list[Path]:
    """Language packs: ``omw_dir``, else ``root``, else ``root/omw``."""
    seen: dict[str, Path] = {}

    def _collect(folder: Path) -> None:
        if not folder.is_dir():
            return
        for path in sorted(folder.glob("wn-data-*.tab")):
            seen.setdefault(path.name, path)

    _collect(omw_dir)
    if not seen:
        _collect(root)
    if not seen:
        _collect(root / "omw")
    return list(seen.values())


def lang_from_omw_name(path: Path) -> str:
    # wn-data-por.tab → por
    name = path.name
    if name.startswith("wn-data-") and name.endswith(".tab"):
        return name[8:-4]
    return ""


def load_pwn30_map(path: Path) -> tuple[dict[str, str], dict[str, str]]:
    """Exact ``offset → ili`` and ``ili → offset`` (first offset wins).

    ILI ids are read from the file; none are constructed.
    """
    off2ili: dict[str, str] = {}
    ili2off: dict[str, str] = {}
    if not path.exists():
        return off2ili, ili2off
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            parts = line.split()
            if len(parts) != 2:
                continue
            ili, off = parts[0].strip(), parts[1].strip()
            if not is_ili_id(ili) or not off:
                continue
            off2ili[off] = ili
            ili2off.setdefault(ili, off)
    return off2ili, ili2off


def _bare_offset(offset: str) -> Optional[str]:
    s = str(offset or "").strip()
    if not s:
        return None
    m = _PWN30_RE.match(s)
    if m:
        return m.group(1).lower()
    m = _OFFSET_RE.match(s)
    if m:
        return m.group(1).lower()
    return None


class CiliEngine:
    """Queryable CILI index. All query methods return plain dicts / ``None``."""

    def __init__(
        self,
        *,
        root: Path,
        omw_dir: Path | None = None,
        pwn30_map: Path | None = None,
        index_path: Path | None = None,
        pin: str | None = None,
        dump_pwn30_map: Path | None = None,
        write_pin: bool = False,
    ) -> None:
        self.root = Path(root)
        self.omw_dir = Path(omw_dir) if omw_dir is not None else self.root
        self.pwn30_map = (
            Path(pwn30_map)
            if pwn30_map is not None
            else self.root / "ili-map-pwn30.tab"
        )
        self.dump_pwn30_map = (
            Path(dump_pwn30_map)
            if dump_pwn30_map is not None
            else self.root / "ili-map-pwn30.tab"
        )
        self.ili_ttl = self.root / "ili.ttl"
        if index_path is not None:
            self.index_path = Path(index_path)
        else:
            self.index_path = (
                Path(__file__).resolve().parent / "data" / "cili.sqlite"
            )
        self.pin = (pin or "").strip() or None
        self.write_pin = write_pin
        self._con: Optional[sqlite3.Connection] = None
        self._lock = Lock()
        self._off2ili: Optional[dict[str, str]] = None
        self._ili2off: Optional[dict[str, str]] = None
        self._map_hash_warning: Optional[str] = None

    # -- construction from config ------------------------------------------

    @classmethod
    def from_config(cls, cfg: dict[str, Any] | None = None) -> "CiliEngine":
        if cfg is None:
            from semantic.settings import load_config

            cfg = load_config()
        from semantic.settings import ROOT, resolve_path

        def _p(key: str, default: str) -> Path:
            raw = cfg.get(key) or default
            p = Path(str(raw))
            if p.is_absolute():
                return p
            return resolve_path(raw, root=ROOT)

        root = _p("cili_root", "cili-master/cili-master")
        omw = _p("cili_omw_dir", str(Path(cfg.get("cili_root") or root)))
        pwn = _p(
            "cili_pwn30_map",
            str(cfg.get("cili_map") or "engines/LexWarrant/data/cili/ili-map-pwn30.tab"),
        )
        return cls(
            root=root,
            omw_dir=omw,
            pwn30_map=pwn,
            dump_pwn30_map=root / "ili-map-pwn30.tab",
            pin=str(cfg.get("cili") or "").strip() or None,
            write_pin=True,
        )

    # -- sources / freshness -----------------------------------------------

    def mapping_files(self) -> list[tuple[str, Path, str]]:
        return discover_mapping_files(self.root)

    def omw_files(self) -> list[Path]:
        return discover_omw_files(self.omw_dir, self.root)

    def source_files(self) -> list[Path]:
        files = [self.ili_ttl]
        files.extend(p for _r, p, _l in self.mapping_files() if p.exists())
        files.extend(self.omw_files())
        if self.pwn30_map.exists():
            files.append(self.pwn30_map)
        return [p for p in files if p.exists()]

    def source_files_mtime(self) -> float:
        files = self.source_files()
        if not files:
            return 0.0
        return max(os.path.getmtime(p) for p in files)

    def index_is_fresh(self) -> bool:
        if not self.index_path.exists():
            return False
        try:
            con = sqlite3.connect(f"file:{self.index_path}?mode=ro", uri=True)
            row = con.execute(
                "SELECT value FROM meta WHERE key='source_mtime'"
            ).fetchone()
            ver = con.execute(
                "SELECT value FROM meta WHERE key='schema_version'"
            ).fetchone()
            con.close()
            return (
                row is not None
                and float(row[0]) >= self.source_files_mtime()
                and ver is not None
                and ver[0] == SCHEMA_VERSION
            )
        except Exception:  # noqa: BLE001
            return False

    def discovered_languages(self) -> list[str]:
        langs = {lang for _r, p, lang in self.mapping_files() if p.exists() and lang}
        for path in self.omw_files():
            lg = lang_from_omw_name(path)
            if lg:
                langs.add(lg)
        return sorted(langs)

    # -- identity (exact, never fabricate) ---------------------------------

    def _load_identity(self) -> None:
        if self._off2ili is not None:
            return
        self._off2ili, self._ili2off = load_pwn30_map(self.pwn30_map)

    def ili_for_pwn30(self, offset: str) -> Optional[str]:
        """Exact PWN-3.0 offset → CILI id, or ``None``. No a↔s flip."""
        bare = _bare_offset(offset)
        if bare is None:
            return None
        self._load_identity()
        return (self._off2ili or {}).get(bare)

    def pwn30_for_ili(self, ili: str) -> Optional[str]:
        """Exact CILI id → PWN-3.0 offset, or ``None``."""
        cid = canonical_ili(ili)
        if cid is None:
            return None
        self._load_identity()
        return (self._ili2off or {}).get(cid)

    # -- index -------------------------------------------------------------

    def build_index(self, force: bool = False, verbose: bool = True) -> dict[str, Any]:
        """Build ``cili.sqlite`` from configured sources. Freshness = mtimes + schema."""
        if not force and self.index_is_fresh():
            stats = self.stats()
            if verbose:
                print("CILI index is fresh — skip rebuild.", flush=True)
            return {"rebuilt": False, "path": str(self.index_path), "stats": stats}

        if not self.ili_ttl.exists():
            raise FileNotFoundError(
                f"ili.ttl not found at {self.ili_ttl} — check [cili] root "
                "(folder that directly contains ili.ttl)."
            )
        if not fts5_available():
            raise RuntimeError("SQLite FTS5 is not available in this Python build.")

        self.close()
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        if self.index_path.exists():
            os.remove(self.index_path)

        t0 = time.time()
        con = sqlite3.connect(self.index_path)
        cur = con.cursor()
        cur.executescript(
            """
            PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
            CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE concepts(
                id INTEGER PRIMARY KEY, ili TEXT UNIQUE, kind TEXT,
                definition TEXT, deflang TEXT, source TEXT,
                pos TEXT, pos_norm TEXT, status TEXT, superseded_by TEXT);
            CREATE TABLE lemmas(
                ili TEXT, lemma TEXT, lemma_lc TEXT,
                resource TEXT, target TEXT, lang TEXT);
            CREATE INDEX idx_lem_l ON lemmas(lemma_lc);
            CREATE INDEX idx_lem_i ON lemmas(ili);
            CREATE INDEX idx_lem_lang ON lemmas(lang);
            CREATE VIRTUAL TABLE fts USING fts5(
                ili UNINDEXED, lemmas, definition, tokenize='porter unicode61');
            """
        )
        if verbose:
            print("Parsing ili.ttl ...", flush=True)
        text = self.ili_ttl.read_text(encoding="utf-8")
        concepts: dict[str, dict[str, Any]] = {}
        for m in CONCEPT_RE.finditer(text):
            ili, kind, body = m.group(1), m.group(2), m.group(3)
            if not is_ili_id(ili):
                continue
            d = DEF_RE.search(body)
            s = SRC_RE.search(body)
            st = STATUS_RE.search(body)
            sb = SUPERSEDED_RE.search(body)
            definition = d.group(1).replace('\\"', '"') if d else ""
            deflang = d.group(2) if d else ""
            source = s.group(1) if s else ""
            raw_pos = source.rsplit("-", 1)[-1] if "-" in source else ""
            pos = raw_pos if raw_pos in POS_NAMES else ""
            concepts[ili] = dict(
                ili=ili,
                kind=kind,
                definition=definition,
                deflang=deflang,
                source=source,
                pos=pos,
                pos_norm=pos_norm(pos) if pos else "",
                status=st.group(1) if st else "active",
                superseded_by=sb.group(1) if sb else None,
            )
        cur.executemany(
            "INSERT INTO concepts(id, ili, kind, definition, deflang, source, "
            "pos, pos_norm, status, superseded_by) VALUES(?,?,?,?,?,?,?,?,?,?)",
            [
                (
                    int(c["ili"][1:]),
                    c["ili"],
                    c["kind"],
                    c["definition"],
                    c["deflang"],
                    c["source"],
                    c["pos"],
                    c["pos_norm"],
                    c["status"],
                    c["superseded_by"],
                )
                for c in concepts.values()
            ],
        )
        if verbose:
            print(f"  {len(concepts)} concepts", flush=True)

        lemma_rows: list[tuple[str, str, str, str, str, str]] = []
        labels_by_resource: dict[str, int] = {}
        labels_by_lang: dict[str, int] = {}
        for resource, path, lang in self.mapping_files():
            if not path.exists():
                continue
            if verbose:
                print(f"Parsing {path.name} ...", flush=True)
            n = 0
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    m = MAP_RE.match(line.strip())
                    if not m:
                        continue
                    ili, _pfx, target, comment = m.groups()
                    if not is_ili_id(ili):
                        continue
                    if comment:
                        for lemma in comment.split(","):
                            lemma = lemma.strip()
                            if lemma:
                                lemma_rows.append(
                                    (ili, lemma, lemma.lower(), resource, target, lang)
                                )
                                n += 1
                    else:
                        lemma_rows.append((ili, "", "", resource, target, lang))
            labels_by_resource[resource] = n
            labels_by_lang[lang] = labels_by_lang.get(lang, 0) + n
            if verbose:
                print(f"  {n} lemma labels ({lang})", flush=True)

        off2ili, _ = load_pwn30_map(self.pwn30_map)
        packs = self.omw_files()
        if packs and off2ili:
            for path in packs:
                lang = lang_from_omw_name(path)
                resource = f"omw-{lang}" if lang else "omw"
                if verbose:
                    print(f"Parsing {path.name} (OMW, {lang}) ...", flush=True)
                n = 0
                with open(path, encoding="utf-8") as fh:
                    for line in fh:
                        if line.startswith("#"):
                            continue
                        parts = line.rstrip("\n").split("\t")
                        if len(parts) < 3 or parts[1].split(":")[-1] != "lemma":
                            continue
                        ili = off2ili.get(parts[0])
                        lemma = parts[2].strip()
                        if ili and lemma:
                            lemma_rows.append(
                                (ili, lemma, lemma.lower(), resource, parts[0], lang)
                            )
                            n += 1
                labels_by_resource[resource] = n
                labels_by_lang[lang] = labels_by_lang.get(lang, 0) + n
                if verbose:
                    print(f"  {n} lemma labels", flush=True)
        elif packs and verbose:
            print(
                "OMW packs present but live pwn30 map missing — packs skipped.",
                flush=True,
            )

        cur.executemany(
            "INSERT INTO lemmas(ili, lemma, lemma_lc, resource, target, lang) "
            "VALUES(?,?,?,?,?,?)",
            lemma_rows,
        )
        if verbose:
            print("Building FTS index ...", flush=True)
        lem_by_ili: dict[str, set[str]] = {}
        for ili, lemma, _lc, _resource, _t, _lang in lemma_rows:
            if lemma:
                lem_by_ili.setdefault(ili, set()).add(lemma)
        cur.executemany(
            "INSERT INTO fts(ili, lemmas, definition) VALUES(?,?,?)",
            [
                (
                    c["ili"],
                    "; ".join(sorted(lem_by_ili.get(c["ili"], []))),
                    c["definition"],
                )
                for c in concepts.values()
            ],
        )

        ttl_hash = sha256_file(self.ili_ttl)
        ttl_prefix = ttl_hash[:12]
        live_hash = sha256_file(self.pwn30_map) if self.pwn30_map.exists() else ""
        dump_hash = (
            sha256_file(self.dump_pwn30_map) if self.dump_pwn30_map.exists() else ""
        )
        maps_differ = bool(live_hash and dump_hash and live_hash != dump_hash)
        if maps_differ:
            self._map_hash_warning = (
                f"pwn30 maps differ: live={self.pwn30_map} ({live_hash[:12]}) "
                f"vs dump={self.dump_pwn30_map} ({dump_hash[:12]}). "
                "Identity joins use the configured live map."
            )
            if verbose:
                print("WARNING: " + self._map_hash_warning, flush=True)

        meta_rows = [
            ("source_mtime", str(self.source_files_mtime())),
            ("schema_version", SCHEMA_VERSION),
            ("built_at", time.strftime("%Y-%m-%d %H:%M:%S")),
            ("ili_ttl_sha256", ttl_hash),
            ("ili_ttl_sha256_prefix", ttl_prefix),
            ("pwn30_live_sha256", live_hash),
            ("pwn30_dump_sha256", dump_hash),
            ("pwn30_maps_differ", "1" if maps_differ else "0"),
            ("pwn30_live_path", str(self.pwn30_map)),
            ("pwn30_dump_path", str(self.dump_pwn30_map)),
            ("languages", ",".join(self.discovered_languages())),
        ]
        cur.executemany("INSERT INTO meta VALUES(?,?)", meta_rows)
        con.commit()
        con.close()
        elapsed = time.time() - t0
        if verbose:
            print(
                f"Index built in {elapsed:.1f} s -> {self.index_path}",
                flush=True,
            )
            for lg, n in sorted(labels_by_lang.items()):
                print(f"  labels[{lg}] = {n}", flush=True)

        pin_note = self._maybe_write_pin(ttl_prefix)
        stats = self.stats()
        return {
            "rebuilt": True,
            "path": str(self.index_path),
            "elapsed_s": round(elapsed, 2),
            "concepts": len(concepts),
            "labels_by_lang": labels_by_lang,
            "labels_by_resource": labels_by_resource,
            "languages": self.discovered_languages(),
            "ili_ttl_sha256_prefix": ttl_prefix,
            "pwn30_maps_differ": maps_differ,
            "map_hash_warning": self._map_hash_warning,
            "pin_written": pin_note,
            "stats": stats,
        }

    def _maybe_write_pin(self, prefix: str) -> Optional[str]:
        """Record ``[pins] cili`` on first successful build; never auto-update."""
        if self.pin or not self.write_pin:
            return None
        try:
            from semantic.settings import write_cili_pin_if_absent

            wrote = write_cili_pin_if_absent(prefix)
        except Exception:  # noqa: BLE001
            return None
        if wrote:
            self.pin = prefix
            return prefix
        return None

    # -- connection --------------------------------------------------------

    def _db(self) -> sqlite3.Connection:
        if self._con is None:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    f"CILI index missing: {self.index_path} — run `python sr.py cili index`"
                )
            self._con = sqlite3.connect(
                f"file:{self.index_path}?mode=ro", uri=True, check_same_thread=False
            )
            self._con.row_factory = sqlite3.Row
        return self._con

    def close(self) -> None:
        if self._con is not None:
            try:
                self._con.close()
            except Exception:  # noqa: BLE001
                pass
            self._con = None

    def q(self, sql: str, args: Iterable[Any] = ()) -> list[dict[str, Any]]:
        with self._lock:
            return [dict(r) for r in self._db().execute(sql, tuple(args)).fetchall()]

    def meta(self) -> dict[str, str]:
        try:
            return {r["key"]: r["value"] for r in self.q("SELECT * FROM meta")}
        except Exception:  # noqa: BLE001
            return {}

    # -- queries -----------------------------------------------------------

    def concept(self, ili: str) -> Optional[dict[str, Any]]:
        cid = canonical_ili(ili)
        if cid is None:
            return None
        rows = self.q("SELECT * FROM concepts WHERE ili=?", (cid,))
        if not rows:
            return None
        c = rows[0]
        c["pos_name"] = POS_NAMES.get(c["pos"], c["pos"] or "—")
        c["pos_norm"] = c.get("pos_norm") or pos_norm(c.get("pos") or "")
        c["rdf_uri"] = CILI_RDF.format(ili=cid)
        c["page_uri"] = CILI_PAGE.format(ili=cid)
        c["mappings"] = self.q(
            "SELECT resource, target, group_concat(DISTINCT lemma) AS lemmas "
            "FROM lemmas WHERE ili=? GROUP BY resource, target ORDER BY resource",
            (cid,),
        )
        lemrows = self.q(
            "SELECT DISTINCT lemma, lang FROM lemmas WHERE ili=? AND lemma<>''",
            (cid,),
        )
        c["lemmas"] = sorted({r["lemma"] for r in lemrows})
        by_lang: dict[str, set[str]] = {}
        for r in lemrows:
            by_lang.setdefault(r["lang"], set()).add(r["lemma"])
        c["by_lang"] = {k: sorted(v) for k, v in sorted(by_lang.items())}
        c["shared"] = self.q(
            """SELECT l2.lemma AS via, c2.ili, c2.definition, c2.pos, c2.pos_norm,
                      count(*) AS nshared
               FROM lemmas l1
               JOIN lemmas l2 ON l1.lemma_lc = l2.lemma_lc AND l2.ili<>l1.ili
               JOIN concepts c2 ON c2.ili = l2.ili
               WHERE l1.ili=? AND l1.lemma<>''
               GROUP BY c2.ili ORDER BY nshared DESC, c2.id LIMIT 40""",
            (cid,),
        )
        words = [w for w in re.findall(r"[a-zA-Z]{4,}", c["definition"] or "")][:8]
        c["similar"] = []
        if words:
            expr = " OR ".join('"%s"' % w for w in words)
            try:
                c["similar"] = self.q(
                    """SELECT fts.ili, c2.definition, c2.pos, c2.pos_norm,
                              bm25(fts) AS rank
                       FROM fts JOIN concepts c2 ON c2.ili=fts.ili
                       WHERE fts MATCH ? AND fts.ili<>? ORDER BY rank LIMIT 15""",
                    ("definition: (%s)" % expr, cid),
                )
            except sqlite3.OperationalError:
                pass
        c["superseders"] = self.q(
            "SELECT ili, definition FROM concepts WHERE superseded_by=?", (cid,)
        )
        return c

    def entry(self, lemma: str) -> dict[str, Any]:
        lemma = (lemma or "").strip()
        rows = self.q(
            """SELECT DISTINCT c.ili, c.kind, c.definition, c.pos, c.pos_norm,
                      c.status, l.lang
               FROM lemmas l JOIN concepts c ON c.ili=l.ili
               WHERE l.lemma_lc = ? ORDER BY c.pos_norm, c.id""",
            (lemma.lower(),),
        )
        src_langs = sorted({r["lang"] for r in rows})
        ilis = sorted({r["ili"] for r in rows})
        trans: dict[str, dict[str, set[str]]] = {}
        if ilis:
            ph = ",".join("?" * len(ilis))
            for t in self.q(
                f"SELECT ili, lang, lemma FROM lemmas WHERE ili IN ({ph}) AND lemma<>''",
                ilis,
            ):
                trans.setdefault(t["ili"], {}).setdefault(t["lang"], set()).add(
                    t["lemma"]
                )
        seen: set[str] = set()
        groups: dict[str, list[dict[str, Any]]] = {}
        for r in rows:
            if r["ili"] in seen:
                continue
            seen.add(r["ili"])
            r["pos_name"] = POS_NAMES.get(r["pos"], r["pos"] or "—")
            r["pos_norm"] = r.get("pos_norm") or pos_norm(r.get("pos") or "")
            r["translations"] = {
                lg: sorted(v) for lg, v in sorted(trans.get(r["ili"], {}).items())
            }
            group_key = POS_NAMES.get(r["pos_norm"], r["pos_norm"] or "other")
            groups.setdefault(group_key, []).append(r)
        equiv: dict[tuple[str, str], int] = {}
        for ili in seen:
            for lg, lems in trans.get(ili, {}).items():
                for lm in lems:
                    if lm.lower() == lemma.lower():
                        continue
                    key = (lg, lm)
                    equiv[key] = equiv.get(key, 0) + 1
        equivalents: dict[str, list[dict[str, Any]]] = {}
        for (lg, lm), n in sorted(equiv.items(), key=lambda kv: (-kv[1], kv[0])):
            equivalents.setdefault(lg, []).append({"lemma": lm, "shared_senses": n})
        for lg in equivalents:
            equivalents[lg] = equivalents[lg][:25]
        all_langs = self._indexed_languages()
        gaps = {
            lg: [i for i in sorted(seen) if lg not in trans.get(i, {})]
            for lg in all_langs
        }
        return {
            "lemma": lemma,
            "langs": src_langs,
            "groups": groups,
            "count": len(seen),
            "equivalents": equivalents,
            "gaps": gaps,
        }

    def search(
        self,
        q: str,
        mode: str = "any",
        pos: str = "",
        kind: str = "",
        lang: str = "",
        resource: str = "",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        match = fts_escape(q)
        if not match:
            return {"total": 0, "results": []}
        col = {"lemma": "lemmas", "definition": "definition"}.get(mode)
        expr = f"{col}: ({match})" if col else match
        where: list[str] = ["fts MATCH ?"]
        args: list[Any] = [expr]
        join = "JOIN concepts c ON c.ili = fts.ili"
        pos = (pos or "").strip().lower()
        if pos == "s":
            where.append("c.pos = ?")
            args.append(pos)
        elif pos:
            where.append("c.pos_norm = ?")
            args.append(pos)
        if kind:
            where.append("c.kind = ?")
            args.append(kind)
        extra = 1
        if resource:
            join += (
                " JOIN (SELECT DISTINCT ili FROM lemmas WHERE resource=?) lr "
                "ON lr.ili=c.ili"
            )
            args.insert(extra, resource)
            extra += 1
        if lang:
            join += (
                " JOIN (SELECT DISTINCT ili FROM lemmas WHERE lang=?) ll "
                "ON ll.ili=c.ili"
            )
            args.insert(extra, lang)
        sql = (
            f"SELECT c.ili, c.kind, c.definition, c.pos, c.pos_norm, c.status, "
            f"c.source, "
            f"snippet(fts, 1, '<b>', '</b>', ' … ', 12) AS lem_snip, "
            f"snippet(fts, 2, '<b>', '</b>', ' … ', 18) AS def_snip, "
            f"bm25(fts) AS rank "
            f"FROM fts {join} WHERE {' AND '.join(where)} "
            f"ORDER BY rank LIMIT ? OFFSET ?"
        )
        rows = self.q(sql, args + [limit, offset])
        for r in rows:
            r["pos_name"] = POS_NAMES.get(r["pos"], r["pos"] or "—")
        total = self.q(
            f"SELECT count(*) AS n FROM fts {join} WHERE {' AND '.join(where)}",
            args,
        )[0]["n"]
        return {"total": total, "results": rows}

    def stats(self) -> dict[str, Any]:
        s: dict[str, Any] = {}
        s["concepts"] = self.q("SELECT count(*) n FROM concepts")[0]["n"]
        s["by_kind"] = self.q("SELECT kind, count(*) n FROM concepts GROUP BY kind")
        s["by_pos"] = self.q(
            "SELECT pos, count(*) n FROM concepts GROUP BY pos ORDER BY n DESC"
        )
        s["by_pos_norm"] = self.q(
            "SELECT pos_norm, count(*) n FROM concepts GROUP BY pos_norm ORDER BY n DESC"
        )
        s["by_status"] = self.q(
            "SELECT status, count(*) n FROM concepts GROUP BY status"
        )
        s["lemma_labels"] = self.q(
            "SELECT resource, count(*) n FROM lemmas WHERE lemma<>'' GROUP BY resource"
        )
        s["labels_by_lang"] = self.q(
            "SELECT lang, count(*) n FROM lemmas WHERE lemma<>'' GROUP BY lang"
        )
        s["distinct_lemmas"] = self.q(
            "SELECT count(DISTINCT lemma_lc) n FROM lemmas WHERE lemma<>''"
        )[0]["n"]
        s["languages"] = [r["lang"] for r in s["labels_by_lang"] if r.get("lang")]
        s["no_lemma"] = self.q(
            """SELECT count(*) n FROM concepts c WHERE NOT EXISTS
               (SELECT 1 FROM lemmas l WHERE l.ili=c.ili AND l.lemma<>'')"""
        )[0]["n"]
        s["meta"] = self.meta()
        s["index_path"] = str(self.index_path)
        s["index_fresh"] = self.index_is_fresh()
        return s

    def _indexed_languages(self) -> list[str]:
        try:
            rows = self.q(
                "SELECT DISTINCT lang FROM lemmas WHERE lang<>'' ORDER BY lang"
            )
            return [r["lang"] for r in rows]
        except Exception:  # noqa: BLE001
            return self.discovered_languages()
