"""R2/R3/R7 — contraste → oposicao migration; T13; no-loss."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic import decisions as decmod


class ContrasteMigrationTests(unittest.TestCase):
    def test_migrate_sense_and_term_to_oposicao(self):
        raw = {
            "class_id": "TexturaUniforme",
            "senses": [
                {
                    "source": "onto",
                    "key": "clip21:18187",
                    "members": ["desigual", "irregular"],
                    "decision": "contraste",
                    "note": "",
                }
            ],
            "terms": [
                {
                    "term": "politípica",
                    "status": "contraste",
                    "note": "Teste 3",
                    "guarantee": ["estipulativa"],
                    "structural": "TexturaHeterogenea",
                    "definition": "textura composta por múltiplos tipos simultâneos",
                },
                {
                    "term": "desigual",
                    "status": "contraste",
                    "note": "Teste 3",
                    "guarantee": ["lexical"],
                },
                {
                    "term": "irregular",
                    "status": "contraste",
                    "note": "Teste 3",
                    "guarantee": ["lexical"],
                },
                {
                    "term": "variável",
                    "status": "contraste",
                    "note": "Teste 3",
                    "guarantee": ["lexical"],
                },
            ],
            "manual_terms": [],
            "exclude_terms": [],
        }
        out = decmod.migrate_contraste(raw)
        self.assertEqual(out["senses"][0]["decision"], "oposicao")
        self.assertEqual(out["senses"][0]["migrado_de"], "contraste")
        self.assertTrue(out["senses"][0]["revisao_pendente"])
        terms = {t["term"]: t for t in out["terms"]}
        for name in ("politípica", "desigual", "irregular", "variável"):
            self.assertEqual(terms[name]["status"], "oposicao")
            self.assertEqual(terms[name]["migrado_de"], "contraste")
            self.assertTrue(terms[name]["revisao_pendente"])
        # No heuristic → vizinha
        self.assertNotEqual(terms["politípica"]["status"], "vizinha")
        # Provenance fields preserved
        self.assertEqual(terms["politípica"]["structural"], "TexturaHeterogenea")
        self.assertIn("múltiplos", terms["politípica"]["definition"])
        log = out[decmod._MIGRATION_FLAG]
        self.assertEqual(log["count"], 5)
        labels = {m["label"] for m in log["items"]}
        self.assertTrue(any("desigual" in lab for lab in labels))
        self.assertIn("politípica", labels)
        self.assertIn("variável", labels)

    def test_load_legacy_file_no_loss_and_t13(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "decisions.json"
            legacy = {
                "class_id": "TexturaUniforme",
                "senses": [
                    {
                        "source": "onto",
                        "key": "contopt:5719",
                        "members": ["desigual", "irregular"],
                        "decision": "contraste",
                        "gloss": "",
                        "note": "keep-me",
                    }
                ],
                "terms": [
                    {
                        "term": "politípica",
                        "status": "contraste",
                        "note": "Teste 3",
                        "guarantee": ["estipulativa"],
                        "structural": "TexturaHeterogenea",
                        "definition": "def",
                    }
                ],
                "manual_terms": [
                    {
                        "term": "politípica",
                        "provenance": ["estipulativa"],
                        "definition": "def",
                        "structural": "TexturaHeterogenea",
                    }
                ],
                "exclude_terms": [],
            }
            path.write_text(
                json.dumps(legacy, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            loaded = decmod.load_decisions(path)
            # T13 — no contraste remains after load
            for s in loaded["senses"]:
                self.assertNotEqual(s.get("decision"), "contraste")
            for t in loaded["terms"]:
                self.assertNotEqual(t.get("status"), "contraste")
            self.assertEqual(loaded["senses"][0]["decision"], "oposicao")
            self.assertEqual(loaded["senses"][0]["note"], "keep-me")
            self.assertEqual(loaded["terms"][0]["status"], "oposicao")
            self.assertEqual(len(loaded["manual_terms"]), 1)
            # Disk untouched until save
            disk = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(disk["terms"][0]["status"], "contraste")
            # Save creates bak and persists oposicao
            decmod.save_decisions(path, loaded)
            from datetime import date
            bak = path.with_name(f"decisions.json.bak-{date.today().strftime('%Y%m%d')}")
            self.assertTrue(bak.exists())
            saved = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(saved["terms"][0]["status"], "oposicao")
            self.assertNotIn(decmod._MIGRATION_FLAG, saved)

    def test_ui_decisions_exclude_contraste(self):
        self.assertNotIn("contraste", decmod.DECISIONS_UI)
        self.assertNotIn("contraste", decmod.DECISIONS)
        self.assertIn("oposicao", decmod.DECISIONS)
        self.assertIn("vizinha", decmod.DECISIONS)


if __name__ == "__main__":
    unittest.main()
