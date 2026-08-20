# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.resource_links import (  # noqa: E402
    links_for_sense,
    materialize_local_view,
    verify_oewn_id,
    verify_onto_key,
    verify_pulo_offset,
)


class ResourceLinkTests(unittest.TestCase):
    def test_pulo_links_verified(self):
        sense = {
            "source": "pulo",
            "key": "pwn30-00001740-a",
            "cili": "i1",
            "ili": "i1",
        }
        links = links_for_sense(sense)
        kinds = {ln.kind for ln in links}
        self.assertIn("cili", kinds)
        self.assertTrue(
            any(ln.kind == "cili" and ln.url.endswith("/cili/i1") and ".html" not in ln.url
                for ln in links)
        )
        self.assertFalse(
            any("ili.globalwordnet.org" in (ln.url or "") for ln in links)
        )
        self.assertTrue(any(ln.kind == "local" and ln.verified for ln in links))
        self.assertTrue(verify_pulo_offset("por-30-00001740-a"))

    def test_onto_links(self):
        sense = {"source": "onto", "key": "ontopt06:10"}
        self.assertTrue(verify_onto_key("ontopt06:10"))
        links = links_for_sense(sense)
        self.assertTrue(any(ln.kind == "onto" for ln in links))
        self.assertTrue(any(ln.kind == "local" and ln.verified for ln in links))
        path = materialize_local_view(sense)
        self.assertIsNotNone(path)
        assert path is not None
        text = path.read_text(encoding="utf-8")
        self.assertIn("Reconfirmado", text)
        self.assertIn("ontopt06:10", text)

    def test_oewn_links(self):
        self.assertTrue(verify_oewn_id("oewn-00001740-a"))
        sense = {
            "source": "wordnet",
            "key": "i1",
            "ili": "i1",
            "local_id": "oewn-00001740-a",
        }
        links = links_for_sense(sense)
        self.assertTrue(any(ln.kind == "oewn" and ln.verified for ln in links))
        self.assertTrue(any("en-word.net/synset/" in (ln.url or "") for ln in links))
        self.assertTrue(
            any((ln.url or "").endswith("02711835-a") or "00001740-a" in (ln.url or "")
                for ln in links)
        )


if __name__ == "__main__":
    unittest.main()
