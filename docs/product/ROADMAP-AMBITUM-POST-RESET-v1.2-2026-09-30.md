# ROADMAP — CIRCE AMBITUM Pós-Reset

**Versão:** 1.2
**Data:** 30/09/2026
**Substitui:** `ROADMAP-AMBITUM-POST-RESET-v1.1-2026-09-28.md`
**Direção consolidada:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.2-2026-09-30.md`, fundamentado pelo Product Reset e pelo `ADR-AMBITUM-PR-002-DUAL-RETRIEVAL-CONVERSATIONAL-WORKSPACE-v1.0-2026-09-30.md`
**Status documental:** revisão candidata na branch atual, sem commit/merge nesta unidade.

## 1. Estado e ordem

PR-00 e PR-01 DONE conforme histórico. PR-02 FINALIZING: fundação commitada e PR-02B não commitada. Nenhuma capacidade futura abaixo deve ser apresentada como implementada.

| ID | Unidade | Estado | Gate macro |
|---|---|---|---|
| PR-00 | Product Reset | DONE | Direção Pool-first formalizada. |
| PR-01 | Audit & Freeze | DONE | Contratos preservados e legado congelado. |
| PR-02 | Smart Metadata + Smart Bins Lite | FINALIZING | Fechamento técnico, confirmação humana curta, revisão, commit e merge pendentes. |
| PR-03 | OCR + Derived Text | PLANNED | Derivados revisáveis, vinculados ao original/página. |
| PR-04 | Evidence Retrieval | PLANNED | Recuperação do Caso ativo com source refs. |
| PR-05 | Knowledge Base + Knowledge Retrieval | PLANNED | Referências com papéis próprios e separação factual. |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED | Trabalho conversacional com fontes dos dois domínios distinguíveis. |
| PR-07 | Live Report + Presets | PLANNED | Produto editável, rastreável e revisável durante sua construção. |
| PR-08 | DOCX + Vertical End-to-End Demo | PLANNED | Export fiel ao relatório revisado e prova com dataset sintético. |
| PR-09 | Operational Pilot | PLANNED | Medir esforço, qualidade e erros em uso controlado. |
| PR-10 | Product Decision | PLANNED | Expandir, refatorar, reduzir, substituir ou arquivar conforme evidência. |

IDs PR-06 a PR-08 preservados com objetivos refinados: presets passam a integrar o Relatório Vivo; DOCX passa a integrar a demonstração vertical.

## 2. PR-02 — saída atual

Preservar fundação `SharedDocument`/metadata, proveniência, atomicidade, isolamento e migration 0011. Entregar Quick Metadata/chips/batch/valores comuns e Smart Bins Lite determinísticos, sem reload após mutações. Remover “Usar no bloco”; bridge/criação de Blocos não são gates.

Demo parcial já relatada: selecionar dois documentos → +Tag → PIX → ENTER → chips/bin/contador → filtrar → remover PIX comum → atualização sem reload. Após remoção do botão, confirmar apenas ausência da ação e funcionamento curto de seleção/Quick Metadata/Smart Bins, sem repetir a demo completa.

Fechamento: smokes Workspace Smart Metadata e Pool Inventory, Jinja parse, JS syntax e diff check; revisão; commit/push/merge autorizado e status atualizado. FINALIZING não pode virar DONE antecipadamente.

## 3. PR-03 — OCR + Derived Text

Depende do fechamento da PR-02. PDF/imagem, texto derivado, vínculo ao documento/página, preview da extração e candidatos revisáveis. Original permanece soberano. Gate: texto consultável e trecho rastreável ao original, falhas explícitas sem perda do material.

## 4. PR-04 — Evidence Retrieval

Depende de derivados da PR-03. Busca textual/semântica e filtros estruturados, source refs, isolamento do Caso e política de reindexação. Provar relevância, rastreabilidade e ausência de recuperação de outro Caso. Não exige InvestigativeBlock. Tecnologia/provider e limites serão definidos na SPEC própria.

## 5. PR-05 — KB + Knowledge Retrieval

Domínio independente: REFERENCE/STYLE_EXAMPLE/TEMPLATE. Escolha/versionamento/permissões conforme SPEC futura, sem obrigar implementação simultânea de escopos pessoal/equipe/institucional. Gate: referência orienta método/forma sem fornecer fatos atuais; documento evidencial entra pelo Intake.

## 6. PR-06 — Mesa conversacional

Depende dos contratos de PR-04/05. Chat/comandos/compose, respostas com identidade das fontes, refinamento e seleção opcional. Voz compartilha a interface como modalidade; disponibilidade deve ser decidida na SPEC, sem subsistema conceitual separado. Gate: investigador trabalha sem montar Blocos.

## 7. PR-07 — Live Report + Presets

Depende da Mesa e contratos de fontes. Preview real, inserção/substituição/reorganização, seções/imagens e revisão. Conteúdo deve poder manter source_refs, provenance, authorship_mode, revisão e origem de alterações. Gate: texto em construção revisável e fontes preservadas. Schema/ações serão decididos nesta etapa.

## 8. PR-08 — DOCX + Demo vertical

Depende do relatório revisável. Exportar o conteúdo revisado, sem geração opaca final. Dataset sintético demonstra Intake → organização → derivados → retrievals → conversa → relatório → revisão → DOCX. Gate: correspondência preview/export e ganho operacional demonstrável antes de ampliar acabamento.

## 9. PR-09 e PR-10

Piloto controlado mede qualidade, esforço, suporte factual, revisões e erros. Decisão final baseada nos resultados: expandir/refatorar/reduzir/substituir/arquivar. Economia insignificante frente à complexidade é razão para reduzir ou rejeitar.

## 10. Freezer e limite da unidade

Legado de Blocos/Produto/Seções/UX-03B preservado, sem requisito nem expansão. Adiar Smart Bins avançados, ontologia extensa, colaboração, versionamento completo, segundo monitor e aprovações institucionais. Agora: arquitetura + documentação + patch mínimo PR-02B. Nenhum OCR/RAG/KB persistente/chat/Report schema/voz/DOCX/migration nova.
