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
from semantic.normalize import normalize_word  # noqa: E402
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
        resolved = [s for s in non_syn if s.get("papel_focal")]
        unresolved = [s for s in non_syn if not s.get("papel_focal")]
        self.assertGreaterEqual(len(resolved), 4)
        for s in resolved:
            self.assertEqual([m["word"] for m in s["members"]], ["compósito"])
        args = {a for s in resolved for a in s["papel_arguments"]}
        self.assertTrue(
            {"material", "utilidade", "substância", "ter diverso utilidade"}
            <= args
        )
        for s in unresolved:
            self.assertTrue(s["members"], "unresolved não pode ter members=[]")
            self.assertEqual(s["papel_direction"], "unresolved")
        syn = next(
            s for s in upgraded["synsets"]
            if (s.get("relations") or {}).get("papel_group") == "SINONIMIA"
        )
        self.assertIn("heterogéneo", [m["word"] for m in syn["members"]])

    def test_focal_matches_unaccented_stored_form(self):
        """D2 residual — query «compósito» casa com w1 armazenado «composito»."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "PAPEL"
            src.mkdir()
            (src / "relacoes_final_REFERENTE.txt").write_text(
                "composito DIZ_SE_SOBRE X\n",
                encoding="utf-8",
            )
            db = Path(td) / "papel.sqlite"
            self.assertTrue(build_papel_sqlite(src, db)["ok"])
            store = PapelStore(db)
            export = store.export_search("compósito", mode="Exact", limit=20)
            store.close()
            self.assertEqual(export["count"], 1)
            syn = export["synsets"][0]
            self.assertEqual((syn.get("relations") or {}).get("papel_rel"), "DIZ_SE_SOBRE")
            self.assertEqual(
                normalize_word(syn["papel_focal"]), normalize_word("compósito")
            )
            self.assertEqual(syn["papel_direction"], "focal_to_argument")
            self.assertEqual([m["word"] for m in syn["members"]], ["composito"])
            self.assertEqual(syn["papel_arguments"], ["X"])

    def test_unresolved_focal_keeps_arguments_in_members(self):
        """D2 residual — sem focal, members conserva os argumentos (nunca [])."""
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "PAPEL"
            src.mkdir()
            (src / "relacoes_final_REFERENTE.txt").write_text(
                "palestriniano DIZ_SE_SOBRE compositor\n"
                "wagneriano DIZ_SE_SOBRE compositor\n",
                encoding="utf-8",
            )
            db = Path(td) / "papel.sqlite"
            self.assertTrue(build_papel_sqlite(src, db)["ok"])
            store = PapelStore(db)
            # «Starts with»: composito ⊂ compositor — hit sem lema exacto
            export = store.export_search("compósito", mode="Starts with", limit=20)
            store.close()
            syn = next(
                s for s in export["synsets"]
                if (s.get("relations") or {}).get("papel_rel") == "DIZ_SE_SOBRE"
            )
            self.assertIsNone(syn["papel_focal"])
            self.assertEqual(syn["papel_direction"], "unresolved")
            mems = {m["word"] for m in syn["members"]}
            self.assertTrue(mems, "members não pode ficar vazio")
            self.assertEqual(mems, set(syn["papel_arguments"]))
            self.assertIn("compositor", mems)


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
