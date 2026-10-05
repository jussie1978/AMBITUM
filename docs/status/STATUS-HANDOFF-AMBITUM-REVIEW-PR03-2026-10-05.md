# STATUS / HANDOFF — AMBITUM REVIEW-PR03

**Data:** 05/10/2026
**Unidade:** REVIEW-PR03 — Capability / Derived Content / Document Text Extraction
**Estado:** REVIEW CONCLUÍDA / DECISÕES APROVADAS / SEM IMPLEMENTAÇÃO
**Próxima unidade:** PR-03 — Derived Content Foundation + Document Text Extraction

## 1. Snapshot de partida

Estado observado após merge da documentação de fechamento da PR-02:

```text
ROOT: C:\Projetos\CIRCE_ATHENA
REMOTE: https://github.com/jussie1978/AMBITUM.git
BRANCH: main
UPSTREAM: origin/main
HEAD abreviado: 315418e
LOCAL == REMOTO: sim
WORKING TREE: limpa
```

PR #2 integrou a atualização documental que marcou PR-02 como DONE e colocou PR-03 em revisão.

Este handoff registra a revisão subsequente.

## 2. Problema revisado

Escopo anterior:

> OCR + Derived Text

Risco identificado:

- começar pela tecnologia;
- criar workflow OCR próprio;
- exigir configuração técnica do policial;
- duplicar posteriormente transcrição/frames/outros derivados;
- acoplar IA a engine/provider;
- transformar uma ferramenta interna em burocracia de produto.

Pergunta adotada:

> **O policial precisa perceber OCR como uma feature ou apenas precisa obter texto rastreável do material?**

Decisão: OCR é meio possível; a capability é o contrato de produto.

## 3. Decisões aprovadas

### D1 — Capability Harness

Adotar arquitetura governada:

```text
Caller
  ↓
Intent / Explicit Action
  ↓
Context
  ↓
Capability
  ↓
Policy
  ↓
Executor
  ↓
Result + Provenance
  ↓
Review
```

Capability pertence ao AMBITUM.

### D2 — primeira capability

```text
document.extract_text
```

### D3 — executores

Estratégias previstas:

```text
native
ocr
vlm
```

Executor é detalhe interno e substituível.

### D4 — política híbrida

- preferir texto nativo;
- OCR local quando necessário;
- VLM local diante de falha objetiva;
- casos ambíguos favorecem **Melhorar extração** sob decisão humana;
- não usar VLM em todo documento por padrão.

### D5 — processamento

Sob demanda primeiro.

Não OCR automático de todo Intake.

### D6 — persistência

Texto derivado é persistente e reutilizável.

Deve permanecer ligado ao original.

### D7 — granularidade

Página é source anchor obrigatório na PR-03.

Bounding box é opcional.

### D8 — revisão humana

Preservar:

```text
raw_text
reviewed_text opcional
```

Correção humana não sobrescreve silenciosamente a saída bruta.

### D9 — separação epistemológica

Extração e interpretação permanecem distintas.

OCR/VLM de extração não autoriza sumarização, inferência ou conclusão factual.

### D10 — UI

Não criar central OCR.

Fluxo mínimo:

```text
documento → Obter texto → estado → páginas → original/revisão
```

### D11 — independência da Mesa

PR-03 deve funcionar sem a futura interface conversacional.

PR-06 reutilizará a mesma capability.

### D12 — NEXUS

NEXUS pode futuramente ser ferramenta especializada do Capability Harness.

Integração NEXUS não pertence à PR-03.

## 4. Mudança de roadmap

Nome anterior:

```text
PR-03 — OCR + Derived Text
```

Nome aprovado:

```text
PR-03 — Derived Content Foundation + Document Text Extraction
```

A revisão deixa de ser blocker conceitual.

Após integração desta documentação, PR-03 pode entrar em implementação.

## 5. Documentos deste pacote

Criar:

```text
docs/adr/
ADR-AMBITUM-PR03-001-CAPABILITY-HARNESS-v1.0-2026-10-05.md

docs/specs/
SPEC-AMBITUM-PR03-DERIVED-CONTENT-DOCUMENT-TEXT-EXTRACTION-v1.0-2026-10-05.md
```

Substituir por novas revisões, preservando históricos:

```text
docs/product/
CIRCE-AMBITUM-PROJECT-MASTER-v2.4-2026-10-05.md

docs/product/
ROADMAP-AMBITUM-POST-RESET-v1.4-2026-10-05.md

docs/specs/
SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.4-2026-10-05.md
```

Adicionar:

```text
docs/status/
STATUS-HANDOFF-AMBITUM-REVIEW-PR03-2026-10-05.md
```

Não apagar versões anteriores.

## 6. Implementação não realizada

Nesta unidade não foram executados:

- mudanças em backend;
- migrations;
- OCR;
- VLM;
- UI funcional;
- testes técnicos de PR-03;
- RAG;
- Knowledge Base;
- Mesa;
- NEXUS;
- áudio/vídeo;
- relatório/DOCX.

Nenhuma dessas capacidades deve ser descrita como implementada.

## 7. Próximo gate

Antes de código:

1. integrar este pacote documental por PR;
2. voltar para `main`;
3. confirmar sync e working tree;
4. criar branch de implementação específica;
5. inspecionar modelos/migrations/services atuais;
6. definir persistência física mínima;
7. selecionar executores locais proporcionais;
8. implementar vertical slice sem ampliar escopo.

Sugestão de branch futura:

```text
feat/pr03-derived-content-text-extraction
```

A criação da branch só deve ocorrer após merge documental e preflight.

## 8. Critério central de aceite da PR-03

> **O policial consegue obter texto utilizável e rastreável de um documento do Caso sem saber nem precisar decidir como ele foi obtido.**

Se a implementação exigir um workflow técnico de OCR, a unidade deve ser revista antes do merge.
