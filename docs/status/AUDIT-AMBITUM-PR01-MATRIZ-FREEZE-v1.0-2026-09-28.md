# AUDIT-AMBITUM-PR01 — Matriz de Audit & Freeze

**Versão:** 1.0  
**Data:** 28/09/2026  
**Projeto:** CIRCE AMBITUM  
**Unidade:** PR-01 — Audit & Freeze  
**Estado:** APROVADA / ENCERRÁVEL  
**Natureza:** auditoria arquitetural read-only / classificação de preservação  
**Repositório canônico:** `jussie1978/AMBITUM`  
**Fonte da verdade:** `origin/main`  
**HEAD remoto auditado:** `273adb4f7ac28a869234e11e1d163685d18cfdb9`  
**Baseline funcional anterior:** `80bf959d95fbd6e9a5028958cafdb9941715c297`  
**Product Reset:** aprovado em 28/09/2026  
**UX-03B legado:** congelado e preservado em `archive/ux03b-pre-product-reset-2026-09-28`  
**Commit de arquivo UX-03B:** `40ff8dada415dc871eae27f1a6adf060dd00c5e4`

---

## 1. Objetivo

Auditar o estado real do repositório após o Product Reset e declarar, antes de qualquer nova implementação, quais superfícies devem ser:

- **MANTER**
- **REUTILIZAR**
- **CONGELAR**
- **ENCAPSULAR**
- **NÃO TOCAR**

A auditoria também deve impedir que Produto/Seções, Blocos ou o UX-03B arquivado se tornem dependência implícita do novo MVP Pool-first.

---

## 2. Regra de execução desta unidade

PR-01 é uma unidade de auditoria e congelamento.

Não autoriza:

- retomada da UX-03B;
- implementação de OCR;
- implementação antecipada de Retrieval;
- reescrita do Intake;
- remodelagem ampla do Workspace;
- remoção de Produto/Seções;
- remoção de Blocos;
- reescrita de migrations históricas.

Nenhum patch funcional é necessário para fechar esta unidade.

---

## 3. Gate read-only confirmado

### 3.1 Repositório remoto

```text
REPOSITÓRIO: jussie1978/AMBITUM
DEFAULT BRANCH: main
FONTE DA VERDADE: origin/main
HEAD REMOTO: 273adb4f7ac28a869234e11e1d163685d18cfdb9
```

Os commits posteriores à baseline funcional `80bf959` são documentais:

```text
e4c12595d3d5cf125c7015fcc087b4b635b56c4b
docs(ambitum): establish product reset and canonical roadmap

273adb4f7ac28a869234e11e1d163685d18cfdb9
docs(ambitum): normalize markdown whitespace
```

Comparação `80bf959...main`:

```text
ahead_by: 2
behind_by: 0
mudanças funcionais: nenhuma
mudanças: seis documentos do Product Reset
```

### 3.2 Branch de arquivo UX-03B

Branch confirmada:

```text
archive/ux03b-pre-product-reset-2026-09-28
```

Commit de arquivo:

```text
40ff8dada415dc871eae27f1a6adf060dd00c5e4
archive(ux03b): preserve pre-product-reset work in progress
```

Comparação com `main`:

```text
status: diverged
merge-base: 80bf959d95fbd6e9a5028958cafdb9941715c297
archive ahead: 1 commit
archive behind: 2 commits documentais
```

Arquivos exclusivos do trabalho UX-03B arquivado:

```text
app/templates/partials/workspace_product_desk.html
app/templates/partials/workspace_product_desk_script.html
app/templates/partials/workspace_product_desk_styles.html
app/templates/workspace.html
scripts/seed_ux03b_demo.py
scripts/smoke_workspace_pool_intake.py
scripts/smoke_workspace_product_desk.py
scripts/smoke_workspace_shell.py
scripts/test_workspace_product_desk_state.mjs
```

**Decisão:** não cherry-pickar, não mesclar e não retomar essa branch como continuação automática.

---

## 4. Achado arquitetural central

O backend de Intake/Storage está suficientemente separado do fluxo antigo e continua adequado à direção Pool-first.

O acoplamento relevante está principalmente na UI atual do Pool:

```text
Pool selection
→ checkboxes com form="create-block-form"
→ criação de InvestigativeBlock
```

Portanto, a nova funcionalidade de Smart Metadata não deve nascer dependente da física de Blocos.

A correção proporcional é **encapsular a seleção do Pool**, tornando-a estado genérico da interface. O fluxo legado de Blocos passa a consumir essa seleção por um bridge compatível.

Direção:

```text
POOL SELECTION
├── Smart Metadata
└── bridge legado → create-block-form
```

Não é necessária feature flag para congelar Produto/Seções ou UX-03B, pois a UI corrente de `main` não consome `WorkspaceProduct`/`ProductSection`.

---

## 5. Matriz MANTER / REUTILIZAR / CONGELAR / ENCAPSULAR / NÃO TOCAR

| Classificação | Superfície | Decisão |
|---|---|---|
| MANTER | `SharedCase` / Caso | Unidade investigativa canônica. |
| MANTER | `SharedDocument` + Original | Primeiro asset físico do vertical slice. |
| MANTER | Intake canônico | Contrato validado e compatível com Pool-first. |
| MANTER | `CaseMaterials` / `load_case_materials()` | Visão read-only canônica e independente do Workspace. |
| MANTER | Pool UX-02 | Inventário, busca, filtros, Intake e feedback perceptível. |
| MANTER | Shell/painéis UX-01 | Planta visual reutilizável. |
| MANTER | auditoria | Infraestrutura transversal para mutações de metadata. |
| MANTER | autenticação | Sem necessidade demonstrada de mudança. |
| REUTILIZAR | `SharedPerson` | Pode representar target estruturado quando existente. Cadastro não é obrigatório. |
| REUTILIZAR | filtros/busca do Pool | Base da filtragem por target/topic/tag. |
| REUTILIZAR | seleção múltipla visual do Pool | Física útil para batch, desde que desacoplada de Blocos. |
| REUTILIZAR | `audit_service` | Registrar mutações humanas de Smart Metadata. |
| REUTILIZAR | `run.py` e Alembic | Somente registros mínimos do novo domínio. |
| CONGELAR | `InvestigativeBlock` | Preservar; não usar como dependência do MVP. |
| CONGELAR | `InvestigativeBlockSource` | Preservar histórico e funcionalidade existente. |
| CONGELAR | operações de Bloco em `workspace_service.py` | Legado funcional, fora do caminho crítico novo. |
| CONGELAR | `WorkspaceProduct` | Fundação disponível, não workflow obrigatório. |
| CONGELAR | `ProductSection` | Não usar como pedágio de geração. |
| CONGELAR | `ProductSectionBlock` | Não expandir no PR-02. |
| CONGELAR | `workspace_product_service.py` | Não ampliar. |
| CONGELAR | `workspace_products.py` | Não ampliar. |
| CONGELAR | Mesa baseada em Blocos | Não evoluir no PR-02. |
| CONGELAR | Inspector/Composer no desenho anterior | Estrutura visual pode permanecer; significado antigo não guia o MVP. |
| CONGELAR | branch `archive/ux03b-pre-product-reset-2026-09-28` | Registro histórico; sem merge/cherry-pick. |
| ENCAPSULAR | Pool selection ↔ `create-block-form` | Principal desacoplamento exigido para PR-02. |
| ENCAPSULAR | `workspace.html` monolítico | Alterar somente superfície necessária do Pool. |
| ENCAPSULAR | `/api/workspaces/.../blocks` | Preservar compatibilidade sem torná-la dependência nova. |
| NÃO TOCAR | `document_intake_service.py` | PR-02 não altera ingestão física. |
| NÃO TOCAR | `storage_service.py` | Metadata não conhece path físico nem bytes. |
| NÃO TOCAR | `routes/documents.py` Intake/Original | Contrato congelado. |
| NÃO TOCAR | migration `0009_at06b_curated_intake_storage` | História Alembic imutável. |
| NÃO TOCAR | migration `0010_ux03a_product_sections` | Continua na cadeia mesmo com Produto/Seções congelados. |
| NÃO TOCAR | AuthGuard/configuração global | Sem dependência do PR-02. |

---

## 6. Dependências que o novo MVP não pode adquirir

PR-02 e unidades posteriores não podem exigir:

```text
Smart Metadata → InvestigativeBlock
Smart Metadata → ProductSection
OCR → InvestigativeBlock
Retrieval → ProductSection
Report Generator → montagem manual obrigatória de Blocos
```

Dependências aceitáveis:

```text
Smart Metadata → Caso
Smart Metadata → SharedDocument
Smart Metadata → SharedPerson opcional
Smart Metadata → auditoria

OCR → SharedDocument
Retrieval → material do Caso + derivados
Report Generator → retrieval + KB + preset
```

---

## 7. Resultado da auditoria

```text
PR-01 — AUDIT & FREEZE
DECISÃO: APROVADA
PATCH FUNCIONAL: NÃO NECESSÁRIO
```

A arquitetura existente permite iniciar Smart Metadata sem:

- apagar legado;
- reescrever Intake;
- retomar UX-03B;
- introduzir feature flag artificial;
- migrar Produto/Seções para o novo fluxo;
- criar uma entidade genérica `Asset` antes de necessidade real.

---

## 8. Critério de entrada da PR-02

PR-02 pode iniciar somente se:

1. partir de `origin/main`;
2. preservar Intake/Original/Storage;
3. manter UX-03B apenas no arquivo;
4. criar Smart Metadata no domínio do Caso;
5. usar `SharedDocument` como primeiro asset físico;
6. não exigir Bloco ou Seção;
7. encapsular seleção do Pool antes de reutilizá-la em batch;
8. manter proveniência explícita;
9. não implementar OCR.

---

## 9. Referências remotas auditadas

- Product Reset: `https://github.com/jussie1978/AMBITUM/commit/e4c12595d3d5cf125c7015fcc087b4b635b56c4b`
- HEAD documental: `https://github.com/jussie1978/AMBITUM/commit/273adb4f7ac28a869234e11e1d163685d18cfdb9`
- Baseline funcional: `https://github.com/jussie1978/AMBITUM/commit/80bf959d95fbd6e9a5028958cafdb9941715c297`
- UX-03B arquivado: `https://github.com/jussie1978/AMBITUM/commit/40ff8dada415dc871eae27f1a6adf060dd00c5e4`

---

## 10. Limite desta evidência

A auditoria desta rodada confirmou o estado **remoto canônico** pelo GitHub. O estado de um clone local específico — branch local, working tree ou ahead/behind local — deve ser confirmado no gate inicial do executor antes de qualquer edição.

Não repetir regressões integrais apenas para retomar o trabalho se o conteúdo remoto auditado permanecer idêntico.
