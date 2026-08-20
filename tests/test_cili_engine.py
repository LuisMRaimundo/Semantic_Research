"""R9 — CILI lexicographical engine (fixture corpus; no real dumps in CI)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engines.CILI.cili_engine import (  # noqa: E402
    CiliEngine,
    SCHEMA_VERSION,
    canonical_ili,
    is_ili_id,
    pos_norm,
)

# ---------------------------------------------------------------------------
# miniature corpus
# ---------------------------------------------------------------------------
_ILI_TTL = """\
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix ili: <https://globalwordnet.github.io/cili/ontology.xml#> .
@prefix pwn30: <http://wordnet-rdf.princeton.edu/wn30/> .

<i1>	a	<Concept> ;
	skos:definition	"having the necessary means or skill"@en ;
	dc:source	pwn30:00001740-a .

<i10>	a	<Concept> ;
	skos:definition	"coming into existence"@en ;
	dc:source	pwn30:00003553-s .

<i100>	a	<Concept> ;
	skos:definition	"a harmonious state of things"@en ;
	dc:source	pwn30:13964868-n .

<i101>	a	<Concept> ;
	skos:definition	"the structure of music with respect to the composition and progression of chords"@en ;
	dc:source	pwn30:07020895-n .

<i200>	a	<Concept> ;
	skos:definition	"the feel of a surface or a fabric"@en ;
	dc:source	pwn30:04930254-n .

<i201>	a	<Concept> ;
	skos:definition	"the characteristic appearance of a surface"@en ;
	dc:source	pwn30:04722616-n .
"""

_MAP_WN31 = """\
ili:i1 owl:sameAs pwn31:300001740-a . # able
ili:i10 owl:sameAs pwn31:300003552-s . # emergent, emerging
ili:i100 owl:sameAs pwn31:113964868-n . # harmony, concord, concordance
ili:i101 owl:sameAs pwn31:107020895-n . # harmony
ili:i200 owl:sameAs pwn31:104930254-n . # texture
ili:i201 owl:sameAs pwn31:104722616-n . # texture
"""

_PWN30 = """\
i1	00001740-a
i10	00003553-s
i100	13964868-n
i101	07020895-n
i200	04930254-n
i201	04722616-n
"""

_OMW_POR = """\
# Portuguese miniature
00001740-a	por:lemma	capaz
13964868-n	por:lemma	harmonia
07020895-n	por:lemma	harmonia
04930254-n	por:lemma	textura
04722616-n	por:lemma	textura
"""


def _write_corpus(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "ili.ttl").write_text(_ILI_TTL, encoding="utf-8")
    (root / "ili-map-wn31.ttl").write_text(_MAP_WN31, encoding="utf-8")
    (root / "ili-map-pwn30.tab").write_text(_PWN30, encoding="utf-8")
    omw = root / "omw"
    omw.mkdir()
    (omw / "wn-data-por.tab").write_text(_OMW_POR, encoding="utf-8")
    return root


@pytest.fixture
def engine(tmp_path: Path) -> CiliEngine:
    corpus = _write_corpus(tmp_path / "cili")
    live_map = tmp_path / "live" / "ili-map-pwn30.tab"
    live_map.parent.mkdir()
    live_map.write_text(_PWN30, encoding="utf-8")
    idx = tmp_path / "index" / "cili.sqlite"
    eng = CiliEngine(
        root=corpus,
        omw_dir=corpus,
        pwn30_map=live_map,
        dump_pwn30_map=corpus / "ili-map-pwn30.tab",
        index_path=idx,
    )
    eng.build_index(force=True, verbose=False)
    return eng


def test_index_build_and_freshness(engine: CiliEngine):
    assert engine.index_path.exists()
    assert engine.index_is_fresh()
    stats = engine.stats()
    assert stats["concepts"] == 6
    assert stats["meta"]["schema_version"] == SCHEMA_VERSION
    # second build without force is a no-op
    info = engine.build_index(force=False, verbose=False)
    assert info["rebuilt"] is False


def test_entry_equivalents_and_gaps(engine: CiliEngine):
    e = engine.entry("harmonia")
    assert e["count"] == 2
    assert "noun" in e["groups"]
    assert len(e["groups"]["noun"]) == 2
    en_eq = {r["lemma"]: r["shared_senses"] for r in e["equivalents"].get("en", [])}
    assert "harmony" in en_eq
    assert en_eq["harmony"] == 2
    # i10 (satellite) has no Portuguese label → gap
    gaps_por = e["gaps"].get("por") or []
    assert gaps_por == []  # both harmonia senses have por
    # able/emergent have no por on i10; check gap on emerging
    em = engine.entry("emerging")
    assert "por" in em["gaps"]
    assert "i10" in em["gaps"]["por"]


def test_satellite_pos_norm_join(engine: CiliEngine):
    c = engine.concept("i10")
    assert c is not None
    assert c["pos"] == "s"
    assert c["pos_norm"] == "a"
    assert c["pos_name"] == "adjective (satellite)"
    assert pos_norm("s") == "a"
    e = engine.entry("emerging")
    assert "adjective" in e["groups"]
    sense = e["groups"]["adjective"][0]
    assert sense["ili"] == "i10"
    assert sense["pos"] == "s"
    assert sense["pos_norm"] == "a"
    assert sense["pos_name"] == "adjective (satellite)"
    # search --pos a includes satellites via pos_norm
    hits = engine.search("existence", mode="definition", pos="a")
    ilis = {r["ili"] for r in hits["results"]}
    assert "i10" in ilis


def test_identity_helpers_none_on_unknown(engine: CiliEngine):
    assert engine.ili_for_pwn30("00001740-a") == "i1"
    assert engine.ili_for_pwn30("pwn30-00001740-a") == "i1"
    assert engine.ili_for_pwn30("00001740-s") is None  # exact: no a↔s flip
    assert engine.ili_for_pwn30("99999999-n") is None
    assert engine.pwn30_for_ili("i1") == "00001740-a"
    assert engine.pwn30_for_ili("i999999") is None
    assert engine.pwn30_for_ili("not-an-ili") is None
    assert engine.concept("i999999") is None
    assert canonical_ili("00001740-a") is None
    assert canonical_ili("i1") == "i1"
    assert not is_ili_id("pwn30-00001740-a")


def test_never_fabricate_ili_from_offset():
    text = Path(ROOT / "engines" / "CILI" / "cili_engine.py").read_text(encoding="utf-8")
    # No code path constructs an i-id from an offset (f"i{…}" / "i" + number).
    assert not re.search(r"""f["']i\{""", text)
    assert not re.search(r"""["']i["']\s*\+""", text)
    assert canonical_ili("04930254-n") is None
    assert canonical_ili("pwn30-04930254-n") is None


def _real_corpus_present() -> bool:
    try:
        eng = CiliEngine.from_config()
        return eng.ili_ttl.exists()
    except Exception:  # noqa: BLE001
        return False


def test_export_flag_off_leaves_md_unchanged(engine: CiliEngine, tmp_path, monkeypatch):
    from semantic.cili_export import render_cili_md
    from semantic.termos_pesquisa import render_termos_md

    base = {
        "class_id": "Demo",
        "pref_label": "demo",
        "axis": "x",
        "search_lang": "en",
        "label_lang": "pt",
        "A_polo_alvo": [],
        "B_polo_contrastante": [],
        "C_conjunto_controlo": [],
        "C_termos": [],
        "D_descritores_adjacentes": [],
        "E_fronteiras_dominio": [],
        "F_vocabulario_pt": [],
        "a_resolver": [],
        "termos_manuais_presentes": True,
    }
    off = render_termos_md(base)
    on = render_termos_md({
        **base,
        "cili_blocks": [{
            "ili": "i1",
            "rdf_uri": "http://ili.globalwordnet.org/ili/i1",
            "page_uri": "https://globalwordnet.github.io/cili/i1",
            "definition": "able",
            "pos": "a",
            "pos_norm": "a",
            "pos_name": "adjective",
            "equivalents": {"en": ["able"], "por": ["capaz"]},
        }],
    })
    assert off == render_termos_md({**base, "cili_blocks": []})
    assert "## CILI" not in off
    assert "## CILI" in on
    assert "i1" in on
    assert "`http://ili.globalwordnet.org/ili/i1`" in on
    assert "](https://globalwordnet.github.io/cili/i1)" in on
    assert render_cili_md([]) == ""


def test_termos_html_stays_local_no_remote_cili_href():
    from semantic.cili_export import html_ident
    from semantic.termos_pesquisa import render_termos_html

    assert html_ident("i1") == "<code>i1</code>"
    html = render_termos_html({
        "class_id": "Demo",
        "pref_label": "demo",
        "axis": "x",
        "search_lang": "en",
        "label_lang": "pt",
        "ancora_ili": ["i1"],
        "A_polo_alvo": [{"forma": "able", "wildcard": "abl*", "ili": "i1"}],
        "B_polo_contrastante": [],
        "C_conjunto_controlo": [],
        "C_termos": [],
        "D_descritores_adjacentes": [],
        "E_fronteiras_dominio": [],
        "F_vocabulario_pt": [],
        "a_resolver": [],
        "termos_manuais_presentes": True,
    })
    assert "i1" in html
    assert "href=\"http" not in html
    assert "ili.globalwordnet.org" not in html
    assert "globalwordnet.github.io" not in html


@pytest.mark.local_corpus
@pytest.mark.skipif(not _real_corpus_present(), reason="CILI dump not present")
def test_local_corpus_smoke_queries():
    eng = CiliEngine.from_config()
    if not eng.index_is_fresh():
        eng.build_index(force=False, verbose=False)
    e = eng.entry("harmonia")
    assert e["count"] >= 1
    en = e["equivalents"].get("en") or []
    assert any(r["lemma"].lower() == "harmony" or "harmon" in r["lemma"].lower() for r in en)
    t = eng.entry("textura")
    assert t["count"] >= 1
    en_t = {r["lemma"].lower() for r in (t["equivalents"].get("en") or [])}
    assert "texture" in en_t
    c = eng.concept("i1")
    assert c and c["ili"] == "i1"
