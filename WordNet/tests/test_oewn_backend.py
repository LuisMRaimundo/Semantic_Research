"""Regression tests for Open English Wordnet backend."""

from __future__ import annotations

import unittest

import oewn_backend as backend
from oewn_backend import (
    SynsetAdapter,
    ensure_oewn,
    format_score,
    get_translation_lemmas,
    get_wordnet,
)


class TestFormatScore(unittest.TestCase):
    def test_none(self):
        self.assertEqual(format_score(None), "N/A")

    def test_finite(self):
        self.assertEqual(format_score(0.0625), "0.0625")

    def test_inf(self):
        self.assertEqual(format_score(float("inf")), "inf")


class TestOpenEnglishWordnetBackend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        ensure_oewn()

    def test_synsets_dog(self):
        hits = backend.synsets("dog")
        self.assertGreater(len(hits), 0)
        self.assertTrue(hits[0].definition())

    def test_morphy(self):
        self.assertEqual(backend.morphy("dogs", backend.NOUN), "dog")

    def test_path_similarity(self):
        dog = backend.synsets("dog")[0]
        cat = backend.synsets("cat")[0]
        score = dog.path_similarity(cat)
        self.assertIsNotNone(score)
        self.assertGreater(score, 0.0)

    def test_similarity_tab_formatting_integration(self):
        dog = backend.synsets("dog")[0]
        cat = backend.synsets("cat")[0]
        rendered = (
            f"Path: {format_score(dog.path_similarity(cat))}; "
            f"WUP: {format_score(dog.wup_similarity(cat))}"
        )
        self.assertIn("Path:", rendered)
        self.assertNotIn("if ", rendered)

    def test_translation_portuguese(self):
        dog = backend.synsets("dog")[0]
        backend.ensure_translation_lexicon("por")
        pt = get_translation_lemmas(dog, "por")
        self.assertTrue(pt)
        self.assertTrue(any("c" in lemma.lower() for lemma in pt))

    def test_foreign_search(self):
        backend.ensure_translation_lexicon("por")
        hits = backend.synsets("cão", lang="por")
        self.assertGreater(len(hits), 0)

    def test_synset_roundtrip(self):
        original = backend.synsets("dog")[0]
        loaded = backend.synset(original.name())
        self.assertEqual(loaded.definition(), original.definition())

    def test_empty_search(self):
        self.assertEqual(backend.synsets("xyzzy_nonexistent_word_12345"), [])

    def test_hypernyms_and_closure(self):
        ss = backend.synsets("dog")[0]
        self.assertGreater(len(ss.hypernyms()), 0)
        closure = ss.closure(lambda s: s.hypernyms(), depth=2)
        self.assertIsInstance(closure, list)

    def test_information_content(self):
        ic = backend.wordnet_ic.ic()
        ss = backend.synsets("dog")[0]
        value = backend.information_content_value(ss, ic)
        self.assertGreater(value, 0.0)


if __name__ == "__main__":
    unittest.main()
