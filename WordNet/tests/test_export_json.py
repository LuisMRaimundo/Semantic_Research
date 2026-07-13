"""Acceptance tests for the enriched WordNet JSON export (Fase 0 bi-source feed).

Exercises the real `WordNetCompleteGUI._export_json` against a small live query
('uniform'), without constructing a Tk window.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import tempfile
import unittest
from pathlib import Path

import oewn_backend as backend

# wordnet_gui_v2 emits banner prints (with ✓/•) at import time; capture stdout/
# stderr so importing it cannot crash under a non-UTF-8 console.
try:
    with contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        import wordnet_gui_v2 as gui
    _GUI_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - only if GUI libs missing
    gui = None
    _GUI_IMPORT_ERROR = exc

ORIGINAL_FIELDS = ("name", "pos", "definition", "examples", "lemmas",
                   "hypernyms", "hyponyms", "min_depth", "max_depth")
RELATION_KEYS = ("antonym", "derivationally_related_form", "similar_to",
                 "attribute", "also_see")


class _Var:
    """Minimal tk.StringVar stand-in."""

    def __init__(self, value: str):
        self._value = value

    def get(self) -> str:
        return self._value


@unittest.skipIf(gui is None, f"GUI module unavailable: {_GUI_IMPORT_ERROR}")
class TestEnrichedExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        backend.ensure_oewn()
        try:
            backend.ensure_translation_lexicon("por")
        except Exception:
            pass  # pt_lemmas may be empty; that's acceptable and noted
        cls.synsets = backend.synsets("uniform")
        assert cls.synsets, "expected 'uniform' to return synsets"

        exporter = gui.WordNetCompleteGUI.__new__(gui.WordNetCompleteGUI)
        # This is a bare instance (no Tk.__init__), so tkinter's Misc.__getattr__
        # would recurse infinitely on any missing attribute (it delegates to
        # self.tk, which is also unset). Give it a tk so __getattr__ raises a
        # normal AttributeError, letting the export's getattr(...) defaults work.
        exporter.tk = None
        exporter.ic = None
        exporter.term_var = _Var("uniform")
        exporter.pos_var = _Var("Todas")
        exporter.lang_var = _Var("English")
        exporter.current_synsets = cls.synsets

        tmp = Path(tempfile.mkdtemp()) / "uniform.json"
        exporter._export_json(str(tmp))
        cls.data = json.loads(tmp.read_text(encoding="utf-8"))
        cls.exported = cls.data["synsets"]

    # T1 -----------------------------------------------------------------
    def test_t1_original_fields_preserved(self):
        for s in self.exported:
            for field in ORIGINAL_FIELDS:
                self.assertIn(field, s, f"missing original field {field!r}")

    # T2 -----------------------------------------------------------------
    def test_t2_every_synset_has_ili_key(self):
        for s in self.exported:
            self.assertIn("ili", s)
            self.assertTrue(s["ili"] is None or isinstance(s["ili"], str))

    # T3 -----------------------------------------------------------------
    def test_t3_relations_shape(self):
        for s in self.exported:
            self.assertIn("relations", s)
            for key in RELATION_KEYS:
                self.assertIn(key, s["relations"], f"missing relation {key!r}")
                for tgt in s["relations"][key]:
                    self.assertIn("id", tgt)
                    self.assertIn("ili", tgt)
                    self.assertIn("words", tgt)
                    self.assertIn("gloss", tgt)
                    self.assertTrue(tgt["words"], "target words must be non-empty")

    # T4 -----------------------------------------------------------------
    def test_t4_adjectives_not_relation_empty(self):
        adjectives = [s for s in self.exported if s["pos"] == "a"]
        self.assertTrue(adjectives, "expected at least one POS='a' synset")
        for s in adjectives:
            rel = s["relations"]
            populated = (rel["antonym"] or rel["similar_to"]
                         or rel["derivationally_related_form"])
            self.assertTrue(
                populated,
                f"adjective {s['name']} has no antonym/similar_to/derivational")

    # T5 -----------------------------------------------------------------
    def test_t5_no_empty_word_targets(self):
        for s in self.exported:
            for key in RELATION_KEYS:
                for tgt in s["relations"][key]:
                    self.assertTrue(tgt["words"], f"empty words in {s['name']}/{key}")

    # T6 -----------------------------------------------------------------
    def test_t6_ili_not_synthesised_from_name(self):
        self.assertEqual(self.data["source"]["alignment"], "ILI via translate()")
        for s in self.exported:
            if not s["ili"]:
                continue
            digits = re.sub(r"\D", "", s["name"])       # oewn id digits
            self.assertNotEqual(s["ili"], "i" + digits,
                                "ILI must not be built from the oewn id")

    # T7 -----------------------------------------------------------------
    def test_t7_top_level_schema(self):
        for key in ("term", "pos", "language", "source", "synsets"):
            self.assertIn(key, self.data)
        self.assertIsInstance(self.data["synsets"], list)

    # T8 -----------------------------------------------------------------
    def test_t8_pt_lemmas_is_list(self):
        for s in self.exported:
            self.assertIn("pt_lemmas", s)
            self.assertIsInstance(s["pt_lemmas"], list)


if __name__ == "__main__":
    unittest.main()
