"""CLI wrapper — prefer automatic generation via PASSO 7 (semantic.manifest)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.manifest import build_version_manifest  # noqa: E402


def main() -> int:
    m = build_version_manifest(ROOT)
    print(f"Wrote {m['_path']} ({m['_ok_count']}/{len(m['artefacts'])} ok)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
