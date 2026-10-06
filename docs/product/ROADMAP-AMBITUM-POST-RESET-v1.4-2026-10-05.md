# ROADMAP — CIRCE AMBITUM Pós-Reset

**Versão:** 1.4
**Data:** 06/10/2026
**Substitui:** `ROADMAP-AMBITUM-POST-RESET-v1.3-2026-10-05.md`
**Autoridade:** Product Reset + Dual Retrieval + Capability Harness + Project Master v2.4
**Baseline de fechamento:** branch `feat/pr03-derived-content-text-extraction`, commit abreviado `e29a5d7`

## 1. Estado e ordem

PR-00, PR-01, PR-02 e PR-03 estão concluídas.

A revisão de produto/arquitetura da PR-03 foi concluída e alterou seu enquadramento: OCR deixa de ser tratado como workflow de produto e passa a ser um executor possível da capability `document.extract_text`.

| ID | Unidade | Estado | Gate macro |
|---|---|---|---|
| PR-00 | Product Reset | DONE | Direção Pool-first formalizada |
| PR-01 | Audit & Freeze | DONE | Contratos preservados e legado congelado |
| PR-02 | Smart Metadata + Smart Bins Lite | DONE | Feature e fechamento documental integrados |
| REVIEW-PR03 | Capability / Derived Content Review | **DONE** | Capability Harness e escopo revisado aprovados |
| PR-03 | Derived Content Foundation + Document Text Extraction | **DONE** | Capability, persistência, fallback e superfície mínima validados |
| PRODUCT-SHELL-V1 | AMBITUM Product Shell V1 | **IMPLEMENTATION NEXT** | Substituir a superfície funcional provisória por um shell de produto coerente |
| PR-04 | Evidence Retrieval | PLANNED / REVIEW REQUIRED | Recuperação rastreável do Caso consumindo derivados quando necessário |
| PR-05 | KB + Knowledge Retrieval | PLANNED / REVIEW REQUIRED | Referência/método separados de fatos do Caso |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED / REVIEW REQUIRED | Orquestrar capabilities existentes; não duplicá-las |
| PR-07 | Live Report + Presets | PLANNED / REVIEW REQUIRED | Produto revisável como consequência do trabalho |
| PR-08 | DOCX + Vertical End-to-End Demo | PLANNED | Export fiel e prova vertical |
| PR-09 | Operational Pilot | PLANNED | Medir ganho real |
| PR-10 | Product Decision | PLANNED | Expandir/refatorar/reduzir/substituir/arquivar |

## 2. Regra de produto

Antes de cada implementação:

> **Esta capacidade reduz trabalho do policial ou apenas desloca trabalho para dentro do AMBITUM?**

Aplicar também:

> **O operador precisa conhecer o mecanismo técnico ou apenas o resultado operacional que precisa obter?**

Se o mecanismo puder ficar oculto sem reduzir controle, segurança ou rastreabilidade, ocultá-lo do workflow principal.

## 3. PR-03 — concluída

Nome:

> **Derived Content Foundation + Document Text Extraction**

Capability:

```text
document.extract_text
```

Vertical slice:

```text
documento do Caso
  ↓
texto nativo?
  ├─ sim → parser nativo
  └─ não → OCR local
               ↓
        falha objetiva?
               ├─ não → texto derivado
               └─ sim → VLM local fallback
```

Casos ambíguos: oferecer melhoria sob decisão humana.

Entregue e validado:

- pypdf para texto nativo;
- RapidOCR local;
- fallback VLM local Qwen3-VL via llama.cpp;
- proveniência e roteamento misto por página;
- API/UI mínima e revisão humana separada de `raw_text`;
- migrations `0014_pr03_document_text` e `0015_pr03_page_provenance`;
- banco operacional validado em `0015_pr03_page_provenance`.

O modelo Qwen3-VL real ainda requer validação operacional quando instalado; o fallback possui smoke determinístico. A UI entregue é uma superfície funcional provisória, não o Product Shell definitivo.

## 4. Gates PR-03 comprovados

PR-03 comprovou:

- original soberano;
- Case isolation;
- texto por página;
- raw text preservado;
- revisão humana separada;
- proveniência de executor;
- reuso de derivado válido;
- falha explícita;
- mais de um executor sob o mesmo contrato;
- UI curta sem configuração obrigatória de engine;
- ausência de dependência da futura Mesa.

## 5. Fora de PR-03

Não incorporar:

- RAG;
- embeddings/vector DB;
- Knowledge Base;
- chat/Mesa;
- áudio/transcrição;
- vídeo/frames;
- NEXUS;
- formulários;
- relatório;
- DOCX;
- cloud provider;
- processamento automático de todo Intake;
- framework universal de DerivedArtifact.

## 6. PR-04 — Evidence Retrieval

Revisar antes de implementar.

Direção:

- consultar material do Caso com source refs;
- consumir Derived Document Text;
- solicitar `document.extract_text` quando texto necessário não existir;
- não incorporar OCR próprio;
- manter filtros estruturados e busca textual/semântica sob contrato único de evidência;
- preservar isolamento entre Casos.

Pergunta de gate:

> O retrieval elimina procura/copy-paste ou cria uma nova etapa de preparação manual?

## 7. PR-05 — Knowledge Retrieval

Preservar:

- Evidence e Knowledge como domínios semanticamente distintos;
- KB não sustenta fatos atuais do Caso;
- papéis como REFERENCE / STYLE_EXAMPLE / TEMPLATE quando forem implementados;
- baixa fricção de uso.

## 8. PR-06 — Mesa IA

Mesa deve ser caller/orquestrador do Capability Harness.

Não criar tools privadas do chat quando uma capability já existir.

Fluxo alvo:

```text
intenção do policial
  ↓
Mesa
  ↓
Capability Harness
  ↓
resultado + fonte
  ↓
superfície adequada
```

Mesa não deve substituir grafo, timeline, player, tabela ou formulário quando essas superfícies forem melhores.

## 9. PR-07 — Live Report + Presets

Revisar para que:

- relatório nasça do trabalho assistido;
- fontes permaneçam rastreáveis;
- edição humana permaneça clara;
- presets reduzam esforço sem engessar autoria;
- relatório não vire um segundo workflow burocrático.

## 10. PR-08 — DOCX + Demo vertical

DOCX deve serializar conteúdo revisado.

A demo vertical deve demonstrar:

- material ingressa pelo Intake;
- capacidades produzem derivados rastreáveis;
- retrieval localiza evidência;
- IA assiste sem perder fontes;
- produto final é revisável;
- export corresponde ao produto visto.

## 11. PR-09 — Operational Pilot

Medir:

- tempo;
- ações;
- copy/paste;
- digitação;
- processamento desnecessário;
- correções;
- erros;
- qualidade de fonte;
- confiança/controle.

Economia insignificante frente à complexidade é motivo para reduzir ou rejeitar solução.

## 12. PR-10 — Product Decision

Decidir com evidência:

- expandir;
- refatorar;
- reduzir;
- substituir;
- arquivar.

## 13. Freezer

Permanecem congelados como requisitos obrigatórios:

- InvestigativeBlock;
- Produto/Seções legados;
- UX-03B antiga;
- Smart Bins avançados;
- ontologia extensa;
- colaboração;
- versionamento universal de artifacts;
- segundo monitor;
- aprovações institucionais.

## 14. Próxima unidade oficial

Após o fechamento da PR-03:

> **AMBITUM PRODUCT SHELL V1**

Essa unidade posterior deve tratar o novo shell de produto. Não pertence à PR-03 e não altera o estado concluído da capability `document.extract_text`.
