# CIRCE AMBITUM — PROJECT MASTER

**Versão:** 2.2
**Data:** 30/09/2026
**Status:** PRODUCT RESET ATIVO / PR-02 FINALIZING
**Substitui:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.1-2026-09-28.md`
**Repositório canônico:** `jussie1978/AMBITUM`
**Governança:** `origin/main` é referência integrada; esta revisão é candidata não commitada na branch `feat/pr02-smart-metadata`.

## 1. Identidade e valor

AMBITUM transforma material bruto de um Caso em informação consultável e produtos policiais rastreáveis, reduzindo trabalho mecânico e preservando autoria, julgamento e controle do investigador. O sistema recupera contexto relevante; o usuário não precisa reconstruir a investigação em Blocos para utilizar IA.

## 2. Decisão atual versus implementação

| Elemento | Estado conhecido |
|---|---|
| Intake, Storage, Original, auditoria, autenticação, Pool e shell | Contratos existentes preservados. |
| Fundação Smart Metadata | Checkpoint `a0b2bdcd711ecc3a5e3f8a16b5b1850f2368313b`. |
| Quick Metadata, chips e Smart Bins Lite | PR-02B em alterações locais; demo parcial relatada no briefing; fechamento pendente. |
| Dois retrievals, KB, nova Mesa, voz, Relatório Vivo e DOCX | Arquitetura alvo / roadmap; não entregues por esta unidade. |

Estado Windows observado em imagem: `C:\Projetos\CIRCE_ATHENA`, branch `feat/pr02-smart-metadata`, três arquivos modificados e origin `https://github.com/jussie1978/AMBITUM.git`. A imagem não substitui uma nova conferência antes de aplicar patches.

## 3. Arquitetura alvo

Caso → Pool → Smart Metadata / Smart Bins → OCR + extração + indexação → Evidence Retrieval + Knowledge Retrieval → Workspace conversacional → Relatório Vivo → revisão humana → export DOCX.

Evidence Retrieval fornece material factual do Caso ativo. Knowledge Retrieval fornece método, estrutura, estilo e referência técnica. KB não é evidência do Caso. Afirmações factuais exigem source refs do Caso; sugestões e labels não equivalem à confirmação dos fatos.

## 4. Princípios e contratos preservados

Local por padrão; original soberano; proveniência; controle humano; baixo atrito; IA assistiva; geração ancorada; arquitetura proporcional; vertical slice antes de expansão. Preservar Intake canônico, SHA-256, deduplicação por Caso, storage opaco, Original governado, auditoria, autenticação, isolamento e Design System.

## 5. Smart Metadata e Smart Bins Lite

Metadata pertence ao Caso e ao `SharedDocument`. Preservar modelo, migration 0011, service/API, proveniência definida no servidor, batch atômico e target opcional via `SharedPerson` do mesmo Caso.

Quick Metadata expõe +Alvo/+Tema/+Tag, editor inline, ENTER/ESCAPE, chips, valores comuns e remoção sem redigitação. Smart Bins Lite são agrupamentos determinísticos derivados de metadata real, com contagem de documentos e filtro no Pool. Não são inferência por IA nem classificação obrigatória.

## 6. Superfícies futuras

| Superfície | Responsabilidade |
|---|---|
| Esquerda | Pool/Smart Bins, material do Caso, organização, filtros, Intake e seleção opcional. |
| Centro | Mesa conversacional, comandos, compose, entrada por voz e refinamento com fontes. |
| Direita | Relatório Vivo/Inspector, preview real, revisão de texto, imagens, seções e fontes. |

DOCX exporta o relatório já revisado. Presets compõem o Live Report na PR-07. Não criar schema definitivo agora.

## 7. Knowledge Base futura

Papéis conceituais: REFERENCE, STYLE_EXAMPLE, TEMPLATE. Escopos futuros: pessoal, equipe e institucional. Não escolher provider/vector DB nem implementar níveis/tabelas nesta unidade. Um documento da KB que se tornar evidência deve ingressar pelo Intake do Caso.

## 8. Legado

InvestigativeBlock/InvestigativeBlockSource: FROZEN LEGACY CAPABILITY. Preservar sem expansão, sem exclusão/migração e sem requisitos para RAG/relatório/geração. Bridge interna opcional; botão “Usar no bloco” sai da Quick Metadata. Centro atual permanece temporariamente. UX-03B, Produto/Seções e Inspector/Composer antigos não são direção obrigatória.

## 9. Roadmap

| ID | Unidade | Estado | Critério macro |
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

Detalhamento: `ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md`.

## 10. Sucesso, métricas e rejeição

Medir tempo até minuta, ações manuais, digitação evitada, texto aproveitável, correções, cobertura e correção de fontes, erros de OCR e confiança/controle do operador. Comparar com método atual.

Rejeitar direção que acrescente burocracia, classificação obrigatória, montagem manual de contexto, fatos vindos da KB, texto sem suporte ou complexidade sem ganho operacional. Teste técnico aprovado não significa produto aceito.

## 11. Autoridade e próxima ação

Product Reset + `ADR-AMBITUM-PR-002-DUAL-RETRIEVAL-CONVERSATIONAL-WORKSPACE-v1.0-2026-09-30.md` → este Project Master → `ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md` → ADRs / SPECs da unidade → implementação / testes / status.

O ADR PR-002 registra e justifica a decisão arquitetural. Este Project Master consolida a visão vigente do produto; o Roadmap organiza sua sequência; ADRs e SPECs governam as unidades específicas. `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.2-2026-09-30.md` orienta a execução sem substituir esta autoridade consolidada.

Versões antigas permanecem históricas; conflitos de direção são resolvidos pelas revisões acima. Próxima ação: revisar fechamento PR-02B, aplicar com preservação do estado local, confirmar UX curta e executar gates proporcionais. Não iniciar PR-03 antes do fechamento/integração da PR-02.
