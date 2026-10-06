# SPEC-AMBITUM — IMPLEMENTATION MASTER

**Versão:** 2.4
**Data:** 06/10/2026
**Status:** PR-03 DONE / AMBITUM PRODUCT SHELL V1 NEXT
**Substitui:** `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.3-2026-10-05.md`
**Autoridade:** Product Reset + Dual Retrieval + Capability Harness + Project Master v2.4
**Repositório:** `jussie1978/AMBITUM`
**Baseline de fechamento:** branch `feat/pr03-derived-content-text-extraction`, commit abreviado `e29a5d7`

## 1. Objetivo

Executar unidades pequenas que reduzam esforço real, preservando contratos comprovados e evitando transformar mecanismos técnicos em burocracia operacional.

Fluxo preferido:

```text
intenção / ação explícita
  ↓
contexto autorizado
  ↓
capability
  ↓
policy
  ↓
executor
  ↓
resultado + proveniência
  ↓
revisão
```

## 2. Estado seguro observado

No fechamento técnico da PR-03, foi observado:

```text
ROOT: C:\Projetos\CIRCE_ATHENA
REMOTE: https://github.com/jussie1978/AMBITUM.git
BRANCH: feat/pr03-derived-content-text-extraction
HEAD abreviado antes do fechamento documental: e29a5d7
WORKING TREE: limpa
ALEMBIC OPERACIONAL: 0015_pr03_page_provenance
```

O banco operacional foi migrado somente após backup com SHA-256 conferido e ensaio bem-sucedido em cópia isolada.

## 3. Roadmap

| ID | Unidade | Estado |
|---|---|---|
| PR-00 | Product Reset | DONE |
| PR-01 | Audit & Freeze | DONE |
| PR-02 | Smart Metadata + Smart Bins Lite | DONE |
| REVIEW-PR03 | Capability / Derived Content Review | DONE |
| PR-03 | Derived Content Foundation + Document Text Extraction | **DONE** |
| PRODUCT-SHELL-V1 | AMBITUM Product Shell V1 | **IMPLEMENTATION NEXT** |
| PR-04 | Evidence Retrieval | PLANNED / REVIEW REQUIRED |
| PR-05 | KB + Knowledge Retrieval | PLANNED / REVIEW REQUIRED |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED / REVIEW REQUIRED |
| PR-07 | Live Report + Presets | PLANNED / REVIEW REQUIRED |
| PR-08 | DOCX + Vertical Demo | PLANNED |
| PR-09 | Operational Pilot | PLANNED |
| PR-10 | Product Decision | PLANNED |

## 4. Contratos preservados

Manter:

- Caso / CaseMaterials;
- SharedDocument;
- SharedPerson opcional;
- Intake / Storage / Original;
- SHA-256 e deduplicação;
- auditoria e autenticação;
- isolamento de Caso;
- Pool/shell/Design System;
- Smart Metadata;
- migration 0011;
- validação estrita;
- batch atômico.

Migration histórica:

```text
0009_at06b_curated_intake_storage
  → 0010_ux03a_product_sections
  → 0011_pr02_smart_metadata
  → 0014_pr03_document_text
  → 0015_pr03_page_provenance
```

As migrations `0014` e `0015` foram aplicadas e validadas no banco operacional, preservando as estruturas e contagens anteriores.

## 5. Capability Harness — contrato aceito

A hipótese da v2.3 passa a ser decisão arquitetural aprovada.

```text
Caller
  ↓
Intent / Explicit Action
  ↓
Context Resolver
  ↓
Capability Contract
  ↓
Policy / Permission Gate
  ↓
Executor Selection
  ↓
Execution
  ↓
Result / Artifact + Provenance
  ↓
Human Review / Next Action
```

Regras:

- capability pertence ao AMBITUM;
- executor é substituível;
- LLM não recebe autoridade direta sobre paths/recursos;
- caller futuro de IA usa o mesmo contrato da UI;
- operações sensíveis mantêm gates proporcionais;
- proveniência é parte do resultado quando necessária;
- modelo/provider não define arquitetura da capability.

## 6. Unidade PR-03

Documento normativo específico:

`SPEC-AMBITUM-PR03-DERIVED-CONTENT-DOCUMENT-TEXT-EXTRACTION-v1.0-2026-10-05.md`

Capability:

```text
document.extract_text
```

Objetivo:

> obter texto utilizável e rastreável de documento do Caso sem exigir que o policial escolha o mecanismo de extração.

## 7. Sequência de implementação PR-03

Sequência concluída. O resultado integrado contém:

- pypdf como executor nativo;
- RapidOCR como executor OCR local;
- cliente de fallback VLM local para Qwen3-VL servido por llama.cpp;
- roteamento por página e provenance `native`, `ocr` ou `vlm`, com extraction `mixed` quando necessário;
- API/UI mínima e revisão humana auditável separada de `raw_text`;
- persistência aditiva pelas migrations `0014` e `0015`.

### T01 — inspeção/preflight

Antes de patch:

- confirmar branch;
- confirmar `origin`;
- confirmar `main` atual;
- working tree;
- migrations;
- modelos `SharedDocument` / Caso;
- storage/original;
- padrões de services/routes;
- auditoria;
- testes/smokes existentes.

Não adivinhar schema existente.

### T02 — contrato e persistência mínima

Definir fisicamente o mínimo para:

- derivado por documento;
- páginas;
- raw text;
- reviewed text opcional;
- status;
- fingerprint do original;
- proveniência de execução.

Evitar entidade universal antecipada.

### T03 — executor nativo

Implementar extração de camada textual quando disponível.

Gate: documento com texto nativo não deve cair em OCR sem necessidade.

### T04 — OCR local

Implementar executor OCR encapsulado.

Gate: mesmo caller/contrato de capability.

### T05 — VLM local fallback

Implementar fallback para falhas objetivas e melhoria explícita.

Não acoplar schema a Qwen/modelo específico.

### T06 — UI mínima

Adicionar ação equivalente a **Obter texto**, estado, resultado por página, original/revisão e melhoria quando aplicável.

Não criar central OCR.

### T07 — revisão/reuso/falhas

Demonstrar:

- raw preservado;
- reviewed separado;
- derivado válido reutilizado;
- failed explícito;
- reprocessamento controlado.

### T08 — validação e aceitação humana

Executar gates proporcionais da SPEC.

Confirmar ganho operacional em fluxo curto.

## 8. Seleção de executor

Direção:

```text
native usable?
  ├─ yes → native
  └─ no → local OCR
              ↓
       objective failure?
              ├─ no → result
              └─ yes → local VLM

ambiguous/low subjective quality
  → operator-triggered improvement
```

Critérios automáticos devem ser determinísticos e documentados.

Não criar confidence universal fictícia.

## 9. Persistência

Derived Document Text deve:

- pertencer ao Caso;
- apontar para `SharedDocument`;
- apontar para fingerprint canônico;
- guardar páginas;
- separar bruto/revisado;
- registrar execução;
- sobreviver à sessão;
- ser reutilizável por PR-04.

Não transformar o derivado em nova evidência independente do original.

## 10. Segurança

Durante PR-03:

- execução local;
- sem provider externo;
- sem path arbitrário no contrato;
- sem quebra de Case isolation;
- sem alteração de original;
- sem conteúdo sensível desnecessário em logs;
- sem permissões novas implícitas para LLM.

## 11. Separação epistemológica

Manter:

```text
extraído ≠ interpretado
interpretado ≠ confirmado
ausência na extração ≠ evidência de ausência
```

`document.extract_text` produz representação derivada, não conclusão investigativa.

Capabilities semânticas futuras devem declarar sua natureza separadamente.

## 12. Validação mínima

A PR-03 não fecha sem evidência para:

- native text;
- scanned/OCR;
- VLM fallback;
- revisão humana;
- reuse/idempotência proporcional;
- falha;
- Case isolation;
- UI curta;
- original intacto;
- proveniência.

Testes devem usar material sintético ou autorizado.

Estado de fechamento: smokes fundacional, native, OCR/mixed, VLM fallback, HTTP e UI passaram. O fallback VLM possui servidor fake determinístico; a execução contra o modelo Qwen3-VL real permanece validação operacional futura e não invalida o fechamento funcional.

## 13. Stop-loss

Parar antes de ampliar se surgir necessidade de:

- RAG funcional;
- embeddings;
- vector DB;
- KB;
- Mesa;
- áudio/vídeo;
- NEXUS;
- formulário;
- relatório;
- DOCX;
- cloud;
- processamento automático de todo Intake;
- framework universal de DerivedArtifact;
- refatoração total do Workspace.

Se a implementação revelar decisão nova sobre boundary persistente/segurança/contrato, registrar antes de prosseguir.

## 14. PR-04 e posteriores

PR-04 deve consumir `document.extract_text`, não duplicar OCR.

PR-06 deve chamar a capability existente, não criar tool paralela privada do chat.

NEXUS pode participar futuramente do harness em unidade própria.

## 15. Documentação e integração

PR-03 está concluída e pronta para Pull Request. Sua superfície atual é funcional e provisória: não deve ser expandida ou redesenhada neste fechamento.

O próximo ciclo é **AMBITUM PRODUCT SHELL V1**, em unidade posterior e separada. PR-04 e demais unidades permanecem planejadas após essa reorganização de superfície.
