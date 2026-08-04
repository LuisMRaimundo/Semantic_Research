# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.gloss_sim import gloss_jaccard, passes_gloss_gate, sense_similarity  # noqa: E402
from semantic.ili_coverage import classify_identifiers  # noqa: E402
from semantic.engines import cili_api  # noqa: E402


class GlossSimTests(unittest.TestCase):
    def test_jaccard_related_glosses(self):
        from semantic.gloss_sim import gloss_tfidf_cosine
        a = "unchanging in form or character; remaining the same"
        b = "not changing or varying; constant in form"
        self.assertGreater(gloss_jaccard(a, b), 0.1)
        self.assertGreater(gloss_tfidf_cosine(a, b), gloss_jaccard(a, b) - 0.05)
        info = sense_similarity(a, b)
        self.assertIn(info["method"], ("tfidf+jaccard", "embedding+tfidf+jaccard"))
        self.assertGreater(info["tfidf_cosine"], 0.1)

    def test_gate_rejects_empty(self):
        self.assertFalse(passes_gloss_gate("", "something here"))

    def test_sense_similarity_components(self):
        info = sense_similarity(
            "a military uniform garment",
            "clothing worn by soldiers",
            ["uniform"],
            ["uniform"],
        )
        self.assertIn("score", info)
        self.assertGreaterEqual(info["score"], 0.0)


class IliCoverageTests(unittest.TestCase):
    def test_resolved_and_drift_buckets(self):
        _, _, resolve, offset = cili_api()
        ili, off = "i1", offset("i1")
        self.assertEqual(resolve(off), ili)
        report = classify_identifiers([
            f"ili-30-{off}",
            ili,
            "i999999999",  # almost certainly unresolved OEWN-style
            "ili-30-99999999-z",
        ])
        self.assertGreaterEqual(report["n_resolved"], 1)
        self.assertGreaterEqual(report["n_unresolved_oewn_ili"], 1)
        self.assertIn("pins", report)


class ConceptModelSmoke(unittest.TestCase):
    def test_render_skos(self):
        from semantic.concept_model import render_skos_owl

        ttl = render_skos_owl({
            "class_id": "ProbeConcept",
            "pref_label": "probe",
            "axis": "test axis",
            "discovery_evidence": {
                "uf_candidates": [{"members": ["alpha", "beta"]}],
                "rt_candidates": [{"members": ["gamma"]}],
                "exclude_records": [{"members": ["noise"], "source": "pulo"}],
            },
            "cili_exact": ["i1"],
            "cili_close": [],
            "cili_related": [],
            "skos_policy": "test policy",
            "generated": "now",
        })
        self.assertIn("skos:Concept", ttl)
        self.assertIn("skos:exactMatch <", ttl)
        self.assertIn("ili.globalwordnet.org/ili/i1", ttl)
        self.assertIn('skos:altLabel "alpha"@pt-PT', ttl)
        self.assertIn("sr:excludedCandidate", ttl)
        self.assertNotIn("skos:hiddenLabel", ttl)


if __name__ == "__main__":
    unittest.main()
