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
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()

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


if __name__ == "__main__":
    unittest.main()
