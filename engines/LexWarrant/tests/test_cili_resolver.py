#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task 1 — CILI resolver: pure lookup, no fabrication, never raises."""
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from cili_resolver import cili_counts, cili_offset, cili_resolve  # noqa: E402


class TestCiliResolver(unittest.TestCase):
    def test_data_loaded(self):
        c = cili_counts()
        self.assertGreater(c["ili_ids"], 100_000)
        self.assertEqual(c["ili_ids"], c["pwn30_offsets"] and c["ili_ids"])

    def test_known_ili_id_roundtrips(self):
        # i1 ↔ 00001740-a (primeira linha do ficheiro vendorizado)
        self.assertEqual(cili_resolve("i1"), "i1")
        self.assertEqual(cili_offset("i1"), "00001740-a")
        self.assertEqual(cili_resolve(cili_offset("i1")), "i1")

    def test_known_oewn_icode_roundtrips(self):
        # i10771 é o «uniform/unvarying» (adjudicado na classe TexturaUniforme)
        self.assertEqual(cili_resolve("i10771"), "i10771")
        off = cili_offset("i10771")
        self.assertIsNotNone(off)
        self.assertEqual(cili_resolve(off), "i10771")

    def test_pwn30_offset_resolves_with_namespace(self):
        # o offset PULO ili-30-XXXXXXXX-p resolve para o id CILI correspondente
        ili = cili_resolve("ili-30-00001740-a")
        self.assertEqual(ili, "i1")
        # namespaces OMW-30 equivalentes resolvem igual (por-30 = mesmo offset)
        self.assertEqual(cili_resolve("por-30-00001740-a"), "i1")

    def test_unknown_and_garbage_return_none(self):
        self.assertIsNone(cili_resolve("i999999999"))
        self.assertIsNone(cili_resolve("ili-30-99999999-z"))
        self.assertIsNone(cili_resolve("contopt:28395"))
        self.assertIsNone(cili_resolve(""))
        self.assertIsNone(cili_resolve(None))
        self.assertIsNone(cili_resolve(12345))
        self.assertIsNone(cili_resolve("zzz-99-12345678-a"))

    def test_never_raises(self):
        for bad in (object(), b"\x00\xff", ["i1"], {"x": 1}):
            try:
                self.assertIsNone(cili_resolve(bad))
            except Exception as exc:  # noqa: BLE001
                self.fail(f"cili_resolve levantou {exc!r} para {bad!r}")


if __name__ == "__main__":
    unittest.main()
