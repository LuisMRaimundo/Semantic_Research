"""Hyperlinks from GUI sense cards → public IDs + live local resource views.

Every link either points at an official public identifier (CILI / OEWN) or at a
small HTML page materialised from the live local DB / ``wn`` lexicon, so the
GUI never claims an id that cannot be re-fetched from the associated resource.
"""

from __future__ import annotations

import html
import sqlite3
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import quote

from . import settings
from .normalize import normalize_word, pretty_word

OEWN_PAGE_BASE = "https://en-word.net/id/"
ONTO_RDF_BASE = "http://ontopt.dei.uc.pt/OntoPT.owl#"
OWNPT_REPO = "https://github.com/own-pt/openWordnet-PT"
PAPEL_HOME = "https://www.linguateca.pt/PAPEL/"


@dataclass
class ResourceLink:
    label: str
    url: str
    kind: str  # cili | oewn | onto | pulo | papel | ownpt | local | export
    verified: bool
    identifier: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _try_cili_page(raw: Any) -> Optional[tuple[str, str]]:
    if not raw:
        return None
    try:
        from .engines import load_identifiers
        ids = load_identifiers()
        cid = ids.try_normalize_cili_id(str(raw))
        if not cid:
            return None
        return cid, ids.cili_page_url(cid)
    except Exception:  # noqa: BLE001
        s = str(raw).strip()
        if s.startswith("i") and s[1:].isdigit():
            return s, f"https://globalwordnet.github.io/cili/{s}.html"
        return None


def _oewn_id(raw: Any) -> Optional[str]:
    s = str(raw or "").strip()
    if not s:
        return None
    if s.startswith("oewn-"):
        return s
    # bare 8digit-pos
    import re
    m = re.fullmatch(r"(\d{8})-([a-z])", s, re.I)
    if m:
        return f"oewn-{m.group(1)}-{m.group(2).lower()}"
    m = re.fullmatch(r"(?:eng|por)-30-(\d{8})-([a-z])", s, re.I)
    if m:
        return f"oewn-{m.group(1)}-{m.group(2).lower()}"
    m = re.fullmatch(r"pwn30-(\d{8})-([a-z])", s, re.I)
    if m:
        return f"oewn-{m.group(1)}-{m.group(2).lower()}"
    m = re.fullmatch(r"ili-30-(\d{8})-([a-z])", s, re.I)
    if m:
        return f"oewn-{m.group(1)}-{m.group(2).lower()}"
    return None


def _por30_from_key(key: str) -> Optional[str]:
    s = (key or "").strip()
    if s.startswith("por-30-"):
        return s
    import re
    m = re.fullmatch(r"(?:ili-30-|pwn30-|eng-30-)(\d{8})-([a-z])", s, re.I)
    if m:
        return f"por-30-{m.group(1)}-{m.group(2).lower()}"
    m = re.fullmatch(r"(\d{8})-([a-z])", s, re.I)
    if m:
        return f"por-30-{m.group(1)}-{m.group(2).lower()}"
    return None


def _ili30_from_key(key: str) -> Optional[str]:
    s = (key or "").strip()
    if s.startswith("ili-30-"):
        return s
    import re
    m = re.fullmatch(r"(?:por-30-|pwn30-|eng-30-)(\d{8})-([a-z])", s, re.I)
    if m:
        return f"ili-30-{m.group(1)}-{m.group(2).lower()}"
    return None


def verify_pulo_offset(offset: str) -> bool:
    cfg = settings.load_config()
    db = Path(cfg["pulo_sqlite"])
    if not db.exists() or not offset:
        return False
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        n = con.execute(
            "SELECT 1 FROM synset WHERE offset=? LIMIT 1", (offset,)
        ).fetchone()
        if not n:
            # Schema: to_ili(iliOffset, pos, offset, iliWnId, csco)
            ili = _ili30_from_key(offset) or offset
            n = con.execute(
                "SELECT 1 FROM to_ili WHERE iliOffset=? OR offset=? LIMIT 1",
                (ili, offset),
            ).fetchone()
        con.close()
        return bool(n)
    except sqlite3.Error:
        return False


def verify_onto_key(key: str) -> bool:
    if ":" not in (key or ""):
        return False
    res, _, sid = key.partition(":")
    cfg = settings.load_config()
    db = Path(cfg["onto_sqlite"])
    if not db.exists() or not res or not sid:
        return False
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        n = con.execute(
            "SELECT 1 FROM synset WHERE res=? AND sid=? LIMIT 1", (res, sid)
        ).fetchone()
        con.close()
        return bool(n)
    except sqlite3.Error:
        return False


def verify_oewn_id(oewn: str) -> bool:
    try:
        import wn  # type: ignore
        pin = str(settings.load_config().get("oewn") or "oewn:2024")
        w = wn.Wordnet(pin)
        return w.synset(oewn) is not None
    except Exception:  # noqa: BLE001
        return False


def verify_papel_key(key: str) -> bool:
    """Keys look like ``papel35:GROUP:REL:lemma``."""
    cfg = settings.load_config()
    db = Path(cfg.get("papel_sqlite") or (settings.ROOT / "data" / "papel.sqlite"))
    if not db.is_absolute():
        db = settings.resolve_path(db)
    if not db.exists():
        return False
    parts = (key or "").split(":")
    # papel35:SINONIMIA:SINONIMO_N_DE:compósito
    lemma = parts[-1] if parts else ""
    qn = normalize_word(lemma)
    if not qn:
        return False
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        n = con.execute(
            "SELECT 1 FROM triple WHERE w1_norm=? OR w2_norm=? LIMIT 1",
            (qn, qn),
        ).fetchone()
        con.close()
        return bool(n)
    except sqlite3.Error:
        return False


def _fetch_pulo_view(offset: str) -> Optional[dict[str, Any]]:
    cfg = settings.load_config()
    db = Path(cfg["pulo_sqlite"])
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute("SELECT * FROM synset WHERE offset=? LIMIT 1", (offset,)).fetchone()
    if not row:
        ili = _ili30_from_key(offset)
        if ili:
            mapr = con.execute(
                "SELECT offset FROM to_ili WHERE iliOffset=? LIMIT 1", (ili,)
            ).fetchone()
            if mapr:
                offset = mapr["offset"]
                row = con.execute(
                    "SELECT * FROM synset WHERE offset=? LIMIT 1", (offset,)
                ).fetchone()
    if not row:
        con.close()
        return None
    members = [
        r["word"]
        for r in con.execute(
            "SELECT word FROM variant WHERE offset=? ORDER BY sense, word",
            (offset,),
        )
    ]
    ili_rows = list(con.execute(
        "SELECT * FROM to_ili WHERE offset=?", (offset,)
    ))
    con.close()
    return {
        "resource": "PULO",
        "id": offset,
        "pos": row["pos"],
        "gloss": row["gloss"] or "",
        "members": members,
        "ili_map": [dict(r) for r in ili_rows],
    }


def _fetch_onto_view(key: str) -> Optional[dict[str, Any]]:
    if ":" not in key:
        return None
    res, _, sid = key.partition(":")
    cfg = settings.load_config()
    db = Path(cfg["onto_sqlite"])
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    row = con.execute(
        "SELECT * FROM synset WHERE res=? AND sid=? LIMIT 1", (res, sid)
    ).fetchone()
    if not row:
        con.close()
        return None
    members = [
        r["word"]
        for r in con.execute(
            "SELECT word FROM member WHERE res=? AND sid=? ORDER BY weight DESC, word",
            (res, sid),
        )
    ]
    con.close()
    return {
        "resource": f"Onto.PT ({res})",
        "id": key,
        "rdf_uri": f"{ONTO_RDF_BASE}{sid}" if res == "ontopt06" else "",
        "pos": row["pos"] or "",
        "gloss": row["gloss"] or "",
        "members": members,
    }


def _fetch_papel_view(key: str) -> Optional[dict[str, Any]]:
    parts = (key or "").split(":")
    lemma = parts[-1] if parts else ""
    group = parts[1] if len(parts) > 2 else ""
    rel = parts[2] if len(parts) > 3 else ""
    qn = normalize_word(lemma)
    cfg = settings.load_config()
    db = Path(cfg.get("papel_sqlite") or (settings.ROOT / "data" / "papel.sqlite"))
    if not db.is_absolute():
        db = settings.resolve_path(db)
    if not db.exists() or not qn:
        return None
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    sql = "SELECT * FROM triple WHERE (w1_norm=? OR w2_norm=?) "
    params: list[Any] = [qn, qn]
    if group:
        sql += "AND group_name=? "
        params.append(group.upper())
    if rel:
        sql += "AND rel=? "
        params.append(rel)
    sql += "LIMIT 80"
    rows = list(con.execute(sql, params))
    con.close()
    if not rows:
        return None
    triples = [
        f"{r['w1']} {r['rel']} {r['w2']}"
        for r in rows
    ]
    return {
        "resource": "PAPEL 3.5",
        "id": key,
        "pos": "",
        "gloss": f"{len(rows)} triplo(s) · grupo={group or '—'} · rel={rel or '—'}",
        "members": [],
        "triples": triples,
    }


def _fetch_oewn_view(oewn: str) -> Optional[dict[str, Any]]:
    try:
        import wn  # type: ignore
        pin = str(settings.load_config().get("oewn") or "oewn:2024")
        w = wn.Wordnet(pin)
        raw = w.synset(oewn)
        if raw is None:
            return None
        ili = getattr(raw, "ili", None)
        ili_s = ""
        if ili is not None:
            ili_s = ili.id if hasattr(ili, "id") else str(ili)
        return {
            "resource": f"OEWN ({pin})",
            "id": oewn,
            "pos": raw.pos,
            "gloss": raw.definition() or "",
            "members": list(raw.lemmas()),
            "ili": ili_s,
        }
    except Exception:  # noqa: BLE001
        return None


def materialize_local_view(sense: dict[str, Any]) -> Optional[Path]:
    """Write a small HTML page from the live resource; return its path."""
    src = (sense.get("source") or "").lower()
    key = str(sense.get("key") or sense.get("local_id") or "")
    data: Optional[dict[str, Any]] = None
    if src == "pulo":
        off = _por30_from_key(key) or key
        data = _fetch_pulo_view(off)
    elif src == "onto":
        data = _fetch_onto_view(key)
    elif src == "papel":
        data = _fetch_papel_view(key)
    elif src in ("wordnet", "oewn", "own-pt", "ownpt"):
        oid = _oewn_id(sense.get("local_id") or key)
        if oid:
            data = _fetch_oewn_view(oid)
    if not data:
        return None

    out_dir = settings.ROOT / "data" / "link_views"
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = quote(f"{src}_{key}", safe="")[:120]
    path = out_dir / f"{safe}.html"

    members = "".join(
        f"<li>{html.escape(pretty_word(str(m)))}</li>" for m in (data.get("members") or [])
    )
    triples = "".join(
        f"<li><code>{html.escape(t)}</code></li>" for t in (data.get("triples") or [])
    )
    ili = html.escape(str(data.get("ili") or sense.get("cili") or sense.get("ili") or "—"))
    rdf = html.escape(str(data.get("rdf_uri") or ""))
    body = f"""<!DOCTYPE html>
<html lang="pt"><head><meta charset="utf-8">
<title>{html.escape(data.get('resource',''))} · {html.escape(data.get('id',''))}</title>
<style>
 body {{ font-family: Georgia, serif; max-width: 720px; margin: 2rem auto; padding: 0 1rem; }}
 h1 {{ font-size: 1.25rem; }} code {{ background: #f4f4f4; padding: 0.1em 0.3em; }}
 .meta {{ color: #444; }} .ok {{ color: #0a5; font-weight: bold; }}
</style></head><body>
<p class="ok">✓ Reconfirmado no recurso local</p>
<h1>{html.escape(data.get('resource',''))}</h1>
<p class="meta">identificador: <code>{html.escape(str(data.get('id','')))}</code>
 · pos: <code>{html.escape(str(data.get('pos','')))}</code>
 · CILI/ILI: <code>{ili}</code></p>
{f'<p>RDF URI: <code>{rdf}</code></p>' if rdf else ''}
<p>{html.escape(str(data.get('gloss') or ''))}</p>
{"<h2>Membros</h2><ul>" + members + "</ul>" if members else ""}
{"<h2>Triplos PAPEL</h2><ul>" + triples + "</ul>" if triples else ""}
</body></html>
"""
    path.write_text(body, encoding="utf-8")
    return path


def links_for_sense(sense: dict[str, Any]) -> list[ResourceLink]:
    """Build clickable links for a decisions.json sense card."""
    src = (sense.get("source") or "").lower()
    key = str(sense.get("key") or "")
    local = str(sense.get("local_id") or key)
    out: list[ResourceLink] = []

    # CILI (any source that carries it)
    cili_raw = sense.get("cili") or sense.get("cili_id") or sense.get("ili")
    cili_hit = _try_cili_page(cili_raw)
    if cili_hit:
        cid, page = cili_hit
        out.append(ResourceLink(
            label=f"CILI {cid}",
            url=page,
            kind="cili",
            verified=True,
            identifier=cid,
            detail="página oficial CILI",
        ))

    if src == "pulo":
        por = _por30_from_key(key) or key
        ok = verify_pulo_offset(por)
        out.append(ResourceLink(
            label=f"PULO {por}" + ("" if ok else " (?)"),
            url="local:",  # materialised on click
            kind="local",
            verified=ok,
            identifier=por,
            detail=(
                "vista local a partir de pulo.sqlite"
                if ok else "offset não encontrado em pulo.sqlite"
            ),
        ))

    elif src == "onto":
        ok = verify_onto_key(key)
        res, _, sid = key.partition(":")
        if res == "ontopt06" and sid:
            uri = f"{ONTO_RDF_BASE}{sid}"
            out.append(ResourceLink(
                label=f"Onto RDF #{sid}",
                url=uri,
                kind="onto",
                verified=ok,
                identifier=uri,
                detail="URI Onto.PT v0.6 (RDF)",
            ))
        out.append(ResourceLink(
            label=f"Onto {key}" + ("" if ok else " (?)"),
            url="local:",
            kind="local",
            verified=ok,
            identifier=key,
            detail=(
                "vista local a partir de ontopt.sqlite"
                if ok else "synset ausente em ontopt.sqlite"
            ),
        ))

    elif src == "papel":
        ok = verify_papel_key(key)
        out.append(ResourceLink(
            label="PAPEL (Linguateca)",
            url=PAPEL_HOME,
            kind="papel",
            verified=True,
            identifier="PAPEL.v.3.5",
            detail="página do recurso",
        ))
        lemma = key.split(":")[-1] if key else "vista"
        out.append(ResourceLink(
            label=f"PAPEL {lemma}" + ("" if ok else " (?)"),
            url="local:",
            kind="local",
            verified=ok,
            identifier=key,
            detail=(
                "triplos reconfirmados em papel.sqlite"
                if ok else "sem triplos em papel.sqlite"
            ),
        ))

    elif src in ("wordnet", "oewn"):
        oid = _oewn_id(local) or _oewn_id(key)
        if oid:
            ok = verify_oewn_id(oid)
            out.append(ResourceLink(
                label=f"OEWN {oid}",
                url=f"{OEWN_PAGE_BASE}{oid}",
                kind="oewn",
                verified=ok,
                identifier=oid,
                detail="en-word.net",
            ))
            out.append(ResourceLink(
                label=f"OEWN local {oid}",
                url="local:",
                kind="local",
                verified=ok,
                identifier=oid,
                detail="reconfirmado via wn pin",
            ))

    elif src in ("own-pt", "ownpt"):
        out.append(ResourceLink(
            label="OWN-PT (GitHub)",
            url=OWNPT_REPO,
            kind="ownpt",
            verified=True,
            identifier="own-pt:1.0.0",
            detail="repositório fonte",
        ))
        # attestation is ILI-mediated — CILI link already added above

    return out


def links_for_onto_ili(onto_key: str, ili: str) -> list[ResourceLink]:
    sense_onto = {"source": "onto", "key": onto_key}
    sense_cili = {"source": "pulo", "key": "", "cili": ili, "ili": ili}
    return links_for_sense(sense_onto) + [
        ln for ln in links_for_sense(sense_cili) if ln.kind == "cili"
    ]


def open_resource_link(link: ResourceLink, sense: Optional[dict[str, Any]] = None) -> bool:
    """Open a ResourceLink in the system browser; materialise local views on demand."""
    import webbrowser

    url = (link.url or "").strip()
    if url.startswith("local:") or (link.kind == "local" and (not url or url == "local:")):
        if not link.verified:
            return False
        sn = dict(sense or {})
        sn.setdefault("key", link.identifier)
        sn.setdefault("local_id", link.identifier)
        if not sn.get("source"):
            ident = link.identifier or ""
            if ident.startswith("por-30-") or ident.startswith("pwn30-"):
                sn["source"] = "pulo"
            elif ident.startswith("oewn-"):
                sn["source"] = "wordnet"
            elif ident.startswith("papel") or ":" in ident and any(
                g in ident.upper()
                for g in ("SINONIM", "HIPERONIM", "ANTONIM", "PARTE", "MATERIAL")
            ):
                sn["source"] = "papel"
            elif ":" in ident:
                sn["source"] = "onto"
            else:
                sn["source"] = "wordnet"
        path = materialize_local_view(sn)
        if path is None:
            return False
        webbrowser.open(path.as_uri())
        return True
    if not url:
        return False
    webbrowser.open(url)
    return True
