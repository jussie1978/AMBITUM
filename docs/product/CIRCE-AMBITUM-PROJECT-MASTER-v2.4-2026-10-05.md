# CIRCE AMBITUM — PROJECT MASTER

**Versão:** 2.4
**Data:** 05/10/2026
**Status:** PRODUCT RESET ATIVO / PR-02 DONE / REVIEW-PR03 APROVADA / PR-03 IMPLEMENTATION NEXT
**Substitui:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.3-2026-10-05.md`
**Repositório canônico:** `jussie1978/AMBITUM`
**Baseline observada:** `main` / `origin/main` no merge da PR #2, commit abreviado `315418e`
**PR #2:** fechamento documental da PR-02 e gate de revisão da PR-03
**Decisão arquitetural nova:** `ADR-AMBITUM-PR03-001-CAPABILITY-HARNESS-v1.0-2026-10-05.md`

## 1. Identidade e valor

AMBITUM transforma material bruto de um Caso em informação consultável e produtos policiais rastreáveis, reduzindo trabalho mecânico e preservando autoria, julgamento e controle do investigador.

A direção do produto é **context-first, capability-first e low-friction**.

O operador deve poder expressar a tarefa que precisa realizar enquanto o AMBITUM resolve contexto, capability, execução e proveniência de forma governada.

Exemplos de intenção operacional:

- “obtenha o texto deste documento”;
- “transcreva este áudio”;
- “extraia os frames deste trecho do vídeo”;
- “localize onde aparece este telefone”;
- “preencha este formulário com dados do Caso”;
- “compare estes documentos”;
- “analise estas transações e mostre relações relevantes”.

Esses exemplos orientam arquitetura futura; apenas capacidades explicitamente marcadas como implementadas devem ser tratadas como disponíveis.

## 2. Estado integrado comprovado

| Elemento | Estado |
|---|---|
| Intake, Storage, Original, auditoria, autenticação, Pool e shell | Preservados |
| Smart Metadata + Smart Bins Lite | Integrados |
| PR-02 | DONE |
| Fechamento documental PR-02 | Integrado via PR #2 |
| Baseline observada após PR #2 | `315418e` |
| REVIEW-PR03 | **APROVADA** |
| ADR Capability Harness | **DECISÃO ACEITA / PENDENTE DE INTEGRAÇÃO DESTA REVISÃO** |
| PR-03 | **IMPLEMENTATION NEXT**, após integração documental |

PR-03 ainda não está implementada.

## 3. Arquitetura alvo

Cadeia estratégica:

```text
Caso
  ↓
Pool
  ↓
metadata/organização
  ↓
capabilities de extração/derivação
  ↓
Evidence Retrieval
  ↓
IA contextual / ferramentas especializadas
  ↓
produto revisável
  ↓
exportação
```

A arquitetura não deve obrigar o policial a manipular conceitos internos como OCR, parser, chunks, embeddings, índices, jobs ou providers para tarefas normais.

## 4. Princípios preservados

- local por padrão;
- original soberano;
- proveniência e rastreabilidade;
- controle humano;
- baixo atrito;
- IA assistiva;
- geração ancorada;
- isolamento entre Casos;
- Intake canônico;
- SHA-256 e deduplicação;
- storage opaco;
- auditoria;
- autenticação;
- arquitetura proporcional;
- vertical slice antes de expansão;
- Design System.

## 5. Capability-First

Antes de implementar nova funcionalidade, perguntar:

> **O operador precisa aprender um workflow novo ou pode pedir o resultado e deixar o AMBITUM usar contexto e ferramentas de forma governada?**

Quando seguro e rastreável, preferir a segunda opção.

Isso não significa chat-only.

Superfícies especializadas permanecem corretas quando ajudam a:

- inspecionar;
- comparar;
- selecionar;
- revisar;
- corrigir;
- visualizar relações, tempo ou estrutura.

## 6. Capability Harness — decisão aceita

O AMBITUM adotará progressivamente:

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
Result / Artifact + Provenance
  ↓
Human Review / Next Action
```

### 6.1. Regra estrutural

**Capability pertence ao AMBITUM.**

LLM/VLM, UI e serviços são callers possíveis.

Executor é substituível.

Exemplo:

```text
document.extract_text
  ├─ native_pdf
  ├─ local_ocr
  └─ local_vlm
```

A future Mesa não deve possuir uma segunda implementação das mesmas tools.

### 6.2. Não autonomia irrestrita

O harness não autoriza:

- paths arbitrários;
- bypass de Case isolation;
- operações destrutivas sem gate;
- envio externo implícito;
- transformação de inferência em fato;
- execução sem proveniência quando ela é necessária.

## 7. PR-03 revisada

Nome canônico:

> **PR-03 — Derived Content Foundation + Document Text Extraction**

Primeira capability:

```text
document.extract_text
```

Estratégia:

```text
texto nativo utilizável?
  ├─ sim → extração nativa
  └─ não → OCR local
               ↓
        falha objetiva?
               ├─ não → resultado
               └─ sim → VLM local fallback
```

Casos ambíguos devem favorecer ação humana de **Melhorar extração**, não consumo automático de VLM.

## 8. Derived Content

Derived Content é reconhecido como conceito arquitetural de resultado persistente ligado a material soberano.

Nesta etapa:

- implementar apenas texto derivado de documento;
- persistir por página;
- manter `raw_text`;
- permitir camada humana revisada separada;
- registrar proveniência;
- reutilizar resultado válido;
- não criar framework universal antecipadamente.

Generalização para áudio/vídeo só ocorrerá após evidência concreta.

## 9. Extração versus interpretação

Contrato obrigatório:

```text
EXTRAÇÃO
material → representação derivada fiel

INTERPRETAÇÃO
material/derivado → inferência, resumo, entidades, resposta
```

`document.extract_text` não deve resumir nem converter inferência em conteúdo extraído.

VLM pode executar extração, mas a origem VLM deve ser rastreável.

## 10. Superfícies de produto

| Superfície | Responsabilidade |
|---|---|
| Pool | materiais, seleção, metadata, filtros e contexto visual |
| Ações/capabilities | execução governada de tarefas |
| Mesa/IA futura | intenção e orquestração |
| Inspector/resultado | inspeção/revisão contextual |
| Relatório Vivo | produto editável/revisável |
| Ferramentas especializadas | grafo, timeline, mídia, tabelas, formulários |

A conversa não substitui interfaces que representem melhor o problema.

## 11. Evidence e Knowledge Retrieval

Continuam semanticamente distintos.

- Evidence Retrieval trabalha com material factual do Caso ativo e source refs.
- Knowledge Retrieval trabalha com método, estilo, referência e templates autorizados.
- KB não é evidência do Caso.

PR-04 poderá consumir texto derivado da PR-03 sem implementar OCR dentro de retrieval.

## 12. NEXUS

NEXUS é candidato a ferramenta especializada futura do Capability Harness.

Exemplo conceitual:

```text
nexus.analyze_transactions
  ↓
resultado estruturado
  ↓
grafo/tabela NEXUS
```

Nenhuma integração NEXUS é autorizada pela PR-03.

## 13. Legado

`InvestigativeBlock` / `InvestigativeBlockSource` permanecem **FROZEN LEGACY CAPABILITY**.

Produto/Seções e UX-03B antiga permanecem fora do workflow obrigatório.

Não ampliar legado para viabilizar PR-03.

## 14. Roadmap corrente

| ID | Unidade | Estado |
|---|---|---|
| PR-00 | Product Reset | DONE |
| PR-01 | Audit & Freeze | DONE |
| PR-02 | Smart Metadata + Smart Bins Lite | DONE |
| REVIEW-PR03 | Capability/Derived Content Review | **DONE** |
| PR-03 | Derived Content Foundation + Document Text Extraction | **IMPLEMENTATION NEXT** |
| PR-04 | Evidence Retrieval | PLANNED / REVIEW REQUIRED |
| PR-05 | KB + Knowledge Retrieval | PLANNED / REVIEW REQUIRED |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED / REVIEW REQUIRED |
| PR-07 | Live Report + Presets | PLANNED / REVIEW REQUIRED |
| PR-08 | DOCX + Vertical End-to-End Demo | PLANNED |
| PR-09 | Operational Pilot | PLANNED |
| PR-10 | Product Decision | PLANNED |

## 15. Critérios de sucesso

Medir:

- tempo até resultado útil;
- ações manuais;
- copy/paste evitado;
- texto aproveitável;
- correções;
- processamento evitado por reutilização;
- rastreabilidade;
- falhas;
- confiança e controle do operador.

Para PR-03, sucesso significa:

> **obter texto utilizável e rastreável sem o policial precisar escolher como ele foi extraído.**

## 16. Rejeição

Rejeitar ou simplificar direção que:

- acrescente burocracia;
- exponha mecanismo técnico como workflow obrigatório;
- processe tudo sem necessidade;
- acople capability a provider/modelo;
- misture extração e inferência;
- esconda proveniência;
- exija montagem manual de contexto;
- acrescente complexidade sem ganho operacional.

## 17. Próxima ação

1. Integrar esta revisão documental com ADR + SPEC PR-03.
2. Somente após merge documental, abrir branch de implementação PR-03.
3. Fazer preflight contra a `main` então corrente.
4. Implementar um vertical slice de `document.extract_text`.
5. Validar texto nativo, OCR, fallback VLM, revisão, reutilização, falha e Case isolation.
6. Confirmar ganho operacional antes de ampliar para PR-04.
