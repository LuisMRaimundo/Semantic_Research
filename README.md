# Semantic Research — R8 workbench (~95 software reliability)

**Any-term / any-concept** research tool over the Portuguese lexicon stack
(**PULO**, **Onto.PT** discovery, **OWN-PT / OEWN**, **LexWarrant**), with a
durable **SenseIndex**, **CILI-only** ILI join, and `sr doctor` pins.

Nothing in the runtime is bound to a particular lemma or class. Existing
folders under `classes/` are just workspaces you created for specific studies.

Decisão só por sentido; junção interlingual via **CILI oficial** canónico
(`i114921`, nunca fabricado; URI RDF `http://ili.globalwordnet.org/ili/i…`;
página `https://globalwordnet.github.io/cili/i….html`). Prefixos CURIE como
`oewn-ili:` são só contextuais — não são o identificador primário. Offsets
PWN 3.0 usam id local `pwn30-…` (legado OMW `ili-30-…` = pivô PWN 3.0, **não**
CILI). Matches SKOS (`exactMatch`/…) só via `concept_mapping` adjudicada —
resolução formal ≠ alinhamento semântico. Onto.PT continua discovery-only;
propostas Onto→ILI são *review-only*.

## Daily path (any concept)

1. **Create** a class for the concept you are grounding.
2. **Search** any lemma (PULO first; Onto.PT = discovery; WordNet = EN facets).
3. Mark each sense: **UF · RT · exclude** (+ `atributo` on PULO).
4. **Save** → **Run** (SenseIndex + CILI + LexWarrant).
5. Open:
   `classes/<Class>/FINAL_RESULTS__Onto_plus_PULO/TERMOS.html`
   (botão **Exportar tudo para pasta…** / ZIP; no workbench: **Exportar FINAL…**)

## Run

```powershell
cd "C:\Users\lmr20\Desktop\Semantic_Research"
pip install -r requirements.txt
python sr.py doctor --deep
python sr.py resources --ensure-ownpt --build-papel
python sr.py gui
```

Lexical dumps expected next to the code (local; gitignored if huge):

| Path | Role |
|------|------|
| `pulo.20160508.sql/` | PULO MySQL dump (preferred; already loaded into `pulo.sqlite`) |
| `pulo.20150502.sql/` | Older PULO dump (reference) |
| `OntoPTv0.6_rdf/` | Onto.PT v0.6 RDF (runtime uses `engines/ONTO/ontopt.sqlite`) |
| `PAPEL.v.3.5_utf8/` | PAPEL relations → index with `--build-papel` |
| `openWordnet-PT/` | Git clone of [own-pt/openWordnet-PT](https://github.com/own-pt/openWordnet-PT); runtime still uses `wn` pin `own-pt:1.0.0` |

CLI (placeholders — substitute your concept):

```powershell
python sr.py new <ClassId> --pref <lemma> --axis "<defining property>" --stems <stem1>,<stem2>
python sr.py search <ClassId> <lemma> --source pulo
python sr.py search <ClassId> <lemma> --source onto
python sr.py search <ClassId> <english_lemma> --source wordnet
python sr.py status <ClassId>
python sr.py run <ClassId>
python sr.py index --class <ClassId>
python sr.py smoke --class <ClassId> --query <lemma>
python sr.py doctor --deep
python sr.py cili index
python sr.py cili entry <lemma>
python sr.py cili concept <iN>
python sr.py cili search <query> [--mode any|lemma|definition] [--pos n|v|a|r] [--lang xx]
python sr.py cili translate <lemma> --to <lang>
```

## Architecture (R8)

| Layer | Role |
|-------|------|
| **PULO** | Sense / UF·RT authority (native `to_ili`; DB from `pulo.20160508.sql`) |
| **Onto.PT / CONTO.PT** | Discovery only — runtime `ontopt.sqlite` (`ontopt06` + fuzzy `contopt`/`clip21`); dumps `OntoPTv0.6_rdf/`, `CONTO.PT/` |
| **PAPEL 3.5** | Discovery only — dictionary word–word relations (`PAPEL.v.3.5_utf8` → `data/papel.sqlite`) |
| **OEWN** (runtime pin `oewn:2025`; companions `2024` + `2025+`) | EN corroboration via facets |
| **OWN-PT** (pin `own-pt:1.0.0`) | PT lemmas via ILI (`atestado`); optional source clone `openWordnet-PT/` |
| **CILI** | Lexicographical reference + interlingual equivalents; read-only; identity via live pwn30 map |
| **SenseIndex** | `data/sense_index.sqlite` — durable sense registry |
| **Onto→ILI proposals** | Scored lemma overlap; status=`proposed` only |
| **LexWarrant** | Concordance / diagnostic merge by ILI |

Config: prefer **`config.toml`** (repo-relative paths + `[pins]`).

`[cili]` points at the local dump (folder that **directly** contains `ili.ttl`;
on this machine `cili-master/cili-master/`) and the live identity map
`engines/LexWarrant/data/cili/ili-map-pwn30.tab`. Lexical dumps stay local and
are gitignored. First `sr cili index` builds `engines/CILI/data/cili.sqlite`
(gitignored) and records `[pins] cili` (ili.ttl sha256 prefix). A pin mismatch
is a doctor warning — never an auto-update. TERMOS CILI blocks are gated by
`export_cili_block = true` (config or per-class `class.json`).

```powershell
python verify_pipeline.py                  # auto-picks any existing class
python verify_pipeline.py --class X --query Y
python tools/build_manifest.py
```

## Layout por classe

```
classes/<Class>/
  class.json
  decisions.json
  FINAL_RESULTS__Onto_plus_PULO/     # DELIVERABLE
    TERMOS.html
    TERMOS_PESQUISA.md|.csv
  exports/ results/ out/
  _specs/
```

## Research hardening (post-R8)

| Issue | Fix |
|-------|-----|
| CILI/OEWN drift | PWN-3.0 **+** PWN-3.1 maps + `wn.ili` validation; `ili_coverage` report |
| Onto inventory | Auto-accept high-confidence unique links + GUI review panel |
| weak(term) polysemy | default `weak_term_mode=gloss_gated` |
| Gloss layer | TF-IDF char/word cosine (+ opt-in embeddings: `gloss_use_embeddings`) |
| OEWN pin risk | Runtime hard pin `oewn:2025`; companions `2024`/`2025+` kept installed |
| Publishable model | `CONCEPT.ttl`: `exactMatch` ≤1 PULO UF CILI; RT→`relatedMatch`; excludes never matched |
| Onto→ILI | Inventory only (`sinalizacao`); emit score≥0.85; auto-accept off by default |

```powershell
python sr.py onto-ili propose <ClassId>
python sr.py onto-ili list <ClassId> --status proposed
python sr.py onto-ili accept <ClassId> --onto-key onto:RES:SID --ili i12345
python sr.py onto-ili accept-top <ClassId> --n 5 --min-score 0.6
python sr.py publish <ClassId>
python sr.py publish --all
```

## Notas

- Paths are **repo-relative**; no Desktop `legacy_root` at runtime.
- Duplicate `cili-master/` dumps belong in `_quarantine/` — live map is
  `engines/LexWarrant/data/cili/ili-map-pwn30.tab`.
- **Garantias** calculadas: `convergencia` · `fonte_unica` · `dominio` · `estipulativa`.
