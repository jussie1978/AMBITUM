# SPEC-AMBITUM-PR02 — Smart Metadata

**Versão:** 1.0  
**Data:** 28/09/2026  
**Estado:** READY PARA IMPLEMENTAÇÃO  
**Projeto:** CIRCE AMBITUM  
**Unidade:** PR-02 — Smart Metadata  
**Autoridade arquitetural:** `ADR-AMBITUM-PR02-001-FUNDACAO-SMART-METADATA-v1.0-2026-09-28.md`  
**Baseline remota:** `origin/main` em `273adb4f7ac28a869234e11e1d163685d18cfdb9`  
**Pré-requisito:** PR-01 Audit & Freeze aprovado

---

## 1. Objetivo

Permitir que o operador enriqueça opcionalmente documentos do Pool com metadata estruturado, individualmente ou em lote, sem:

- alterar o arquivo original;
- exigir classificação durante Intake;
- criar Bloco;
- criar Produto/Seção;
- executar OCR;
- depender do Workspace como proprietário do dado.

O resultado deve preparar o Pool para filtros estruturados e para Retrieval futuro.

---

## 2. Resultado demonstrável

Em um Caso com documentos existentes:

```text
abrir Caso
→ selecionar 3 documentos no Pool
→ aplicar target "Alvo A"
→ aplicar topic "financeiro"
→ adicionar tag "PIX"
→ recarregar página
→ metadata permanece
→ filtrar Pool por target/topic/tag
→ somente documentos correspondentes permanecem visíveis
```

Também demonstrar:

```text
documento de outro Caso em batch
→ requisição inteira rejeitada
→ nenhuma gravação parcial
```

E:

```text
arquivo sem metadata
→ continua perfeitamente válido no Pool
```

---

## 3. Escopo

### Incluído

- modelo persistente de Smart Metadata para `SharedDocument`;
- kinds iniciais;
- proveniência;
- CRUD mínimo necessário para batch;
- leitura por Caso;
- auditoria;
- isolamento entre Casos;
- aplicação em lote;
- filtros no Pool;
- desacoplamento da seleção do Pool;
- bridge de compatibilidade para criação legada de Bloco;
- migration aditiva;
- testes de domínio/HTTP/UI estrutural.

### Fora de escopo

- OCR;
- extração automática;
- LLM;
- sugestões automáticas reais;
- embeddings;
- Retrieval;
- Smart Bins inferidos;
- reconciliação automática de pessoas;
- criação de `Asset` genérico;
- edição de Produto/Seções;
- UX-03B;
- Inspector Vivo;
- Composer novo;
- Knowledge Base;
- geração de relatório;
- exportação;
- classificação obrigatória no Intake.

---

## 4. Modelo persistente

Nova entidade proposta:

```text
AssetSmartMetadata
```

Tabela sugerida:

```text
asset_smart_metadata
```

Campos:

| Campo | Regra |
|---|---|
| `id` | PK inteira |
| `shared_case_id` | FK `shared_cases.id`, obrigatório, indexado |
| `shared_document_id` | FK `shared_documents.id`, obrigatório, indexado |
| `kind` | string curta, allowlist |
| `value_text` | valor textual normalizado, obrigatório |
| `linked_person_id` | FK opcional para `shared_persons.id` |
| `provenance` | enum lógico controlado |
| `created_by_operator_id` | opcional conforme sessão existente |
| `created_by_username` | obrigatório |
| `created_at` | UTC |
| `updated_at` | UTC |

### 4.1 Kinds

Allowlist inicial:

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

### 4.2 Proveniência

Allowlist:

```text
human_confirmed
ai_suggested
system_derived
```

No PR-02, o endpoint humano grava `human_confirmed`.

### 4.3 Duplicidade

Para o primeiro corte, o mesmo documento não deve acumular duplicata exata de:

```text
kind + normalized value_text + linked_person_id
```

Reaplicar a mesma metadata em batch deve ser idempotente no efeito observável: não criar linhas repetidas.

### 4.4 Exclusão

O operador deve poder retirar um valor de metadata sem excluir o documento.

A exclusão do metadata é auditada.

Não implementar exclusão definitiva de documento.

---

## 5. Integridade de Caso

Toda mutação deve confirmar:

```text
case_ref
→ SharedCase.id
→ SharedDocument.shared_case_id == case.id
```

Se `linked_person_id` for informado:

```text
SharedPerson.shared_case_id == case.id
```

Qualquer ID externo:

```text
→ rejeitar batch inteiro
→ zero alteração parcial
```

Não revelar conteúdo de outro Caso na mensagem pública.

---

## 6. Serviço

Novo serviço:

```text
app/services/smart_metadata_service.py
```

Responsabilidades:

- normalização;
- allowlists;
- resolução do Caso;
- validação dos documentos;
- validação opcional de pessoa;
- aplicação batch;
- remoção;
- listagem por Caso/documento;
- serialização;
- transação atômica;
- preservação de proveniência.

O serviço não chama:

- storage;
- OCR;
- LLM;
- Produto/Seções;
- Blocos.

---

## 7. HTTP

Novo router:

```text
app/routes/smart_metadata.py
```

Prefixo:

```text
/api/cases/{case_ref}/smart-metadata
```

### 7.1 GET

```text
GET /api/cases/{case_ref}/smart-metadata
```

Retorna metadata do Caso, agrupável por `shared_document_id`.

Filtros opcionais podem incluir:

```text
document_id
kind
```

Não implementar mecanismo de consulta complexo neste PR.

### 7.2 Batch PUT

```text
PUT /api/cases/{case_ref}/smart-metadata/batch
```

Payload conceitual:

```json
{
  "document_ids": [10, 11, 12],
  "operation": "add",
  "kind": "topic",
  "value": "financeiro",
  "linked_person_id": null
}
```

Operações mínimas:

```text
add
remove
```

O servidor define:

```text
provenance = human_confirmed
```

### 7.3 Respostas

- `200` — batch aplicado;
- `404` — Caso inexistente;
- `422` — payload/kind/IDs inválidos;
- `500` — erro público genérico.

Se a autenticação existente redireciona para login sem sessão, preservar esse contrato; não alterar AuthGuard global.

---

## 8. Auditoria

Eventos sugeridos:

```text
smart_metadata_batch_added
smart_metadata_batch_removed
```

Registrar, sem despejar dados excessivos:

- operador;
- Caso;
- documentos afetados;
- kind;
- valor;
- target/person quando aplicável;
- quantidade;
- timestamp.

Não registrar conteúdo de arquivo original.

A mutação e o evento de sucesso devem confirmar na mesma transação.

Falha da auditoria de sucesso deve reverter a mutação.

---

## 9. Migration

Nova revisão:

```text
0011_pr02_smart_metadata
```

Com:

```text
down_revision = "0010_ux03a_product_sections"
```

A migration:

- cria apenas a estrutura nova e índices/restrições necessários;
- não altera `shared_documents`;
- não altera Produto/Seções;
- não altera tabelas de Blocos;
- não altera storage;
- não preenche metadata fictício;
- não promove histórico automaticamente;
- não cria conteúdo AI_SUGGESTED/SYSTEM_DERIVED.

Validar:

1. banco novo pela cadeia Alembic;
2. fixture em `0010` com Caso/Workspace/documentos/Produto-Seções existentes;
3. segundo `upgrade head`;
4. downgrade/upgrade somente em banco descartável.

---

## 10. UX do Pool

### 10.1 Seleção genérica

Hoje os checkboxes do Pool estão ligados ao `create-block-form`.

PR-02 deve transformar a seleção em estado genérico de Pool.

Invariante:

```text
selecionar material ≠ criar Bloco
```

### 10.2 Bridge legado

A criação existente de Bloco continua funcionando.

No submit do formulário legado:

```text
seleção genérica do Pool
→ gerar hidden inputs sources
→ submeter create-block-form
```

Nenhum código novo de Smart Metadata chama endpoint de Bloco.

### 10.3 Batch UI

Com seleção ativa, expor ação de metadata.

Primeiro corte pode usar painel/popover compacto contendo:

- tipo;
- valor;
- target existente opcional;
- aplicar;
- remover quando aplicável.

Não criar Smart Bin nem editor complexo.

### 10.4 Filtros

Adicionar filtros determinísticos do Pool para:

- target;
- topic;
- tag.

`section_hint` pode ser exibido/aplicado, mas não precisa virar filtro de destaque se isso ampliar demais a UI.

Os filtros devem operar sobre dados reais devolvidos pelo servidor.

---

## 11. Reutilização de SharedPerson

Para `kind=target`:

### Pessoa existente

```text
linked_person_id = ID
value_text = nome/label
```

### Label livre

```text
linked_person_id = null
value_text = texto informado
```

O sistema não cria `SharedPerson` implicitamente.

Reconciliar label livre com pessoa canônica é futuro.

---

## 12. Normalização

Regras mínimas:

- `kind`: lowercase e allowlist;
- `value_text`: trim; não vazio;
- limite de `value_text`: 256 caracteres no primeiro corte;
- tags/topics/section hints não devem ser truncados silenciosamente;
- IDs: inteiros positivos;
- `document_ids`: únicos, lote limitado.

Limite inicial sugerido:

```text
até 100 documentos por batch
```

Esse limite deve ser centralizado no serviço.

---

## 13. Arquivos previstos

| Caminho | Ação |
|---|---|
| `app/models/smart_metadata.py` | novo |
| `app/services/smart_metadata_service.py` | novo |
| `app/routes/smart_metadata.py` | novo |
| `alembic/versions/0011_pr02_smart_metadata.py` | novo |
| `scripts/smoke_smart_metadata_service.py` | novo |
| `scripts/smoke_smart_metadata_http.py` | novo |
| `scripts/smoke_workspace_smart_metadata.py` | novo |
| `run.py` | registro mínimo do router/modelo |
| `alembic/env.py` | import do modelo |
| `app/routes/workspace.py` | exposição mínima da metadata para render do Pool |
| `app/templates/workspace.html` | seleção genérica, batch e filtros |

Ampliação além desses caminhos deve ser justificada antes de editar.

---

## 14. Arquivos proibidos na PR-02

Não alterar por conveniência:

```text
app/services/document_intake_service.py
app/services/storage_service.py
app/routes/documents.py
app/models/workspace_product.py
app/services/workspace_product_service.py
app/routes/workspace_products.py
alembic/versions/0009_at06b_curated_intake_storage.py
alembic/versions/0010_ux03a_product_sections.py
```

Não recuperar arquivos da branch UX-03B arquivada.

---

## 15. Critérios de aceitação

### Domínio

- [ ] Documento sem metadata continua válido.
- [ ] Metadata pertence a documento do Caso correto.
- [ ] Target pode apontar para `SharedPerson` do mesmo Caso.
- [ ] Label de target pode existir sem `SharedPerson`.
- [ ] Duplicata exata não gera linha repetida.
- [ ] Remover metadata não altera documento.
- [ ] Proveniência humana é atribuída no servidor.

### Isolamento

- [ ] Documento externo ao Caso rejeita batch integral.
- [ ] Pessoa externa ao Caso rejeita batch integral.
- [ ] Nenhuma gravação parcial em batch inválido.

### Auditoria

- [ ] Add é auditado.
- [ ] Remove é auditado.
- [ ] Falha de auditoria reverte mutação.
- [ ] Dados sensíveis do original não são copiados para logs.

### UX

- [ ] Pool permite seleção genérica.
- [ ] Batch metadata funciona para múltiplos documentos.
- [ ] Filtro target funciona.
- [ ] Filtro topic funciona.
- [ ] Filtro tag funciona.
- [ ] criação legada de Bloco continua funcional via bridge.
- [ ] Intake continua funcionando.
- [ ] Original continua governado.
- [ ] reload preserva metadata.

### Migration

- [ ] cadeia `0009 → 0010 → 0011` válida;
- [ ] banco novo migra;
- [ ] fixture `0010` migra sem perda;
- [ ] segundo upgrade não duplica;
- [ ] migrations antigas permanecem inalteradas.

---

## 16. Bateria proporcional

Executar obrigatoriamente:

```text
scripts.smoke_smart_metadata_service
scripts.smoke_smart_metadata_http
scripts.smoke_workspace_smart_metadata
scripts.smoke_workspace_pool_inventory
scripts.smoke_workspace_pool_intake
scripts.smoke_at06b_curated_document_http
scripts.smoke_at06b_curated_document_intake
scripts.smoke_at06b_curated_storage
WORKSPACE JINJA PARSE
git diff --check
```

Executar smoke de migration novo com bancos descartáveis.

Não repetir a bateria completa de UX-03A apenas por rotina se Produto/Seções não forem alterados.

---

## 17. Stop-loss

Parar e reportar antes de ampliar escopo se a implementação exigir:

- mudança no contrato de Intake;
- mudança em `SharedDocument` apenas para acomodar metadata;
- reativação de UX-03B;
- dependência de Blocos/Produto/Seções;
- nova abstração `Asset`;
- OCR;
- embeddings;
- refatoração global do `workspace.html`;
- alteração de AuthGuard;
- nova infraestrutura externa.

---

## 18. Gate de execução local

Antes de editar:

```powershell
Set-Location "C:\Projetos\AMBITUM"

git status --short --branch
git remote -v
git branch --show-current
git fetch origin
git rev-parse origin/main
git log -5 --oneline --decorate origin/main
```

Esperado remotamente:

```text
origin/main = 273adb4f7ac28a869234e11e1d163685d18cfdb9
```

Se o clone local possuir trabalho posterior, não sobrescrever nem resetar automaticamente.

A branch de implementação deve nascer da `origin/main` confirmada, em unidade única coerente para PR-02.

---

## 19. Prompt executável para Codex

```text
PROJETO: CIRCE AMBITUM
UNIDADE: PR-02 — Smart Metadata
REPOSITÓRIO: jussie1978/AMBITUM
FONTE DA VERDADE: origin/main
BASELINE REMOTA AUDITADA: 273adb4f7ac28a869234e11e1d163685d18cfdb9

Leia:
- ADR-AMBITUM-PR-001 Product Reset
- AUDIT-AMBITUM-PR01-MATRIZ-FREEZE
- ADR-AMBITUM-PR02-001
- SPEC-AMBITUM-PR02-SMART-METADATA
- Project Master corrente
- Implementation Master corrente

Primeiro execute gate read-only local e verifique AGENTS.md aplicáveis.
Não sobrescreva trabalho local e não troque de branch silenciosamente.

Implemente somente PR-02.

Regras:
- Smart Metadata pertence ao Caso e ao SharedDocument.
- Não criar Asset genérico.
- Não tocar Intake/Storage/Original.
- Não retomar UX-03B.
- Não implementar OCR.
- Não depender de InvestigativeBlock, WorkspaceProduct ou ProductSection.
- Preserve a cadeia Alembic e crie 0011 após 0010.
- Torne a seleção do Pool genérica e preserve criação legada de Bloco por bridge.
- Proveniência de ações humanas é definida no servidor como human_confirmed.
- Batch é atômico e isolado por Caso.
- Reutilize SharedPerson opcionalmente para target sem torná-lo obrigatório.
- Use testes proporcionais ao patch; não execute verificações redundantes sem motivo.

Antes de stage/commit:
- apresente diff stat;
- caminhos alterados;
- resultados reais dos testes;
- riscos;
- status Git.
Pare para revisão antes de commit/push se surgir qualquer necessidade fora da SPEC.
```
