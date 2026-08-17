# Fase 0 — Relatório de selecção lexical: **textura compósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Base de corroboração:** `E:\PYTHON CODES\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-08-17T06:35:16
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:1320', 'contopt:16611', 'fuzzythes:26969', 'fuzzythes:27002', 'fuzzythes:27069', 'ontopt06:81042', 'thes5rec:19632', 'thes5rec:22375'] |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| Etapa 2 | Os membros colhidos provêm exclusivamente de synsets da lista branca. | PASS ✅ | OK |
| Etapa 3 | Candidatos difusos admitidos cumprem peso≥0.5, coocorrência≥2 e ≥1 corroboração externa. | PASS ✅ | OK |
| Etapa 3 | Candidatos que falham a corroboração vão para sinalizacao[], não para admitidos[]. | PASS ✅ | OK |
| Etapa 4 | Colocações multipalavra e padrões de ruído sem corroboração são descartados (não permanecem na pool de candidatos). | PASS ✅ | OK |
| Etapa 5 | Cada termo em admitidos[] tem estatuto∈{UF,RT} (Onto = descoberta; garantia calculada a jusante). | PASS ✅ | OK |
| Consistência final | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência final | Nenhum estatuto de evidência em admitidos[] (contraste/atributo/oposicao/vizinha). | PASS ✅ | OK |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- Synsets admitidos (on-axis): `['clip21:1320', 'contopt:16611', 'fuzzythes:26969', 'fuzzythes:27002', 'fuzzythes:27069', 'ontopt06:3928', 'ontopt06:7120', 'ontopt06:81042', 'polaridades:1620', 'thes5rec:19632', 'thes5rec:22375']`
- Synsets excluídos (off-axis): `['clip21:15438', 'clip21:17923', 'contopt:26524', 'fuzzythes:25832', 'ontopt06:6214', 'clip21:2083', 'contopt:24966', 'fuzzythes:7161', 'ontopt06:23962', 'ontopt06:25561', 'ontopt06:30747', 'ontopt06:49495', 'ontopt06:43961', 'thes5rec:13577', 'top01:2962']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:1320', 'glosa': '', 'decision': 'UF', 'members': ['compósito', 'materiais compostos']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:16611', 'glosa': '', 'decision': 'UF', 'members': ['compósito', 'materiais compostos']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26969', 'glosa': '', 'decision': 'RT', 'members': ['dissimilar', 'heterogéneo', 'dessemelhante', 'absimilhante', 'dissímil', 'díspar', 'dissemelhante', 'diferente', 'compósito']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27002', 'glosa': '', 'decision': 'RT', 'members': ['heterogêneo', 'compósito', 'constituído', 'composto', 'formado', 'elaborado', 'feito', 'heterogéneo', 'aprimorado', 'bem-avindo', 'misto', 'conciliado', 'mesclado', 'concordado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27069', 'glosa': '', 'decision': 'UF', 'members': ['heterogéneo', 'compósito', 'heterogêneo', 'dissimilar', 'composto', 'dessemelhante', 'mesclado', 'constituído']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:81042', 'glosa': '', 'decision': 'UF', 'members': ['compósito']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:19632', 'glosa': '', 'decision': 'UF', 'members': ['composto', 'compósito', 'dessemelhante', 'dissimilar', 'heterogéneo', 'heterogêneo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:22375', 'glosa': '', 'decision': 'UF', 'members': ['composto', 'compósito', 'constituído', 'elaborado', 'feito', 'formado', 'heterogêneo']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **21**

| Termo | Offsets ILI |
|-------|-------------|
| absimilhante | fuzzythes:26969 |
| aprimorado | fuzzythes:27002 |
| bem-avindo | fuzzythes:27002 |
| compósito | clip21:1320, contopt:16611, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, ontopt06:81042, polaridades:1620, thes5rec:19632, thes5rec:22375 |
| composto | fuzzythes:27002, fuzzythes:27069, ontopt06:3928, thes5rec:19632, thes5rec:22375 |
| conciliado | fuzzythes:27002 |
| concordado | fuzzythes:27002 |
| constituído | fuzzythes:27002, fuzzythes:27069, thes5rec:22375 |
| dessemelhante | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 |
| diferente | fuzzythes:26969 |
| díspar | fuzzythes:26969 |
| dissemelhante | fuzzythes:26969 |
| dissímil | fuzzythes:26969 |
| dissimilar | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 |
| elaborado | fuzzythes:27002, thes5rec:22375 |
| feito | fuzzythes:27002, thes5rec:22375 |
| formado | fuzzythes:27002, thes5rec:22375 |
| heterogéneo | fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, polaridades:1620, thes5rec:19632, thes5rec:22375 |
| materiais compostos | clip21:1320, contopt:16611 |
| mesclado | fuzzythes:27002, fuzzythes:27069 |
| misto | fuzzythes:27002 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **16**  ·  nucleares (peso ≥ 0.5): **12**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **0**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **0**

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT
- Termos **admitidos** (decisão humana completa): **21**
- Termos **pendentes** (aguardam decisão humana): **0**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| compósito | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:1320, contopt:16611, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, ontopt06:81042, polaridades:1620, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| materiais compostos | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt | clip21:1320, contopt:16611 | derivado do sentido (PASSO 3) | sense_decision |
| dissimilar | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 | derivado do sentido (PASSO 3) | sense_decision |
| heterogéneo | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, polaridades:1620, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| dessemelhante | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 | derivado do sentido (PASSO 3) | sense_decision |
| absimilhante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| dissímil | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| díspar | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| dissemelhante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| diferente | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| constituído | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, fuzzythes:27069, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| composto | UF | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27002, fuzzythes:27069, ontopt06:3928, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| formado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| elaborado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| feito | UF | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| aprimorado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| bem-avindo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| misto | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| conciliado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| mesclado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | fuzzythes:27002, fuzzythes:27069 | derivado do sentido (PASSO 3) | sense_decision |
| concordado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **textura compósita**
- `skos:altLabel` (UF) → composto, compósito, constituído, dessemelhante, dissimilar, elaborado, feito, formado, heterogéneo, materiais compostos, mesclado
- `:termoRelacionado` (RT) → absimilhante, aprimorado, bem-avindo, conciliado, concordado, diferente, dissemelhante, dissímil, díspar, misto

_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada como relação SKOS._
