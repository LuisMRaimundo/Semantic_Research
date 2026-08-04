# Relatório detalhado da pipeline lexical — motores **PULO** e **ONTO**

> Âmbito: os dois motores de *Fase 0* que sustentam o ecossistema `Semantic_Research`.
> **PULO** = `phase0_pulo.py` (PULO / WordNet.PT, âncora ILI).
> **ONTO** = `phase0_skos.py` (Onto.PT / CONTO.PT, corroboração difusa).
> Fusão final = `lexwarrant.py`. Fonte: leitura directa do código restaurado em
> `…\Tesaurus e Dicionários\{PULO Thesaurus GUI, ONTO, LexWarrant}`.

---

## 0. Mapa mental (uma frase por peça)

**O PULO decide o *sentido* (ancorado no ILI, sem estatística); o ONTO *corrobora*
com dados difusos (CONTO.PT, com porta estatística); o LexWarrant *relata* a
concordância entre ambos — nunca decide.**

```
decisions.json ──► compile_specs ──►  X.pulo.json ─►  phase0_pulo ─►  X.PULO.result.json ┐
   (humano)                       └►  X.onto.json ─►  phase0_skos ─►  X.ONTO.result.json ┤
                                                                                          ▼
                                                                    lexwarrant.run_report
                                                                                          │
                                                                       X.concordance.md/.json
                                                                    (FINAL_RESULTS, Onto+PULO)
```

Assimetria fundamental do protocolo:

| | **PULO** (`phase0_pulo`) | **ONTO** (`phase0_skos`) |
|---|---|---|
| Papel | **Âncora** (montante) | **Corroborador** (jusante) |
| Dados | Synsets desambiguados, 1 synset = 1 acepção | Synsets difusos com **pesos** (CONTO.PT) |
| Chave | **ILI** (`ili-30-…`) | `recurso:sid` (sem ILI) |
| Porta estatística | **Não existe** | **Sim** (peso + coocorrência) |
| «Etapa 3» | Colheita de **relações tipadas** (WordNet) | Corroboração **difusa gated** |
| Estatutos | UF · RT · contraste · BT · NT · **atributo** | UF · RT · contraste |
| Produz | **whitelist ILI** que o ONTO consome | — |

---

## 1. Vocabulário de artefactos

| Tipo | Ficheiro | Quem produz | Quem lê |
|------|----------|-------------|---------|
| DADOS | `exports/*.json` (export do thesaurus) | adaptadores / GUIs | motores |
| CONFIG | `_specs/X.pulo.json`, `_specs/X.onto.json` | `compile_specs.py` | motores |
| RESULT | `X.result.json` (+ `.report.md`, `.skos.ttl`, `.whitelist.json`) | motores | LexWarrant |
| SIDECAR | `X.ONTO.pending.json`, `X.PULO.signals.*` | ONTO / pipeline | humano |
| FINAL | `X.concordance.md` / `.json` | LexWarrant | humano |

A `spec` (CONFIG) é o contrato: nenhum motor tem nada codificado para um termo
concreto — tudo o que é específico de uma classe vive no JSON.

---

## 2. Estrutura da `spec` (entrada de cada motor)

Campos comuns (validados em `ClassSpec.load`):

- `class_id`, `pref_label`, `axis` — **obrigatórios**.
- `stage1_whitelist[]` — as acepções escolhidas: `{ili_offset, glosa, decision, members}`
  com `decision ∈ {UF, RT, exclude}`.
- `manual_terms[]`, `exclusion_patterns[]`, `adjudication{}`, `disjoint_classes{}`.

Diferenças de campo:

| Campo | PULO | ONTO |
|-------|------|------|
| `axis_terms[]` (verificação de eixo por glosa) | **sim** | — |
| `attribute_bucket[]` (nomes de qualidade) | **sim** | — |
| `exclude_terms[]` | **sim** | — |
| `focus_stems[]` (radicais-foco) | — | **obrigatório** |
| `gating{weight_min, min_cooccurrence}` | — | **sim** (0.5 / 2) |
| `fuzzy_resources[]` | — | `["contopt"]` |

`compile_specs.py` traduz `decisions.json` (humano) → estas specs. Notas do
tradutor: `atributo` de um sentido PULO vira `UF` na whitelist **e** empurra os
membros para `attribute_bucket`; `contraste` num sentido vira `exclude` (o
contraste é tratado por `adjudication`/relações). No ONTO, `atributo` colapsa em
`UF` (o ONTO não tem *bucket* de atributo).

---

## 3. Motor **PULO** (`phase0_pulo.py`) — passo a passo

### Indexação inicial
`PuloPhase0Engine.__init__` indexa os synsets do export por **ILI** (`by_ili`);
os synsets **sem** `ili_offset` vão para `no_ili` e são **sinalizados** (nunca
descartados em silêncio, nunca com ILI fabricado).

### Etapa 1 — Selecção de acepções (lista branca ILI)
- Percorre `stage1_whitelist`: `exclude` → excluídos; `UF`/`RT` → admitidos;
  outra coisa → inválido.
- Faz *cross-check* da `glosa` da spec contra a glosa real do export (`_export_gloss`).
- **Asserções**:
  - A1.1 — todo admitido tem `ili_offset` **e** glosa; um **UF** tem de estar
    *on-axis* (a glosa contém um dos `axis_terms`).
  - A1.2 — nenhum offset excluído aparece nos admitidos.
  - A1.3 — offsets ILI únicos e todos presentes.

### Verificação ILI (canónica)
- Nenhum id `por-`/`oewn-` é usado como chave de junção — **só ILI**.
- Synsets sem ILI ficam registados como sinalizados.

### Etapa 2 — Sementes
- Recolhe os **sinónimos** de cada synset admitido (do export, não da spec).
- Asserção: as sementes só podem vir de synsets admitidos (nada de fuga off-axis).

### Etapa 3 — Colheita de relações tipadas (o equivalente WordNet à «Etapa 3»)
Para cada synset admitido, percorre `relations[]` e classifica o rótulo
(`classify_relation`) em *buckets*:

| Rótulo (substring) | Bucket | Destino SKOS |
|---|---|---|
| antonym / antónimo | `contrast` | `:contrastaCom` |
| similar | `rt_uf` | RT/UF (**com verificação de eixo pela glosa do alvo**) |
| deriv | `family` | família morfológica (fora da pool) |
| hyponym/narrower | `NT` | `skos:narrower` |
| hypernym/broader | `BT` | `skos:broader` |
| attribute | `attribute` | `:temAtributo` |
| (nada) / `relation #NN` | `unnamed` | **sinalização** |

Regras finas: um *similar-to* cujo alvo **não** está no eixo (pela glosa) cai em
**sinalização** («similar-to fora do eixo»); alvos `(no lemma)` nunca são
admitidos. **Não há qualquer filtro estatístico** — é colheita tipada pura.

### Etapa 4 — Exclusão automática
Remove da pool: `exclude_terms` da spec; assinaturas de ruído (regex, ex.:
`por meio de`); colocações multipalavra **sem** corroboração; termos que só
existem via relação não-nomeada sem corroboração.

### Etapa 5 — Adjudicação + garantia
- Um termo é **admitido** só se tiver `status ∈ {UF,RT,contraste,BT,NT,atributo}`
  **e** `test` (teste decisivo) **e** `guarantee` (≥1 garantia).
- Nomes de qualidade (do `attribute_bucket` ∪ alcançados por relação `attribute`)
  são forçados a `atributo` — vão para `:temAtributo`, **nunca** `altLabel`.
- Garantia `estipulativa` exige **definição** *e* **relação estrutural**
  (senão fica pendente — foi exactamente o que bloqueou *politípica* antes).
- Tudo o que não estiver completo fica em `pending`.

### Consistência final
- Nenhum termo é **UF** de duas classes `owl:disjointWith`.
- Contrastantes **não** são serializados como `skos:related`.

### Serialização SKOS-XL/OWL (com `rdflib`)
`build_graph` constrói o grafo e `run_spec` **valida** por *round-trip*: reparsa o
Turtle e confirma a contagem de triplos → asserção «Serialização».

Mapeamento: UF→`skosxl:altLabel`; RT→`skos:related`; BT→`skos:broader`;
NT→`skos:narrower`; atributo→`:temAtributo`; contraste→`:contrastaCom`+`scopeNote`;
irmãs→`owl:disjointWith`.

### Saídas
`X.result.json` (com `stage1..stage5`, `sinalizacao`, `family`, `provenance`,
`assertions`, `all_passed`), `X.report.md`, `X.skos.ttl`, e **`X.whitelist.json`**
— esta última no esquema que o motor ONTO lê como `stage1_whitelist`.

---

## 4. Motor **ONTO** (`phase0_skos.py`) — passo a passo

Lê a `spec` **e** a base `ontopt.sqlite` (Onto.PT + CONTO.PT). Só admite
candidatos que já venham de synsets ancorados no ILI (via whitelist); a CONTO.PT
serve **apenas** para corroborar/sinalizar.

### Etapa 1 — Selecção de acepções
Igual em espírito ao PULO (whitelist por ILI, mesmas asserções A1.1–A1.3), mas a
chave prática dos sentidos Onto é `recurso:sid` (o Onto não tem ILI próprio).

### Etapa 2 — Núcleo de candidatos
Sementes = `members[]` de cada synset admitido (vindos da spec). Asserção: só de
synsets da lista branca.

### Etapa 3 — Corroboração difusa **gated** (o coração do ONTO)
1. Lê todos os membros dos `fuzzy_resources` (CONTO.PT) via SQL, agrupa por synset.
2. Marca **synsets-foco** (têm um membro cujo `word_norm` começa por um
   `focus_stem`) e **synsets nucleares** (esse membro tem `weight ≥ weight_min`).
3. Para cada co-membro `nw` desses synsets-foco calcula três condições:
   - **cond1** `in_nuclear` — apareceu num synset nuclear (peso suficiente);
   - **cond2** `cooccurrence ≥ min_cooccurrence` — co-ocorre em ≥ N synsets-foco;
   - **cond3** `corroborated` — está no conjunto de corroboração (sementes ILI ∪
     atestações de dicionário).
4. **cond1 ∧ cond2 ∧ cond3 → admitido**; **cond1 ∧ cond2 ∧ ¬cond3 → sinalização**.
- Asserções: A3.1 (todo admitido difuso cumpre as 3 condições) e A3.2 (quem falha
  corroboração vai para `sinalizacao[]`, nunca para `admitidos[]`).

> É esta a **porta estatística** que não existe no PULO: no ONTO um termo difuso
> só entra se tiver peso, repetição **e** corroboração externa.

### Etapa 4 — Exclusão automática
Regex de ruído + colocações multipalavra sem corroboração (igual ao PULO, sem o
`exclude_terms`/`only_unnamed`).

### Etapa 5 — Adjudicação
Admite só com `status ∈ {UF,RT,contraste}` + `test` + `guarantee`. Sem `atributo`,
sem BT/NT. O resto fica `pending`.

### Consistência final
C1 (UF não em classes disjuntas) e C2 (contraste não em `skos:related`).

### Serialização
`render_turtle` (escrita manual do Turtle, **sem** rdflib) + `X.whitelist.json`
(só `admitted_offsets`/`excluded_offsets`).

### Filtro de saída (importante)
`split_pending_for_persist`: o `X.result.json` persistido **só leva os admitidos**;
as centenas de sementes difusas por adjudicar vão para o *sidecar*
**`X.ONTO.pending.json`** — para o LexWarrant nunca as ingerir.

---

## 5. Diferenças PULO × ONTO (resumo operacional)

| Dimensão | PULO | ONTO |
|---|---|---|
| Fonte de verdade do sentido | synset desambiguado + ILI | whitelist ILI (herdada) + CONTO.PT |
| Expansão | relações tipadas WordNet | co-ocorrência difusa com pesos |
| Filtro | tipagem + eixo (glosa) | **peso ≥ 0.5** + **coocorr. ≥ 2** + corroboração |
| Estatutos extra | BT, NT, atributo | — |
| Nomes de qualidade | `:temAtributo` | (não modelado) |
| Turtle | `rdflib` (validado) | string manual |
| «Lixo» para revisão | `sinalizacao{}` no result | `X.ONTO.pending.json` (sidecar) |
| Relação entre eles | **produz** whitelist | **consome** whitelist |

---

## 6. Fusão final — `lexwarrant.py` (relato, nunca decisão)

Junta ≥2 `result.json` por conceito.

### Chave de junção
- **Primária (ILI):** `canonical_ili` normaliza offsets OMW-3.0 (`por-30-… ↔
  ili-30-…`, declarado) e ILIs OEWN (`i123…` → `oewn-ili:…`). Namespaces não
  declaradas → `(None, False)` e são **sinalizadas** (nunca forçadas).
- **Tabela de equivalência:** `EquivMap` lê só as linhas `map` (alta confiança)
  de `ili_equivalence.json` e unifica chaves (union-find). Sem esta tabela, as
  junções OEWN↔PULO caem para junção por termo.
- **Secundária (fraca):** `weak(term)` por termo normalizado quando não há ILI
  comum.

### Veredictos
| Veredicto | Condição |
|---|---|
| `convergência plena` | junção **por ILI** + ≥2 fontes admitem + **mesmo** estatuto |
| `convergência (termo)` | igual, mas a junção é `weak(term)` |
| `divergência de relação` | ≥2 admitem mas com **estatutos diferentes** |
| `fonte única` | admitido por exactamente 1 fonte |
| `sinalização` | ≥1 sinaliza e ninguém admite |

`pendente` conta como ausente; um conceito só-pendente é contado, não listado.

### Políticas de `proposta_final` (só sugestão)
- **conservative:** propõe estatuto só em convergência ou fonte única; qualquer
  divergência → `null`.
- **informed:** estatuto maioritário; empate → `null`.

### Asserções T1–T11
Precedência do ILI, junções fracas rotuladas, nenhum ILI fabricado, divergências
registadas por-fonte, fonte única nunca descartada, coluna WordNet ausente ⇒ «—»,
política respeitada, classes mistas recusadas, «convergência plena» exige ILI,
nenhum só-pendente na matriz, e *round-trip* do JSON.

---

## 7. Onde a pipeline `Semantic_Research` liga tudo

`semantic/pipeline.py :: run_class`:
1. `write_specs` → `_specs/X.{pulo,onto}.json` (a partir de `decisions.json`).
2. Corre `phase0_pulo.run_spec` (com o export PULO) → `results/X.PULO.result.json`.
3. Corre `phase0_skos.run_spec` (com `ontopt.sqlite`) → `results/X.ONTO.result.json`.
4. **Sidelining** do PULO: `sinalizacao` é retirada para `out/X.PULO.signals.*` e
   a fusão recebe uma cópia limpa (`hide_pulo_signals: true`).
5. `lexwarrant.run_report` → publica em `FINAL_RESULTS__Onto_plus_PULO/`.

---

## 8. Limitações conhecidas (estado actual)

- **O lado ONTO não ancora em ILI por natureza do recurso** (verificado no
  esquema real do `ontopt.sqlite`, 2026-07-13): os `sid` de todos os recursos
  (`contopt`, `clip21`, `fuzzythes`, `ontopt06`, …) são inteiros sequenciais
  sem qualquer traço de offset PWN-3.0 — não há campo de mapeamento no esquema.
  O CILI (catálogo canónico, vendorizado em `engines/LexWarrant/data/cili/`)
  resolve a perna OEWN↔PULO, mas não tem onde agarrar na perna ONTO. Ancorá-la
  exigiria uma distribuição do Onto.PT/ECO com mapeamento PWN exportado, ou
  re-projecção própria — fora de âmbito. O ONTO fica **corroboração-só**.
- Sem `ili_equivalence.json` na classe, as junções ONTO↔PULO são **weak(term)** →
  nunca há «convergência plena» (só «convergência (termo)»). Foi o caso do
  `TexturaUniforme`.
- O ONTO não modela `atributo`; um sentido marcado `atributo` colapsa em `UF` no
  seu lado — daí divergências legítimas (ex.: *uniformidade*/*invariância*).
- O PULO gera muita `sinalizacao` (relações não-nomeadas #NN) — ruído esperado,
  arquivado no *sidecar*, não é decisão.
- WordNet ainda não é uma faixa de motor; entra só como coluna/corroboração.

---

## 9. Comandos (headless)

```powershell
# PULO
python "phase0_pulo.py" X.pulo.json --pulo-export export.json --outdir fase0
# ONTO
python "phase0_skos.py" X.onto.json --db ontopt.sqlite --outdir fase0
# Fusão
python "lexwarrant.py" ONTO.result.json PULO.result.json --outdir .
```

Ou, no workbench: **Run pipeline** faz os três automaticamente.
