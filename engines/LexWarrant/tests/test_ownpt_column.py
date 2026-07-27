#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OWN-PT as declared column — convergência (sentido) + recursos_derivados:PWN."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_ili_equivalence as bie  # type: ignore
import lexwarrant as lw  # type: ignore


class OwnPtColumnTests(unittest.TestCase):
    def test_source_columns_include_ownpt(self):
        self.assertEqual(
            lw.SOURCE_COLUMNS, ["ONTO", "PULO", "OWN-PT", "WordNet"]
        )
        self.assertNotIn(lw.ATESTATO, lw.ADMIT_STATUSES)

    def test_infer_label_ownpt_before_wordnet(self):
        p = Path("TexturaUniforme.OWN-PT.result.json")
        self.assertEqual(lw.infer_label(p), "OWN-PT")

    def test_convergencia_sentido_pulo_ownpt_ili(self):
        """PULO UF + OWN-PT atestado, shared ILI → convergência (sentido) + PWN."""
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            pulo = {
                "class_id": "Demo",
                "provenance": [{
                    "termo": "invariável",
                    "estatuto": "UF",
                    "offsets_ili": ["ili-30-01966488-a"],
                    "recursos_atestacao": ["seed"],
                    "teste_decisivo": "t1",
                    "garantia": ["lexical"],
                }],
                "sinalizacao": {},
            }
            own = {
                "class_id": "Demo",
                "lexicon": "own-pt:1.0.0",
                "provenance": [],
                "atestacao": {
                    "invariavel": {
                        "display": "invariável",
                        "reason": "atestado OWN-PT [own-pt:1.0.0] via ILI i10771",
                        "offsets_ili": ["i10771"],
                        "lexicon": "own-pt:1.0.0",
                    }
                },
            }
            (td / "Demo.PULO.result.json").write_text(
                json.dumps(pulo), encoding="utf-8"
            )
            (td / "Demo.OWN-PT.result.json").write_text(
                json.dumps(own), encoding="utf-8"
            )
            # equivalence table: unify namespaces
            eq = lw.EquivMap()
            eq.n_map = 1
            eq.pairs = [("oewn-ili:i10771", "ili-30-01966488-a")]
            # link via parent union — use load from mini file
            map_doc = {
                "map": [{
                    "oewn_ili": "i10771",
                    "pulo_ili": "ili-30-01966488-a",
                    "confidence": "high",
                    "source": "human-adjudicated",
                }],
                "review": [],
                "unmatched": [],
                "coverage": {"map": 1, "review": 0, "unmatched": 0},
            }
            map_path = td / "ili_equivalence.json"
            map_path.write_text(json.dumps(map_doc), encoding="utf-8")

            doc = lw.run_report(
                [
                    ("PULO", td / "Demo.PULO.result.json"),
                    ("OWN-PT", td / "Demo.OWN-PT.result.json"),
                ],
                td / "out",
                policy="conservative",
                map_path=map_path,
            )
            concepts = {c["term"]: c for c in doc["concepts"]}
            self.assertIn("invariável", concepts)
            row = concepts["invariável"]
            self.assertEqual(row["veredicto"], "convergência (sentido)")
            self.assertEqual(row["join"], "ili")
            self.assertEqual(row["sources"].get("OWN-PT"), "atestado")
            self.assertEqual(row["sources"].get("PULO"), "UF")
            self.assertEqual(row.get("recursos_derivados"), "PWN")
            self.assertTrue(
                any("recursos_derivados: PWN" in n for n in row["notes"])
            )
            # OWN-PT never invents UF
            self.assertNotEqual(row["sources"].get("OWN-PT"), "UF")
            self.assertEqual(row["proposta_final"], "UF")  # from PULO only
            # lexicon auditability in provenance
            self.assertTrue(
                any("own-pt:1.0.0" in p for p in row["union_of_provenance"])
            )

    def test_atestado_is_not_admit_farda(self):
        """OWN-PT attestation alone → sinalização; never auto UF."""
        with tempfile.TemporaryDirectory() as tmp:
            td = Path(tmp)
            own = {
                "class_id": "Demo",
                "lexicon": "own-pt:1.0.0",
                "provenance": [],
                "atestacao": {
                    "farda": {
                        "display": "farda",
                        "reason": "atestado OWN-PT via ILI i60712",
                        "offsets_ili": ["i60712"],
                        "lexicon": "own-pt:1.0.0",
                    }
                },
            }
            onto = {
                "class_id": "Demo",
                "provenance": [{
                    "termo": "constante",
                    "estatuto": "UF",
                    "offsets_ili": [],
                    "teste_decisivo": "t",
                    "garantia": ["lexical"],
                }],
            }
            (td / "Demo.OWN-PT.result.json").write_text(
                json.dumps(own), encoding="utf-8"
            )
            (td / "Demo.ONTO.result.json").write_text(
                json.dumps(onto), encoding="utf-8"
            )
            doc = lw.run_report(
                [
                    ("ONTO", td / "Demo.ONTO.result.json"),
                    ("OWN-PT", td / "Demo.OWN-PT.result.json"),
                ],
                td / "out",
                policy="conservative",
            )
            by_term = {c["term"]: c for c in doc["concepts"]}
            self.assertIn("farda", by_term)
            self.assertEqual(by_term["farda"]["veredicto"], "sinalização")
            self.assertEqual(by_term["farda"]["sources"]["OWN-PT"], "atestado")
            self.assertIsNone(by_term["farda"]["proposta_final"])

    def test_unmatched_pertinence_splits_verb(self):
        rows = [
            {"oewn_ili": "i33388", "pos": "v", "lemmas": [],
             "why": "sem lemas PT para evidência"},
            {"oewn_ili": "i6560", "pos": "a", "lemmas": [],
             "why": "sem lemas PT para evidência"},
        ]
        bie.annotate_unmatched_pertinence(rows)
        by = {r["oewn_ili"]: r for r in rows}
        self.assertEqual(by["i33388"]["pertinence"], "excluida_pela_classe")
        self.assertEqual(by["i6560"]["pertinence"], "pertinente")


if __name__ == "__main__":
    unittest.main()
