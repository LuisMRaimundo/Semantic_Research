# Fase 0 — Relatório de selecção lexical: **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Base de corroboração:** `C:\Users\lmr20\Desktop\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-07-27T12:38:24
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2945', 'clip21:15521', 'clip21:20421'] |
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
- Synsets admitidos (on-axis): `['contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2131', 'ontopt06:2133', 'ontopt06:2945', 'polaridades:1656', 'polaridades:4484', 'clip21:15521', 'clip21:20421']`
- Synsets excluídos (off-axis): `['clip01:6948', 'clip21:12405', 'clip21:16596', 'clip21:17576', 'clip21:17930', 'clip21:19004', 'clip21:19228', 'clip21:19272', 'clip21:19790', 'contopt:9180', 'contopt:9502', 'contopt:15361', 'contopt:16491', 'fuzzythes:1661', 'fuzzythes:1920', 'fuzzythes:2140', 'fuzzythes:3480', 'fuzzythes:23180', 'fuzzythes:23495', 'fuzzythes:23527', 'fuzzythes:24915', 'fuzzythes:26484', 'fuzzythes:27110', 'ontopt06:787', 'ontopt06:803', 'ontopt06:1186', 'ontopt06:28292', 'polaridades:4425', 'polaridades:5083', 'polaridades:5938', 'clip01:3425', 'clip01:4659', 'clip01:7405', 'clip01:1043', 'clip21:18187', 'clip21:19074', 'clip21:16541', 'clip21:8149', 'clip21:14314', 'clip21:14562', 'clip21:19940', 'clip21:20073', 'clip21:1403', 'clip21:5416', 'clip21:6019', 'clip21:7565', 'clip21:7750', 'clip21:9132', 'clip21:10543', 'clip21:13406', 'clip21:14088', 'clip21:14525', 'clip21:14687', 'clip21:1731', 'clip21:12874', 'contopt:5719']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'contopt:28395', 'glosa': '', 'decision': 'RT', 'members': ['contínuo', 'constante', 'ininterrupto', 'sucessivo', 'permanente', 'frequente', 'incessante', 'perpétuo', 'continuado', 'assíduo', 'seguido', 'perene', 'aturado', 'porfioso', 'incessável', 'ininterrompido', 'afio', 'consecutivo', 'estável', 'imutável', 'imudável', 'invariável', 'amiudado', 'repetido', 'manente', 'duradouro', 'imediato', 'jacente', 'conseguinte', 'subsecutivo', 'persistente', 'eterno', 'miúdo', 'vitalício', 'firme', 'inalterável', 'infindável', 'regular', 'crebro', 'periódico', 'permanecente', 'diligente', 'fiel', 'sempiterno', 'jazente', 'reiterado', 'sem paradas', 'aplicado', 'habitual', 'imóvel', 'ordinário', 'uniforme', 'usual']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23298', 'glosa': '', 'decision': 'RT', 'members': ['consignado', 'constante', 'imudável', 'imutável', 'invariável', 'manente', 'incessável', 'estável', 'ininterrompido', 'aturado', 'afio', 'incessante', 'perseverante', 'permanente', 'continuado', 'imanente', 'escrito', 'ininterrupto', 'jazente', 'permanecente', 'contínuo', 'diamantino', 'estóico', 'assíduo', 'seguido', 'firme', 'sistemático', 'uniforme', 'jacente', 'sucessivo', 'adamantino', 'persistente', 'porfioso', 'mencionado', 'perene', 'metódico', 'perpétuo', 'ordenado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25600', 'glosa': '', 'decision': 'RT', 'members': ['unímodo', 'uniforme', 'homótono', 'equável', 'homogéneo', 'monótono', 'recto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26445', 'glosa': '', 'decision': 'RT', 'members': ['homogéneo', 'unívoco', 'similar', 'inequívoco', 'uniforme', 'análogo', 'idêntico', 'contínuo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27091', 'glosa': '', 'decision': 'RT', 'members': ['inflexivo', 'invariável', 'intemporal', 'imudável', 'estereotipado', 'imutável', 'constante', 'imaterial', 'irretratável', 'estereótipo', 'imóvel', 'eterno', 'uniforme', 'inalterável', 'estável']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:2945', 'glosa': '', 'decision': 'UF', 'members': ['homótono', 'invariável', 'monótono', 'uniforme']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:15521', 'glosa': '', 'decision': 'UF', 'members': ['uniformador', 'uniformizador']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:20421', 'glosa': '', 'decision': 'RT', 'members': ['inalteravelmente', 'uniformemente', 'de maneira justa', 'imutavelmente', 'monotonamente', 'unanimemente']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **89**

| Termo | Offsets ILI |
|-------|-------------|
| adamantino | fuzzythes:23298 |
| afio | contopt:28395, fuzzythes:23298 |
| amiudado | contopt:28395 |
| análogo | fuzzythes:26445 |
| aplicado | contopt:28395 |
| assíduo | contopt:28395, fuzzythes:23298 |
| aturado | contopt:28395, fuzzythes:23298 |
| consecutivo | contopt:28395 |
| conseguinte | contopt:28395 |
| consignado | fuzzythes:23298 |
| constante | contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| continuado | contopt:28395, fuzzythes:23298 |
| contínuo | contopt:28395, fuzzythes:23298, fuzzythes:26445 |
| crebro | contopt:28395 |
| de maneira justa | clip21:20421 |
| diamantino | fuzzythes:23298 |
| diligente | contopt:28395 |
| duradouro | contopt:28395 |
| equável | fuzzythes:25600, ontopt06:2131, polaridades:1656 |
| escrito | fuzzythes:23298 |
| estável | contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| estereotipado | fuzzythes:27091 |
| estereótipo | fuzzythes:27091 |
| estóico | fuzzythes:23298 |
| eterno | contopt:28395, fuzzythes:27091 |
| fiel | contopt:28395 |
| firme | contopt:28395, fuzzythes:23298 |
| frequente | contopt:28395 |
| habitual | contopt:28395 |
| homogéneo | fuzzythes:25600, fuzzythes:26445 |
| homótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| idêntico | fuzzythes:26445 |
| imanente | fuzzythes:23298 |
| imaterial | fuzzythes:27091 |
| imediato | contopt:28395 |
| imóvel | contopt:28395, fuzzythes:27091 |
| imudável | contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| imutável | contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| imutavelmente | clip21:20421 |
| inalterável | contopt:28395, fuzzythes:27091 |
| inalteravelmente | clip21:20421 |
| incessante | contopt:28395, fuzzythes:23298 |
| incessável | contopt:28395, fuzzythes:23298 |
| inequívoco | fuzzythes:26445 |
| infindável | contopt:28395 |
| inflexivo | fuzzythes:27091 |
| ininterrompido | contopt:28395, fuzzythes:23298 |
| ininterrupto | contopt:28395, fuzzythes:23298 |
| intemporal | fuzzythes:27091 |
| invariável | contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 |
| irretratável | fuzzythes:27091 |
| jacente | contopt:28395, fuzzythes:23298 |
| jazente | contopt:28395, fuzzythes:23298 |
| manente | contopt:28395, fuzzythes:23298 |
| mencionado | fuzzythes:23298 |
| metódico | fuzzythes:23298 |
| miúdo | contopt:28395 |
| monotonamente | clip21:20421 |
| monótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| ordenado | fuzzythes:23298 |
| ordinário | contopt:28395 |
| perene | contopt:28395, fuzzythes:23298 |
| periódico | contopt:28395 |
| permanecente | contopt:28395, fuzzythes:23298 |
| permanente | contopt:28395, fuzzythes:23298 |
| perpétuo | contopt:28395, fuzzythes:23298 |
| perseverante | fuzzythes:23298 |
| persistente | contopt:28395, fuzzythes:23298 |
| porfioso | contopt:28395, fuzzythes:23298 |
| recto | fuzzythes:25600 |
| regular | contopt:28395 |
| reiterado | contopt:28395 |
| repetido | contopt:28395 |
| seguido | contopt:28395, fuzzythes:23298 |
| sem paradas | contopt:28395 |
| sempiterno | contopt:28395 |
| similar | fuzzythes:26445 |
| sistemático | fuzzythes:23298 |
| subsecutivo | contopt:28395 |
| sucessivo | contopt:28395, fuzzythes:23298 |
| unanimemente | clip21:20421 |
| uniformador | clip21:15521 |
| uniforme | contopt:28395, fuzzythes:23298, fuzzythes:25600, fuzzythes:26445, fuzzythes:27091, ontopt06:2131, ontopt06:2133, ontopt06:2945, polaridades:1656, polaridades:4484 |
| uniformemente | clip21:20421 |
| uniformizador | clip21:15521 |
| unímodo | fuzzythes:25600, ontopt06:2133 |
| unívoco | fuzzythes:26445 |
| usual | contopt:28395 |
| vitalício | contopt:28395 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **38**  ·  nucleares (peso ≥ 0.5): **17**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **30**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **52**

### Admitidos por corroboração
| Termo | Coocorrência | Nuclear | Peso máx. | Synsets |
|-------|--------------|---------|-----------|---------|
| firme | 5 | True | 3.056 | contopt:10331, contopt:27200, contopt:28395, contopt:5675, contopt:8553 |
| inalterável | 4 | True | 2.333 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| imóvel | 4 | True | 0.286 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| regular | 3 | True | 1.727 | contopt:15361, contopt:28395, contopt:9502 |
| imutável | 3 | True | 0.432 | contopt:10331, contopt:28395, contopt:6511 |
| jacente | 3 | True | 0.25 | contopt:10331, contopt:28395, contopt:6511 |
| estável | 3 | True | 2.167 | contopt:10331, contopt:28395, contopt:6511 |
| persistente | 3 | True | 0.963 | contopt:10331, contopt:28395, contopt:8553 |
| fiel | 3 | True | 1.125 | contopt:10331, contopt:28395, contopt:5675 |
| ordenado | 2 | True | 1.286 | contopt:15361, contopt:9502 |
| metódico | 2 | True | 1.071 | contopt:15361, contopt:9502 |
| contínuo | 2 | True | 1.795 | contopt:27944, contopt:28395 |
| unanimemente | 2 | True | 1.25 | contopt:21106, contopt:5990 |
| monotonamente | 2 | True | 1.0 | contopt:21106, contopt:29177 |
| eterno | 2 | True | 0.429 | contopt:28395, contopt:6511 |
| estóico | 2 | True | 0.286 | contopt:10331, contopt:6511 |
| perpétuo | 2 | True | 1.136 | contopt:28395, contopt:6511 |
| permanente | 2 | True | 1.273 | contopt:10331, contopt:28395 |
| frequente | 2 | True | 1.227 | contopt:15361, contopt:28395 |
| assíduo | 2 | True | 1.0 | contopt:28395, contopt:5675 |
| porfioso | 2 | True | 0.762 | contopt:28395, contopt:8553 |
| manente | 2 | True | 0.295 | contopt:10331, contopt:28395 |
| duradouro | 2 | True | 0.316 | contopt:10331, contopt:28395 |
| periódico | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| permanecente | 2 | True | 0.211 | contopt:10331, contopt:28395 |
| habitual | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| ordinário | 2 | True | 1.0 | contopt:15361, contopt:28395 |
| perseverante | 2 | True | 0.211 | contopt:10331, contopt:8553 |
| monótono | 2 | True | 0.417 | contopt:15361, contopt:30149 |
| idêntico | 2 | True | 1.082 | contopt:15361, contopt:16491 |

### Sinalização (revisão humana — NÃO admitidos)
| Termo | Coocorrência | Peso máx. |
|-------|--------------|-----------|
| monotonia | 4 | 1.25 |
| unissonância | 3 | 0.286 |
| cotidianidade | 3 | 0.538 |
| quotidianidade | 3 | 0.538 |
| conformidade | 3 | 1.0 |
| igual | 3 | 0.852 |
| seguro | 3 | 2.278 |
| continuamente | 2 | 1.882 |
| incessantemente | 2 | 1.529 |
| sempre | 2 | 1.529 |
| eternamente | 2 | 1.333 |
| permanentemente | 2 | 0.3 |
| perpetuamente | 2 | 1.556 |
| para sempre | 2 | 1.222 |
| perenemente | 2 | 0.444 |
| regularidade | 2 | 1.267 |
| impassível | 2 | 3.333 |
| imperturbável | 2 | 2.667 |
| inabalável | 2 | 1.0 |
| indestrutível | 2 | 0.571 |
| insensível | 2 | 0.571 |
| fixo | 2 | 2.278 |
| certo | 2 | 0.485 |
| efetivo | 2 | 0.242 |
| agarrado | 2 | 0.211 |
| resistente | 2 | 0.9 |
| aferrado | 2 | 0.925 |
| afincado | 2 | 0.787 |
| apegado | 2 | 0.111 |
| confiável | 2 | 0.438 |
| tenaz | 2 | 0.975 |
| leal | 2 | 0.438 |
| obstinado | 2 | 1.438 |
| verdadeiro | 2 | 2.125 |
| pertinaz | 2 | 1.325 |
| constância | 2 | 3.0 |
| fixidez | 2 | 0.4 |
| imobilidade | 2 | 0.4 |
| coerência | 2 | 0.154 |
| semelhança | 2 | 2.412 |
| similitude | 2 | 1.294 |
| paridade | 2 | 0.941 |
| afinidade | 2 | 0.667 |
| igualdade | 2 | 1.421 |
| relação | 2 | 0.278 |
| paralelismo | 2 | 0.316 |
| correspondência | 2 | 0.842 |
| moderado | 2 | 0.333 |
| harmónico | 2 | 0.333 |
| harmonioso | 2 | 1.222 |
| identidade | 2 | 0.842 |
| platitude | 2 | 0.846 |

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT
- Termos **admitidos** (decisão humana completa): **88**
- Termos **pendentes** (aguardam decisão humana): **1**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| contínuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395, fuzzythes:23298, fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| constante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrupto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| sucessivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| permanente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| frequente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| incessante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perpétuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| continuado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| assíduo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| seguido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perene | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| aturado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| porfioso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| incessável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrompido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| afio | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| consecutivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| estável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imutável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imudável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| invariável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| amiudado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| repetido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| manente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| duradouro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| imediato | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| jacente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| conseguinte | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| subsecutivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| persistente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| eterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| miúdo | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| vitalício | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| firme | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| inalterável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| infindável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| regular | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| crebro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| periódico | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| permanecente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| diligente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| fiel | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| sempiterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| jazente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| reiterado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| sem paradas | RT | invariância face a um parâmetro | clip21, contopt | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| aplicado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| habitual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| imóvel | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| ordinário | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| usual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| consignado | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perseverante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| imanente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| escrito | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| diamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| estóico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| sistemático | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| adamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| mencionado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| metódico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
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
| uniformador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |
| uniformizador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |
| inalteravelmente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| uniformemente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| de maneira justa | RT | invariância face a um parâmetro | clip21, contopt | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| imutavelmente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| monotonamente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| unanimemente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |

### Pendentes (necessitam de decisão na spec `adjudication`)
politípica

## §6 — Mapeamento SKOS-XL / OWL (só Bloco A)
- `skos:prefLabel` → **uniforme**
- `skosxl:altLabel` (UF) → equável, homótono, invariável, monótono, uniformador, uniformizador, unímodo
- `:termoRelacionado` (RT) → adamantino, afio, amiudado, análogo, aplicado, assíduo, aturado, consecutivo, conseguinte, consignado, constante, continuado, contínuo, crebro, de maneira justa, diamantino, diligente, duradouro, escrito, estereotipado, estereótipo, estável, estóico, eterno, fiel, firme, frequente, habitual, homogéneo, idêntico, imanente, imaterial, imediato, imudável, imutavelmente, imutável, imóvel, inalteravelmente, inalterável, incessante, incessável, inequívoco, infindável, inflexivo, ininterrompido, ininterrupto, intemporal, irretratável, jacente, jazente, manente, mencionado, metódico, miúdo, monotonamente, ordenado, ordinário, perene, periódico, permanecente, permanente, perpétuo, perseverante, persistente, porfioso, recto, regular, reiterado, repetido, seguido, sem paradas, sempiterno, similar, sistemático, subsecutivo, sucessivo, unanimemente, uniformemente, unívoco, usual, vitalício

_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada como relação SKOS/SKOS-XL._
