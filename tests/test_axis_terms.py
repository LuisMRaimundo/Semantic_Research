"""D1 — axis_terms derivado; locked respeitado; exclude-only sinalizado."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.compile_specs import (
    axis_terms_exclusive_to_exclude,
    compile_pulo_spec,
)
from semantic.normalize import fold
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


class AxisTermsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()
        self.ws = ClassWorkspace.create(
            "DemoAxis", pref_label="compósito", axis="heterogeneidade",
            focus_stems=["compósito"],
        )
        meta = self.ws.load_meta()
        meta["axis_terms"] = [
            "vario", "mesclado", "misturado", "amalgamado", "compósito",
        ]
        self.ws.save_meta(meta)
        self.ws.decisions_json.write_text(
            json.dumps({
                "class_id": "DemoAxis",
                "senses": [
                    {
                        "source": "pulo",
                        "key": "uf-1",
                        "ili": "i1",
                        "members": ["compósito"],
                        "decision": "UF",
                        "gloss": "feito de partes distintas",
                    },
                    {
                        "source": "pulo",
                        "key": "ex-1",
                        "ili": "i2",
                        "members": ["misturado", "amalgamado", "mesclado"],
                        "decision": "exclude",
                        "gloss": "mistura de ingredientes",
                    },
                ],
                "terms": [],
                "manual_terms": [],
                "exclude_terms": [],
            }, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_compile_drops_exclude_only_terms(self):
        spec = compile_pulo_spec(self.ws)
        axis = spec["axis_terms"]
        for dead in ("misturado", "amalgamado", "mesclado", "vario"):
            self.assertNotIn(fold(dead), axis)
        self.assertIn(fold("compósito"), axis)
        meta = self.ws.load_meta()
        self.assertEqual(meta["axis_terms"], axis)
        self.assertIn("misturado", [fold(t) for t in meta["axis_terms_previous"]])
        # Glosa de fusão deixa de passar o teste de eixo
        g = fold("mistura de ingredientes amalgamado")
        self.assertFalse(any(t in g for t in axis))

    def test_locked_keeps_stored(self):
        meta = self.ws.load_meta()
        meta["axis_terms_locked"] = True
        self.ws.save_meta(meta)
        spec = compile_pulo_spec(self.ws)
        self.assertIn(fold("misturado"), spec["axis_terms"])

    def test_doctor_flags_exclude_only(self):
        meta = self.ws.load_meta()
        dec = json.loads(self.ws.decisions_json.read_text(encoding="utf-8"))
        bad = axis_terms_exclusive_to_exclude(meta, dec)
        self.assertIn(fold("misturado"), bad)
        self.assertNotIn(fold("compósito"), bad)


if __name__ == "__main__":
    unittest.main()
