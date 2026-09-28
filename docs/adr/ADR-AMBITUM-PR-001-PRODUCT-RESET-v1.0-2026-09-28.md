# ADR-AMBITUM-PR-001 — Product Reset: Pool-First, Knowledge-Grounded e Relatório Rastreável

**Versão:** 1.0  
**Data:** 28/09/2026  
**Status:** ACEITA  
**Projeto:** CIRCE AMBITUM  
**Substitui como direção de produto:** sequência UX-03B → UX-04 → UX-05 como prioridade automática  
**Preserva:** Intake/Storage canônico, Pool, Original, auditoria, autenticação, Design System e fundações técnicas já validadas

**Repositório canônico:** `https://github.com/jussie1978/AMBITUM`  
**Fonte da verdade:** `origin/main` do repositório canônico  
**Nome legado:** CIRCE-ATHENA, preservado apenas em histórico anterior a 28/09/2026

## 1. Contexto

O CIRCE AMBITUM, denominado **CIRCE-ATHENA até 28/09/2026**, evoluiu para um Workspace investigativo com Intake físico, Pool, painéis e uma fundação persistente de Produto/Seções. A pausa do projeto permitiu reavaliar a relação entre esforço operacional e valor entregue.

Foi identificado risco de arquitetura prematura: o fluxo baseado em Blocos → Seções → Espinha → Inspector → Composer acrescenta etapas ao trabalho do investigador antes de demonstrar que essas etapas reduzem esforço real.

A experiência acumulada no LexisPro demonstrou uma física de produto mais eficiente: uma Base de Conhecimento reutilizável orienta uma IA especializada, enquanto o usuário fornece o contexto do caso e revisa a peça gerada.

## 2. Problema

O objetivo do AMBITUM é reduzir atrito e tempo operacional. Um fluxo que exige ao investigador reconstruir manualmente seu raciocínio em entidades intermediárias pode aumentar o trabalho em vez de reduzi-lo.

O trabalho real já produz matéria-prima suficiente:

- documentos;
- PDFs;
- prints;
- imagens;
- extrações de sistemas;
- material de Cellebrite;
- conteúdo de redes sociais;
- observações humanas;
- planilhas;
- transcrições e outros artefatos.

O sistema deve consumir essa matéria-prima com o menor pedágio possível.

## 3. Decisão

O novo centro do produto passa a ser:

```text
CASO
  ↓
POOL DE EVIDÊNCIAS
  ↓
SMART METADATA / SMART BINS
  ↓
OCR + EXTRAÇÃO + INDEXAÇÃO
  ↓
RETRIEVAL DO CASO
  +
BASE DE CONHECIMENTO
  ↓
ASSISTENTE IA DO AMBITUM
  ↓
RELATÓRIO / PEÇA RASTREÁVEL
  ↓
REVISÃO HUMANA
```

A composição por Blocos/Seções deixa de ser workflow obrigatório.

Blocos e Produto/Seções já implementados permanecem preservados no código, mas ficam **congelados** até que um caso de uso real demonstre necessidade clara.

## 4. Princípios

1. **Pool-first:** o investigador trabalha principalmente alimentando e organizando o Pool.
2. **Baixo atrito:** nenhum metadado opcional pode impedir ingestão.
3. **Proveniência obrigatória:** toda afirmação gerada deve poder apontar para sua origem quando houver suporte documental.
4. **Conhecimento ≠ Evidência:** Base de Conhecimento orienta forma, método e referência; não se mistura silenciosamente ao material factual do Caso.
5. **IA como assistente:** OCR, entidades, tags e relações automáticas entram como sugestões revisáveis.
6. **Human override:** operador pode corrigir, rejeitar, complementar ou ignorar qualquer sugestão.
7. **Original soberano:** derivados não substituem o arquivo original.
8. **Vertical slice antes de expansão:** provar o fluxo completo antes de reativar módulos avançados.

## 5. Smart Metadata

Assets do Pool podem receber metadados opcionais e múltiplos:

- alvo/pessoa/organização;
- tema/assunto;
- seção ou tipo de produto sugerido;
- evento/data;
- relevância;
- origem;
- status de validação;
- tags livres;
- relações estruturadas futuras.

Deve existir distinção explícita entre:

```text
HUMAN_CONFIRMED
AI_SUGGESTED
SYSTEM_DERIVED
```

Nenhuma sugestão automática equivale a confirmação humana.

## 6. Base de Conhecimento

A Base de Conhecimento contém material reutilizável entre Casos:

- modelos de relatórios;
- padrões de redação;
- presets;
- instruções institucionais autorizadas;
- glossários;
- referências procedimentais;
- exemplos aprovados;
- orientações de estilo/estrutura.

O Pool contém material específico do Caso.

Esses dois domínios não devem compartilhar namespace, retenção ou significado sem contrato explícito.

## 7. Geração

A geração de produto combina:

```text
contexto do Caso
+ filtros estruturados do Smart Metadata
+ recuperação semântica no Pool
+ Base de Conhecimento selecionada
+ preset de produto
+ instrução do operador
```

A saída deve manter ligação entre trechos do produto e assets/fontes utilizadas sempre que tecnicamente possível.

## 8. Consequências

### Mantido
- Caso/Workspace;
- Intake físico;
- storage governado;
- SHA-256;
- Original;
- Pool;
- auditoria;
- autenticação;
- UI de painéis;
- Design System.

### Congelado
- UX-03B como continuação automática;
- uso obrigatório de Blocos;
- Produto/Seções como pedágio de geração;
- Inspector Vivo;
- Composer no desenho anterior;
- ontologia analítica extensa;
- Smart Bins complexos;
- colaboração/versionamento;
- exportação sofisticada.

### Reavaliado
Produto/Seções pode voltar como estrutura interna da peça ou ferramenta opcional, mas somente após prova de necessidade.

## 9. Critério de sucesso

O novo caminho é aprovado quando um operador consegue:

1. criar/abrir Caso;
2. inserir material real com baixo esforço;
3. enriquecer opcionalmente assets com Smart Metadata;
4. executar OCR/indexação;
5. consultar o acervo;
6. selecionar preset/Base de Conhecimento;
7. gerar uma minuta útil;
8. rastrear o texto de volta às fontes;
9. revisar e corrigir;
10. gastar menos esforço do que no método manual.

## 10. Critério de rejeição

Rejeitar ou reduzir escopo se:

- ingestão exigir classificação excessiva;
- geração depender de montagem manual de blocos;
- rastreabilidade não puder ser apresentada de modo compreensível;
- OCR exigir correção manual comparável à digitação original;
- RAG gerar respostas sem fonte identificável;
- construção do produto exigir mais esforço que Word/processo atual;
- Base de Conhecimento contaminar o fato investigativo;
- IA transformar sugestão em dado confirmado.

## 11. Decisão final

**APROVADO — REDIRECIONAR O PRODUTO.**

O próximo desenvolvimento não é UX-03B. O próximo desenvolvimento é o MVP vertical definido em `SPEC-AMBITUM-MVP-01-RELATORIO-RASTREAVEL`.
