# ADR-AMBITUM-PR02-001 — Fundação mínima de Smart Metadata

**Versão:** 1.0  
**Data:** 28/09/2026  
**Status:** ACEITA  
**Projeto:** CIRCE AMBITUM  
**Unidade:** PR-02 — Smart Metadata  
**Origem:** Product Reset + PR-01 Audit & Freeze  
**Baseline de decisão:** `origin/main` em `273adb4f7ac28a869234e11e1d163685d18cfdb9`

---

## 1. Contexto

O Product Reset tornou o Pool o centro operacional do AMBITUM e retirou Blocos/Produto/Seções do workflow obrigatório.

A PR-01 confirmou que:

- Intake/Storage/Original são independentes e reutilizáveis;
- `CaseMaterials` é visão canônica do Caso;
- `SharedDocument` já representa adequadamente o primeiro tipo de asset físico do MVP;
- `SharedPerson` pode ser reutilizado opcionalmente como target estruturado;
- seleção múltipla existe visualmente, porém está acoplada ao `create-block-form`;
- Produto/Seções permanecem no backend mas não são consumidos pela UI corrente;
- nenhuma entidade genérica `Asset` existe ou é necessária para o primeiro corte.

---

## 2. Decisão

### 2.1 Não criar entidade genérica `Asset` na PR-02

O primeiro vertical slice de Smart Metadata será aplicado a `SharedDocument`.

Razões:

- PDFs, screenshots, PNG/JPEG, TXT, CSV, DOCX e XLSX já ingressam como `SharedDocument`;
- criar `Asset` agora adicionaria camada de abstração sem segundo consumidor concreto;
- o domínio pode ser generalizado posteriormente quando surgir outro tipo real de asset com os mesmos requisitos.

### 2.2 Smart Metadata pertence ao Caso

A API e o serviço devem validar a cadeia:

```text
Caso
→ SharedDocument
→ Smart Metadata
```

O Workspace pode expor a UX, mas não é o proprietário do metadado.

### 2.3 Modelo extensível, não tabela por tipo

Usar uma estrutura única de entradas de metadata.

Contrato conceitual:

```text
AssetSmartMetadata
├── id
├── shared_case_id
├── shared_document_id
├── kind
├── value_text
├── linked_person_id         nullable
├── provenance
├── created_by_operator_id
├── created_by_username
├── created_at
└── updated_at
```

Não criar tabelas separadas para tag, topic, target ou section hint no primeiro corte.

### 2.4 Proveniência é atributo do registro

Valores aceitos:

```text
human_confirmed
ai_suggested
system_derived
```

Na PR-02, mutações originadas pela UI humana são registradas como `human_confirmed` pelo servidor.

O cliente não recebe autoridade para declarar arbitrariamente uma alteração humana como `ai_suggested` ou `system_derived`.

### 2.5 Target pode reutilizar SharedPerson sem obrigatoriedade

Quando houver pessoa canônica no Caso:

```text
kind = target
linked_person_id = <SharedPerson.id>
value_text = label legível
```

Quando não houver cadastro:

```text
kind = target
linked_person_id = null
value_text = label livre
```

O operador não é obrigado a cadastrar uma pessoa antes de enriquecer um documento.

### 2.6 Seleção do Pool torna-se genérica

Os checkboxes do Pool deixam de pertencer semanticamente ao formulário de Bloco.

A seleção passa a representar apenas:

```text
selected material(s) in Pool
```

Consumidores:

```text
Smart Metadata batch
legacy block bridge
```

A compatibilidade com criação de Bloco é mantida por bridge no submit, sem fazer Smart Metadata depender de Blocos.

---

## 3. Kinds iniciais

Permitir inicialmente:

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

O desenho deve aceitar extensão futura sem migration para cada novo `kind`, mas não deve aceitar strings arbitrárias sem allowlist controlada pelo serviço.

---

## 4. API

Prefixo de domínio:

```text
/api/cases/{case_ref}/smart-metadata
```

Contrato inicial mínimo:

```text
GET /api/cases/{case_ref}/smart-metadata
PUT /api/cases/{case_ref}/smart-metadata/batch
```

O endpoint batch recebe múltiplos `shared_document_id` do mesmo Caso e uma operação de metadata validada.

IDs externos ao Caso devem rejeitar a operação inteira.

---

## 5. Alembic

A nova migration deve continuar a cadeia existente:

```text
0009_at06b_curated_intake_storage
→ 0010_ux03a_product_sections
→ 0011_pr02_smart_metadata
```

O congelamento de Produto/Seções não autoriza bifurcar ou reescrever a história de migration.

---

## 6. Consequências

### Positivas

- preserva baixo atrito;
- evita dependência de Blocos/Seções;
- permite batch real no Pool;
- mantém metadata separado do original;
- prepara filtros estruturados para Retrieval;
- preserva possibilidade de generalização futura.

### Custos aceitos

- `SharedDocument` funciona temporariamente como primeiro asset concreto;
- um target pode existir apenas como label até ser reconciliado com `SharedPerson`;
- a UI precisa de pequeno desacoplamento da seleção atual.

### Não resolvido nesta ADR

- OCR;
- extração de entidades;
- algoritmo de sugestão;
- embeddings;
- Smart Bins;
- reconciliação sofisticada de entidades;
- versionamento completo de metadata;
- KB;
- geração de relatório.

---

## 7. Critério para generalizar `Asset`

Criar abstração genérica somente quando houver pelo menos um segundo tipo de material real que:

1. não seja `SharedDocument`;
2. precise do mesmo contrato de metadata;
3. torne a duplicação concreta pior que a abstração.

Até lá, não antecipar a camada.

---

## 8. Rejeição

Refatorar se PR-02:

- exigir Bloco ou Produto/Seção;
- alterar bytes ou storage do original;
- exigir metadata para Intake;
- permitir metadata de documento de outro Caso;
- aceitar proveniência arbitrária do cliente;
- criar uma tabela por tipo de tag;
- introduzir OCR;
- criar entidade `Asset` sem consumidor adicional real.
