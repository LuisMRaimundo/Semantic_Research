"""D8 — caixa Meta: continuação indentada, scope_note, chaves extra."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.meta_box import apply_meta_box, format_meta_box, parse_meta_box


class MetaBoxTests(unittest.TestCase):
    def test_multiline_axis_and_scope_note(self):
        text = (
            "pref_label: compósito\n"
            "axis: qualidade de ser feito de partes\n"
            "  distintas que convivem\n"
            "  no mesmo corpo\n"
            "scope_note: nota de âmbito\n"
            "  que ocupa duas linhas\n"
            "focus_stems: composito, misto\n"
        )
        parsed = parse_meta_box(text)
        f = parsed["fields"]
        self.assertEqual(f["pref_label"], "compósito")
        self.assertEqual(
            f["axis"],
            "qualidade de ser feito de partes distintas que convivem no mesmo corpo",
        )
        self.assertEqual(f["scope_note"], "nota de âmbito que ocupa duas linhas")
        self.assertEqual(f["focus_stems"], ["composito", "misto"])

    def test_axis_terms_and_lock(self):
        text = (
            "pref_label: x\n"
            "axis: y\n"
            "axis_terms: alfa, beta\n"
            "axis_terms_locked: true\n"
        )
        f = parse_meta_box(text)["fields"]
        self.assertEqual(f["axis_terms"], ["alfa", "beta"])
        self.assertTrue(f["axis_terms_locked"])

    def test_unknown_key_preserved_and_warned(self):
        meta = {"class_id": "Demo", "pref_label": "x", "concept_mapping": {"a": 1}}
        text = (
            "pref_label: x\n"
            "axis: y\n"
            "scope_note:\n"
            "focus_stems:\n"
            "axis_terms:\n"
            "axis_terms_locked: false\n"
            "nota_extra: valor livre\n"
        )
        out, warns = apply_meta_box(meta, text)
        self.assertEqual(out["nota_extra"], "valor livre")
        self.assertEqual(out["concept_mapping"], {"a": 1})
        self.assertTrue(any("nota_extra" in w for w in warns))

    def test_roundtrip_known_fields(self):
        meta = {
            "pref_label": "compósito",
            "axis": "heterogeneidade",
            "scope_note": "âmbito",
            "focus_stems": ["composito"],
            "axis_terms": ["misto"],
            "axis_terms_locked": False,
        }
        parsed = parse_meta_box(format_meta_box(meta))
        self.assertEqual(parsed["fields"]["pref_label"], "compósito")
        self.assertEqual(parsed["fields"]["scope_note"], "âmbito")
        self.assertEqual(parsed["fields"]["axis_terms"], ["misto"])
        self.assertFalse(parsed["fields"]["axis_terms_locked"])


if __name__ == "__main__":
    unittest.main()
