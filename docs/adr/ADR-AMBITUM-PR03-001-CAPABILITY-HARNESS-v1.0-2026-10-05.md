# ADR-AMBITUM-PR03-001 — Capability Harness Governado

**Versão:** 1.0
**Data:** 05/10/2026
**Status da decisão:** ACEITA / IMPLEMENTAÇÃO INCREMENTAL
**Projeto:** CIRCE AMBITUM
**Unidade de origem:** REVIEW-PR03
**Repositório:** `jussie1978/AMBITUM`
**Baseline observada:** `main` / `origin/main` no merge da PR #2, commit abreviado `315418e`
**Complementa:** `ADR-AMBITUM-PR-002-DUAL-RETRIEVAL-CONVERSATIONAL-WORKSPACE-v1.0-2026-09-30.md`
**Relacionada a:** `SPEC-AMBITUM-PR03-DERIVED-CONTENT-DOCUMENT-TEXT-EXTRACTION-v1.0-2026-10-05.md`

---

## 1. Contexto

O Product Reset consolidou a direção Pool-first e retirou estruturas intermediárias sem valor operacional do caminho obrigatório.

A revisão da PR-03 mostrou que tratar OCR como uma feature isolada induz o produto a começar pela tecnologia, e não pela intenção do policial. O operador normalmente precisa de resultados como:

- obter o texto de um documento;
- transcrever áudio;
- extrair frames de um trecho de vídeo;
- localizar uma informação em materiais do Caso;
- preencher um formulário a partir de dados já existentes;
- analisar relações/transações em ferramenta especializada.

OCR, ASR, VLM, parsers, mecanismos de busca e ferramentas como NEXUS são meios possíveis para satisfazer essas intenções, não necessariamente workflows que o operador deve aprender.

Ao mesmo tempo, delegar diretamente ao LLM a escolha e a execução irrestrita de ferramentas criaria acoplamento, baixa auditabilidade e risco operacional.

---

## 2. Problema

É necessário definir uma fronteira estável entre:

1. intenção do operador;
2. contexto autorizado do Caso;
3. capability solicitada;
4. política e permissões;
5. executor concreto;
6. resultado/artefato produzido;
7. proveniência;
8. revisão humana e próxima ação.

Essa fronteira deve funcionar tanto para chamadas explícitas da interface quanto, futuramente, para chamadas originadas na Mesa/IA.

---

## 3. Decisão

O AMBITUM adotará um **Capability Harness governado pelo produto**.

A capability pertence ao AMBITUM, não ao modelo de IA e não ao executor concreto.

Fluxo conceitual:

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

O `Caller` pode ser:

- ação explícita de UI;
- endpoint interno autorizado;
- serviço do próprio AMBITUM;
- futura Mesa/IA.

O restante do contrato deve permanecer o mesmo.

---

## 4. Capability versus executor

Capability representa **o que precisa ser realizado**.

Executor representa **como aquela capability é satisfeita nesta execução**.

Exemplo:

```text
capability:
  document.extract_text

executors possíveis:
  native_pdf
  local_ocr
  local_vlm
```

A seleção de executor pertence ao AMBITUM.

O caller não deve precisar conhecer biblioteca, modelo, provider, GPU, caminho físico de arquivo ou detalhes de implantação.

---

## 5. Independência de modelo

O LLM/VLM não é proprietário das tools.

Um modelo local, um modelo futuro ou uma interface tradicional podem solicitar a mesma capability.

Consequências:

- trocar o modelo de IA não exige reescrever ferramentas;
- trocar OCR/VLM não exige reescrever a camada de intenção;
- capacidades podem funcionar antes da Mesa conversacional;
- operações continuam governadas pelo AMBITUM;
- a arquitetura não depende de um provider específico.

Qwen ou qualquer outro modelo é candidato a executor/modelo em capacidades compatíveis, não dependência arquitetural desta ADR.

---

## 6. Política e contexto

A capability deve receber identificadores e contexto governados, não paths físicos arbitrários fornecidos por LLM.

O harness deve:

- resolver recursos dentro do Caso autorizado;
- preservar isolamento entre Casos;
- aplicar autenticação/autorização existentes;
- validar entradas e parâmetros;
- rejeitar referências fora do escopo permitido;
- registrar falhas de forma explícita;
- exigir confirmação proporcional para operações sensíveis, destrutivas ou irreversíveis.

Esta ADR não concede autonomia irrestrita ao modelo.

---

## 7. Resultados e proveniência

Capabilities podem produzir:

- resposta efêmera;
- dado estruturado;
- artefato derivado persistente;
- ação com efeito observável.

Quando houver artefato derivado persistente, ele deve manter vínculo rastreável com a fonte e com sua execução.

Proveniência mínima deve permitir responder, conforme a capability:

- qual material originou o resultado;
- qual capability foi executada;
- qual estratégia/executor foi usado;
- qual engine/modelo e versão, quando aplicável;
- quais parâmetros relevantes influenciaram o resultado;
- quando a execução ocorreu.

Resultado gerado/inferido não deve ser apresentado como fato confirmado apenas por existir no sistema.

---

## 8. Interface

O AMBITUM não será chat-only.

A conversa/Mesa é uma superfície futura de intenção e orquestração.

Superfícies especializadas permanecem apropriadas quando aumentam a qualidade de inspeção ou manipulação, por exemplo:

- documento + texto revisável;
- player + transcrição;
- timeline + frames;
- tabela;
- formulário;
- grafo NEXUS.

Uma mesma capability não deve ser duplicada em implementações paralelas por existir em mais de uma superfície.

---

## 9. Derived Content

Esta ADR reconhece **Derived Content** como classe conceitual de resultados persistentes gerados a partir de material soberano.

Não cria, neste momento, um framework universal de `DerivedArtifact`.

A PR-03 implementará apenas o mínimo necessário para texto derivado de documentos.

Áudio, vídeo, frames, tabelas e outros derivados futuros deverão testar quais propriedades são realmente comuns antes de generalizar o modelo persistente.

---

## 10. Primeira prova vertical

A primeira capability formal será:

```text
document.extract_text
```

Ela será implementada pela PR-03 revisada.

Estratégias previstas:

```text
documento
  ↓
texto nativo utilizável?
  ├─ sim → native extraction
  └─ não → OCR local
                ↓
         falha objetiva?
                ├─ não → resultado
                └─ sim → VLM local fallback

caso ambíguo:
  operador pode solicitar melhoria
```

A escolha final de bibliotecas/modelos pertence à implementação e não altera esta decisão arquitetural.

---

## 11. Alternativas consideradas

### 11.1. OCR como módulo independente

**Rejeitada como direção de produto.**

OCR continua necessário, mas não deve obrigar o operador a administrar um workflow técnico para obter texto.

### 11.2. Tool calling diretamente acoplado ao LLM

**Rejeitada.**

Acopla capabilities ao provider/modelo e enfraquece policy, validação e auditabilidade.

### 11.3. Framework universal de artifacts antes da primeira implementação

**Rejeitada neste momento.**

Generalização antecipada aumentaria arquitetura sem evidência suficiente.

### 11.4. Capability Harness incremental

**Aceita.**

Permite provar o contrato com `document.extract_text` e evoluir com evidência real.

---

## 12. Consequências positivas

- reduz trabalho mecânico do operador;
- separa intenção de implementação;
- preserva uso por UI direta antes da Mesa;
- permite reutilização por retrieval e capacidades futuras;
- reduz lock-in de modelos/providers;
- melhora rastreabilidade;
- favorece testes por contrato;
- permite especialização de interfaces sem duplicar execução.

---

## 13. Riscos

- transformar o harness em framework excessivamente genérico;
- adicionar abstrações antes de existir segunda necessidade concreta;
- esconder decisões relevantes do operador;
- acionar modelos caros sem necessidade;
- confundir extração com interpretação;
- persistir resultados sem vínculo suficiente com a fonte;
- usar confidence ou saída de VLM como verdade factual.

Mitigação: vertical slices pequenos, contratos explícitos, processamento proporcional, original soberano e revisão humana.

---

## 14. Fora de escopo desta ADR

Esta decisão não implementa:

- OCR;
- VLM;
- Mesa/IA;
- RAG;
- Knowledge Base;
- áudio/transcrição;
- vídeo/frames;
- NEXUS;
- formulário inteligente;
- relatório;
- DOCX;
- autorização de providers externos.

Esses itens exigem unidades próprias.

---

## 15. Critério de permanência da decisão

A arquitetura será considerada validada após a PR-03 demonstrar que:

1. uma UI direta invoca `document.extract_text`;
2. a capability resolve contexto sem receber path arbitrário;
3. mais de um executor pode satisfazer o contrato sem alterar o caller;
4. o resultado preserva proveniência;
5. o derivado pode ser reutilizado sem repetir processamento desnecessário;
6. o original permanece inalterado;
7. a solução reduz atrito em relação a um workflow OCR manual.

Se esses pontos não forem demonstráveis, a ADR deve ser revista antes de expandir o harness.
