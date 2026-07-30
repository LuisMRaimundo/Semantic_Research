"""Publishable SKOS / OWL concept model (cross-class, CILI-aware).

Writes per-class ``CONCEPT.ttl`` into FINAL_RESULTS and a registry
``data/concepts/registry.ttl`` aggregating all classes.

SKOS discipline (audit / Global WordNet practice)
-------------------------------------------------
* ``skos:exactMatch`` is reserved for at most **one** primary CILI pivot —
  a PULO UF sense with an official ``i…`` id. It must NOT list every ILI
  harvested during research (excludes, RT, Onto inventory, weak Onto→ILI).
* Additional UF PULO CILIs → ``skos:closeMatch`` (review; not interchangeable).
* RT CILIs → ``skos:relatedMatch``.
* Exclude lemmas → ``skos:hiddenLabel`` only (never ILI match links).
* Onto.PT UF lemmas → ``skos:altLabel`` without inventing CILI links.
* Inventory of other resolved CILIs (if any) stays in JSON under
  ``ili_inventory`` — not as SKOS matches.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .normalize import normalize_word, pretty_word
from .settings import DATA_DIR, ROOT
from .workspace import ClassWorkspace

_SAFE = re.compile(r"[^A-Za-z0-9_\-]+")
CILI_URI_BASE = "http://globalwordnet.org/ili/"


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


def _ili_uri(ili: str) -> Optional[str]:
    s = (ili or "").strip()
    if s.startswith("oewn-ili:") or s.startswith("ili:") or s.startswith("cili:"):
        s = s.rsplit(":", 1)[-1]
    if s.startswith("i") and s[1:].isdigit() and not s[1:].startswith("0"):
        return f"{CILI_URI_BASE}{s}"
    if s.startswith("i") and s[1:].isdigit():
        return f"{CILI_URI_BASE}{s}"
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


def build_class_concept_graph(ws: ClassWorkspace) -> dict[str, Any]:
    """Collect prefLabel, UF/RT lemmas, disciplined CILI matches, excludes."""
    from . import decisions as decmod
    from .engines import cili_api

    _, _, resolve, _ = cili_api()
    meta = ws.load_meta()
    dec = decmod.load_decisions(ws.decisions_json)
    pref = (meta.get("pref_label") or ws.class_id).strip()
    axis = (meta.get("axis") or "").strip()

    uf: list[dict[str, Any]] = []
    rt: list[dict[str, Any]] = []
    excl: list[dict[str, Any]] = []

    # Disciplined CILI buckets (never dump excludes into matches)
    uf_pulo_cilis: list[str] = []      # all distinct PULO UF CILIs
    related_cili: list[str] = []       # RT with CILI
    ili_inventory: list[dict[str, Any]] = []  # audit only

    for sense in dec.get("senses") or []:
        decision = (sense.get("decision") or "").strip()
        source = (sense.get("source") or "").lower()
        members = [pretty_word(m) for m in (sense.get("members") or []) if m]
        raw_ili = sense.get("cili") or sense.get("ili") or ""
        cid = _resolve_cili(str(raw_ili), resolve) if raw_ili else None
        # Only resolve bare CILI / pwn / legacy keys for *admitted* senses.
        # Excludes must not contribute SKOS matches (even if key is ili-30-…).
        if not cid and decision in ("UF", "RT"):
            key = str(sense.get("key") or sense.get("pwn_id") or "")
            cid = _resolve_cili(key, resolve) if key else None

        row = {
            "members": members,
            "source": sense.get("source"),
            "ili": cid,
            "gloss": sense.get("gloss") or "",
            "key": sense.get("key"),
        }
        if decision == "UF":
            uf.append(row)
            if cid and source == "pulo":
                if cid not in uf_pulo_cilis:
                    uf_pulo_cilis.append(cid)
                ili_inventory.append({
                    "cili": cid, "role": "uf_pulo", "key": sense.get("key"),
                })
            elif cid:
                ili_inventory.append({
                    "cili": cid, "role": f"uf_{source or 'other'}",
                    "key": sense.get("key"),
                    "note": "not used as skos:exactMatch",
                })
        elif decision == "RT":
            rt.append(row)
            if cid:
                if cid not in related_cili and cid not in uf_pulo_cilis:
                    related_cili.append(cid)
                ili_inventory.append({
                    "cili": cid, "role": "rt", "key": sense.get("key"),
                })
        elif decision == "exclude":
            excl.append(row)
            # deliberately no CILI match / inventory promotion

    for m in dec.get("manual_terms") or []:
        term = pretty_word(m.get("term") or m.get("lemma") or "")
        if not term:
            continue
        st = (m.get("status") or m.get("decision") or "UF").strip()
        row = {
            "members": [term], "source": "manual", "ili": None,
            "gloss": "", "key": term,
        }
        if st == "RT":
            rt.append(row)
        elif st != "exclude":
            uf.append(row)

    # Publish rule: exactMatch only when exactly one PULO UF CILI
    if len(uf_pulo_cilis) == 1:
        exact = list(uf_pulo_cilis)
        close_cili: list[str] = []
    else:
        exact = []
        close_cili = list(uf_pulo_cilis)

    return {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": axis,
        "uf": uf,
        "rt": rt,
        "exclude": excl,
        # Back-compat key: only SKOS-match ILIs (not the old dump of all)
        "ilis": exact + [c for c in close_cili if c not in exact],
        "cili_exact": exact,
        "cili_close": close_cili,
        "cili_related": related_cili,
        "ili_inventory": ili_inventory,
        "skos_policy": (
            "skos:exactMatch ≤1 primary PULO UF CILI; "
            "extra UF PULO → closeMatch; RT → relatedMatch; "
            "excludes never linked as matches; Onto lemmas = altLabel only."
        ),
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def render_skos_owl(
    graph: dict[str, Any],
    *,
    base_ns: str = "http://semantic-research.local/concept/",
) -> str:
    """Render a class as owl:Class + skos:Concept with disciplined CILI matches."""
    cid = graph["class_id"]
    local = _slug(cid)
    pref = _ttl_escape(graph.get("pref_label") or cid)
    axis = _ttl_escape(graph.get("axis") or "")

    preds: list[str] = [
        f'    skos:prefLabel "{pref}"@pt',
    ]
    if axis:
        preds.append(f'    skos:scopeNote "{axis}"@pt')
    preds.append(f'    dct:identifier "{_ttl_escape(cid)}"')
    preds.append(
        f'    skos:editorialNote "{_ttl_escape(graph.get("skos_policy") or "")}"@en'
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

    seen_alt: set[str] = set()
    for row in graph.get("uf") or []:
        for m in row.get("members") or []:
            n = normalize_word(m)
            if not n or n == normalize_word(pref) or n in seen_alt:
                continue
            seen_alt.add(n)
            preds.append(f'    skos:altLabel "{_ttl_escape(m)}"@pt')

    for row in graph.get("rt") or []:
        for m in row.get("members") or []:
            if m:
                preds.append(
                    f'    skos:related [ a skos:Concept ; '
                    f'skos:prefLabel "{_ttl_escape(m)}"@pt ]'
                )

    for row in graph.get("exclude") or []:
        for m in row.get("members") or []:
            if m:
                preds.append(f'    skos:hiddenLabel "{_ttl_escape(m)}"@pt')

    n_uf = len(graph.get("uf") or [])
    n_rt = len(graph.get("rt") or [])
    preds.append(
        f'    rdfs:comment "UF senses={n_uf}; RT={n_rt}; '
        f'exactCILI={len(graph.get("cili_exact") or [])}; '
        f'closeCILI={len(graph.get("cili_close") or [])}; '
        f'relatedCILI={len(graph.get("cili_related") or [])}"@en'
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
        f"# Concept model — {cid}",
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
        "n_uf": len(graph.get("uf") or []),
        "n_rt": len(graph.get("rt") or []),
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
        "schema": "semantic_research.concept_registry/2",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(ROOT),
        "classes": ClassWorkspace.list_classes(),
        "registry_ttl": str(path),
        "skos_policy": (
            "exactMatch≤1 PULO UF CILI; closeMatch/relatedMatch for other "
            "admitted CILIs; excludes never matched"
        ),
    }
    (reg_dir / "registry.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path
