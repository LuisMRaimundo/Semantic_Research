"""Publishable SKOS / OWL concept model (cross-class, ILI-anchored).

Writes per-class ``CONCEPT.ttl`` into FINAL_RESULTS and a registry
``data/concepts/registry.ttl`` aggregating all classes.
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
    if s.startswith("i") and s[1:].isdigit():
        return f"https://globalwordnet.org/ili/{s}"
    return None


def build_class_concept_graph(ws: ClassWorkspace) -> dict[str, Any]:
    """Collect prefLabel, UF/RT lemmas, ILIs, excludes from decisions."""
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
    ilis: set[str] = set()

    for sense in dec.get("senses") or []:
        decision = (sense.get("decision") or "").strip()
        members = [pretty_word(m) for m in (sense.get("members") or []) if m]
        raw_ili = sense.get("ili") or ""
        cid = resolve(str(raw_ili)) if raw_ili else None
        if not cid:
            key = str(sense.get("key") or "")
            cid = resolve(key) if key else None
        if cid:
            ilis.add(cid)
        row = {
            "members": members,
            "source": sense.get("source"),
            "ili": cid,
            "gloss": sense.get("gloss") or "",
            "key": sense.get("key"),
        }
        if decision == "UF":
            uf.append(row)
        elif decision == "RT":
            rt.append(row)
        elif decision == "exclude":
            excl.append(row)

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

    return {
        "class_id": ws.class_id,
        "pref_label": pref,
        "axis": axis,
        "uf": uf,
        "rt": rt,
        "exclude": excl,
        "ilis": sorted(ilis),
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def render_skos_owl(
    graph: dict[str, Any],
    *,
    base_ns: str = "http://semantic-research.local/concept/",
) -> str:
    """Render a class as owl:Class + skos:Concept with ILI exactMatch."""
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

    for ili in graph.get("ilis") or []:
        u = _ili_uri(ili)
        if u:
            preds.append(f"    skos:exactMatch <{u}>")

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
        f'ILI anchors={len(graph.get("ilis") or [])}"@en'
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
        "n_ili": len(graph.get("ilis") or []),
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
        "schema": "semantic_research.concept_registry/1",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "root": str(ROOT),
        "classes": ClassWorkspace.list_classes(),
        "registry_ttl": str(path),
    }
    (reg_dir / "registry.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path
