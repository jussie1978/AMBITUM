# CIRCE AMBITUM — PROJECT MASTER

**Versão:** 2.3
**Data:** 05/10/2026
**Status:** PRODUCT RESET ATIVO / PR-02 DONE / PR-03 EM REVISÃO DE PRODUTO
**Substitui:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.2-2026-09-30.md`
**Repositório canônico:** `jussie1978/AMBITUM`
**Baseline integrada:** `origin/main` em `78a49128c65473421894611fcf09999fff34ee8a`
**Merge PR-02:** PR #1 — `Merge pull request #1 from jussie1978/feat/pr02-smart-metadata`
**Commit funcional final da PR-02:** `26fdb76ae12dceb76e23626d7348da104b4c4200`

## 1. Identidade e valor

AMBITUM transforma material bruto de um Caso em informação consultável e produtos policiais rastreáveis, reduzindo trabalho mecânico e preservando autoria, julgamento e controle do investigador.

A direção do produto permanece **context-first e low-friction**: o operador não deve reconstruir manualmente contexto, copiar dados entre telas ou alimentar estruturas intermediárias apenas para permitir que a IA trabalhe.

O valor central buscado é permitir que o policial expresse **a tarefa que precisa realizar**, enquanto o sistema combina contexto do Caso, ferramentas adequadas, dados autorizados, proveniência e controles humanos para executar ou assistir essa tarefa.

Exemplos de intenção operacional que devem orientar as próximas revisões:

- “transcreva este áudio”;
- “extraia os frames deste trecho do vídeo”;
- “preencha este formulário com os dados já existentes no Caso”;
- “localize neste material as referências a determinada pessoa/telefone/veículo”;
- “compare estes documentos”;
- “prepare este conteúdo no formato exigido, mantendo as fontes”.

Esses exemplos são direção de produto, não capacidades declaradas como já implementadas.

## 2. Estado integrado comprovado

| Elemento | Estado |
|---|---|
| Intake, Storage, Original, auditoria, autenticação, Pool e shell | Preservados |
| Fundação Smart Metadata | Integrada |
| Quick Metadata, chips, batch e Smart Bins Lite | Integrados |
| PR-02 | **DONE** |
| Branch integrada | `feat/pr02-smart-metadata` |
| Commit final da feature | `26fdb76` |
| Merge em `main` | `78a4912` |
| `main == origin/main` | Confirmado em 05/10/2026 |
| Working tree | Limpa no gate de 05/10/2026 |
| PR-03 | Próxima unidade, **antes em revisão de produto** |

A documentação v2.2 registrava PR-02 como FINALIZING. Esse estado foi superado pela evidência real do Git e por esta versão.

## 3. Arquitetura alvo — direção, não camisa de força

A cadeia estratégica continua válida como referência:

`Caso → Pool → metadata/organização → extração/derivados → retrieval → IA contextual → produto revisável → exportação`

A ordem e os nomes das PRs futuras podem ser refinados quando uma etapa estiver transformando o trabalho em burocracia em vez de reduzi-lo.

A arquitetura não deve obrigar o operador a entender ou manipular internamente conceitos técnicos como OCR, embeddings, chunks, índices, jobs ou pipelines para realizar tarefas normais.

## 4. Princípios e contratos preservados

- local por padrão;
- original soberano;
- proveniência e rastreabilidade;
- controle humano;
- baixo atrito;
- IA assistiva;
- geração ancorada;
- arquitetura proporcional;
- vertical slice antes de expansão;
- Intake canônico;
- SHA-256 e deduplicação por Caso;
- storage opaco;
- Original governado;
- auditoria;
- autenticação;
- isolamento entre Casos;
- Design System.

### 4.1. Princípio de produto para revisão das próximas unidades

Antes de implementar uma nova funcionalidade, perguntar:

> **O operador precisa aprender um workflow novo para alimentar a IA, ou pode simplesmente pedir o resultado que precisa e deixar o sistema usar contexto e ferramentas de forma governada?**

Quando a segunda opção for tecnicamente segura, rastreável e mais simples, ela é preferível.

Isso não implica interface exclusivamente conversacional. Ferramentas visuais especializadas continuam apropriadas quando ajudam a inspecionar, comparar, selecionar, revisar ou corrigir resultados.

## 5. Smart Metadata e Smart Bins Lite

Metadata pertence ao Caso e ao `SharedDocument`. Modelo, migration 0011, service/API, proveniência definida no servidor, batch atômico e target opcional via `SharedPerson` permanecem válidos.

Quick Metadata expõe ações de baixo atrito e Smart Bins Lite apresenta agrupamentos determinísticos derivados de metadata real. Não são inferência automática nem classificação obrigatória.

A ação legada “Usar no bloco” foi removida da direção operacional. InvestigativeBlock não condiciona retrieval, geração, relatório ou uso futuro da IA.

## 6. Superfícies de produto

| Superfície | Responsabilidade esperada |
|---|---|
| Pool | materiais do Caso, Intake, organização, filtros, seleção e contexto visual |
| Mesa/IA | expressão de intenção, comandos, diálogo, compose e orquestração de capacidades |
| Inspector/resultado | inspeção e revisão de artefatos/resultados |
| Relatório Vivo | composição e revisão de produto final quando aplicável |
| Ferramentas especializadas | visualizações adequadas a tarefas como grafo, timeline, mídia, tabelas e formulários |

A conversa deve funcionar como **porta de entrada e camada de orquestração**, não como substituta obrigatória de toda interface especializada.

## 7. Capability / Tool Harness — hipótese a formalizar

Para a revisão da PR-03 e das etapas posteriores, adotar como hipótese de trabalho um **capability harness**: camada que permite à IA identificar a intenção do operador e invocar ferramentas com contratos explícitos.

Um harness aceitável deve combinar:

`intenção → contexto autorizado → ferramenta → parâmetros → execução → resultado → proveniência → revisão humana`

Não equivale a autonomia irrestrita. Operações destrutivas, sensíveis ou irreversíveis continuam exigindo controles e confirmações compatíveis com o risco.

Essa hipótese será discutida e, se aprovada, formalizada em ADR própria antes de alterar substancialmente roadmap/arquitetura.

## 8. Evidence Retrieval e Knowledge Retrieval

Continuam domínios distintos.

- **Evidence Retrieval:** material factual do Caso ativo, com source refs e isolamento.
- **Knowledge Retrieval:** método, estrutura, estilo, referência técnica e templates autorizados.

Knowledge Base não é evidência do Caso. Um documento da KB que passe a ser evidência deve ingressar pelo Intake do Caso.

## 9. Legado

`InvestigativeBlock` / `InvestigativeBlockSource` permanecem **FROZEN LEGACY CAPABILITY**.

Preservar sem expansão e sem requisito para RAG, relatório, geração ou execução de ferramentas. UX-03B, Produto/Seções e Inspector/Composer antigos não são direção obrigatória.

## 10. Roadmap corrente

| ID | Unidade | Estado | Critério macro |
|---|---|---|---|
| PR-00 | Product Reset | DONE | Direção Pool-first formalizada |
| PR-01 | Audit & Freeze | DONE | Contratos preservados e legado congelado |
| PR-02 | Smart Metadata + Smart Bins Lite | **DONE** | Merge PR #1 em `main`, baseline `78a4912` |
| PR-03 | OCR + Derived Text | **REVIEW NEXT** | Revisar necessidade, UX e posição no capability harness antes de implementar |
| PR-04 | Evidence Retrieval | PLANNED / REVIEW REQUIRED | Revisar sob a mesma filosofia antes da implementação |
| PR-05 | KB + Knowledge Retrieval | PLANNED / REVIEW REQUIRED | Preservar separação factual e reduzir burocracia |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED / REVIEW REQUIRED | Orquestrar contexto e capacidades; não exigir Blocos |
| PR-07 | Live Report + Presets | PLANNED / REVIEW REQUIRED | Produto revisável, rastreável e de baixo atrito |
| PR-08 | DOCX + Vertical End-to-End Demo | PLANNED | Export fiel e prova vertical |
| PR-09 | Operational Pilot | PLANNED | Medir ganho real |
| PR-10 | Product Decision | PLANNED | Expandir/refatorar/reduzir/substituir/arquivar |

## 11. Critério de sucesso e rejeição

Medir:

- tempo até resultado útil;
- ações manuais;
- copy/paste evitado;
- digitação evitada;
- texto/resultado aproveitável;
- correções necessárias;
- rastreabilidade;
- erros;
- confiança e controle do operador.

Rejeitar ou simplificar direção que:

- acrescente burocracia;
- exija montagem manual de contexto;
- imponha classificação sem necessidade operacional;
- transforme ferramenta técnica em workflow obrigatório;
- esconda proveniência;
- produza fatos sem suporte;
- exija mais trabalho do que o método atual;
- acrescente complexidade sem ganho mensurável.

## 12. Próxima ação

1. Tratar este fechamento documental da PR-02 como sincronização do estado real.
2. Não implementar PR-03 imediatamente.
3. Abrir **revisão de produto/arquitetura da PR-03**.
4. Pergunta central da revisão: OCR/Derived Text deve aparecer ao operador como workflow próprio ou funcionar principalmente como capacidade invocável e reutilizável pelo sistema?
5. Depois da PR-03, revisar PR-04 a PR-07 com o mesmo teste de atrito antes de codificar.
