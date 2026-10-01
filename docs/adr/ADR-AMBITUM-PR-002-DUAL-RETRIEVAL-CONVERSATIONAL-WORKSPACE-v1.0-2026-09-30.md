# ADR-AMBITUM-PR-002 — Dual Retrieval e Workspace Conversacional

**Versão:** 1.0
**Data:** 30/09/2026
**Status da decisão:** ACEITA no briefing do responsável; implementação futura
**Repositório:** `jussie1978/AMBITUM`
**Complementa:** `ADR-AMBITUM-PR-001-PRODUCT-RESET-v1.0-2026-09-28.md`
**Supersede parcialmente:** gates que tornavam a bridge/criação de Blocos requisito da PR-02 e direção Presets → Report Generator isolado. Não substitui os contratos de Intake, Original, isolamento e auditoria.

## 1. Contexto e problema

A fundação PR-02 possui checkpoint funcional `a0b2bdcd711ecc3a5e3f8a16b5b1850f2368313b`. A primeira UI funcionava tecnicamente, mas exigia manipulação de kind/value/linked_person_id e redigitação para remoção. A PR-02B introduziu Quick Metadata, chips, aplicação em lote e Smart Bins Lite. O briefing registra validação humana parcial: aplicar PIX a dois documentos, ver chips/bin/contador sem reload, filtrar pelo bin e remover o valor comum sem redigitação.

A demo reforçou que reconstruir contexto manualmente em InvestigativeBlocks não corresponde ao objetivo operacional. Recuperar material relevante é responsabilidade do sistema. Aprovação técnica e aceitação de produto são decisões distintas.

## 2. Alternativas

| Alternativa | Avaliação |
|---|---|
| Blocos manuais obrigatórios antes da IA | Rejeitada: transfere ao investigador trabalho de preparação que o retrieval deve executar. |
| Retrieval único misturando Caso e KB | Rejeitada: relatórios anteriores/modelos podem contaminar fatos atuais. |
| Dois domínios, Mesa conversacional e Relatório Vivo | Aceita: separa fatos e referências e permite revisar o produto durante a construção. |

## 3. Decisão: dois domínios independentes

| Domínio | Origem | Função | Regra de suporte |
|---|---|---|---|
| Evidence Retrieval | Caso ativo, documentos, imagens, OCR, extrações, metadata, vínculos e derivados | Recuperar material factual do Caso | Afirmações factuais do Caso exigem source refs deste domínio. |
| Knowledge Retrieval | KB adicionada pelo usuário/equipe/instituição | Método, estrutura, terminologia, estilo, interpretação e referência técnica | Não sustenta, por si só, fatos do Caso atual. |

A presença de uma fonte no Caso não torna seu conteúdo automaticamente verdadeiro ou confirmado. Proveniência, contexto e revisão continuam necessários. Smart Metadata/Smart Bins organizam e restringem recuperação; um rótulo não prova a ocorrência que descreve.

Exemplo: “João transferiu R$ 10.000 para Empresa X” exige fonte do Caso. “Use o Manual X como estrutura” pode usar Knowledge Retrieval. Relatório anterior usado como estilo não pode fornecer nomes, valores ou acontecimentos ao Caso atual.

Os domínios têm origem, autorização e significado separados. A decisão não exige dois produtos de banco nem escolhe vector DB/provider. Recuperação futura deve respeitar Caso ativo e permissões da KB; resultados devem preservar a identidade do domínio. Ausência de suporte deve ser apresentada como lacuna, sem preencher fatos com exemplos da KB.

## 4. Papéis e escopos conceituais da KB

| Papel | Uso |
|---|---|
| REFERENCE | Conhecimento e metodologia. |
| STYLE_EXAMPLE | Exemplo de redação e estrutura. |
| TEMPLATE | Modelo de produto. |

KB não recebe papel EVIDENCE dentro do Caso. Se documento externo passar a ser material evidencial, deve ingressar formalmente pelo Intake canônico, com identidade/proveniência próprias no Caso.

Escopos futuros: pessoal (relatórios/modelos próprios), equipe (procedimentos e referências selecionados) e institucional (manuais, doutrina, normas e documentação). Não implementar níveis, tabelas ou schemas nesta unidade.

## 5. Workspace alvo

- **Esquerda — Pool / Smart Bins:** incorporação, organização, metadata, filtros e seleção contextual opcional.
- **Centro — Mesa conversacional / IA:** chat, comandos, compose, fontes e refinamento iterativo. Seleção manual pode restringir contexto, mas não é pré-requisito para recuperação. Voz é modalidade de entrada da mesma interface.
- **Direita — Relatório Vivo / Inspector:** preview real do produto; inserir/substituir/reorganizar texto, imagens e seções e revisar fontes/redação.

Conteúdo do relatório deverá poder manter `source_refs`, `provenance`, `authorship_mode`, revisão e origem da alteração. Esses requisitos são conceituais; schema definitivo e motor de edição são futuros.

## 6. DOCX

DOCX será a serialização do Relatório Vivo revisado. O preview deve permitir conhecer o conteúdo antes de exportar. Não regenerar opacamente uma peça diferente no momento do export.

## 7. Destino do legado

`InvestigativeBlock` e `InvestigativeBlockSource`: **FROZEN LEGACY CAPABILITY**. Preservar backend, migrations e histórico; não ampliar, apagar ou migrar. Não exigir Blocos para RAG, relatório ou geração. Produto/Seções e UX-03B continuam congelados como workflow obrigatório.

Retirar “Usar no bloco” da Quick Metadata. A bridge interna existente pode permanecer se barata, sem requisito de aceitação da PR-02. O centro atual pode permanecer temporariamente; sua substituição pertence à PR-06.

## 8. Consequências, riscos e limites

A nova direção reduz preparação manual e torna o produto observável. Exige no futuro contratos de fontes, recuperação, revisão e edição. Riscos: vazamento entre Casos, uso de exemplos da KB como fatos, conclusão excessiva sobre fontes fracas e perda de rastreabilidade após edição. Os gates futuros devem demonstrar isolamento, separação de domínios e correspondência entre texto e fonte.

Nesta unidade: arquitetura, documentação e fechamento mínimo PR-02B. Nenhum OCR, embedding, provider, KB persistente, novo schema/migration de Report, voz, DOCX ou refatoração integral do Workspace.

## 9. Aceitação e ligação documental

PR-02B deve preservar Quick Metadata/chips/Smart Bins sem reload e remover ação legada e dependências de testes. PR-02 permanece FINALIZING até fechamento técnico, revisão e integração. Roadmap corrente: `ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md`. Contrato PR-02: `SPEC-AMBITUM-PR02-SMART-METADATA-v1.1-2026-09-30.md`. Resultado/testes: `STATUS-HANDOFF-AMBITUM-ARCHITECTURE-REFINEMENT-2026-09-30.md`.
