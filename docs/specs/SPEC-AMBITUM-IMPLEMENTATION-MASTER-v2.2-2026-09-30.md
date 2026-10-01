# SPEC-AMBITUM — IMPLEMENTATION MASTER

**Versão:** 2.2
**Data:** 30/09/2026
**Status:** PR-02 FINALIZING / REFINAMENTO DOCUMENTAL E UX
**Substitui:** `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.1-2026-09-28.md`
**Direção consolidada:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.2-2026-09-30.md`, fundamentado pelo Product Reset e pelo `ADR-AMBITUM-PR-002-DUAL-RETRIEVAL-CONVERSATIONAL-WORKSPACE-v1.0-2026-09-30.md`
**Repositório:** `jussie1978/AMBITUM`.

## 1. Objetivo

Executar unidades pequenas que reduzam esforço real, preservando contratos comprovados. Esta unidade fecha coerentemente PR-02B e documenta a direção futura; não entrega o pipeline completo.

## 2. Estado seguro

Windows: `C:\Projetos\CIRCE_ATHENA`, branch `feat/pr02-smart-metadata`, checkpoint `a0b2bdcd711ecc3a5e3f8a16b5b1850f2368313b`. Trabalho PR-02B existente em template e dois smokes deve ser preservado. Confirmar root/branch/HEAD/origin/status antes de editar/aplicar. Não resetar, sobrescrever alterações posteriores, force push, rebase silencioso ou editar main.

## 3. Roadmap e fronteiras

| ID | Unidade | Estado | Resultado |
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

Detalhamento: `ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md`. Dois domínios de retrieval independentes; KB não sustenta fatos do Caso; Mesa conversacional e Relatório Vivo são alvos futuros. Blocos não condicionam nenhum deles.

## 4. Contratos atuais preservados

Manter Caso/CaseMaterials/SharedDocument/SharedPerson opcional, Intake/Storage/Original, SHA-256, deduplicação, auditoria, autenticação, Pool/shell/Design System. Preservar service/API/modelo/migration 0011 de Smart Metadata, allowlists, proveniência humana atribuída no servidor, validação estrita, isolamento de Caso e batch atômico.

Migration histórica: `0009_at06b_curated_intake_storage → 0010_ux03a_product_sections → 0011_pr02_smart_metadata`. Nenhuma migration nova; não bifurcar/pular legado.

## 5. PR-02B — tarefa delimitada

| Arquivo | Alteração |
|---|---|
| app/templates/workspace.html | Retirar botão “Usar no bloco”, referência DOM, atualização de disabled e listener exclusivos dele. Preservar bridge interna e centro temporário. |
| scripts/smoke_workspace_smart_metadata.py | Retirar requisitos de bridge/Bloco, permitir ausência do formulário legado, conservar checagem de desacoplamento quando presente e da UX Quick Metadata. |
| scripts/smoke_workspace_pool_inventory.py | Retirar bridge como requisito de Pool. |

Preservar Quick Metadata, ENTER/ESCAPE, chips, batch, interseção comum, remoção sem redigitação, Smart Bins Lite/contagem/filtro e atualização canônica sem reload.

## 6. Gates proporcionais

- G0: confirmar identidade/estado; preservar pacote recebido e baseline.
- G1: revisar somente patch mínimo nos três arquivos e documentação coordenada.
- G2: executar `scripts.smoke_workspace_smart_metadata`, `scripts.smoke_workspace_pool_inventory`, Jinja parse, JS/syntax pertinente e `git diff --check`.
- G3: confirmação humana curta da remoção do botão e funcionamento Quick Metadata/Smart Bins. Demo completa anterior é evidência relatada, não repetida aqui.
- G4: apresentar caminhos, documentos novos, diff stat, decisões, testes reais e status Git antes de commit/push.

Não repetir service/HTTP/migration/Intake/Storage sem mudança material nesses domínios. Testes estáticos não comprovam comportamento em navegador; registrar separadamente a confirmação humana.

## 7. Domínios futuros

Evidence Retrieval: material do Caso ativo com source refs; seleção manual opcional. Knowledge Retrieval: referências/estilo/templates autorizados e distinguíveis. Não promover documentos da KB a evidência sem Intake formal. Separação sem impor duas tecnologias de banco.

Live Report deve poder conservar fontes, proveniência, modo de autoria, revisão e origem de alterações. DOCX serializa o preview revisado. Presets pertencem à PR-07. Voz é entrada da Mesa. Schemas/providers/permissões detalhadas pertencem às SPECs futuras.

## 8. Stop-loss

Parar antes de ampliar se exigir OCR, extração funcional, embeddings/vector DB, LLM/provider, RAG, nova KB persistente, schema de Report, DOCX, voz, refatoração completa do Workspace, remoção física de Blocos ou migration nova. Não ampliar legado.

## 9. Documentação e integração

Hierarquia vigente: Product Reset + ADR PR-002 → Project Master v2.2 → Roadmap v1.2 → ADRs / SPECs da unidade → implementação / testes / status. O ADR PR-002 registra e justifica a decisão arquitetural; o Project Master consolida a direção do produto.

Revisões novas supersedem versões anteriores explicitamente; conservar históricos. Autoridade PR-02: `ADR-AMBITUM-PR02-001-FUNDACAO-SMART-METADATA-v1.1-2026-09-30.md` e `SPEC-AMBITUM-PR02-SMART-METADATA-v1.1-2026-09-30.md`. Metodologia: `CIRCE_SPEC_DRIVEN_WORKFLOW_v1.1_2026-09-30.md`. Handoff: `STATUS-HANDOFF-AMBITUM-ARCHITECTURE-REFINEMENT-2026-09-30.md`.

Status FINALIZING até completar os gates e integração. Não afirmar testes não executados nem commit/merge inexistente. Depois da revisão, executor local aplica somente delta compatível, executa gates necessários e aguarda autorização de commit/push. PR-03 permanece fora desta branch.
