#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acceptance tests for «Close TexturaUniforme» — Part A (PULO admits the on-axis
core) and Part B (the equivalence table is actually LOADED and made visible).

A1  core_provenance lists each core term with its synset gloss + relation type.
A2  the PULO engine admits an on-axis core term as UF anchored to its ili_offset.
A3  a core term whose ONLY path is an unnamed relation with an off-axis gloss is
    NOT admitted (never admitted on unnamed-relation evidence alone).
B1  builder maps oewn↔pulo by shared PT lemma (covered by test_ili_equivalence too).
B2  LexWarrant prints the ili_equivalence counts at run time; a LOUD warning fires
    when there are 0 usable mappings (never a silent weak(term) fallback).

Fixtures are small and controlled. Two extra checks run against the LIVE
TexturaUniforme artefacts when present (constante admitted UF on-axis).

Run:  python -m unittest discover -s tests   (from the LexWarrant folder)
"""
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_LEX = _HERE.parent
_ROOT = _LEX.parent                       # «Tesaurus e Dicionários»
_PULO_GUI = _ROOT / "PULO Thesaurus GUI"

sys.path.insert(0, str(_LEX))
sys.path.insert(0, str(_PULO_GUI))

import lexwarrant as lw                    # noqa: E402
import pulo_core_provenance as pcp         # noqa: E402
import phase0_pulo as pp                   # noqa: E402
import build_ili_equivalence as bie        # noqa: E402


# ---------------------------------------------------------------------------
# T3 — the builder must use each synset's OWN pt_lemmas (non-lossy), so a lemma
# shared by an adjective AND a noun synset still yields the noun high pair even
# though the result.json `sinalizacao` deduped that lemma onto the adjective.
# ---------------------------------------------------------------------------
class TestPerSynsetHighPair(unittest.TestCase):
    def test_t3_persynset_block_yields_high_pair(self):
        wn = {
            "class_id": "TexturaUniforme",
            # per-synset block keeps «uniforme» on BOTH synsets (non-lossy)
            "synsets": [
                {"name": "oewn-01973553-a", "ili": "i10771", "pos": "a",
                 "pt_lemmas": ["invariável", "uniforme"]},
                {"name": "oewn-04516887-n", "ili": "i60712", "pos": "n",
                 "pt_lemmas": ["farda", "fardamento", "uniforme"]},
            ],
            # sinalizacao (lossy) attributes «uniforme» ONLY to the adjective —
            # the builder must NOT rely on this alone.
            "sinalizacao": {"uniforme": {"display": "uniforme",
                            "reason": "… oewn-01973553-a … ILI i10771",
                            "offsets_ili": ["i10771"]}},
        }
        pulo = {"synsets": [
            {"synset_offset": "por-30-04509592-n", "pos": "n", "synonyms": ["uniforme"],
             "ili": [{"ili_offset": "ili-30-04509592-n"}]},
            # TWO adjective senses share «uniforme» → the adjective i10771 is
            # ambiguous (review); only the NOUN maps unambiguously (high).
            {"synset_offset": "por-30-00744506-a", "pos": "a", "synonyms": ["uniforme"],
             "ili": [{"ili_offset": "ili-30-00744506-a"}]},
            {"synset_offset": "por-30-00909545-a", "pos": "a", "synonyms": ["uniforme"],
             "ili": [{"ili_offset": "ili-30-00909545-a"}]},
        ]}
        doc = bie.build_equivalence(bie.load_wordnet_synsets(wn),
                                    bie.load_pulo_synsets(pulo), "TexturaUniforme")
        self.assertTrue(any(
            r["oewn_ili"] == "i60712" and r["pulo_ili"] == "ili-30-04509592-n"
            and r["evidence"]["shared_lemmas"] == ["uniforme"]
            for r in doc["map"]), f"esperava par high noun; obtive {doc['map']}")
        # the ambiguous adjective «uniforme» stays in review, never auto-picked
        self.assertTrue(any(r["oewn_ili"] == "i10771" for r in doc["review"]))
        # no map row without lemma evidence; no ILI string-derived
        for r in doc["map"]:
            self.assertTrue(r["evidence"]["shared_lemmas"])
            self.assertNotIn("i60712", r["pulo_ili"])


# ---------------------------------------------------------------------------
# A1 — core provenance diagnostic
# ---------------------------------------------------------------------------
class TestCoreProvenance(unittest.TestCase):
    def _export(self):
        return {"synsets": [{
            "synset_offset": "por-30-00909545-a", "pos": "a",
            "synonyms": ["uniforme", "regular", "igual"],
            "gloss": "sendo regular e sem variação; estar no mesmo plano\n",
            "ili": [{"ili_offset": "ili-30-00909545-a"}],
            "relations": [{"relation": "see also (unnamed)", "targets": [{
                "synset_offset": "por-30-02301560-a",
                "words": "regular, constante, estável",
                "gloss": "não sujeitos a mudança ou variação, especialmente no comportamento\n",
            }]}],
        }]}

    def test_a1_lists_core_terms_with_gloss_and_relation(self):
        axis = ["variação", "mudança", "mesmo", "não"]
        doc = pcp.build_core_provenance(self._export(), axis,
                                        ["constante", "uniforme", "imutável"])
        # uniforme reached as headword synonym on an on-axis synset
        uni = doc["hits"]["uniforme"]
        self.assertTrue(any("sinónimo" in r["relation"] for r in uni))
        self.assertTrue(doc["summary"]["uniforme"]["any_on_axis"])
        # constante reached as target of an (unnamed) relation, gloss on-axis
        con = doc["hits"]["constante"]
        self.assertTrue(con, "constante deve ter proveniência")
        self.assertTrue(all(r["gloss"] for r in con), "cada linha tem glosa")
        self.assertTrue(any("alvo de" in r["relation"] for r in con))
        self.assertTrue(doc["summary"]["constante"]["any_on_axis"])
        # imutável is absent from the export → reported as such
        self.assertFalse(doc["summary"]["imutável"]["present"])
        md = pcp.render_md(doc, "K")
        for t in ("constante", "uniforme", "imutável"):
            self.assertIn(t, md)


# ---------------------------------------------------------------------------
# A2 / A3 — PULO admits on-axis core, never on unnamed-relation-only evidence
# ---------------------------------------------------------------------------
class TestPuloAdmitsCore(unittest.TestCase):
    def _spec(self, folder, whitelist, adjudication):
        spec = {
            "class_id": "K", "pref_label": "K",
            "axis": "invariância",
            "axis_terms": ["variação", "mudança", "mesmo", "não"],
            "stage1_whitelist": whitelist,
            "adjudication": adjudication,
        }
        p = folder / "spec.json"
        p.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
        return pp.ClassSpec.load(p)

    def _uf(self, test="t"):
        return {"status": "UF", "test": test, "guarantee": ["lexical"]}

    def test_a2_admits_on_axis_core_as_uf_anchored_to_ili(self):
        # A whitelisted on-axis synset whose members include «constante».
        export = {"synsets": [{
            "synset_offset": "por-30-02301560-a", "pos": "a",
            "synonyms": ["regular", "constante", "estável"],
            "gloss": "não sujeitos a mudança ou variação\n",
            "ili": [{"ili_offset": "ili-30-02301560-a"}], "relations": [],
        }]}
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(Path(d), [{
                "ili_offset": "ili-30-02301560-a",
                "glosa": "não sujeitos a mudança ou variação\n",
                "decision": "UF", "members": ["regular", "constante", "estável"]}],
                {"constante": self._uf()})
            result = pp.PuloPhase0Engine(spec, export).run()
            prov = {p["termo"]: p for p in result["provenance"]}
            self.assertIn("constante", prov)
            self.assertEqual(prov["constante"]["estatuto"], "UF")
            self.assertIn("ili-30-02301560-a", prov["constante"]["offsets_ili"])
            # A3 — nothing admitted was routed via an unnamed relation
            for p in result["provenance"]:
                self.assertNotIn("não-nomeada", (p.get("via") or ""))

    def test_a3_core_via_unnamed_offaxis_relation_is_not_admitted(self):
        # «imutável» reached ONLY as target of an unnamed relation whose gloss is
        # OFF-axis → must stay out of the admitted set (sinalização, not UF).
        export = {"synsets": [{
            "synset_offset": "por-30-00744506-a", "pos": "a",
            "synonyms": ["uniforme"], "gloss": "não diferenciado\n",
            "ili": [{"ili_offset": "ili-30-00744506-a"}],
            "relations": [{"relation": "relation #17", "targets": [{
                "synset_offset": "por-30-09999999-a",
                "words": "imutável",
                "gloss": "uma peça de roupa distinta usada por um grupo\n"}]}],
        }]}
        with tempfile.TemporaryDirectory() as d:
            spec = self._spec(Path(d), [{
                "ili_offset": "ili-30-00744506-a", "glosa": "não diferenciado\n",
                "decision": "UF", "members": ["uniforme"]}],
                {"uniforme": self._uf(), "imutavel": self._uf()})
            result = pp.PuloPhase0Engine(spec, export).run()
            admitted = {p["termo"] for p in result["provenance"]}
            self.assertNotIn("imutável", admitted)
            self.assertIn("imutavel", result["sinalizacao"])


# ---------------------------------------------------------------------------
# B2 — the equivalence-table load is visible (counts printed) / LOUD if empty
# ---------------------------------------------------------------------------
class TestEquivLoadVisible(unittest.TestCase):
    def _capture(self, equiv, map_path):
        buf = io.StringIO()
        with redirect_stdout(buf):
            lw._report_equiv_load(equiv, map_path)
        return buf.getvalue()

    def test_b2_prints_counts_when_loaded(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ili_equivalence.json"
            p.write_text(json.dumps({"class": "K", "map": [
                {"oewn_ili": "i1", "pulo_ili": "ili-30-00000001-a",
                 "evidence": {"shared_lemmas": ["x"], "pos": "a"}, "confidence": "high"}],
                "review": [1, 2], "unmatched": [1]}), encoding="utf-8")
            equiv = lw.EquivMap.load(p)
            out = self._capture(equiv, p)
            self.assertIn("ili_equivalence:", out)
            self.assertIn("1 mapped", out)
            self.assertIn("2 review", out)
            self.assertNotIn("NÃO CARREGADA", out)

    def test_b2_loud_warning_when_zero_mapped(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "ili_equivalence.json"
            p.write_text(json.dumps({"class": "K", "map": [],
                                     "review": [1], "unmatched": []}), encoding="utf-8")
            equiv = lw.EquivMap.load(p)
            out = self._capture(equiv, p)
            self.assertIn("TABELA DE EQUIVALÊNCIA NÃO CARREGADA", out)

    def test_b2_loud_warning_when_absent(self):
        out = self._capture(None, None)
        self.assertIn("TABELA DE EQUIVALÊNCIA NÃO CARREGADA", out)


# ---------------------------------------------------------------------------
# Live artefacts (best-effort): constante admitted UF, on-axis, in the real PULO run
# ---------------------------------------------------------------------------
_LIVE = (_ROOT / "UNIFORM" / "Uniform_léxicos_tesauros" / "PULO"
         / "TexturaUniforme.result.json")


class TestLivePuloArtifact(unittest.TestCase):
    @unittest.skipUnless(_LIVE.exists(), "PULO result.json ao vivo ausente")
    def test_live_constante_uf_on_axis(self):
        doc = json.loads(_LIVE.read_text(encoding="utf-8"))
        prov = {p["termo"]: p for p in doc["provenance"]}
        self.assertIn("constante", prov)
        self.assertEqual(prov["constante"]["estatuto"], "UF")
        self.assertTrue(any(o.startswith("ili-30-")
                            for o in prov["constante"]["offsets_ili"]))
        for p in doc["provenance"]:
            self.assertNotIn("não-nomeada", (p.get("via") or ""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
