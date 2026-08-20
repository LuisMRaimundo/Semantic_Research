"""Human / JSON formatters for ``sr cili`` subcommands."""

from __future__ import annotations

import json
from typing import Any

from engines.CILI.cili_engine import CiliEngine, POS_NAMES


def engine_from_config() -> CiliEngine:
    return CiliEngine.from_config()


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2)


def format_concept(c: dict[str, Any] | None) -> str:
    if not c:
        return "concept not found"
    lines = [
        f"{c['ili']}  ·  {c.get('kind') or '—'}  ·  "
        f"{c.get('pos_name') or '—'}  ·  pos_norm={c.get('pos_norm') or '—'}  ·  "
        f"{c.get('status') or '—'}",
        c.get("definition") or "(no definition)",
        f"RDF  {c.get('rdf_uri')}",
        f"page {c.get('page_uri')}",
    ]
    by_lang = c.get("by_lang") or {}
    if by_lang:
        lines.append("lemmas")
        for lg, lems in by_lang.items():
            lines.append(f"  {lg}: {', '.join(lems)}")
    mappings = c.get("mappings") or []
    if mappings:
        lines.append("mappings")
        for m in mappings:
            lines.append(
                f"  {m.get('resource')}  {m.get('target')}  "
                f"{m.get('lemmas') or ''}"
            )
    return "\n".join(lines)


def format_entry(e: dict[str, Any], *, lang: str | None = None) -> str:
    if not e.get("count"):
        return (
            f"No exact lemma {e.get('lemma')!r} in the CILI index. "
            "Try: python sr.py cili search <query>"
        )
    lines = [
        f"{e['lemma']}  ·  {e['count']} sense(s)  ·  {', '.join(e.get('langs') or [])}",
    ]
    eq = e.get("equivalents") or {}
    if lang:
        eq = {k: v for k, v in eq.items() if k == lang or k.startswith(lang)}
    if eq:
        lines.append("interlingual equivalents (shared-sense count)")
        for lg, rows in eq.items():
            bits = [f"{r['lemma']}^{r['shared_senses']}" for r in rows]
            lines.append(f"  {lg}: {', '.join(bits)}")
    for pos, rows in (e.get("groups") or {}).items():
        lines.append(pos)
        for i, r in enumerate(rows, 1):
            pos_disp = r.get("pos_name") or POS_NAMES.get(r.get("pos") or "", "")
            extra = f"  [{pos_disp}]" if pos_disp and pos_disp != pos else ""
            lines.append(
                f"  {i}. {r.get('definition') or '(no definition)'}  "
                f"{r['ili']}{extra}"
            )
            for lg, lems in (r.get("translations") or {}).items():
                if lang and lg != lang and not lg.startswith(lang):
                    continue
                lines.append(f"     {lg}: {', '.join(lems)}")
    gaps = e.get("gaps") or {}
    src = set(e.get("langs") or [])
    shown = False
    for lg, missing in gaps.items():
        if not missing:
            continue
        if src == {lg}:
            continue
        if lang and lg != lang and not lg.startswith(lang):
            continue
        if not shown:
            lines.append("lexical gaps")
            shown = True
        lines.append(f"  {lg}: no label for {len(missing)} sense(s): {', '.join(missing)}")
    return "\n".join(lines)


def format_search(doc: dict[str, Any]) -> str:
    lines = [f"{doc.get('total', 0)} match(es)"]
    for r in doc.get("results") or []:
        pos = r.get("pos_name") or r.get("pos") or ""
        snip = (r.get("lem_snip") or "").replace("<b>", "").replace("</b>", "")
        definition = (r.get("def_snip") or r.get("definition") or "")
        definition = definition.replace("<b>", "").replace("</b>", "")
        lines.append(f"  {r['ili']}  {pos}  {snip}")
        if definition:
            lines.append(f"      {definition[:160]}")
    return "\n".join(lines)


def format_index(info: dict[str, Any]) -> str:
    lines = [
        f"rebuilt={info.get('rebuilt')}  path={info.get('path')}",
    ]
    if info.get("elapsed_s") is not None:
        lines.append(f"elapsed={info['elapsed_s']}s  concepts={info.get('concepts')}")
    by_lang = info.get("labels_by_lang") or {}
    if by_lang:
        bits = [f"{lg}={n}" for lg, n in sorted(by_lang.items())]
        lines.append("labels: " + ", ".join(bits))
    langs = info.get("languages") or []
    if langs:
        lines.append("languages: " + ", ".join(langs))
    if info.get("pin_written"):
        lines.append(f"pin written: {info['pin_written']}")
    if info.get("map_hash_warning"):
        lines.append("WARNING: " + info["map_hash_warning"])
    stats = info.get("stats") or {}
    if stats.get("concepts") and not info.get("rebuilt"):
        lines.append(f"concepts={stats['concepts']}")
        labels = stats.get("labels_by_lang") or []
        if labels:
            bits = [f"{r['lang']}={r['n']}" for r in labels]
            lines.append("labels: " + ", ".join(bits))
    return "\n".join(lines)
