# LexWarrant — concordância cruzada (**TexturaComposita**)

- **Política de divergência:** conservative
- **Fontes:** PULO, OWN-PT, WordNet  (colunas: ONTO, PULO, OWN-PT, WordNet)
- **Tabela legada OEWN↔PULO** (`legacy_equivalence`): não carregada (junção runtime usa CILI oficial quando ambas as fontes partilham ``i…``; isto não significa que os identificadores CILI estejam indisponíveis).
- **Junções interfontes:** nenhuma — 10 item(ns) da matriz provenientes exclusivamente de PULO + OWN-PT (identificadores CILI normalizados na coluna ILI não implicam junção OEWN↔PULO).
- **WordNet/OEWN:** disponível/consultada, sem formas portuguesas admitidas na matriz (`source_contributed_results=false`)
- **Onto.PT:** discovery-only — queried=True; discovery_evidence=True; concordance_results=false (não admite na matriz LexWarrant)
- **Gerado:** 2026-08-17T06:35:17
- **Descartados (só pendentes):** 29 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 13/13 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | OWN-PT | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|---|
| composição | i52229, i59707, i62908, i63671 | — | RT | — | — | single | fonte única | RT |  |
| constituição | i62908 | — | RT | — | — | single | fonte única | RT |  |
| construção | i59707 | — | RT | — | — | single | fonte única | RT |  |
| contextura | i59707 | — | RT | — | — | single | fonte única | RT |  |
| edifício | i59707 | — | RT | — | — | single | fonte única | RT |  |
| estrutura | i59707 | — | RT | — | — | single | fonte única | RT |  |
| Composição | i67721 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i67721 · oewn-05878802-n |
| composto | i67721 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i67721 · oewn-05878802-n |
| composto químico | i114921 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i114921 · oewn-14842408-n; excluded_cili:i114921 |
| substância química | i114921 | — | — | atestado | — | single | sinalização | — | OWN-PT: atestado OWN-PT [own-pt:1.0.0] via ILI i114921 · oewn-14842408-n; excluded_cili:i114921 |

## Resumo por veredicto

- **fonte única:** 6
- **sinalização:** 4

## Cobertura da recolha automática de contraste (R6)

_Verificação apenas — a lógica de recolha não é alterada nesta etapa._

- **OWN-PT:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **PULO:** 0 antónimo(s) auto — fonte sem antonímia consultável (esperado)
- **WordNet:** 0 antónimo(s) auto — antonímia consultável (OEWN)
- **ILIs ancorados (admitidos) sem material de contraste auto:** i52229, i59707, i62908, i63671
- **Fontes sem antonímia consultável (esperado):** PULO

## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência (sentido) — PULO admitido + OWN-PT atestado (ILI partilhado)
_Sem estatuto simulado no OWN-PT. Pares PULO↔OWN-PT: `recursos_derivados: PWN`._
_(nenhum)_

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
_(nenhum)_

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
composição, constituição, construção, contextura, edifício, estrutura

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 0 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; junção OEWN↔PULO só via CILI; pares sem âncora CILI ficam sem junção ILI (não fabricados). | PASS ✅ | bogus→(None, False); unmapped_flag=False |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Nenhum termo admitido pelos motores é descartado da matriz (PULO; OWN-PT/WordNet corroboram; Onto = descoberta) | PASS ✅ | 6 admitidos / 6 em matriz |
| T6 | WordNet/OEWN: source_available / source_queried / source_contributed_results distintos. | PASS ✅ | source_available=true; source_queried=true; source_contributed_results=false (sem formas PT admitidas na matriz) |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» / «convergência (sentido)» exigem junção por ILI (nunca só weak(term)). | PASS ✅ | OK |
| T10b | Convergência ILI PULO↔OWN-PT marca sempre recursos_derivados:«PWN». | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 10 conceitos |
| T13 | Nenhuma célula nem proposta_final com valor «contraste» na matriz (migração completa: ver teste unitário de decisions). | PASS ✅ | OK |
| T12 | Nenhum item do bloco de evidência figura no bloco de vocabulário, e vice-versa. | PASS ✅ | blocos A/B disjuntos |
| T15 | Cada item exportado (altLabel/termoRelacionado/matriz/tabela F) rastreia a uma decisão desta classe; cada decisão UF/RT figura em ≥1 artefacto ou é listada como descartada com motivo declarado. | PASS ✅ | OK |

# Relatório residual — `TexturaComposita`

Taxonomia de reconciliação (b1/b2/c1/c2/estipulações) **removida** (Corte 2).

## Acepções adjudicadas sem correspondência em motor

- `UF` · papel:papel35:SINONIMIA:SINONIMO_ADJ_DE:composito · compósito, heterogéneo, mesclado

## Descartado (Onto.PT discovery-only)

Acepções Onto.PT adjudicadas UF/RT — por desenho nunca entram na matriz LexWarrant (Corte 3). Listadas aqui para rastreabilidade.

- `UF` · onto:clip21:1320 · compósito, materiais compostos
- `UF` · onto:contopt:16611 · compósito, materiais compostos
- `RT` · onto:fuzzythes:26969 · dissimilar, heterogéneo, dessemelhante, absimilhante, dissímil, díspar, dissemelhante, diferente, compósito
- `RT` · onto:fuzzythes:27002 · heterogêneo, compósito, constituído, composto, formado, elaborado, feito, heterogéneo, aprimorado, bem-avindo, misto, conciliado, mesclado, concordado
- `UF` · onto:fuzzythes:27069 · heterogéneo, compósito, heterogêneo, dissimilar, composto, dessemelhante, mesclado, constituído
- `UF` · onto:ontopt06:3928 · composto, compósito, heterogêneo
- `UF` · onto:ontopt06:7120 · compósito, dessemelhante, dissimilar, heterogéneo
- `UF` · onto:ontopt06:81042 · compósito
- `RT` · onto:polaridades:1620 · compósito, dessemelhante, dissimilar, heterogéneo
- `UF` · onto:thes5rec:19632 · composto, compósito, dessemelhante, dissimilar, heterogéneo, heterogêneo
- `UF` · onto:thes5rec:22375 · composto, compósito, constituído, elaborado, feito, formado, heterogêneo
