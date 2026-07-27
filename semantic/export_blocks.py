"""PASSO 7 sibling blocks: vocabulario (SKOS-XL) vs evidencia_delimitacao."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Optional

from .decisions import EVIDENCIA, VOCABULARIO, load_decisions
from .workspace import ClassWorkspace

EVIDENCE_NOTE = (
    "Registos documentais. Não constituem relações do vocabulário."
)

_ANTONYM_RE = re.compile(r"material de contraste\s*\(antonym\)", re.I)
_SIMILAR_RE = re.compile(r"vizinho\s+similar_to", re.I)


def _ili_anchor(decisions: dict[str, Any], meta: dict[str, Any]) -> list[str]:
    """Prefer PULO UF senses with ILI; fall back to any PULO ILI on the class."""
    ilis: list[str] = []
    seen = set()
    for s in decisions.get("senses") or []:
        if (s.get("source") or "").lower() != "pulo":
            continue
        if (s.get("decision") or "").strip() != "UF":
            continue
        ili = (s.get("ili") or "").strip()
        if ili and ili not in seen:
            seen.add(ili)
            ilis.append(ili)
    if ilis:
        return ilis
    for s in decisions.get("senses") or []:
        if (s.get("source") or "").lower() != "pulo":
            continue
        ili = (s.get("ili") or "").strip()
        if ili and ili not in seen:
            seen.add(ili)
            ilis.append(ili)
    return ilis


def _collect_auto_signals(ws: ClassWorkspace) -> dict[str, list[dict[str, Any]]]:
    """Harvest antonym / similar_to rows from engine result sinalizacao (read-only)."""
    antonyms: list[dict[str, Any]] = []
    similar: list[dict[str, Any]] = []
    for path in sorted(ws.results.glob(f"{ws.class_id}.*.result.json")):
        if ".for_merge" in path.name:
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        source = "WordNet"
        low = path.name.lower()
        if ".pulo." in low:
            source = "PULO"
        elif ".onto." in low:
            source = "ONTO"
        sina = data.get("sinalizacao") or {}
        if not isinstance(sina, dict):
            continue
        for _key, info in sina.items():
            reason = info.get("reason") or ""
            row = {
                "termo": info.get("display") or _key,
                "ili": list(info.get("offsets_ili") or []),
                "synset_origem": reason,
                "fonte": source,
                "reason": reason,
            }
            if _ANTONYM_RE.search(reason):
                antonyms.append(row)
            elif _SIMILAR_RE.search(reason):
                similar.append(row)
    return {"antonym": antonyms, "similar_to": similar}


def build_export_blocks(ws: ClassWorkspace) -> dict[str, Any]:
    """Build Bloco A (vocabulario) + Bloco B (evidencia_delimitacao) from decisions."""
    meta = ws.load_meta()
    dec = load_decisions(ws.decisions_json)
    pref = meta.get("pref_label") or ws.class_id
    axis = meta.get("axis") or ""

    alt_labels: list[dict[str, Any]] = []
    relacionados: list[dict[str, Any]] = []
    excludes: list[dict[str, Any]] = []
    atributos: list[dict[str, Any]] = []
    oposicoes: list[dict[str, Any]] = []
    vizinhas: list[dict[str, Any]] = []

    for s in dec.get("senses") or []:
        decision = (s.get("decision") or "").strip()
        if not decision:
            continue
        base = {
            "fonte": s.get("source"),
            "key": s.get("key"),
            "ili": s.get("ili"),
            "membros": list(s.get("members") or []),
            "gloss": s.get("gloss") or "",
            "note": s.get("note") or "",
            "destino": s.get("destino") or (
                "vocabulario" if decision in VOCABULARIO else "evidencia"
            ),
        }
        if decision == "UF":
            for m in s.get("members") or []:
                alt_labels.append({**base, "termo": m, "skos": "skosxl:altLabel"})
        elif decision == "RT":
            for m in s.get("members") or []:
                relacionados.append({
                    **base,
                    "termo": m,
                    "skos": "tex:termoRelacionado",
                })
        elif decision == "exclude":
            excludes.append(base)
        elif decision == "atributo":
            atributos.append({**base, "eixo_vertente": axis})
        elif decision == "oposicao":
            oposicoes.append({
                **base,
                "migrado_de": s.get("migrado_de"),
                "revisao_pendente": s.get("revisao_pendente"),
            })
        elif decision == "vizinha":
            vizinhas.append({
                **base,
                "classe_remissao": s.get("structural") or s.get("note") or "",
            })

    for t in dec.get("terms") or []:
        status = (t.get("status") or "").strip()
        if not status:
            continue
        row = {
            "termo": t.get("term"),
            "fonte": "terms",
            "note": t.get("note") or "",
            "guarantee": list(t.get("guarantee") or []),
            "destino": t.get("destino") or (
                "vocabulario" if status in VOCABULARIO else "evidencia"
            ),
        }
        if status == "UF":
            alt_labels.append({**row, "skos": "skosxl:altLabel"})
        elif status == "RT":
            relacionados.append({**row, "skos": "tex:termoRelacionado"})
        elif status == "exclude":
            excludes.append(row)
        elif status == "atributo":
            atributos.append({**row, "eixo_vertente": axis})
        elif status == "oposicao":
            oposicoes.append({
                **row,
                "migrado_de": t.get("migrado_de"),
                "revisao_pendente": t.get("revisao_pendente"),
                "definition": t.get("definition") or "",
                "structural": t.get("structural") or "",
            })
        elif status == "vizinha":
            vizinhas.append({
                **row,
                "classe_remissao": t.get("structural") or t.get("note") or "",
                "definition": t.get("definition") or "",
            })

    auto = _collect_auto_signals(ws)

    vocabulario = {
        "prefLabel": {
            "termo": pref,
            "skos": "skos:prefLabel",
            # SKOS-XL labelling of the preferred form is via skosxl:prefLabel
            # when a label node is used; engines also emit skos:prefLabel literal.
            "skosxl": "skosxl:prefLabel",
        },
        "altLabel": alt_labels,
        "termoRelacionado": relacionados,
    }
    evidencia = {
        "nota": EVIDENCE_NOTE,
        "ancora_ili": _ili_anchor(dec, meta),
        "exclude": excludes,
        "material_contraste_auto": auto["antonym"],
        "vizinhos_similar_to_auto": auto["similar_to"],
        "atributo": atributos,
        "oposicao": oposicoes,
        "vizinha": vizinhas,
    }

    return {
        "class_id": ws.class_id,
        "vocabulario": vocabulario,
        "evidencia_delimitacao": evidencia,
    }


def assert_blocks_disjoint(blocks: dict[str, Any]) -> tuple[bool, str]:
    """T12: no *decision record* is routed to both vocabulary and evidence.

    Polysemy may place the same lemma string in both blocks (UF sense + exclude
    sense members) — that is expected. Violations are mis-routed records:
    a vocabulary row with destino=evidencia, or an evidence row with
    destino=vocabulario, or the same sense key appearing in both blocks.
    """
    vocab_keys: set[str] = set()
    evid_keys: set[str] = set()
    bad_destino: list[str] = []

    for key in ("altLabel", "termoRelacionado"):
        for row in (blocks.get("vocabulario") or {}).get(key) or []:
            dest = (row.get("destino") or "vocabulario").strip()
            if dest == "evidencia":
                bad_destino.append(
                    f"vocab←evidencia:{row.get('fonte')}|{row.get('key')}|{row.get('termo')}"
                )
            sk = f"{row.get('fonte')}|{row.get('key')}"
            if row.get("key"):
                vocab_keys.add(sk)
            elif row.get("termo"):
                vocab_keys.add(f"termo|{str(row['termo']).casefold()}")

    evid = blocks.get("evidencia_delimitacao") or {}
    for key in (
        "exclude",
        "atributo",
        "oposicao",
        "vizinha",
    ):
        for row in evid.get(key) or []:
            dest = (row.get("destino") or "evidencia").strip()
            if dest == "vocabulario":
                bad_destino.append(
                    f"evid←vocabulario:{row.get('fonte')}|{row.get('key')}|{row.get('termo')}"
                )
            if row.get("key"):
                evid_keys.add(f"{row.get('fonte')}|{row.get('key')}")
            elif row.get("termo"):
                evid_keys.add(f"termo|{str(row['termo']).casefold()}")

    overlap_keys = sorted(vocab_keys & evid_keys)
    if bad_destino:
        return False, f"destino incorrecto: {bad_destino[:12]}"
    if overlap_keys:
        return False, f"mesmo registo em ambos os blocos: {overlap_keys[:12]}"
    return True, "registos disjuntos (lemas podem repetir-se por polissemia)"


def render_blocks_markdown(blocks: dict[str, Any]) -> str:
    v = blocks.get("vocabulario") or {}
    e = blocks.get("evidencia_delimitacao") or {}
    L: list[str] = []
    ap = L.append
    ap(f"# Blocos de exportação — `{blocks.get('class_id')}`")
    ap("")
    ap("## Vocabulário (SKOS-XL)")
    ap("")
    pref = (v.get("prefLabel") or {}).get("termo") or "—"
    ap(f"- **prefLabel** (`skosxl:prefLabel` / `skos:prefLabel`): **{pref}**")
    alts = [r.get("termo") for r in (v.get("altLabel") or []) if r.get("termo")]
    ap(f"- **altLabel** (`skosxl:altLabel` ← UF): {', '.join(alts) or '—'}")
    rts = [r.get("termo") for r in (v.get("termoRelacionado") or []) if r.get("termo")]
    ap(
        f"- **termoRelacionado** (`tex:termoRelacionado` ← RT): "
        f"{', '.join(rts) or '—'}"
    )
    ap("")
    ap("## Evidência de delimitação (não serializada)")
    ap("")
    ap(EVIDENCE_NOTE)
    ap("")
    ap(f"- **Âncora ILI:** {', '.join(e.get('ancora_ili') or []) or '—'}")
    ap(f"- **exclude:** {_brief_exclude(e.get('exclude') or [])}")
    ap(
        f"- **material de contraste (auto):** "
        f"{_brief_auto(e.get('material_contraste_auto') or [])}"
    )
    ap(
        f"- **similar_to (auto):** "
        f"{_brief_auto(e.get('vizinhos_similar_to_auto') or [])}"
    )
    ap(f"- **atributo:** {_brief_terms(e.get('atributo') or [])}")
    ap(f"- **oposicao:** {_brief_terms(e.get('oposicao') or [])}")
    ap(f"- **vizinha:** {_brief_vizinha(e.get('vizinha') or [])}")
    ap("")
    return "\n".join(L)


def _brief_exclude(rows: list[dict]) -> str:
    bits = []
    for r in rows:
        ili = r.get("ili") or "—"
        mems = ", ".join(r.get("membros") or []) or r.get("termo") or r.get("key")
        bits.append(f"{mems} ({ili})")
    return "; ".join(bits) if bits else "—"


def _brief_auto(rows: list[dict]) -> str:
    if not rows:
        return "—"
    return ", ".join(
        f"{r.get('termo')} [{r.get('fonte')}]" for r in rows if r.get("termo")
    )


def _brief_terms(rows: list[dict]) -> str:
    if not rows:
        return "—"
    out = []
    for r in rows:
        t = r.get("termo") or ", ".join(r.get("membros") or []) or r.get("key")
        out.append(str(t))
    return ", ".join(out)


def _brief_vizinha(rows: list[dict]) -> str:
    if not rows:
        return "—"
    bits = []
    for r in rows:
        t = r.get("termo") or ", ".join(r.get("membros") or []) or "?"
        rem = r.get("classe_remissao") or "—"
        bits.append(f"{t} → {rem}")
    return "; ".join(bits)


def write_export_blocks(
    ws: ClassWorkspace,
    dest_dir: Optional[Path] = None,
) -> dict[str, Any]:
    """Write sibling JSON+MD for blocks A/B next to (or into) FINAL_RESULTS."""
    blocks = build_export_blocks(ws)
    ok, evidence = assert_blocks_disjoint(blocks)
    blocks["assertions"] = [{
        "id": "T12",
        "text": (
            "Nenhum item do bloco de evidência figura no bloco de "
            "vocabulário, e vice-versa."
        ),
        "passed": ok,
        "evidence": evidence,
    }]
    folder = Path(dest_dir) if dest_dir else ws.final_results
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"{ws.class_id}.blocos"
    json_path = folder / f"{stem}.json"
    md_path = folder / f"{stem}.md"
    json_path.write_text(
        json.dumps(blocks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md_path.write_text(render_blocks_markdown(blocks), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path), "t12_ok": ok}


def append_t12_to_concordance(
    json_path: Path, blocks_info: dict[str, Any]
) -> None:
    """Attach T12 to the LexWarrant concordance JSON (+ MD assertions table)."""
    if not json_path.exists():
        return
    try:
        doc = json.loads(json_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    t12 = {
        "id": "T12",
        "text": (
            "Nenhum item do bloco de evidência figura no bloco de "
            "vocabulário, e vice-versa."
        ),
        "passed": bool(blocks_info.get("t12_ok")),
        "evidence": (
            "blocos A/B disjuntos"
            if blocks_info.get("t12_ok")
            else f"ver {blocks_info.get('json')}"
        ),
    }
    asserts = [a for a in (doc.get("assertions") or []) if a.get("id") != "T12"]
    asserts.append(t12)
    doc["assertions"] = asserts
    doc["all_passed"] = all(a.get("passed") or a.get("pass") for a in asserts)
    json_path.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    md_path = json_path.with_suffix(".md")
    if not md_path.exists():
        return
    text = md_path.read_text(encoding="utf-8")
    if "| T12 |" in text:
        return
    mark = "PASS ✅" if t12["passed"] else "FAIL ❌"
    line = f"| T12 | {t12['text']} | {mark} | {t12['evidence']} |\n"
    if "## Asserções" in text:
        md_path.write_text(text.rstrip() + "\n" + line, encoding="utf-8")


def skos_serializable_terms(blocks: dict[str, Any]) -> set[str]:
    """Terms that may appear in Turtle/SKOS output (Bloco A only)."""
    v = blocks.get("vocabulario") or {}
    out: set[str] = set()
    pref = (v.get("prefLabel") or {}).get("termo")
    if pref:
        out.add(str(pref).casefold())
    for key in ("altLabel", "termoRelacionado"):
        for row in v.get(key) or []:
            if row.get("termo"):
                out.add(str(row["termo"]).casefold())
    return out


def evidence_terms(blocks: dict[str, Any]) -> set[str]:
    e = blocks.get("evidencia_delimitacao") or {}
    out: set[str] = set()
    for key in (
        "exclude",
        "material_contraste_auto",
        "vizinhos_similar_to_auto",
        "atributo",
        "oposicao",
        "vizinha",
    ):
        for row in e.get(key) or []:
            if row.get("termo"):
                out.add(str(row["termo"]).casefold())
            for m in row.get("membros") or []:
                out.add(str(m).casefold())
    return out
