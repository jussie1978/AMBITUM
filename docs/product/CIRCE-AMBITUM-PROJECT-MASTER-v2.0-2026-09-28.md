# CIRCE AMBITUM — PROJECT MASTER

**Versão:** 2.0
**Data:** 28/09/2026
**Status:** PRODUCT RESET APROVADO
**Substitui:** Project Master v1.4 como autoridade corrente de produto
**Preserva como histórico:** roadmap e decisões anteriores não conflitantes

**Nome canônico:** CIRCE AMBITUM
**Nome legado:** CIRCE-ATHENA (até 28/09/2026)
**Repositório canônico:** `https://github.com/jussie1978/AMBITUM`
**Fonte da verdade:** `origin/main`; clones locais devem encerrar cada unidade sincronizados com o remoto.

## 1. Identidade

CIRCE AMBITUM é uma ferramenta investigativa assistida destinada a transformar material bruto de um Caso em informação consultável e produtos policiais rastreáveis, reduzindo trabalho mecânico sem retirar do operador autoria, julgamento ou controle.

## 2. Proposta de valor

> **O investigador investiga normalmente, deposita e organiza o material relevante, e o AMBITUM faz o trabalho mecânico de leitura, recuperação, síntese e redação assistida.**

O usuário não deve reconstruir manualmente a investigação para que a IA consiga trabalhar.

## 3. Física do produto

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

A geração também consulta uma Base de Conhecimento separada.

## 4. Domínios

### Caso
Unidade investigativa.

### Pool
Acervo operacional do Caso. Não é storage paralelo.

### Asset
Material original ou derivado associado ao Caso.

### Smart Metadata
Contexto estruturado opcional aplicado ao asset.

### Base de Conhecimento
Conhecimento reutilizável e não factual do Caso.

### Assistente IA
Camada de assistência, recuperação contextual e geração fundamentada do AMBITUM.

### Produto
Saída produzida: relatório, síntese ou peça. Sua estrutura interna não deve impor trabalho intermediário desnecessário.

## 5. Princípios

- local por padrão;
- original soberano;
- proveniência;
- controle humano;
- baixo atrito;
- IA assistiva;
- fatos do Caso separados de conhecimento de referência;
- sugestões automáticas não equivalem a confirmação;
- geração ancorada em fontes;
- arquitetura proporcional à prova de valor.

## 6. Contratos preservados

Continuam vigentes:

- Intake no Caso;
- SHA-256;
- storage opaco;
- deduplicação no Caso;
- recuperação governada do Original;
- auditoria;
- autenticação;
- Pool real;
- Design System;
- painéis validados.

## 7. Estado do legado recente

### Validado e reutilizável
- UX-01 Shell/Painéis;
- UX-02 Pool/Intake;
- backend AT-06B;
- UX-03A como fundação técnica disponível.

### Congelado
- UX-03B;
- Produto/Seções como workflow obrigatório;
- Blocos como pedágio;
- UX-04;
- UX-05;
- ontologia analítica extensa.

Nada é removido por este documento.

## 8. Smart Metadata

Uso principal:

- organizar;
- filtrar;
- orientar retrieval;
- aumentar precisão da geração.

Metadados podem representar alvo, tema, evento, seção sugerida, origem, relevância e estado.

O operador deve conseguir aplicar metadados em lote.

## 9. OCR

OCR é capacidade central do novo produto.

Deve servir a dois fins:

1. transformar documento/imagem em conteúdo pesquisável;
2. sugerir dados estruturados para preenchimento/revisão.

OCR não altera nem substitui o original.

## 10. Base de Conhecimento

A Base de Conhecimento serve para ensinar o assistente IA do AMBITUM a produzir.

Exemplos:

- estrutura de relatório;
- estilo;
- modelos;
- presets;
- orientações;
- exemplos aprovados.

Ela não deve funcionar como evidência do Caso.

## 11. Relatórios

A primeira meta é gerar uma minuta útil com baixa intervenção.

O produto deve permitir navegar da redação até as fontes utilizadas.

O operador continua responsável por revisão e aprovação.

## 12. Métrica de produto

Avaliar:

- tempo total até minuta;
- ações manuais;
- volume de digitação evitada;
- percentual de texto aproveitável;
- número de correções;
- cobertura de citações;
- erros de OCR;
- confiança do operador;
- tempo comparado ao método atual.

## 13. Critério macro de sucesso

O AMBITUM é bem-sucedido se reduzir de modo perceptível o esforço de transformar material investigativo em produto utilizável, preservando rastreabilidade e controle humano.

## 14. Critério macro de falha

Falha se:

- adicionar burocracia;
- exigir classificação excessiva;
- gerar texto sem fonte;
- exigir reconstrução manual da investigação;
- ocultar diferenças entre sugestão e confirmação;
- misturar conhecimento de referência com evidência;
- economizar pouco tempo diante da complexidade criada.

## 15. Roadmap corrente

A autoridade de sequência passa a ser:

`ROADMAP-AMBITUM-POST-RESET-v1.0-2026-09-28.md`.

A próxima unidade é `PR-01 — Audit & Freeze`.
