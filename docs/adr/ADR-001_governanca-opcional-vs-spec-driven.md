# ADR-001: Governança opcional por maturidade em vez do rigor spec-driven obrigatório

## Status

Aceita

## Contexto

Em setembro de 2026, foi feita uma análise comparativa entre o ScrumAIDev e o [spec-kit](https://github.com/github/spec-kit) (GitHub), um framework que também guia desenvolvimento assistido por IA, mas por um caminho diferente: "Spec-Driven Development" (SDD). No spec-kit, a especificação é o artefato primário e o código é uma expressão gerada e descartável dela; todo ciclo de trabalho passa por uma sequência obrigatória (constituição → especificação → plano → tarefas → implementação → convergência), com checagens formais de consistência entre artefatos, marcadores de ambiguidade limitados, e um adaptador que converte os mesmos comandos para a sintaxe nativa de dezenas de agentes de IA diferentes.

O spec-kit é mantido como produto pelo GitHub: tem CLI instalável, autoatualização, ecossistema de extensões/presets/bundles de terceiros e lançamentos frequentes (várias versões por mês no momento desta análise).

A dúvida central: o ScrumAIDev deveria adotar esse mesmo nível de rigor obrigatório por padrão, ou continuar como está?

Nota de validade: esta análise reflete o estado do spec-kit em setembro de 2026. É um projeto com lançamentos frequentes — nomes de comando, arquitetura interna e escopo do ecossistema podem já ter mudado. Este ADR registra o raciocínio da decisão, não uma descrição atualizada do spec-kit.

## Decisão

O ScrumAIDev continua **sprint-driven por padrão**, com rigor técnico opcional e escalonado pelo próprio Modelo de Maturidade já existente (`docs/maturity_model.md`, Níveis 0-4), em vez de exigir um ciclo formal de especificação para toda mudança.

Elementos do spec-kit com baixo custo de contexto e alto valor prático foram importados seletivamente (ver PR #3):

- verificação automática de que todo workflow/skill está documentado (`scripts/check_agent_docs_sync.py`), inspirada no teste de consistência de agentes do spec-kit;
- marcador de ambiguidade `[PRECISA CLARIFICAR]`, limitado a 3 por User Story;
- checagem de consistência entre artefatos no `/code-review`, mas como passo **condicional** (só roda em Nível ScrumAIDev 2+ ou `Behavior change = YES`), não obrigatório em toda mudança;
- disclosure de assistência de IA via trailer de commit (`Assisted-by:`), nunca `Co-authored-by:`;
- declaração explícita do modelo de persistência de specs/stories.

Elementos de infraestrutura pesada do spec-kit foram explicitamente **não adotados**: CLI própria instalável, adaptador de sintaxe para múltiplos agentes de IA, e marketplace de extensões/presets/bundles de terceiros.

## Alternativas Consideradas

| Alternativa | Vantagens | Riscos / Custos |
|---|---|---|
| Adotar o modelo spec-driven do spec-kit integralmente | Rigor máximo; forte consistência entre especificação/plano/código; suporte nativo a dezenas de agentes de IA | Aumento significativo do custo de contexto por tarefa, contrariando o princípio central de `docs/token_budget.md`; abandono do vínculo com as cerimônias Scrum que o framework já usa; esforço de engenharia (CLI, adaptador multi-agente, ecossistema) desproporcional ao tamanho atual do ScrumAIDev |
| Manter o ScrumAIDev como estava, ignorando o spec-kit | Zero esforço, nenhum risco de mudança | Perder melhorias de baixo custo e alto valor — já havíamos sofrido na prática o tipo de problema que uma dessas melhorias resolve (o workflow `/publish-github-planning` ficou sem documentação até ser corrigido manualmente) |
| **Adoção seletiva, gated pelo Modelo de Maturidade (escolhida)** | Aproveita o que tem alto valor/baixo custo sem violar o princípio de contexto mínimo; reaproveita um mecanismo que o framework já tinha (Níveis 0-4) em vez de inventar um novo | Exige julgamento contínuo sobre o que vale a pena importar a cada evolução de ferramentas como o spec-kit; risco de o passo condicional do `/code-review` ser esquecido em mudanças que deveriam tê-lo ativado |

## Consequências

- O ScrumAIDev permanece leve por padrão — times pequenos ou protótipos não pagam custo de rigor que não precisam.
- Times que precisam de mais rigor (Nível 2+) já têm caminho aberto usando construções que o próprio framework já oferece, sem depender de uma ferramenta externa.
- Esta decisão precisa ser revisitada se o ScrumAIDev algum dia mirar um público que exija suporte nativo a múltiplos agentes de IA com sintaxes diferentes, ou se a ambição mudar para um produto instalável — nesse cenário, CLI própria e adaptação multi-formato voltam a ser candidatas válidas.
- Novas práticas de baixo custo observadas em ferramentas como o spec-kit continuam sendo candidatas a importação seletiva, seguindo o mesmo critério usado aqui: custo de contexto vs. valor real, e preferência por mecanismos que o ScrumAIDev já possui.

## Nota de Atualização (0.1.0rc1)

A rejeição de "CLI própria instalável" registrada acima foi revisitada e parcialmente revertida. A partir da 0.1.0rc1, o ScrumAIDev passou a ser distribuído como uma CLI Python instalável (`scrumaidev config/doctor/uninstall`, ver `docs/distribution_architecture.md` e `RELEASE_NOTES_0.1.0rc1.md`), para permitir configurar projetos existentes sem exigir `git clone` do framework como base do projeto. Essa mudança resolveu um problema prático de reprodutibilidade/instalação e não foi motivada pelo mesmo objetivo do spec-kit (suporte nativo a dezenas de agentes de IA com sintaxes diferentes, marketplace de extensões). O restante da decisão original — rigor opcional escalonado pelo Modelo de Maturidade, em vez de spec-driven obrigatório — continua válido e não foi alterado.

## Rastreabilidade

- User Story: N/A
- Spec: N/A
- Contract: N/A
- BDD: N/A
- Nivel ScrumAIDev: 0 (decisão de processo/governança do próprio framework)
