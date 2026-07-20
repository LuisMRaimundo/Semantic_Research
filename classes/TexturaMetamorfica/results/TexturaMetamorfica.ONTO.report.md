# Fase 0 — Relatório de selecção lexical: **TexturaMetamórfica** (`TexturaMetamrfica`)

- **Eixo definidor:** muda de forma, relativamente a um ou vários parâmetros
- **Base de corroboração:** `C:\Users\lmr20\Desktop\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-07-13T17:43:34
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:15380', 'contopt:146', 'fuzzythes:30854', 'thes5rec:23634'] |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| Etapa 2 | Os membros colhidos provêm exclusivamente de synsets da lista branca. | PASS ✅ | OK |
| Etapa 3 | Candidatos difusos admitidos cumprem peso≥0.5, coocorrência≥2 e ≥1 corroboração externa. | PASS ✅ | OK |
| Etapa 3 | Candidatos que falham a corroboração vão para sinalizacao[], não para admitidos[]. | PASS ✅ | OK |
| Etapa 4 | Colocações multipalavra e padrões de ruído sem corroboração são descartados (não permanecem na pool de candidatos). | PASS ✅ | OK |
| Etapa 5 | Cada termo em admitidos[] tem estatuto∈{UF,RT,contraste}, teste decisivo registado e ≥1 garantia. | PASS ✅ | OK |
| Consistência final | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência final | Contrastantes não são serializados como skos:related. | PASS ✅ | OK |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- Synsets admitidos (on-axis): `['clip21:15380', 'contopt:146', 'fuzzythes:30854', 'ontopt06:10369', 'thes5rec:23634']`
- Synsets excluídos (off-axis): `[]`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:15380', 'glosa': '', 'decision': 'UF', 'members': ['hemoético', 'metamórfico']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:146', 'glosa': '', 'decision': 'UF', 'members': ['hemoético', 'metamórfico']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:30854', 'glosa': '', 'decision': 'UF', 'members': ['hemoético', 'metamórfico']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:23634', 'glosa': '', 'decision': 'UF', 'members': ['hemoético', 'metamórfico']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **2**

| Termo | Offsets ILI |
|-------|-------------|
| hemoético | clip21:15380, contopt:146, fuzzythes:30854, ontopt06:10369, thes5rec:23634 |
| metamórfico | clip21:15380, contopt:146, fuzzythes:30854, ontopt06:10369, thes5rec:23634 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **0**  ·  nucleares (peso ≥ 0.5): **0**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **0**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **0**

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT / contraste
- Termos **admitidos** (decisão humana completa): **0**
- Termos **pendentes** (aguardam decisão humana): **2**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|

### Pendentes (necessitam de decisão na spec `adjudication`)
hemoético, metamórfico

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **TexturaMetamórfica**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `:contrastaCom` + `skos:scopeNote` (contraste) → —

_Contrastantes NÃO são serializados como `skos:related` (o SKOS não modela antonímia)._
