#!/usr/bin/env python3
"""Run backend regression tests."""

import unittest

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests", pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    raise SystemExit(not runner.run(suite).wasSuccessful())
