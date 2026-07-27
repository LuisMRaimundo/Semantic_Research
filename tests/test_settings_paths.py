# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from semantic.settings import ROOT as SR_ROOT, load_config, resolve_path  # noqa: E402


class SettingsPathTests(unittest.TestCase):
    def test_relative_resolve(self):
        p = resolve_path("engines/LexWarrant")
        self.assertTrue(p.is_absolute())
        self.assertTrue(str(p).endswith("LexWarrant"))
        self.assertTrue(str(p).startswith(str(SR_ROOT)))

    def test_load_config_resolves_inside_repo(self):
        cfg = load_config()
        for key in ("pulo_sqlite", "onto_sqlite", "lexwarrant_dir", "cili_map"):
            p = Path(cfg[key])
            self.assertTrue(p.is_absolute(), key)
            self.assertTrue(
                str(p.resolve()).lower().startswith(str(SR_ROOT.resolve()).lower()),
                f"{key} outside repo: {p}",
            )
            self.assertTrue(p.exists(), f"missing {key}: {p}")

    def test_pins_present(self):
        cfg = load_config()
        self.assertEqual(cfg.get("oewn"), "oewn:2024")
        self.assertEqual(cfg.get("own_pt"), "own-pt:1.0.0")
        self.assertGreaterEqual(int(cfg.get("cili_min_pairs") or 0), 117000)


if __name__ == "__main__":
    unittest.main()
