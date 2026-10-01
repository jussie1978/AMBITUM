# STATUS / HANDOFF — AMBITUM Architecture Refinement

**Data:** 30/09/2026
**Estado:** PRODUCT REALITY GATE APROVADO / PR-02 PRONTA PARA INTEGRAÇÃO
**Integração:** aplicada e validada no Windows; pronta para commit/push/integração, sem merge declarado neste documento.

## 1. Resultado e decisões

Retirados “Usar no bloco”, variável DOM, atualização disabled e listener exclusivos. Bridge interna e centro atual preservados. Smokes não exigem bridge/criação de Bloco; conservam desacoplamento quando formulário legado presente. Quick Metadata/chips/batch/Smart Bins Lite preservados.

Formalizados Evidence Retrieval e Knowledge Retrieval independentes; KB não sustenta fatos atuais. Mesa conversacional, Relatório Vivo e DOCX como serialização do relatório revisado são arquitetura futura. Blocos são FROZEN LEGACY CAPABILITY. Roadmap e metodologia atualizados; nenhum OCR/RAG/provider/KB/chat/voz/Report schema/DOCX/migration implementado.

## 2. Estado e fontes

Briefing `Texto colado(1).txt`, screenshot Windows e ZIP `arq_circe.zip`. Nenhum AGENTS.md fornecido/encontrado na cópia clonada. Arquivos do ZIP preservados separadamente.

Clone Linux isolado: `/workspace/scratch/e784c21da130/ambitum-review`; branch `feat/pr02-smart-metadata`; HEAD `a0b2bdcd711ecc3a5e3f8a16b5b1850f2368313b`; origin `https://github.com/jussie1978/AMBITUM.git`. Confirmados antes de copiar/editar. Windows informado: `C:\Projetos\CIRCE_ATHENA`, sem acesso direto nesta execução.

Git de revisão: três tracked modificados e oito documentos novos untracked; sem stage/commit/push/merge, main intacta. Backend/service/API/modelo/migrations e históricos não alterados. Finais de linha normalizados a LF para evitar ruído no diff; comparar estado local antes de aplicação.

## 3. Diff técnico acumulado contra checkpoint

```text
app/templates/workspace.html              | 483 ++++++++++++++++++++++--------
 scripts/smoke_workspace_pool_inventory.py |   2 -
 scripts/smoke_workspace_smart_metadata.py |  89 ++++--
 3 files changed, 419 insertions(+), 155 deletions(-)
```

Inclui trabalho PR-02B recebido, já não commitado. O ajuste desta revisão é apenas o delta abaixo, contra o ZIP:

```text
app/templates/workspace.html              |    8 --------
 scripts/smoke_workspace_pool_inventory.py |    1 -
 scripts/smoke_workspace_smart_metadata.py |   21 ++++++++++++---------
 3 files changed, 12 insertions(+), 18 deletions(-)
```

## 4. Documentos novos

| Pasta | Documento |
|---|---|
| docs/adr | ADR-AMBITUM-PR-002-DUAL-RETRIEVAL-CONVERSATIONAL-WORKSPACE-v1.0-2026-09-30.md |
| docs/adr | ADR-AMBITUM-PR02-001-FUNDACAO-SMART-METADATA-v1.1-2026-09-30.md |
| docs/product | CIRCE-AMBITUM-PROJECT-MASTER-v2.2-2026-09-30.md |
| docs/product | ROADMAP-AMBITUM-POST-RESET-v1.2-2026-09-30.md |
| docs/specs | SPEC-AMBITUM-IMPLEMENTATION-MASTER-v2.2-2026-09-30.md |
| docs/specs | SPEC-AMBITUM-PR02-SMART-METADATA-v1.1-2026-09-30.md |
| docs/methodology | CIRCE_SPEC_DRIVEN_WORKFLOW_v1.1_2026-09-30.md |
| docs/status | Este STATUS/HANDOFF |

Versões antigas preservadas e supersede explícito. Metodologia conserva 42 seções e acrescenta cinco refinamentos; regra de reabertura ajustada para correções necessárias à unidade atual. SPEC/ADR PR-02 preservam contrato detalhado de domínio/API/isolamento/auditoria/migration; gates antigos de UX substituídos.

## 5. Testes realmente executados

Ambiente: Linux, Python 3.12, Jinja 3.1.6 em diretório isolado e Node 24.19.0. Não certifica baseline Windows/Python 3.11.

| Verificação | Resultado | Limite |
|---|---|---|
| `python -m scripts.smoke_workspace_smart_metadata` | PASS | Estrutural/estático; route do checkpoint + template refinado. |
| `python -m scripts.smoke_workspace_pool_inventory` | PASS | Estrutural/estático; não teste novo de Intake/Storage. |
| `Environment().parse(template)` | PASS | Sintaxe Jinja, sem banco/sessão. |
| Render do script inline com contexto sintético + `node --check` | PASS | Sintaxe JS; não execução no navegador. |
| `git diff --check` nos arquivos tracked | PASS | Diff técnico sem erros de whitespace. |

Service/HTTP/migration/Intake/Storage não repetidos porque não tocados. Demo completa anterior foi relatada no briefing e não repetida. Não confundir testes estáticos com produto aceito.

### 5.1 Confirmação humana Windows/browser

**Resultado:** PASS
**Product Reality Gate:** PASS

Validação manual realizada em `http://127.0.0.1:8766/workspace/PR02-DEMO`:

- botão “Usar no bloco” ausente;
- dois documentos selecionáveis;
- `+Tag` aplicou `PIX` aos dois documentos;
- chips `PIX` apareceram;
- Smart Bin `PIX` apareceu com contador 2;
- metadata comum aos selecionados apareceu;
- remoção de `PIX` sem redigitação funcionou;
- chips desapareceram e Smart Bin desapareceu/atualizou sem reload completo;
- seleção permaneceu coerente;
- nenhuma criação de Bloco foi usada como gate.

PR-02 / PR-02B aprovada no Product Reality Gate e pronta para commit, push e integração. O merge ainda não é declarado neste handoff.

## 6. Aplicação local preservando estado

`PR02B-REFINAMENTO-PARA-REVISAO.patch` contém o delta contra os três arquivos do ZIP e os oito documentos novos. Não reaplica PR-02B inteira. Arquivos finais individuais também fornecidos para revisão; evitar cópia por cima sem comparar estado.

Antes de aplicar, conferir branch/HEAD/origin/status e SHA-256 dos três arquivos. Se qualquer arquivo mudou desde o ZIP, comparar/regerar delta; não sobrescrever.

| Arquivo | SHA-256 esperado dos bytes recebidos |
|---|---|
| `app/templates/workspace.html` | `73f6e2544e2eca27dc50e71e24d1f370e70ec7757259bcdb409b3e013b678a7a` |
| `scripts/smoke_workspace_pool_inventory.py` | `9f5b4723156bea1f5887f78924d83fa1f541d8c29652b155cf7ae54eeaaf1893` |
| `scripts/smoke_workspace_smart_metadata.py` | `2e2498a3bb84d13c0a81cada9aee913572ca9b8d0318c0328603ca5a5a26e9ba` |

Salve o patch em `C:\Projetos\CIRCE_ATHENA_REFERENCIAS\PR02B-REFINAMENTO-PARA-REVISAO.patch`. Na raiz local:

```powershell
Set-Location 'C:\Projetos\CIRCE_ATHENA'
git branch --show-current
git rev-parse HEAD
git status --short --branch
git remote -v
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Projetos\CIRCE_ATHENA\app\templates\workspace.html'
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Projetos\CIRCE_ATHENA\scripts\smoke_workspace_pool_inventory.py'
Get-FileHash -Algorithm SHA256 -LiteralPath 'C:\Projetos\CIRCE_ATHENA\scripts\smoke_workspace_smart_metadata.py'
git apply --ignore-space-change --check 'C:\Projetos\CIRCE_ATHENA_REFERENCIAS\PR02B-REFINAMENTO-PARA-REVISAO.patch'
```

Somente com identidade/hashes/check corretos:

```powershell
git apply --ignore-space-change 'C:\Projetos\CIRCE_ATHENA_REFERENCIAS\PR02B-REFINAMENTO-PARA-REVISAO.patch'
# Criar um ambiente Python descartável a partir de um interpretador funcional
# disponível no Windows. Não usar nem reparar a .venv do projeto nesta unidade.
& $reviewPython -m scripts.smoke_workspace_smart_metadata
& $reviewPython -m scripts.smoke_workspace_pool_inventory
git diff --check
git diff --stat
git status --short --branch
```

Jinja/JS foram conferidos na cópia de revisão. Não repetir bateria geral sem mudança material. No navegador, confirmar ausência do botão, seleção, aplicação/remoção simples e atualização de chips/Smart Bins. Não criar Bloco como gate nem repetir demo completa.

## 7. Pendências e próxima unidade

Revisão do responsável, aplicação no clone Windows e confirmação humana curta concluídas. Product Reality Gate aprovado; PR-02 pronta para commit/push/integração. PR-00/01 DONE; PR-03–PR-10 PLANNED conforme Roadmap v1.2.

Depois do fechamento/integração: PR-03 OCR + Derived Text, em unidade própria. Stop-loss atual: nenhum OCR/embeddings/vector DB/provider/RAG/KB persistente/chat/voz/Report schema/DOCX/migration nova/refatoração integral/remoção física de Blocos.
