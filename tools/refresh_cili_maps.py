#!/usr/bin/env python3
"""Download upstream CILI offset maps (PWN 3.0 + 3.1) into engines/LexWarrant/data/cili/."""
from __future__ import annotations

from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "engines" / "LexWarrant" / "data" / "cili"
BASE = "https://raw.githubusercontent.com/globalwordnet/cili/master"


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    for name in ("ili-map-pwn30.tab", "ili-map-pwn31.tab"):
        url = f"{BASE}/{name}"
        print(f"GET {url}")
        data = urlopen(url, timeout=90).read()
        path = DEST / name
        path.write_bytes(data)
        print(f"  -> {path} ({len(data)} bytes, {data.count(chr(10).encode())} lines)")
    header = DEST / "HEADER.txt"
    header.write_text(
        """CILI — Collaborative Inter-Lingual Index (vendored, offline)
=============================================================
Files:     ili-map-pwn30.tab , ili-map-pwn31.tab
Fonte:     https://github.com/globalwordnet/cili  (branch master)
Refrescado: tools/refresh_cili_maps.py
Formato:   TSV sem cabeçalho, 2 colunas:  <ili-id>\\t<pwn-offset-pos>
Licença:   CC BY 4.0
Uso:       cili_resolver.py — multi-map lookup (PWN-3.0 + PWN-3.1) + optional
           wn.ili catalogue validation for bare i… ids (OEWN-native).
           Normalização a↔s. Nunca fabrica ILI.
""",
        encoding="utf-8",
    )
    print("HEADER refreshed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
