# SPEC-AMBITUM — IMPLEMENTATION MASTER

**Versão:** 2.1  
**Data:** 28/09/2026  
**Status:** PR-01 CONCLUÍDA / PR-02 READY  
**Direção:** Product Reset Pool-first  
**Repositório canônico:** `jussie1978/AMBITUM`  
**Fonte da verdade:** `origin/main`  
**Substitui:** `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.0-2026-09-28.md`

---

## 1. Objetivo

Implementar o AMBITUM em unidades verticais pequenas, preservando contratos comprovados e impedindo que o fluxo anterior condicione o novo MVP.

---

## 2. Ordem

```text
PR-00 PRODUCT RESET              DONE
→ PR-01 AUDIT/FREEZE             DONE
→ PR-02 SMART METADATA           READY
→ PR-03 OCR
→ PR-04 RETRIEVAL
→ PR-05 KNOWLEDGE BASE
→ PR-06 PRESETS
→ PR-07 REPORT GENERATOR
→ PR-08 VERTICAL DEMO
→ PR-09 PILOT
→ PR-10 PRODUCT DECISION
```

Nenhuma unidade antecipa a próxima sem dependência demonstrada.

---

## 3. Estado congelado confirmado pela PR-01

### Manter

- Caso;
- CaseMaterials;
- SharedDocument;
- Intake;
- Storage;
- Original;
- Pool;
- auditoria;
- autenticação;
- shell/painéis.

### Congelar

- InvestigativeBlock como workflow obrigatório;
- WorkspaceProduct/ProductSection como workflow obrigatório;
- UX-03B;
- Inspector/Composer antigos como direção;
- ontologia analítica extensa.

### Encapsular

```text
Pool selection ↔ create-block-form
```

Transformar em seleção genérica com bridge legado.

### Não tocar no PR-02

- Intake;
- Storage;
- Original;
- migrations antigas;
- AuthGuard global;
- Produto/Seções;
- branch UX-03B.

---

## 4. Regra de testes

Executar validação proporcional ao patch.

Não repetir bateria completa de baseline imutável apenas por retomada, pausa ou formalidade.

Aumentar a bateria quando:

- arquivo de domínio relacionado for tocado;
- migration afetar cadeia existente;
- regressão aparecer;
- contrato de boundary mudar.

---

## 5. PR-02 — Smart Metadata

Autoridades:

```text
ADR-AMBITUM-PR02-001-FUNDACAO-SMART-METADATA-v1.0-2026-09-28.md
SPEC-AMBITUM-PR02-SMART-METADATA-v1.0-2026-09-28.md
```

### Objetivo

Adicionar metadata opcional e batch ao Pool sem introduzir OCR ou dependência do fluxo congelado.

### Fundação

```text
Caso
→ SharedDocument
→ AssetSmartMetadata
```

Não criar `Asset` genérico nesta unidade.

### Kinds iniciais

```text
target
topic
tag
section_hint
event_ref
relevance
source_kind
validation_status
```

### Proveniência

```text
human_confirmed
ai_suggested
system_derived
```

PR-02 grava ações humanas como `human_confirmed`.

### Target

Pode usar `SharedPerson` do mesmo Caso, mas label livre continua permitido.

### Batch

- até limite centralizado;
- documentos únicos;
- transação atômica;
- isolamento por Caso;
- add/remove;
- sem mutação parcial.

### Pool

- seleção genérica;
- filtros target/topic/tag;
- ação batch;
- bridge para Bloco legado.

---

## 6. PR-02 — fronteiras

Não implementar:

- OCR;
- extração automática;
- IA;
- embeddings;
- Retrieval;
- Smart Bins;
- entidade Asset genérica;
- Knowledge Base;
- report generator;
- exportação;
- UX-03B.

---

## 7. Migration corrente

História obrigatória:

```text
0009_at06b_curated_intake_storage
→ 0010_ux03a_product_sections
→ 0011_pr02_smart_metadata
```

Não bifurcar a cadeia para “pular” Produto/Seções congelados.

---

## 8. Gates PR-02

### G0 — Local read-only

Confirmar:

- root;
- remote;
- branch;
- `origin/main`;
- working tree;
- AGENTS.md aplicáveis.

Não resetar trabalho local automaticamente.

### G1 — Domínio

Provar:

- CRUD mínimo;
- duplicidade;
- target livre/SharedPerson;
- isolamento;
- atomicidade;
- proveniência.

### G2 — HTTP/auditoria

Provar:

- auth preservada;
- payloads estritos;
- Caso inexistente;
- IDs externos;
- batch;
- rollback da auditoria.

### G3 — Migration

Provar cadeia Alembic real em banco descartável.

### G4 — Pool

Provar:

- seleção genérica;
- batch;
- filtros;
- reload;
- bridge legado.

### G5 — Regressão proporcional

Executar smokes de Pool, Intake, Original/Storage atingidos pela superfície editada, Jinja e diff check.

---

## 9. Stop-loss global

Parar antes de ampliar se uma unidade exigir simultaneamente:

- reescrita de Intake;
- nova ontologia complexa;
- múltiplos providers;
- editor completo;
- exportação final;
- reformulação total do Workspace.

Para PR-02 especificamente, parar se exigir:

- OCR;
- Asset genérico;
- Blocos;
- Produto/Seções;
- mudança de storage;
- mudança global de autenticação.

---

## 10. Git

Cada unidade funcional deve:

1. partir de baseline confirmada;
2. usar branch coerente;
3. evitar enxurrada de branches;
4. stage explícito;
5. executar testes proporcionais;
6. revisar diff;
7. commit/push;
8. sincronizar local/remoto;
9. atualizar documentação corrente quando estado ou contrato mudar.

Documentação não deve afirmar commit que ainda não existe.

---

## 11. Próxima ação

Executar PR-02 segundo sua SPEC.

Nada da PR-03 deve entrar silenciosamente.
