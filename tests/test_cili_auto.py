"""D6 — pares ILI divergentes produzem pending_ili_adjudication."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.cili_auto import pending_ili_from_report
from semantic.concept_model import build_class_concept_graph
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


class PendingIliTests(unittest.TestCase):
    def test_helper_copies_diverged_pairs(self):
        pending = pending_ili_from_report({
            "diverged": [{
                "oewn_ili": "oewn-ili:i1",
                "pulo_ili": "pwn30-1-a",
                "cili_oewn": "i1",
                "cili_pulo": "i2",
                "source": "human",
                "human": True,
            }],
            "confirmed": [{"oewn_ili": "x"}],
        })
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["cili_oewn"], "i1")
        self.assertEqual(pending[0]["cili_pulo"], "i2")

    def test_concept_graph_marks_pending_divergence(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        settings.CLASSES_DIR = Path(tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()
        ws = ClassWorkspace.create("DemoIli", pref_label="x", axis="y")
        ws.decisions_json.write_text(
            json.dumps({
                "class_id": "DemoIli",
                "senses": [], "terms": [], "manual_terms": [], "exclude_terms": [],
            }),
            encoding="utf-8",
        )
        fake = {
            "diverged": [{
                "oewn_ili": "oewn-1",
                "pulo_ili": "pwn30-1-a",
                "cili_oewn": "i10",
                "cili_pulo": "i20",
                "source": "legacy",
                "human": True,
            }],
            "confirmed": [],
            "legacy_without_cili": [],
        }
        with patch(
            "semantic.cili_auto.migrate_human_ili_table", return_value=fake
        ):
            graph = build_class_concept_graph(ws)
        self.assertEqual(len(graph["pending_ili_adjudication"]), 1)
        self.assertEqual(graph["mapping_status"], "pending_ili_divergence")


class CiliAutoMapKeyTests(unittest.TestCase):
    def test_markdown_uses_cili_auto_map(self):
        sys.path.insert(0, str(ROOT / "engines" / "LexWarrant"))
        from lexwarrant import render_markdown  # noqa: WPS433
        doc = {
            "class": "X",
            "policy": "conservative",
            "generated": "now",
            "columns": ["PULO"],
            "sources": ["PULO"],
            "source_status": {},
            "join_counts": {},
            "cili_auto_map": "out/ili_equivalence.cili.json",
            "legacy_equivalence_counts": {"mapped": 2, "unmatched": 0},
            "legacy_equivalence_loaded": True,
            "concepts": [],
            "summary": {
                "veredicto_totals": {},
                "descartados_pendentes": 0,
                "convergencia_plena": [],
                "convergencia_sentido": [],
                "convergencia_termo": [],
                "divergences": [],
                "fonte_unica": [],
            },
            "assertions": [],
            "all_passed": True,
        }
        md = render_markdown(doc, [])
        self.assertIn("`cili_auto_map`", md)
        self.assertNotIn("`legacy_equivalence`", md)
        # leitura retrocompatível da chave antiga
        doc.pop("cili_auto_map")
        doc["legacy_equivalence_map"] = "old.json"
        md_old = render_markdown(doc, [])
        self.assertIn("old.json", md_old)


if __name__ == "__main__":
    unittest.main()
