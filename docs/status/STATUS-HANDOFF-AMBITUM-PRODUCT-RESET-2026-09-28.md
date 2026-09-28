# STATUS / HANDOFF — CIRCE AMBITUM Product Reset

**Data:** 28/09/2026
**Estado:** DIREÇÃO DE PRODUTO REDEFINIDA
**Próxima unidade:** PR-01 — Audit & Freeze
**Implementação nova nesta sessão:** nenhuma
**Nome canônico:** CIRCE AMBITUM
**Nome legado:** CIRCE-ATHENA
**Repositório canônico:** `https://github.com/jussie1978/AMBITUM`

## 1. Decisão

O projeto não retomará automaticamente a UX-03B.

A prioridade passa a ser provar um fluxo vertical:

```text
Pool
→ Smart Metadata
→ OCR/Indexação
→ Retrieval
→ Base de Conhecimento
→ Assistente IA do AMBITUM
→ Relatório rastreável
```

## 2. Motivação

O fluxo anterior acumulava entidades intermediárias e risco de transferir trabalho de composição para o próprio investigador.

A nova direção procura aproveitar o trabalho que o operador já realiza naturalmente durante a investigação.

## 3. Preservar

- Caso/Workspace;
- Intake;
- Original;
- Storage;
- SHA-256;
- Pool;
- autenticação;
- auditoria;
- painéis;
- Design System.

## 4. Congelar

- UX-03B;
- Blocos como etapa obrigatória;
- Produto/Seções como etapa obrigatória;
- UX-04;
- UX-05;
- ontologia analítica completa;
- Smart Bins avançados;
- exportação sofisticada.

## 5. Próxima sessão

Primeira ação no repositório:

1. gate read-only;
2. confirmar estado atual e eventuais mudanças posteriores a `80bf959`;
3. auditar dependências reais;
4. produzir matriz MANTER / REUTILIZAR / CONGELAR / ENCAPSULAR / NÃO TOCAR;
5. identificar menor patch necessário para iniciar Smart Metadata;
6. não alterar código de domínio antes dessa auditoria.

## 6. Migração e normalização Git

Concluído em 28/09/2026:

- histórico do repositório legado `Prjkt-CIRCE/CIRCE-ATHENA` espelhado para `jussie1978/AMBITUM`;
- `main` canônica promovida para a baseline validada `80bf959d95fbd6e9a5028958cafdb9941715c297`;
- trabalho UX-03B não concluído preservado na branch `archive/ux03b-pre-product-reset-2026-09-28`;
- snapshot UX-03B arquivado no commit `40ff8da`;
- clone operacional sincronizado com `origin/main`, working tree limpa antes da entrada do Product Reset.

A falha de mirror em `refs/pull/1/head` foi restrita a ref interno/oculto do GitHub e não afetou branches ou histórico operacional.

## 7. Documentos correntes

- `ADR-AMBITUM-PR-001-PRODUCT-RESET-v1.0-2026-09-28.md`
- `SPEC-AMBITUM-MVP-01-RELATORIO-RASTREAVEL-v1.0-2026-09-28.md`
- `ROADMAP-AMBITUM-POST-RESET-v1.0-2026-09-28.md`
- `CIRCE-AMBITUM-PROJECT-MASTER-v2.0-2026-09-28.md`
- `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.0-2026-09-28.md`
- este Status/Handoff

## 8. Relação com documentação anterior

### Substituir como autoridade corrente
- Project Master v1.4 → Project Master v2.0
- Implementation Master v1.4 → Implementation Master v2.0
- roadmap corrente anterior → Roadmap Pós-Reset

### Manter
- metodologia Spec-Driven;
- Design System;
- SPEC do Intake;
- baseline Windows;
- ADR/SPEC UX-03A como registro de decisão e implementação existente.

### Arquivar como orientação anterior
- handoff de retomada UX-03A que apontava UX-03B como próxima execução.

## 9. Prompt de retomada

```text
Circe, vamos iniciar PR-01 — Audit & Freeze do CIRCE AMBITUM após o Product Reset de 28/09/2026.

Autoridades correntes:
- ADR-AMBITUM-PR-001;
- SPEC-AMBITUM-MVP-01;
- ROADMAP-AMBITUM-POST-RESET;
- Project Master v2.0;
- Implementation Master v2.0;
- Status/Handoff Product Reset.

Comece somente por gate read-only e auditoria do repositório real.
Não retome UX-03B.
Não modifique Intake/Storage.
Não implemente OCR ainda.
Entregue primeiro a matriz MANTER / REUTILIZAR / CONGELAR / ENCAPSULAR / NÃO TOCAR e o plano mínimo da PR-02.
```
