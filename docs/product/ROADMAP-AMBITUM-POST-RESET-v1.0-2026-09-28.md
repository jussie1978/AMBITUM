# ROADMAP — CIRCE AMBITUM Pós-Reset

**Versão:** 1.0
**Data:** 28/09/2026
**Autoridade:** ADR-AMBITUM-PR-001
**Repositório canônico:** `https://github.com/jussie1978/AMBITUM`
**Fonte da verdade:** `origin/main`

## Estado anterior

Preservado como histórico. UX-01, UX-02 e UX-03A continuam entregas válidas. UX-03B/04/05 deixam de ser sequência obrigatória.

## Novo roadmap

| ID | Unidade | Objetivo | Estado |
|---|---|---|---|
| PR-00 | Product Reset | Formalizar nova física Pool-first | DONE |
| PR-01 | Audit & Freeze | Mapear código atual em MANTER / CONGELAR / NÃO TOCAR | READY |
| PR-02 | Smart Metadata | Tags, alvos, temas, hints e proveniência | PLANNED |
| PR-03 | OCR Pipeline | OCR, texto derivado e extração revisável | PLANNED |
| PR-04 | Retrieval do Caso | Busca textual + semântica + filtros estruturados | PLANNED |
| PR-05 | Knowledge Base | Base separada, versionada e consultável | PLANNED |
| PR-06 | Presets de Produto | Templates/instruções de geração | PLANNED |
| PR-07 | AMBITUM Report Generator | Geração rastreável de minuta | PLANNED |
| PR-08 | Vertical Demo | Prova end-to-end com dataset sintético | PLANNED |
| PR-09 | Operational Pilot | Teste controlado com fluxo próximo do real | PLANNED |
| PR-10 | Product Decision | Expandir / refatorar / reduzir / arquivar | PLANNED |

## PR-01 — Audit & Freeze

Entregáveis:

- inventário da superfície atual;
- confirmar baseline Git;
- identificar dependências do fluxo antigo;
- preservar Intake/Pool;
- marcar Produto/Seções e Blocos como opcionais/congelados;
- impedir que código congelado se torne dependência do MVP.

Nenhuma reescrita ampla.

## PR-02 — Smart Metadata

Entrega mínima:

- metadados por asset;
- origem do metadado;
- aplicação em lote;
- filtros no Pool;
- alvo/tema/tag/section hint;
- nenhuma classificação obrigatória.

## PR-03 — OCR Pipeline

Entrega mínima:

- PDF/imagem;
- texto derivado;
- vínculo página/asset;
- preview da extração;
- confirmação de campos candidatos.

## PR-04 — Retrieval do Caso

Entrega mínima:

- busca textual;
- filtro por target/topic/tag;
- vetor/embedding;
- resultados com source refs;
- política clara de reindexação.

## PR-05 — Knowledge Base

Entrega mínima:

- domínio separado do Caso;
- upload/registro de fontes;
- categorias/presets;
- busca;
- ativação explícita durante geração.

## PR-06 — Presets

Primeiros presets:

- Relatório Investigativo — Básico;
- Síntese de Diligências;
- Informação/Resumo Operacional.

Os nomes são iniciais e não constituem padrão institucional sem validação.

## PR-07 — Geração

Entrega:

- prompt construído com contexto recuperado;
- separação Pool/KB;
- minuta;
- source map;
- warnings de lacuna;
- persistência de rascunho.

## PR-08 — Vertical Demo

Gate de produto obrigatório.

Nada posterior avança sem demo convincente.

## PR-09 — Pilot

Avaliar:

- tempo economizado;
- correções necessárias;
- confiança nas fontes;
- número de ações;
- erros de OCR;
- utilidade dos metadados;
- qualidade do relatório.

## PR-10 — Decisão

Estados possíveis:

```text
EXPANDIR
REFATORAR
REDUZIR ESCOPO
SUBSTITUIR ABORDAGEM
ARQUIVAR
```

## Itens no freezer

- UX-03B no desenho anterior;
- Inspector Vivo;
- Composer Contextual anterior;
- ontologia FATO/DECLARAÇÃO/EVIDÊNCIA completa;
- Smart Bins avançados;
- colaboração;
- versionamento completo;
- exportação sofisticada;
- segundo monitor;
- workflows institucionais de aprovação.

Podem retornar apenas por necessidade demonstrada.
