"""OEWN (Open English WordNet) search → facets export for the workbench.

Keeps WordNet in the same PASSO 2 flow as PULO / Onto.PT. Exports land in
``classes/<Class>/exports/*.facets.json`` so the WordNet track / CILI harvest
do not pick up stale bundles from ``WordNet/exports/``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from ..engines import load_oewn_backend
from ..settings import load_config


def _ensure_backend():
    backend = load_oewn_backend()
    cfg = load_config()
    pin = str(cfg.get("oewn") or "oewn:2024")
    if hasattr(backend, "set_oewn_pin"):
        backend.set_oewn_pin(pin, hard=True)
    else:
        if hasattr(backend, "OEWN_PINNED_VERSION"):
            backend.OEWN_PINNED_VERSION = pin  # type: ignore[attr-defined]
        if hasattr(backend, "OEWN_LEXICON"):
            backend.OEWN_LEXICON = None  # type: ignore[attr-defined]
    return backend


def _rel_targets(synsets) -> list[dict]:
    out = []
    for s in synsets or []:
        try:
            out.append({
                "id": s.name(),
                "ili": s.ili(),
                "words": [l.name() for l in s.lemmas()],
                "gloss": s.definition() or "",
            })
        except Exception:  # noqa: BLE001
            continue
    return out


def _lemma_rel_targets(synset, method: str) -> list[dict]:
    """Collect antonym / derivational targets from lemma-level relations."""
    seen: set[str] = set()
    out: list[dict] = []
    for lemma in synset.lemmas():
        try:
            fn = getattr(lemma, method, None)
            related = fn() if callable(fn) else []
        except Exception:  # noqa: BLE001
            related = []
        for other in related or []:
            try:
                ss = other.synset()
                key = ss.name()
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "id": key,
                    "ili": ss.ili(),
                    "words": [other.name()],
                    "gloss": ss.definition() or "",
                })
            except Exception:  # noqa: BLE001
                continue
    return out


def _facet_synset(synset) -> dict[str, Any]:
    return {
        "name": synset.name(),
        "ili": synset.ili(),
        "pos": synset.pos(),
        "definition": synset.definition(),
        "examples": list(synset.examples() or []),
        "lemmas": [l.name() for l in synset.lemmas()],
        "pt_lemmas": list(synset.pt_lemmas() or []),
        "hypernyms": [h.name() for h in synset.hypernyms()],
        "hyponyms": [h.name() for h in synset.hyponyms()],
        "relations": {
            "antonym": _lemma_rel_targets(synset, "antonyms"),
            "derivationally_related_form": _lemma_rel_targets(
                synset, "derivationally_related_forms"
            ),
            "similar_to": _rel_targets(synset.similar_tos()),
            "attribute": _rel_targets(synset.attributes()),
            "also_see": _rel_targets(synset.also_sees()),
        },
    }


class WordNetStore:
    """Search OEWN and build a facets document (no Tk WordNet GUI required)."""

    def export_search(
        self,
        query: str,
        *,
        class_id: str = "",
        pos: Optional[str] = None,
        limit: int = 40,
    ) -> dict[str, Any]:
        backend = _ensure_backend()
        pos_arg = None if not pos or pos in ("", "Todas", "all") else pos
        synsets = list(backend.synsets(query.strip(), pos=pos_arg, lang="eng"))
        if limit:
            synsets = synsets[:limit]
        facets = [_facet_synset(s) for s in synsets]
        n_pt = sum(1 for s in facets if s.get("pt_lemmas"))
        return {
            "type": "oewn_facets",
            "term": query.strip(),
            "pos": pos_arg or "Todas",
            "language": "English",
            "class_id": class_id,
            "generated": datetime.now().isoformat(timespec="seconds"),
            "count": len(facets),
            "facets": ["synsets_relations"],
            "source": {
                "lexicon": "oewn",
                "backend": "wn",
                "alignment": "ILI via translate()",
                "via": "semantic.adapters.wordnet (workbench)",
                "pt_coverage": f"{n_pt}/{len(facets)} synsets com pt_lemmas",
            },
            "synsets": facets,
            "similarity": {"pairs": [], "note": "omitted in workbench search"},
            "hierarchy": {},
            "visualization": {},
        }
