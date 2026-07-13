# LexWarrant — concordância cruzada (**TexturaUniforme**)

- **Política de divergência:** conservative
- **Fontes:** PULO, ONTO, WordNet  (colunas: ONTO, PULO, WordNet)
- **Tabela de equivalência ILI:** C:\Users\lmr20\Desktop\Semantic_Research\classes\TexturaUniforme\out\ili_equivalence.json  (3 mapeados, 5 revisão, 3 sem correspondência)
- **Gerado:** 2026-07-13T14:16:59
- **Descartados (só pendentes):** 9 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 11/11 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|
| igual | ili-30-00909545-a | RT | atributo | — | weak(term) | convergência (termo) | RT | junção por termo — as fontes não partilham um ILI comum (fiabilidade menor); projecção p/ comparação: PULO: atributo→RT/UF; proposta «RT» com dupla natureza: PULO via «atributo» (destino :temAtributo preservado); namespace não-mapeada (não-juntável): polaridades:5938 |
| politípica | — | contraste | contraste | — | weak(term) | convergência (termo) | contraste | junção fraca por termo (sem ILI) — fiabilidade menor |
| regular | ili-30-00909545-a | RT | atributo | — | weak(term) | convergência (termo) | RT | junção por termo — as fontes não partilham um ILI comum (fiabilidade menor); projecção p/ comparação: PULO: atributo→RT/UF; proposta «RT» com dupla natureza: PULO via «atributo» (destino :temAtributo preservado); namespace não-mapeada (não-juntável): clip21:19004, contopt:28395, polaridades:4425 |
| constante | — | UF | — | — | single | fonte única | UF | namespace não-mapeada (não-juntável): clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, polaridades:4425 |
| desigual | — | — | contraste | — | single | fonte única | contraste |  |
| igualdade | — | — | atributo | — | single | fonte única | atributo | projecção p/ comparação: PULO: atributo→RT/UF |
| imutável | — | UF | — | — | single | fonte única | UF | namespace não-mapeada (não-juntável): clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091 |
| invariável | oewn-ili:i10771 | UF | — | sinalização | weak(term) | fonte única | UF | junção por termo — as fontes não partilham um ILI comum (fiabilidade menor); sinalizado por WordNet enquanto admitido por ONTO; namespace não-mapeada (não-juntável): clip21:19004, contopt:28395, fuzzythes:23298, fuzzythes:27091, ontopt06:2945, polaridades:4484; WordNet: atestado na WordNet [pt_lemma (ILI)] · oewn-01973553-a · ILI i10771 |
| irregular | — | — | contraste | — | single | fonte única | contraste |  |
| periódico | — | RT | — | — | single | fonte única | RT | namespace não-mapeada (não-juntável): clip21:19004, contopt:28395 |
| uniformidade | — | UF | — | — | single | fonte única | UF | namespace não-mapeada (não-juntável): clip01:4659 |
| dedifferentiated | oewn-ili:i4127 | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| differentiated | oewn-ili:i4125 | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| multiform | oewn-ili:i10773 | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| single | oewn-ili:i10772 | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| undifferentiated | oewn-ili:i4126 | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |
| uniform | oewn-ili:i4126 | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |
| uniforme | oewn-ili:i10771 | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [pt_lemma (ILI)] · oewn-01973553-a · ILI i10771 |

## Resumo por veredicto

- **convergência (termo):** 3
- **fonte única:** 8
- **sinalização:** 7

## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
igual, politípica, regular

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
constante, desigual, igualdade, imutável, invariável, irregular, periódico, uniformidade

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 4 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; mapeamento só pela tabela declarada; pares não-mapeados são flagueados. | PASS ✅ | bogus→(None, False); unmapped_flag=True |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Termo de fonte única aparece como «fonte única» e nenhum termo admitido é descartado. | PASS ✅ | OK |
| T6 | Fonte WordNet ausente ⇒ coluna toda «—». | PASS ✅ | WordNet presente — N/A |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» exige junção por ILI (o conjunto mais defensável nunca assenta só em weak(term)). | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 18 conceitos |
