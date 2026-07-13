#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1/T2 — the ILI→own-pt bridge is live and pinned.

Requires own-pt:1.0.0 + oewn:2024 installed (as in the target environment). If
own-pt is absent the PT assertions are skipped (the note-only-when-empty rule is
still checked structurally elsewhere).
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import oewn_backend as backend  # noqa: E402

_HAS_PT = backend.own_pt_installed()


class TestPtAlignment(unittest.TestCase):
    def test_pinned_to_2024(self):
        # With 2024 installed it must pin to 2024, never jump to 2025.
        self.assertEqual(backend.ensure_oewn(), "oewn:2024")

    @unittest.skipUnless(_HAS_PT, "own-pt não instalado")
    def test_t1_pt_lemmas_match_repl(self):
        pt = backend.synset(backend.PT_SELFCHECK_SYNSET).pt_lemmas()
        self.assertIn("uniforme", pt)
        self.assertIn("invariável", pt)

    @unittest.skipUnless(_HAS_PT, "own-pt não instalado")
    def test_selfcheck_returns_pt(self):
        pt = backend.pt_alignment_selfcheck(log=False)
        self.assertIn("uniforme", pt)

    @unittest.skipUnless(_HAS_PT, "own-pt não instalado")
    def test_t2_empty_only_when_translate_truly_empty(self):
        # This synset DOES translate → non-empty (the note may NOT claim missing).
        self.assertTrue(backend.synset("oewn-01973553-a").pt_lemmas())
        # This one genuinely has no own-pt synset → [] (note is legitimate here).
        self.assertEqual(backend.synset("oewn-00748118-a").pt_lemmas(), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
