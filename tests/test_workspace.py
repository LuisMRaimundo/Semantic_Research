"""Unit tests for workspace + decisions + compile (no heavy engines)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic import decisions as decmod
from semantic.compile_specs import compile_pulo_spec
from semantic.workspace import ClassWorkspace, slug_class
import semantic.settings as settings


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()

    def test_slug_folds_accents(self):
        self.assertEqual(slug_class("TexturaCompósita"), "TexturaComposita")
        self.assertEqual(slug_class("Textura Metamórfica"), "TexturaMetamorfica")
        self.assertEqual(slug_class("TexturaPolitípica"), "TexturaPolitipica")
        self.assertEqual(slug_class("TexturaComposita"), "TexturaComposita")

    def test_create_and_status(self):
        ws = ClassWorkspace.create("DemoClass", pref_label="demo", axis="axis")
        st = ws.status()
        self.assertEqual(st["class_id"], "DemoClass")
        self.assertEqual(st["senses_total"], 0)
        self.assertIn("Search", st["next_step"])

    def test_seed_from_pulo_export(self):
        ws = ClassWorkspace.create("DemoClass")
        export = {
            "type": "pulo_thesaurus_search",
            "synsets": [
                {
                    "synset_offset": "por-30-1-a",
                    "pos": "a",
                    "gloss": "g",
                    "synonyms": ["alpha", "beta"],
                    "ili": [{"ili_offset": "ili-30-1-a"}],
                    "relations": [],
                }
            ],
        }
        dec = decmod.from_pulo_export(export, decmod.blank_decisions("DemoClass"))
        dec["senses"][0]["decision"] = "UF"
        decmod.save_decisions(ws.decisions_json, dec)
        spec = compile_pulo_spec(ws)
        self.assertEqual(spec["class_id"], "DemoClass")
        self.assertEqual(len(spec["stage1_whitelist"]), 1)
        self.assertEqual(spec["stage1_whitelist"][0]["decision"], "UF")

    def test_rename_preserves_decisions(self):
        ws = ClassWorkspace.create(
            "TexturaMetamrfica", pref_label="metamórfica", axis="mudança"
        )
        dec = decmod.blank_decisions(ws.class_id)
        dec["senses"] = [{
            "source": "pulo",
            "key": "ili-30-1-n",
            "ili": "ili-30-1-n",
            "gloss": "g",
            "members": ["a"],
            "decision": "UF",
            "note": "keep me",
        }]
        decmod.save_decisions(ws.decisions_json, dec)
        # fake artefacts keyed by class_id
        (ws.results / f"{ws.class_id}.PULO.result.json").write_text(
            json.dumps({"class_id": ws.class_id, "stage5": {"admitted": {}}},
                       ensure_ascii=False),
            encoding="utf-8",
        )
        (ws.final_results / f"FINAL__Onto_plus_PULO__{ws.class_id}.concordance.md"
         ).write_text("# ok\n", encoding="utf-8")

        renamed = ws.rename("TexturaMetamorfica")
        self.assertEqual(renamed.class_id, "TexturaMetamorfica")
        self.assertFalse((settings.CLASSES_DIR / "TexturaMetamrfica").exists())
        self.assertTrue(renamed.root.exists())
        meta = renamed.load_meta()
        self.assertEqual(meta["class_id"], "TexturaMetamorfica")
        self.assertEqual(meta["pref_label"], "metamórfica")  # untouched
        self.assertEqual(meta["axis"], "mudança")
        new_dec = json.loads(renamed.decisions_json.read_text(encoding="utf-8"))
        self.assertEqual(new_dec["class_id"], "TexturaMetamorfica")
        self.assertEqual(new_dec["senses"][0]["decision"], "UF")
        self.assertEqual(new_dec["senses"][0]["note"], "keep me")
        self.assertTrue(
            (renamed.results / "TexturaMetamorfica.PULO.result.json").exists()
        )
        self.assertTrue(
            (renamed.final_results
             / "FINAL__Onto_plus_PULO__TexturaMetamorfica.concordance.md").exists()
        )
        payload = json.loads(
            (renamed.results / "TexturaMetamorfica.PULO.result.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(payload["class_id"], "TexturaMetamorfica")


if __name__ == "__main__":
    unittest.main()
