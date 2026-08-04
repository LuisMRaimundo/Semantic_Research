# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.adapters.papel import PapelStore, build_papel_sqlite  # noqa: E402
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
            self.assertTrue({"composto", "material"} & members)


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
