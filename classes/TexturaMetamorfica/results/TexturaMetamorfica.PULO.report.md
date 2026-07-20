# Fase 0 (PULO / WordNet.PT) — **TexturaMetamórfica** (`TexturaMetamrfica`)

- **Eixo definidor:** muda de forma, relativamente a um ou vários parâmetros
- **Fonte:** PULO / WordNet.PT export (âncora ILI; sem porta estatística)
- **Gerado:** 2026-07-13T17:43:33
- **Estado global:** ✅ TODAS AS ASSERÇÕES PASSARAM

## Quadro de asserções (protocolo)

| Etapa | Asserção | Resultado | Evidência |
|-------|----------|-----------|-----------|
| Etapa 1 | Todo o synset admitido tem ili_offset e glosa mapeada ao eixo. | PASS ✅ | OK |
| Etapa 1 | Nenhum synset off-axis (exclude) figura na lista branca admitida. | PASS ✅ | OK |
| Etapa 1 | A lista branca é persistida por offset ILI e os offsets são únicos. | PASS ✅ | OK |
| ILI | Nenhum id oewn-/por- é usado como chave de junção; a chave é o ILI. | PASS ✅ | OK |
| ILI | Synsets sem ili_offset são sinalizados (não descartados em silêncio). | PASS ✅ | nenhum synset sem ILI no export |
| Etapa 2 | Os sinónimos colhidos provêm exclusivamente de synsets admitidos. | PASS ✅ | OK |
| Etapa 3 | Alvos de relação são tipados pelo mapeamento; «(no lemma)» nunca admitido. | PASS ✅ | OK (471 alvos «(no lemma)» descartados) |
| Etapa 4 | «(no lemma)», colocações e termos só de relação não-nomeada (sem corroboração) são excluídos. | PASS ✅ | OK |
| Etapa 5 | Cada admitido tem estatuto∈{UF,RT,contraste,BT,NT,atributo}, teste decisivo e ≥1 garantia; nomes de qualidade em attribute_bucket. | PASS ✅ | OK |
| Garantia | Termos com garantia «estipulativa» têm definição E relação estrutural. | PASS ✅ | OK |
| Consistência | Nenhum termo é UF de duas classes com owl:disjointWith entre si. | PASS ✅ | OK |
| Consistência | Contrastantes não são serializados como skos:related. | PASS ✅ | OK |
| Serialização | X.skos.ttl analisa com rdflib e tem a contagem de triplos esperada. | PASS ✅ | triplos esperados=4, analisados=4 |

## Etapa 1 — Selecção de acepções (lista branca ILI)
- **UF** `ili-30-07359599-n` — uma mudança qualitativa

- **RT** `ili-30-00126264-v` — causar à mudança; fazer diferente; causar uma transformação

- Excluídos (off-axis): `[]`

## Etapa 2 — Sementes (sinónimos de synsets admitidos)
Total: **21** — alterar, alteração, cambiar, converter, demudar, evolucionar, evoluir, falsificar, metamorfose, metamorfosear, modificar, modificação, mudança, mudar, perturbar, tornar, tranformar, transformar, transformação, transmudação, transmutação

## Etapa 3 — Colheita de relações tipadas
- **Contraste (antonym):** —
- **RT/UF (similar-to):** —
- **BT (hypernym):** alteração, câmbio, modificação, mudança, troca, variação
- **NT (hyponym):** abastardar, abusador, acabar, acalmar, acelerar, acordar, acostumar, acrecentar, acrescentar, acurar, adelgaçar, adornar, adulterar, afazer, afetar, afiar, afinar, agalegar, agravar, ajustar, alargar, alindar, altear, alterar, amadurecer, amargurar, ampliar, animalizar, animar, anular, aperfeiçoar, aperfeiçoar-se, apostemar, aprimorar, apurar, aquecer, arterializar, assanhar, assimilar, aumentar, aviltar, beneficiar, bolear, bonificar, brunir, burilar, capturar, causar, centralizar, civilizar, colocar, comover, comparar, compensar, complicar, concentrar, concluir, confundir, congelar, contaminar, conter, contribuir, convalescer, conversão, converter, corrigir, corroer, corromper, corrompido, corrupto, costumar, cozer, debilitar, debochar, decorar, deformar, degenerar, degradar, depravado, depravar, derrancar, derrubar, desagravar, descarreirar, descer, descongestionar, desencaminhar, desencarreirar, desenvolver, desestabilizar, desmanchar, desmoralizar, desobstruir, desodorizar, despertar, desregrar, destruir, desvirtuar, devassar, devasso, diminuir, dispor, disposto, dissoluto, dissolver, dominar, eclipsar, eivar, elaborar, embelezar, empatar, empestar, encher, encobrir, endurecer, enfeitar, envelhecer, envenenar, equiparar, esclarecer, esconder, escurecer, esmagar, esmerar, esmerar-se, esmerilar, espiritualizar, esquentar, esticar, estilar, estilizar, estragado, estragar, esvaziar, exacerbar, facetar, fazer, fazer dormir, fecundar, fertilizar, formar, gangrenar, gelar, glorificar, habilitar, habituar, humilhar, igualar, incrementar, industrializar, insidiar, instaurar, investir, isolar, levantar, levar, limpar, liquidar, madurar, manchar, marcar, melhorar, melhoria, minar, misturar, moderar, modificar, mudar, naturalizar, neutralizar, nivelar, obscurecer, obter, ocultar, ofuscar, paramentar, passagem, patentear, permitir, perverter, pervertido, piorar, pirólise, polir, preencher, preparar, prevaricar, prevenido, privatizar, produzir, profanar, pronto, provocar, purificar, puxar, pôr, recolher, recomendar, reconstruir, recrescer, recriar, reduzir, refazer, refinar, refrescar, refrigerar, relaxar, requintar, restabelecer, retirar, retocar, revelar, revezar, revolucionar, romper, secar, sensibilizar, simplificar, situar, submeter, substituir, subverter, suscitar, suspender, temperar, terminar, tocar, tornar, transfigurar, transformar, transição, transpor, transportar, transviar, trocar, ulcerar, ungir, unificar, unir, urbanizar, validar, vazar, viciar, voltar
- **Atributo:** —
- **Família derivada:** alteração, câmbio, modificar, modificação, mudança, troca, variação
- Alvos «(no lemma)» descartados: 471

### Sinalização (revisão humana — NÃO admitidos)
- acomodar — relação não-nomeada / #NN (via «relation #61»)
- adaptar — relação não-nomeada / #NN (via «relation #61»)
- agitar — relação não-nomeada / #NN (via «relation #61»)
- ajustar — relação não-nomeada / #NN (via «relation #61»)
- aleijar — relação não-nomeada / #NN (via «relation #61»)
- alteração — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- alterar — relação não-nomeada / #NN (via «relation #61»)
- amputar — relação não-nomeada / #NN (via «relation #61»)
- assassinar — relação não-nomeada / #NN (via «relation #61»)
- ave — relação não-nomeada / #NN (via «relation #61»)
- cambiar — relação não-nomeada / #NN (via «relation #61»)
- câmbio — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- colocar — relação não-nomeada / #NN (via «relation #61»)
- conversão — relação não-nomeada / #NN (via «relation #61»)
- converter — relação não-nomeada / #NN (via «relation #61»)
- corrigir — relação não-nomeada / #NN (via «relation #61»)
- decotar — relação não-nomeada / #NN (via «relation #61»)
- deformar — relação não-nomeada / #NN (via «relation #61»)
- degradação — relação não-nomeada / #NN (via «relation #61»)
- demudar — relação não-nomeada / #NN (via «relation #61»)
- desenvolver — relação não-nomeada / #NN (via «relation #61»)
- deslocar — relação não-nomeada / #NN (via «relation #61»)
- desmembrar — relação não-nomeada / #NN (via «relation #61»)
- elaborar — relação não-nomeada / #NN (via «relation #61»)
- escaravelho — relação não-nomeada / #NN (via «relation #61»)
- estropiar — relação não-nomeada / #NN (via «relation #61»)
- evolucionar — relação não-nomeada / #NN (via «relation #61»)
- evoluir — relação não-nomeada / #NN (via «relation #61»)
- falsificar — relação não-nomeada / #NN (via «relation #61»)
- fanar — relação não-nomeada / #NN (via «relation #61»)
- fixo — relação não-nomeada / #NN (via «relation #61»)
- fusão — relação não-nomeada / #NN (via «relation #61»)
- girar — relação não-nomeada / #NN (via «relation #61»)
- giro — relação não-nomeada / #NN (via «relation #61»)
- inativo — relação não-nomeada / #NN (via «relation #61»)
- máquina — relação não-nomeada / #NN (via «relation #61»)
- metamorfose — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- metamorfosear — relação não-nomeada / #NN (via «relation #61»)
- modificação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- modificar — relação não-nomeada / #NN (via «relation #61»)
- modulação — relação não-nomeada / #NN (via «relation #61»)
- mudança — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- mudar — relação não-nomeada / #NN (via «relation #61»)
- mutação — relação não-nomeada / #NN (via «relation #61»)
- mutilar — relação não-nomeada / #NN (via «relation #61»)
- obter — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- passagem — relação não-nomeada / #NN (via «relation #61»)
- pássaro — relação não-nomeada / #NN (via «relation #61»)
- perturbar — relação não-nomeada / #NN (via «relation #61»)
- pirólise — relação não-nomeada / #NN (via «relation #61»)
- privatização — relação não-nomeada / #NN (via «relation #61»)
- qualitativo — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- recrescer — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- recriar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- remover — relação não-nomeada / #NN (via «relation #61»)
- reorganização — relação não-nomeada / #NN (via «relation #61»)
- secularização — relação não-nomeada / #NN (via «relation #61»)
- sintetizador — relação não-nomeada / #NN (via «relation #61»)
- sorrir — relação não-nomeada / #NN (via «relation #61»)
- subjectivo — relação não-nomeada / #NN (via «relation #61»)
- tornar — relação não-nomeada / #NN (via «relation #61»)
- tranformar — relação não-nomeada / #NN (via «relation #61»)
- transfigurar — relação não-nomeada / #NN (via «relation #61»)
- transformação — relação não-nomeada / #NN (via «relation #61»)
- transformar — relação não-nomeada / #NN (via «relation #61»)
- transição — relação não-nomeada / #NN (via «relation #61»)
- transmudação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- transmutação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- troca — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- troncar — relação não-nomeada / #NN (via «relation #61»)
- tronchar — relação não-nomeada / #NN (via «relation #61»)
- truncar — relação não-nomeada / #NN (via «relation #61»)
- variação — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- voltar — relação não-nomeada / #NN (via «relation #61 (inverse)»)
- voz — relação não-nomeada / #NN (via «relation #61»)

## Etapa 4 — Exclusão automática
| Termo | Motivo |
|-------|--------|
| fazer dormir | colocação multipalavra sem corroboração |

## Etapa 5 — Adjudicação + §7 proveniência
Admitidos: **0**  ·  Pendentes: **254**  ·  Atributos: **0**

| termo | estatuto | via | offset/ILI | teste decisivo | garantia | definição |
|-------|----------|-----|------------|----------------|----------|-----------|

### Pendentes (necessitam de decisão na spec `adjudication`)
abastardar, abusador, acabar, acalmar, acelerar, acordar, acostumar, acrecentar, acrescentar, acurar, adelgaçar, adornar, adulterar, afazer, afetar, afiar, afinar, agalegar, agravar, ajustar, alargar, alindar, altear, alterar, amadurecer, amargurar, ampliar, animalizar, animar, anular, aperfeiçoar, aperfeiçoar-se, apostemar, aprimorar, apurar, aquecer, arterializar, assanhar, assimilar, aumentar, aviltar, beneficiar, bolear, bonificar, brunir, burilar, cambiar, capturar, causar, centralizar, civilizar, colocar, comover, comparar, compensar, complicar, concentrar, concluir, confundir, congelar, contaminar, conter, contribuir, convalescer, conversão, converter, corrigir, corroer, corromper, corrompido, corrupto, costumar, cozer, debilitar, debochar, decorar, deformar, degenerar, degradar, demudar, depravado, depravar, derrancar, derrubar, desagravar, descarreirar, descer, descongestionar, desencaminhar, desencarreirar, desenvolver, desestabilizar, desmanchar, desmoralizar, desobstruir, desodorizar, despertar, desregrar, destruir, desvirtuar, devassar, devasso, diminuir, dispor, disposto, dissoluto, dissolver, dominar, eclipsar, eivar, elaborar, embelezar, empatar, empestar, encher, encobrir, endurecer, enfeitar, envelhecer, envenenar, equiparar, esclarecer, esconder, escurecer, esmagar, esmerar, esmerar-se, esmerilar, espiritualizar, esquentar, esticar, estilar, estilizar, estragado, estragar, esvaziar, evolucionar, evoluir, exacerbar, facetar, falsificar, fazer, fecundar, fertilizar, formar, gangrenar, gelar, glorificar, habilitar, habituar, humilhar, igualar, incrementar, industrializar, insidiar, instaurar, investir, isolar, levantar, levar, limpar, liquidar, madurar, manchar, marcar, melhorar, melhoria, metamorfose, metamorfosear, minar, misturar, moderar, mudar, naturalizar, neutralizar, nivelar, obscurecer, obter, ocultar, ofuscar, paramentar, passagem, patentear, permitir, perturbar, perverter, pervertido, piorar, pirólise, polir, preencher, preparar, prevaricar, prevenido, privatizar, produzir, profanar, pronto, provocar, purificar, puxar, pôr, recolher, recomendar, reconstruir, recrescer, recriar, reduzir, refazer, refinar, refrescar, refrigerar, relaxar, requintar, restabelecer, retirar, retocar, revelar, revezar, revolucionar, romper, secar, sensibilizar, simplificar, situar, submeter, substituir, subverter, suscitar, suspender, temperar, terminar, tocar, tornar, tranformar, transfigurar, transformar, transformação, transição, transmudação, transmutação, transpor, transportar, transviar, trocar, ulcerar, ungir, unificar, unir, urbanizar, validar, vazar, viciar, voltar

## §6 — Mapeamento SKOS-XL / OWL
- `skos:prefLabel` → **TexturaMetamórfica**
- `skosxl:altLabel` (UF) → —
- `skos:related` (RT) → —
- `skos:broader` (BT) → —
- `skos:narrower` (NT) → —
- `:temAtributo` (nomes de qualidade) → —
- `:contrastaCom` + `scopeNote` (contraste) → —

_Nomes de qualidade NÃO são `skosxl:altLabel`; contrastantes NÃO são `skos:related` (o SKOS não modela antonímia)._
