# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.adapters.papel import (  # noqa: E402
    PapelStore,
    build_papel_sqlite,
    upgrade_papel_export,
)
from semantic.resources import inventory  # noqa: E402


class PapelIndexTests(unittest.TestCase):
    def test_build_and_search(self):
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "PAPEL"
            src.mkdir()
            (src / "relacoes_final_SINONIMIA.txt").write_text(
                "compósito SINONIMO_ADJ_DE composto\n"
                "textura SINONIMO_N_DE tecido\n",
                encoding="utf-8",
            )
            (src / "relacoes_final_HIPERONIMIA.txt").write_text(
                "compósito HIPERONIMO_DE material\n",
                encoding="utf-8",
            )
            db = Path(td) / "papel.sqlite"
            info = build_papel_sqlite(src, db)
            self.assertTrue(info["ok"])
            self.assertEqual(info["n_triples"], 3)
            store = PapelStore(db)
            export = store.export_search("compósito", mode="Exact", limit=20)
            store.close()
            self.assertGreaterEqual(export["count"], 1)
            members = {
                m["word"].lower()
                for syn in export["synsets"]
                for m in syn["members"]
            }
            self.assertIn("compósito", members)
            by_group = {
                (s.get("relations") or {}).get("papel_group"): s
                for s in export["synsets"]
            }
            hip = by_group.get("HIPERONIMIA")
            self.assertIsNotNone(hip)
            self.assertEqual(
                [m["word"] for m in hip["members"]], ["compósito"]
            )
            self.assertEqual(hip["papel_arguments"], ["material"])
            self.assertEqual(hip["papel_focal"], "compósito")
            self.assertEqual(hip["papel_direction"], "focal_to_argument")
            sin = by_group.get("SINONIMIA")
            self.assertIsNotNone(sin)
            sin_mem = {m["word"] for m in sin["members"]}
            self.assertEqual(sin_mem, {"compósito", "composto"})

    def test_upgrade_composito_export_keeps_args_out_of_members(self):
        """D2 — reprocessar o export versionado: não-SINONIMIA só tem o focal."""
        src = (
            ROOT / "classes" / "TexturaComposita" / "exports" / "papel_compósito.json"
        )
        if not src.exists():
            self.skipTest("papel_compósito.json não versionado neste checkout")
        raw = json.loads(src.read_text(encoding="utf-8"))
        upgraded = upgrade_papel_export(raw)
        non_syn = [
            s for s in upgraded["synsets"]
            if (s.get("relations") or {}).get("papel_group") != "SINONIMIA"
        ]
        self.assertEqual(len(non_syn), 4)
        for s in non_syn:
            self.assertEqual([m["word"] for m in s["members"]], ["compósito"])
        args = [a for s in non_syn for a in s["papel_arguments"]]
        self.assertEqual(
            set(args),
            {"material", "utilidade", "substância", "ter diverso utilidade"},
        )
        syn = next(
            s for s in upgraded["synsets"]
            if (s.get("relations") or {}).get("papel_group") == "SINONIMIA"
        )
        self.assertIn("heterogéneo", [m["word"] for m in syn["members"]])


class ResourceInventoryTests(unittest.TestCase):
    def test_inventory_sees_local_dumps(self):
        inv = inventory()
        by_id = {i["id"]: i for i in inv["items"]}
        self.assertIn("pulo_sqlite", by_id)
        self.assertTrue(by_id["pulo_sqlite"]["exists"])
        self.assertTrue(by_id["onto_sqlite"]["exists"])
        # dumps present on this machine
        self.assertTrue(by_id["onto_rdf"]["exists"])
        self.assertTrue(by_id["papel_dir"]["exists"])
        self.assertTrue(by_id["pulo_sql_20160508"]["exists"])


if __name__ == "__main__":
    unittest.main()
