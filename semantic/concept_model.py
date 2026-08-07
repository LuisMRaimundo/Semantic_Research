"""Publishable SKOS / OWL concept model (cross-class, CILI-aware).

Writes per-class ``CONCEPT.ttl`` into FINAL_RESULTS and a registry
``data/concepts/registry.ttl`` aggregating all classes.

SKOS discipline (audit / Global WordNet practice)
-------------------------------------------------
* ``skos:exactMatch`` / ``closeMatch`` / ``relatedMatch`` are emitted **only**
  from explicit ``concept_mapping`` adjudication — never auto-filled from a
  formally resolved PULO UF/RT CILI (formal ≈≠ semantic).
* Harvested CILIs stay in ``ili_inventory`` / ``excluded_cili`` for audit.
* Onto.PT group co-members are **not** automatic ``skos:altLabel``.
* ``skos:prefLabel``, ``altLabel`` and ``hiddenLabel`` are mutually disjoint;
  excludes use ``sr:excludedCandidate``, not ``skos:hiddenLabel``.
* CILI URI namespace: ``http://ili.globalwordnet.org/ili/``.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .normalize import normalize_word, pretty_word
from .settings import DATA_DIR, ROOT
from .workspace import ClassWorkspace

log = logging.getLogger(__name__)

_SAFE = re.compile(r"[^A-Za-z0-9_\-]+")


def _cili_uri_base() -> str:
    try:
        from .engines import load_identifiers
        return load_identifiers().CILI_URI_BASE
    except Exception:  # noqa: BLE001
        return "http://ili.globalwordnet.org/ili/"

_KNOWN_EN = frozenset({
    "dissimilar", "decay", "decomposition", "compound", "composite",
    "combination", "construction", "mixture", "heterogeneous",
})


def _slug(text: str) -> str:
    s = _SAFE.sub("_", (text or "").strip())
    return s.strip("_") or "x"


def _ttl_escape(text: str) -> str:
    return (
        (text or "")
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", " ")
        .replace("\r", "")
    )


def label_lang_tag(lemma: str) -> str:
    """BCP 47 tag for a lexical form (pt-PT default; en / pt-BR when clear)."""
    t = (lemma or "").strip()
    if not t:
        return "pt-PT"
    low = t.casefold()
    if low in _KNOWN_EN:
        return "en"
    # Brazilian orthography of common lemmas (circumflex vs European acute)
    if low in {"heterogêneo", "heterogênea"}:
        return "pt-BR"
    return "pt-PT"


def _ili_uri(ili: str) -> Optional[str]:
    s = (ili or "").strip()
    if s.startswith("oewn-ili:") or s.startswith("ili:") or s.startswith("cili:"):
        s = s.rsplit(":", 1)[-1]
    if "ili.globalwordnet.org/ili/" in s or "globalwordnet.org/ili/" in s:
        s = s.rstrip("/").rsplit("/", 1)[-1]
    if s.startswith("i") and s[1:].isdigit():
        return f"{_cili_uri_base()}{s}"
    return None


def _resolve_cili(raw: str, resolve) -> Optional[str]:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        from .engines import load_identifiers
        cid = load_identifiers().try_normalize_cili_id(s)
        if cid:
            return cid
    except Exception:  # noqa: BLE001
        pass
    try:
        return resolve(s)
    except Exception:  # noqa: BLE001
        return None


def _mapping_block(meta: dict[str, Any], dec: dict[str, Any]) -> dict[str, Any]:
    """Explicit concept_mapping from class.json or decisions (adjudication)."""
    cm = meta.get("concept_mapping")
    if not isinstance(cm, dict):
        cm = dec.get("concept_mapping")
    return dict(cm) if isinstance(cm, dict) else {}


def _as_cili_list(raw: Any) -> list[str]:
    out: list[str] = []
    for item in raw or []:
        if isinstance(item, dict):
            cid = str(item.get("cili") or item.get("ili") or "").strip()
        else:
            cid = str(item or "").strip()
        if cid.startswith(("oewn-ili:", "ili:", "cili:")):
            cid = cid.rsplit(":", 1)[-1]
        if cid.startswith("i") and cid[1:].isdigit() and cid not in out:
            out.append(cid)
    return out


def _as_excluded_cili(raw: Any) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in raw or []:
        if isinstance(item, dict):
            cid = str(item.get("cili") or item.get("ili") or "").strip()
            reason = str(item.get("reason") or item.get("motivo") or "").strip()
        else:
            cid = str(item or "").strip()
            reason = ""
        if cid.startswith(("oewn-ili:", "ili:", "cili:")):
            cid = cid.rsplit(":", 1)[-1]
        if not (cid.startswith("i") and cid[1:].isdigit()) or cid in seen:
            continue
        seen.add(cid)
        out.append({"cili": cid, "reason": reason})
    return out


def build_class_concept_graph(ws: ClassWorkspace) -> dict[str, Any]:
    """Collect inventory + adjudicated SKOS matches (no auto CILI promotion)."""
    from . import decisions as decmod
    from .engines import cili_api

    _, _, resolve, _ = cili_api()
    meta = ws.load_meta()
    dec = decmod.load_decisions(ws.decisions_json)
    pref = (meta.get("pref_label") or ws.class_id).strip()
    axis = (meta.get("axis") or "").strip()
    cm = _mapping_block(meta, dec)
    focus = {
        normalize_word(x)
        for x in (meta.get("focus_stems") or [])
        if x
    }
    focus.add(normalize_word(pref))

    uf: list[dict[str, Any]] = []
    rt: list[dict[str, Any]] = []
    excl: list[dict[str, Any]] = []
    ili_inventory: list[dict[str, Any]] = []
    excluded_cili = _as_excluded_cili(cm.get("excluded_cili"))
    excluded_ids = {e["cili"] for e in excluded_cili}

    for sense in dec.get("senses") or []:
        decision = (sense.get("decision") or "").strip()
        source = (sense.get("source") or "").lower()
        members = [pretty_word(m) for m in (sense.get("members") or []) if m]
        raw_ili = sense.get("cili") or sense.get("ili") or ""
        cid = _resolve_cili(str(raw_ili), resolve) if raw_ili else None
        if not cid and decision in ("UF", "RT", "exclude"):
            key = str(sense.get("key") or sense.get("pwn_id") or "")
            cid = _resolve_cili(key, resolve) if key else None

        row = {
            "members": members,
            "source": sense.get("source"),
            "ili": cid,
            "gloss": sense.get("gloss") or "",
            "key": sense.get("key"),
        }
        if decision == "exclude":
            # Exclusion targets the sense/record, not every lemma token in the group
            row["exclusion_scope"] = "record_or_sense_not_lemma"
            validated_skip = {
                normalize_word(x)
                for x in (cm.get("validated_alt_labels") or [])
                if x
            }
            validated_skip |= focus
            row["members"] = [
                m for m in members if normalize_word(m) not in validated_skip
            ]
            row["members_omitted_focal"] = [
                m for m in members if normalize_word(m) in validated_skip
            ]
        if decision == "UF":
            if source == "onto":
                # Same focus-stem filter applied by _vocab_alt_labels at
                # render time — declared here on the row, never silent.
                row["members_dropped_focus_filter"] = [
                    m for m in members if normalize_word(m) not in focus
                ]
            uf.append(row)
            if cid:
                role = "uf_pulo_candidate" if source == "pulo" else f"uf_{source or 'other'}_candidate"
                ili_inventory.append({
                    "cili": cid, "role": role, "key": sense.get("key"),
                    "note": "inventory only — not auto skos:exactMatch",
                })
                if cid in excluded_ids:
                    ili_inventory[-1]["note"] = "excluded by concept_mapping"
        elif decision == "RT":
            rt.append(row)
            if cid:
                ili_inventory.append({
                    "cili": cid, "role": "rt_candidate", "key": sense.get("key"),
                    "note": "inventory only — not auto skos:relatedMatch",
                })
                if cid in excluded_ids:
                    ili_inventory[-1]["note"] = "excluded by concept_mapping"
        elif decision == "exclude":
            excl.append(row)
            if cid:
                ili_inventory.append({
                    "cili": cid,
                    "role": "exclude_sense",
                    "key": sense.get("key"),
                    "note": "evidence only — not vocabulary CILI",
                })
                # Adjudicated domain exclusions stay in concept_mapping;
                # do not auto-inflate RDF excludedCili from every PULO exclude.

    stipulated_terms: list[dict[str, Any]] = []
    for m in dec.get("manual_terms") or []:
        term = pretty_word(m.get("term") or m.get("lemma") or "")
        if not term:
            continue
        st = (m.get("status") or m.get("decision") or "").strip()
        if not st:
            # No silent default to UF (same policy as compile_specs):
            # a status-less manual term is a stipulation, never vocabulary.
            entry = {
                "term": term,
                "provenance": list(m.get("provenance") or m.get("guarantee") or []),
                "definition": m.get("definition") or "",
                "structural": m.get("structural") or "",
                "note": "manual_terms entry without status — not adjudicated; "
                        "kept for audit only",
            }
            stipulated_terms.append(entry)
            log.warning(
                "concept_model [%s]: manual_terms «%s» sem status — "
                "excluído de skos:altLabel (proveniência: %s)",
                ws.class_id, term,
                ", ".join(entry["provenance"]) or "—",
            )
            continue
        row = {
            "members": [term], "source": "manual", "ili": None,
            "gloss": "", "key": term,
        }
        if st == "RT":
            rt.append(row)
        elif st != "exclude":
            uf.append(row)

    # Adjudicated SKOS matches only (empty list is intentional null mapping)
    if "cili_exact" in cm or "cili_close" in cm or "cili_related" in cm:
        exact = [c for c in _as_cili_list(cm.get("cili_exact")) if c not in excluded_ids]
        close_cili = [c for c in _as_cili_list(cm.get("cili_close")) if c not in excluded_ids]
        related_cili = [
            c for c in _as_cili_list(cm.get("cili_related")) if c not in excluded_ids
        ]
    else:
        exact, close_cili, related_cili = [], [], []

    mapping_status = str(
        cm.get("mapping_status")
        or ("validated_cili" if (exact or close_cili or related_cili) else "no_validated_cili")
    )

    validated_alts = [
        pretty_word(x) for x in (cm.get("validated_alt_labels") or []) if x
    ]

    discovery = {
        "uf_candidates": uf,
        "rt_candidates": rt,
        "exclude_records": excl,
        "note": (
            "Discovery / raw adjudication evidence — NOT validated vocabulary. "
            "Validated labels live only in validated_alt_labels; "
            "SKOS matches only in cili_exact/close/related."
        ),
    }
    return {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": axis,
        "discovery_evidence": discovery,
        "stipulated_terms": stipulated_terms,
        "cili_exact": exact,
        "cili_close": close_cili,
        "cili_related": related_cili,
        "excluded_cili": excluded_cili,
        "validated_alt_labels": validated_alts,
        "focus_stems": sorted(focus - {""}),
        "ili_inventory": ili_inventory,
        "mapping_status": mapping_status,
        "skos_policy": (
            "SKOS matches only from concept_mapping adjudication; "
            "discovery_evidence.uf/rt_candidates are not validated altLabels; "
            "excludes → sr:excludedCandidate (sense scope, not every lemma); "
            "pref/alt/hidden mutually disjoint."
        ),
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def discovery_lists(graph: dict[str, Any]) -> tuple[list, list, list]:
    """(uf_candidates, rt_candidates, exclude_records) from CONCEPT graph."""
    disc = graph.get("discovery_evidence")
    if isinstance(disc, dict):
        return (
            list(disc.get("uf_candidates") or []),
            list(disc.get("rt_candidates") or []),
            list(disc.get("exclude_records") or []),
        )
    # Older CONCEPT.json only (pre-alias cleanup)
    return (
        list(graph.get("uf") or []),
        list(graph.get("rt") or []),
        list(graph.get("exclude") or []),
    )


def _vocab_alt_labels(graph: dict[str, Any]) -> list[str]:
    """Conservative altLabels: validated list, else PULO UF members only."""
    pref_n = normalize_word(graph.get("pref_label") or "")
    validated = [pretty_word(x) for x in (graph.get("validated_alt_labels") or []) if x]
    if validated:
        return [m for m in validated if normalize_word(m) != pref_n]

    focus = {normalize_word(x) for x in (graph.get("focus_stems") or []) if x}
    out: list[str] = []
    seen: set[str] = set()
    excluded = {
        e.get("cili") for e in (graph.get("excluded_cili") or [])
        if isinstance(e, dict) and e.get("cili")
    }
    uf_rows, _, _ = discovery_lists(graph)
    for row in uf_rows:
        ili = row.get("ili")
        if ili and ili in excluded:
            continue
        src = (row.get("source") or "").lower()
        members = list(row.get("members") or [])
        if src == "onto":
            # Attestation only: keep members that are focus stems, not co-hyponyms
            pick = [m for m in members if normalize_word(m) in focus]
        else:
            pick = members
        for m in pick:
            n = normalize_word(m)
            if not n or n == pref_n or n in seen:
                continue
            seen.add(n)
            out.append(m)
    return out


def render_skos_owl(
    graph: dict[str, Any],
    *,
    base_ns: str = "http://semantic-research.local/concept/",
) -> str:
    """Render a class as owl:Class + skos:Concept (plain SKOS, not SKOS-XL)."""
    cid = graph["class_id"]
    local = _slug(cid)
    pref = _ttl_escape(graph.get("pref_label") or cid)
    axis = _ttl_escape(graph.get("axis") or "")
    pref_lang = label_lang_tag(graph.get("pref_label") or cid)

    preds: list[str] = [
        f'    skos:prefLabel "{pref}"@{pref_lang}',
    ]
    if axis:
        preds.append(f'    skos:scopeNote "{axis}"@pt-PT')
    preds.append(f'    dct:identifier "{_ttl_escape(cid)}"')
    preds.append(
        f'    skos:editorialNote "{_ttl_escape(graph.get("skos_policy") or "")}"@en'
    )
    preds.append(
        f'    sr:mappingStatus "{_ttl_escape(graph.get("mapping_status") or "")}"'
    )

    for ili in graph.get("cili_exact") or []:
        u = _ili_uri(ili)
        if u:
            preds.append(f"    skos:exactMatch <{u}>")

    for ili in graph.get("cili_close") or []:
        u = _ili_uri(ili)
        if u:
            preds.append(f"    skos:closeMatch <{u}>")

    for ili in graph.get("cili_related") or []:
        u = _ili_uri(ili)
        if u:
            preds.append(f"    skos:relatedMatch <{u}>")

    alt_forms = _vocab_alt_labels(graph)
    seen_alt = {normalize_word(m) for m in alt_forms}
    pref_n = normalize_word(graph.get("pref_label") or "")
    seen_alt.add(pref_n)
    for m in alt_forms:
        lang = label_lang_tag(m)
        preds.append(f'    skos:altLabel "{_ttl_escape(m)}"@{lang}')

    # Do not expand RT members into blank skos:related concepts (Onto noise).

    uf_rows, rt_rows, excl_rows = discovery_lists(graph)
    # Only PULO exclude lemmas enter RDF evidence (Onto group dumps stay in JSON)
    for row in excl_rows:
        src_raw = str(row.get("source") or "").lower()
        if src_raw == "onto":
            continue
        src = _ttl_escape(str(row.get("source") or ""))
        reason = _ttl_escape((row.get("gloss") or "")[:180])
        for m in row.get("members") or []:
            if not m:
                continue
            n = normalize_word(m)
            if n in seen_alt or n == pref_n:
                # SKOS integrity: never also emit as a label of the concept
                continue
            lang = label_lang_tag(m)
            preds.append(
                "    sr:excludedCandidate ["
                f' rdf:value "{_ttl_escape(m)}"@{lang} ;'
                f' dct:source "{src}" ;'
                f' sr:exclusionReason "{reason or "exclude"}"'
                " ]"
            )

    for ex in graph.get("excluded_cili") or []:
        cid_ex = ex.get("cili") if isinstance(ex, dict) else str(ex)
        reason = _ttl_escape(
            (ex.get("reason") if isinstance(ex, dict) else "") or "domain mismatch"
        )
        u = _ili_uri(str(cid_ex or ""))
        if u:
            preds.append(
                "    sr:excludedCili ["
                f" sr:cili <{u}> ;"
                f' sr:exclusionReason "{reason}"'
                " ]"
            )

    preds.append(
        f'    rdfs:comment "UF senses={len(uf_rows)}; RT={len(rt_rows)}; '
        f'exactCILI={len(graph.get("cili_exact") or [])}; '
        f'closeCILI={len(graph.get("cili_close") or [])}; '
        f'relatedCILI={len(graph.get("cili_related") or [])}; '
        f'mapping={graph.get("mapping_status") or ""}"@en'
    )

    joined = " ;\n".join(preds) + " ."
    return "\n".join([
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dct: <http://purl.org/dc/terms/> .",
        f"@prefix sr: <{base_ns}> .",
        "",
        f"# Concept model (plain SKOS, not SKOS-XL) — {cid}",
        f"# generated {graph.get('generated')}",
        f"# policy: {graph.get('skos_policy')}",
        "",
        f"sr:{local} a owl:Class, skos:Concept ;",
        joined,
        "",
    ])


def publish_class_concept(
    class_id: str,
    *,
    dest_dir: Optional[Path] = None,
    update_registry: bool = True,
) -> dict[str, Any]:
    ws = ClassWorkspace.open(class_id)
    graph = build_class_concept_graph(ws)
    ttl = render_skos_owl(graph)
    folder = Path(dest_dir) if dest_dir else ws.final_results
    folder.mkdir(parents=True, exist_ok=True)
    ttl_path = folder / "CONCEPT.ttl"
    json_path = folder / "CONCEPT.json"
    ttl_path.write_text(ttl, encoding="utf-8")
    json_path.write_text(
        json.dumps(graph, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    out: dict[str, Any] = {
        "class_id": class_id,
        "ttl": str(ttl_path),
        "json": str(json_path),
        "n_exact": len(graph.get("cili_exact") or []),
        "n_close": len(graph.get("cili_close") or []),
        "n_related": len(graph.get("cili_related") or []),
        "n_uf": len((graph.get("discovery_evidence") or {}).get("uf_candidates") or []),
        "n_rt": len((graph.get("discovery_evidence") or {}).get("rt_candidates") or []),
        "mapping_status": graph.get("mapping_status"),
    }
    if update_registry:
        out["registry"] = str(update_global_registry())
    return out


def update_global_registry() -> Path:
    """Rebuild data/concepts/registry.ttl from every class."""
    reg_dir = DATA_DIR / "concepts"
    reg_dir.mkdir(parents=True, exist_ok=True)
    chunks = [
        "@prefix owl: <http://www.w3.org/2002/07/owl#> .",
        "@prefix skos: <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dct: <http://purl.org/dc/terms/> .",
        "@prefix sr: <http://semantic-research.local/concept/> .",
        "",
        "sr:Scheme a skos:ConceptScheme ;",
        '    dct:title "Semantic Research concept registry"@en ;',
        f'    dct:modified "{datetime.now(timezone.utc).date().isoformat()}" .',
        "",
    ]
    for name in ClassWorkspace.list_classes():
        try:
            ws = ClassWorkspace.open(name)
            graph = build_class_concept_graph(ws)
            ttl = render_skos_owl(graph)
            chunks.append(ttl)
            (reg_dir / f"{_slug(name)}.ttl").write_text(ttl, encoding="utf-8")
        except Exception:  # noqa: BLE001
            continue
    path = reg_dir / "registry.ttl"
    path.write_text("\n".join(chunks), encoding="utf-8")
    index = {
        "schema": "semantic_research.concept_registry/3",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(ROOT),
        "classes": ClassWorkspace.list_classes(),
        "registry_ttl": str(path),
        "skos_policy": (
            "SKOS matches only from concept_mapping; "
            "no auto exactMatch from PULO CILI resolution"
        ),
    }
    (reg_dir / "registry.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path
