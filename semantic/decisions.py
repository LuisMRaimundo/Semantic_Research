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


def from_pulo_export(
    export: dict[str, Any], existing: Optional[dict] = None
) -> dict[str, Any]:
    """Seed sense cards from a PULO export (keeps prior decisions)."""
    class_id = (existing or {}).get("class_id") or "Unknown"
    out = existing or blank_decisions(class_id)
    prior = {
        sense_key(s["source"], s["key"]): s
        for s in out.get("senses", []) if s.get("source") and s.get("key")
    }
    senses = list(out.get("senses", []))
    seen = set()
    for syn in export.get("synsets", []):
        ili = None
        for item in syn.get("ili") or []:
            ili = (item.get("ili_offset") or "").strip() or ili
        key = ili or syn.get("synset_offset") or ""
        if not key:
            continue
        sk = sense_key("pulo", key)
        seen.add(sk)
        if sk in prior:
            continue
        senses.append({
            "source": "pulo",
            "key": key,
            "ili": ili,
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
