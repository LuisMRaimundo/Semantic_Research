"""Re-export LexWarrant identity helpers for the semantic package."""

from __future__ import annotations

from typing import Any

__all__ = [
    "SenseIdentity",
    "make_pwn30_id",
    "parse_identifier",
    "from_pulo_to_ili",
    "to_pwn30",
    "stable_key",
    "join_key",
    "export_ili_item",
    "is_cili",
]


def __getattr__(name: str) -> Any:
    if name in __all__:
        from .engines import load_identifiers

        return getattr(load_identifiers(), name)
    raise AttributeError(name)
