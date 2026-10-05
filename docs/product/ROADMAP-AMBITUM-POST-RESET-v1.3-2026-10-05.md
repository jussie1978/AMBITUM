# ROADMAP — CIRCE AMBITUM Pós-Reset

**Versão:** 1.3
**Data:** 05/10/2026
**Substitui:** `ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md`
**Autoridade:** Product Reset + ADR Dual Retrieval + Project Master v2.3
**Baseline integrada:** `main` / `origin/main` em `78a49128c65473421894611fcf09999fff34ee8a`

## 1. Estado e ordem

PR-00, PR-01 e PR-02 estão concluídas. PR-03 é a próxima unidade, porém entra primeiro em **REVIEW**, não em implementação.

| ID | Unidade | Estado | Gate macro |
|---|---|---|---|
| PR-00 | Product Reset | DONE | Direção Pool-first formalizada |
| PR-01 | Audit & Freeze | DONE | Contratos preservados e legado congelado |
| PR-02 | Smart Metadata + Smart Bins Lite | **DONE** | Merge PR #1 em `main`; baseline `78a4912` |
| PR-03 | OCR + Derived Text | **REVIEW NEXT** | Validar produto, abstração e papel no capability harness antes de codificar |
| PR-04 | Evidence Retrieval | PLANNED / REVIEW REQUIRED | Recuperação rastreável do Caso sem montagem manual de contexto |
| PR-05 | KB + Knowledge Retrieval | PLANNED / REVIEW REQUIRED | Referências separadas de fatos do Caso |
| PR-06 | Conversational Workspace / Mesa IA | PLANNED / REVIEW REQUIRED | IA contextual capaz de orquestrar capacidades |
| PR-07 | Live Report + Presets | PLANNED / REVIEW REQUIRED | Produto revisável sem virar workflow burocrático |
| PR-08 | DOCX + Vertical End-to-End Demo | PLANNED | Export fiel e prova de valor |
| PR-09 | Operational Pilot | PLANNED | Medir esforço, qualidade e erros |
| PR-10 | Product Decision | PLANNED | Expandir, refatorar, reduzir, substituir ou arquivar |

## 2. PR-02 — encerrada

Entrega integrada:

- fundação Smart Metadata;
- migration 0011;
- Quick Metadata;
- chips;
- operações batch;
- valores comuns;
- Smart Bins Lite determinísticos;
- remoção da dependência operacional do botão “Usar no bloco”;
- smokes pertinentes atualizados;
- documentação de arquitetura/refinamento integrada.

Referências Git:

- feature final: `26fdb76ae12dceb76e23626d7348da104b4c4200`;
- merge em `main`: `78a49128c65473421894611fcf09999fff34ee8a`;
- `main == origin/main` e working tree limpa no gate de 05/10/2026.

## 3. Regra de revisão das próximas funcionalidades

Antes de cada PR relevante, aplicar o teste:

> **Esta capacidade reduz trabalho do policial ou apenas desloca o trabalho para dentro do AMBITUM?**

Preferir fluxos nos quais o operador declara a intenção e o sistema resolve contexto, ferramenta e parâmetros de forma auditável.

Não transformar mecanismos internos — OCR, frames, transcrição, embeddings, RAG, schemas intermediários — em etapas obrigatórias de UX quando puderem funcionar como capacidades transparentes e revisáveis.

Não adotar “chat-only”: visualizações especializadas permanecem quando melhoram inspeção, seleção ou revisão.

## 4. PR-03 — OCR + Derived Text — revisão antes da SPEC

A definição anterior era:

- PDF/imagem;
- texto derivado;
- vínculo ao documento/página;
- preview;
- candidatos revisáveis;
- original soberano.

A revisão deve responder antes de implementar:

1. OCR é uma feature que o usuário “entra para usar” ou uma capability que outras tarefas invocam?
2. Qual o menor contrato comum para derivados que também possa acomodar futuramente transcrição, frames e outras extrações?
3. Quando a execução deve ser automática, sob demanda ou sugerida?
4. Como o operador inspeciona/corrige o resultado sem refazer o trabalho?
5. Como cada derivado referencia o original, página/região/tempo e parâmetros de geração?
6. O que deve persistir e o que pode ser efêmero?
7. Qual parte exige IA e qual deve permanecer determinística?
8. Como a capacidade será chamada pela futura Mesa/IA sem criar acoplamento antecipado?
9. Qual é o custo computacional/local e qual fallback é aceitável?
10. Qual prova demonstra ganho operacional real?

Nenhum patch funcional PR-03 deve começar antes dessas respostas e de uma SPEC/ADR proporcionais.

## 5. PR-04 — Evidence Retrieval

Direção preservada, sujeita a revisão posterior.

Objetivo esperado: permitir que a IA e o operador encontrem material relevante do Caso sem montagem manual de Blocos ou contexto.

Gate futuro deve provar:

- source refs;
- isolamento do Caso;
- relevância;
- rastreabilidade;
- política de atualização/reindexação;
- resposta honesta quando não houver suporte.

## 6. PR-05 — KB + Knowledge Retrieval

Domínio independente de Evidence Retrieval.

Papéis conceituais atuais: REFERENCE, STYLE_EXAMPLE, TEMPLATE.

Gate futuro: referências orientam método/forma sem fornecer fatos atuais do Caso.

## 7. PR-06 — Mesa conversacional / IA contextual

Direção de produto:

- operador expressa intenção;
- sistema usa contexto ativo;
- capability/tool harness escolhe ferramenta autorizada;
- resultado volta com estado, proveniência e controles;
- seleção manual permanece possível quando útil.

A Mesa não deve exigir que o policial “prepare a IA” por copy/paste ou monte estruturas intermediárias sem valor próprio.

## 8. PR-07 — Live Report + Presets

Revisar antes de implementar para garantir que o relatório seja consequência natural do trabalho assistido, e não um segundo workflow burocrático.

## 9. PR-08 — DOCX + Demo vertical

Exportar conteúdo revisado, não geração final opaca.

A demo vertical deve demonstrar ganho operacional mensurável, e não apenas integração técnica.

## 10. PR-09 e PR-10

Piloto controlado mede:

- tempo;
- ações;
- correções;
- suporte factual;
- falhas;
- confiança;
- trabalho evitado.

Economia insignificante frente à complexidade é motivo para reduzir ou rejeitar uma solução.

## 11. Freezer

Permanecem congelados como requisitos obrigatórios:

- InvestigativeBlock;
- Produto/Seções legados;
- UX-03B antiga;
- Smart Bins avançados;
- ontologia extensa;
- colaboração;
- versionamento completo;
- segundo monitor;
- aprovações institucionais.

Próxima unidade oficial: **REVIEW-PR03 — OCR / Derived Content / Capability Harness**.
