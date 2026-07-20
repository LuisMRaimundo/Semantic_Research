# LexWarrant — concordância cruzada (**TexturaMetamrfica**)

- **Política de divergência:** conservative
- **Fontes:** PULO, ONTO  (colunas: ONTO, PULO, WordNet)
- **Tabela de equivalência ILI:** ⚠ NÃO CARREGADA (0 pares de alta confiança) — junções por ILI OEWN↔PULO indisponíveis; só por termo.
- **Gerado:** 2026-07-18T15:27:24
- **Descartados (só pendentes):** 254 (termos ainda por adjudicar; contados, não listados)
- **Asserções:** 11/11 PASS ✅

> Esta etapa **relata**; não admite nem reclassifica. `proposta_final` é uma sugestão para adjudicação humana, nunca uma auto-admissão.

## Matriz de concordância

| termo | ili | ONTO | PULO | WordNet | join | veredicto | proposta | notas |
|---|---|---|---|---|---|---|---|---|

## Resumo por veredicto


## Conjunto mais defensável — «convergência plena» (requer junção por ILI)
_(nenhum — nenhuma convergência ancorada em ILI)_

## Convergência por termo (acordo de ≥2 fontes, mas sem ILI comum)
_(nenhum)_

## Lista de trabalho humano — divergências
_(nenhuma divergência)_

## Fonte única (aguarda segunda fonte)
_(nenhum)_

## Asserções

| # | Asserção | Resultado | Evidência |
|---|----------|-----------|-----------|
| T1 | Nenhuma junção por termo quando ambos têm ILI (ILI tem precedência). | PASS ✅ | OK |
| T2 | Junção weak(term) só ocorre sem ILI partilhado entre fontes (caso contrário aplicar-se-ia a junção por ILI). | PASS ✅ | 0 conceito(s) weak(term) |
| T3 | Nenhum ILI é fabricado; mapeamento só pela tabela declarada; pares não-mapeados são flagueados. | PASS ✅ | bogus→(None, False); unmapped_flag=False |
| T4 | Cada divergência de estatuto é registada por-fonte (sem colapso em contagem). | PASS ✅ | 0 divergência(s) |
| T5 | Termo de fonte única aparece como «fonte única» e nenhum termo admitido é descartado. | PASS ✅ | OK |
| T6 | Fonte WordNet ausente ⇒ coluna toda «—»; execução continua (exit 0). | PASS ✅ | coluna WordNet ausente e uniformemente «—» |
| T7 | proposta_final nunca é um estatuto não suportado; conservador ⇒ null em divergência. | PASS ✅ | OK |
| T8 | Entradas de classes diferentes são recusadas com erro claro. | PASS ✅ | ClassMismatch levantada para classes mistas |
| T10 | «Convergência plena» exige junção por ILI (o conjunto mais defensável nunca assenta só em weak(term)). | PASS ✅ | OK |
| T11 | Nenhum conceito só-pendente figura como linha da matriz (são contados em «descartados_pendentes»). | PASS ✅ | OK |
| T9 | concordance.json faz round-trip (contagens de term/ili estáveis). | PASS ✅ | 0 conceitos |
