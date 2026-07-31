"""Human decisions — the only curated artefact researchers must edit."""

from __future__ import annotations

import json
import logging
from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger(__name__)

# PASSO 3 radio choices (UI); vizinha/oposicao are file-only / migration.
DECISIONS_UI = ("UF", "RT", "exclude", "atributo", "")
# All persisted decision/status values (including non-serialisable evidence).
DECISIONS = (
    "UF",
    "RT",
    "exclude",
    "atributo",
    "oposicao",
    "vizinha",
    "",
)
# Legacy value still recognised on load (always migrated away).
_LEGACY_CONTRASTE = "contraste"

VOCABULARIO = frozenset({"UF", "RT"})
EVIDENCIA = frozenset({"exclude", "atributo", "oposicao", "vizinha"})

# Soft flag: set on the in-memory dict when contraste→oposicao ran this load.
_MIGRATION_FLAG = "_migracao_contraste"


def decision_destino(decision: str) -> Optional[str]:
    """Return ``vocabulario`` | ``evidencia`` | None for a decision/status value."""
    d = (decision or "").strip()
    if d in VOCABULARIO:
        return "vocabulario"
    if d in EVIDENCIA:
        return "evidencia"
    return None


def blank_decisions(class_id: str) -> dict[str, Any]:
    return {
        "class_id": class_id,
        "senses": [],
        "terms": [],
        "manual_terms": [],
        "exclude_terms": [],
    }


def migrate_contraste(data: dict[str, Any]) -> dict[str, Any]:
    """Convert every legacy ``contraste`` to ``oposicao`` (in memory).

    No heuristic distinguishes oposicao vs vizinha — reclassification to
    ``vizinha`` is exclusively manual. Sets ``migrado_de`` and
    ``revisao_pendente`` on each converted record. Logs the term list.
    """
    out = deepcopy(data)
    class_id = out.get("class_id") or "?"
    migrated: list[dict[str, str]] = []

    for s in out.get("senses") or []:
        if (s.get("decision") or "").strip() != _LEGACY_CONTRASTE:
            continue
        s["decision"] = "oposicao"
        s["migrado_de"] = _LEGACY_CONTRASTE
        s["revisao_pendente"] = True
        s["destino"] = "evidencia"
        label = ", ".join(s.get("members") or []) or s.get("key") or "?"
        migrated.append({
            "kind": "sense",
            "source": s.get("source") or "",
            "key": s.get("key") or "",
            "label": label,
        })

    for t in out.get("terms") or []:
        if (t.get("status") or "").strip() != _LEGACY_CONTRASTE:
            continue
        t["status"] = "oposicao"
        t["migrado_de"] = _LEGACY_CONTRASTE
        t["revisao_pendente"] = True
        t["destino"] = "evidencia"
        migrated.append({
            "kind": "term",
            "source": "",
            "key": "",
            "label": t.get("term") or "?",
        })

    if migrated:
        out[_MIGRATION_FLAG] = {
            "class_id": class_id,
            "from": _LEGACY_CONTRASTE,
            "to": "oposicao",
            "count": len(migrated),
            "items": migrated,
        }
        labels = [m["label"] for m in migrated]
        log.warning(
            "Migração contraste→oposicao [%s]: %d registo(s) — %s "
            "(revisao_pendente; reclassificar para vizinha só manualmente)",
            class_id,
            len(migrated),
            "; ".join(labels),
        )
    return out


def annotate_destino(data: dict[str, Any]) -> dict[str, Any]:
    """Fill ``destino`` on senses/terms from decision/status (idempotent)."""
    out = deepcopy(data)
    for s in out.get("senses") or []:
        dest = decision_destino(s.get("decision") or "")
        if dest:
            s["destino"] = dest
        else:
            s.pop("destino", None)
    for t in out.get("terms") or []:
        dest = decision_destino(t.get("status") or "")
        if dest:
            t["destino"] = dest
        else:
            t.pop("destino", None)
    return out


def load_decisions(path: Path) -> dict[str, Any]:
    if not path.exists():
        return blank_decisions(path.parent.name)
    raw = json.loads(path.read_text(encoding="utf-8"))
    migrated = migrate_contraste(raw)
    return annotate_destino(migrated)


def decisions_need_disk_backup(data: dict[str, Any]) -> bool:
    """True if this in-memory payload carries a contraste migration to persist."""
    return bool(data.get(_MIGRATION_FLAG))


def backup_decisions_file(path: Path) -> Optional[Path]:
    """Copy ``decisions.json`` → ``decisions.json.bak-YYYYMMDD`` if present."""
    if not path.exists():
        return None
    stamp = date.today().strftime("%Y%m%d")
    bak = path.with_name(f"{path.name}.bak-{stamp}")
    if not bak.exists():
        bak.write_bytes(path.read_bytes())
    return bak


def save_decisions(
    path: Path,
    data: dict[str, Any],
    *,
    backup_if_migrated: bool = True,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = annotate_destino(deepcopy(data))
    if backup_if_migrated and decisions_need_disk_backup(out):
        backup_decisions_file(path)
    # Never persist the soft in-memory migration log key.
    out.pop(_MIGRATION_FLAG, None)
    path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def sense_key(source: str, key: str) -> str:
    return f"{source}|{key}"


def upsert_sense(decisions: dict[str, Any], sense: dict[str, Any]) -> dict[str, Any]:
    """Insert or update a sense card by (source, key)."""
    out = deepcopy(decisions)
    senses = out.setdefault("senses", [])
    src = sense["source"]
    key = sense["key"]
    for i, existing in enumerate(senses):
        if existing.get("source") == src and existing.get("key") == key:
            merged = dict(existing)
            merged.update(sense)
            senses[i] = merged
            return annotate_destino(out)
    senses.append(sense)
    return annotate_destino(out)


def set_decision(
    decisions: dict[str, Any],
    source: str,
    key: str,
    decision: str,
    note: str = "",
) -> dict[str, Any]:
    out = deepcopy(decisions)
    for s in out.get("senses", []):
        if s.get("source") == source and s.get("key") == key:
            s["decision"] = decision
            if note:
                s["note"] = note
            dest = decision_destino(decision)
            if dest:
                s["destino"] = dest
            else:
                s.pop("destino", None)
            return out
    raise KeyError(f"sense not found: {source}|{key}")


def upsert_term(
    decisions: dict[str, Any],
    term: str,
    status: str,
    note: str = "",
    guarantee: Optional[list] = None,
) -> dict[str, Any]:
    out = deepcopy(decisions)
    terms = out.setdefault("terms", [])
    for t in terms:
        if t.get("term") == term:
            t["status"] = status
            if note:
                t["note"] = note
            if guarantee is not None:
                t["guarantee"] = guarantee
            dest = decision_destino(status)
            if dest:
                t["destino"] = dest
            else:
                t.pop("destino", None)
            return out
    terms.append({
        "term": term,
        "status": status,
        "note": note,
        "guarantee": guarantee or ["lexical"],
        **({"destino": decision_destino(status)} if decision_destino(status) else {}),
    })
    return out


def undecided_count(decisions: dict[str, Any]) -> int:
    """Count undecided PULO/ONTO cards only (WordNet is corroboration, not UF/RT)."""
    return sum(
        1 for s in decisions.get("senses", [])
        if (s.get("source") or "").lower() in ("pulo", "onto")
        and not (s.get("decision") or "").strip()
    )


def _pulo_identity(syn: dict[str, Any]) -> dict[str, Any]:
    """Normalise PULO synset identity: pwn30 + optional official CILI."""
    try:
        from .engines import load_identifiers
        ids = load_identifiers()
    except Exception:  # noqa: BLE001
        ids = None
    item = {}
    for raw in syn.get("ili") or []:
        if isinstance(raw, dict):
            item = raw
            break
    if ids is not None:
        ident = ids.from_pulo_to_ili(
            item.get("pwn_id") or item.get("ili_offset") or item.get("cili"),
            synset_offset=syn.get("synset_offset"),
            ili_wn_id=item.get("ili_wn_id"),
            resolve_cili=True,
        )
        # Prefer CILI already present on the export item (from adapter)
        if item.get("cili") and not ident.cili:
            ident.cili = str(item["cili"]).strip()
            ident.mapping_status = item.get("mapping_status") or "official"
        if item.get("pwn_id") and not ident.pwn_id:
            ident.pwn_id = str(item["pwn_id"]).strip()
        cid = ident.cili_id or ident.cili
        return {
            "key": ident.pwn_id or ident.source_synset_id or "",
            "pwn_id": ident.pwn_id,
            "ili": cid,  # bare CILI only (never oewn-ili: CURIE)
            "cili": cid,
            "cili_id": cid,
            "cili_uri": ident.cili_uri or item.get("cili_uri"),
            "source_curie": ident.source_curie or item.get("source_curie"),
            "legacy_omw_ili": ident.legacy_omw_ili or item.get("legacy_omw_ili"),
            "mapping_status": ident.mapping_status,
            "stable": ids.stable_key(
                ident.pwn_id or item.get("ili_offset") or syn.get("synset_offset")
            ),
        }
    # Fallback without identifiers module
    raw = (item.get("ili_offset") or item.get("pwn_id") or "").strip()
    return {
        "key": raw or syn.get("synset_offset") or "",
        "pwn_id": item.get("pwn_id") or raw,
        "ili": item.get("cili"),
        "cili": item.get("cili"),
        "legacy_omw_ili": item.get("legacy_omw_ili"),
        "mapping_status": item.get("mapping_status") or "unverified",
        "stable": raw or syn.get("synset_offset") or "",
    }


def from_pulo_export(
    export: dict[str, Any], existing: Optional[dict] = None
) -> dict[str, Any]:
    """Seed sense cards from a PULO export (keeps prior decisions)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    try:
        from .engines import load_identifiers
        stable = load_identifiers().stable_key
    except Exception:  # noqa: BLE001
        stable = lambda x: str(x or "").strip()  # noqa: E731

    prior_by_stable: dict[str, dict] = {}
    prior_by_sk: dict[str, dict] = {}
    for s in out.get("senses", []):
        if not s.get("source") or not s.get("key"):
            continue
        prior_by_sk[sense_key(s["source"], s["key"])] = s
        prior_by_stable[stable(s.get("pwn_id") or s.get("key") or s.get("ili"))] = s
        if s.get("legacy_omw_ili"):
            prior_by_stable[stable(s["legacy_omw_ili"])] = s

    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        ident = _pulo_identity(syn)
        key = ident["key"]
        if not key:
            continue
        sk = sense_key("pulo", key)
        hit = prior_by_sk.get(sk) or prior_by_stable.get(ident["stable"])
        if hit is not None:
            # Upgrade legacy ili-30 keys / fill CILI when newly resolved
            if (hit.get("key") or "").startswith("ili-30-") and ident.get("pwn_id"):
                hit["key"] = ident["pwn_id"]
                hit["pwn_id"] = ident["pwn_id"]
            if ident.get("cili") and not hit.get("cili"):
                hit["cili"] = ident["cili"]
                hit["cili_id"] = ident.get("cili_id") or ident["cili"]
                hit["ili"] = ident["cili"]
                hit["cili_uri"] = ident.get("cili_uri")
                hit["source_curie"] = ident.get("source_curie")
                hit["mapping_status"] = ident.get("mapping_status") or "official"
            # Strip legacy CURIE-as-primary if still stored
            for fld in ("ili", "cili", "cili_id"):
                val = str(hit.get(fld) or "")
                if val.startswith(("oewn-ili:", "ili:")):
                    hit[fld] = val.rsplit(":", 1)[-1]
            if ident.get("pwn_id") and not hit.get("pwn_id"):
                hit["pwn_id"] = ident["pwn_id"]
            if ident.get("legacy_omw_ili") and not hit.get("legacy_omw_ili"):
                hit["legacy_omw_ili"] = ident["legacy_omw_ili"]
            continue
        senses.append({
            "source": "pulo",
            "key": key,
            "pwn_id": ident.get("pwn_id"),
            "ili": ident.get("cili"),  # bare official CILI only (may be null)
            "cili": ident.get("cili"),
            "cili_id": ident.get("cili_id") or ident.get("cili"),
            "cili_uri": ident.get("cili_uri"),
            "source_curie": ident.get("source_curie"),
            "legacy_omw_ili": ident.get("legacy_omw_ili"),
            "mapping_status": ident.get("mapping_status") or "unverified",
            "local_id": syn.get("synset_offset"),
            "pos": syn.get("pos"),
            "gloss": syn.get("gloss") or "",
            "members": list(syn.get("synonyms") or []),
            "decision": "",
            "note": "",
        })
    out["senses"] = senses
    return out


def from_onto_export(
    export: dict[str, Any], existing: Optional[dict] = None
) -> dict[str, Any]:
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        res = syn.get("resource") or syn.get("res") or ""
        sid = str(syn.get("synset_id") or syn.get("sid") or "")
        key = f"{res}:{sid}" if res and sid else sid
        if not key:
            continue
        sk = sense_key("onto", key)
        if sk in prior:
            continue
        members = []
        for m in syn.get("members") or []:
            if isinstance(m, dict):
                members.append(m.get("word") or "")
            else:
                members.append(str(m))
        senses.append({
            "source": "onto",
            "key": key,
            "ili": None,
            "local_id": key,
            "pos": syn.get("pos"),
            "gloss": syn.get("gloss") or "",
            "members": [m for m in members if m],
            "decision": "",
            "note": "",
        })
    out["senses"] = senses
    return out


def from_papel_export(
    export: dict[str, Any], existing: Optional[dict] = None
) -> dict[str, Any]:
    """Seed PAPEL discovery cards (dictionary relations — never LexWarrant admit)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        res = syn.get("resource") or "papel35"
        sid = str(syn.get("synset_id") or syn.get("sid") or "")
        key = f"{res}:{sid}" if res and sid else sid
        if not key:
            continue
        sk = sense_key("papel", key)
        if sk in prior:
            continue
        members = []
        for m in syn.get("members") or []:
            if isinstance(m, dict):
                members.append(m.get("word") or "")
            else:
                members.append(str(m))
        rel = (syn.get("relations") or {}).get("papel_rel") or ""
        senses.append({
            "source": "papel",
            "key": key,
            "ili": None,
            "local_id": key,
            "pos": syn.get("pos"),
            "gloss": syn.get("gloss") or (f"PAPEL {rel}" if rel else "PAPEL"),
            "members": [m for m in members if m],
            "decision": "",
            "note": "discovery: PAPEL 3.5",
        })
    out["senses"] = senses
    return out


def from_wordnet_export(
    export: dict[str, Any], existing: Optional[dict] = None
) -> dict[str, Any]:
    """Seed read-only OEWN sense cards (corroboration / WordNet track — no UF/RT)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    for syn in export.get("synsets", []):
        ili = (syn.get("ili") or "").strip()
        key = ili or syn.get("name") or ""
        if not key:
            continue
        sk = sense_key("wordnet", key)
        if sk in prior:
            continue
        members = list(syn.get("lemmas") or [])
        pt = list(syn.get("pt_lemmas") or [])
        if pt:
            members = members + [f"PT: {w}" for w in pt]
        senses.append({
            "source": "wordnet",
            "key": key,
            "ili": ili,
            "local_id": syn.get("name") or "",
            "pos": syn.get("pos") or "",
            "gloss": syn.get("definition") or "",
            "members": members,
            "decision": "",  # not adjudicated here — corroboration only
            "note": "OEWN corroboration (WordNet track)",
        })
    out["senses"] = senses
    return out
