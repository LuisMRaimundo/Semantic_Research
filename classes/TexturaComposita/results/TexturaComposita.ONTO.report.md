# Fase 0 — Relatório de selecção lexical: **textura compósita** (`TexturaComposita`)

- **Eixo definidor:** heterogeneidade / composição de materiais ou partes distintas
- **Base de corroboração:** `C:\Users\lmr20\Desktop\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-07-31T04:21:26
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:1320', 'clip21:17923', 'contopt:16611', 'fuzzythes:25832', 'fuzzythes:26969', 'fuzzythes:27002', 'fuzzythes:27069', 'ontopt06:6214', 'ontopt06:81042', 'thes5rec:19632', 'thes5rec:22375'] |
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
- Synsets admitidos (on-axis): `['clip21:1320', 'clip21:17923', 'contopt:16611', 'fuzzythes:25832', 'fuzzythes:26969', 'fuzzythes:27002', 'fuzzythes:27069', 'ontopt06:3928', 'ontopt06:6214', 'ontopt06:7120', 'ontopt06:81042', 'polaridades:1620', 'thes5rec:19632', 'thes5rec:22375']`
- Synsets excluídos (off-axis): `['clip21:15438', 'contopt:26524', 'clip21:2083', 'contopt:24966', 'fuzzythes:7161', 'ontopt06:23962', 'ontopt06:25561', 'ontopt06:30747', 'ontopt06:49495', 'ontopt06:43961', 'thes5rec:13577', 'top01:2962']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:1320', 'glosa': '', 'decision': 'UF', 'members': ['compósito', 'materiais compostos']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:17923', 'glosa': '', 'decision': 'RT', 'members': ['vário', 'variado', 'variegado', 'mesclado', 'matizado', 'diferente', 'diverso', 'versicolor', 'misturado', 'diversicolor', 'misto', 'desvairado', 'desvariado', 'diversificado', 'sortido', 'copioso', 'pintado', 'confuso', 'desigual', 'promíscuo', 'raiado', 'sorteado', 'colorido', 'cromatizado', 'discordante', 'distinto', 'entremeado', 'inconstante', 'multifário', 'multíplice', 'sarapintado', 'tingido', 'amalgamado', 'nuançado', 'confundido', 'envolto', 'indiscriminado', 'mudado', 'mudável', 'multímodo', 'versátil', 'abigarrado', 'alagartado', 'altamado', 'diversos', 'ecléctico', 'numerosos', 'pecilocromático', 'permixto', 'que oferece várias aspectos', 'variados', 'varioso', 'combinado', 'complexo', 'delirante', 'desirmanado', 'desirmão', 'discrepante', 'divergente', 'entressachado', 'impermanente', 'indistinto', 'instável', 'intermeado', 'mudadiço', 'mutável', 'místico', 'variável', 'voltário', 'voltívolo', 'volátil', 'volúvel', 'vários', 'abastecido', 'alterado', 'alucinado', 'bom', 'buliçoso', 'caprichoso', 'composto', 'compósito', 'contraditório', 'desconforme', 'dessemelhante', 'doido', 'embaralhado', 'esmaltado', 'furta-cor', 'hesitante', 'híbrido', 'incerto', 'indistinguível', 'irregular', 'junto', 'leviano', 'marchetado', 'múltiplo', 'numeroso', 'permisto', 'perplexo', 'pingado', 'precário', 'que oferece vários aspectos', 'recamado', 'salpicado', 'vasto', 'veiro']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:16611', 'glosa': '', 'decision': 'UF', 'members': ['compósito', 'materiais compostos']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25832', 'glosa': '', 'decision': 'RT', 'members': ['amalgamado', 'entressachado', 'diversicolor', 'mesclado', 'versicolor', 'intermeado', 'envolto', 'misto', 'entremeado', 'variegado', 'raiado', 'matizado', 'misturado', 'variado', 'vário', 'intervalado', 'compósito', 'promíscuo', 'intercalado', 'salteado', 'heterogêneo', 'diversificado', 'cromatizado', 'alternado', 'composto', 'indiscriminado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26969', 'glosa': '', 'decision': 'RT', 'members': ['dissimilar', 'heterogéneo', 'dessemelhante', 'absimilhante', 'dissímil', 'díspar', 'dissemelhante', 'diferente', 'compósito']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27002', 'glosa': '', 'decision': 'RT', 'members': ['heterogêneo', 'compósito', 'constituído', 'composto', 'formado', 'elaborado', 'feito', 'heterogéneo', 'aprimorado', 'bem-avindo', 'misto', 'conciliado', 'mesclado', 'concordado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27069', 'glosa': '', 'decision': 'RT', 'members': ['heterogéneo', 'compósito', 'heterogêneo', 'dissimilar', 'composto', 'dessemelhante', 'mesclado', 'constituído']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:6214', 'glosa': '', 'decision': 'UF', 'members': ['compósito', 'entremeado', 'mesclado', 'misto', 'misturado', 'raiado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:81042', 'glosa': '', 'decision': 'UF', 'members': ['compósito']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:19632', 'glosa': '', 'decision': 'UF', 'members': ['composto', 'compósito', 'dessemelhante', 'dissimilar', 'heterogéneo', 'heterogêneo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:22375', 'glosa': '', 'decision': 'UF', 'members': ['composto', 'compósito', 'constituído', 'elaborado', 'feito', 'formado', 'heterogêneo']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **126**

| Termo | Offsets ILI |
|-------|-------------|
| abastecido | clip21:17923 |
| abigarrado | clip21:17923 |
| absimilhante | fuzzythes:26969 |
| alagartado | clip21:17923 |
| altamado | clip21:17923 |
| alterado | clip21:17923 |
| alternado | fuzzythes:25832 |
| alucinado | clip21:17923 |
| amalgamado | clip21:17923, fuzzythes:25832 |
| aprimorado | fuzzythes:27002 |
| bem-avindo | fuzzythes:27002 |
| bom | clip21:17923 |
| buliçoso | clip21:17923 |
| caprichoso | clip21:17923 |
| colorido | clip21:17923 |
| combinado | clip21:17923 |
| complexo | clip21:17923 |
| compósito | clip21:1320, clip21:17923, contopt:16611, fuzzythes:25832, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:6214, ontopt06:7120, ontopt06:81042, polaridades:1620, thes5rec:19632, thes5rec:22375 |
| composto | clip21:17923, fuzzythes:25832, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, thes5rec:19632, thes5rec:22375 |
| conciliado | fuzzythes:27002 |
| concordado | fuzzythes:27002 |
| confundido | clip21:17923 |
| confuso | clip21:17923 |
| constituído | fuzzythes:27002, fuzzythes:27069, thes5rec:22375 |
| contraditório | clip21:17923 |
| copioso | clip21:17923 |
| cromatizado | clip21:17923, fuzzythes:25832 |
| delirante | clip21:17923 |
| desconforme | clip21:17923 |
| desigual | clip21:17923 |
| desirmanado | clip21:17923 |
| desirmão | clip21:17923 |
| dessemelhante | clip21:17923, fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 |
| desvairado | clip21:17923 |
| desvariado | clip21:17923 |
| diferente | clip21:17923, fuzzythes:26969 |
| discordante | clip21:17923 |
| discrepante | clip21:17923 |
| díspar | fuzzythes:26969 |
| dissemelhante | fuzzythes:26969 |
| dissímil | fuzzythes:26969 |
| dissimilar | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 |
| distinto | clip21:17923 |
| divergente | clip21:17923 |
| diversicolor | clip21:17923, fuzzythes:25832 |
| diversificado | clip21:17923, fuzzythes:25832 |
| diverso | clip21:17923 |
| diversos | clip21:17923 |
| doido | clip21:17923 |
| ecléctico | clip21:17923 |
| elaborado | fuzzythes:27002, thes5rec:22375 |
| embaralhado | clip21:17923 |
| entremeado | clip21:17923, fuzzythes:25832, ontopt06:6214 |
| entressachado | clip21:17923, fuzzythes:25832 |
| envolto | clip21:17923, fuzzythes:25832 |
| esmaltado | clip21:17923 |
| feito | fuzzythes:27002, thes5rec:22375 |
| formado | fuzzythes:27002, thes5rec:22375 |
| furta-cor | clip21:17923 |
| hesitante | clip21:17923 |
| heterogêneo | fuzzythes:25832, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, polaridades:1620, thes5rec:19632, thes5rec:22375 |
| híbrido | clip21:17923 |
| impermanente | clip21:17923 |
| incerto | clip21:17923 |
| inconstante | clip21:17923 |
| indiscriminado | clip21:17923, fuzzythes:25832 |
| indistinguível | clip21:17923 |
| indistinto | clip21:17923 |
| instável | clip21:17923 |
| intercalado | fuzzythes:25832 |
| intermeado | clip21:17923, fuzzythes:25832 |
| intervalado | fuzzythes:25832 |
| irregular | clip21:17923 |
| junto | clip21:17923 |
| leviano | clip21:17923 |
| marchetado | clip21:17923 |
| materiais compostos | clip21:1320, contopt:16611 |
| matizado | clip21:17923, fuzzythes:25832 |
| mesclado | clip21:17923, fuzzythes:25832, fuzzythes:27002, fuzzythes:27069, ontopt06:6214 |
| místico | clip21:17923 |
| misto | clip21:17923, fuzzythes:25832, fuzzythes:27002, ontopt06:6214 |
| misturado | clip21:17923, fuzzythes:25832, ontopt06:6214 |
| mudadiço | clip21:17923 |
| mudado | clip21:17923 |
| mudável | clip21:17923 |
| multifário | clip21:17923 |
| multímodo | clip21:17923 |
| multíplice | clip21:17923 |
| múltiplo | clip21:17923 |
| mutável | clip21:17923 |
| nuançado | clip21:17923 |
| numeroso | clip21:17923 |
| numerosos | clip21:17923 |
| pecilocromático | clip21:17923 |
| permisto | clip21:17923 |
| permixto | clip21:17923 |
| perplexo | clip21:17923 |
| pingado | clip21:17923 |
| pintado | clip21:17923 |
| precário | clip21:17923 |
| promíscuo | clip21:17923, fuzzythes:25832 |
| que oferece várias aspectos | clip21:17923 |
| que oferece vários aspectos | clip21:17923 |
| raiado | clip21:17923, fuzzythes:25832, ontopt06:6214 |
| recamado | clip21:17923 |
| salpicado | clip21:17923 |
| salteado | fuzzythes:25832 |
| sarapintado | clip21:17923 |
| sorteado | clip21:17923 |
| sortido | clip21:17923 |
| tingido | clip21:17923 |
| variado | clip21:17923, fuzzythes:25832 |
| variados | clip21:17923 |
| variável | clip21:17923 |
| variegado | clip21:17923, fuzzythes:25832 |
| vário | clip21:17923, fuzzythes:25832 |
| vários | clip21:17923 |
| varioso | clip21:17923 |
| vasto | clip21:17923 |
| veiro | clip21:17923 |
| versátil | clip21:17923 |
| versicolor | clip21:17923, fuzzythes:25832 |
| volátil | clip21:17923 |
| voltário | clip21:17923 |
| voltívolo | clip21:17923 |
| volúvel | clip21:17923 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **16**  ·  nucleares (peso ≥ 0.5): **12**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **0**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **0**

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT
- Termos **admitidos** (decisão humana completa): **126**
- Termos **pendentes** (aguardam decisão humana): **0**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|
| compósito | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:1320, clip21:17923, contopt:16611, fuzzythes:25832, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:6214, ontopt06:7120, ontopt06:81042, polaridades:1620, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| materiais compostos | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt | clip21:1320, contopt:16611 | derivado do sentido (PASSO 3) | sense_decision |
| vário | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| variado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| variegado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| mesclado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832, fuzzythes:27002, fuzzythes:27069, ontopt06:6214 | derivado do sentido (PASSO 3) | sense_decision |
| matizado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| diferente | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| diverso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| versicolor | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| misturado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832, ontopt06:6214 | derivado do sentido (PASSO 3) | sense_decision |
| diversicolor | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| misto | UF | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923, fuzzythes:25832, fuzzythes:27002, ontopt06:6214 | derivado do sentido (PASSO 3) | sense_decision |
| desvairado | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| desvariado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| diversificado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| sortido | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| copioso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| pintado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| confuso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| desigual | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| promíscuo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| raiado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832, ontopt06:6214 | derivado do sentido (PASSO 3) | sense_decision |
| sorteado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| colorido | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| cromatizado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| discordante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| distinto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| entremeado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832, ontopt06:6214 | derivado do sentido (PASSO 3) | sense_decision |
| inconstante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| multifário | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| multíplice | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| sarapintado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| tingido | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| amalgamado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| nuançado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| confundido | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| envolto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| indiscriminado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| mudado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| mudável | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| multímodo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| versátil | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| abigarrado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| alagartado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| altamado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| diversos | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| ecléctico | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| numerosos | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| pecilocromático | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| permixto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, ontopt06 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| que oferece várias aspectos | RT | heterogeneidade / composição de materiais ou partes distintas | clip21 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| variados | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| varioso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| combinado | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| complexo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| delirante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| desirmanado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| desirmão | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| discrepante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| divergente | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| entressachado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| impermanente | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| indistinto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| instável | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| intermeado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923, fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| mudadiço | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| mutável | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| místico | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| variável | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| voltário | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| voltívolo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| volátil | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| volúvel | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| vários | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| abastecido | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| alterado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| alucinado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| bom | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| buliçoso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| caprichoso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| composto | UF | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923, fuzzythes:25832, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| contraditório | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| desconforme | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| dessemelhante | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923, fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 | derivado do sentido (PASSO 3) | sense_decision |
| doido | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| embaralhado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| esmaltado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| furta-cor | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| hesitante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| híbrido | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| incerto | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| indistinguível | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| irregular | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| junto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| leviano | RT | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| marchetado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| múltiplo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| numeroso | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| permisto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| perplexo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| pingado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| precário | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| que oferece vários aspectos | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| recamado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| salpicado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| vasto | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| veiro | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, ontopt06 | clip21:17923 | derivado do sentido (PASSO 3) | sense_decision |
| intervalado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| intercalado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| salteado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| heterogêneo | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:25832, fuzzythes:26969, fuzzythes:27002, fuzzythes:27069, ontopt06:3928, ontopt06:7120, polaridades:1620, thes5rec:19632, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| alternado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, thes5rec | fuzzythes:25832 | derivado do sentido (PASSO 3) | sense_decision |
| dissimilar | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969, fuzzythes:27069, ontopt06:7120, polaridades:1620, thes5rec:19632 | derivado do sentido (PASSO 3) | sense_decision |
| absimilhante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| dissímil | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| díspar | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| dissemelhante | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:26969 | derivado do sentido (PASSO 3) | sense_decision |
| constituído | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, fuzzythes:27069, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| formado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| elaborado | UF | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| feito | UF | heterogeneidade / composição de materiais ou partes distintas | clip01, clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec, top01 | fuzzythes:27002, thes5rec:22375 | derivado do sentido (PASSO 3) | sense_decision |
| aprimorado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| bem-avindo | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| conciliado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |
| concordado | RT | heterogeneidade / composição de materiais ou partes distintas | clip21, contopt, fuzzythes, ontopt06, polaridades, thes5rec | fuzzythes:27002 | derivado do sentido (PASSO 3) | sense_decision |

## §6 — Mapeamento SKOS / OWL (só Bloco A)
- `skos:prefLabel` → **textura compósita**
- `skos:altLabel` (UF) → composto, compósito, constituído, dessemelhante, dissimilar, elaborado, entremeado, feito, formado, heterogêneo, materiais compostos, mesclado, misto, misturado, raiado
- `:termoRelacionado` (RT) → abastecido, abigarrado, absimilhante, alagartado, altamado, alterado, alternado, alucinado, amalgamado, aprimorado, bem-avindo, bom, buliçoso, caprichoso, colorido, combinado, complexo, conciliado, concordado, confundido, confuso, contraditório, copioso, cromatizado, delirante, desconforme, desigual, desirmanado, desirmão, desvairado, desvariado, diferente, discordante, discrepante, dissemelhante, dissímil, distinto, divergente, diversicolor, diversificado, diverso, diversos, doido, díspar, ecléctico, embaralhado, entressachado, envolto, esmaltado, furta-cor, hesitante, híbrido, impermanente, incerto, inconstante, indiscriminado, indistinguível, indistinto, instável, intercalado, intermeado, intervalado, irregular, junto, leviano, marchetado, matizado, mudadiço, mudado, mudável, multifário, multímodo, multíplice, mutável, místico, múltiplo, nuançado, numeroso, numerosos, pecilocromático, permisto, permixto, perplexo, pingado, pintado, precário, promíscuo, que oferece várias aspectos, que oferece vários aspectos, recamado, salpicado, salteado, sarapintado, sorteado, sortido, tingido, variado, variados, variegado, varioso, variável, vasto, veiro, versicolor, versátil, voltário, voltívolo, volátil, volúvel, vário, vários

_Evidência (oposição, atributo, vizinha, sinalização) NÃO é serializada como relação SKOS._
