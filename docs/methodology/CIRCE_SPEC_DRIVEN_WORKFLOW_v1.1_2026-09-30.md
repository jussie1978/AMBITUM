# CIRCE — Metodologia Spec-Driven para Desenvolvimento Controlado, Auditável e Eficaz

**Versão:** 1.1
**Data de criação:** 25/08/2026
**Data da revisão:** 30/09/2026
**Substitui:** `CIRCE_SPEC_DRIVEN_WORKFLOW_v1.0_2026-08-25.md`
**Mudança:** preserva as seções 1–42 e acrescenta gates de realidade de produto, feedback arquitetural, verificação proporcional, checkpoint e divisão de trabalho.
**Status:** Documento-base reutilizável
**Aplicação:** Qualquer projeto de software, laboratório técnico, protótipo, ferramenta, módulo ou integração desenvolvido com apoio de IA.

---

## 1. Finalidade

Esta metodologia estabelece um processo de desenvolvimento **controlado, rastreável, verificável e orientado a entrega real**.

O objetivo é reduzir a distância entre:

> **ideia → planejamento → implementação → resultado visível**

e impedir que projetos tecnicamente promissores fiquem presos em ciclos longos de discussão, retrabalho, debugging indefinido, mudanças de escopo ou perda de contexto.

A metodologia foi inspirada nos princípios de **Spec-Driven Development** e em conceitos presentes no **GitHub Spec Kit**, especialmente:

- definição do que deve ser construído antes da implementação;
- separação entre especificação, plano, tarefas e implementação;
- decomposição de funcionalidades grandes em unidades menores;
- artefatos Markdown como memória estruturada;
- análise de consistência entre especificação, plano e execução;
- princípios de projeto como autoridade superior.

Entretanto, este documento **não exige o uso do Spec Kit, CLI específica, automação ou ferramenta determinada**.
O processo foi adaptado para ser mais simples, prático e adequado a projetos conduzidos iterativamente com IA.

---

# 2. Princípio central

> **Nenhuma implementação começa sem que saibamos exatamente o que estamos tentando provar ou entregar.**

Antes de codificar, devem estar claros:

1. o problema;
2. o resultado esperado;
3. o escopo;
4. a stack ou ferramentas;
5. a arquitetura mínima;
6. a sequência de execução;
7. os critérios de aceitação;
8. os critérios de rejeição;
9. como o resultado será demonstrado;
10. o que acontece se a abordagem falhar.

A implementação não é um exercício de exploração infinita.

Ela deve responder a uma pergunta concreta.

---

# 3. Regra fundamental: uma unidade de trabalho por chat

Sempre que possível:

> **1 chat = 1 unidade técnica coerente.**

Exemplos de unidade:

- uma ADR;
- uma SPEC;
- um spike;
- uma sprint;
- uma refatoração delimitada;
- uma auditoria;
- uma correção de bug complexa;
- uma etapa de integração;
- um experimento técnico;
- um fechamento documental.

Evitar no mesmo chat:

- criar uma tela;
- depois implementar um workspace;
- depois refatorar arquitetura;
- depois discutir uma integração;
- depois corrigir bugs de outro módulo.

Esse comportamento destrói rastreabilidade e aumenta a chance de perda de contexto.

Ao concluir a unidade atual, deve-se decidir explicitamente:

- continuar no mesmo chat porque a próxima tarefa é inseparável da atual; ou
- encerrar a unidade e gerar **handoff para um novo chat**.

A preferência padrão é **novo chat quando houver mudança material de escopo**.

---

# 4. Hierarquia documental

A documentação deve funcionar como **memória canônica do projeto**.

A ordem de autoridade recomendada é:

```text
CONSTITUIÇÃO / PRINCÍPIOS
        ↓
SPEC MASTER / VISÃO DO PRODUTO
        ↓
ROADMAP
        ↓
ADRs
        ↓
SPECs
        ↓
PLANOS / SPRINTS
        ↓
TAREFAS
        ↓
IMPLEMENTAÇÃO
        ↓
TESTES / VALIDAÇÃO
        ↓
STATUS / HANDOFF
```

## 4.1 Constituição ou princípios do projeto

Define regras que não podem ser violadas silenciosamente.

Exemplos:

- diretórios protegidos;
- requisitos de segurança;
- dados permitidos ou proibidos;
- política de dependências;
- stack preferencial;
- política de branches;
- padrões de qualidade;
- limites de escopo.

Se uma decisão de implementação violar um princípio vigente, deve ocorrer uma das duas coisas:

1. a implementação é rejeitada; ou
2. o princípio é formalmente revisado e a mudança documentada.

Nunca alterar a regra por conveniência sem registro.

---

## 4.2 SPEC Master

A SPEC Master descreve o produto como um todo.

Deve responder:

- o que é;
- para quem existe;
- qual problema resolve;
- quais capacidades principais possui;
- o que está fora do escopo;
- quais restrições são permanentes;
- qual é a definição de sucesso do produto.

Ela não deve virar um documento de implementação detalhada.

---

## 4.3 Roadmap

O roadmap representa a sequência oficial de evolução.

Cada item deve possuir:

- ID imutável;
- nome;
- objetivo;
- dependências;
- estado;
- unidade documental associada;
- critério macro de conclusão.

Exemplo:

```text
R0 — Fundação
R1 — Mapa
R2 — Camadas
R3 — Seleção
R4 — Timeline
R5 — Playback
```

Estados recomendados:

- `planned`
- `ready`
- `in_progress`
- `blocked`
- `validated`
- `done`
- `rejected`
- `archived`

Uma funcionalidade não deve ser tratada como concluída apenas porque existe código.

Ela é concluída quando foi:

1. implementada;
2. testada;
3. validada;
4. documentada.

---

# 5. Guardião do roadmap

Durante qualquer conversa técnica, a IA deve manter visão do roadmap.

Se surgir uma solicitação fora da etapa atual, deve alertar:

> “Isso pertence a uma etapa posterior do roadmap. Deseja mudar formalmente a prioridade ou registrar como insight para tratar depois?”

As opções são:

### A. Registrar como insight

A ideia é documentada e não interfere na execução corrente.

### B. Criar unidade futura

A ideia vira uma futura SPEC, spike, ADR ou tarefa.

### C. Alterar prioridade

A sequência do roadmap é formalmente modificada.

### D. Incorporar à unidade atual

Somente quando a nova ideia for realmente necessária para concluir o objetivo corrente.

Nenhuma mudança de escopo deve acontecer de forma silenciosa.

---

# 6. Tipos de unidade de trabalho

## 6.1 ADR — Architecture Decision Record

Usar ADR quando a questão for:

> **“Qual decisão estrutural devemos tomar?”**

Exemplos:

- MapLibre ou Cesium;
- SQLite ou PostgreSQL;
- aplicação local ou serviço web;
- arquitetura monolítica ou modular;
- dependência externa ou solução própria.

A ADR deve conter:

- contexto;
- problema;
- opções consideradas;
- critérios;
- decisão;
- consequências;
- riscos;
- status.

Estados possíveis:

- Proposta
- Aceita
- Substituída
- Rejeitada
- Obsoleta

---

## 6.2 SPEC — Especificação de funcionalidade

Usar SPEC quando a pergunta for:

> **“O que esta funcionalidade precisa fazer?”**

A SPEC deve definir comportamento, não apenas aparência.

Conteúdo mínimo:

- objetivo;
- problema;
- usuário ou cenário;
- entradas;
- saídas;
- comportamento;
- estados;
- requisitos;
- restrições;
- casos de erro;
- critérios de aceitação;
- critérios de rejeição;
- dependências.

Uma SPEC grande pode ser dividida em várias sub-SPECs.

---

## 6.3 Spike — Experimento técnico

Usar spike quando ainda não sabemos se algo é tecnicamente viável.

Pergunta típica:

> **“Esta tecnologia realmente resolve nosso problema?”**

Exemplo:

```text
SPIKE — Cesium + Photorealistic 3D Tiles em Cuiabá
```

O spike deve ser descartável.

Ele não precisa possuir arquitetura final, mas deve possuir:

- hipótese;
- pergunta;
- stack;
- ambiente;
- cenário de teste;
- dados simulados;
- limite de esforço;
- critérios de sucesso;
- critérios de falha;
- demonstração visível;
- decisão final.

Resultado obrigatório:

```text
APROVADO
REPROVAR
REFATORAR UMA VEZ
SUBSTITUIR TECNOLOGIA
ARQUIVAR
```

Spike não pode virar produto por acidente.

---

## 6.4 Sprint

Sprint é um conjunto pequeno e fechado de trabalho necessário para entregar parte de uma SPEC.

Uma SPEC pode ser concluída em:

```text
SPEC-03
 ├─ Sprint 03.1
 ├─ Sprint 03.2
 └─ Sprint 03.3
```

Cada sprint precisa produzir resultado verificável.

Nunca criar uma sprint definida apenas como:

> “continuar desenvolvimento”.

---

## 6.5 Refatoração

Refatoração deve ser uma unidade própria quando altera de maneira relevante:

- estrutura;
- estado;
- componentes;
- organização;
- arquitetura;
- contratos;
- fluxo.

A pergunta é:

> **“Como melhorar internamente sem alterar o comportamento aprovado?”**

Refatoração não deve servir como desculpa para redefinir continuamente a funcionalidade.

---

## 6.6 Auditoria

Usar auditoria quando o sistema começou a acumular sintomas, regressões ou inconsistências.

Antes de adicionar mais funcionalidades:

1. parar;
2. mapear sintomas;
3. reproduzir problemas;
4. localizar causas;
5. classificar severidade;
6. corrigir regressões;
7. validar novamente;
8. somente então retomar roadmap.

---

# 7. Ciclo padrão de desenvolvimento

O ciclo normal é:

```text
INTENÇÃO
   ↓
SPEC
   ↓
PLANO
   ↓
TAREFAS
   ↓
IMPLEMENTAÇÃO
   ↓
TESTE
   ↓
DEMONSTRAÇÃO
   ↓
DECISÃO
   ↓
DOCUMENTAÇÃO
   ↓
HANDOFF
```

Para decisões arquiteturais:

```text
PROBLEMA
   ↓
OPÇÕES
   ↓
SPIKE (se necessário)
   ↓
EVIDÊNCIA
   ↓
ADR
   ↓
IMPLEMENTAÇÃO
```

---

# 8. Fase 1 — Intenção

Antes de qualquer trabalho técnico, registrar:

### Problema

O que está errado, ausente ou insuficiente?

### Objetivo

O que queremos alcançar?

### Resultado esperado

O que deverá existir quando terminarmos?

### Valor

Por que isso vale a pena?

### Fora do escopo

O que deliberadamente não será feito agora?

---

# 9. Fase 2 — Definição da bancada

Antes de construir o produto, identificar os elementos necessários para provar a solução.

Pensar como uma bancada eletrônica:

```text
fonte
resistor
protoboard
fio
instrumento de medição
carga
```

No software:

```text
runtime
framework
biblioteca
dados
serviço
API
renderer
UI mínima
teste
medição
```

Pergunta obrigatória:

> **Qual é a menor combinação de componentes capaz de provar ou refutar nossa hipótese?**

Essa combinação é a **bancada mínima**.

---

# 10. Fase 3 — Stack e arquitetura

Antes de codificar, declarar:

- linguagem;
- framework;
- bibliotecas;
- serviços externos;
- APIs;
- armazenamento;
- estrutura de diretórios;
- componentes principais;
- fluxo de dados;
- dependências.

Também deve ser respondido:

> O projeto será um único arquivo, um protótipo descartável ou uma estrutura modular destinada a crescer?

Estrutura deve ser proporcional à intenção.

Não criar arquitetura empresarial para um spike de dois dias.

Também não construir um produto crescente dentro de um HTML monolítico se isso comprometer manutenção.

---

# 11. Fase 4 — Plano executável

O plano deve dizer **em qual ordem as coisas serão feitas**.

Exemplo:

```text
1. preparar ambiente;
2. instalar dependências;
3. iniciar aplicação;
4. renderizar mapa;
5. validar navegação;
6. adicionar marcador;
7. adicionar rota;
8. adicionar polígono;
9. medir desempenho;
10. registrar decisão.
```

Cada passo deve possuir:

- pré-condição;
- ação;
- resultado esperado;
- validação.

Evitar tarefas genéricas como:

```text
melhorar mapa
corrigir interface
otimizar sistema
```

Preferir:

```text
renderizar tiles 3D na câmera inicial
selecionar marcador e centralizar câmera
filtrar eventos por severidade
```

---

# 12. Fase 5 — Decomposição em tarefas

Cada tarefa deve ser:

- pequena;
- verificável;
- necessária;
- rastreável à SPEC;
- executável sem redefinir o projeto.

Formato recomendado:

```text
T03 — Renderizar camada de eventos
Origem: SPEC-02 / FR-04
Dependência: T01, T02
Resultado: 300 eventos visíveis
Teste: contagem determinística
```

Tarefas podem ser agrupadas em sprint.

---

# 13. Fase 6 — Implementação incremental

A implementação deve seguir uma regra simples:

> **Uma função por vez.**

Fluxo:

```text
implementar
    ↓
rodar
    ↓
verificar
    ↓
aceitar ou corrigir
    ↓
congelar
    ↓
próxima função
```

Não empilhar dez funcionalidades não validadas.

Quanto maior a distância entre implementação e teste, maior o custo de diagnóstico.

---

# 14. Resultado observável obrigatório

Todo incremento funcional deve produzir algo que possa ser observado.

Exemplos:

- uma tela;
- um botão;
- uma rota;
- um mapa;
- um relatório;
- um arquivo;
- uma API funcionando;
- uma resposta determinística;
- um gráfico;
- uma transformação;
- um teste automatizado;
- um cenário demonstrável.

A pergunta é:

> **“Como alguém que não participou da implementação comprova que isso funciona?”**

Sempre que possível, criar uma **demo reproduzível**.

Exemplo:

```text
npm run demo
```

ou:

```text
Abrir aplicação
→ clicar em "Demo"
→ visualizar cenário simulado
```

---

# 15. Testes e validação

Cada unidade deve definir antecipadamente o que será medido.

Possíveis dimensões:

### Funcional

Faz o que a SPEC exige?

### Visual

A interface corresponde ao resultado esperado?

### Desempenho

É suficientemente rápido?

### Usabilidade

A interação é compreensível?

### Robustez

Falhas previsíveis são tratadas?

### Manutenção

A estrutura continua compreensível?

### Segurança

Alguma regra foi violada?

### Reprodutibilidade

Outra pessoa consegue executar?

---

# 16. Critérios de aceitação

Critérios de aceitação devem ser binários sempre que possível.

Ruim:

> “O mapa deve ficar bom.”

Melhor:

```text
- mapa carrega sem erro;
- câmera inicial centraliza Cuiabá;
- edifícios 3D são exibidos;
- marcador é selecionável;
- rota é renderizada;
- FPS permanece acima do limite acordado;
- build passa.
```

---

# 17. Critérios de rejeição

Toda unidade experimental deve possuir também critérios de rejeição.

Exemplo:

```text
REJEITAR se:

- cobertura geográfica for insuficiente;
- desempenho ficar abaixo do mínimo;
- licença impedir o uso pretendido;
- custo exceder o orçamento;
- integração exigir reescrita desproporcional;
- resultado visual não atender à necessidade operacional.
```

Isto evita racionalizar indefinidamente uma solução ruim.

---

# 18. Stop-loss técnico

Nenhuma abordagem deve consumir tempo indefinidamente apenas porque já houve investimento nela.

Quando uma implementação falhar:

```text
1. diagnosticar;
2. corrigir causa conhecida;
3. repetir teste;
4. avaliar resultado.
```

Se continuar falhando, deve ocorrer um gate explícito:

### Refatorar

Existe evidência de que a solução funciona, mas a implementação atual está errada.

### Substituir abordagem

A tecnologia atual não atende, mas existe alternativa viável.

### Reduzir escopo

A ideia principal ainda tem valor, mas parte da ambição é inviável.

### Arquivar

Não existem opções tecnicamente ou economicamente razoáveis.

> **Arquivar um caminho inviável é resultado técnico válido.**

Persistência não pode se transformar em desperdício.

---

# 19. Matriz de decisão após cada unidade

Ao final de uma unidade, escolher explicitamente:

| Estado | Significado |
|---|---|
| **APROVADO** | Resultado atende critérios. Seguir roadmap. |
| **APROVADO COM PENDÊNCIAS** | Núcleo funciona; pendências não bloqueantes registradas. |
| **REFATORAR** | Conceito é válido, implementação precisa revisão delimitada. |
| **BLOQUEADO** | Falta dependência, informação ou recurso externo. |
| **REJEITADO** | Critérios mínimos não foram alcançados. |
| **ARQUIVADO** | Não há custo-benefício para continuar. |

A decisão precisa ser registrada no handoff.

---

# 20. Insights durante a implementação

É normal surgirem ideias melhores durante o trabalho.

Entretanto:

> **Insight não significa mudança automática de escopo.**

Ao surgir uma ideia:

```text
INSIGHT
    ↓
é necessário para concluir a unidade atual?
    ↓
SIM → avaliar incorporação
NÃO → registrar backlog / nova SPEC / novo spike
```

Isso permite criatividade sem destruir a sequência.

---

# 21. Congelamento de funcionalidade

Uma funcionalidade aprovada deve ser considerada **congelada**.

Isso significa:

- não reabrir sem motivo;
- não alterar por impulso;
- não quebrar para acomodar funcionalidade futura;
- preservar seu contrato.

Pode ser reaberta quando:

- surgir bug;
- requisito mudar;
- dependência exigir;
- nova ADR substituir decisão anterior;
- evidência mostrar que a solução é insuficiente.

A reabertura deve gerar nova unidade de trabalho quando houver mudança material de escopo. Correção necessária para cumprir o objetivo da unidade em curso pode permanecer nela, conforme seção 43.2.

---

# 22. Controle de contexto

Para projetos conduzidos com IA, contexto é recurso técnico.

Portanto:

### Evitar

- chats intermináveis;
- múltiplos módulos no mesmo chat;
- decisões misturadas com debugging;
- especificação sendo redefinida durante implementação;
- depender da memória conversacional como fonte oficial.

### Preferir

- unidade pequena;
- documentos canônicos;
- snapshots;
- status atualizado;
- handoffs;
- IDs rastreáveis;
- links entre ADR, SPEC, sprint e commit.

---

# 23. Rastreabilidade

Toda implementação relevante deve poder responder:

> **Por que esse código existe?**

Cadeia ideal:

```text
Roadmap R3
   ↓
ADR-004
   ↓
SPEC-012
   ↓
Sprint 012.2
   ↓
Task T07
   ↓
Branch
   ↓
Commit
   ↓
Teste
```

Não é necessário usar todas as camadas para pequenas tarefas.

Mas funcionalidades significativas devem possuir trilha suficiente para reconstrução histórica.

---

# 24. Branches

Quando Git estiver presente:

> **Uma branch deve representar uma unidade técnica coerente.**

Exemplos:

```text
feat/spec-012-timeline
spike/cesium-cuiaba
fix/workspace-state-persistence
refactor/event-store
```

Evitar trabalhar diretamente em `main` quando o projeto exigir isolamento.

Antes da implementação, confirmar:

```text
diretório
raiz Git
branch
status
remote
```

Projetos podem adicionar seus próprios guardrails.

---

# 25. Commits

Commit não significa simplesmente “salvar código”.

Commit representa um **checkpoint verificável**.

Antes do commit:

- escopo correto;
- testes executados;
- build executado quando aplicável;
- nenhum segredo;
- nenhum arquivo acidental;
- documentação sincronizada.

Mensagem deve comunicar a unidade concluída.

---

# 26. Handoff obrigatório

Toda unidade relevante termina com um handoff.

O handoff deve permitir que outro chat, outra IA ou outra pessoa continue o trabalho sem reconstruir toda a conversa.

Conteúdo mínimo:

```text
# HANDOFF

## Unidade concluída
## Objetivo
## Resultado
## Arquivos alterados
## Decisões
## Testes
## Evidências
## Pendências
## Riscos
## Estado do Git
## Roadmap atualizado
## Próxima unidade
## Arquivos que precisam ser anexados
## Prompt recomendado para o próximo chat
```

Se uma unidade foi rejeitada, o handoff também deve explicar:

- por que falhou;
- o que foi tentado;
- o que não deve ser repetido;
- qual alternativa será considerada.

---

# 27. Briefing de entrada do próximo chat

O novo chat começa com um briefing curto e operacional.

Exemplo:

```text
PROJETO:
CIRCE Situation Room

UNIDADE:
SPIKE-004 — Cesium / Cuiabá

OBJETIVO:
Avaliar cobertura 3D e navegação operacional.

ESTADO:
Roadmap R1 em andamento.
SPIKE-003 rejeitado.

FONTES A LER:
- SPEC_MASTER.md
- ROADMAP.md
- ADR_002.md
- HANDOFF_SPIKE_003.md

ARQUIVOS VISUAIS:
- baseline.png

RESTRIÇÕES:
- dados simulados;
- não alterar projeto original.

PRIMEIRA AÇÃO:
confirmar ambiente e reproduzir baseline.
```

O objetivo é minimizar reconstrução de contexto.

---

# 28. Estado do projeto

Todo projeto relevante deve possuir um documento simples de estado atual.

Exemplo:

```text
ROADMAP: 42%
ETAPA: R3
SPEC ATUAL: SPEC-012
SPRINT: 012.2
STATUS: in_progress
BLOQUEIOS: nenhum
ÚLTIMA UNIDADE: SPIKE-004 aprovado
PRÓXIMA: Sprint 012.3
```

Percentuais não precisam ser matematicamente perfeitos.

Devem representar posição aproximada e compreensível no plano.

---

# 29. Fechamento de SPEC

Quando todas as sprints associadas forem concluídas:

```text
SPEC-012
├─ Sprint 012.1 ✅
├─ Sprint 012.2 ✅
└─ Sprint 012.3 ✅
```

produzir um fechamento:

```text
SPEC-012 — CONCLUÍDA

Critérios: 12/12
Testes: aprovados
Pendências: 2 não bloqueantes
ADR relacionada: ADR-004
Roadmap: R3 concluído
```

Somente então marcar a SPEC como finalizada.

---

# 30. Atualização documental

Uma decisão nova pode impactar documentos existentes.

Antes de encerrar a unidade, verificar:

- SPEC Master;
- roadmap;
- ADRs;
- SPECs;
- status;
- changelog;
- arquitetura;
- modelo de dados;
- critérios de aceitação;
- handoff.

Se algum deles ficou inconsistente, deve ser atualizado.

Documentação desatualizada é dívida técnica.

---

# 31. Regra contra “documentação decorativa”

Documentação existe para governar execução.

Se um documento não ajuda a responder:

- o que estamos fazendo;
- por quê;
- como;
- em qual ordem;
- como validar;
- o que vem depois;

ele provavelmente está excessivo.

Não criar documentos apenas para aumentar formalidade.

---

# 32. Regra contra arquitetura prematura

Antes de introduzir:

- backend;
- banco;
- fila;
- worker;
- microsserviço;
- IA;
- infraestrutura;
- abstração adicional;

perguntar:

> **Isto é necessário para a unidade atual?**

Se não for, adiar.

---

# 33. Regra da demonstração para terceiros

Sempre que o projeto pretender ser utilizado, apresentado ou avaliado por outras pessoas, deve existir um caminho de demonstração.

Idealmente:

```text
instalar
executar
abrir
clicar
ver
```

Uma funcionalidade que só pode ser comprovada lendo o código ainda não está suficientemente demonstrada para validação de produto.

---

# 34. Modo laboratório

Tecnologias desconhecidas devem preferencialmente entrar primeiro em laboratório isolado.

Fluxo:

```text
IDEIA
  ↓
SPIKE
  ↓
DEMO
  ↓
MEDIDA
  ↓
DECISÃO
```

Somente uma tecnologia aprovada migra para o produto.

Isto vale especialmente para:

- engines;
- renderers;
- modelos de IA;
- APIs;
- bancos;
- sistemas de mapas;
- bibliotecas grandes;
- formatos experimentais.

---

# 35. Exemplo aplicado

Problema:

> “Precisamos de mapa urbano 3D reconhecível.”

## Etapa 1 — Hipótese

```text
Google Photorealistic 3D Tiles + Cesium pode atender.
```

## Etapa 2 — Spike

```text
SPIKE-GEO-01
```

## Etapa 3 — Bancada

```text
Vite
CesiumJS
Photorealistic 3D Tiles
Cuiabá
1 marcador
1 rota
1 polígono
```

## Etapa 4 — Testes

```text
cobertura
qualidade visual
interação
sobreposição
FPS
custo
licença
```

## Etapa 5 — Decisão

```text
APROVADO
```

ou:

```text
REJEITADO — cobertura insuficiente
```

## Etapa 6 — Próxima opção

Somente após rejeição formal:

```text
SPIKE-GEO-02
```

Esse processo evita semanas tentando salvar uma abordagem que não resolve o problema.

---

# 36. Fluxo resumido

```text
┌───────────────────────┐
│ VISÃO / SPEC MASTER   │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ ROADMAP               │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ ADR / SPEC / SPIKE    │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ PLANO                 │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ TAREFAS / SPRINT      │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ IMPLEMENTAÇÃO         │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ TESTE                 │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ DEMONSTRAÇÃO          │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ DECISÃO               │
└──────────┬────────────┘
           ↓
┌───────────────────────┐
│ DOC + HANDOFF         │
└──────────┬────────────┘
           ↓
       PRÓXIMA UNIDADE
```

---

# 37. Checklist de abertura de unidade

- [ ] Qual projeto?
- [ ] Qual unidade de trabalho?
- [ ] Qual ID?
- [ ] Em qual item do roadmap estamos?
- [ ] Qual objetivo?
- [ ] Qual resultado visível esperado?
- [ ] Qual escopo?
- [ ] O que está fora do escopo?
- [ ] Quais documentos governam esta unidade?
- [ ] Existe ADR pendente?
- [ ] Stack definida?
- [ ] Ambiente definido?
- [ ] Branch definida?
- [ ] Critérios de aceitação definidos?
- [ ] Critérios de rejeição definidos?
- [ ] Testes definidos?
- [ ] Stop-loss definido?
- [ ] Próxima decisão prevista?

---

# 38. Checklist de encerramento

- [ ] Resultado implementado?
- [ ] Resultado executado?
- [ ] Resultado observado?
- [ ] Critérios de aceitação verificados?
- [ ] Critérios de rejeição verificados?
- [ ] Testes executados?
- [ ] Build executado?
- [ ] Bugs conhecidos registrados?
- [ ] Insights futuros registrados?
- [ ] Decisão final tomada?
- [ ] Roadmap atualizado?
- [ ] Status atualizado?
- [ ] ADRs sincronizadas?
- [ ] SPEC sincronizada?
- [ ] Handoff criado?
- [ ] Próxima unidade declarada?
- [ ] Arquivos necessários para o próximo chat listados?

---

# 39. Papel da IA

A IA atua simultaneamente como:

- copiloto técnico;
- guardiã de escopo;
- mantenedora de contexto;
- revisora de consistência;
- facilitadora de documentação;
- auditora de roadmap;
- apoio à implementação.

A IA não deve:

- concordar automaticamente com mudança de escopo;
- inventar sucesso;
- declarar funcionalidade concluída sem validação;
- esconder falha de teste;
- continuar indefinidamente uma abordagem sem custo-benefício;
- introduzir arquitetura não aprovada;
- misturar unidades diferentes por conveniência;
- substituir evidência por expectativa.

Quando detectar desvio, deve apontá-lo.

---

# 40. Papel do decisor humano

O responsável pelo projeto decide:

- prioridades;
- produto;
- trade-offs;
- aceitação visual;
- mudanças de escopo;
- custos;
- riscos;
- continuidade;
- abandono.

A IA pode recomendar.

A decisão final pertence ao responsável pelo projeto.

---

# 41. Princípio de encerramento

> **Planejar é definir o alvo.
> Especificar é tornar o alvo verificável.
> Implementar é construir uma hipótese.
> Testar é confrontá-la com a realidade.
> Documentar é preservar o aprendizado.
> Decidir é avançar — inclusive quando avançar significa abandonar uma solução ruim.**

O objetivo desta metodologia não é produzir mais documentação.

O objetivo é:

> **entregar o que foi proposto, saber exatamente onde o projeto está e descobrir cedo quando algo não vale a pena.**

---

# 42. Referências conceituais

A metodologia deste documento é própria e adaptada ao fluxo de projetos CIRCE, porém utiliza conceitos compatíveis com Spec-Driven Development e com o GitHub Spec Kit.

Referências:

- GitHub Spec Kit: https://github.com/github/spec-kit
- Documentação: https://github.github.com/spec-kit/
- Spec of Specs: https://github.github.com/spec-kit/concepts/spec-of-specs.html
- Agentic SDD: https://github.com/github/spec-kit/blob/main/docs/reference/agentic-sdd.md

Fluxo principal do Spec Kit utilizado como inspiração:

```text
Constitution
→ Specify
→ Clarify
→ Plan
→ Tasks
→ Analyze
→ Implement
→ Converge
```

A metodologia CIRCE acrescenta como elementos operacionais centrais:

```text
Roadmap
Unidade por chat
Bancada mínima
Spike descartável
Resultado observável
Critério de rejeição
Stop-loss técnico
Congelamento
Handoff
Snapshot de estado
```

---



# 43. Refinamentos operacionais da v1.1

## 43.1 Product Reality Gate

Para funcionalidades com UX/workflow humano: **teste técnico passar ≠ produto aceito**. Após implementação funcional, quando pertinente: demo real → uso humano → decisão de produto. Registrar cenário, resultado técnico e avaliação operacional separadamente.

Um recurso pode ficar FUNCIONALMENTE APROVADO e PRODUTAMENTE REJEITADO / REVISAR UX se for burocrático, confuso ou contrariar o objetivo. Aceitação exige redução de esforço/clareza/controle no cenário previsto, além dos testes. Não marcar DONE apenas por smoke verde.

## 43.2 Feedback arquitetural da demo

Uma demo pode mostrar que a arquitetura não representa o trabalho humano. Registrar aprendizado e evidência; preservar checkpoint seguro; ajustar SPEC/ADR; corrigir direção antes do merge quando barato. Correção necessária ao objetivo original não é scope creep por definição. Funcionalidades novas independentes continuam sob as regras de roadmap/escopo.

Distinguir decisão vigente, implementação existente e arquitetura futura. Um ADR aceito não prova que sua arquitetura foi implementada. Preservar documentos antigos e declarar supersede nas revisões.

## 43.3 Proportional Verification

Após patch pequeno, testar a superfície afetada. Não executar “verificação da verificação” sem mudança material. Bateria integral somente quando boundary/domínio crítico/migration mudar, regressão surgir ou risco concreto justificar. Pausa, retomada ou formalidade não justificam repetição automática.

Registrar comandos reais, ambiente, resultado e limites. Reaproveitar evidência anterior com origem explícita, sem apresentá-la como teste novo. Teste estrutural/sintático não equivale a teste de navegador. Demo manual completa já aceita não precisa ser repetida por retirada pontual de botão; confirmar a superfície afetada.

## 43.4 Checkpoint antes de reorientação

1. Preservar checkpoint seguro na branch coerente; alterações não commitadas devem ser resguardadas antes de qualquer operação que possa perdê-las.
2. Confirmar diretório, branch, HEAD, remote e working tree.
3. Registrar decisão e motivo.
4. Refinar com patch delimitado.
5. Comparar com o estado preservado e demonstrar o efeito.
6. Aceitar/rejeitar e atualizar documentação.

Não resetar, descartar, force push ou rebasear silenciosamente. Preservar checkpoint não obriga nova branch nem commit prematuro; seguir autorização/guardrails do projeto e comparar o estado antes de aplicar patch. Evitar sobrescrever alterações posteriores.

## 43.5 Divisão de trabalho IA

| Papel/ferramenta | Responsabilidade preferencial |
|---|---|
| Modelo principal | Arquitetura, integração, decisões e revisão crítica. |
| Modelos mais baratos | Tarefas mecânicas pequenas, delimitadas e verificáveis. |
| Work | Mudanças cross-cutting, auditorias, múltiplos arquivos, documentação coordenada e workflows longos. |
| Codex no repositório | Implementação técnica delimitada e validação no ambiente correspondente. |

Evitar delegação quando coordenação custar mais que o trabalho. Essa divisão orienta eficiência; não exige paralelismo, troca de modelo ou infraestrutura adicional. Confirmar disponibilidade e permissões antes de executar delegação. A execução técnica no repositório canônico deve preservar a unidade/branch e a responsabilidade de integração.

---

**Fim do documento**
