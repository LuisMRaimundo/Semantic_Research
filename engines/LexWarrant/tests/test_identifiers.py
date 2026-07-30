#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identity helpers: never fabricate CILI; ili-30- is legacy PWN3.0 only."""
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from identifiers import (  # noqa: E402
    from_pulo_to_ili,
    join_key,
    make_pwn30_id,
    parse_identifier,
    stable_key,
    to_pwn30,
)
from cili_resolver import cili_resolve  # noqa: E402


class TestIdentifiers(unittest.TestCase):
    def test_make_pwn30_not_ili30(self):
        self.assertEqual(make_pwn30_id("14818238", "n"), "pwn30-14818238-n")
        self.assertFalse(make_pwn30_id("14818238", "n").startswith("ili-"))

    def test_legacy_ili30_is_pwn_not_cili(self):
        ident = parse_identifier("ili-30-14818238-n", resolve_cili=True)
        self.assertEqual(ident.pwn_id, "pwn30-14818238-n")
        self.assertEqual(ident.pwn_offset, "14818238")
        self.assertEqual(ident.part_of_speech, "n")
        self.assertEqual(ident.legacy_omw_ili, "ili-30-14818238-n")
        # Official CILI for this PWN30 offset
        self.assertEqual(ident.cili, "i114921")
        self.assertEqual(ident.mapping_status, "official")
        # The legacy string itself is NOT a CILI id
        self.assertNotEqual(ident.cili, "ili-30-14818238-n")

    def test_join_key_unifies_on_cili(self):
        a, a_ok = join_key("ili-30-14818238-n")
        b, b_ok = join_key("i114921")
        c, c_ok = join_key("pwn30-14818238-n")
        self.assertTrue(a_ok and b_ok and c_ok)
        self.assertEqual(a, "oewn-ili:i114921")
        self.assertEqual(b, "oewn-ili:i114921")
        self.assertEqual(c, "oewn-ili:i114921")

    def test_stable_key_equates_spellings(self):
        self.assertEqual(
            stable_key("ili-30-14818238-n"),
            stable_key("pwn30-14818238-n"),
        )
        self.assertEqual(
            stable_key("por-30-14818238-n"),
            stable_key("pwn30-14818238-n"),
        )

    def test_from_pulo_to_ili(self):
        ident = from_pulo_to_ili(
            "ili-30-14818238-n",
            synset_offset="por-30-14818238-n",
            ili_wn_id="eng-30",
        )
        self.assertEqual(ident.source, "PULO")
        self.assertEqual(ident.pwn_id, "pwn30-14818238-n")
        self.assertEqual(ident.cili, "i114921")
        self.assertEqual(to_pwn30("ili-30-14818238-n"), "pwn30-14818238-n")

    def test_cili_resolve_accepts_pwn30(self):
        self.assertEqual(cili_resolve("pwn30-14818238-n"), "i114921")
        self.assertEqual(cili_resolve("ili-30-14818238-n"), "i114921")


if __name__ == "__main__":
    unittest.main()
