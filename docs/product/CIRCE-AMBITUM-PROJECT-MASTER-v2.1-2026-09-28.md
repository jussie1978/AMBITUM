# CIRCE AMBITUM — PROJECT MASTER

**Versão:** 2.1  
**Data:** 28/09/2026  
**Status:** PRODUCT RESET ATIVO / PR-01 CONCLUÍDA / PR-02 READY  
**Substitui:** `CIRCE-AMBITUM-PROJECT-MASTER-v2.0-2026-09-28.md`  
**Repositório canônico:** `jussie1978/AMBITUM`  
**Fonte da verdade:** `origin/main`

---

## 1. Identidade

CIRCE AMBITUM é uma ferramenta investigativa assistida destinada a transformar material bruto de um Caso em informação consultável e produtos policiais rastreáveis, reduzindo trabalho mecânico sem retirar do operador autoria, julgamento ou controle.

---

## 2. Proposta de valor

> O investigador investiga normalmente, deposita e organiza o material relevante, e o AMBITUM executa o trabalho mecânico de leitura, recuperação, síntese e redação assistida.

O sistema não deve exigir reconstrução manual da investigação para que a IA consiga trabalhar.

---

## 3. Física corrente

```text
CASO
→ POOL
→ SMART METADATA
→ OCR / EXTRAÇÃO / INDEXAÇÃO
→ RETRIEVAL
→ ASSISTENTE IA
→ RELATÓRIO
→ REVISÃO HUMANA
```

A geração também consulta Base de Conhecimento separada do Caso.

Blocos e Produto/Seções não são workflow obrigatório.

---

## 4. Princípios

- local por padrão;
- original soberano;
- proveniência;
- controle humano;
- baixo atrito;
- IA assistiva;
- sugestão automática ≠ confirmação;
- fatos do Caso separados de conhecimento de referência;
- geração ancorada em fontes;
- arquitetura proporcional à prova de valor;
- vertical slice antes de expansão.

---

## 5. Contratos preservados

Continuam vigentes:

- Intake no Caso;
- SHA-256;
- storage opaco;
- deduplicação no Caso;
- Original governado;
- auditoria;
- autenticação;
- Pool real;
- Design System;
- shell/painéis validados.

---

## 6. Estado técnico pós PR-01

### Remoto canônico

```text
origin/main: 273adb4f7ac28a869234e11e1d163685d18cfdb9
baseline funcional: 80bf959d95fbd6e9a5028958cafdb9941715c297
```

As alterações após a baseline funcional são documentais.

### UX-03B legado

Preservado em:

```text
archive/ux03b-pre-product-reset-2026-09-28
40ff8dada415dc871eae27f1a6adf060dd00c5e4
```

Não retomar como continuidade.

---

## 7. Resultado PR-01

PR-01 concluiu:

- Intake/Storage/Original: manter;
- Pool: manter;
- seleção visual do Pool: reutilizar e desacoplar;
- Blocos: congelar;
- Produto/Seções: congelar;
- UX-03B: congelar;
- Intake/Storage/migrations históricas: não tocar;
- nenhum patch funcional de freeze necessário.

O principal acoplamento legado é:

```text
Pool selection → create-block-form
```

PR-02 deve convertê-lo em:

```text
Pool selection genérica
├── Smart Metadata
└── bridge legado → Blocos
```

---

## 8. Smart Metadata — direção aprovada

No primeiro corte:

- `SharedDocument` é o asset concreto;
- não criar `Asset` genérico;
- metadata pertence ao Caso;
- modelo extensível único;
- proveniência explícita;
- batch atômico;
- target pode reutilizar `SharedPerson` sem obrigatoriedade;
- filtros target/topic/tag entram no Pool;
- OCR permanece PR-03.

---

## 9. Roadmap corrente

| Unidade | Estado |
|---|---|
| PR-00 Product Reset | DONE |
| PR-01 Audit & Freeze | DONE |
| PR-02 Smart Metadata | READY |
| PR-03 OCR | PLANNED |
| PR-04 Retrieval | PLANNED |
| PR-05 Knowledge Base | PLANNED |
| PR-06 Presets | PLANNED |
| PR-07 Report Generator | PLANNED |
| PR-08 Vertical Demo | PLANNED |
| PR-09 Pilot | PLANNED |
| PR-10 Product Decision | PLANNED |

Autoridade detalhada:

```text
ROADMAP-AMBITUM-POST-RESET-v1.1-2026-09-28.md
```

---

## 10. Métricas de produto

Avaliar no vertical slice:

- tempo até minuta;
- ações manuais;
- digitação evitada;
- percentual de texto aproveitável;
- correções;
- cobertura de fontes;
- erros de OCR;
- confiança do operador;
- tempo comparado ao método atual.

---

## 11. Critério macro de sucesso

AMBITUM é bem-sucedido se reduzir de modo perceptível o esforço de transformar material investigativo em produto utilizável, preservando rastreabilidade e controle humano.

---

## 12. Critério macro de falha

Falha se:

- adicionar burocracia;
- exigir classificação excessiva;
- gerar texto sem fonte;
- exigir reconstrução manual da investigação;
- ocultar diferença entre sugestão e confirmação;
- misturar KB com evidência;
- economizar pouco tempo diante da complexidade criada.

---

## 13. Próxima unidade

```text
PR-02 — Smart Metadata
```

Contrato detalhado:

```text
ADR-AMBITUM-PR02-001-FUNDACAO-SMART-METADATA-v1.0-2026-09-28.md
SPEC-AMBITUM-PR02-SMART-METADATA-v1.0-2026-09-28.md
```

Primeira ação do executor: gate read-only local.

---

## 14. Autoridade documental corrente

```text
ADR-AMBITUM-PR-001
→ PROJECT MASTER v2.1
→ IMPLEMENTATION MASTER v2.1
→ ROADMAP v1.1
→ AUDIT PR-01
→ ADR PR02-001
→ SPEC PR-02
→ implementação/testes
→ STATUS/HANDOFF
```

Versões anteriores permanecem históricas quando conflitarem com esta versão.
