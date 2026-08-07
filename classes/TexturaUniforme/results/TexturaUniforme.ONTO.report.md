# Fase 0 — Relatório de selecção lexical: **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Base de corroboração:** `E:\PYTHON CODES\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-08-07T14:10:58
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:19004', 'contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2945', 'clip21:15521', 'clip21:20421'] |
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
- Synsets admitidos (on-axis): `['clip21:19004', 'contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2131', 'ontopt06:2133', 'ontopt06:2945', 'polaridades:1656', 'polaridades:4484', 'clip21:15521', 'clip21:20421']`
- Synsets excluídos (off-axis): `['clip01:6948', 'clip21:12405', 'clip21:16596', 'clip21:17576', 'clip21:17930', 'clip21:19228', 'clip21:19272', 'clip21:19790', 'contopt:9180', 'contopt:9502', 'contopt:15361', 'contopt:16491', 'fuzzythes:1661', 'fuzzythes:1920', 'fuzzythes:2140', 'fuzzythes:3480', 'fuzzythes:23180', 'fuzzythes:23495', 'fuzzythes:23527', 'fuzzythes:24915', 'fuzzythes:26484', 'fuzzythes:27110', 'ontopt06:787', 'ontopt06:803', 'ontopt06:1186', 'ontopt06:28292', 'polaridades:4425', 'polaridades:5083', 'polaridades:5938', 'clip01:3425', 'clip01:4659', 'clip01:7405', 'clip01:1043', 'clip21:18187', 'clip21:19074', 'clip21:16541', 'clip21:8149', 'clip21:14314', 'clip21:14562', 'clip21:19940', 'clip21:20073', 'clip21:1403', 'clip21:5416', 'clip21:6019', 'clip21:7565', 'clip21:7750', 'clip21:9132', 'clip21:10543', 'clip21:13406', 'clip21:14088', 'clip21:14525', 'clip21:14687', 'clip21:1731', 'clip21:12874', 'contopt:5719']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:19004', 'glosa': '', 'decision': 'RT', 'members': ['contínuo', 'constante', 'ininterrupto', 'sucessivo', 'permanente', 'frequente', 'incessante', 'perpétuo', 'continuado', 'assíduo', 'seguido', 'perene', 'aturado', 'porfioso', 'incessável', 'ininterrompido', 'afio', 'consecutivo', 'estável', 'imutável', 'imudável', 'invariável', 'amiudado', 'repetido', 'manente', 'duradouro', 'imediato', 'jacente', 'conseguinte', 'subsecutivo', 'persistente', 'eterno', 'miúdo', 'vitalício', 'firme', 'inalterável', 'infindável', 'regular', 'crebro', 'periódico', 'permanecente', 'diligente', 'fiel', 'sempiterno', 'jazente', 'reiterado', 'sem paradas', 'aplicado', 'habitual', 'imóvel', 'ordinário', 'uniforme', 'usual', 'áfio', 'comum', 'consequente', 'consistente', 'duplicado', 'duradoiro', 'mencionado', 'perdurável', 'perenal', 'pontual', 'renovado', 'seguinte', 'usado', 'contino', 'redito', 'definitivo', 'esforçado', 'imanente', 'inabalável', 'interminável', 'irretratável', 'iterativo', 'monótono', 'perseverante', 'acontecedeiro', 'consignado', 'freqüente', 'inflexivo', 'invariante', 'jornal', 'periodico', 'por toda vida', 'sequencial', 'acostumado', 'adotado', 'atento', 'atilado', 'cadimo', 'consueto', 'consuetudinário', 'correntio', 'costumado', 'costumeiro', 'costumário', 'durador', 'durável', 'escrito', 'escrupuloso', 'exato', 'futuro', 'incansável', 'irretractável', 'irrevogável', 'metódico', 'ordenado', 'pertinaz', 'religioso', 'rente', 'resultante', 'rotineiro', 'rítmico', 'sólito', 'tenaz', 'vulgar', 'acompanhado', 'activo', 'adamantino', 'adoptado', 'alterno', 'ativo', 'coerente', 'crónico', 'cíclico', 'deitado', 'durativo', 'efectivo', 'escolhido', 'estendido', 'estereotipado', 'eterna', 'eternas', 'eternos', 'fixo', 'frequentado', 'hereditário', 'homogéneo', 'imperecível', 'inamovível', 'inextinguível', 'infinita', 'infinito', 'intemporal', 'intermitente', 'laborioso', 'localizado', 'matraqueado', 'normal', 'novo', 'nutrido', 'ocasional', 'operoso', 'pegado', 'porfiado', 'próximo', 'recalcado', 'revezado', 'sazonal', 'seguro', 'sem idade', 'sistemático', 'situado', 'sucedido', 'sínoco', 'trabalhador', 'trilhado', 'ulterior', 'unânime', 'vital']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:28395', 'glosa': '', 'decision': 'RT', 'members': ['contínuo', 'constante', 'ininterrupto', 'sucessivo', 'permanente', 'frequente', 'incessante', 'perpétuo', 'continuado', 'assíduo', 'seguido', 'perene', 'aturado', 'porfioso', 'incessável', 'ininterrompido', 'afio', 'consecutivo', 'estável', 'imutável', 'imudável', 'invariável', 'amiudado', 'repetido', 'manente', 'duradouro', 'imediato', 'jacente', 'conseguinte', 'subsecutivo', 'persistente', 'eterno', 'miúdo', 'vitalício', 'firme', 'inalterável', 'infindável', 'regular', 'crebro', 'periódico', 'permanecente', 'diligente', 'fiel', 'sempiterno', 'jazente', 'reiterado', 'sem paradas', 'aplicado', 'habitual', 'imóvel', 'ordinário', 'uniforme', 'usual']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23298', 'glosa': '', 'decision': 'RT', 'members': ['consignado', 'constante', 'imudável', 'imutável', 'invariável', 'manente', 'incessável', 'estável', 'ininterrompido', 'aturado', 'afio', 'incessante', 'perseverante', 'permanente', 'continuado', 'imanente', 'escrito', 'ininterrupto', 'jazente', 'permanecente', 'contínuo', 'diamantino', 'estóico', 'assíduo', 'seguido', 'firme', 'sistemático', 'uniforme', 'jacente', 'sucessivo', 'adamantino', 'persistente', 'porfioso', 'mencionado', 'perene', 'metódico', 'perpétuo', 'ordenado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25600', 'glosa': '', 'decision': 'RT', 'members': ['unímodo', 'uniforme', 'homótono', 'equável', 'homogéneo', 'monótono', 'recto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26445', 'glosa': '', 'decision': 'RT', 'members': ['homogéneo', 'unívoco', 'similar', 'inequívoco', 'uniforme', 'análogo', 'idêntico', 'contínuo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27091', 'glosa': '', 'decision': 'RT', 'members': ['inflexivo', 'invariável', 'intemporal', 'imudável', 'estereotipado', 'imutável', 'constante', 'imaterial', 'irretratável', 'estereótipo', 'imóvel', 'eterno', 'uniforme', 'inalterável', 'estável']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:2945', 'glosa': '', 'decision': 'UF', 'members': ['homótono', 'invariável', 'monótono', 'uniforme']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:15521', 'glosa': '', 'decision': 'UF', 'members': ['uniformador', 'uniformizador']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:20421', 'glosa': '', 'decision': 'RT', 'members': ['inalteravelmente', 'uniformemente', 'de maneira justa', 'imutavelmente', 'monotonamente', 'unanimemente']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **189**

| Termo | Offsets ILI |
|-------|-------------|
| acompanhado | clip21:19004 |
| acontecedeiro | clip21:19004 |
| acostumado | clip21:19004 |
| activo | clip21:19004 |
| adamantino | clip21:19004, fuzzythes:23298 |
| adoptado | clip21:19004 |
| adotado | clip21:19004 |
| afio | clip21:19004, contopt:28395, fuzzythes:23298 |
| alterno | clip21:19004 |
| amiudado | clip21:19004, contopt:28395 |
| análogo | fuzzythes:26445 |
| aplicado | clip21:19004, contopt:28395 |
| assíduo | clip21:19004, contopt:28395, fuzzythes:23298 |
| atento | clip21:19004 |
| atilado | clip21:19004 |
| ativo | clip21:19004 |
| aturado | clip21:19004, contopt:28395, fuzzythes:23298 |
| cadimo | clip21:19004 |
| cíclico | clip21:19004 |
| coerente | clip21:19004 |
| comum | clip21:19004 |
| consecutivo | clip21:19004, contopt:28395 |
| conseguinte | clip21:19004, contopt:28395 |
| consequente | clip21:19004 |
| consignado | clip21:19004, fuzzythes:23298 |
| consistente | clip21:19004 |
| constante | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| consueto | clip21:19004 |
| consuetudinário | clip21:19004 |
| contino | clip21:19004 |
| continuado | clip21:19004, contopt:28395, fuzzythes:23298 |
| contínuo | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:26445 |
| correntio | clip21:19004 |
| costumado | clip21:19004 |
| costumário | clip21:19004 |
| costumeiro | clip21:19004 |
| crebro | clip21:19004, contopt:28395 |
| crónico | clip21:19004 |
| de maneira justa | clip21:20421 |
| definitivo | clip21:19004 |
| deitado | clip21:19004 |
| diamantino | fuzzythes:23298 |
| diligente | clip21:19004, contopt:28395 |
| duplicado | clip21:19004 |
| duradoiro | clip21:19004 |
| durador | clip21:19004 |
| duradouro | clip21:19004, contopt:28395 |
| durativo | clip21:19004 |
| durável | clip21:19004 |
| efectivo | clip21:19004 |
| equável | fuzzythes:25600, ontopt06:2131, polaridades:1656 |
| escolhido | clip21:19004 |
| escrito | clip21:19004, fuzzythes:23298 |
| escrupuloso | clip21:19004 |
| esforçado | clip21:19004 |
| estável | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| estendido | clip21:19004 |
| estereotipado | clip21:19004, fuzzythes:27091 |
| estereótipo | fuzzythes:27091 |
| estóico | fuzzythes:23298 |
| eterna | clip21:19004 |
| eternas | clip21:19004 |
| eterno | clip21:19004, contopt:28395, fuzzythes:27091 |
| eternos | clip21:19004 |
| exato | clip21:19004 |
| fiel | clip21:19004, contopt:28395 |
| firme | clip21:19004, contopt:28395, fuzzythes:23298 |
| fixo | clip21:19004 |
| frequentado | clip21:19004 |
| frequente | clip21:19004, contopt:28395 |
| futuro | clip21:19004 |
| habitual | clip21:19004, contopt:28395 |
| hereditário | clip21:19004 |
| homogéneo | clip21:19004, fuzzythes:25600, fuzzythes:26445 |
| homótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| idêntico | fuzzythes:26445 |
| imanente | clip21:19004, fuzzythes:23298 |
| imaterial | fuzzythes:27091 |
| imediato | clip21:19004, contopt:28395 |
| imóvel | clip21:19004, contopt:28395, fuzzythes:27091 |
| imperecível | clip21:19004 |
| imudável | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| imutável | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| imutavelmente | clip21:20421 |
| inabalável | clip21:19004 |
| inalterável | clip21:19004, contopt:28395, fuzzythes:27091 |
| inalteravelmente | clip21:20421 |
| inamovível | clip21:19004 |
| incansável | clip21:19004 |
| incessante | clip21:19004, contopt:28395, fuzzythes:23298 |
| incessável | clip21:19004, contopt:28395, fuzzythes:23298 |
| inequívoco | fuzzythes:26445 |
| inextinguível | clip21:19004 |
| infindável | clip21:19004, contopt:28395 |
| infinita | clip21:19004 |
| infinito | clip21:19004 |
| inflexivo | clip21:19004, fuzzythes:27091 |
| ininterrompido | clip21:19004, contopt:28395, fuzzythes:23298 |
| ininterrupto | clip21:19004, contopt:28395, fuzzythes:23298 |
| intemporal | clip21:19004, fuzzythes:27091 |
| interminável | clip21:19004 |
| intermitente | clip21:19004 |
| invariante | clip21:19004 |
| invariável | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 |
| irretractável | clip21:19004 |
| irretratável | clip21:19004, fuzzythes:27091 |
| irrevogável | clip21:19004 |
| iterativo | clip21:19004 |
| jacente | clip21:19004, contopt:28395, fuzzythes:23298 |
| jazente | clip21:19004, contopt:28395, fuzzythes:23298 |
| jornal | clip21:19004 |
| laborioso | clip21:19004 |
| localizado | clip21:19004 |
| manente | clip21:19004, contopt:28395, fuzzythes:23298 |
| matraqueado | clip21:19004 |
| mencionado | clip21:19004, fuzzythes:23298 |
| metódico | clip21:19004, fuzzythes:23298 |
| miúdo | clip21:19004, contopt:28395 |
| monotonamente | clip21:20421 |
| monótono | clip21:19004, fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| normal | clip21:19004 |
| novo | clip21:19004 |
| nutrido | clip21:19004 |
| ocasional | clip21:19004 |
| operoso | clip21:19004 |
| ordenado | clip21:19004, fuzzythes:23298 |
| ordinário | clip21:19004, contopt:28395 |
| pegado | clip21:19004 |
| perdurável | clip21:19004 |
| perenal | clip21:19004 |
| perene | clip21:19004, contopt:28395, fuzzythes:23298 |
| periódico | clip21:19004, contopt:28395 |
| permanecente | clip21:19004, contopt:28395, fuzzythes:23298 |
| permanente | clip21:19004, contopt:28395, fuzzythes:23298 |
| perpétuo | clip21:19004, contopt:28395, fuzzythes:23298 |
| perseverante | clip21:19004, fuzzythes:23298 |
| persistente | clip21:19004, contopt:28395, fuzzythes:23298 |
| pertinaz | clip21:19004 |
| pontual | clip21:19004 |
| por toda vida | clip21:19004 |
| porfiado | clip21:19004 |
| porfioso | clip21:19004, contopt:28395, fuzzythes:23298 |
| próximo | clip21:19004 |
| recalcado | clip21:19004 |
| recto | fuzzythes:25600 |
| redito | clip21:19004 |
| regular | clip21:19004, contopt:28395 |
| reiterado | clip21:19004, contopt:28395 |
| religioso | clip21:19004 |
| renovado | clip21:19004 |
| rente | clip21:19004 |
| repetido | clip21:19004, contopt:28395 |
| resultante | clip21:19004 |
| revezado | clip21:19004 |
| rítmico | clip21:19004 |
| rotineiro | clip21:19004 |
| sazonal | clip21:19004 |
| seguido | clip21:19004, contopt:28395, fuzzythes:23298 |
| seguinte | clip21:19004 |
| seguro | clip21:19004 |
| sem idade | clip21:19004 |
| sem paradas | clip21:19004, contopt:28395 |
| sempiterno | clip21:19004, contopt:28395 |
| sequencial | clip21:19004 |
| similar | fuzzythes:26445 |
| sínoco | clip21:19004 |
| sistemático | clip21:19004, fuzzythes:23298 |
| situado | clip21:19004 |
| sólito | clip21:19004 |
| subsecutivo | clip21:19004, contopt:28395 |
| sucedido | clip21:19004 |
| sucessivo | clip21:19004, contopt:28395, fuzzythes:23298 |
| tenaz | clip21:19004 |
| trabalhador | clip21:19004 |
| trilhado | clip21:19004 |
| ulterior | clip21:19004 |
| unânime | clip21:19004 |
| unanimemente | clip21:20421 |
| uniformador | clip21:15521 |
| uniforme | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:25600, fuzzythes:26445, fuzzythes:27091, ontopt06:2131, ontopt06:2133, ontopt06:2945, polaridades:1656, polaridades:4484 |
| uniformemente | clip21:20421 |
| uniformizador | clip21:15521 |
| unímodo | fuzzythes:25600, ontopt06:2133 |
| unívoco | fuzzythes:26445 |
| usado | clip21:19004 |
| usual | clip21:19004, contopt:28395 |
| vital | clip21:19004 |
| vitalício | clip21:19004, contopt:28395 |
| vulgar | clip21:19004 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **38**  ·  nucleares (peso ≥ 0.5): **17**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **35**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **47**

### Admitidos por corroboração
| Termo | Coocorrência | Nuclear | Peso máx. | Synsets |
|-------|--------------|---------|-----------|---------|
| firme | 5 | True | 3.056 | contopt:10331, contopt:27200, contopt:28395, contopt:5675, contopt:8553 |
| imóvel | 4 | True | 0.286 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| inalterável | 4 | True | 2.333 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| regular | 3 | True | 1.727 | contopt:15361, contopt:28395, contopt:9502 |
| persistente | 3 | True | 0.963 | contopt:10331, contopt:28395, contopt:8553 |
| seguro | 3 | True | 2.278 | contopt:10331, contopt:5675, contopt:8553 |
| estável | 3 | True | 2.167 | contopt:10331, contopt:28395, contopt:6511 |
| imutável | 3 | True | 0.432 | contopt:10331, contopt:28395, contopt:6511 |
| jacente | 3 | True | 0.25 | contopt:10331, contopt:28395, contopt:6511 |
| fiel | 3 | True | 1.125 | contopt:10331, contopt:28395, contopt:5675 |
| ordenado | 2 | True | 1.286 | contopt:15361, contopt:9502 |
| metódico | 2 | True | 1.071 | contopt:15361, contopt:9502 |
| ordinário | 2 | True | 1.0 | contopt:15361, contopt:28395 |
| monótono | 2 | True | 0.417 | contopt:15361, contopt:30149 |
| idêntico | 2 | True | 1.082 | contopt:15361, contopt:16491 |
| periódico | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| habitual | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| frequente | 2 | True | 1.227 | contopt:15361, contopt:28395 |
| fixo | 2 | True | 2.278 | contopt:10331, contopt:18050 |
| monotonamente | 2 | True | 1.0 | contopt:21106, contopt:29177 |
| unanimemente | 2 | True | 1.25 | contopt:21106, contopt:5990 |
| pertinaz | 2 | True | 1.325 | contopt:10331, contopt:8553 |
| tenaz | 2 | True | 0.975 | contopt:10331, contopt:8553 |
| porfioso | 2 | True | 0.762 | contopt:28395, contopt:8553 |
| perseverante | 2 | True | 0.211 | contopt:10331, contopt:8553 |
| contínuo | 2 | True | 1.795 | contopt:27944, contopt:28395 |
| permanente | 2 | True | 1.273 | contopt:10331, contopt:28395 |
| perpétuo | 2 | True | 1.136 | contopt:28395, contopt:6511 |
| assíduo | 2 | True | 1.0 | contopt:28395, contopt:5675 |
| manente | 2 | True | 0.295 | contopt:10331, contopt:28395 |
| duradouro | 2 | True | 0.316 | contopt:10331, contopt:28395 |
| eterno | 2 | True | 0.429 | contopt:28395, contopt:6511 |
| permanecente | 2 | True | 0.211 | contopt:10331, contopt:28395 |
| inabalável | 2 | True | 1.0 | contopt:10331, contopt:6511 |
| estóico | 2 | True | 0.286 | contopt:10331, contopt:6511 |

### Sinalização (revisão humana — NÃO admitidos)
| Termo | Coocorrência | Peso máx. |
|-------|--------------|-----------|
| monotonia | 4 | 1.25 |
| cotidianidade | 3 | 0.538 |
| quotidianidade | 3 | 0.538 |
| unissonância | 3 | 0.286 |
| igual | 3 | 0.852 |
| conformidade | 3 | 1.0 |
| platitude | 2 | 0.846 |
| moderado | 2 | 0.333 |
| harmónico | 2 | 0.333 |
| harmonioso | 2 | 1.222 |
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
| obstinado | 2 | 1.438 |
| aferrado | 2 | 0.925 |
| resistente | 2 | 0.9 |
| afincado | 2 | 0.787 |
| agarrado | 2 | 0.211 |
| apegado | 2 | 0.111 |
| continuamente | 2 | 1.882 |
| incessantemente | 2 | 1.529 |
| sempre | 2 | 1.529 |
| eternamente | 2 | 1.333 |
| permanentemente | 2 | 0.3 |
| perpetuamente | 2 | 1.556 |
| para sempre | 2 | 1.222 |
| perenemente | 2 | 0.444 |
| imobilidade | 2 | 0.4 |
| fixidez | 2 | 0.4 |
| constância | 2 | 3.0 |
| impassível | 2 | 3.333 |
| imperturbável | 2 | 2.667 |
| indestrutível | 2 | 0.571 |
| insensível | 2 | 0.571 |
| verdadeiro | 2 | 2.125 |
| certo | 2 | 0.485 |
| confiável | 2 | 0.438 |
| leal | 2 | 0.438 |
| efetivo | 2 | 0.242 |

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT
- Termos **admitidos** (decisão humana completa): **188**
- Termos **pendentes** (aguardam decisão humana): **0**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| contínuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| constante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrupto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| sucessivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| permanente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| frequente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| incessante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perpétuo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| continuado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| assíduo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| seguido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perene | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| aturado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| porfioso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| incessável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| ininterrompido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| afio | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| consecutivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| estável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imutável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| imudável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| invariável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| amiudado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| repetido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| manente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| duradouro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| imediato | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| jacente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| conseguinte | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| subsecutivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| persistente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| eterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| miúdo | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| vitalício | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| firme | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| inalterável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| infindável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| regular | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| crebro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| periódico | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| permanecente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| diligente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| fiel | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| sempiterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| jazente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| reiterado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| sem paradas | RT | invariância face a um parâmetro | clip21, contopt | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| aplicado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| habitual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| imóvel | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| ordinário | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| usual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395 | derivado do sentido (PASSO 3) | sense_decision |
| comum | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| consequente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| consistente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| duplicado | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| duradoiro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| mencionado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| perdurável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| perenal | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| pontual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| renovado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| seguinte | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| usado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| contino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| redito | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| definitivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| esforçado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| imanente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| inabalável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| interminável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| irretratável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| iterativo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| monótono | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:25600, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| perseverante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| acontecedeiro | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| consignado | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| inflexivo | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| invariante | RT | invariância face a um parâmetro | clip21, contopt, ontopt06, polaridades | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| jornal | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| por toda vida | RT | invariância face a um parâmetro | clip21 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sequencial | RT | invariância face a um parâmetro | clip21, ontopt06 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| acostumado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| adotado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| atento | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| atilado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| cadimo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| consueto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| consuetudinário | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| correntio | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| costumado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| costumeiro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| costumário | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| durador | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| durável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| escrito | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| escrupuloso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| exato | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| futuro | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| incansável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| irretractável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| irrevogável | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| metódico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| ordenado | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| pertinaz | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| religioso | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| rente | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| resultante | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| rotineiro | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| rítmico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sólito | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| tenaz | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| vulgar | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| acompanhado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| activo | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| adamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| adoptado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| alterno | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| ativo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| coerente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| crónico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| cíclico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| deitado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| durativo | RT | invariância face a um parâmetro | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| efectivo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| escolhido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| estendido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| estereotipado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| eterna | RT | invariância face a um parâmetro | clip21, contopt, ontopt06, polaridades | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| eternas | RT | invariância face a um parâmetro | clip21, contopt, ontopt06, polaridades | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| eternos | RT | invariância face a um parâmetro | clip21, contopt, ontopt06, polaridades | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| fixo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| frequentado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| hereditário | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| homogéneo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:25600, fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| imperecível | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| inamovível | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| inextinguível | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| infinita | RT | invariância face a um parâmetro | clip21, contopt, ontopt06, polaridades | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| infinito | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| intemporal | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| intermitente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| laborioso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| localizado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| matraqueado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| normal | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| novo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| nutrido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| ocasional | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| operoso | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| pegado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| porfiado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| próximo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| recalcado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| revezado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sazonal | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| seguro | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sem idade | RT | invariância face a um parâmetro | clip21, contopt | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sistemático | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| situado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sucedido | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| sínoco | RT | invariância face a um parâmetro | clip21, contopt | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| trabalhador | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| trilhado | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| ulterior | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| unânime | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| vital | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:19004 | derivado do sentido (PASSO 3) | sense_decision |
| diamantino | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| estóico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:23298 | derivado do sentido (PASSO 3) | sense_decision |
| unímodo | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2133 | derivado do sentido (PASSO 3) | sense_decision |
| homótono | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2945, polaridades:4484 | derivado do sentido (PASSO 3) | sense_decision |
| equável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600, ontopt06:2131, polaridades:1656 | derivado do sentido (PASSO 3) | sense_decision |
| recto | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25600 | derivado do sentido (PASSO 3) | sense_decision |
| unívoco | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| similar | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| inequívoco | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| análogo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| idêntico | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26445 | derivado do sentido (PASSO 3) | sense_decision |
| imaterial | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| estereótipo | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27091 | derivado do sentido (PASSO 3) | sense_decision |
| uniformador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |
| uniformizador | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:15521 | derivado do sentido (PASSO 3) | sense_decision |
| inalteravelmente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| uniformemente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| de maneira justa | RT | invariância face a um parâmetro | clip21, contopt | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| imutavelmente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| monotonamente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |
| unanimemente | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:20421 | derivado do sentido (PASSO 3) | sense_decision |

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **uniforme**
- `skos:altLabel` (UF) → equável, homótono, invariável, monótono, uniformador, uniformizador, unímodo
- `:termoRelacionado` (RT) → acompanhado, acontecedeiro, acostumado, activo, adamantino, adoptado, adotado, afio, alterno, amiudado, análogo, aplicado, assíduo, atento, atilado, ativo, aturado, cadimo, coerente, comum, consecutivo, conseguinte, consequente, consignado, consistente, constante, consueto, consuetudinário, contino, continuado, contínuo, correntio, costumado, costumeiro, costumário, crebro, crónico, cíclico, de maneira justa, definitivo, deitado, diamantino, diligente, duplicado, duradoiro, durador, duradouro, durativo, durável, efectivo, escolhido, escrito, escrupuloso, esforçado, estendido, estereotipado, estereótipo, estável, estóico, eterna, eternas, eterno, eternos, exato, fiel, firme, fixo, frequentado, frequente, futuro, habitual, hereditário, homogéneo, idêntico, imanente, imaterial, imediato, imperecível, imudável, imutavelmente, imutável, imóvel, inabalável, inalteravelmente, inalterável, inamovível, incansável, incessante, incessável, inequívoco, inextinguível, infindável, infinita, infinito, inflexivo, ininterrompido, ininterrupto, intemporal, interminável, intermitente, invariante, irretractável, irretratável, irrevogável, iterativo, jacente, jazente, jornal, laborioso, localizado, manente, matraqueado, mencionado, metódico, miúdo, monotonamente, normal, novo, nutrido, ocasional, operoso, ordenado, ordinário, pegado, perdurável, perenal, perene, periódico, permanecente, permanente, perpétuo, perseverante, persistente, pertinaz, pontual, por toda vida, porfiado, porfioso, próximo, recalcado, recto, redito, regular, reiterado, religioso, renovado, rente, repetido, resultante, revezado, rotineiro, rítmico, sazonal, seguido, seguinte, seguro, sem idade, sem paradas, sempiterno, sequencial, similar, sistemático, situado, subsecutivo, sucedido, sucessivo, sínoco, sólito, tenaz, trabalhador, trilhado, ulterior, unanimemente, uniformemente, unânime, unívoco, usado, usual, vital, vitalício, vulgar

_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada como relação SKOS._
