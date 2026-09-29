# ROADMAP — CIRCE AMBITUM Pós-Reset

**Versão:** 1.1  
**Data:** 28/09/2026  
**Autoridade:** ADR-AMBITUM-PR-001  
**Repositório canônico:** `jussie1978/AMBITUM`  
**Fonte da verdade:** `origin/main`  
**Substitui:** `ROADMAP-AMBITUM-POST-RESET-v1.0-2026-09-28.md`

---

## 1. Estado consolidado

Product Reset aprovado.

PR-01 foi concluída como auditoria read-only. Não foi necessário patch funcional para congelamento.

A próxima unidade executável é PR-02.

---

## 2. Roadmap corrente

| ID | Unidade | Objetivo | Estado |
|---|---|---|---|
| PR-00 | Product Reset | Formalizar nova física Pool-first | DONE |
| PR-01 | Audit & Freeze | Mapear e congelar dependências do fluxo anterior | DONE |
| PR-02 | Smart Metadata | Tags, alvos, temas, hints, proveniência e batch no Pool | READY |
| PR-03 | OCR Pipeline | OCR, texto derivado e extração revisável | PLANNED |
| PR-04 | Retrieval do Caso | Busca textual + semântica + filtros estruturados | PLANNED |
| PR-05 | Knowledge Base | Base separada, versionada e consultável | PLANNED |
| PR-06 | Presets de Produto | Templates/instruções declarativas | PLANNED |
| PR-07 | AMBITUM Report Generator | Geração rastreável de minuta | PLANNED |
| PR-08 | Vertical Demo | Prova end-to-end com dataset sintético | PLANNED |
| PR-09 | Operational Pilot | Teste controlado próximo do real | PLANNED |
| PR-10 | Product Decision | Expandir / refatorar / reduzir / substituir / arquivar | PLANNED |

---

## 3. PR-01 — conclusão

Entregue:

- baseline remota confirmada;
- branch UX-03B preservada;
- dependências reais auditadas;
- matriz `MANTER / REUTILIZAR / CONGELAR / ENCAPSULAR / NÃO TOCAR`;
- principal acoplamento legado identificado;
- confirmação de que feature flag de freeze não é necessária;
- plano mínimo de PR-02 aprovado.

Documento corrente:

```text
AUDIT-AMBITUM-PR01-MATRIZ-FREEZE-v1.0-2026-09-28.md
```

---

## 4. PR-02 — Smart Metadata

### Entrega mínima

- metadata por `SharedDocument`;
- proveniência;
- target/topic/tag/section hint;
- target opcionalmente ligado a `SharedPerson`;
- aplicação em lote;
- remoção;
- filtros no Pool;
- isolamento por Caso;
- auditoria;
- seleção genérica do Pool;
- bridge legado para Blocos.

### Não fazer

- OCR;
- LLM;
- embeddings;
- Smart Bins;
- nova entidade Asset;
- reativação UX-03B;
- dependência de Blocos/Produto/Seções.

### Gate de saída

PR-02 só fecha quando demonstrar:

```text
selecionar documentos
→ aplicar metadata
→ reload
→ filtrar por metadata
→ preservar Intake/Original
→ preservar criação legada de Bloco
```

---

## 5. PR-03 — OCR Pipeline

Somente após PR-02 fechada.

Entrega mínima:

- PDF/imagem;
- texto derivado;
- vínculo página/asset;
- preview da extração;
- candidatos revisáveis.

OCR nunca substitui o original.

---

## 6. PR-04 — Retrieval

Entrega mínima:

- filtros estruturados;
- busca textual;
- embeddings;
- resultados com source refs;
- política de reindexação.

Não começar por reranking sofisticado.

---

## 7. PR-05 — Knowledge Base

Domínio separado do Caso.

A KB orienta produção e não funciona como evidência.

---

## 8. PR-06 — Presets

Configuração declarativa.

Primeiros nomes continuam provisórios:

- Relatório Investigativo — Básico;
- Síntese de Diligências;
- Informação/Resumo Operacional.

---

## 9. PR-07 — Geração

Contrato alvo:

```text
GenerateReport(case_id, preset_id, user_instruction)
```

A geração não exige montagem manual de Blocos/Seções.

---

## 10. PR-08 — Vertical Demo

Gate obrigatório antes de expansão de acabamento.

---

## 11. Freezer

Continuam congelados:

- UX-03B anterior;
- uso obrigatório de Blocos;
- Produto/Seções como pedágio;
- Inspector Vivo antigo;
- Composer antigo;
- ontologia completa;
- Smart Bins avançados;
- colaboração;
- versionamento completo;
- exportação sofisticada;
- segundo monitor;
- workflows institucionais de aprovação.

Retorno somente por necessidade demonstrada.
