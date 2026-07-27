"""Onto.PT → CILI links: propose → human review → inventory use.

Accepted links:
  * stamp Onto sense cards with ``ili`` in decisions.json
  * emit ``*.ONTO-ILI.result.json`` (atestado) for LexWarrant
  * update SenseIndex rows

Rejected / proposed never enter LexWarrant as identity.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .gloss_sim import sense_similarity
from .normalize import normalize_word, pretty_word
from .sense_index import SenseIndex
from .workspace import ClassWorkspace


def _lemma_set(lemmas_json: str | list) -> set[str]:
    if isinstance(lemmas_json, list):
        raw = lemmas_json
    else:
        try:
            raw = json.loads(lemmas_json or "[]")
        except json.JSONDecodeError:
            raw = []
    return {normalize_word(x) for x in raw if x}


def _lemmas_list(lemmas_json: str | list) -> list[str]:
    if isinstance(lemmas_json, list):
        return [pretty_word(x) for x in lemmas_json if x]
    try:
        return [pretty_word(x) for x in json.loads(lemmas_json or "[]") if x]
    except json.JSONDecodeError:
        return []


def propose_for_class(
    class_id: str,
    *,
    min_score: float = 0.35,
    index: Optional[SenseIndex] = None,
    write_report: bool = True,
) -> dict[str, Any]:
    """Generate Onto→ILI proposals (lemma overlap + gloss similarity)."""
    ws = ClassWorkspace.open(class_id)
    si = index or SenseIndex()
    owned = index is not None
    try:
        c = si.connect()
        onto_rows = c.execute(
            "SELECT * FROM sense WHERE source = 'onto' AND class_id = ?",
            (class_id,),
        ).fetchall()
        anchors = c.execute(
            "SELECT * FROM sense WHERE source IN ('pulo', 'own-pt', 'oewn') "
            "AND ili IS NOT NULL AND ili != '' AND class_id = ?",
            (class_id,),
        ).fetchall()
        if not anchors:
            anchors = c.execute(
                "SELECT * FROM sense WHERE source IN ('pulo', 'own-pt') "
                "AND ili IS NOT NULL AND ili != '' LIMIT 50000"
            ).fetchall()

        inv: dict[str, list[Any]] = {}
        by_ili_gloss: dict[str, str] = {}
        by_ili_lemmas: dict[str, list[str]] = {}
        for a in anchors:
            ili = a["ili"]
            by_ili_gloss.setdefault(ili, a["gloss"] or "")
            by_ili_lemmas.setdefault(ili, _lemmas_list(a["lemmas"]))
            for lem in _lemma_set(a["lemmas_norm"]):
                inv.setdefault(lem, []).append(a)

        # Preserve accepted/rejected statuses
        prior = {
            (r["onto_key"], r["ili"]): r["status"]
            for r in c.execute(
                "SELECT onto_key, ili, status FROM onto_ili_proposal "
                "WHERE class_id = ?",
                (class_id,),
            )
        }

        proposals: list[dict[str, Any]] = []
        for o in onto_rows:
            lemmas = _lemma_set(o["lemmas_norm"])
            if not lemmas:
                continue
            votes: dict[str, dict[str, Any]] = {}
            for lem in lemmas:
                for a in inv.get(lem, []):
                    ili = a["ili"]
                    slot = votes.setdefault(ili, {
                        "ili": ili,
                        "shared": set(),
                        "sources": set(),
                        "anchors": set(),
                    })
                    slot["shared"].add(lem)
                    slot["sources"].add(a["source"])
                    slot["anchors"].add(a["sense_key"])
            for ili, slot in votes.items():
                shared = slot["shared"]
                lemma_score = len(shared) / max(len(lemmas), 1)
                if len(slot["sources"]) >= 2:
                    lemma_score = min(1.0, lemma_score + 0.1)
                gloss_info = sense_similarity(
                    o["gloss"] or "",
                    by_ili_gloss.get(ili, ""),
                    _lemmas_list(o["lemmas"]),
                    by_ili_lemmas.get(ili, []),
                )
                # Blend: lemma overlap primary; gloss can rescue or demote
                score = 0.7 * lemma_score + 0.3 * gloss_info["score"]
                if score < min_score:
                    continue
                status = prior.get((o["sense_key"], ili), "proposed")
                if status not in ("accepted", "rejected", "proposed"):
                    status = "proposed"
                evidence = {
                    "shared_lemmas": sorted(shared),
                    "onto_lemmas": sorted(lemmas),
                    "anchor_sources": sorted(slot["sources"]),
                    "n_anchors": len(slot["anchors"]),
                    "gloss": gloss_info,
                    "lemma_score": round(lemma_score, 4),
                }
                # Do not overwrite human accepted/rejected with proposed
                write_status = status if status in ("accepted", "rejected") else "proposed"
                si.save_onto_proposal(
                    onto_key=o["sense_key"],
                    ili=ili,
                    score=round(score, 4),
                    method="lemma_jaccard+gloss",
                    evidence=evidence,
                    class_id=class_id,
                    status=write_status,
                )
                proposals.append({
                    "onto_key": o["sense_key"],
                    "ili": ili,
                    "score": round(score, 4),
                    "evidence": evidence,
                    "status": write_status,
                })

        proposals.sort(key=lambda x: (-x["score"], x["onto_key"], x["ili"]))
        auto = auto_accept_confident(class_id, proposals, index=si)
        # refresh statuses after auto-accept
        if auto.get("n"):
            for p in proposals:
                for a in auto.get("accepted") or []:
                    if a.get("onto_key") == p["onto_key"] and a.get("ili") == p["ili"]:
                        p["status"] = "accepted"
                        p["auto"] = True
        report = {
            "class_id": class_id,
            "policy": (
                "Propose → review (GUI / CLI) → accepted links stamp Onto sense "
                "cards and feed ONTO-ILI atestado into LexWarrant. "
                "High-confidence unique proposals may auto-accept "
                "(config onto_ili_auto_accept_min)."
            ),
            "min_score": min_score,
            "n_onto": len(onto_rows),
            "n_anchors": len(anchors),
            "n_proposals": len(proposals),
            "n_accepted": sum(1 for p in proposals if p["status"] == "accepted"),
            "n_rejected": sum(1 for p in proposals if p["status"] == "rejected"),
            "auto_accept": auto,
            "proposals": proposals[:500],
        }
        if write_report:
            ws.out.mkdir(parents=True, exist_ok=True)
            path = ws.out / "onto_ili_proposals.json"
            path.write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            report["path"] = str(path)
        if report["n_accepted"]:
            apply_accepted_to_decisions(class_id)
            emit_onto_ili_result(class_id)
        return report
    finally:
        if not owned:
            si.close()


def auto_accept_confident(
    class_id: str,
    proposals: list[dict[str, Any]],
    *,
    index: Optional[SenseIndex] = None,
) -> dict[str, Any]:
    """Auto-accept unique high-score proposals (safe bootstrap for inventory).

    Rules (all required):
      * status is still ``proposed``
      * score ≥ ``onto_ili_auto_accept_min`` (default 0.85)
      * best ILI for that onto_key beats the runner-up by ≥ ``margin`` (0.12)
      * gloss component present with score ≥ 0.15 OR lemma_score ≥ 0.8
    """
    from .settings import load_config

    cfg = load_config()
    if not bool(cfg.get("onto_ili_auto_accept", True)):
        return {"n": 0, "accepted": [], "skipped": "disabled"}
    min_score = float(cfg.get("onto_ili_auto_accept_min") or 0.85)
    margin = float(cfg.get("onto_ili_auto_accept_margin") or 0.12)

    by_key: dict[str, list[dict[str, Any]]] = {}
    for p in proposals:
        if p.get("status") != "proposed":
            continue
        by_key.setdefault(p["onto_key"], []).append(p)

    accepted: list[dict[str, Any]] = []
    si = index
    owned = index is not None
    try:
        if si is None:
            si = SenseIndex()
            si.connect()
        for onto_key, group in by_key.items():
            group = sorted(group, key=lambda x: -float(x.get("score") or 0))
            best = group[0]
            score = float(best.get("score") or 0)
            if score < min_score:
                continue
            second = float(group[1]["score"]) if len(group) > 1 else 0.0
            if second and (score - second) < margin:
                continue
            ev = best.get("evidence") or {}
            gloss_sc = float((ev.get("gloss") or {}).get("score") or 0)
            lemma_sc = float(ev.get("lemma_score") or 0)
            if gloss_sc < 0.15 and lemma_sc < 0.8:
                continue
            si.save_onto_proposal(
                onto_key=onto_key,
                ili=best["ili"],
                score=score,
                method="auto_accept_confident",
                evidence={**ev, "auto_accept": True},
                class_id=class_id,
                status="accepted",
            )
            accepted.append({
                "onto_key": onto_key,
                "ili": best["ili"],
                "score": score,
                "status": "accepted",
                "auto": True,
            })
        return {
            "n": len(accepted),
            "accepted": accepted,
            "min_score": min_score,
            "margin": margin,
        }
    finally:
        if not owned and si is not None:
            si.close()


def list_proposals(class_id: str, status: Optional[str] = None) -> list[dict]:
    with SenseIndex() as si:
        c = si.connect()
        if status:
            rows = c.execute(
                "SELECT * FROM onto_ili_proposal WHERE class_id = ? AND status = ? "
                "ORDER BY score DESC",
                (class_id, status),
            ).fetchall()
        else:
            rows = c.execute(
                "SELECT * FROM onto_ili_proposal WHERE class_id = ? "
                "ORDER BY score DESC",
                (class_id,),
            ).fetchall()
        out = []
        for r in rows:
            d = dict(r)
            try:
                d["evidence"] = json.loads(d.get("evidence") or "{}")
            except json.JSONDecodeError:
                pass
            out.append(d)
        return out


def set_proposal_status(
    class_id: str,
    onto_key: str,
    ili: str,
    status: str,
) -> dict[str, Any]:
    if status not in ("accepted", "rejected", "proposed"):
        raise ValueError("status must be accepted|rejected|proposed")
    with SenseIndex() as si:
        c = si.connect()
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        cur = c.execute(
            "UPDATE onto_ili_proposal SET status = ?, updated = ? "
            "WHERE class_id = ? AND onto_key = ? AND ili = ?",
            (status, now, class_id, onto_key, ili),
        )
        if cur.rowcount == 0:
            # allow creating a manual accept row
            si.save_onto_proposal(
                onto_key=onto_key, ili=ili, score=1.0,
                method="manual", evidence={"manual": True},
                class_id=class_id, status=status,
            )
        else:
            c.commit()
    applied = apply_accepted_to_decisions(class_id)
    result_path = None
    if status == "accepted":
        result_path = emit_onto_ili_result(class_id)
    return {
        "onto_key": onto_key,
        "ili": ili,
        "status": status,
        "decisions_stamped": applied.get("stamped"),
        "onto_ili_result": result_path,
    }


def accept_top(class_id: str, n: int = 5, min_score: float = 0.6) -> dict[str, Any]:
    """Accept the top-N still-proposed links above min_score (explicit CLI action)."""
    props = [
        p for p in list_proposals(class_id, status="proposed")
        if float(p.get("score") or 0) >= min_score
    ]
    accepted = []
    for p in props[: max(0, int(n))]:
        accepted.append(set_proposal_status(
            class_id, p["onto_key"], p["ili"], "accepted",
        ))
    emit_onto_ili_result(class_id)
    apply_accepted_to_decisions(class_id)
    return {"class_id": class_id, "accepted": accepted, "n": len(accepted)}


def apply_accepted_to_decisions(class_id: str) -> dict[str, Any]:
    """Stamp accepted ILIs onto Onto sense cards in decisions.json."""
    from . import decisions as decmod

    ws = ClassWorkspace.open(class_id)
    accepted = list_proposals(class_id, status="accepted")
    by_key = {p["onto_key"]: p["ili"] for p in accepted}
    data = decmod.load_decisions(ws.decisions_json)
    stamped = 0
    for sense in data.get("senses") or []:
        if (sense.get("source") or "").lower() != "onto":
            continue
        # sense keys look like onto:RES:SID or res/sid variants
        key = str(sense.get("key") or "")
        candidates = [key, f"onto:{key}"]
        res = sense.get("resource")
        sid = sense.get("synset_id") or sense.get("sid")
        if res and sid:
            candidates.append(f"onto:{res}:{sid}")
        ili = None
        for cand in candidates:
            if cand in by_key:
                ili = by_key[cand]
                break
        if not ili:
            continue
        if sense.get("ili") != ili:
            sense["ili"] = ili
            sense["ili_source"] = "onto_ili_accepted"
            stamped += 1
    if stamped:
        decmod.save_decisions(ws.decisions_json, data)
    return {"stamped": stamped, "n_accepted": len(accepted)}


def emit_onto_ili_result(class_id: str) -> Optional[str]:
    """Write results/<Class>.ONTO-ILI.result.json for LexWarrant (atestado only)."""
    ws = ClassWorkspace.open(class_id)
    accepted = list_proposals(class_id, status="accepted")
    if not accepted:
        return None

    with SenseIndex() as si:
        c = si.connect()
        atestacao: dict[str, Any] = {}
        provenance: list[dict[str, Any]] = []
        for p in accepted:
            row = c.execute(
                "SELECT * FROM sense WHERE sense_key = ?", (p["onto_key"],)
            ).fetchone()
            lemmas = _lemmas_list(row["lemmas"]) if row else []
            gloss = (row["gloss"] if row else "") or ""
            ili = p["ili"]
            for lem in lemmas or [p["onto_key"]]:
                nw = normalize_word(lem)
                atestacao[nw] = {
                    "display": pretty_word(lem),
                    "offsets_ili": [ili],
                    "reason": (
                        f"Onto→ILI accepted · {p['onto_key']} → {ili} "
                        f"(score={p.get('score')})"
                    ),
                    "lexicon": "onto-pt+cili",
                }
            if lemmas:
                provenance.append({
                    "termo": pretty_word(lemmas[0]),
                    "estatuto": "atestado",
                    "offsets_ili": [ili],
                    "eixo": "",
                    "garantia": ["onto_ili_accepted"],
                    "gloss": gloss,
                    "origem": "onto_ili_accepted",
                })

    doc = {
        "class_id": class_id,
        "source": "ONTO-ILI",
        "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "policy": (
            "Accepted Onto→ILI projections as entry warrant (atestado). "
            "Not UF/RT. Human still adjudicates vocabulary on sense cards."
        ),
        "provenance": provenance,
        "atestacao": atestacao,
        "sinalizacao": {},
        "assertions": [],
        "all_passed": True,
    }
    ws.results.mkdir(parents=True, exist_ok=True)
    path = ws.results / f"{class_id}.ONTO-ILI.result.json"
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(path)
