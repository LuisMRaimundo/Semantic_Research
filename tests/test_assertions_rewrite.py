"""D5 — cabeçalho, tabela Markdown e JSON partilham a mesma contagem."""

from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from semantic.assertions import rewrite_assertions_block
from semantic.export_blocks import append_t12_to_concordance
from semantic.traceability import append_t15_to_concordance


_HEADER_RE = re.compile(r"^- \*\*Asserções:\*\* (\d+)/(\d+) PASS", re.M)


def _sample_md(n: int, extra_rows: str = "", residual: bool = False) -> str:
    rows = "\n".join(
        f"| T{i} | texto {i} | PASS ✅ | ev |" for i in range(1, n + 1)
    )
    tail = extra_rows
    if residual:
        tail += "\n# Relatório residual — `Demo`\n\n_(nenhuma)_\n"
    return (
        "# LexWarrant — concordância cruzada (**Demo**)\n\n"
        f"- **Asserções:** {n}/{n} PASS ✅\n\n"
        "## Asserções\n\n"
        "| # | Asserção | Resultado | Evidência |\n"
        "|---|----------|-----------|-----------|\n"
        f"{rows}\n"
        f"{tail}"
    )


def _counts(md_text: str, doc: dict) -> tuple[int, int, int]:
    m = _HEADER_RE.search(md_text)
    header_n = int(m.group(2)) if m else -1
    in_table = False
    md_rows = 0
    for ln in md_text.splitlines():
        if ln.strip() == "## Asserções":
            in_table = True
            continue
        if in_table and (ln.startswith("# ") or (
            ln.startswith("## ") and ln.strip() != "## Asserções"
        )):
            break
        if in_table and ln.startswith("| ") and not ln.startswith("| #") \
                and not ln.startswith("|---"):
            md_rows += 1
    return header_n, md_rows, len(doc.get("assertions") or [])


class AssertionsRewriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)

    def _write(self, asserts: list[dict], md: str) -> Path:
        jp = self.folder / "Demo.concordance.json"
        jp.write_text(
            json.dumps({"class": "Demo", "assertions": asserts}, indent=2) + "\n",
            encoding="utf-8",
        )
        jp.with_suffix(".md").write_text(md, encoding="utf-8")
        return jp

    def test_rewrite_keeps_header_table_json_equal(self):
        base = [{"id": f"T{i}", "text": f"t{i}", "passed": True, "evidence": "ok"}
                for i in range(1, 14)]
        jp = self._write(base, _sample_md(13, residual=True))
        extra = [
            {"id": "T12", "text": "blocos", "passed": True, "evidence": "ok"},
            {"id": "T15", "text": "rastreio", "passed": True, "evidence": "ok"},
            {"id": "R1", "text": "residual", "passed": True, "evidence": "n=0"},
        ]
        doc = json.loads(jp.read_text(encoding="utf-8"))
        doc["assertions"] = base + extra
        jp.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        info = rewrite_assertions_block(jp)
        doc2 = json.loads(jp.read_text(encoding="utf-8"))
        md = jp.with_suffix(".md").read_text(encoding="utf-8")
        header_n, md_rows, json_n = _counts(md, doc2)
        self.assertEqual(header_n, md_rows)
        self.assertEqual(md_rows, json_n)
        self.assertEqual(json_n, 16)
        self.assertEqual(info["header_n"], info["md_rows"])
        self.assertIn("# Relatório residual", md)
        # A tabela não reaparece depois do relatório
        after = md.split("# Relatório residual", 1)[1]
        self.assertNotIn("## Asserções", after)

    def test_append_helpers_then_rewrite_stay_equal(self):
        base = [{"id": f"T{i}", "text": f"t{i}", "passed": True, "evidence": "ok"}
                for i in range(1, 14)]
        jp = self._write(base, _sample_md(13, residual=True))
        append_t12_to_concordance(jp, {"t12_ok": True, "json": "x"})
        append_t15_to_concordance(jp, {
            "id": "T15",
            "text": "rastreio",
            "passed": True,
            "evidence": "OK",
        })
        doc = json.loads(jp.read_text(encoding="utf-8"))
        doc["assertions"] = [
            a for a in doc["assertions"] if a.get("id") != "R1"
        ]
        doc["assertions"].append({
            "id": "R1", "text": "residual", "passed": True, "evidence": "n=0",
        })
        jp.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        rewrite_assertions_block(jp)
        doc2 = json.loads(jp.read_text(encoding="utf-8"))
        md = jp.with_suffix(".md").read_text(encoding="utf-8")
        header_n, md_rows, json_n = _counts(md, doc2)
        self.assertEqual(header_n, md_rows)
        self.assertEqual(md_rows, json_n)
        self.assertEqual({a["id"] for a in doc2["assertions"]},
                         {f"T{i}" for i in range(1, 14)} | {"T12", "T15", "R1"})


if __name__ == "__main__":
    unittest.main()
