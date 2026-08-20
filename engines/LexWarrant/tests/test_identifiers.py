#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identity helpers: bare CILI canonical; oewn-ili: is contextual CURIE only."""
import sys
import unittest
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE.parent))

from identifiers import (  # noqa: E402
    cili_page_url,
    cili_ref,
    cili_uri,
    from_pulo_to_ili,
    join_key,
    make_pwn30_id,
    normalize_cili_id,
    parse_identifier,
    public_id,
    stable_key,
    to_pwn30,
)
from cili_resolver import cili_resolve  # noqa: E402


class TestIdentifiers(unittest.TestCase):
    def test_make_pwn30_not_ili30(self):
        self.assertEqual(make_pwn30_id("14818238", "n"), "pwn30-14818238-n")
        self.assertFalse(make_pwn30_id("14818238", "n").startswith("ili-"))

    def test_normalize_cili_strips_curie(self):
        self.assertEqual(normalize_cili_id("oewn-ili:i114921"), "i114921")
        self.assertEqual(normalize_cili_id("ili:i97733"), "i97733")
        self.assertEqual(
            normalize_cili_id("http://globalwordnet.org/ili/i114921"), "i114921"
        )
        self.assertEqual(
            normalize_cili_id("http://ili.globalwordnet.org/ili/i114921"), "i114921"
        )
        self.assertEqual(
            normalize_cili_id("https://globalwordnet.github.io/cili/i97733.html"),
            "i97733",
        )
        self.assertEqual(
            normalize_cili_id("https://globalwordnet.github.io/cili/i97733"),
            "i97733",
        )
        with self.assertRaises(ValueError):
            normalize_cili_id("ili-30-14818238-n")
        with self.assertRaises(ValueError):
            normalize_cili_id("oewn-ili:i0")

    def test_cili_uri_and_page(self):
        self.assertEqual(
            cili_uri("oewn-ili:i114921"), "http://ili.globalwordnet.org/ili/i114921"
        )
        self.assertEqual(
            cili_page_url("i97733"),
            "https://globalwordnet.github.io/cili/i97733",
        )
        ref = cili_ref("oewn-ili:i114921", source="OEWN")
        self.assertEqual(ref["cili_id"], "i114921")
        self.assertEqual(ref["source_curie"], "oewn-ili:i114921")
        self.assertNotEqual(ref["cili_id"], ref["source_curie"])

    def test_legacy_ili30_is_pwn_not_cili(self):
        ident = parse_identifier("ili-30-14818238-n", resolve_cili=True)
        self.assertEqual(ident.pwn_id, "pwn30-14818238-n")
        self.assertEqual(ident.pwn_offset, "14818238")
        self.assertEqual(ident.part_of_speech, "n")
        self.assertEqual(ident.legacy_omw_ili, "ili-30-14818238-n")
        self.assertEqual(ident.cili_id, "i114921")
        self.assertEqual(ident.cili, "i114921")
        self.assertEqual(ident.cili_uri, "http://ili.globalwordnet.org/ili/i114921")
        self.assertEqual(ident.mapping_status, "official")
        self.assertNotEqual(ident.cili, "ili-30-14818238-n")

    def test_join_key_uses_bare_cili(self):
        a, a_ok = join_key("ili-30-14818238-n")
        b, b_ok = join_key("i114921")
        c, c_ok = join_key("oewn-ili:i114921")
        d, d_ok = join_key("pwn30-14818238-n")
        self.assertTrue(a_ok and b_ok and c_ok and d_ok)
        self.assertEqual(a, "i114921")
        self.assertEqual(b, "i114921")
        self.assertEqual(c, "i114921")
        self.assertEqual(d, "i114921")
        self.assertFalse(a.startswith("oewn-ili:"))

    def test_public_id_never_emits_curie(self):
        self.assertEqual(public_id("oewn-ili:i97733"), "i97733")
        self.assertEqual(public_id("i97733"), "i97733")

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
        self.assertEqual(ident.cili_id, "i114921")
        self.assertEqual(to_pwn30("ili-30-14818238-n"), "pwn30-14818238-n")

    def test_cili_resolve_accepts_pwn30(self):
        self.assertEqual(cili_resolve("pwn30-14818238-n"), "i114921")
        self.assertEqual(cili_resolve("ili-30-14818238-n"), "i114921")


if __name__ == "__main__":
    unittest.main()
