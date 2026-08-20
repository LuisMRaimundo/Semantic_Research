# CHANGES — R9 — CILI lexicographical engine (2026-08-20)

## R9 — CILI lexicographical engine
- **WP1** — `engines/CILI/cili_engine.py`: read-only `CiliEngine` (index + FTS5, `concept` / `entry` / `search` / `stats`, exact `ili_for_pwn30` / `pwn30_for_ili`). Satellite `pos` + `pos_norm` (`s→a`). `[cili]` in `config.toml` (root = folder that contains `ili.ttl`; live pwn30 map = LexWarrant). First index writes `[pins] cili`; mismatch is a doctor warning, never an auto-update. Languages discovered from mapping files + OMW packs.
- **WP2** — `sr.py cili index|entry|concept|search|translate` (human text or `--json`).
- **WP3** — workbench: CILI Toplevel (search / entry / concept / copy-as-candidate into `_specs/`, not decisions) + inline CILI definition on sense cards that already carry an ILI id. TERMOS CILI block gated by `export_cili_block` (config or `class.json`); flag off leaves existing exports unchanged.
- **WP4** — `sr doctor` / `--deep`: config, root/`ili.ttl`, pwn30 map, index freshness, pin, languages, FTS5, map-hash warning.
- **WP5** — `tests/test_cili_engine.py` (fixture corpus; `@pytest.mark.local_corpus` smoke). `.gitignore`: `engines/CILI/data/` + `/CILI/` dump patterns. README architecture + CLI. Dumps stay local.
- **Local corpus actuals** (this machine): 117,659 concepts; labels en=207,061 (wn31), nl=58,786 (odwn13), por=69,154, fra=95,762, spa=133,347. OMW pack *lines* are ~73k/100k/165k; the engine indexes only rows whose PWN-3.0 offset is in the live map (unmapped offsets stay unmapped).

# CHANGES — scope_note SKOS + D2 residual (não semear) (2026-08-17)

## scope_note chega ao CONCEPT e ao TTL
- **Ficheiros:** `semantic/concept_model.py`, `semantic/termos_pesquisa.py`
- **Antes:** `build_class_concept_graph` ignorava `meta["scope_note"]`; o TTL punha o `axis` em `skos:scopeNote`.
- **Depois:** lê `scope_note`; `axis` → `skos:definition`; `scope_note` → `skos:scopeNote`. O campo vai para CONCEPT.json e para o cabeçalho de TERMOS_PESQUISA.md (`**Nota de âmbito:**`).

## D2 residual — prefixo sem focal não semeia cartão
- **Ficheiros:** `semantic/adapters/papel.py`, `semantic/decisions.py`
- **Antes:** «Starts with» `compósito` apanhava `compositor DIZ_SE_SOBRE X` e semeava um cartão com `members=[]` (ou, após o residual anterior, com os argumentos).
- **Depois:** se o focal não casa com a consulta, o bucket não é semeado — fica em `members_dropped_focus_filter` (`reason: focal_nao_casa_com_consulta`). Se o bucket for anotado à mesma, `papel_focal=null`, `papel_direction="unresolved"` e `members` nunca fica vazio. `from_papel_export` ignora synsets unresolved (exports pré-D2, sem esses campos, continuam a semear).

# CHANGES — fix pass adjudicação → artefactos (2026-08-17)

Branch `fix/adjudication-export`, um commit por defeito (D7→D5→D8→D2→D3→D4→D6→D1→T16).

## D7 — prefixos OEWN já não caem na heurística PULO
- **Ficheiros:** `semantic/ili_coverage.py`
- **Antes:** `_is_pwn30ish` tratava qualquer id ≥10 caracteres terminado em `-<letra>` como offset PULO, incluindo `oewn-92460746-n`.
- **Depois:** prefixos conhecidos primeiro (`oewn-` → não-PULO; `ili-30-`/`pwn30-`/`por-` → PULO); a heurística de forma só corre depois.

## D5 — contagem de asserções unificada
- **Ficheiros:** `semantic/assertions.py` (novo), `export_blocks.py`, `traceability.py`, `reconcile.py`
- **Antes:** cabeçalho 13, tabela 15, JSON 16 — T12/T15/R1 escreviam Markdown à parte (e R1 só no JSON).
- **Depois:** `rewrite_assertions_block` lê o JSON e reescreve cabeçalho + secção `## Asserções` no sítio; os três módulos só anexam ao JSON.

## D8 — caixa Meta já não trunca nem descarta scope_note
- **Ficheiros:** `semantic/meta_box.py` (novo), `semantic/workbench.py`
- **Antes:** analisador por prefixo de linha; `axis` multilinha perdia continuações; `scope_note`/`axis_terms` inexistentes.
- **Depois:** blocos `chave:` + continuação indentada; reconhece pref_label, axis, scope_note, focus_stems, axis_terms, axis_terms_locked; chaves extra ficam em meta com aviso.

## D2 — PAPEL conserva a estrutura argumental
- **Ficheiros:** `semantic/adapters/papel.py`, `semantic/decisions.py`
- **Antes:** os dois argumentos do triplo iam para `members` sem papel nem direcção (HIPERONIMO_DE ≡ sinónimos).
- **Depois:** cada bucket declara `papel_focal`, `papel_arguments`, `papel_direction`; `members` só inclui os argumentos em SINONIMIA.
- **Residual (superseded):** o fold sem focal já não semeia o cartão — ver secção «D2 residual — prefixo sem focal não semeia cartão». A comparação de lema usa `_norm_lema` (acentos/caixa/bytes).

## D3 — exclude PAPEL e termoRelacionado colapsado
- **Ficheiros:** `semantic/export_blocks.py`, `semantic/concept_model.py`
- **Antes:** o filtro «omitir o lema focal» invertia triplos PAPEL (retinha `material`); `termoRelacionado` repetia o mesmo termo por membro.
- **Depois:** exclude PAPEL conserva `papel_focal` e lista `papel_arguments` à parte; RT colapsa por forma, com `keys`/`ilis` de todas as origens.

## D4 — validated_alt_labels deixa de descartar UF em silêncio
- **Ficheiros:** `semantic/export_blocks.py`, `semantic/pipeline.py`
- **Antes:** a lista UF era substituída por `validated_alt_labels` sem rasto.
- **Depois:** entradas suprimidas em `alt_labels_suppressed_by_validated`, linha no `blocos.md` e aviso no log do Run.

## D6 — pares ILI divergentes passam a pending
- **Ficheiros:** `semantic/cili_auto.py`, `semantic/concept_model.py`, `semantic/pipeline.py`, `engines/LexWarrant/lexwarrant.py`
- **Antes:** `report["diverged"]` só era impresso; a chave `legacy_equivalence_map` apontava para um ficheiro CILI-only.
- **Depois:** chave `cili_auto_map` (lê a antiga); cada par divergente vai para `pending_ili_adjudication` e `mapping_status: pending_ili_divergence`; aviso no Run.

## D1 — axis_terms deixa de ficar congelado
- **Ficheiros:** `semantic/compile_specs.py`, `semantic/doctor.py` (exposição Meta: D8)
- **Antes:** `axis_terms` gravado era reutilizado para sempre, incluindo termos de cartões entretanto exclude.
- **Depois:** derivado a cada compilação (focus_stems + UF/RT), salvo `axis_terms_locked`; o valor antigo vai para `axis_terms_previous`; doctor avisa termos exclusive-exclude.

## T16 — CILI não pode estar em UF/RT e exclude ao mesmo tempo
- **Ficheiros:** `semantic/concept_model.py`, `semantic/pipeline.py`
- **Antes:** nenhuma asserção via incoerência de identificadores dentro do bloco de evidência (T12 só compara vocabulário ↔ evidência).
- **Depois:** T16 anexa-se ao concordance após o CONCEPT; falha se o mesmo CILI estiver em `uf`/`rt_candidates` e em `exclude_records`.

# CHANGES — fix pass pós-auditoria de rastreabilidade (2026-08-07)

Branch `fix/traceability-pass`, um commit por item. Suite de testes corrida
após cada item: 78 passed / 1 skipped, com 1 falha PRÉ-EXISTENTE (já em
`main`): `tests/test_termos_pesquisa.py::TexturaUniformeRegressionTests::
test_regression_surface` (asserção R4 contra dados vivos da classe).

## Fix 1 — manual_terms sem status já não viram altLabel
- **Ficheiros:** `semantic/concept_model.py`
- **Antes:** entrada de `manual_terms` sem `status`/`decision` era promovida
  silenciosamente a UF (`st = (... or "UF")`) e exportada como
  `skos:altLabel`.
- **Depois:** essas entradas vão para uma lista de auditoria
  `stipulated_terms` no CONCEPT.json (ao lado de `discovery_evidence`) e é
  emitido um warning por entrada (class_id, termo, proveniência). Alinha
  com a política de `compile_specs.py` («No silent default to UF»).
- **Check:** CONCEPT.ttl da TexturaUniforme reconstruído — «politípica»
  ausente de `skos:altLabel` e presente em `stipulated_terms`.

## Fix 2 — dados: registos de teste removidos de TexturaUniforme (DATA)
- **Ficheiros:** `classes/TexturaUniforme/decisions.json` (+ cópia de
  evidência `decisions.json.pre-cleanup-20260807`, commitada).
- **Antes:** 10 `terms` com notas «Teste 1»/«Teste 1 falha»/«Teste 3» e a
  entrada `manual_terms` «politípica» (fixtures do commit inicial)
  contaminavam blocos, TERMOS e CONCEPT.
- **Depois:** só esses 11 registos removidos (listados verbatim na mensagem
  do commit); os 93 senses e os 2 terms reais («uniformidade»,
  «invariância», nota «qualidade») intactos.
- **Check:** pipeline re-executado; diff dos artefactos mostra apenas:
  «politípica» fora de `stipulated_terms` (warning do Fix 1 deixa de
  disparar), linhas dos terms de teste fora dos blocos,
  `descartados_pendentes` 11→10, timestamps.

## Fix 3 — flags de proveniência MD/JSON nunca divergem
- **Ficheiros:** `semantic/pipeline.py`, `engines/LexWarrant/lexwarrant.py`
- **Antes:** o MD era renderizado com defaults (ONTO `queried=False`) e o
  pipeline remendava só as cópias JSON a posteriori — MD ≠ JSON.
- **Depois:** abordagem preferida implementada — o pipeline calcula o
  estado real do ONTO ANTES de `run_report` (`_onto_source_status`) e
  passa-o via `source_status_overrides`; `render_json` funde-o antes de
  qualquer render, MD e JSON saem do mesmo dict; remendo pós-hoc removido.
  Semântica de `queried` corrigida: fonte efetivamente consultada (motor
  correu OU cartões seeded no decisions.json), não «existe ficheiro».
- **Check:** `TexturaUniforme.concordance.md` e `.json` (e cópias FINAL__)
  reportam ONTO `queried=true; discovery_evidence=true;
  concordance_results=false` (68 cartões discovery).

## Fix 4 — descartes onto declarados, nunca silenciosos
- **Ficheiros:** `semantic/reconcile.py`, `semantic/termos_pesquisa.py`,
  `semantic/export_blocks.py`, `semantic/concept_model.py`
- **Antes:** acepções Onto.PT UF/RT eram saltadas com `continue`
  (reconcile, termos) e membros filtrados por focus-stem eram descartados
  invisivelmente (blocos, CONCEPT).
- **Depois:** secção «Descartado (Onto.PT discovery-only)» no relatório
  residual e no TERMOS (MD/JSON/HTML), com chave, membros e decisão;
  membros removidos pelo filtro focus-stem registados em
  `members_dropped_focus_filter` (blocos: lista em `vocabulario`; CONCEPT:
  campo na linha UF). Nenhum critério de admissão mudou.
- **Check:** `clip21:15521` (uniformador/uniformizador, UF) figura no
  relatório residual sob a nova secção, no TERMOS_PESQUISA.json, e a sua
  linha UF no CONCEPT.json lista os membros filtrados.

## Fix 5 — workbench: edições por guardar sobrevivem à troca de filtro
- **Ficheiros:** `semantic/workbench.py`
- **Antes:** `_render_senses` limpava `self._sense_vars` na troca de filtro;
  escolhas de rádio não guardadas perdiam-se em silêncio.
- **Depois:** flush para um dict em memória (`_pending_decisions`) antes de
  cada re-render; reaplicado ao reconstruir os cartões; gravação em disco
  continua exclusiva do «4 · Guardar decisões» (que agora persiste edições
  feitas sob QUALQUER filtro da sessão); barra de estado acrescenta
  «· alterações por guardar»; edições pendentes não cruzam classes nem
  sobrevivem ao fecho sem guardar.
- **Check (guiado por script contra a GUI real + passos manuais no commit):**
  adjudicar sob «Onto/CONTO only», trocar para «PAPEL only» e voltar — a
  escolha persiste e o disco fica intacto; trocar de classe/fechar sem
  guardar — a edição desaparece.

## Fix 6 — T15: rastreabilidade adjudicação ↔ artefactos
- **Ficheiros:** `semantic/traceability.py` (novo), `semantic/pipeline.py`
- **Antes:** nenhuma asserção verificava exportado ↔ decidido; perdas como
  o clip21:15521 eram invisíveis.
- **Depois:** T15 conforme o sketch da auditoria — (a) cada item exportado
  (CONCEPT altLabel, blocos altLabel/termoRelacionado, TERMOS tabela F)
  rastreia a uma decisão UF/RT desta classe; (b) cada decisão UF/RT chega a
  ≥1 artefacto ou consta de `dropped_with_reason` sob regra declarada.
  `KNOWN_DROP_RULES` (constante de módulo): `onto_discovery_only`,
  `excluded_cili`. Desvio deliberado do sketch: o inventário exportado
  inclui também `termoRelacionado` (senão toda a decisão RT contava como
  «perdida», contradizendo a cláusula (b)). Ligado em `run_class` logo após
  TERMOS/CONCEPT, anexado ao concordance MD+JSON no padrão do T12. CLI
  retrospectivo: `python -m semantic.traceability <classe>|--all` (tabela
  classe × PASS/FAIL × violações; exit 1 se houver FAIL; não re-executa
  pipelines).
- **Check:** T15 PASSA na TexturaUniforme, com clip21:15521 em
  `dropped_with_reason` como `onto_discovery_only` (77 descartes
  declarados). O `--all` retrospetivo assinala TexturaComposita (2 membros
  papel adjudicados sem artefacto) — achado real em artefactos antigos.

## Feature — «Exportar fonte…» no workbench
- **Ficheiros:** `semantic/source_export.py` (novo), `semantic/workbench.py`
- **Antes:** sem forma de exportar, por fonte, os cartões da classe com as
  respetivas adjudicações.
- **Depois:** um Menubutton «Exportar fonte…» (em vez de 4 botões — a barra
  já tem 6 controlos) com Exportar ONTO…/PAPEL…/WordNet…/PULO…. Escreve
  `<classe>/EXPORT_<FONTE>_<timestamp>/` com `.md` (tabela por cartão) e
  `.json` (um registo por acepção): decisão, membros, ids, gloss, ligações
  externas; cabeçalho com class_id, fonte, pins do VERSION_MANIFEST,
  contagens e timestamp. Relatório puro: não toca em matriz, TERMOS,
  CONCEPT, FINAL_RESULTS nem decisions.json.
- **Check:** «Exportar ONTO…» na TexturaUniforme produz 68 cartões
  (6 UF · 6 RT · 56 exclude), incluindo clip21:15521 marcado UF.
