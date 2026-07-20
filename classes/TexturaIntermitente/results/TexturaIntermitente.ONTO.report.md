# Fase 0 — Relatório de selecção lexical: **TexturaIntermitente** (`TexturaIntermitente`)

- **Eixo definidor:** que ocorre espaçadamente, a intervalos, regulares ou irregulares
- **Base de corroboração:** `C:\Users\lmr20\Desktop\Semantic_Research\engines\ONTO\ontopt.sqlite`  ·  recursos difusos: contopt
- **Porta (Etapa 3):** peso ≥ 0.5, coocorrência ≥ 2
- **Gerado:** 2026-07-13T18:00:17
- **Estado global:** ❌ EXISTEM ASSERÇÕES FALHADAS

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido possui ili_offset e glosa mapeada ao eixo. | FAIL ❌ | synsets sem ili/glosa: ['clip21:17265', 'clip21:19737', 'contopt:5236', 'contopt:33686', 'fuzzythes:23329', 'fuzzythes:23659', 'fuzzythes:23873', 'fuzzythes:24056', 'fuzzythes:25214', 'fuzzythes:26922', 'fuzzythes:26927', 'fuzzythes:26998', 'fuzzythes:27907', 'ontopt06:1386', 'ontopt06:4134', 'ontopt06:54924', 'thes5rec:18150', 'thes5rec:21772', 'thes5rec:23361', 'thes5rec:23954'] |
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
- Synsets admitidos (on-axis): `['clip21:17265', 'clip21:19737', 'contopt:5236', 'contopt:33686', 'fuzzythes:23329', 'fuzzythes:23659', 'fuzzythes:23873', 'fuzzythes:24056', 'fuzzythes:25214', 'fuzzythes:26922', 'fuzzythes:26927', 'fuzzythes:26998', 'fuzzythes:27907', 'ontopt06:1386', 'ontopt06:3833', 'ontopt06:4134', 'ontopt06:4160', 'ontopt06:54924', 'polaridades:13335', 'thes5rec:18150', 'thes5rec:21772', 'thes5rec:23361', 'thes5rec:23954']`
- Synsets excluídos (off-axis): `['clip21:19004', 'fuzzythes:25210', 'fuzzythes:10163', 'thes5rec:8218']`
- ⚠ Entradas inválidas: [{'entry': {'ili_offset': 'clip21:17265', 'glosa': '', 'decision': 'UF', 'members': ['alternado', 'entremeado', 'salteado', 'revezado', 'alterno', 'intermeado', 'intervalado', 'alternativo', 'intercalado', 'intermitente', 'mesclado', 'alternante', 'interposto', 'raiado', 'entressachado', 'espaçado', 'alternativa', 'interpolado', 'assaltado', 'alternador', 'intercalar', 'recíproco', 'surpreendido', 'acessional', 'embolismal', 'intexto', 'parentético', 'repetir', 'intercadente', 'mútuo', 'sobressalteado', 'adicional', 'atacado', 'descontínuo', 'entrelaçado', 'interjacente', 'listrado', 'misturado', 'periódico', 'repetido', 'sobressaltado', 'sucessivo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'clip21:19737', 'glosa': '', 'decision': 'RT', 'members': ['interrompido', 'descontínuo', 'suspenso', 'descontinuado', 'incontínuo', 'intercadente', 'interrupto', 'intercepto', 'interceptado', 'sustado', 'cortado', 'impedido', 'interruto', 'atalhado', 'bloqueado', 'inaccessível', 'inacessível', 'intermitente', 'irregular', 'obstruído', 'alternado', 'arretado', 'detido', 'empatado', 'interciso', 'paralisado', 'quebrado', 'quebrantado', 'solto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:5236', 'glosa': '', 'decision': 'UF', 'members': ['alternado', 'entremeado', 'salteado', 'revezado', 'alterno', 'intermeado', 'intervalado', 'alternativo', 'intercalado', 'intermitente', 'mesclado', 'alternante', 'interposto', 'raiado', 'entressachado', 'espaçado', 'alternativa', 'interpolado', 'assaltado', 'alternador', 'intercalar', 'recíproco', 'surpreendido']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'contopt:33686', 'glosa': '', 'decision': 'UF', 'members': ['interrompido', 'descontínuo', 'suspenso', 'descontinuado', 'incontínuo', 'intercadente', 'interrupto', 'intercepto', 'interceptado', 'sustado', 'cortado', 'impedido', 'interruto', 'atalhado', 'bloqueado', 'inaccessível', 'inacessível', 'intermitente', 'irregular', 'obstruído']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23329', 'glosa': '', 'decision': 'UF', 'members': ['incontínuo', 'descontinuado', 'descontínuo', 'intercadente', 'interrupto', 'interrompido', 'intermitente', 'sustado', 'alternado', 'revezado', 'irregular', 'suspenso', 'salteado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23659', 'glosa': '', 'decision': 'RT', 'members': ['alterno', 'revezado', 'alternado', 'alternativo', 'intermitente', 'salteado', 'intervalado', 'entremeado', 'recíproco', 'intermeado', 'mútuo', 'intercadente', 'descontínuo', 'espaçado', 'entressachado', 'assaltado', 'intercalado', 'sobressalteado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:23873', 'glosa': '', 'decision': 'RT', 'members': ['interpolado', 'intervalado', 'entremeado', 'salteado', 'intermeado', 'alternado', 'intercalado', 'espaçado', 'entressachado', 'alterno', 'revezado', 'espacioso', 'pausado', 'mesclado', 'intermitente', 'prorrogado', 'alternativo', 'distanciado', 'interposto', 'adiado', 'espaçoso', 'espacejado', 'arrastado', 'raiado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:24056', 'glosa': '', 'decision': 'RT', 'members': ['entremeado', 'intermeado', 'entressachado', 'intervalado', 'intercalado', 'alternado', 'salteado', 'interjacente', 'espaçado', 'mesclado', 'interposto', 'raiado', 'revezado', 'interpolado', 'alterno', 'intermitente', 'intermédio', 'misto', 'alternativo', 'assaltado', 'rajado', 'sobressalteado', 'misturado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:25214', 'glosa': '', 'decision': 'RT', 'members': ['interjacente', 'interposto', 'intermeado', 'entressachado', 'entremeado', 'intercalado', 'intervalado', 'intermédio', 'mesclado', 'salteado', 'raiado', 'alternado', 'intermediário', 'espaçado', 'interpolado', 'revezado', 'alterno', 'intermitente', 'intercalar', 'alternativo', 'assaltado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26922', 'glosa': '', 'decision': 'RT', 'members': ['interpolado', 'salteado', 'intervalado', 'intercalado', 'intermitente', 'assaltado', 'alternado', 'revezado', 'alterno', 'entremeado', 'intermeado', 'acometido', 'agredido', 'atacado', 'alternativo', 'sobressalteado', 'entressachado', 'espaçado', 'espaventado', 'intercadente', 'trépido', 'estremecido', 'mesclado', 'descontínuo']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26927', 'glosa': '', 'decision': 'RT', 'members': ['recíproco', 'alternativo', 'mútuo', 'alterno', 'revezado', 'alternado', 'intermitente', 'salteado', 'intervalado', 'respectivo', 'entremeado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:26998', 'glosa': '', 'decision': 'RT', 'members': ['sustado', 'interrupto', 'intercadente', 'suspenso', 'interrompido', 'descontinuado', 'descontínuo', 'incontínuo', 'impedido', 'intermitente']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'fuzzythes:27907', 'glosa': '', 'decision': 'RT', 'members': ['acessional', 'intermitente', 'adicional', 'revezado', 'alternado', 'salteado', 'alterno', 'intercadente', 'descontínuo', 'alternativo', 'incontínuo', 'descontinuado', 'intervalado', 'entremeado', 'interrupto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:1386', 'glosa': '', 'decision': 'RT', 'members': ['alternado', 'alternativo', 'alterno', 'intercadente', 'intermitente', 'repetir', 'revezado', 'salteado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:4134', 'glosa': '', 'decision': 'UF', 'members': ['descontinuado', 'descontínuo', 'incontínuo', 'intercadente', 'interciso', 'intermitente', 'interrompido', 'interrupto']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'ontopt06:54924', 'glosa': '', 'decision': 'UF', 'members': ['intermitente']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:18150', 'glosa': '', 'decision': 'RT', 'members': ['alternado', 'alterno', 'assaltado', 'entremeado', 'intercalado', 'intermitente', 'interpolado', 'intervalado', 'revezado', 'salteado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:21772', 'glosa': '', 'decision': 'RT', 'members': ['atalhado', 'descontinuado', 'descontínuo', 'incontínuo', 'intercadente', 'interceptado', 'intercepto', 'interciso', 'intermitente', 'interrompido', 'interrupto', 'interruto', 'suspenso', 'sustado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:23361', 'glosa': '', 'decision': 'RT', 'members': ['acessional', 'adicional', 'alternado', 'intermitente', 'revezado', 'salteado']}, 'why': 'sem ili_offset ou glosa'}, {'entry': {'ili_offset': 'thes5rec:23954', 'glosa': '', 'decision': 'RT', 'members': ['alternado', 'alternativo', 'alterno', 'entremeado', 'intermeado', 'intermitente', 'intervalado', 'mútuo', 'recíproco', 'revezado', 'salteado']}, 'why': 'sem ili_offset ou glosa'}]

## Etapa 2 — Núcleo de candidatos (membros dos synsets admitidos)
Total de sementes: **85**

| Termo | Offsets ILI |
|-------|-------------|
| acessional | clip21:17265, fuzzythes:27907, ontopt06:3833, thes5rec:23361 |
| acometido | fuzzythes:26922 |
| adiado | fuzzythes:23873 |
| adicional | clip21:17265, fuzzythes:27907, thes5rec:23361 |
| agredido | fuzzythes:26922 |
| alternado | clip21:17265, clip21:19737, contopt:5236, fuzzythes:23329, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:1386, ontopt06:4160, thes5rec:18150, thes5rec:23361, thes5rec:23954 |
| alternador | clip21:17265, contopt:5236 |
| alternante | clip21:17265, contopt:5236 |
| alternativa | clip21:17265, contopt:5236 |
| alternativo | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:1386, thes5rec:23954 |
| alterno | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:1386, thes5rec:18150, thes5rec:23954 |
| arrastado | fuzzythes:23873 |
| arretado | clip21:19737 |
| assaltado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, thes5rec:18150 |
| atacado | clip21:17265, fuzzythes:26922 |
| atalhado | clip21:19737, contopt:33686, thes5rec:21772 |
| bloqueado | clip21:19737, contopt:33686 |
| cortado | clip21:19737, contopt:33686 |
| descontinuado | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, fuzzythes:27907, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| descontínuo | clip21:17265, clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:23659, fuzzythes:26922, fuzzythes:26998, fuzzythes:27907, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| detido | clip21:19737 |
| distanciado | fuzzythes:23873 |
| embolismal | clip21:17265 |
| empatado | clip21:19737 |
| entrelaçado | clip21:17265 |
| entremeado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:4160, thes5rec:18150, thes5rec:23954 |
| entressachado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922 |
| espaçado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922 |
| espacejado | fuzzythes:23873 |
| espacioso | fuzzythes:23873 |
| espaçoso | fuzzythes:23873 |
| espaventado | fuzzythes:26922 |
| estremecido | fuzzythes:26922 |
| impedido | clip21:19737, contopt:33686, fuzzythes:26998 |
| inaccessível | clip21:19737, contopt:33686 |
| inacessível | clip21:19737, contopt:33686 |
| incontínuo | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, fuzzythes:27907, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| intercadente | clip21:17265, clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:23659, fuzzythes:26922, fuzzythes:26998, fuzzythes:27907, ontopt06:1386, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| intercalado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, thes5rec:18150 |
| intercalar | clip21:17265, contopt:5236, fuzzythes:25214 |
| interceptado | clip21:19737, contopt:33686, thes5rec:21772 |
| intercepto | clip21:19737, contopt:33686, thes5rec:21772 |
| interciso | clip21:19737, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| interjacente | clip21:17265, fuzzythes:24056, fuzzythes:25214 |
| intermeado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, ontopt06:4160, thes5rec:23954 |
| intermediário | fuzzythes:25214 |
| intermédio | fuzzythes:24056, fuzzythes:25214 |
| intermitente | clip21:17265, clip21:19737, contopt:33686, contopt:5236, fuzzythes:23329, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:26998, fuzzythes:27907, ontopt06:1386, ontopt06:3833, ontopt06:4134, ontopt06:4160, ontopt06:54924, polaridades:13335, thes5rec:18150, thes5rec:21772, thes5rec:23361, thes5rec:23954 |
| interpolado | clip21:17265, contopt:5236, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, ontopt06:4160, thes5rec:18150 |
| interposto | clip21:17265, contopt:5236, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214 |
| interrompido | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| interrupto | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, fuzzythes:27907, ontopt06:4134, polaridades:13335, thes5rec:21772 |
| interruto | clip21:19737, contopt:33686, thes5rec:21772 |
| intervalado | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:4160, thes5rec:18150, thes5rec:23954 |
| intexto | clip21:17265, ontopt06:4160 |
| irregular | clip21:19737, contopt:33686, fuzzythes:23329 |
| listrado | clip21:17265 |
| mesclado | clip21:17265, contopt:5236, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922 |
| misto | fuzzythes:24056 |
| misturado | clip21:17265, fuzzythes:24056 |
| mútuo | clip21:17265, fuzzythes:23659, fuzzythes:26927, thes5rec:23954 |
| obstruído | clip21:19737, contopt:33686 |
| paralisado | clip21:19737 |
| parentético | clip21:17265 |
| pausado | fuzzythes:23873 |
| periódico | clip21:17265, ontopt06:3833 |
| prorrogado | fuzzythes:23873 |
| quebrado | clip21:19737 |
| quebrantado | clip21:19737 |
| raiado | clip21:17265, contopt:5236, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214 |
| rajado | fuzzythes:24056 |
| recíproco | clip21:17265, contopt:5236, fuzzythes:23659, fuzzythes:26927, thes5rec:23954 |
| repetido | clip21:17265 |
| repetir | clip21:17265, ontopt06:1386 |
| respectivo | fuzzythes:26927 |
| revezado | clip21:17265, contopt:5236, fuzzythes:23329, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:1386, thes5rec:18150, thes5rec:23361, thes5rec:23954 |
| salteado | clip21:17265, contopt:5236, fuzzythes:23329, fuzzythes:23659, fuzzythes:23873, fuzzythes:24056, fuzzythes:25214, fuzzythes:26922, fuzzythes:26927, fuzzythes:27907, ontopt06:1386, ontopt06:4160, thes5rec:18150, thes5rec:23361, thes5rec:23954 |
| sobressaltado | clip21:17265 |
| sobressalteado | clip21:17265, fuzzythes:23659, fuzzythes:24056, fuzzythes:26922 |
| solto | clip21:19737 |
| sucessivo | clip21:17265 |
| surpreendido | clip21:17265, contopt:5236 |
| suspenso | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, thes5rec:21772 |
| sustado | clip21:19737, contopt:33686, fuzzythes:23329, fuzzythes:26998, thes5rec:21772 |
| trépido | fuzzythes:26922 |

## Etapa 3 — Corroboração via CONTO.PT (gated)
- Synsets com membro-foco: **0**  ·  nucleares (peso ≥ 0.5): **0**
- Candidatos difusos **admitidos** (cumprem as 3 condições): **0**
- Candidatos em **sinalização** (cumprem 1–2, falham corroboração): **0**

## Etapa 4 — Exclusão automática (assinaturas de ruído)
Nenhum candidato descartado por assinatura de ruído.

## Etapa 5 — Adjudicação UF / RT / contraste
- Termos **admitidos** (decisão humana completa): **0**
- Termos **pendentes** (aguardam decisão humana): **85**

### §7 — Registo de proveniência (termos admitidos)
| termo | estatuto | eixo | recursos de atestação | offset/ILI | teste decisivo | garantia |
|-------|----------|------|-----------------------|------------|----------------|----------|

### Pendentes (necessitam de decisão na spec `adjudication`)
acessional, acometido, adiado, adicional, agredido, alternado, alternador, alternante, alternativa, alternativo, alterno, arrastado, arretado, assaltado, atacado, atalhado, bloqueado, cortado, descontinuado, descontínuo, detido, distanciado, embolismal, empatado, entrelaçado, entremeado, entressachado, espacejado, espacioso, espaventado, espaçado, espaçoso, estremecido, impedido, inaccessível, inacessível, incontínuo, intercadente, intercalado, intercalar, interceptado, intercepto, interciso, interjacente, intermeado, intermediário, intermitente, intermédio, interpolado, interposto, interrompido, interrupto, interruto, intervalado, intexto, irregular, listrado, mesclado, misto, misturado, mútuo, obstruído, paralisado, parentético, pausado, periódico, prorrogado, quebrado, quebrantado, raiado, rajado, recíproco, repetido, repetir, respectivo, revezado, salteado, sobressaltado, sobressalteado, solto, sucessivo, surpreendido, suspenso, sustado, trépido

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **TexturaIntermitente**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `:contrastaCom` + `skos:scopeNote` (contraste) → —

_Contrastantes NÃO são serializados como `skos:related` (o SKOS não modela antonímia)._
