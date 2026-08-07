# LexWarrant — concordância cruzada (**TexturaUniforme**)

- **Política de divergência:** conservative
- **Fontes:** PULO, OWN-PT, WordNet  (colunas: ONTO, PULO, OWN-PT, WordNet)
- **Tabela legada OEWN↔PULO** (`legacy_equivalence`): não carregada (junção runtime usa CILI oficial quando ambas as fontes partilham ``i…``; isto não significa que os identificadores CILI estejam indisponíveis).
- **Junções interfontes por CILI:** 1
- **WordNet/OEWN:** consultada e com resultados na matriz
- **Onto.PT:** discovery-only — queried=True; discovery_evidence=True; concordance_results=false (não admite na matriz LexWarrant)
- **Gerado:** 2026-08-07T14:22:38
- **Descartados (só pendentes):** 2 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 13/13 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | OWN-PT | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|---|
| uniforme | i10771, i6560 | — | UF | atestado | — | ili | convergência (sentido) 〔recursos_derivados:PWN〕 | UF | recursos_derivados: PWN — concordância entre recursos derivados da mesma estrutura conceptual; não constitui atestação independente do português; OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i10771 · oewn-01973553-a |
| constante | i6560 | — | UF | — | — | single | fonte única | UF |  |
| imutável | i10771 | — | UF | — | — | single | fonte única | UF |  |
| invariável | i6560 | — | UF | — | — | single | fonte única | UF |  |
| consistent | i6560 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-01203638-s · ILI i6560 |
| dedifferentiated | i4127 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| differentiated | i4125 | — | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i4126 (oewn-00748118-a) — sem estatuto; adjudicação humana |
| homogeneous | i6559 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i6560 (oewn-01203638-s) — sem estatuto; adjudicação humana |
| homogenous | i6559 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i6560 (oewn-01203638-s) — sem estatuto; adjudicação humana |
| invariável | i10771 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i10771 · oewn-01973553-a |
| multiform | i10773 | — | — | — | sinalização | single | sinalização | — | WordNet: material de contraste (antonym) de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| single | i10772 | — | — | — | sinalização | single | sinalização | — | WordNet: vizinho similar_to de i10771 (oewn-01973553-a) — sem estatuto; adjudicação humana |
| undifferentiated | i4126 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |
| uniform | i4126 | — | — | — | sinalização | single | sinalização | — | WordNet: atestado na WordNet [en_lemma (sem correspondência own-pt)] · oewn-00748118-a · ILI i4126 |

## Resumo por veredicto

- **convergência (sentido):** 1
- **fonte única:** 3
- **sinalização:** 10

## Cobertura da recolha automática de contraste (R6)

_Verificação apenas — a lógica de recolha não é alterada nesta etapa._

- **OWN-PT:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **PULO:** 0 antónimo(s) auto — fonte sem antonímia consultável (esperado)
- **WordNet:** 2 antónimo(s) auto — antonímia consultável (OEWN)
  - termos: differentiated, multiform
- **ILIs ancorados (admitidos) sem material de contraste auto:** i6560
- **Fontes sem antonímia consultável (esperado):** PULO

## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência (sentido) — PULO admitido + OWN-PT atestado (ILI partilhado)
_Sem estatuto simulado no OWN-PT. Pares PULO↔OWN-PT: `recursos_derivados: PWN`._
uniforme

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
_(nenhum)_

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
constante, imutável, invariável

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 0 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; junção OEWN↔PULO só via CILI; pares sem âncora CILI ficam sem junção ILI (não fabricados). | PASS ✅ | bogus→(None, False); unmapped_flag=False |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Nenhum termo admitido pelos motores é descartado da matriz (PULO; OWN-PT/WordNet corroboram; Onto = descoberta) | PASS ✅ | 4 admitidos / 4 em matriz |
| T6 | WordNet/OEWN: source_available / source_queried / source_contributed_results distintos. | PASS ✅ | source_available=true; source_queried=true; source_contributed_results=true |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» / «convergência (sentido)» exigem junção por ILI (nunca só weak(term)). | PASS ✅ | OK |
| T10b | Convergência ILI PULO↔OWN-PT marca sempre recursos_derivados:«PWN». | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 14 conceitos |
| T13 | Nenhuma célula nem proposta_final com valor «contraste» na matriz (migração completa: ver teste unitário de decisions). | PASS ✅ | OK |
| T12 | Nenhum item do bloco de evidência figura no bloco de vocabulário, e vice-versa. | PASS ✅ | blocos A/B disjuntos |
| T15 | Cada item exportado (altLabel/termoRelacionado/matriz/tabela F) rastreia a uma decisão desta classe; cada decisão UF/RT figura em ≥1 artefacto ou é listada como descartada com motivo declarado. | PASS ✅ | OK |
