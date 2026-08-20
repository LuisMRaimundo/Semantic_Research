#!/usr/bin/env python3
"""REFERENCE COPY of the CILI Lexicographer Workbench (stdlib-only).

Vendored from the local dump's ``run-workbench.py`` for the R9 engine port.
Do not run this as the Semantic Research workbench — use ``sr.py cili`` /
``sr.py gui``. Parsing and query logic was ported into ``engines/CILI/``.

Original docstring follows.
"""
# CILI Lexicographer Workbench — single-file, stdlib-only.

Parses the CILI Turtle files (ili.ttl + mapping files), builds a disposable
SQLite FTS5 index (.cili-workbench.sqlite3), and serves a local browser GUI:

  * ranked search over lemmas and definitions (with filters: POS, kind, resource, mode)
  * dictionary-entry view for a lemma (all its senses, grouped by POS)
  * concept inspector (definition, source, mappings, lemmas, supersession)
  * associations: shared-lemma senses + definition-similarity neighbours
  * data-quality overview

Run from the repository root (next to ili.ttl):

    python3 run-workbench.py            # first run builds the index (~30 s)
    python3 run-workbench.py --reindex  # force rebuild
    python3 run-workbench.py --port 9000 --host 127.0.0.1

Then open http://127.0.0.1:8765/ .  No third-party dependencies.
"""

import argparse
import json
import os
import re
import sqlite3
import sys
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Lock

HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, ".cili-workbench.sqlite3")
ILI_TTL = os.path.join(HERE, "ili.ttl")
MAPS = [
    ("wn31", os.path.join(HERE, "ili-map-wn31.ttl"), "en"),
    ("wn30", os.path.join(HERE, "ili-map-wn30.ttl"), "en"),
    ("odwn13", os.path.join(HERE, "ili-map-odwn13.ttl"), "nl"),
]
SCHEMA_VERSION = "3"  # bump to force automatic reindex on schema change
POS_NAMES = {"n": "noun", "v": "verb", "a": "adjective", "s": "adjective (satellite)", "r": "adverb"}

# ----------------------------------------------------------------------------- indexing

CONCEPT_RE = re.compile(
    r"<(i\d+)>\s+a\s+<(Concept|Instance)>\s*;(.*?)(?:\n\s*\n|\Z)", re.S)
DEF_RE = re.compile(r'skos:definition\s+"((?:[^"\\]|\\.)*)"@(\w+)')
SRC_RE = re.compile(r"dc:source\s+([\w:.\-]+)")
STATUS_RE = re.compile(r"ili:status\s+ili:(\w+)")
SUPERSEDED_RE = re.compile(r"ili:supersededBy\s+<?(i\d+)>?")
MAP_RE = re.compile(r"ili:(i\d+)\s+owl:sameAs\s+([\w]+):([\w.\-]+)\s*\.\s*(?:#\s*(.*))?")


def omw_files():
    import glob
    return sorted(glob.glob(os.path.join(HERE, "wn-data-*.tab")) +
                  glob.glob(os.path.join(HERE, "omw", "wn-data-*.tab")))


def source_files_mtime():
    files = [ILI_TTL] + [p for _, p, _l in MAPS if os.path.exists(p)] + omw_files()
    return max(os.path.getmtime(p) for p in files if os.path.exists(p))


def index_is_fresh():
    if not os.path.exists(DB_PATH):
        return False
    try:
        con = sqlite3.connect(DB_PATH)
        row = con.execute("SELECT value FROM meta WHERE key='source_mtime'").fetchone()
        ver = con.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
        con.close()
        return (row is not None and float(row[0]) >= source_files_mtime()
                and ver is not None and ver[0] == SCHEMA_VERSION)
    except Exception:
        return False


def build_index(verbose=True):
    t0 = time.time()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.executescript(
        """
        PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT);
        CREATE TABLE concepts(
            id INTEGER PRIMARY KEY, ili TEXT UNIQUE, kind TEXT, definition TEXT,
            deflang TEXT, source TEXT, pos TEXT, status TEXT, superseded_by TEXT);
        CREATE TABLE lemmas(ili TEXT, lemma TEXT, lemma_lc TEXT, resource TEXT, target TEXT, lang TEXT);
        CREATE INDEX idx_lem_l ON lemmas(lemma_lc);
        CREATE INDEX idx_lem_i ON lemmas(ili);
        CREATE VIRTUAL TABLE fts USING fts5(
            ili UNINDEXED, lemmas, definition, tokenize='porter unicode61');
        """
    )
    if verbose:
        print("Parsing ili.ttl ...", flush=True)
    text = open(ILI_TTL, encoding="utf-8").read()
    concepts = {}
    for m in CONCEPT_RE.finditer(text):
        ili, kind, body = m.group(1), m.group(2), m.group(3)
        d = DEF_RE.search(body)
        s = SRC_RE.search(body)
        st = STATUS_RE.search(body)
        sb = SUPERSEDED_RE.search(body)
        definition = d.group(1).replace('\\"', '"') if d else ""
        deflang = d.group(2) if d else ""
        source = s.group(1) if s else ""
        pos = source.rsplit("-", 1)[-1] if "-" in source else ""
        concepts[ili] = dict(
            ili=ili, kind=kind, definition=definition, deflang=deflang,
            source=source, pos=pos if pos in POS_NAMES else "",
            status=st.group(1) if st else "active",
            superseded_by=sb.group(1) if sb else None)
    cur.executemany(
        "INSERT INTO concepts(id, ili, kind, definition, deflang, source, pos, status, superseded_by)"
        " VALUES(?,?,?,?,?,?,?,?,?)",
        [(int(c["ili"][1:]), c["ili"], c["kind"], c["definition"], c["deflang"],
          c["source"], c["pos"], c["status"], c["superseded_by"]) for c in concepts.values()])
    if verbose:
        print(f"  {len(concepts)} concepts", flush=True)

    lemma_rows = []
    for resource, path, lang in MAPS:
        if not os.path.exists(path):
            continue
        if verbose:
            print(f"Parsing {os.path.basename(path)} ...", flush=True)
        n = 0
        for line in open(path, encoding="utf-8"):
            m = MAP_RE.match(line.strip())
            if not m:
                continue
            ili, _pfx, target, comment = m.groups()
            if comment:
                for lemma in comment.split(","):
                    lemma = lemma.strip()
                    if lemma:
                        lemma_rows.append((ili, lemma, lemma.lower(), resource, target, lang))
                        n += 1
            else:
                lemma_rows.append((ili, "", "", resource, target, lang))
        if verbose:
            print(f"  {n} lemma labels", flush=True)
    # Open Multilingual Wordnet language packs: wn-data-<lang>.tab (PWN 3.0 offsets)
    bridge = os.path.join(HERE, "ili-map-pwn30.tab")
    packs = omw_files()
    if packs and os.path.exists(bridge):
        off2ili = {}
        for line in open(bridge, encoding="utf-8"):
            parts = line.split()
            if len(parts) == 2:
                off2ili[parts[1]] = parts[0]
        for path in packs:
            lang = os.path.basename(path)[8:11]
            if verbose:
                print(f"Parsing {os.path.basename(path)} (OMW, {lang}) ...", flush=True)
            n = 0
            for line in open(path, encoding="utf-8"):
                if line.startswith("#"):
                    continue
                parts = line.rstrip("\n").split("\t")
                if len(parts) < 3 or parts[1].split(":")[-1] != "lemma":
                    continue
                ili = off2ili.get(parts[0])
                lemma = parts[2].strip()
                if ili and lemma:
                    lemma_rows.append((ili, lemma, lemma.lower(), "omw-" + lang, parts[0], lang))
                    n += 1
            if verbose:
                print(f"  {n} lemma labels", flush=True)
    cur.executemany(
        "INSERT INTO lemmas(ili, lemma, lemma_lc, resource, target, lang) VALUES(?,?,?,?,?,?)", lemma_rows)

    if verbose:
        print("Building FTS index ...", flush=True)
    lem_by_ili = {}
    for ili, lemma, _lc, resource, _t, _lang in lemma_rows:
        if lemma:
            lem_by_ili.setdefault(ili, set()).add(lemma)
    cur.executemany(
        "INSERT INTO fts(ili, lemmas, definition) VALUES(?,?,?)",
        [(c["ili"], "; ".join(sorted(lem_by_ili.get(c["ili"], []))), c["definition"])
         for c in concepts.values()])
    cur.execute("INSERT INTO meta VALUES('source_mtime', ?)", (str(source_files_mtime()),))
    cur.execute("INSERT INTO meta VALUES('schema_version', ?)", (SCHEMA_VERSION,))
    cur.execute("INSERT INTO meta VALUES('built_at', ?)", (time.strftime("%Y-%m-%d %H:%M:%S"),))
    con.commit()
    con.close()
    if verbose:
        print(f"Index built in {time.time()-t0:.1f} s -> {DB_PATH}", flush=True)


# ----------------------------------------------------------------------------- queries

class DB:
    def __init__(self):
        self.con = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.con.row_factory = sqlite3.Row
        self.lock = Lock()

    def q(self, sql, args=()):
        with self.lock:
            return [dict(r) for r in self.con.execute(sql, args).fetchall()]


def fts_escape(q):
    """Build a safe FTS5 MATCH expression from free text (prefix search per token)."""
    tokens = re.findall(r"[\w'\-]+", q, re.UNICODE)
    if not tokens:
        return None
    return " ".join('"{}"*'.format(t.replace('"', '')) for t in tokens)


def search(db, q, mode="any", pos="", kind="", resource="", status="", limit=50, offset=0):
    match = fts_escape(q)
    if not match:
        return {"total": 0, "results": []}
    col = {"lemma": "lemmas", "definition": "definition"}.get(mode)
    expr = f"{col}: ({match})" if col else match
    where, args = ["fts MATCH ?"], [expr]
    join = "JOIN concepts c ON c.ili = fts.ili"
    if pos:
        where.append("c.pos = ?"); args.append(pos)
    if kind:
        where.append("c.kind = ?"); args.append(kind)
    if status:
        where.append("c.status = ?"); args.append(status)
    if resource:
        join += " JOIN (SELECT DISTINCT ili FROM lemmas WHERE resource=?) lr ON lr.ili=c.ili"
        args.insert(1, resource)
    sql = (f"SELECT c.ili, c.kind, c.definition, c.pos, c.status, c.source, "
           f"snippet(fts, 1, '<b>', '</b>', ' … ', 12) AS lem_snip, "
           f"snippet(fts, 2, '<b>', '</b>', ' … ', 18) AS def_snip, bm25(fts) AS rank "
           f"FROM fts {join} WHERE {' AND '.join(where)} "
           f"ORDER BY rank LIMIT ? OFFSET ?")
    rows = db.q(sql, args + [limit, offset])
    total = db.q(f"SELECT count(*) AS n FROM fts {join} WHERE {' AND '.join(where)}", args)[0]["n"]
    return {"total": total, "results": rows}


def concept(db, ili):
    rows = db.q("SELECT * FROM concepts WHERE ili=?", (ili,))
    if not rows:
        return None
    c = rows[0]
    c["pos_name"] = POS_NAMES.get(c["pos"], c["pos"] or "—")
    c["mappings"] = db.q(
        "SELECT resource, target, group_concat(DISTINCT lemma) AS lemmas FROM lemmas "
        "WHERE ili=? GROUP BY resource, target ORDER BY resource", (ili,))
    lemrows = db.q("SELECT DISTINCT lemma, lang FROM lemmas WHERE ili=? AND lemma<>''", (ili,))
    c["lemmas"] = sorted({r["lemma"] for r in lemrows})
    c["by_lang"] = {}
    for r in lemrows:
        c["by_lang"].setdefault(r["lang"], set()).add(r["lemma"])
    c["by_lang"] = {k: sorted(v) for k, v in sorted(c["by_lang"].items())}
    # shared-lemma associations (polysemy / synonym neighbourhood)
    c["shared"] = db.q(
        """SELECT l2.lemma AS via, c2.ili, c2.definition, c2.pos, count(*) AS nshared
           FROM lemmas l1 JOIN lemmas l2 ON l1.lemma_lc = l2.lemma_lc AND l2.ili<>l1.ili
           JOIN concepts c2 ON c2.ili = l2.ili
           WHERE l1.ili=? AND l1.lemma<>''
           GROUP BY c2.ili ORDER BY nshared DESC, c2.id LIMIT 40""", (ili,))
    # definition-similarity neighbours via FTS on content words
    words = [w for w in re.findall(r"[a-zA-Z]{4,}", c["definition"] or "")][:8]
    c["similar"] = []
    if words:
        expr = " OR ".join('"%s"' % w for w in words)
        try:
            c["similar"] = db.q(
                """SELECT fts.ili, c2.definition, c2.pos, bm25(fts) AS rank
                   FROM fts JOIN concepts c2 ON c2.ili=fts.ili
                   WHERE fts MATCH ? AND fts.ili<>? ORDER BY rank LIMIT 15""",
                ("definition: (%s)" % expr, ili))
        except sqlite3.OperationalError:
            pass
    c["superseders"] = db.q("SELECT ili, definition FROM concepts WHERE superseded_by=?", (ili,))
    return c


def lemma_entry(db, lemma):
    rows = db.q(
        """SELECT DISTINCT c.ili, c.kind, c.definition, c.pos, c.status, l.lang
           FROM lemmas l JOIN concepts c ON c.ili=l.ili
           WHERE l.lemma_lc = ? ORDER BY c.pos, c.id""", (lemma.lower(),))
    src_langs = sorted({r["lang"] for r in rows})
    ilis = sorted({r["ili"] for r in rows})
    trans = {}
    if ilis:
        ph = ",".join("?" * len(ilis))
        for t in db.q(f"SELECT ili, lang, lemma FROM lemmas WHERE ili IN ({ph}) AND lemma<>''", ilis):
            trans.setdefault(t["ili"], {}).setdefault(t["lang"], set()).add(t["lemma"])
    seen, groups = set(), {}
    for r in rows:
        if r["ili"] in seen:
            continue
        seen.add(r["ili"])
        r["translations"] = {lg: sorted(v) for lg, v in sorted(trans.get(r["ili"], {}).items())}
        groups.setdefault(POS_NAMES.get(r["pos"], r["pos"] or "other"), []).append(r)
    # interlingual equivalents: rank other-language lemmas by number of shared senses
    equiv = {}
    for ili in seen:
        for lg, lems in trans.get(ili, {}).items():
            for lm in lems:
                if lm.lower() == lemma.lower():
                    continue
                key = (lg, lm)
                equiv[key] = equiv.get(key, 0) + 1
    equivalents = {}
    for (lg, lm), n in sorted(equiv.items(), key=lambda kv: (-kv[1], kv[0])):
        equivalents.setdefault(lg, []).append({"lemma": lm, "shared_senses": n})
    for lg in equivalents:
        equivalents[lg] = equivalents[lg][:25]
    # lexical gaps: senses with no label in some indexed language
    all_langs = sorted({l for _r, _p, l in MAPS if os.path.exists(_p)} |
                       {os.path.basename(p)[8:11] for p in omw_files()})
    gaps = {lg: [i for i in sorted(seen) if lg not in trans.get(i, {})]
            for lg in all_langs}
    return {"lemma": lemma, "langs": src_langs, "groups": groups,
            "count": len(seen), "equivalents": equivalents, "gaps": gaps}


def stats(db):
    s = {}
    s["concepts"] = db.q("SELECT count(*) n FROM concepts")[0]["n"]
    s["by_kind"] = db.q("SELECT kind, count(*) n FROM concepts GROUP BY kind")
    s["by_pos"] = db.q("SELECT pos, count(*) n FROM concepts GROUP BY pos ORDER BY n DESC")
    s["by_status"] = db.q("SELECT status, count(*) n FROM concepts GROUP BY status")
    s["lemma_labels"] = db.q("SELECT resource, count(*) n FROM lemmas WHERE lemma<>'' GROUP BY resource")
    s["distinct_lemmas"] = db.q("SELECT count(DISTINCT lemma_lc) n FROM lemmas WHERE lemma<>''")[0]["n"]
    s["dup_definitions"] = db.q(
        """SELECT definition, count(*) n FROM concepts WHERE definition<>''
           GROUP BY definition HAVING n>1 ORDER BY n DESC LIMIT 25""")
    s["no_lemma"] = db.q(
        """SELECT count(*) n FROM concepts c WHERE NOT EXISTS
           (SELECT 1 FROM lemmas l WHERE l.ili=c.ili AND l.lemma<>'')""")[0]["n"]
    s["meta"] = {r["key"]: r["value"] for r in db.q("SELECT * FROM meta")}
    return s


# ----------------------------------------------------------------------------- HTTP

PAGE = r"""<!doctype html><html><head><meta charset="utf-8">
<title>CILI Lexicographer Workbench</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#f6f4ee;--panel:#fffdf8;--ink:#26231e;--mut:#7a7468;--acc:#7a3b2e;--line:#e2ddd2;--hl:#fdf3d8}
*{box-sizing:border-box}body{margin:0;font:15px/1.55 Georgia,'Times New Roman',serif;background:var(--bg);color:var(--ink)}
header{padding:14px 22px;border-bottom:1px solid var(--line);background:var(--panel);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header h1{font-size:19px;margin:0;letter-spacing:.4px}header small{color:var(--mut)}
#bar{display:flex;gap:8px;flex-wrap:wrap;padding:14px 22px;background:var(--panel);border-bottom:1px solid var(--line);align-items:center}
input[type=text]{font:inherit;padding:7px 11px;border:1px solid var(--line);border-radius:6px;min-width:320px;background:#fff}
select,button{font:inherit;padding:6px 9px;border:1px solid var(--line);border-radius:6px;background:#fff;cursor:pointer}
button.primary{background:var(--acc);color:#fff;border-color:var(--acc)}
main{display:grid;grid-template-columns:minmax(340px,46%) 1fr;gap:0;height:calc(100vh - 122px)}
#results{overflow:auto;border-right:1px solid var(--line);padding:10px 0}
#detail{overflow:auto;padding:22px 28px;background:var(--panel)}
.res{padding:10px 22px;border-bottom:1px solid var(--line);cursor:pointer}
.res:hover{background:var(--hl)}.res.sel{background:var(--hl)}
.res .id{color:var(--acc);font-weight:bold;font-family:ui-monospace,monospace;font-size:13px}
.res .pos{color:var(--mut);font-style:italic;font-size:13px;margin-left:6px}
.res .lem{font-weight:bold}
.res .def{color:#3d3a33;font-size:14px}
b{background:var(--hl)}
h2{font-size:22px;margin:.2em 0 .3em}h3{font-size:15px;margin:1.4em 0 .4em;color:var(--acc);letter-spacing:.5px;text-transform:uppercase;font-family:Verdana,sans-serif;font-size:11px}
.tag{display:inline-block;border:1px solid var(--line);border-radius:4px;padding:1px 7px;margin:2px 4px 2px 0;font-size:12px;background:#fff;color:var(--mut)}
.lemma{cursor:pointer;color:var(--acc)}.lemma:hover{text-decoration:underline}
table{border-collapse:collapse;width:100%;font-size:13.5px}td,th{border-bottom:1px solid var(--line);padding:5px 8px;text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:normal;font-family:Verdana,sans-serif;font-size:11px;text-transform:uppercase}
.assoc{padding:6px 0;border-bottom:1px dotted var(--line);cursor:pointer}.assoc:hover{background:var(--hl)}
.assoc .via{color:var(--acc);font-weight:bold}
.mut{color:var(--mut)}
.lang{display:inline-block;background:var(--acc);color:#fff;border-radius:3px;padding:0 6px;font:11px Verdana,sans-serif;vertical-align:middle;margin-right:4px}
.trans{margin:1px 0 2px 1.2em;font-size:13.5px;color:#4a463e}
sup{color:var(--mut);font-size:10px}.mono{font-family:ui-monospace,monospace;font-size:12.5px}
#count{color:var(--mut);font-size:13px;margin-left:auto}
#entry h2 span{color:var(--mut);font-weight:normal;font-size:15px}
.sense{margin:.35em 0 .35em 1.2em;text-indent:-1.2em}.sense .n{color:var(--acc);font-weight:bold}
a.pill{cursor:pointer;color:var(--acc)}
@media(max-width:900px){main{grid-template-columns:1fr;height:auto}#results{max-height:45vh}}
</style></head><body>
<header><h1>CILI Lexicographer Workbench</h1><small id="meta"></small>
<span id="count"></span></header>
<div id="bar">
 <input id="q" type="text" placeholder="Search a term, phrase or definition…  (Enter)" autofocus>
 <select id="mode"><option value="any">lemmas + definitions</option><option value="lemma">lemmas only</option><option value="definition">definitions only</option></select>
 <select id="pos"><option value="">any POS</option><option value="n">noun</option><option value="v">verb</option><option value="a">adjective</option><option value="s">adj. satellite</option><option value="r">adverb</option></select>
 <select id="kind"><option value="">concept + instance</option><option value="Concept">Concept</option><option value="Instance">Instance</option></select>
 <select id="resource"><option value="">any resource</option><option value="wn31">PWN 3.1</option><option value="wn30">PWN 3.0</option><option value="odwn13">ODWN 1.3</option></select>
 <button class="primary" onclick="go(0)">Search</button>
 <button onclick="openLemma($('#q').value.trim())" title="Open the dictionary entry / translations for this exact term">&#8646; Entry</button>
 <button onclick="showStats()">Data quality</button>
</div>
<main><div id="results"></div><div id="detail"><p class="mut">Search on the left; click a result to inspect it.<br>
Click any <span class="lemma">lemma</span> anywhere to open its dictionary entry: senses, per-sense translations,<br>ranked <i>interlingual equivalents</i> (en ⇄ nl via the ILI pivot) and lexical gaps.</p></div></main>
<script>
const $=s=>document.querySelector(s);let OFFSET=0,LIMIT=60;
function esc(s){return (s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}
function api(u){return fetch(u).then(r=>r.json())}
function params(){return new URLSearchParams({q:$('#q').value,mode:$('#mode').value,pos:$('#pos').value,kind:$('#kind').value,resource:$('#resource').value,limit:LIMIT,offset:OFFSET})}
function go(off){OFFSET=off||0;if(!$('#q').value.trim())return;
 api('/api/search?'+params()).then(d=>{
  $('#count').textContent=d.total+' matches';
  $('#results').innerHTML=d.results.map(r=>`<div class="res" onclick="openC('${r.ili}',this)">
   <span class="id">${r.ili}</span><span class="pos">${r.pos||''} · ${r.kind}${r.status!=='active'?' · '+r.status:''}</span><br>
   <span class="lem">${r.lem_snip||''}</span><div class="def">${r.def_snip||esc(r.definition)}</div></div>`).join('')
  +(d.total>OFFSET+LIMIT?`<div class="res mut" onclick="go(${OFFSET+LIMIT})">more…</div>`:'');
  if(d.results.length)openC(d.results[0].ili,document.querySelector('.res'));});}
function openC(ili,el){if(el){document.querySelectorAll('.res.sel').forEach(x=>x.classList.remove('sel'));el.classList.add('sel');}
 api('/api/concept/'+ili).then(c=>{if(!c){$('#detail').innerHTML='not found';return}
  $('#detail').innerHTML=`
  <h2>${c.ili} <span class="mut" style="font-size:14px">${c.kind} · ${c.pos_name} · ${c.status}${c.superseded_by?' → superseded by <a class="pill" onclick="openC(\''+c.superseded_by+'\')">'+c.superseded_by+'</a>':''}</span></h2>
  <p style="font-size:17px">${esc(c.definition)||'<span class=mut>(no definition)</span>'}</p>
  ${Object.entries(c.by_lang||{}).map(([lg,ls])=>`<div style="margin:3px 0"><span class="lang">${lg}</span> ${ls.map(l=>`<span class="tag lemma" onclick="openLemma('${esc(l).replace(/'/g,"\\'")}')">${esc(l)}</span>`).join('')}</div>`).join('')||'<span class=mut>no lemma labels</span>'}
  <h3>Mappings</h3><table><tr><th>resource</th><th>target</th><th>lemmas</th></tr>
  ${c.mappings.map(m=>`<tr><td>${m.resource}</td><td class="mono">${m.target}</td><td>${esc(m.lemmas||'')}</td></tr>`).join('')}</table>
  <div class="mono mut" style="margin-top:4px">source: ${esc(c.source)||'—'}</div>
  ${c.superseders.length?`<h3>Supersedes</h3>`+c.superseders.map(s=>`<div class="assoc" onclick="openC('${s.ili}')"><span class="via">${s.ili}</span> ${esc(s.definition)}</div>`).join(''):''}
  <h3>Associations — shared lemmas</h3>
  ${c.shared.length?c.shared.map(a=>`<div class="assoc" onclick="openC('${a.ili}')"><span class="via">${esc(a.via)}</span> → <b>${a.ili}</b> <span class="mut">(${a.pos||'?'})</span> ${esc((a.definition||'').slice(0,160))}</div>`).join(''):'<div class="mut">none</div>'}
  <h3>Associations — similar definitions</h3>
  ${c.similar.map(a=>`<div class="assoc" onclick="openC('${a.ili}')"><b>${a.ili}</b> <span class="mut">(${a.pos||'?'})</span> ${esc((a.definition||'').slice(0,160))}</div>`).join('')||'<div class="mut">none</div>'}`;});}
function openLemma(l){if(!l)return;api('/api/lemma/'+encodeURIComponent(l)).then(e=>{
 if(!e.count){$('#detail').innerHTML=`<h2>${esc(l)}</h2><p class="mut">No exact lemma with this spelling in the indexed mappings. Try Search — the term may appear inside multiword lemmas or definitions.</p>`;return}
 let h=`<div id="entry"><h2>${esc(e.lemma)} <span>· ${e.count} sense${e.count==1?'':'s'} · ${e.langs.join(', ')}</span></h2>`;
 const eq=e.equivalents||{};
 if(Object.keys(eq).length){h+=`<h3>Interlingual equivalents (ranked by shared senses)</h3>`;
  for(const [lg,rows] of Object.entries(eq)){h+=`<div style="margin:2px 0"><span class="lang">${lg}</span> `+
   rows.map(r=>`<span class="tag lemma" onclick="openLemma('${esc(r.lemma).replace(/'/g,"\\'")}')">${esc(r.lemma)}<sup>${r.shared_senses}</sup></span>`).join('')+`</div>`;}}
 for(const [pos,rows] of Object.entries(e.groups)){h+=`<h3>${pos}</h3>`;
  rows.forEach((r,i)=>{h+=`<div class="sense"><span class="n">${i+1}.</span> ${esc(r.definition)} <a class="pill mono" onclick="openC('${r.ili}')">${r.ili}</a>${r.status!=='active'?' <span class=tag>'+r.status+'</span>':''}`;
   for(const [lg,ls] of Object.entries(r.translations||{})){h+=`<div class="trans"><span class="lang">${lg}</span> ${ls.map(x=>`<span class="lemma" onclick="openLemma('${esc(x).replace(/'/g,"\\'")}')">${esc(x)}</span>`).join(', ')}</div>`;}
   h+=`</div>`;})}
 const gapLangs=Object.entries(e.gaps||{}).filter(([lg,g])=>g.length&&!(e.langs.length===1&&e.langs[0]===lg));
 if(gapLangs.length){h+=`<h3>Lexical gaps</h3>`;
  gapLangs.forEach(([lg,g])=>{h+=`<div class="mut" style="font-size:13px"><span class="lang">${lg}</span> no label for ${g.length} sense${g.length==1?'':'s'}: ${g.map(i=>`<a class="pill mono" onclick="openC('${i}')">${i}</a>`).join(' ')}</div>`});}
 $('#detail').innerHTML=h+'</div>';});}
function showStats(){api('/api/stats').then(s=>{
 $('#detail').innerHTML=`<h2>Data quality</h2>
 <p>${s.concepts} records · ${s.distinct_lemmas} distinct lemmas · index built ${s.meta.built_at}</p>
 <h3>By kind</h3>${s.by_kind.map(r=>`<span class=tag>${r.kind}: ${r.n}</span>`).join('')}
 <h3>By POS</h3>${s.by_pos.map(r=>`<span class=tag>${r.pos||'—'}: ${r.n}</span>`).join('')}
 <h3>By status</h3>${s.by_status.map(r=>`<span class=tag>${r.status}: ${r.n}</span>`).join('')}
 <h3>Lemma labels per resource</h3>${s.lemma_labels.map(r=>`<span class=tag>${r.resource}: ${r.n}</span>`).join('')}
 <p class="mut">${s.no_lemma} records have no lemma label from any indexed mapping.</p>
 <h3>Most duplicated definitions</h3><table><tr><th>n</th><th>definition</th></tr>
 ${s.dup_definitions.map(r=>`<tr><td>${r.n}</td><td>${esc(r.definition)}</td></tr>`).join('')}</table>`;});}
$('#q').addEventListener('keydown',e=>{if(e.key==='Enter'){if(e.shiftKey)openLemma($('#q').value.trim());else go(0)}});
api('/api/stats').then(s=>{$('#meta').textContent=s.concepts+' concepts · '+s.distinct_lemmas+' lemmas'});
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    db = None

    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        def p(name, default=""):
            return qs.get(name, [default])[0]

        try:
            if parsed.path == "/":
                data = PAGE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif parsed.path == "/api/search":
                self.send_json(search(
                    self.db, p("q"), p("mode", "any"), p("pos"), p("kind"),
                    p("resource"), p("status"),
                    min(int(p("limit", "50") or 50), 200), int(p("offset", "0") or 0)))
            elif parsed.path.startswith("/api/concept/"):
                self.send_json(concept(self.db, parsed.path.rsplit("/", 1)[1]))
            elif parsed.path.startswith("/api/lemma/"):
                self.send_json(lemma_entry(
                    self.db, urllib.parse.unquote(parsed.path.rsplit("/", 1)[1])))
            elif parsed.path == "/api/stats":
                self.send_json(stats(self.db))
            else:
                self.send_json({"error": "not found"}, 404)
        except BrokenPipeError:
            pass
        except Exception as e:
            self.send_json({"error": str(e)}, 500)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--reindex", action="store_true", help="force index rebuild")
    args = ap.parse_args()
    if not os.path.exists(ILI_TTL):
        sys.exit("ili.ttl not found next to this script — run from the CILI repository root.")
    if args.reindex or not index_is_fresh():
        build_index()
    Handler.db = DB()
    srv = HTTPServer((args.host, args.port), Handler)
    print(f"CILI Lexicographer Workbench: http://{args.host}:{args.port}/  (Ctrl-C to stop)")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
