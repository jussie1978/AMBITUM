# SPEC-AMBITUM — IMPLEMENTATION MASTER v2.0

**Data:** 28/09/2026
**Status:** READY
**Direção:** Product Reset
**Próxima unidade:** PR-01 — Audit & Freeze
**Repositório canônico:** `https://github.com/jussie1978/AMBITUM`
**Regra de sincronização:** `origin/main` é a fonte da verdade; local e remoto devem terminar cada unidade em 0/0.

## 1. Objetivo de implementação

Redirecionar o projeto sem reescrita destrutiva, preservando o que foi validado e evitando que o fluxo antigo condicione o novo MVP.

## 2. Ordem

```text
PR-01 AUDIT/FREEZE
→ PR-02 SMART METADATA
→ PR-03 OCR
→ PR-04 RETRIEVAL
→ PR-05 KNOWLEDGE BASE
→ PR-06 PRESETS
→ PR-07 REPORT GENERATOR
→ PR-08 VERTICAL DEMO
```

## 3. Regra central

Nenhuma unidade deve antecipar a próxima.

Não construir:

- UI final da Base de Conhecimento durante Smart Metadata;
- gerador durante OCR;
- múltiplos providers durante Retrieval;
- DOCX/PDF durante a demo;
- ontologia completa antes do pilot.

## 4. PR-01 — Audit & Freeze

### Objetivo

Conhecer o estado real do repositório e declarar quais componentes:

```text
MANTER
REUTILIZAR
CONGELAR
ENCAPSULAR
NÃO TOCAR
CANDIDATO A REMOÇÃO FUTURA
```

### Sem mudanças funcionais amplas

Permitido:

- documentação;
- feature flags mínimas se estritamente necessárias;
- isolamento de dependência;
- testes de caracterização.

Não permitido:

- remover Produto/Seções;
- apagar migrations;
- reescrever Intake;
- refazer Workspace;
- iniciar OCR.

### Saída

Mapa arquitetural do código real + plano PR-02.

## 5. PR-02 — Smart Metadata

Preferir schema pequeno e extensível.

Não introduzir uma tabela por tipo de tag.

Primeiro desenho deve permitir:

- vínculos a entidades/alvos existentes ou labels simples;
- temas;
- tags;
- section hints;
- proveniência;
- operações em lote.

## 6. PR-03 — OCR

Separar:

```text
asset original
derived text
extraction candidate
confirmed structured value
```

Nunca sobrescrever campos canônicos diretamente a partir de OCR.

## 7. PR-04 — Retrieval

Camadas:

1. filtro estruturado;
2. full-text quando disponível;
3. embeddings;
4. reranking apenas se demonstrado necessário.

Não começar por pipeline sofisticado.

## 8. PR-05 — Knowledge Base

Criar domínio independente de Caso.

A KB precisa suportar:

- fonte;
- categoria;
- texto indexado;
- ativação/desativação;
- versão mínima;
- associação a preset.

Não duplicar o Pool.

## 9. PR-06 — Presets

Preset é configuração declarativa de produto, não código específico.

## 10. PR-07 — Gerador

Contrato inicial:

```text
GenerateReport(case_id, preset_id, user_instruction)
```

Internamente:

```text
resolve scope
→ retrieve case sources
→ retrieve KB
→ build grounded context
→ call model
→ persist draft
→ persist source map
```

## 11. Provider de IA

Criar adapter simples quando necessário.

Não construir framework multi-provider antes de haver dois providers reais.

## 12. Testes

Prioridade:

- isolamento entre Casos;
- proveniência;
- não mistura KB/evidência;
- OCR derivado;
- permissões;
- source map;
- falha segura;
- regressão de Intake.

Evitar verificar repetidamente baseline imutável sem causa.

## 13. Demo antes de polimento

A UI do MVP pode ser simples, mas deve ser utilizável.

O Design System vigente deve ser respeitado sem iniciar UX-06 completa antes da prova de valor.

## 14. Gate de expansão

Nenhum item do freezer retorna antes da Vertical Demo.

Exceção somente por dependência concreta comprovada.
