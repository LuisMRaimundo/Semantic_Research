"""Analisador da caixa Meta do workbench (blocos chave: / continuação indentada)."""

from __future__ import annotations

from typing import Any, Optional

KNOWN_META_KEYS = (
    "pref_label",
    "axis",
    "scope_note",
    "focus_stems",
    "axis_terms",
    "axis_terms_locked",
)
_LIST_KEYS = frozenset({"focus_stems", "axis_terms"})
_BOOL_KEYS = frozenset({"axis_terms_locked"})


def _is_key_line(line: str) -> bool:
    s = line.strip()
    if not s or s.startswith("#"):
        return False
    if line[:1] in (" ", "\t"):
        return False
    return ":" in s


def _parse_bool(raw: str) -> bool:
    return raw.strip().casefold() in {"1", "true", "yes", "sim"}


def _parse_list(raw: str) -> list[str]:
    return [x.strip() for x in raw.split(",") if x.strip()]


def parse_meta_box(text: str) -> dict[str, Any]:
    """Analisa o texto da caixa Meta.

    Uma linha ``chave:`` inicia um valor; linhas seguintes indentadas são
    continuação e concatenam-se com espaço. Chaves não reconhecidas não
    são descartadas — ficam em ``unknown``.
    """
    fields: dict[str, Any] = {}
    unknown: dict[str, str] = {}
    current: Optional[str] = None
    buf: list[str] = []

    def flush() -> None:
        nonlocal current, buf
        if current is None:
            return
        raw = " ".join(p for p in buf if p).strip()
        if current in _LIST_KEYS:
            val: Any = _parse_list(raw)
        elif current in _BOOL_KEYS:
            val = _parse_bool(raw)
        else:
            val = raw
        if current in KNOWN_META_KEYS:
            fields[current] = val
        else:
            unknown[current] = raw
        current = None
        buf = []

    for line in (text or "").splitlines():
        if _is_key_line(line):
            flush()
            key, rest = line.split(":", 1)
            current = key.strip()
            buf = [rest.strip()]
        elif current is not None and line[:1] in (" ", "\t"):
            buf.append(line.strip())
        elif line.strip():
            # Linha não indentada sem chave — tratar como continuação
            # só se já houver campo aberto; senão ignorar.
            if current is not None:
                buf.append(line.strip())
    flush()
    return {"fields": fields, "unknown": unknown}


def format_meta_box(meta: dict[str, Any]) -> str:
    """Renderiza os campos conhecidos (e desconhecidos já gravados) na caixa."""
    lines: list[str] = []
    for key in KNOWN_META_KEYS:
        val = meta.get(key)
        if key in _LIST_KEYS:
            lines.append(f"{key}: {', '.join(val or [])}")
        elif key in _BOOL_KEYS:
            lines.append(f"{key}: {'true' if val else 'false'}")
        else:
            lines.append(f"{key}: {val or ''}")
    return "\n".join(lines) + "\n"


def apply_meta_box(meta: dict[str, Any], text: str) -> tuple[dict[str, Any], list[str]]:
    """Actualiza *meta* com o texto da caixa. Devolve (meta, avisos)."""
    parsed = parse_meta_box(text)
    out = dict(meta)
    out.update(parsed["fields"])
    warnings: list[str] = []
    for key, val in parsed["unknown"].items():
        out[key] = val
        warnings.append(f"chave Meta não reconhecida preservada: {key}")
    return out, warnings
