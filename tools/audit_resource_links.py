#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit GUI resource hyperlinks against live resources / docs."""

from __future__ import annotations

import json
import re
import sqlite3
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import wn  # type: ignore

from engines.LexWarrant import identifiers as ids
from semantic.resource_links import (
    OEWN_PAGE_BASE,
    ONTO_RDF_BASE,
    OWNPT_REPO,
    PAPEL_HOME,
    _fetch_onto_view,
    _fetch_papel_view,
    _fetch_pulo_view,
    links_for_sense,
)


def _get(url: str, nbytes: int = 20000) -> tuple[int | str, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "SR-link-audit/1.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.status, resp.read(nbytes).decode("utf-8", "replace")


def main() -> int:
    rows: list[tuple] = []

    # CILI
    page = ids.cili_page_url("i1")
    uri = ids.cili_uri("i1")
    try:
        code, body = _get(page)
        title = re.search(r"<title>(.*?)</title>", body, re.I | re.S)
        ok = code == 200 and ("i1" in body or "able" in body.lower())
        rows.append(("CILI page", page, code, ok, title.group(1).strip() if title else ""))
    except Exception as exc:  # noqa: BLE001
        rows.append(("CILI page", page, "ERR", False, str(exc)))
    rows.append((
        "CILI URI pattern",
        uri,
        "doc",
        uri == "http://ili.globalwordnet.org/ili/i1",
        "GWA / identifiers.py",
    ))

    # OEWN
    oid = "oewn-00001740-a"
    from semantic import settings as _cfg
    _pin = str(_cfg.load_config().get("oewn") or "oewn:2025")
    ss = wn.Wordnet(_pin).synset(oid)
    lemmas = list(ss.lemmas()) if ss else []
    definition = ss.definition() if ss else ""
    oewn_url = OEWN_PAGE_BASE + oid
    try:
        code, body = _get(oewn_url)
        has_lemma = any(l.lower() in body.lower() for l in lemmas[:3])
        rows.append((
            "OEWN page",
            oewn_url,
            code,
            code == 200 and has_lemma,
            f"lemmas={lemmas}; def~{definition[:70]}",
        ))
    except Exception as exc:  # noqa: BLE001
        rows.append(("OEWN page", oewn_url, "ERR", False, str(exc)))

    # PULO
    off = "por-30-00001740-a"
    pv = _fetch_pulo_view(off)
    con = sqlite3.connect(str(ROOT / "engines/PULO Thesaurus GUI/pulo.sqlite"))
    gloss = con.execute(
        "SELECT gloss FROM synset WHERE offset=?", (off,)
    ).fetchone()[0]
    variants = [
        r[0]
        for r in con.execute(
            "SELECT word FROM variant WHERE offset=? ORDER BY sense, word", (off,)
        )
    ]
    ili = con.execute(
        "SELECT iliOffset, offset FROM to_ili WHERE offset=?", (off,)
    ).fetchone()
    con.close()
    rows.append((
        "PULO local view",
        off,
        "sqlite",
        bool(pv) and pv["gloss"] == gloss and set(pv["members"]) == set(variants),
        f"ili={ili}; n_members={len(variants)}",
    ))

    # Onto
    key = "ontopt06:10"
    ov = _fetch_onto_view(key)
    con = sqlite3.connect(str(ROOT / "engines/ONTO/ontopt.sqlite"))
    row = con.execute(
        "SELECT pos, gloss FROM synset WHERE res=? AND sid=?", ("ontopt06", "10")
    ).fetchone()
    mems = [
        r[0]
        for r in con.execute(
            "SELECT word FROM member WHERE res=? AND sid=? ORDER BY word",
            ("ontopt06", "10"),
        )
    ]
    con.close()
    rows.append((
        "Onto local view",
        key,
        "sqlite",
        bool(ov)
        and ov["gloss"] == (row[1] or "")
        and set(ov["members"]) == set(mems),
        f"n_members={len(mems)}; gloss~{(row[1] or '')[:50]}",
    ))
    rdf_uri = ONTO_RDF_BASE + "10"
    found = False
    rdf_path = ROOT / "OntoPTv0.6_rdf" / "OntoPTv0.6.rdfs"
    needle = 'rdf:about="http://ontopt.dei.uc.pt/OntoPT.owl#10"'
    with rdf_path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if needle in line:
                found = True
                break
    rows.append((
        "Onto RDF id in dump",
        rdf_uri,
        "OntoPTv0.6.rdfs",
        found,
        "matches LEIAME / WN RDF Basic style ids",
    ))
    # Does the URI resolve on the web?
    try:
        code, body = _get(rdf_uri, 4000)
        rows.append((
            "Onto RDF HTTP",
            rdf_uri,
            code,
            code == 200,
            "live ontopt.dei.uc.pt (may be offline)",
        ))
    except Exception as exc:  # noqa: BLE001
        rows.append(("Onto RDF HTTP", rdf_uri, "ERR", False, str(exc)[:120]))

    # PAPEL
    try:
        code, body = _get(PAPEL_HOME, 8000)
        rows.append((
            "PAPEL home",
            PAPEL_HOME,
            code,
            code == 200 and "PAPEL" in body.upper(),
            "linguateca.pt/PAPEL",
        ))
    except Exception as exc:  # noqa: BLE001
        rows.append(("PAPEL home", PAPEL_HOME, "ERR", False, str(exc)[:120]))

    con = sqlite3.connect(str(ROOT / "data" / "papel.sqlite"))
    con.row_factory = sqlite3.Row
    sample = con.execute(
        "SELECT w1, rel, group_name, w2 FROM triple LIMIT 1"
    ).fetchone()
    con.close()
    pkey = f"papel35:{sample['group_name']}:{sample['rel']}:{sample['w1']}"
    papel_v = _fetch_papel_view(pkey)
    rows.append((
        "PAPEL local view",
        pkey,
        "sqlite",
        bool(papel_v and papel_v.get("triples")),
        f"n_triples={len((papel_v or {}).get('triples') or [])}",
    ))

    # OWN-PT
    try:
        code, body = _get(OWNPT_REPO, 8000)
        rows.append((
            "OWN-PT GitHub",
            OWNPT_REPO,
            code,
            code == 200 and "openWordnet-PT" in body,
            "source clone / docs; runtime uses wn pin",
        ))
    except Exception as exc:  # noqa: BLE001
        rows.append(("OWN-PT GitHub", OWNPT_REPO, "ERR", False, str(exc)[:120]))

    # Sample cards from TexturaComposita
    dec_path = ROOT / "classes" / "TexturaComposita" / "decisions.json"
    dec = json.loads(dec_path.read_text(encoding="utf-8"))
    for src in ("pulo", "onto", "papel", "wordnet"):
        sense = next(
            (
                x
                for x in (dec.get("senses") or [])
                if (x.get("source") or "").lower() == src
            ),
            None,
        )
        if not sense:
            rows.append((f"card:{src}", "—", "n/a", False, "no sense in decisions"))
            continue
        links = links_for_sense(sense)
        detail = [
            f"{ln.kind}:{ln.label}:{'ok' if ln.verified else 'bad'}"
            for ln in links
        ]
        rows.append((
            f"card:{src}",
            str(sense.get("key")),
            f"{len(links)} links",
            bool(links) and all(
                ln.verified or ln.kind in ("papel", "ownpt") for ln in links
            ),
            "; ".join(detail),
        ))

    print("RESOURCE LINK AUDIT")
    print("=" * 88)
    n_ok = 0
    for name, target, status, ok, detail in rows:
        mark = "OK" if ok else "FAIL"
        if ok:
            n_ok += 1
        print(f"[{mark}] {name}")
        print(f"      target: {target}")
        print(f"      status: {status}")
        print(f"      detail: {detail}")
    print("=" * 88)
    print(f"{n_ok}/{len(rows)} checks passed")
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
