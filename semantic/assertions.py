"""Reescrita da secção de asserções do concordance a partir do JSON.

T12, T15, R1 (e futuras) anexam-se só à lista JSON; esta função é a única
que toca no Markdown — no sítio, nunca por append — para o cabeçalho, a
tabela e o JSON ficarem com a mesma contagem.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_HEADER_RE = re.compile(
    r"^- \*\*Asserções:\*\* \d+/\d+ PASS[^\n]*",
    re.M,
)


def _assertion_passed(row: dict[str, Any]) -> bool:
    return bool(row.get("passed") or row.get("pass"))


def _render_assertions_section(asserts: list[dict[str, Any]]) -> str:
    lines = [
        "## Asserções",
        "",
        "| # | Asserção | Resultado | Evidência |",
        "|---|----------|-----------|-----------|",
    ]
    for a in asserts:
        mark = "PASS ✅" if _assertion_passed(a) else "FAIL ❌"
        ev = str(a.get("evidence") or "").replace("|", "\\|")
        lines.append(
            f"| {a.get('id') or '—'} | {a.get('text') or ''} | {mark} | {ev} |"
        )
    lines.append("")
    return "\n".join(lines)


def _replace_assertions_section(text: str, new_section: str) -> str:
    """Substitui ``## Asserções`` no sítio; deixa o que vier a seguir intacto."""
    lines = text.splitlines()
    start = None
    for i, ln in enumerate(lines):
        if ln.strip() == "## Asserções":
            start = i
            break
    if start is None:
        body = text.rstrip()
        return (body + "\n\n" if body else "") + new_section
    end = len(lines)
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if s.startswith("# ") or (
            s.startswith("## ") and s.strip() != "## Asserções"
        ):
            end = j
            break
    out = lines[:start] + new_section.splitlines()
    rest = lines[end:]
    if rest:
        if out and out[-1] != "":
            out.append("")
        out.extend(rest)
    return "\n".join(out) + "\n"


def rewrite_assertions_block(json_path: Path) -> dict[str, Any]:
    """Lê ``assertions`` do JSON e reescreve cabeçalho + tabela do ``.md``.

    Devolve contagens para testes: ``header_n``, ``md_rows``, ``json_n``.
    """
    json_path = Path(json_path)
    doc = json.loads(json_path.read_text(encoding="utf-8"))
    asserts = list(doc.get("assertions") or [])
    passed = sum(1 for a in asserts if _assertion_passed(a))
    total = len(asserts)
    all_ok = bool(asserts) and all(_assertion_passed(a) for a in asserts)
    if not asserts:
        all_ok = True
    doc["all_passed"] = all_ok
    json_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    md_path = json_path.with_suffix(".md")
    if not md_path.exists():
        return {"header_n": total, "md_rows": 0, "json_n": total}

    text = md_path.read_text(encoding="utf-8")
    mark = "✅" if all_ok else "❌"
    header = f"- **Asserções:** {passed}/{total} PASS {mark}"
    if _HEADER_RE.search(text):
        text = _HEADER_RE.sub(header, text, count=1)
    else:
        # Cabeçalho em falta — inserir antes da primeira secção
        text = header + "\n" + text.lstrip()

    text = _replace_assertions_section(text, _render_assertions_section(asserts))
    md_path.write_text(text, encoding="utf-8")

    # Contar só as linhas da tabela de asserções (após ## Asserções, antes do
    # próximo heading).
    in_table = False
    table_rows = 0
    for ln in text.splitlines():
        if ln.strip() == "## Asserções":
            in_table = True
            continue
        if in_table and (ln.startswith("# ") or (
            ln.startswith("## ") and ln.strip() != "## Asserções"
        )):
            break
        if in_table and ln.startswith("| ") and not ln.startswith("| #") \
                and not ln.startswith("|---"):
            table_rows += 1

    return {
        "header_n": total,
        "md_rows": table_rows,
        "json_n": total,
        "passed": passed,
        "header_line": header,
    }
