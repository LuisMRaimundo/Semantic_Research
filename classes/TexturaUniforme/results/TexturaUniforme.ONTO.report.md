# Fase 0 — Relatório de selecção lexical: **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Base de corroboração:** `E:\PYTHON CODES\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-08-07T14:22:36
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2945', 'clip21:15521'] |
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
- Synsets admitidos (on-axis): `['fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2131', 'ontopt06:2133', 'ontopt06:2945', 'polaridades:1656', 'polaridades:4484', 'clip21:15521']`
- Synsets excluídos (off-axis): `['clip01:6948', 'clip21:12405', 'clip21:16596', 'clip21:17576', 'clip21:17930', 'clip21:19004', 'clip21:19228', 'clip21:19272', 'clip21:19790', 'contopt:9180', 'contopt:9502', 'contopt:15361', 'contopt:16491', 'contopt:28395', 'fuzzythes:1661', 'fuzzythes:1920', 'fuzzythes:2140', 'fuzzythes:3480', 'fuzzythes:23180', 'fuzzythes:23495', 'fuzzythes:23527', 'fuzzythes:24915', 'fuzzythes:26484', 'fuzzythes:27110', 'ontopt06:787', 'ontopt06:803', 'ontopt06:1186', 'ontopt06:28292', 'polaridades:4425', 'polaridades:5083', 'polaridades:5938', 'clip01:3425', 'clip01:4659', 'clip01:7405', 'clip01:1043', 'clip21:18187', 'clip21:19074', 'clip21:16541', 'clip21:8149', 'clip21:14314', 'clip21:14562', 'clip21:19940', 'clip21:20073', 'clip21:20421', 'clip21:1403', 'clip21:5416', 'clip21:6019', 'clip21:7565', 'clip21:7750', 'clip21:9132', 'clip21:10543', 'clip21:13406', 'clip21:14088', 'clip21:14525', 'clip21:14687', 'clip21:1731', 'clip21:12874', 'contopt:5719']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'fuzzythes:23298', 'glosa': '', 'decision': 'RT', 'members': ['consignado', 'constante', 'imudável', 'imutável', 'invariável', 'manente', 'incessável', 'estável', 'ininterrompido', 'aturado', 'afio', 'incessante', 'perseverante', 'permanente', 'continuado', 'imanente', 'escrito', 'ininterrupto', 'jazente', 'permanecente', 'contínuo', 'diamantino', 'estóico', 'assíduo', 'seguido', 'firme', 'sistemático', 'uniforme', 'jacente', 'sucessivo', 'adamantino', 'persistente', 'porfioso', 'mencionado', 'perene', 'metódico', 'perpétuo', 'ordenado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25600', 'glosa': '', 'decision': 'RT', 'members': ['unímodo', 'uniforme', 'homótono', 'equável', 'homogéneo', 'monótono', 'recto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26445', 'glosa': '', 'decision': 'RT', 'members': ['homogéneo', 'unívoco', 'similar', 'inequívoco', 'uniforme', 'análogo', 'idêntico', 'contínuo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27091', 'glosa': '', 'decision': 'RT', 'members': ['inflexivo', 'invariável', 'intemporal', 'imudável', 'estereotipado', 'imutável', 'constante', 'imaterial', 'irretratável', 'estereótipo', 'imóvel', 'eterno', 'uniforme', 'inalterável', 'estável']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:2945', 'glosa': '', 'decision': 'UF', 'members': ['homótono', 'invariável', 'monótono', 'uniforme']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:15521', 'glosa': '', 'decision': 'UF', 'members': ['uniformador', 'uniformizador']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **60**

| Termo | Offsets ILI |
|-------|-------------|
| adamantino | fuzzythes:23298 |
| afio | fuzzythes:23298 |
| análogo | fuzzythes:26445 |
| assíduo | fuzzythes:23298 |
| aturado | fuzzythes:23298 |
| consignado | fuzzythes:23298 |
| constante | fuzzythes:23298, fuzzythes:27091 |
| continuado | fuzzythes:23298 |
| contínuo | fuzzythes:23298, fuzzythes:26445 |
| diamantino | fuzzythes:23298 |
| equável | fuzzythes:25600, ontopt06:2131, polaridades:1656 |
| escrito | fuzzythes:23298 |
| estável | fuzzythes:23298, fuzzythes:27091 |
| estereotipado | fuzzythes:27091 |
| estereótipo | fuzzythes:27091 |
| estóico | fuzzythes:23298 |
| eterno | fuzzythes:27091 |
| firme | fuzzythes:23298 |
| homogéneo | fuzzythes:25600, fuzzythes:26445 |
| homótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| idêntico | fuzzythes:26445 |
| imanente | fuzzythes:23298 |
| imaterial | fuzzythes:27091 |
| imóvel | fuzzythes:27091 |
| imudável | fuzzythes:23298, fuzzythes:27091 |
| imutável | fuzzythes:23298, fuzzythes:27091 |
| inalterável | fuzzythes:27091 |
| incessante | fuzzythes:23298 |
| incessável | fuzzythes:23298 |
| inequívoco | fuzzythes:26445 |
| inflexivo | fuzzythes:27091 |
| ininterrompido | fuzzythes:23298 |
| ininterrupto | fuzzythes:23298 |
| intemporal | fuzzythes:27091 |
| invariável | fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 |
| irretratável | fuzzythes:27091 |
| jacente | fuzzythes:23298 |
| jazente | fuzzythes:23298 |
| manente | fuzzythes:23298 |
| mencionado | fuzzythes:23298 |
| metódico | fuzzythes:23298 |
| monótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| ordenado | fuzzythes:23298 |
| perene | fuzzythes:23298 |
| permanecente | fuzzythes:23298 |
| permanente | fuzzythes:23298 |
| perpétuo | fuzzythes:23298 |
| perseverante | fuzzythes:23298 |
| persistente | fuzzythes:23298 |
| porfioso | fuzzythes:23298 |
| recto | fuzzythes:25600 |
| seguido | fuzzythes:23298 |
| similar | fuzzythes:26445 |
| sistemático | fuzzythes:23298 |
| sucessivo | fuzzythes:23298 |
| uniformador | clip21:15521 |
| uniforme | fuzzythes:23298, fuzzythes:25600, fuzzythes:26445, fuzzythes:27091, ontopt06:2131, ontopt06:2133, ontopt06:2945, polaridades:1656, polaridades:4484 |
| uniformizador | clip21:15521 |
| unímodo | fuzzythes:25600, ontopt06:2133 |
| unívoco | fuzzythes:26445 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **38**  ·  nucleares (peso ≥ 0.5): **17**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **21**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **61**

### Admitidos por corroboração
| Termo | Coocorrência | Nuclear | Peso máx. | Synsets |
|-------|--------------|---------|-----------|---------|
| firme | 5 | True | 3.056 | contopt:10331, contopt:27200, contopt:28395, contopt:5675, contopt:8553 |
| imóvel | 4 | True | 0.286 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| inalterável | 4 | True | 2.333 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| estável | 3 | True | 2.167 | contopt:10331, contopt:28395, contopt:6511 |
| jacente | 3 | True | 0.25 | contopt:10331, contopt:28395, contopt:6511 |
| imutável | 3 | True | 0.432 | contopt:10331, contopt:28395, contopt:6511 |
| persistente | 3 | True | 0.963 | contopt:10331, contopt:28395, contopt:8553 |
| assíduo | 2 | True | 1.0 | contopt:28395, contopt:5675 |
| ordenado | 2 | True | 1.286 | contopt:15361, contopt:9502 |
| metódico | 2 | True | 1.071 | contopt:15361, contopt:9502 |
| manente | 2 | True | 0.295 | contopt:10331, contopt:28395 |
| permanente | 2 | True | 1.273 | contopt:10331, contopt:28395 |
| perseverante | 2 | True | 0.211 | contopt:10331, contopt:8553 |
| permanecente | 2 | True | 0.211 | contopt:10331, contopt:28395 |
| estóico | 2 | True | 0.286 | contopt:10331, contopt:6511 |
| eterno | 2 | True | 0.429 | contopt:28395, contopt:6511 |
| perpétuo | 2 | True | 1.136 | contopt:28395, contopt:6511 |
| contínuo | 2 | True | 1.795 | contopt:27944, contopt:28395 |
| monótono | 2 | True | 0.417 | contopt:15361, contopt:30149 |
| idêntico | 2 | True | 1.082 | contopt:15361, contopt:16491 |
| porfioso | 2 | True | 0.762 | contopt:28395, contopt:8553 |

### Sinalização (revisão humana — NÃO admitidos)
| Termo | Coocorrência | Peso máx. |
|-------|--------------|-----------|
| monotonia | 4 | 1.25 |
| fiel | 3 | 1.125 |
| seguro | 3 | 2.278 |
| regular | 3 | 1.727 |
| igual | 3 | 0.852 |
| conformidade | 3 | 1.0 |
| cotidianidade | 3 | 0.538 |
| quotidianidade | 3 | 0.538 |
| unissonância | 3 | 0.286 |
| verdadeiro | 2 | 2.125 |
| certo | 2 | 0.485 |
| confiável | 2 | 0.438 |
| leal | 2 | 0.438 |
| efetivo | 2 | 0.242 |
| monotonamente | 2 | 1.0 |
| unanimemente | 2 | 1.25 |
| fixo | 2 | 2.278 |
| inabalável | 2 | 1.0 |
| duradouro | 2 | 0.316 |
| agarrado | 2 | 0.211 |
| indestrutível | 2 | 0.571 |
| resistente | 2 | 0.9 |
| aferrado | 2 | 0.925 |
| afincado | 2 | 0.787 |
| apegado | 2 | 0.111 |
| tenaz | 2 | 0.975 |
| impassível | 2 | 3.333 |
| imperturbável | 2 | 2.667 |
| insensível | 2 | 0.571 |
| obstinado | 2 | 1.438 |
| pertinaz | 2 | 1.325 |
| perpetuamente | 2 | 1.556 |
| eternamente | 2 | 1.333 |
| para sempre | 2 | 1.222 |
| sempre | 2 | 1.529 |
| perenemente | 2 | 0.444 |
| continuamente | 2 | 1.882 |
| permanentemente | 2 | 0.3 |
| incessantemente | 2 | 1.529 |
| igualdade | 2 | 1.421 |
| identidade | 2 | 0.842 |
| correspondência | 2 | 0.842 |
| semelhança | 2 | 2.412 |
| paridade | 2 | 0.941 |
| paralelismo | 2 | 0.316 |
| afinidade | 2 | 0.667 |
| similitude | 2 | 1.294 |
| regularidade | 2 | 1.267 |
| coerência | 2 | 0.154 |
| relação | 2 | 0.278 |
| constância | 2 | 3.0 |
| fixidez | 2 | 0.4 |
| imobilidade | 2 | 0.4 |
| platitude | 2 | 0.846 |
| harmonioso | 2 | 1.222 |
| harmónico | 2 | 0.333 |
| frequente | 2 | 1.227 |
| periódico | 2 | 0.167 |
| habitual | 2 | 0.167 |
| ordinário | 2 | 1.0 |
| moderado | 2 | 0.333 |

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT
- Termos **admitidos** (decisão humana completa): **59**
- Termos **pendentes** (aguardam decisão humana): **0**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| consignado | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| constante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imudável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imutável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| invariável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| manente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| incessável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| estável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrompido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| aturado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| afio | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| incessante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perseverante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| permanente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| continuado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| imanente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| escrito | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrupto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| jazente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| permanecente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| contínuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298, fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| diamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| estóico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| assíduo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| seguido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| firme | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| sistemático | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| jacente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| sucessivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| adamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| persistente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| porfioso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| mencionado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perene | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| metódico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perpétuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| ordenado | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| unímodo | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2133 | derivado do sentido (PASSO 3) | sense_decision |
| homótono | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| equável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2131, polaridades:1656 | derivado do sentido (PASSO 3) | sense_decision |
| homogéneo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| monótono | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| recto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600 | derivado do sentido (PASSO 3) | sense_decision |
| unívoco | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| similar | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| inequívoco | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| análogo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| idêntico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| inflexivo | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| intemporal | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| estereotipado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imaterial | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| irretratável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| estereótipo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imóvel | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| eterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| inalterável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| uniformador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |
| uniformizador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **uniforme**
- `skos:altLabel` (UF) → equável, homótono, invariável, monótono, uniformador, uniformizador, unímodo
- `:termoRelacionado` (RT) → adamantino, afio, análogo, assíduo, aturado, consignado, constante, continuado, contínuo, diamantino, escrito, estereotipado, estereótipo, estável, estóico, eterno, firme, homogéneo, idêntico, imanente, imaterial, imudável, imutável, imóvel, inalterável, incessante, incessável, inequívoco, inflexivo, ininterrompido, ininterrupto, intemporal, irretratável, jacente, jazente, manente, mencionado, metódico, ordenado, perene, permanecente, permanente, perpétuo, perseverante, persistente, porfioso, recto, seguido, similar, sistemático, sucessivo, unívoco

_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada como relação SKOS._
