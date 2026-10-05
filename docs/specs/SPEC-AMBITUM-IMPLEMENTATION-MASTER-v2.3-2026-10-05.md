# SPEC-AMBITUM — IMPLEMENTATION MASTER

**Versão:** 2.3
**Data:** 05/10/2026
**Status:** PR-02 DONE / PR-03 REVIEW NEXT
**Substitui:** `SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.2-2026-09-30.md`
**Autoridade:** Product Reset + ADR Dual Retrieval + Project Master v2.3
**Repositório:** `jussie1978/AMBITUM`
**Baseline integrada:** `78a49128c65473421894611fcf09999fff34ee8a`

## 1. Objetivo

Executar unidades pequenas que reduzam esforço real, preservando contratos comprovados e evitando transformar mecanismos técnicos em burocracia operacional.

O sistema deve favorecer **intenção → contexto → capability → resultado revisável**, em vez de **usuário → copiar → colar → preparar estrutura → executar ferramenta → copiar resultado**.

## 2. Estado seguro

Gate observado em 05/10/2026:

```text
ROOT: C:\Projetos\CIRCE_ATHENA
REMOTE: https://github.com/jussie1978/AMBITUM.git
BRANCH: main
HEAD: 78a49128c65473421894611fcf09999fff34ee8a
UPSTREAM: origin/main
LOCAL == REMOTO: sim
WORKING TREE: limpa
```

PR-02 foi integrada pelo PR #1. Não retornar à branch de feature como base corrente.

## 3. Roadmap e fronteiras

| ID | Unidade | Estado |
|---|---|---|
| PR-00 | Product Reset | DONE |
| PR-01 | Audit & Freeze | DONE |
| PR-02 | Smart Metadata + Smart Bins Lite | **DONE** |
| PR-03 | OCR + Derived Text | **REVIEW NEXT** |
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
- proveniência humana atribuída no servidor;
- validação estrita;
- batch atômico.

Migration histórica:

`0009_at06b_curated_intake_storage → 0010_ux03a_product_sections → 0011_pr02_smart_metadata`

Não alterar essa cadeia durante a revisão documental da PR-03.

## 5. PR-02 — registro de fechamento

Feature final:

`26fdb76ae12dceb76e23626d7348da104b4c4200`

Merge:

`78a49128c65473421894611fcf09999fff34ee8a`

Resultado: Quick Metadata, chips, batch, valores comuns e Smart Bins Lite integrados; dependência operacional de “Usar no bloco” removida; documentação de arquitetura integrada.

A documentação v2.2 que dizia FINALIZING é histórica.

## 6. Regra Capability-First para novas unidades

Antes de desenhar uma UI ou schema, registrar:

- **intenção do operador**;
- **contexto já disponível**;
- **capability necessária**;
- **entrada mínima**;
- **resultado observável**;
- **proveniência**;
- **controles humanos**;
- **falhas explícitas**;
- **persistência necessária**;
- **como a futura IA poderá invocar a capability sem conhecer detalhes internos**.

Uma capability não precisa ser um botão ou uma tela.

Uma interface dedicada é justificada quando inspeção, comparação, seleção, visualização espacial/temporal ou correção humana ganham qualidade com ela.

## 7. Capability Harness — contrato conceitual para revisão

Hipótese:

```text
Intent
  ↓
Context Resolver
  ↓
Capability Registry / Tool Contract
  ↓
Policy / Permission Gate
  ↓
Executor
  ↓
Result + Provenance + Artifacts
  ↓
Human Review / Next Action
```

O harness não deve:

- conceder autonomia irrestrita;
- ocultar operações sensíveis;
- transformar inferência em fato;
- executar ação destrutiva sem gate proporcional;
- expor paths físicos ou segredos;
- acoplar IA a um único provider.

A arquitetura final dessa camada ainda não está aprovada; a PR-03 deve ajudar a provar o contrato mínimo.

## 8. REVIEW-PR03 — escopo obrigatório antes do patch

Não implementar OCR ainda.

A revisão deve decidir:

- papel de OCR no produto;
- modelo mínimo de Derived Content;
- referência a original/página/região;
- possibilidade futura de tempo/faixa para áudio e vídeo;
- execução on-demand versus automática;
- persistência versus cache;
- revisão/correção humana;
- status e falhas;
- contrato de invocação por ferramenta/IA;
- independência de provider;
- custo local e fallback;
- testes e demonstração.

### Stop-loss da revisão

Parar antes de codificar se ainda não estiver claro:

- por que o policial precisaria perceber “OCR” como função;
- como o resultado será reutilizado pela IA e retrieval;
- como o derivado se liga ao original;
- como evitar processamento desnecessário;
- como a mesma fundação evitará soluções paralelas para texto, áudio e vídeo.

## 9. Domínios futuros

Evidence Retrieval e Knowledge Retrieval permanecem separados semanticamente.

Live Report deve conservar fontes, proveniência, modo de autoria e revisão.

DOCX serializa conteúdo revisado.

NEXUS e outras ferramentas especializadas podem futuramente participar do capability harness, mas integração concreta exige unidade própria e não deve ser presumida na PR-03.

## 10. Documentação e integração

Esta versão sincroniza apenas o fechamento da PR-02 e estabelece o gate de revisão da PR-03.

Nenhuma implementação PR-03, migration nova, OCR, RAG, KB, voz, relatório ou integração NEXUS é autorizada por este documento.

Próxima unidade: `REVIEW-PR03 — OCR / Derived Content / Capability Harness`.
