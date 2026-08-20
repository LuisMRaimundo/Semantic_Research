#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Local-first audit: link targets vs data/docs already in Semantic_Research."""

from __future__ import annotations

import json
import sqlite3
import sys
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
    _fetch_oewn_view,
    _fetch_onto_view,
    _fetch_papel_view,
    _fetch_pulo_view,
    links_for_sense,
    verify_oewn_id,
    verify_onto_key,
    verify_papel_key,
    verify_pulo_offset,
)


def main() -> int:
    rows: list[tuple[str, str, bool, str]] = []

    # --- CILI (local map + documented URL patterns) ---
    page = ids.cili_page_url("i1")
    uri = ids.cili_uri("i1")
    map30 = ROOT / "engines" / "LexWarrant" / "data" / "cili" / "ili-map-pwn30.tab"
    hit = ""
    with map30.open(encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("i1\t"):
                hit = line.strip()
                break
    rows.append((
        "CILI page pattern",
        page,
        page == "https://globalwordnet.github.io/cili/i1",
        "HEADER.txt + identifiers.py",
    ))
    rows.append((
        "CILI URI pattern",
        uri,
        uri == "http://ili.globalwordnet.org/ili/i1",
        "GWA / identifiers.py",
    ))
    rows.append((
        "CILI local map i1",
        hit,
        hit == "i1\t00001740-a",
        str(map30.relative_to(ROOT)),
    ))

    # --- OEWN (local wn pin; URL form) ---
    oid = "oewn-00001740-a"
    from semantic import settings as _cfg
    _pin = str(_cfg.load_config().get("oewn") or "oewn:2025")
    ss = wn.Wordnet(_pin).synset(oid)
    lemmas = list(ss.lemmas()) if ss else []
    definition = (ss.definition() or "") if ss else ""
    view = _fetch_oewn_view(oid)
    bare = oid.removeprefix("oewn-")
    oewn_url = OEWN_PAGE_BASE + bare
    rows.append((
        "OEWN local synset",
        oid,
        bool(ss) and "able" in lemmas and "necessary means" in definition.lower(),
        f"lemmas={lemmas}; def~{definition[:60]}",
    ))
    rows.append((
        "OEWN local view vs wn",
        oid,
        bool(view) and set(view.get("members") or []) == set(lemmas),
        "resource_links._fetch_oewn_view",
    ))
    rows.append((
        "OEWN URL form",
        oewn_url,
        oewn_url == f"https://en-word.net/synset/{bare}",
        "en-word.net/synset/<offset-pos> (matches local wn id)",
    ))
    rows.append((
        "OEWN verify helper",
        oid,
        verify_oewn_id(oid),
        f"wn pin {_pin}",
    ))

    # --- PULO (local sqlite) ---
    off = "por-30-00001740-a"
    pdb = ROOT / "engines" / "PULO Thesaurus GUI" / "pulo.sqlite"
    con = sqlite3.connect(str(pdb))
    gloss = con.execute("SELECT gloss FROM synset WHERE offset=?", (off,)).fetchone()
    variants = [
        r[0]
        for r in con.execute(
            "SELECT word FROM variant WHERE offset=? ORDER BY sense, word", (off,)
        )
    ]
    ili = con.execute(
        "SELECT iliOffset, iliWnId, csco FROM to_ili WHERE offset=?", (off,)
    ).fetchone()
    con.close()
    pv = _fetch_pulo_view(off)
    rows.append((
        "PULO local view = sqlite",
        off,
        bool(pv)
        and gloss is not None
        and pv["gloss"] == gloss[0]
        and set(pv["members"]) == set(variants),
        f"ili={ili}; members={variants[:5]}",
    ))
    rows.append((
        "PULO verify helper",
        off,
        verify_pulo_offset(off),
        str(pdb.relative_to(ROOT)),
    ))

    # --- Onto (sqlite + local RDF dump / LEIAME) ---
    key = "ontopt06:10"
    odb = ROOT / "engines" / "ONTO" / "ontopt.sqlite"
    con = sqlite3.connect(str(odb))
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
    ov = _fetch_onto_view(key)
    rows.append((
        "Onto local view = sqlite",
        key,
        bool(ov)
        and row is not None
        and ov["gloss"] == (row[1] or "")
        and set(ov["members"]) == set(mems),
        f"gloss~{(row[1] or '')[:50] if row else ''}; n={len(mems)}",
    ))
    rdf_uri = ONTO_RDF_BASE + "10"
    rdf_path = ROOT / "OntoPTv0.6_rdf" / "OntoPTv0.6.rdfs"
    needle = 'rdf:about="http://ontopt.dei.uc.pt/OntoPT.owl#10"'
    found = False
    with rdf_path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if needle in line:
                found = True
                break
    leiame = (ROOT / "OntoPTv0.6_rdf" / "LEIAME.txt").read_text(
        encoding="utf-8", errors="ignore"
    )
    rows.append((
        "Onto RDF id in local dump",
        rdf_uri,
        found and ONTO_RDF_BASE == "http://ontopt.dei.uc.pt/OntoPT.owl#",
        "OntoPTv0.6.rdfs + LEIAME (WN RDF Basic style)",
    ))
    rows.append((
        "Onto LEIAME documents RDF model",
        "OntoPTv0.6_rdf/LEIAME.txt",
        "modelo RDF" in leiame and "WordNet RDF" in leiame,
        "local dump docs (HTTP fragment not required)",
    ))
    rows.append((
        "Onto verify helper",
        key,
        verify_onto_key(key),
        str(odb.relative_to(ROOT)),
    ))

    # --- PAPEL (local sqlite + documented home) ---
    pdb_papel = ROOT / "data" / "papel.sqlite"
    con = sqlite3.connect(str(pdb_papel))
    n = con.execute("SELECT COUNT(*) FROM triple").fetchone()[0]
    sample = con.execute(
        "SELECT w1, rel, group_name, w2 FROM triple LIMIT 1"
    ).fetchone()
    con.close()
    pkey = f"papel35:{sample[2]}:{sample[1]}:{sample[0]}"
    papel_v = _fetch_papel_view(pkey)
    rows.append((
        "PAPEL home URL (docs)",
        PAPEL_HOME,
        PAPEL_HOME == "https://www.linguateca.pt/PAPEL/",
        "LEIAME/Onto cites linguateca.pt/PAPEL; no per-triple public URL",
    ))
    rows.append((
        "PAPEL local view = sqlite",
        pkey,
        bool(papel_v and papel_v.get("triples")) and n > 0,
        f"n_triples_db={n}",
    ))
    rows.append((
        "PAPEL verify helper",
        pkey,
        verify_papel_key(pkey),
        str(pdb_papel.relative_to(ROOT)),
    ))

    # --- OWN-PT (local clone + GitHub URL) ---
    clone = ROOT / "openWordnet-PT"
    readme = clone / "README.md"
    readme_txt = readme.read_text(encoding="utf-8", errors="ignore") if readme.exists() else ""
    rows.append((
        "OWN-PT local clone",
        str(clone),
        clone.is_dir() and readme.exists(),
        "openWordnet-PT/ present",
    ))
    # GUI points at own-pt org; LEIAME historically cites arademaker/wordnet-br
    rows.append((
        "OWN-PT GitHub URL",
        OWNPT_REPO,
        OWNPT_REPO in ("https://github.com/own-pt/openWordnet-PT",
                       "https://github.com/arademaker/wordnet-br"),
        "runtime attestation uses wn pin own-pt:1.0.0; clone is local source",
    ))
    rows.append((
        "OWN-PT README present",
        "openWordnet-PT/README.md",
        bool(readme_txt) and ("WordNet" in readme_txt or "wordnet" in readme_txt.lower()),
        readme_txt.splitlines()[0][:80] if readme_txt else "missing",
    ))

    # --- Sense cards from TexturaComposita ---
    dec = json.loads(
        (ROOT / "classes" / "TexturaComposita" / "decisions.json").read_text(
            encoding="utf-8"
        )
    )
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
            rows.append((f"card:{src}", "—", False, "no sense in decisions"))
            continue
        links = links_for_sense(sense)
        local_ok = all(
            (ln.kind != "local") or ln.verified for ln in links
        )
        detail = "; ".join(
            f"{ln.kind}:{ln.label}:{'ok' if ln.verified else 'bad'}->{ln.url[:60]}"
            for ln in links
        )
        rows.append((
            f"card:{src}",
            str(sense.get("key")),
            bool(links) and local_ok,
            detail,
        ))

    print("RESOURCE LINK AUDIT (local-first)")
    print("=" * 88)
    n_ok = 0
    for name, target, ok, detail in rows:
        mark = "OK" if ok else "FAIL"
        if ok:
            n_ok += 1
        print(f"[{mark}] {name}")
        print(f"      target: {target}")
        print(f"      detail: {detail}")
    print("=" * 88)
    print(f"{n_ok}/{len(rows)} checks passed")
    return 0 if n_ok == len(rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
