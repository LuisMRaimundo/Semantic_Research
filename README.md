# Semantic Research — R8 workbench (~95 reliability)

**Any-term / any-concept** research tool over the Portuguese lexicon stack
(**PULO**, **Onto.PT** discovery, **OWN-PT / OEWN**, **LexWarrant**), with a
durable **SenseIndex**, **CILI-only** ILI join, and `sr doctor` pins.

Nothing in the runtime is bound to a particular lemma or class. Existing
folders under `classes/` are just workspaces you created for specific studies.

Decisão só por sentido; junção interlingual via **CILI oficial** canónico
(`i114921`, nunca fabricado; URI `http://globalwordnet.org/ili/i…`; página
`https://globalwordnet.github.io/cili/i….html`). Prefixos CURIE como
`oewn-ili:` são só contextuais — não são o identificador primário. Offsets
PWN 3.0 usam id local `pwn30-…` (legado OMW `ili-30-…` = pivô PWN 3.0, **não**
CILI). Onto.PT continua discovery-only; propostas Onto→ILI são *review-only*.

## Daily path (any concept)

1. **Create** a class for the concept you are grounding.
2. **Search** any lemma (PULO first; Onto.PT = discovery; WordNet = EN facets).
3. Mark each sense: **UF · RT · exclude** (+ `atributo` on PULO).
4. **Save** → **Run** (SenseIndex + CILI + LexWarrant).
5. Open:
   `classes/<Class>/FINAL_RESULTS__Onto_plus_PULO/TERMOS.html`

## Run

```powershell
cd "C:\Users\lmr20\Desktop\Semantic_Research"
pip install -r requirements.txt
python sr.py doctor --deep
python sr.py gui
```

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
```

## Architecture (R8)

| Layer | Role |
|-------|------|
| **PULO** | Sense / UF·RT authority (native `to_ili`) |
| **Onto.PT** | Discovery only — never LexWarrant admission |
| **OEWN** (pin `oewn:2024`) | EN corroboration via facets |
| **OWN-PT** (pin `own-pt:1.0.0`) | PT lemmas via ILI (`atestado`) |
| **CILI** | Pure identity `i…` ↔ PWN-3.0 offset (+ a↔s satellite norm) |
| **SenseIndex** | `data/sense_index.sqlite` — durable sense registry |
| **Onto→ILI proposals** | Scored lemma overlap; status=`proposed` only |
| **LexWarrant** | Concordance / diagnostic merge by ILI |

Config: prefer **`config.toml`** (repo-relative paths + `[pins]`).

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
| OEWN pin risk | Hard pin to `oewn:2024` — extras ignored |
| Publishable model | `CONCEPT.ttl` + `data/concepts/registry.ttl` |

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
