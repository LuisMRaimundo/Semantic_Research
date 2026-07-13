# Fase 0 — Relatório de selecção lexical: **uniforme** (`TexturaUniforme`)

- **Eixo definidor:** invariância face a um parâmetro
- **Base de corroboração:** `C:\Users\lmr20\Desktop\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-07-13T14:16:59
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:19004', 'contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2945', 'clip01:4659', 'clip01:1043', 'clip21:8149', 'clip21:15521', 'clip21:14562', 'clip21:20073', 'clip21:20421', 'clip21:12874'] |
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
- Synsets admitidos (on-axis): `['clip21:19004', 'contopt:28395', 'fuzzythes:23298', 'fuzzythes:25600', 'fuzzythes:26445', 'fuzzythes:27091', 'ontopt06:2131', 'ontopt06:2133', 'ontopt06:2945', 'polaridades:1656', 'polaridades:4425', 'polaridades:4484', 'polaridades:5938', 'clip01:4659', 'clip01:1043', 'clip21:8149', 'clip21:15521', 'clip21:14562', 'clip21:20073', 'clip21:20421', 'clip21:12874']`
- Synsets excluídos (off-axis): `['clip01:6948', 'clip21:12405', 'clip21:16596', 'clip21:17576', 'clip21:17930', 'clip21:19228', 'clip21:19272', 'clip21:19790', 'contopt:9180', 'contopt:9502', 'contopt:15361', 'contopt:16491', 'fuzzythes:1661', 'fuzzythes:1920', 'fuzzythes:2140', 'fuzzythes:3480', 'fuzzythes:23180', 'fuzzythes:23495', 'fuzzythes:23527', 'fuzzythes:24915', 'fuzzythes:26484', 'fuzzythes:27110', 'ontopt06:787', 'ontopt06:803', 'ontopt06:1186', 'ontopt06:28292', 'polaridades:5083', 'clip01:3425', 'clip21:19074', 'clip21:16541', 'clip21:14314', 'clip21:19940', 'clip21:1403', 'clip21:13406', 'clip21:14088', 'clip21:14525', 'clip21:14687', 'clip21:1731']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:19004', 'glosa': '', 'decision': 'RT', 'members': ['contínuo', 'constante', 'ininterrupto', 'sucessivo', 'permanente', 'frequente', 'incessante', 'perpétuo', 'continuado', 'assíduo', 'seguido', 'perene', 'aturado', 'porfioso', 'incessável', 'ininterrompido', 'afio', 'consecutivo', 'estável', 'imutável', 'imudável', 'invariável', 'amiudado', 'repetido', 'manente', 'duradouro', 'imediato', 'jacente', 'conseguinte', 'subsecutivo', 'persistente', 'eterno', 'miúdo', 'vitalício', 'firme', 'inalterável', 'infindável', 'regular', 'crebro', 'periódico', 'permanecente', 'diligente', 'fiel', 'sempiterno', 'jazente', 'reiterado', 'sem paradas', 'aplicado', 'habitual', 'imóvel', 'ordinário', 'uniforme', 'usual', 'áfio', 'comum', 'consequente', 'consistente', 'duplicado', 'duradoiro', 'mencionado', 'perdurável', 'perenal', 'pontual', 'renovado', 'seguinte', 'usado', 'contino', 'redito', 'definitivo', 'esforçado', 'imanente', 'inabalável', 'interminável', 'irretratável', 'iterativo', 'monótono', 'perseverante', 'acontecedeiro', 'consignado', 'freqüente', 'inflexivo', 'invariante', 'jornal', 'periodico', 'por toda vida', 'sequencial', 'acostumado', 'adotado', 'atento', 'atilado', 'cadimo', 'consueto', 'consuetudinário', 'correntio', 'costumado', 'costumeiro', 'costumário', 'durador', 'durável', 'escrito', 'escrupuloso', 'exato', 'futuro', 'incansável', 'irretractável', 'irrevogável', 'metódico', 'ordenado', 'pertinaz', 'religioso', 'rente', 'resultante', 'rotineiro', 'rítmico', 'sólito', 'tenaz', 'vulgar', 'acompanhado', 'activo', 'adamantino', 'adoptado', 'alterno', 'ativo', 'coerente', 'crónico', 'cíclico', 'deitado', 'durativo', 'efectivo', 'escolhido', 'estendido', 'estereotipado', 'eterna', 'eternas', 'eternos', 'fixo', 'frequentado', 'hereditário', 'homogéneo', 'imperecível', 'inamovível', 'inextinguível', 'infinita', 'infinito', 'intemporal', 'intermitente', 'laborioso', 'localizado', 'matraqueado', 'normal', 'novo', 'nutrido', 'ocasional', 'operoso', 'pegado', 'porfiado', 'próximo', 'recalcado', 'revezado', 'sazonal', 'seguro', 'sem idade', 'sistemático', 'situado', 'sucedido', 'sínoco', 'trabalhador', 'trilhado', 'ulterior', 'unânime', 'vital']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:28395', 'glosa': '', 'decision': 'RT', 'members': ['contínuo', 'constante', 'ininterrupto', 'sucessivo', 'permanente', 'frequente', 'incessante', 'perpétuo', 'continuado', 'assíduo', 'seguido', 'perene', 'aturado', 'porfioso', 'incessável', 'ininterrompido', 'afio', 'consecutivo', 'estável', 'imutável', 'imudável', 'invariável', 'amiudado', 'repetido', 'manente', 'duradouro', 'imediato', 'jacente', 'conseguinte', 'subsecutivo', 'persistente', 'eterno', 'miúdo', 'vitalício', 'firme', 'inalterável', 'infindável', 'regular', 'crebro', 'periódico', 'permanecente', 'diligente', 'fiel', 'sempiterno', 'jazente', 'reiterado', 'sem paradas', 'aplicado', 'habitual', 'imóvel', 'ordinário', 'uniforme', 'usual']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23298', 'glosa': '', 'decision': 'RT', 'members': ['consignado', 'constante', 'imudável', 'imutável', 'invariável', 'manente', 'incessável', 'estável', 'ininterrompido', 'aturado', 'afio', 'incessante', 'perseverante', 'permanente', 'continuado', 'imanente', 'escrito', 'ininterrupto', 'jazente', 'permanecente', 'contínuo', 'diamantino', 'estóico', 'assíduo', 'seguido', 'firme', 'sistemático', 'uniforme', 'jacente', 'sucessivo', 'adamantino', 'persistente', 'porfioso', 'mencionado', 'perene', 'metódico', 'perpétuo', 'ordenado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25600', 'glosa': '', 'decision': 'RT', 'members': ['unímodo', 'uniforme', 'homótono', 'equável', 'homogéneo', 'monótono', 'recto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26445', 'glosa': '', 'decision': 'RT', 'members': ['homogéneo', 'unívoco', 'similar', 'inequívoco', 'uniforme', 'análogo', 'idêntico', 'contínuo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27091', 'glosa': '', 'decision': 'UF', 'members': ['inflexivo', 'invariável', 'intemporal', 'imudável', 'estereotipado', 'imutável', 'constante', 'imaterial', 'irretratável', 'estereótipo', 'imóvel', 'eterno', 'uniforme', 'inalterável', 'estável']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:2945', 'glosa': '', 'decision': 'RT', 'members': ['homótono', 'invariável', 'monótono', 'uniforme']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip01:4659', 'glosa': '', 'decision': 'RT', 'members': ['coerência', 'equabilidade', 'gemeidade', 'homogeneidade', 'igualdade', 'lógica', 'unidade', 'uniformidade']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip01:1043', 'glosa': '', 'decision': 'RT', 'members': ['homogeneização', 'uniformização']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:18187', 'glosa': '', 'decision': 'contraste', 'members': ['desnivelado', 'despadronizado', 'desuniforme', 'escadeado', 'desigual', 'desalinhado', 'inclinado', 'irregular']}, 'why': 'decisão desconhecida'}, {'entry': {'ili_offset': 'clip21:8149', 'glosa': '', 'decision': 'RT', 'members': ['uniform resource locator', 'url']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:15521', 'glosa': '', 'decision': 'UF', 'members': ['uniformador', 'uniformizador']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:14562', 'glosa': '', 'decision': 'RT', 'members': ['uniformizar', 'uniformar', 'homogeneizar', 'padronizar', 'equalizar', 'homogenizar', 'igualar', 'igualizar', 'fardar', 'estandardizar', 'monotonizar', 'normalizar', 'regrar']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:20073', 'glosa': '', 'decision': 'RT', 'members': ['unanimemente', 'indivisamente', 'froixo', 'frouxo', 'de forma unânime', 'unanimimente', 'uniformemente']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:20421', 'glosa': '', 'decision': 'RT', 'members': ['inalteravelmente', 'uniformemente', 'de maneira justa', 'imutavelmente', 'monotonamente', 'unanimemente']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:12874', 'glosa': '', 'decision': 'RT', 'members': ['padronização', 'estandardização', 'homologação', 'uniformização', 'normalização', 'aprovação', 'confirmação', 'homogeneização']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:5719', 'glosa': '', 'decision': 'contraste', 'members': ['desnivelado', 'despadronizado', 'desuniforme', 'escadeado', 'desigual', 'desalinhado', 'inclinado', 'irregular']}, 'why': 'decisão desconhecida'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **263**

| Termo | Offsets ILI |
|-------|-------------|
| acompanhado | clip21:19004 |
| acontecedeiro | clip21:19004 |
| acostumado | clip21:19004 |
| activo | clip21:19004 |
| adamantino | clip21:19004, fuzzythes:23298 |
| adoptado | clip21:19004 |
| adotado | clip21:19004 |
| afim | polaridades:5938 |
| afio | clip21:19004, contopt:28395, fuzzythes:23298 |
| alterno | clip21:19004 |
| amiudado | clip21:19004, contopt:28395 |
| análogo | fuzzythes:26445, polaridades:5938 |
| aparentado | polaridades:5938 |
| aparente | polaridades:5938 |
| aplicado | clip21:19004, contopt:28395 |
| aprovação | clip21:12874 |
| assemelhado | polaridades:5938 |
| assíduo | clip21:19004, contopt:28395, fuzzythes:23298 |
| atento | clip21:19004 |
| atilado | clip21:19004 |
| ativo | clip21:19004 |
| aturado | clip21:19004, contopt:28395, fuzzythes:23298 |
| cadimo | clip21:19004 |
| cíclico | clip21:19004 |
| coerência | clip01:4659 |
| coerente | clip21:19004 |
| cômpar | polaridades:5938 |
| comparado | polaridades:5938 |
| comparável | polaridades:5938 |
| comum | clip21:19004, polaridades:5938 |
| confirmação | clip21:12874 |
| conforme | polaridades:5938 |
| congénere | polaridades:5938 |
| consecutivo | clip21:19004, contopt:28395 |
| conseguinte | clip21:19004, contopt:28395 |
| consequente | clip21:19004 |
| consignado | clip21:19004, fuzzythes:23298 |
| consistente | clip21:19004 |
| constante | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, polaridades:4425 |
| consubstanciado | polaridades:5938 |
| consueto | clip21:19004 |
| consuetudinário | clip21:19004 |
| contino | clip21:19004 |
| continuado | clip21:19004, contopt:28395, fuzzythes:23298 |
| contínuo | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:26445 |
| convizinho | polaridades:5938 |
| correntio | clip21:19004 |
| costumado | clip21:19004 |
| costumário | clip21:19004 |
| costumeiro | clip21:19004 |
| crebro | clip21:19004, contopt:28395 |
| crónico | clip21:19004 |
| de forma unânime | clip21:20073 |
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
| engembrado | polaridades:5938 |
| equabilidade | clip01:4659 |
| equalizar | clip21:14562 |
| equável | fuzzythes:25600, ontopt06:2131, polaridades:1656 |
| equipendente | polaridades:5938 |
| équo | polaridades:5938 |
| escolhido | clip21:19004 |
| escrito | clip21:19004, fuzzythes:23298 |
| escrupuloso | clip21:19004 |
| esforçado | clip21:19004 |
| estandardização | clip21:12874 |
| estandardizar | clip21:14562 |
| estável | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| este | polaridades:5938 |
| estendido | clip21:19004 |
| estereotipado | clip21:19004, fuzzythes:27091 |
| estereótipo | fuzzythes:27091 |
| estóico | fuzzythes:23298 |
| eterna | clip21:19004 |
| eternas | clip21:19004 |
| eterno | clip21:19004, contopt:28395, fuzzythes:27091 |
| eternos | clip21:19004 |
| exato | clip21:19004 |
| fardar | clip21:14562 |
| fiel | clip21:19004, contopt:28395 |
| firme | clip21:19004, contopt:28395, fuzzythes:23298 |
| fixo | clip21:19004 |
| frequentado | clip21:19004 |
| frequente | clip21:19004, contopt:28395 |
| froixo | clip21:20073 |
| frouxo | clip21:20073 |
| futuro | clip21:19004 |
| gemeidade | clip01:4659 |
| gémeo | polaridades:5938 |
| habitual | clip21:19004, contopt:28395 |
| hereditário | clip21:19004 |
| homogeneidade | clip01:4659 |
| homogeneização | clip01:1043, clip21:12874 |
| homogeneizar | clip21:14562 |
| homogéneo | clip21:19004, fuzzythes:25600, fuzzythes:26445, polaridades:5938 |
| homogenizar | clip21:14562 |
| homográfico | polaridades:5938 |
| homologação | clip21:12874 |
| homólogo | polaridades:5938 |
| homótipo | polaridades:5938 |
| homótono | fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| idêntico | fuzzythes:26445, polaridades:5938 |
| igual | polaridades:5938 |
| igualar | clip21:14562 |
| igualdade | clip01:4659 |
| igualizar | clip21:14562 |
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
| indivisamente | clip21:20073 |
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
| lógica | clip01:4659 |
| manente | clip21:19004, contopt:28395, fuzzythes:23298 |
| matraqueado | clip21:19004 |
| mencionado | clip21:19004, fuzzythes:23298 |
| mesmo | polaridades:5938 |
| metódico | clip21:19004, fuzzythes:23298, polaridades:4425 |
| metodizado | polaridades:4425 |
| miúdo | clip21:19004, contopt:28395 |
| monotonamente | clip21:20421 |
| monotonizar | clip21:14562 |
| monótono | clip21:19004, fuzzythes:25600, ontopt06:2945, polaridades:4484 |
| normal | clip21:19004 |
| normalização | clip21:12874 |
| normalizar | clip21:14562 |
| novo | clip21:19004 |
| nutrido | clip21:19004 |
| ocasional | clip21:19004 |
| operoso | clip21:19004 |
| ordenado | clip21:19004, fuzzythes:23298, polaridades:4425 |
| ordinário | clip21:19004, contopt:28395 |
| outro-tanto | polaridades:5938 |
| padronização | clip21:12874 |
| padronizar | clip21:14562 |
| paralelo | polaridades:5938 |
| parecente | polaridades:5938 |
| parecido | polaridades:5938 |
| parente | polaridades:5938 |
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
| pessoa | polaridades:5938 |
| pontual | clip21:19004 |
| por toda vida | clip21:19004 |
| porfiado | clip21:19004 |
| porfioso | clip21:19004, contopt:28395, fuzzythes:23298 |
| próximo | clip21:19004 |
| quejando | polaridades:5938 |
| recalcado | clip21:19004 |
| recto | fuzzythes:25600 |
| redito | clip21:19004 |
| regrar | clip21:14562 |
| regular | clip21:19004, contopt:28395, polaridades:4425 |
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
| semeável | polaridades:5938 |
| semelhante | polaridades:5938 |
| semelhável | polaridades:5938 |
| sempiterno | clip21:19004, contopt:28395 |
| sequencial | clip21:19004 |
| símil | polaridades:5938 |
| similar | fuzzythes:26445 |
| símile | polaridades:5938 |
| sínoco | clip21:19004 |
| sistemático | clip21:19004, fuzzythes:23298, polaridades:4425 |
| sistêmico | polaridades:4425 |
| situado | clip21:19004 |
| sólito | clip21:19004 |
| subsecutivo | clip21:19004, contopt:28395 |
| sucedido | clip21:19004 |
| sucessivo | clip21:19004, contopt:28395, fuzzythes:23298 |
| tal | polaridades:5938 |
| tenaz | clip21:19004 |
| tirante | polaridades:5938 |
| trabalhador | clip21:19004 |
| trilhado | clip21:19004 |
| ulterior | clip21:19004 |
| unânime | clip21:19004 |
| unanimemente | clip21:20073, clip21:20421 |
| unanimimente | clip21:20073 |
| unidade | clip01:4659 |
| uniform resource locator | clip21:8149 |
| uniformador | clip21:15521 |
| uniformar | clip21:14562 |
| uniforme | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:25600, fuzzythes:26445, fuzzythes:27091, ontopt06:2131, ontopt06:2133, ontopt06:2945, polaridades:1656, polaridades:4425, polaridades:4484, polaridades:5938 |
| uniformemente | clip21:20073, clip21:20421 |
| uniformidade | clip01:4659 |
| uniformização | clip01:1043, clip21:12874 |
| uniformizador | clip21:15521 |
| uniformizar | clip21:14562 |
| unímodo | fuzzythes:25600, ontopt06:2133 |
| unívoco | fuzzythes:26445 |
| url | clip21:8149 |
| usado | clip21:19004 |
| usual | clip21:19004, contopt:28395 |
| vital | clip21:19004 |
| vitalício | clip21:19004, contopt:28395 |
| vizinho | polaridades:5938 |
| vulgar | clip21:19004 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **38**  ·  nucleares (peso ≥ 0.5): **17**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **38**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **44**

### Admitidos por corroboração
| Termo | Coocorrência | Nuclear | Peso máx. | Synsets |
|-------|--------------|---------|-----------|---------|
| firme | 5 | True | 3.056 | contopt:10331, contopt:27200, contopt:28395, contopt:5675, contopt:8553 |
| inalterável | 4 | True | 2.333 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| imóvel | 4 | True | 0.286 | contopt:10331, contopt:18050, contopt:28395, contopt:6511 |
| imutável | 3 | True | 0.432 | contopt:10331, contopt:28395, contopt:6511 |
| jacente | 3 | True | 0.25 | contopt:10331, contopt:28395, contopt:6511 |
| estável | 3 | True | 2.167 | contopt:10331, contopt:28395, contopt:6511 |
| igual | 3 | True | 0.852 | contopt:15361, contopt:16491, contopt:6511 |
| fiel | 3 | True | 1.125 | contopt:10331, contopt:28395, contopt:5675 |
| seguro | 3 | True | 2.278 | contopt:10331, contopt:5675, contopt:8553 |
| persistente | 3 | True | 0.963 | contopt:10331, contopt:28395, contopt:8553 |
| regular | 3 | True | 1.727 | contopt:15361, contopt:28395, contopt:9502 |
| monótono | 2 | True | 0.417 | contopt:15361, contopt:30149 |
| coerência | 2 | True | 0.154 | contopt:19305, contopt:20283 |
| monotonamente | 2 | True | 1.0 | contopt:21106, contopt:29177 |
| inabalável | 2 | True | 1.0 | contopt:10331, contopt:6511 |
| eterno | 2 | True | 0.429 | contopt:28395, contopt:6511 |
| estóico | 2 | True | 0.286 | contopt:10331, contopt:6511 |
| perpétuo | 2 | True | 1.136 | contopt:28395, contopt:6511 |
| unanimemente | 2 | True | 1.25 | contopt:21106, contopt:5990 |
| idêntico | 2 | True | 1.082 | contopt:15361, contopt:16491 |
| assíduo | 2 | True | 1.0 | contopt:28395, contopt:5675 |
| pertinaz | 2 | True | 1.325 | contopt:10331, contopt:8553 |
| tenaz | 2 | True | 0.975 | contopt:10331, contopt:8553 |
| porfioso | 2 | True | 0.762 | contopt:28395, contopt:8553 |
| perseverante | 2 | True | 0.211 | contopt:10331, contopt:8553 |
| ordenado | 2 | True | 1.286 | contopt:15361, contopt:9502 |
| metódico | 2 | True | 1.071 | contopt:15361, contopt:9502 |
| contínuo | 2 | True | 1.795 | contopt:27944, contopt:28395 |
| permanente | 2 | True | 1.273 | contopt:10331, contopt:28395 |
| frequente | 2 | True | 1.227 | contopt:15361, contopt:28395 |
| manente | 2 | True | 0.295 | contopt:10331, contopt:28395 |
| duradouro | 2 | True | 0.316 | contopt:10331, contopt:28395 |
| periódico | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| permanecente | 2 | True | 0.211 | contopt:10331, contopt:28395 |
| habitual | 2 | True | 0.167 | contopt:15361, contopt:28395 |
| ordinário | 2 | True | 1.0 | contopt:15361, contopt:28395 |
| fixo | 2 | True | 2.278 | contopt:10331, contopt:18050 |
| igualdade | 2 | True | 1.421 | contopt:13592, contopt:20283 |

### Sinalização (revisão humana — NÃO admitidos)
| Termo | Coocorrência | Peso máx. |
|-------|--------------|-----------|
| monotonia | 4 | 1.25 |
| conformidade | 3 | 1.0 |
| cotidianidade | 3 | 0.538 |
| quotidianidade | 3 | 0.538 |
| unissonância | 3 | 0.286 |
| harmonioso | 2 | 1.222 |
| harmónico | 2 | 0.333 |
| imobilidade | 2 | 0.4 |
| fixidez | 2 | 0.4 |
| platitude | 2 | 0.846 |
| identidade | 2 | 0.842 |
| constância | 2 | 3.0 |
| regularidade | 2 | 1.267 |
| impassível | 2 | 3.333 |
| imperturbável | 2 | 2.667 |
| indestrutível | 2 | 0.571 |
| insensível | 2 | 0.571 |
| moderado | 2 | 0.333 |
| verdadeiro | 2 | 2.125 |
| certo | 2 | 0.485 |
| confiável | 2 | 0.438 |
| leal | 2 | 0.438 |
| efetivo | 2 | 0.242 |
| obstinado | 2 | 1.438 |
| aferrado | 2 | 0.925 |
| resistente | 2 | 0.9 |
| afincado | 2 | 0.787 |
| agarrado | 2 | 0.211 |
| apegado | 2 | 0.111 |
| perpetuamente | 2 | 1.556 |
| eternamente | 2 | 1.333 |
| para sempre | 2 | 1.222 |
| sempre | 2 | 1.529 |
| perenemente | 2 | 0.444 |
| continuamente | 2 | 1.882 |
| permanentemente | 2 | 0.3 |
| incessantemente | 2 | 1.529 |
| semelhança | 2 | 2.412 |
| similitude | 2 | 1.294 |
| paridade | 2 | 0.941 |
| afinidade | 2 | 0.667 |
| relação | 2 | 0.278 |
| paralelismo | 2 | 0.316 |
| correspondência | 2 | 0.842 |

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT / contraste
- Termos **admitidos** (decisão humana completa): **8**
- Termos **pendentes** (aguardam decisão humana): **255**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| constante | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, polaridades:4425 | Teste 1 | lexical |
| imutável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 | Teste 1 | lexical |
| invariável | UF | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484 | Teste 1 | lexical |
| regular | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:19004, contopt:28395, polaridades:4425 | Teste 1 falha | lexical |
| periódico | RT | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, thes5rec, top01 | clip21:19004, contopt:28395 | Teste 3 | lexical |
| igual | RT | invariância face a um parâmetro | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | polaridades:5938 | Teste 1 falha | lexical |
| uniformidade | UF | invariância face a um parâmetro | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip01:4659 | qualidade | lexical |
| politípica | contraste | invariância face a um parâmetro | — | — | Teste 3 | estipulativa |

### Pendentes (necessitam de decisão na spec `adjudication`)
acompanhado, acontecedeiro, acostumado, activo, adamantino, adoptado, adotado, afim, afio, alterno, amiudado, análogo, aparentado, aparente, aplicado, aprovação, assemelhado, assíduo, atento, atilado, ativo, aturado, cadimo, coerente, coerência, comparado, comparável, comum, confirmação, conforme, congénere, consecutivo, conseguinte, consequente, consignado, consistente, consubstanciado, consueto, consuetudinário, contino, continuado, contínuo, convizinho, correntio, costumado, costumeiro, costumário, crebro, crónico, cíclico, cômpar, de forma unânime, de maneira justa, definitivo, deitado, diamantino, diligente, duplicado, duradoiro, durador, duradouro, durativo, durável, efectivo, engembrado, equabilidade, equalizar, equipendente, equável, escolhido, escrito, escrupuloso, esforçado, estandardizar, estandardização, este, estendido, estereotipado, estereótipo, estável, estóico, eterna, eternas, eterno, eternos, exato, fardar, fiel, firme, fixo, frequentado, frequente, froixo, frouxo, futuro, gemeidade, gémeo, habitual, hereditário, homogeneidade, homogeneizar, homogeneização, homogenizar, homográfico, homogéneo, homologação, homólogo, homótipo, homótono, idêntico, igualar, igualdade, igualizar, imanente, imaterial, imediato, imperecível, imudável, imutavelmente, imóvel, inabalável, inalteravelmente, inalterável, inamovível, incansável, incessante, incessável, indivisamente, inequívoco, inextinguível, infindável, infinita, infinito, inflexivo, ininterrompido, ininterrupto, intemporal, interminável, intermitente, invariante, irretractável, irretratável, irrevogável, iterativo, jacente, jazente, jornal, laborioso, localizado, lógica, manente, matraqueado, mencionado, mesmo, metodizado, metódico, miúdo, monotonamente, monotonizar, monótono, normal, normalizar, normalização, novo, nutrido, ocasional, operoso, ordenado, ordinário, outro-tanto, padronizar, padronização, paralelo, parecente, parecido, parente, pegado, perdurável, perenal, perene, permanecente, permanente, perpétuo, perseverante, persistente, pertinaz, pessoa, pontual, por toda vida, porfiado, porfioso, próximo, quejando, recalcado, recto, redito, regrar, reiterado, religioso, renovado, rente, repetido, resultante, revezado, rotineiro, rítmico, sazonal, seguido, seguinte, seguro, sem idade, sem paradas, semelhante, semelhável, semeável, sempiterno, sequencial, similar, sistemático, sistêmico, situado, subsecutivo, sucedido, sucessivo, símil, símile, sínoco, sólito, tal, tenaz, tirante, trabalhador, trilhado, ulterior, unanimemente, unanimimente, unidade, uniform resource locator, uniformador, uniformar, uniformemente, uniformizador, uniformizar, uniformização, unânime, unímodo, unívoco, url, usado, usual, vital, vitalício, vizinho, vulgar, équo

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **uniforme**
- `skosxl:altLabel` (UF) → constante, imutável, invariável, uniformidade
- `skos:related` (RT) → igual, periódico, regular
- `:contrastaCom` + `skos:scopeNote` (contraste) → politípica

_Contrastantes NÃO são serializados como `skos:related` (o SKOS não modela antonímia)._
