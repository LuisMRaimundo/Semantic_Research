# -*- coding: utf-8 -*-
"""SenseIndex unit tests — fixtures are arbitrary CILI identities, not domain terms."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.engines import cili_api  # noqa: E402
from semantic.sense_index import (  # noqa: E402
    SenseIndex,
    rows_from_onto_export,
    rows_from_pulo_export,
    rows_from_wordnet_facets,
)


def _first_cili_pair() -> tuple[str, str]:
    """Return (ili_id, pwn30_offset) from the vendored map (any concept)."""
    _, counts_fn, resolve, offset = cili_api()
    counts = counts_fn()
    path = Path(counts["data_file"])
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            ili, off = parts[0].strip(), parts[1].strip()
            if ili and off and resolve(off) == ili:
                return ili, off
    raise RuntimeError("CILI map empty")


def _first_satellite_as_pair() -> tuple[str, str]:
    """Return (ili_id, offset-s) where PULO-style …-a must still resolve."""
    _, counts_fn, resolve, _ = cili_api()
    path = Path(counts_fn()["data_file"])
    with path.open(encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 2:
                continue
            ili, off = parts[0].strip(), parts[1].strip()
            if off.endswith("-s") and resolve(off[:-1] + "a") == ili:
                return ili, off
    raise RuntimeError("no a↔s satellite pair in CILI map")


class SenseIndexTests(unittest.TestCase):
    def test_pulo_rows_resolve_ili(self):
        ili, off = _first_cili_pair()
        export = {
            "type": "pulo_thesaurus_search",
            "synsets": [{
                "synset_offset": f"por-30-{off}",
                "pos": off[-1],
                "gloss": "fixture",
                "synonyms": ["lemma_alpha", "lemma_beta"],
                "ili": [{"ili_offset": f"ili-30-{off}"}],
            }],
        }
        rows = rows_from_pulo_export(export, "AnyClass")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["source"], "pulo")
        self.assertEqual(rows[0]["ili"], ili)
        self.assertEqual(rows[0]["class_id"], "AnyClass")

    def test_pulo_as_satellite_normalisation(self):
        ili, off_s = _first_satellite_as_pair()
        off_a = off_s[:-1] + "a"
        export = {
            "type": "pulo_thesaurus_search",
            "synsets": [{
                "synset_offset": f"por-30-{off_a}",
                "pos": "a",
                "gloss": "",
                "synonyms": ["lemma_gamma"],
                "ili": [{"ili_offset": f"ili-30-{off_a}"}],
            }],
        }
        rows = rows_from_pulo_export(export, "ProbeClass")
        self.assertEqual(rows[0]["ili"], ili)

    def test_onto_rows_have_null_ili(self):
        export = {
            "type": "thesaurus_search",
            "synsets": [{
                "resource": "TEP",
                "synset_id": "42",
                "pos": "n",
                "gloss": "",
                "members": [{"word": "lemma_delta", "weight": 1.0}],
            }],
        }
        rows = rows_from_onto_export(export, "ProbeClass")
        self.assertIsNone(rows[0]["ili"])
        self.assertTrue(rows[0]["sense_key"].startswith("onto:"))

    def test_upsert_and_stats(self):
        ili, _ = _first_cili_pair()
        with tempfile.TemporaryDirectory() as tmp:
            idx = SenseIndex(Path(tmp) / "idx.sqlite")
            with idx:
                n = idx.upsert_many(rows_from_wordnet_facets({
                    "type": "oewn_facets",
                    "synsets": [{
                        "name": f"oewn-fixture-{ili}",
                        "ili": ili,
                        "pos": "n",
                        "definition": "x",
                        "lemmas": ["en_lemma"],
                        "pt_lemmas": ["pt_lemma"],
                    }],
                }, "ProbeClass"))
                self.assertGreaterEqual(n, 2)
                st = idx.stats()
                self.assertGreaterEqual(st["with_ili"], 1)
                ids = idx.identifiers_for_class("ProbeClass")
                self.assertIn(ili, ids)


if __name__ == "__main__":
    unittest.main()
