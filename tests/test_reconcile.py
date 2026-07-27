"""Corte 2 — residual report (T14 taxonomy removed)."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.reconcile import build_residual_report, reconcile_class
from semantic.workspace import ClassWorkspace
import semantic.settings as settings


class ResidualReconcileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        settings.CLASSES_DIR = Path(self.tmp.name) / "classes"
        settings.CLASSES_DIR.mkdir()
        self.ws = ClassWorkspace.create(
            "DemoRec", pref_label="uniforme", axis="invariância"
        )
        dec = {
            "class_id": "DemoRec",
            "senses": [
                {
                    "source": "pulo",
                    "key": "ili-30-1-a",
                    "ili": "ili-30-1-a",
                    "members": ["invariável"],
                    "decision": "UF",
                    "gloss": "g",
                    "note": "",
                },
                {
                    "source": "pulo",
                    "key": "ili-30-orphan-a",
                    "ili": "ili-30-orphan-a",
                    "members": ["fantasma"],
                    "decision": "UF",
                    "gloss": "g",
                    "note": "",
                },
            ],
            "terms": [],
            "manual_terms": [],
            "exclude_terms": [],
        }
        self.ws.decisions_json.write_text(
            json.dumps(dec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # Motor admits only invariável
        self.ws.results.mkdir(parents=True, exist_ok=True)
        (self.ws.results / "DemoRec.PULO.result.json").write_text(
            json.dumps(
                {
                    "class_id": "DemoRec",
                    "provenance": [
                        {
                            "termo": "invariável",
                            "estatuto": "UF",
                            "offsets_ili": ["ili-30-1-a"],
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_orphan_sense_listed(self):
        report = build_residual_report(self.ws)
        self.assertTrue(report.get("t14_removed"))
        orphans = report["acepcoes_sem_motor"]
        self.assertEqual(len(orphans), 1)
        self.assertEqual(orphans[0]["membros"], ["fantasma"])

    def test_reconcile_writes_files(self):
        r = reconcile_class(self.ws)
        self.assertTrue(Path(r["reconcile_json"]).exists())
        self.assertTrue(Path(r["reconcile_md"]).exists())


if __name__ == "__main__":
    unittest.main()
