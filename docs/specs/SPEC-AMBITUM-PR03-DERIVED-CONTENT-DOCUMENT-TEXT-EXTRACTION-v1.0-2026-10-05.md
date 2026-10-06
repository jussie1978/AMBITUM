# SPEC-AMBITUM-PR03 — Derived Content Foundation + Document Text Extraction

**Versão:** 1.0
**Data:** 06/10/2026
**Estado:** DONE / TECHNICAL AND OPERATIONAL VALIDATION COMPLETE
**Projeto:** CIRCE AMBITUM
**Unidade:** PR-03
**Autoridade arquitetural:** `ADR-AMBITUM-PR03-001-CAPABILITY-HARNESS-v1.0-2026-10-05.md`
**Pré-requisito:** PR-02 DONE
**Baseline de fechamento:** branch `feat/pr03-derived-content-text-extraction`, commit abreviado `e29a5d7`
**Substitui conceitualmente:** escopo anterior “OCR + Derived Text” do roadmap v1.3

---

## 1. Objetivo

Permitir que o operador obtenha **texto utilizável e rastreável** de um documento do Caso sem precisar conhecer ou configurar o mecanismo técnico usado.

A capability canônica é:

```text
document.extract_text
```

O AMBITUM deve escolher a estratégia adequada entre extração nativa, OCR local e VLM local de fallback, preservando original, proveniência, isolamento e revisão humana.

---

## 2. Resultado demonstrável

Cenário mínimo:

1. abrir/selecionar um documento pertencente ao Caso;
2. acionar **Obter texto**;
3. o AMBITUM resolve a fonte dentro do Caso;
4. escolhe uma estratégia válida;
5. processa sem alterar o original;
6. apresenta o texto organizado por página;
7. informa estado e proveniência;
8. permite correção humana sem sobrescrever o bruto;
9. nova solicitação reutiliza o derivado válido quando apropriado.

O operador não precisa escolher OCR, modelo, DPI, parser ou provider.

---

## 3. Princípios normativos

- original é soberano;
- texto derivado não substitui o original;
- extração e interpretação são operações diferentes;
- bruto e revisão humana permanecem distinguíveis;
- página é a unidade mínima canônica de origem nesta PR;
- processamento é sob demanda;
- execução local é padrão nesta PR;
- falhas são explícitas;
- nenhuma confidence transforma saída em fato confirmado;
- caller usa IDs governados, nunca paths arbitrários;
- uma capability deve funcionar por UI direta antes da futura Mesa;
- o design deve permitir futura invocação pela IA sem acoplamento ao modelo.

---

## 4. Escopo incluído

### 4.1. Capability

Implementar contrato interno equivalente a:

```text
document.extract_text(document_id, options?)
```

O servidor resolve:

- Caso;
- documento;
- original;
- permissões;
- estratégia/executor;
- persistência;
- proveniência.

`case_id` pode existir no contexto de rota/sessão, mas a implementação deve validar que o documento pertence ao Caso autorizado.

### 4.2. Estratégias de extração

A implementação deve suportar a arquitetura:

```text
A. texto nativo
B. OCR local
C. VLM local fallback
```

Não é obrigatório expor essas estratégias ao operador como opções primárias.

### 4.3. Texto nativo

Quando PDF/documento possuir camada textual utilizável, preferir extração determinística nativa.

Não executar OCR/VLM sem necessidade quando o texto nativo satisfizer a capability.

Implementação concluída com pypdf, examinando o texto nativo por página e preservando erro técnico real do parser como erro, sem mascará-lo como documento escaneado.

### 4.4. OCR local

Quando não houver texto nativo utilizável, executar OCR local adequado ao tipo de documento suportado.

A implementação concluída usa RapidOCR local com ONNX Runtime. O executor:

- permanece encapsulado;
- não altera o contrato da capability;
- expõe falha de modo observável;
- registra engine/versão quando disponível.

### 4.5. VLM local fallback

VLM local pode atuar como fallback para extração visual.

Fallback automático é permitido apenas diante de condição objetiva, como:

- inexistência de texto nativo;
- OCR com erro explícito;
- saída vazia após processamento;
- condição determinística equivalente documentada e testada.

Quando o resultado for apenas ambíguo/insatisfatório, sem falha objetiva, o sistema deve preferir oferecer ação equivalente a **Melhorar extração**, em vez de consumir VLM automaticamente.

Solicitação explícita do operador também pode autorizar o fallback.

O fallback implementado usa o contrato local OpenAI-compatible do servidor llama.cpp, configurado para `Qwen/Qwen3-VL-8B-Instruct-GGUF:Q4_K_M`. Nenhum conteúdo é enviado a cloud, OpenAI ou Ollama.

A execução contra o modelo Qwen3-VL real permanece pendente de validação operacional quando servidor e modelo estiverem instalados. O routing e o contrato possuem smoke determinístico com servidor HTTP fake.

---

## 5. Derived Document Text

A PR-03 deve persistir um resultado derivado governado.

Modelo lógico mínimo:

```text
DerivedDocumentText
  id
  case_id
  source_document_id
  capability
  status
  source_fingerprint
  extraction_profile
  pages[]
  provenance
  created_at
```

Os nomes físicos podem seguir os padrões existentes do repositório; o contrato semântico é obrigatório.

### 5.1. Página

Cada página deve conseguir representar:

```text
page_number
raw_text
reviewed_text?
executor_type
engine?
engine_version?
status
error_code?
error_detail?
fallback_candidate?
```

Regras:

- `raw_text` é resultado do executor e não é sobrescrito por correção humana;
- `reviewed_text` é opcional;
- ausência de revisão não invalida `raw_text`;
- revisão não significa validação factual do conteúdo;
- auditoria existente deve registrar mutações humanas quando aplicável.

### 5.2. Source anchor

Nesta PR, o anchor obrigatório é:

```text
source_document_id + page_number
```

Bounding box/região é opcional e não é gate de conclusão.

Áudio/timestamps e vídeo/frame-time não serão implementados nesta PR.

### 5.3. Fingerprint

O derivado deve estar ligado ao fingerprint/identidade canônica do original, preferencialmente usando o SHA-256 já preservado pelo domínio de Intake/Storage.

Isso permite saber se um resultado continua associado ao mesmo material soberano.

---

## 6. Proveniência

Cada execução persistida deve conseguir registrar, quando aplicável:

```text
capability
executor_type
engine
engine_version
relevant_parameters
source_fingerprint
created_at
```

`executor_type` deve distinguir ao menos:

```text
native
ocr
vlm
```

Quando páginas de uma mesma extração usam executores diferentes, a extração pai registra `mixed`; a proveniência real permanece em cada página.

A implementação pode armazenar detalhes adicionais sem expô-los como configuração obrigatória ao operador.

---

## 7. Estados

Estados mínimos:

```text
processing
ready
failed
```

`reviewed` não será usado como substituto de `ready`.

A revisão humana pode ser representada por metadados próprios, sem sugerir validação factual.

Falha deve:

- preservar o original;
- registrar razão útil;
- não deixar resultado `ready` incompleto;
- permitir nova tentativa controlada.

---

## 8. Reutilização e reprocessamento

Ao solicitar novamente a mesma capability para o mesmo original:

- derivado `ready` compatível pode ser reutilizado;
- processamento caro não deve ser repetido sem necessidade;
- usuário ou sistema pode solicitar reprocessamento quando houver motivo;
- reprocessamento não deve sobrescrever silenciosamente o bruto anterior se houver necessidade de preservar a execução anterior.

A implementação mínima pode manter uma execução corrente e histórico proporcional, desde que não destrua proveniência necessária.

Não construir sistema completo de versionamento de artifacts nesta PR.

---

## 9. Separação entre extração e interpretação

`document.extract_text` deve buscar fidelidade ao conteúdo observável.

Não faz parte da capability:

- resumir;
- inferir intenção;
- decidir se alguém mente;
- extrair entidades semanticamente como fatos;
- classificar relevância investigativa;
- responder perguntas sobre o conteúdo;
- transformar texto em narrativa conclusiva.

Essas operações pertencem a capabilities futuras.

Um VLM usado como executor de extração continua sujeito ao contrato de extração e sua origem deve permanecer explícita.

---

## 10. Interface mínima

A PR-03 não cria “módulo OCR”.

Superfície mínima esperada:

```text
documento
  ↓
[Obter texto]
  ↓
estado de processamento
  ↓
texto por página
  ↓
[Abrir original] [Revisar]
  ↓
[Melhorar extração] quando aplicável
```

A interface deve permitir perceber:

- qual documento está sendo processado;
- estado;
- texto resultante;
- página;
- estratégia/proveniência em detalhe acessível, sem poluir o fluxo principal;
- falha, se houver.

Não exigir seleção manual de engine.

A API e a UI mínima foram entregues com obtenção/consulta, resultado por página, indicação de origem, acesso ao Original e revisão humana auditada. Essa UI é somente uma superfície funcional provisória; o novo shell de produto pertence ao ciclo posterior **AMBITUM PRODUCT SHELL V1**.

---

## 11. Segurança e isolamento

Obrigatório:

- preservar isolamento entre Casos;
- resolver documento por identificador autorizado;
- impedir acesso por path físico arbitrário;
- não enviar material para provider externo nesta PR;
- não alterar o arquivo original;
- respeitar autenticação e auditoria existentes;
- rejeitar document_id fora do Caso ativo;
- evitar logs com conteúdo sensível desnecessário.

---

## 12. Persistência e migration

A implementação criou migrations aditivas para suportar Derived Document Text:

- `0014_pr03_document_text` — extrações e páginas;
- `0015_pr03_page_provenance` — proveniência individual por página e executor pai `mixed`.

A migration deve:

- preservar migrations existentes;
- não alterar conteúdo de arquivos originais;
- não remover estruturas legadas;
- permitir rollback técnico conforme padrões do projeto;
- manter Case isolation explícito.

A definição física final deve ser revista contra os modelos existentes antes do patch.

O banco operacional foi protegido por backup verificado, ensaiado em cópia isolada e migrado com sucesso até `0015_pr03_page_provenance`, preservando tabelas e contagens canônicas.

---

## 13. API/serviço

A UI não deve chamar diretamente engines.

Fluxo esperado:

```text
UI / future caller
  ↓
capability/service
  ↓
context + policy
  ↓
executor selection
  ↓
derived persistence
```

O contrato deve ser reutilizável pela futura Mesa/IA.

Nenhum endpoint deve aceitar caminho de arquivo fornecido pelo modelo/cliente como autoridade da fonte.

---

## 14. Qualidade e fallback

Esta PR não depende de um score universal de confidence.

A seleção automática de VLM deve usar falhas objetivas e reason codes determinísticos.

Casos subjetivos de baixa qualidade devem favorecer:

- visibilidade do resultado;
- ação de melhoria pelo operador;
- comparação com original.

Não criar falsa precisão numérica para decidir qualidade.

---

## 15. Testes mínimos

A implementação deve demonstrar, com material sintético ou autorizado:

### G1 — native text

PDF com camada textual:

- capability retorna texto;
- executor registrado como `native`;
- OCR/VLM não é acionado sem necessidade;
- página/origem preservada.

### G2 — OCR

Documento escaneado sem camada textual:

- OCR local é usado;
- resultado `ready`;
- páginas preservadas;
- original intacto.

### G3 — fallback

Condição objetiva de falha do OCR:

- fallback VLM local pode ser acionado;
- proveniência indica `vlm`;
- caller não muda de contrato.

### G4 — revisão

- `raw_text` permanece;
- correção humana cria/atualiza camada revisada;
- mutação é auditável;
- revisão não altera original.

### G5 — reutilização

Segunda solicitação compatível:

- reutiliza derivado `ready` quando aplicável;
- não repete processamento caro sem necessidade.

### G6 — falha

- erro resulta em `failed`;
- mensagem é observável;
- original e resultados válidos anteriores permanecem íntegros.

### G7 — isolamento

- documento de outro Caso não pode ser processado/acessado pelo contexto atual.

### G8 — UI curta

Operador consegue:

- selecionar/abrir documento;
- obter texto;
- ver páginas;
- abrir original;
- revisar ou melhorar quando aplicável;

sem configurar engine.

---

## 16. Critério de aceite de produto

PR-03 só é aceita como produto se demonstrar:

> **O policial consegue obter texto utilizável e rastreável de um documento do Caso sem saber nem precisar decidir como ele foi obtido.**

Além disso:

- texto aponta para documento/página;
- original continua soberano;
- processamento desnecessário é evitado;
- correções humanas não apagam a saída bruta;
- mais de uma estratégia pode satisfazer a mesma capability;
- a solução reduz passos em relação a um workflow OCR manual.

Teste técnico aprovado não substitui confirmação de ganho operacional.

Estado de fechamento: aceite técnico e operacional concluído para a superfície mínima da PR-03. Os smokes fundacional, native, OCR/mixed, VLM fallback, HTTP e UI passaram; o teste com Qwen3-VL real fica registrado como validação operacional futura.

---

## 17. Fora de escopo

Não implementar nesta PR:

- Evidence Retrieval/RAG;
- embeddings/vector DB;
- Knowledge Base;
- Mesa conversacional;
- voz;
- áudio/transcrição;
- vídeo/frames;
- NEXUS;
- preenchimento de formulário;
- extração semântica de entidades;
- sumarização;
- Live Report;
- DOCX;
- provider externo/cloud;
- OCR automático de todo Intake;
- framework universal de DerivedArtifact;
- refatoração integral do Workspace;
- remoção física de InvestigativeBlock/Produto/Seções.

---

## 18. Stop-loss

Parar e reavaliar antes de ampliar se a implementação começar a exigir:

- generalização para áudio/vídeo antes do vertical slice;
- configuração técnica obrigatória pelo policial;
- processamento automático de todo material sem evidência de benefício;
- acoplamento ao Qwen ou outro modelo específico;
- envio externo de evidência;
- novo workflow manual para preparar contexto;
- duplicação de capability entre UI e futura IA;
- interpretação semântica misturada ao texto extraído.

---

## 19. Próxima relação com o roadmap

Após PR-03:

- **AMBITUM PRODUCT SHELL V1** será o próximo ciclo, substituindo em unidade própria a superfície funcional provisória desta PR;
- PR-04 Evidence Retrieval poderá consumir Derived Document Text;
- PR-04 poderá solicitar `document.extract_text` quando necessário, sem implementar OCR dentro de retrieval;
- PR-06 Mesa/IA poderá invocar a mesma capability;
- futuras capabilities de áudio/vídeo testarão a necessidade real de generalizar Derived Content.

Nenhuma dessas etapas está implementada por esta SPEC.
