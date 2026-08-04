# LexWarrant — relator de garantia/concordância cruzada (ancorado no ILI)

**Etapa final, de RELATO, do Protocolo Fase 0.** Ingere os `result.json` por-fonte
produzidos pelos motores existentes (ONTO = `phase0_skos.py`, PULO =
`phase0_pulo.py` e, futuramente, o export enriquecido da WordNet), junta os
veredictos **por ILI** e produz uma **matriz de concordância** + um **veredicto por
termo** para adjudicação humana por convergência.

> **RELATA; nunca decide.** Não há qualquer mecanismo que promova um termo a um
> estatuto por *contagem* de fontes — isso reintroduziria a fronteira métrica
> UF/RT que o protocolo rejeita. `proposta_final` é sempre uma **sugestão** para
> o humano, nunca uma auto-admissão.

## Executar

```powershell
python lexwarrant.py "..\ONTO\fase0\TexturaUniforme.result.json" ^
                     "..\PULO Thesaurus GUI\fase0\TexturaUniforme.result.json" ^
                     --outdir .
```

Rótulo por fonte: inferido do caminho (ONTO / PULO / WordNet) ou explícito via
`--source ROTULO=ficheiro.json`. Requer ≥2 fontes, todas da **mesma classe-alvo**
(classes mistas são recusadas). Sem dependências além da biblioteca padrão.

Sai com código ≠ 0 se alguma asserção (T1–T9) falhar (CI-friendly).

## Chave de junção — CILI primário, termo secundário (fraco)

- **Primário (CILI):** dois registos juntam-se sse partilharem um id oficial
  ``i…`` (resolvido via mapa CILI / OEWN). Offsets PWN 3.0 usam id local
  ``pwn30-…``; legado OMW ``ili-30-…`` / ``por-30-…`` são **pivôs PWN 3.0**, não
  CILI. A tabela legada ``ili_equivalence.json`` é **opcional** (auditoria /
  migração); a sua ausência **não** significa que o CILI esteja indisponível.
- **Secundário (fraco):** termos sem âncora CILI partilhável podem casar por
  string normalizada (`join="weak(term)"`, tipicamente com gate de glosa).
- Um termo presente em **apenas uma** fonte é mantido (`fonte única`), nunca
  descartado.
- ``concept_mapping.excluded_cili`` anula ``proposta_final`` para CILIs
  semanticamente rejeitados (resolução formal ≠ admissão).

O conceito é ancorado no **termo (lema)** e **confirmado pelo ILI**: homógrafos com
ILI disjunto ficam em linhas separadas (nunca fundidos por string), e membros
distintos do mesmo synset (ex.: *constante* vs *invariável*) permanecem em linhas
distintas.

## Veredicto (por conceito)

| veredicto | condição |
|-----------|----------|
| `convergência plena` | presente em ≥2 fontes **e** todas concordam no estatuto |
| `divergência de relação` | presente em ≥2 fontes **mas** o estatuto difere (regista-se cada fonte) |
| `fonte única` | presente em exactamente 1 fonte |
| `sinalização` | ≥1 fonte marca `sinalizacao` e nenhuma admite |

A divergência é **informação**, não ruído: nunca é colapsada numa contagem; a
matriz mostra sempre o valor de cada fonte.

## Política de divergência

- **`conservative`** (predefinição): mantém-se um estatuto só se **todas** as
  fontes atestantes concordarem; qualquer desacordo ⇒ `proposta_final = null`
  (aguarda adjudicação humana).
- **`informed`** (`--policy informed`): `proposta_final = estatuto maioritário`;
  empates ⇒ `null`; a divergência é sempre registada.

Em ambas, `proposta_final` é apenas uma sugestão.

## Saídas

| Ficheiro | Conteúdo |
|----------|----------|
| `<Classe>.concordance.md`   | matriz legível + contagens por veredicto + lista de convergências e worklist de divergências + quadro de asserções |
| `<Classe>.concordance.json` | por-conceito `{term, ili, sources:{ONTO,PULO,WordNet}, join, veredicto, proposta_final, divergences[], union_of_provenance[], notes[]}` + `summary` |

A coluna **WordNet** existe desde o início: se nenhuma fonte WordNet for dada, a
coluna fica uniformemente `—` (não é erro). Acrescentar a WordNet mais tarde é um
**preenchimento de coluna**, não uma reescrita — ver `examples/`.

## Asserções de aceitação (T1–T9)

Verificadas em cada execução e impressas com PASS/FAIL (exit ≠ 0 se falhar):
T1 precedência do ILI sobre o termo · T2 junções fracas etiquetadas · T3 nenhum
ILI fabricado, pares não-mapeados flagueados · T4 divergências registadas
por-fonte · T5 fonte única nunca descartada · T6 WordNet ausente ⇒ coluna `—`,
exit 0 · T7 política de `proposta_final` respeitada · T8 classes mistas recusadas
· T9 round-trip do JSON.

## Nota sobre um achado real

No exemplo `TexturaUniforme`, *uniformidade* e *invariância* aparecem como
**divergência de relação**: o motor ONTO classificou-as `UF` (altLabel) e o PULO
encaminhou-as para `atributo` (attribute_bucket). Isto **não** é um bug do relator
— é precisamente o tipo de discrepância entre recursos que esta etapa existe para
tornar visível na *worklist* humana.
