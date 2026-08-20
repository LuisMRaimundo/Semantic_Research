"""Read-only CILI blocks for TERMOS export (never writes decisions)."""

from __future__ import annotations

from typing import Any, Optional

from .decisions import VOCABULARIO
from engines.CILI.cili_engine import CiliEngine, canonical_ili


def html_ident(ident: Any, *, text: str | None = None) -> str:
    """Plain identifier for TERMOS.html — never a remote ``<a href>``.

    FINAL_RESULTS HTML is a local document; links stay inside the export folder.
    """
    import html as _html

    raw = "" if ident is None else str(ident).strip()
    display = raw if text is None else str(text)
    if not raw or raw == "—":
        return _html.escape(display or "—", quote=True)
    return f"<code>{_html.escape(display or raw, quote=True)}</code>"


def html_idents(value: Any) -> str:
    if value is None or value == "" or value == "—":
        return "—"
    if isinstance(value, (list, tuple)):
        parts = [html_ident(x) for x in value if str(x).strip()]
        return "; ".join(parts) if parts else "—"
    s = str(value).strip()
    if ";" in s:
        bits = [html_ident(p.strip()) for p in s.split(";") if p.strip()]
        return "; ".join(bits) if bits else "—"
    return html_ident(s)


def export_cili_block_enabled(meta: dict[str, Any] | None, cfg: dict[str, Any] | None = None) -> bool:
    if meta and "export_cili_block" in meta:
        return bool(meta.get("export_cili_block"))
    if cfg is None:
        from .settings import load_config

        cfg = load_config()
    return bool(cfg.get("export_cili_block"))


def sense_cili_id(sense: dict[str, Any]) -> Optional[str]:
    """Extract a real CILI id from a sense card. Never fabricates."""
    for fld in ("cili_id", "cili", "to_ili", "ili"):
        cid = canonical_ili(sense.get(fld))
        if cid:
            return cid
    return None


def _export_langs(meta: dict[str, Any], indexed: list[str]) -> list[str]:
    raw = meta.get("cili_langs")
    if isinstance(raw, (list, tuple)) and raw:
        wanted = [str(x).strip().lower() for x in raw if str(x).strip()]
    else:
        wanted = ["pt", "en"]
    # Include other indexed languages when packs are present.
    extra = [lg for lg in indexed if lg not in wanted]
    ordered = []
    for lg in wanted + extra:
        if lg not in ordered:
            ordered.append(lg)
    return ordered


def build_cili_blocks(
    senses: list[dict[str, Any]],
    meta: dict[str, Any],
    engine: CiliEngine | None = None,
) -> list[dict[str, Any]]:
    """One block per adjudicated sense that already carries a CILI id."""
    if engine is None:
        engine = CiliEngine.from_config()
    indexed = []
    try:
        indexed = list(engine.stats().get("languages") or [])
    except Exception:  # noqa: BLE001
        indexed = engine.discovered_languages()
    langs = _export_langs(meta, indexed)
    blocks: list[dict[str, Any]] = []
    seen: set[str] = set()
    for sense in senses:
        decision = (sense.get("decision") or "").strip()
        if decision not in VOCABULARIO:
            continue
        cid = sense_cili_id(sense)
        if not cid or cid in seen:
            continue
        concept = engine.concept(cid)
        if not concept:
            continue
        seen.add(cid)
        by_lang = concept.get("by_lang") or {}
        equivalents = {
            lg: by_lang[lg]
            for lg in langs
            if lg in by_lang
        }
        # also match por/pt, eng/en
        for lg in langs:
            if lg in equivalents:
                continue
            for key, lems in by_lang.items():
                if key.startswith(lg) or lg.startswith(key[:2]):
                    equivalents[lg] = lems
                    break
        blocks.append({
            "sense_key": sense.get("key"),
            "decision": decision,
            "source": sense.get("source"),
            "ili": cid,
            "rdf_uri": concept.get("rdf_uri"),
            "page_uri": concept.get("page_uri"),
            "definition": concept.get("definition") or "",
            "pos": concept.get("pos"),
            "pos_norm": concept.get("pos_norm"),
            "pos_name": concept.get("pos_name"),
            "equivalents": equivalents,
        })
    return blocks


def render_cili_md(blocks: list[dict[str, Any]]) -> str:
    if not blocks:
        return ""
    lines = ["## CILI", ""]
    lines.append(
        "Read-only lexicographical reference (canonical ILI + English definition "
        "+ equivalents). Not a decision."
    )
    lines.append("")
    for b in blocks:
        lines.append(f"### {b['ili']}")
        lines.append("")
        rdf = b.get("rdf_uri") or ""
        page = b.get("page_uri") or ""
        lines.append(f"- **RDF:** `{rdf}`" if rdf else "- **RDF:** —")
        lines.append(f"- **page:** [{page}]({page})" if page else "- **page:** —")
        if b.get("pos_name"):
            lines.append(
                f"- **POS:** {b['pos_name']} (raw `{b.get('pos')}`, "
                f"norm `{b.get('pos_norm')}`)"
            )
        lines.append(f"- **definition (en):** {b.get('definition') or '—'}")
        eq = b.get("equivalents") or {}
        if eq:
            lines.append("- **equivalents:**")
            for lg, lems in eq.items():
                lines.append(f"  - `{lg}`: {', '.join(lems)}")
        lines.append("")
    return "\n".join(lines)


def render_cili_html(blocks: list[dict[str, Any]]) -> str:
    if not blocks:
        return ""
    import html as _html

    def _esc(s: Any) -> str:
        return _html.escape("" if s is None else str(s), quote=True)

    items = []
    for b in blocks:
        eq_bits = []
        for lg, lems in (b.get("equivalents") or {}).items():
            eq_bits.append(
                f"<span class=\"lang\">{_esc(lg)}</span> {_esc(', '.join(lems))}"
            )
        eq_html = " · ".join(eq_bits) if eq_bits else "<span class=\"empty\">—</span>"
        items.append(
            "<article class=\"cili-block\">"
            f"<h3>{html_ident(b.get('ili'))}</h3>"
            f"<p class=\"mono\">"
            f"<code>{_esc(b.get('page_uri'))}</code><br>"
            f"<code>{_esc(b.get('rdf_uri'))}</code>"
            f"</p>"
            f"<p>{_esc(b.get('definition') or '(no definition)')}</p>"
            f"<p>{eq_html}</p>"
            "</article>"
        )
    return (
        '\n<section class="sec" id="CILI" aria-labelledby="h-CILI">'
        '<header class="sec-head"><h2 id="h-CILI">CILI</h2></header>'
        "<p class=\"blurb\">Read-only lexicographical reference. Not a decision.</p>"
        + "".join(items)
        + "</section>"
    )
