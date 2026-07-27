#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acceptance tests A1–A8 for the ILI equivalence table + LexWarrant wiring.

These use small controlled fixtures (NOT the live TexturaUniforme data) so they
pin the MECHANISM: lemma-evidence mapping, ILI-join via the declared table,
pendente suppression and the «convergência plena requires ILI» rule.

Run:  python -m unittest discover -s tests    (from the LexWarrant folder)
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import build_ili_equivalence as bie   # noqa: E402
import lexwarrant as lw                # noqa: E402


def _write(folder: Path, name: str, obj: dict) -> Path:
    p = folder / name
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def _source(class_id: str, provenance=None, pending=None, sinalizacao=None) -> dict:
    return {
        "class_id": class_id,
        "provenance": provenance or [],
        "sinalizacao": sinalizacao or {},
        "stage5": {"pending": pending or {}},
    }


class TestBuilder(unittest.TestCase):
    def test_a1_high_confidence_single_match(self):
        wn = {"synsets": [{"ili": "i10771", "pos": "a",
                           "pt_lemmas": ["uniforme", "invariável"]}]}
        pulo = {"synsets": [{"synset_offset": "por-30-00744506-a", "pos": "a",
                             "synonyms": ["uniforme"],
                             "ili": [{"ili_offset": "ili-30-00744506-a"}]}]}
        doc = bie.build_equivalence(bie.load_wordnet_synsets(wn),
                                    bie.load_pulo_synsets(pulo), "TexturaUniforme")
        self.assertEqual(len(doc["map"]), 1)
        row = doc["map"][0]
        self.assertEqual(row["oewn_ili"], "i10771")
        self.assertEqual(row["pulo_ili"], "ili-30-00744506-a")
        self.assertEqual(row["evidence"]["shared_lemmas"], ["uniforme"])
        self.assertEqual(row["confidence"], "high")

    def test_a2_no_row_without_lemma_evidence_and_no_string_derivation(self):
        wn = {"synsets": [{"ili": "i10771", "pos": "a", "pt_lemmas": ["uniforme"]}]}
        pulo = {"synsets": [{"synset_offset": "por-30-00744506-a", "pos": "a",
                             "synonyms": ["uniforme"],
                             "ili": [{"ili_offset": "ili-30-00744506-a"}]}]}
        doc = bie.build_equivalence(bie.load_wordnet_synsets(wn),
                                    bie.load_pulo_synsets(pulo))
        for row in doc["map"] + doc["review"]:
            self.assertTrue(row["evidence"]["shared_lemmas"],
                            "toda a linha tem de carregar evidência de lema partilhado")
            # ILIs are taken verbatim from the inputs, never edited from each other
            self.assertEqual(row["oewn_ili"], "i10771")
            self.assertTrue(row["pulo_ili"].startswith("ili-30-"))
            self.assertNotIn("i10771", row["pulo_ili"])

    def test_a3_multi_match_review_and_no_match_unmatched(self):
        wn = {"synsets": [
            {"ili": "i10771", "pos": "a", "pt_lemmas": ["uniforme"]},        # 2 PULO senses
            {"ili": "i99999", "pos": "a", "pt_lemmas": ["inexistente"]},     # 0 PULO senses
        ]}
        pulo = {"synsets": [
            {"synset_offset": "por-30-00744506-a", "pos": "a", "synonyms": ["uniforme"],
             "ili": [{"ili_offset": "ili-30-00744506-a"}]},
            {"synset_offset": "por-30-00909545-a", "pos": "a", "synonyms": ["uniforme", "igual"],
             "ili": [{"ili_offset": "ili-30-00909545-a"}]},
        ]}
        doc = bie.build_equivalence(bie.load_wordnet_synsets(wn),
                                    bie.load_pulo_synsets(pulo))
        self.assertEqual(doc["map"], [])                       # ambiguous → not mapped
        self.assertEqual(len(doc["review"]), 2)                # both senses surfaced
        self.assertTrue(all(r["confidence"] == "review" for r in doc["review"]))
        self.assertEqual([u["oewn_ili"] for u in doc["unmatched"]], ["i99999"])


class TestWiring(unittest.TestCase):
    def _run(self, folder, onto, pulo, wn=None, with_map=True,
             weak_term_mode="gloss_gated"):
        specs = [("ONTO", _write(folder, "ONTO.result.json", onto)),
                 ("PULO", _write(folder, "PULO.result.json", pulo))]
        if wn is not None:
            specs.append(("WordNet", _write(folder, "WordNet.result.json", wn)))
        map_path = None
        if with_map:
            map_doc = {"class": "K", "map": [
                {"oewn_ili": "i111", "pulo_ili": "ili-30-00000001-a",
                 "evidence": {"shared_lemmas": ["constante"], "pos": "a"},
                 "confidence": "high"},
                {"oewn_ili": "i222", "pulo_ili": "ili-30-00000002-a",
                 "evidence": {"shared_lemmas": ["invariável"], "pos": "a"},
                 "confidence": "high"},
            ], "review": [], "unmatched": []}
            map_path = _write(folder, "ili_equivalence.json", map_doc)
        return lw.run_report(
            specs, folder, policy="conservative", map_path=map_path,
            weak_term_mode=weak_term_mode,
        )

    def _concept(self, doc, term):
        for c in doc["concepts"]:
            if c["term"] == term:
                return c
        return None

    def test_a4_table_enables_ili_join_full_convergence(self):
        # ONTO carries OEWN ILIs, PULO carries ili-30 ILIs; only the table links them.
        onto = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["i111"]},
            {"termo": "invariável", "estatuto": "UF", "offsets_ili": ["i222"]},
        ])
        pulo = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["ili-30-00000001-a"]},
            {"termo": "invariável", "estatuto": "UF", "offsets_ili": ["ili-30-00000002-a"]},
        ])
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(Path(d), onto, pulo, with_map=True)
            for term in ("constante", "invariável"):
                c = self._concept(doc, term)
                self.assertIsNotNone(c, f"{term} em falta")
                self.assertEqual(c["join"], "ili", f"{term} devia juntar por ILI")
                self.assertEqual(c["veredicto"], "convergência plena")
                self.assertNotEqual(c["veredicto"], "fonte única")

    def test_a4b_without_map_no_ili_join(self):
        onto = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["i111"]}])
        pulo = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["ili-30-00000001-a"]}])
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(Path(d), onto, pulo, with_map=False)
            c = self._concept(doc, "constante")
            self.assertNotEqual(c["join"], "ili")
            self.assertNotEqual(c["veredicto"], "convergência plena")

    def test_a5_unmapped_flag(self):
        onto = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["i111"]},
            {"termo": "homogeneo", "estatuto": "UF", "offsets_ili": ["clip21:999"]},
        ])
        pulo = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["ili-30-00000001-a"]},
        ])
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(Path(d), onto, pulo, with_map=True)
            covered = self._concept(doc, "constante")
            self.assertFalse(covered["unmapped_flag"],
                             "conceito coberto pela tabela não deve ser flagueado")
            genuine = self._concept(doc, "homogeneo")
            self.assertTrue(genuine["unmapped_flag"],
                            "offset interno genuinamente não-mapeado deve ser flagueado")

    def test_a6_pendente_suppression_counted_not_listed(self):
        onto = _source("K",
                       provenance=[{"termo": "constante", "estatuto": "UF",
                                    "offsets_ili": ["i111"]}],
                       pending={"carteiro": {"display": "carteiro"},
                                "url": {"display": "url"},
                                "siria": {"display": "síria"}})
        pulo = _source("K", provenance=[
            {"termo": "constante", "estatuto": "UF", "offsets_ili": ["ili-30-00000001-a"]}])
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(Path(d), onto, pulo, with_map=True)
            terms = {c["term"] for c in doc["concepts"]}
            self.assertNotIn("carteiro", terms)
            self.assertNotIn("url", terms)
            self.assertGreaterEqual(doc["summary"]["descartados_pendentes"], 3)
            for c in doc["concepts"]:
                present = [v for v in c["sources"].values() if v != lw.ABSENT]
                self.assertTrue(present, "nenhuma linha pode ter todas as fontes «—»")

    def test_a8_plena_requires_ili_defensavel_excludes_weak(self):
        # Same status in both sources but NO shared/linked ILI.
        # Default gloss_gated with empty glosses → refuse weak join (safer).
        onto = _source("K", provenance=[
            {"termo": "homogeneo", "estatuto": "RT", "offsets_ili": ["clip21:1"]}])
        pulo = _source("K", provenance=[
            {"termo": "homogeneo", "estatuto": "RT", "offsets_ili": ["ili-30-01199751-a"]}])
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(Path(d), onto, pulo, with_map=True)
            c = self._concept(doc, "homogeneo")
            self.assertIn(c["join"], ("single", "weak(term)"))
            self.assertNotEqual(c["veredicto"], "convergência plena")
            self.assertNotIn("homogeneo", doc["summary"]["convergencia_plena"])
        # legacy mode still forms weak(term) / convergência (termo)
        with tempfile.TemporaryDirectory() as d:
            doc = self._run(
                Path(d), onto, pulo, with_map=True, weak_term_mode="legacy",
            )
            c = self._concept(doc, "homogeneo")
            self.assertEqual(c["join"], "weak(term)")
            self.assertEqual(c["veredicto"], "convergência (termo)")
            self.assertNotIn("homogeneo", doc["summary"]["convergencia_plena"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
