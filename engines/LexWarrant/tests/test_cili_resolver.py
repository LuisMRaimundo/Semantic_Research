#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CILI resolver: pure lookup, a↔s satellite normalisation, never fabricates."""
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from cili_resolver import CILI_VERSION, cili_counts, cili_offset, cili_resolve  # noqa: E402


def _map_path() -> Path:
    return Path(cili_counts()["data_file"])


def _first_row() -> tuple[str, str]:
    with _map_path().open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[0] and parts[1]:
                return parts[0].strip(), parts[1].strip()
    raise RuntimeError("empty CILI map")


def _first_satellite_s() -> tuple[str, str]:
    with _map_path().open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) == 2 and parts[1].endswith("-s"):
                return parts[0].strip(), parts[1].strip()
    raise RuntimeError("no -s row in CILI map")


class TestCiliResolver(unittest.TestCase):
    def test_data_loaded(self):
        c = cili_counts()
        self.assertGreater(c["ili_ids"], 100_000)
        # Multi-map: offsets from pwn30+pwn31 ≥ ili id count
        self.assertGreaterEqual(c.get("pwn_offsets") or c["pwn30_offsets"], c["ili_ids"])
        self.assertGreaterEqual(len(c.get("data_files") or []), 1)
        self.assertIn("cili@", CILI_VERSION)

    def test_known_ili_id_roundtrips(self):
        ili, off = _first_row()
        self.assertEqual(cili_resolve(ili), ili)
        self.assertEqual(cili_offset(ili), off)
        self.assertEqual(cili_resolve(off), ili)

    def test_pwn30_offset_resolves_with_namespace(self):
        ili, off = _first_row()
        self.assertEqual(cili_resolve(f"ili-30-{off}"), ili)
        self.assertEqual(cili_resolve(f"por-30-{off}"), ili)
        self.assertEqual(cili_resolve(f"eng-30-{off}"), ili)

    def test_adjective_satellite_a_s_normalisation(self):
        ili, off_s = _first_satellite_s()
        off_a = off_s[:-1] + "a"
        self.assertEqual(cili_offset(ili), off_s)
        self.assertEqual(cili_resolve(off_s), ili)
        self.assertEqual(cili_resolve(f"ili-30-{off_a}"), ili)
        self.assertEqual(cili_resolve(f"por-30-{off_a}"), ili)

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
