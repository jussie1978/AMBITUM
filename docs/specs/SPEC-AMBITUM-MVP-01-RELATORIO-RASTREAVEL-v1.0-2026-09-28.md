# SPEC-AMBITUM-MVP-01 — Pool Inteligente e Relatório Rastreável

**Versão:** 1.0
**Data:** 28/09/2026
**Estado:** READY
**Origem:** ADR-AMBITUM-PR-001
**Objetivo:** provar um fluxo vertical de baixo atrito do material bruto até uma minuta de relatório rastreável.

## 1. Pergunta de produto

> Um investigador consegue colocar material relevante em um Caso e obter uma minuta de relatório útil, fundamentada e rastreável, com esforço substancialmente menor que o processo manual?

## 2. Usuário

Investigador/analista responsável por reunir material, organizar evidências e produzir relatório ou peça de natureza investigativa.

## 3. Fluxo canônico do MVP

```text
ABRIR CASO
→ INSERIR MATERIAL NO POOL
→ OCR/EXTRAÇÃO QUANDO APLICÁVEL
→ REVISAR/SUGERIR SMART METADATA
→ INDEXAR
→ CONSULTAR
→ ESCOLHER PRESET
→ GERAR RELATÓRIO
→ VER FONTES
→ REVISAR
```

Nenhuma etapa exige criação manual de Bloco ou Seção.

## 4. Intake

Reutilizar o contrato canônico já validado.

Requisitos:

- original preservado;
- hash;
- storage governado;
- auditoria;
- duplicidade explícita;
- ingestão sem classificação obrigatória;
- feedback perceptível.

## 5. Smart Metadata

### 5.1 Metadados mínimos

```text
asset_id
case_id
targets[]
topics[]
section_hints[]
event_refs[]
tags[]
relevance
source_kind
validation_status
metadata_provenance
```

### 5.2 Proveniência

Cada atributo deve informar origem:

```text
human_confirmed
ai_suggested
system_derived
```

Metadado sugerido por IA não deve ser promovido automaticamente a confirmado.

### 5.3 Operação em lote

O operador deve poder selecionar múltiplos assets e aplicar:

- alvo;
- tema;
- tag;
- seção sugerida;
- status de revisão.

## 6. OCR e extração

Primeiro recorte:

- PDF textual;
- PDF rasterizado;
- PNG;
- JPEG/JPG;
- screenshots.

Saídas:

- texto extraído;
- páginas/frames de origem;
- campos candidatos;
- entidades candidatas;
- confiança técnica quando disponível.

OCR não altera o original.

Extração estruturada deve ser apresentada para revisão antes de alimentar campos canônicos.

## 7. Indexação e Retrieval

O sistema deve indexar:

- texto OCR;
- texto nativo;
- metadados;
- nome/tipo do asset;
- relações confirmadas.

Retrieval deve combinar:

```text
filtros estruturados
+ busca textual
+ busca semântica
```

Filtros humanos confirmados têm precedência sobre sugestões automáticas.

## 8. Base de Conhecimento

Domínio separado do Caso.

Itens podem conter:

- preset de relatório;
- instrução de estilo;
- estrutura recomendada;
- documentos de referência;
- exemplos aprovados.

Um item deve ser ativado explicitamente ou por preset conhecido.

Não deve ser confundido com fonte factual do Caso.

## 9. Preset de produto

Contrato inicial:

```text
preset_id
name
description
instructions
knowledge_sources[]
output_structure
citation_policy
```

O preset não contém fatos do Caso.

## 10. Geração

Entrada:

```text
Caso
+ consulta/objetivo do operador
+ assets recuperados
+ Smart Metadata confirmado
+ Base de Conhecimento selecionada
+ preset
```

Saída:

- minuta de relatório;
- mapa de fontes/citações;
- lista de assets utilizados;
- avisos de lacunas;
- separação entre material encontrado e inferência redacional.

## 11. Regra de citação

O MVP deve conseguir, no mínimo, associar cada parágrafo ou unidade textual relevante a uma ou mais fontes recuperadas.

Granularidade por frase é desejável, mas não obrigatória no primeiro corte.

A UI deve permitir:

```text
trecho do relatório
→ ver fontes utilizadas
→ abrir asset original
```

## 12. Assistência conversacional

O assistente IA do AMBITUM pode responder perguntas sobre o Caso, desde que:

- use retrieval;
- mostre fontes;
- admita ausência de suporte;
- não transforme hipótese em fato;
- diferencie Base de Conhecimento de evidência do Caso.

## 13. Modelo de IA

Arquitetura desacoplada de fornecedor.

Primeiro MVP deve suportar ao menos uma das opções:

- modelo local;
- API externa por chave do usuário/configuração institucional.

A escolha concreta deve ser feita em spike técnico antes de acoplar fornecedor ao domínio.

## 14. Segurança

- local por padrão;
- nenhuma saída para serviço externo sem configuração explícita;
- log sem conteúdo sensível desnecessário;
- original não enviado automaticamente;
- política de chunks deve respeitar configuração do provedor;
- autorização por Caso preservada.

## 15. Fora de escopo

- criação manual obrigatória de Blocos;
- editor rico;
- espinha visual sofisticada;
- Inspector Vivo completo;
- Composer antigo;
- colaboração simultânea;
- versionamento documental completo;
- workflow de aprovação;
- ontologia analítica extensa;
- Smart Bins inferidos complexos;
- exportação DOCX/PDF final;
- automação de conclusão jurídica/investigativa.

## 16. Demo canônica

Dataset sintético:

- 5 screenshots;
- 2 PDFs;
- 1 documento textual;
- 2 alvos;
- 2 temas.

Cenário:

```text
criar Caso
→ incorporar 8 assets
→ OCR
→ confirmar Alvo A em 3 assets
→ marcar 2 assets como tema financeiro
→ consultar "o que relaciona Alvo A às movimentações?"
→ escolher preset "Relatório Investigativo — Básico"
→ gerar minuta
→ abrir fontes de dois parágrafos
→ corrigir um trecho
→ salvar rascunho
```

## 17. Critérios de aceitação

- ingestão funciona sem metadado obrigatório;
- OCR gera texto pesquisável;
- operador confirma/rejeita sugestão;
- aplicação em lote funciona;
- retrieval usa metadado e semântica;
- Base de Conhecimento permanece separada;
- relatório é gerado sem Blocos/Seções manuais;
- fontes são navegáveis;
- ausência de suporte produz aviso;
- revisão humana é possível;
- fluxo completo é demonstrável;
- operador considera o fluxo mais simples que o método atual.

## 18. Stop-loss

Parar se a primeira prova exigir simultaneamente:

- nova ontologia complexa;
- reescrita do Intake;
- múltiplos provedores de IA;
- editor completo;
- exportação final;
- reformulação total do Workspace.

O MVP deve provar valor antes de acabamento.
