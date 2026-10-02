# ScrumAIDev - Analise do Repositorio e Guia para Novo Engenheiro

**Data da analise:** 2026-04-11  
**Repositorio analisado:** ScrumAIDev  
**Estado operacional observado:** pre-inicializacao, sem backlog e sem sprint ativa  
**Publico-alvo deste documento:** engenheiro de software que vai entender, manter e evoluir este framework

---

## 1. Resumo Executivo

Este repositorio serve como uma **infraestrutura de desenvolvimento assistido por IA para projetos ageis**. Ele nao e, no estado atual, um produto final de software com `frontend/`, `backend/` e `database/` implementados. Ele e um **framework/template operacional** que orienta agentes de IA e engenheiros humanos a transformar insumos de produto, especialmente ZIPs exportados do Figma, em backlog, user stories, sprints, specs, contratos, BDD, tasks, PRs e deploys rastreaveis.

O nome conceitual mais forte para o repositorio e **ScrumAIDev**: uma proposta de metodo em que a IA nao atua apenas como geradora de codigo, mas como participante governado de um ciclo Agile + Spec/Contract/BDD anchored.

Pontos mais fortes:

- Ha uma arquitetura de governanca clara: `AGENTS.md`, `docs/project_manifest.md`, `docs/token_budget.md`, workflows, skills e templates.
- O repositorio tem uma politica explicita de uso economico de contexto, evitando releituras e separando tarefas em `LIGHT CONTEXT`, `NORMAL CONTEXT` e `HEAVY CONTEXT`.
- O fluxo novo de Spec, Contract e BDD e bem pensado para evitar mudancas silenciosas de comportamento.
- A regra de Figma e muito relevante: se o ZIP trouxer frontend navegavel, a estrategia default passa a ser `copia_integral_frontend`, com paridade visual maxima.
- A integracao com GitHub Planning evita fonte dupla de verdade ao manter os artefatos locais como referencia canonica.

Pontos que precisavam de atencao no diagnostico inicial:

- O manifesto ainda marca o projeto como `UNDEFINED`, sem backlog e sem sprint ativa.
- Algumas referencias antigas foram identificadas e devem permanecer sob monitoramento por validador documental.
- Alguns workflows usavam caminhos divergentes; o refinamento posterior passou a padronizar sprint e retrospectiva em `docs/sprints/` e `docs/retrospectives/`.
- O CI pressupunha `Makefile`; o refinamento posterior passou a incluir um `Makefile` genérico baseado em detecção de capacidades reais da stack.
- As skills de dominio sao uteis, mas devem continuar sendo tratadas como `core` ou `adapter de stack`, conforme a tecnologia escolhida em cada projeto derivado.

---

## 2. Para Que Este Repositorio Serve

O ScrumAIDev serve para padronizar como uma equipe pequena ou media usa IA no ciclo de desenvolvimento de software, reduzindo tres riscos comuns:

| Risco | Como o repositorio tenta resolver |
|---|---|
| IA lendo contexto demais | `docs/token_budget.md`, `project_manifest.md`, `context_summary.md` e regras anti-releitura |
| IA alterando escopo sem controle | workflows, Touch List, Spec/Contract/BDD e branch rules |
| Planejamento se perdendo entre Markdown e GitHub | `docs/github_planning.md`, issue forms e `/publish-github-planning` |

Na pratica, ele e uma base para:

- iniciar projetos novos a partir de design Figma ou backlog manual;
- gerar backlog e user stories refinadas;
- planejar sprints e tasks tecnicas;
- decidir quando uma mudanca precisa de Spec governada, Contract e BDD;
- orientar agentes especializados por skills;
- conduzir code review, E2E, deploy e retrospectiva;
- publicar planejamento local no GitHub sem perder a fonte canonica local;
- controlar gasto de tokens da IA por tipo de trabalho.

---

## 3. Modelo Mental do Framework

O repositorio funciona em camadas:

| Camada | Pasta/arquivo | Funcao |
|---|---|---|
| Contrato operacional | `AGENTS.md` | Define regras do agente, ordem de leitura, branch, paths e saida obrigatoria |
| Estado do projeto | `docs/project_manifest.md` | Diz se o projeto esta inicializado, qual contexto foi processado e qual proximo passo seguir |
| Economia de contexto | `docs/token_budget.md` | Define quando usar leitura `LIGHT CONTEXT`, `NORMAL CONTEXT` ou `HEAVY CONTEXT` |
| Playbook | `docs/engineering_playbook.md` | Resume o processo de engenharia e governanca |
| Governanca tecnica | `docs/decisoes_governanca_us_spec_bdd.md`, `docs/contracts/`, `docs/bdd/`, `docs/specs/` | Ancora comportamento, contratos e testes de comportamento |
| Workflows de IA | `.agents/workflows/` | Executam processos por slash command, como `/sprint-planning` e `/feature-development` |
| Skills de IA | `.agents/skills/` | Dão papeis especializados ao agente |
| Templates | `templates/` | Modelos para backlog, US, sprint, tasks, DoD, PR, debug, postmortem etc. |
| Planejamento GitHub | `.github/` e `docs/github_planning.md` | Projeta backlog/sprint local em issues, labels, milestones e projects |
| Insumos de UI | `examples/figma/` | Recebe ZIPs, imagens e docs do Figma para gerar backlog ou copiar frontend |

---

## 4. Analise por Pasta

### Raiz do repositorio

| Item | Analise |
|---|---|
| `AGENTS.md` | E o contrato operacional principal. Esta forte: define precedencia, leitura minima, branch, paths convencionados, proibicao de reler README e regra de Figma. Deve continuar sendo tratado como fonte normativa. |
| `CONTRIBUTING.md` | Bom guia para contribuidores. Foi alinhado ao nome ScrumAIDev e deve continuar evitando tratar `README.md` como fonte operacional canonica. |
| `.gitignore` | Cobre dependencias, builds, segredos, Python, IDEs, `.codex` e `study/`. Bom para seguranca basica. Ha um detalhe: ele ignora `*.code-workspace`, mas existe `ScrumAIDev.code-workspace` no repositorio; vale confirmar se esse arquivo deve mesmo ser versionado. |
| `.editorconfig` | Simples e adequado. Padroniza LF, UTF-8, 2 espacos e tab para Makefile. |
| `.gitmessage` | Bom template de Conventional Commits com escopo, exemplo e footer. |
| `ScrumAIDev.code-workspace` | Apenas aponta o workspace para a raiz. Util para VS Code, mas opcional. |
| `.codex` | Arquivo vazio. Como tambem esta no `.gitignore`, parece resquicio local; pode ser removido se estiver versionado sem funcao. |

### `docs/`

| Documento | Analise |
|---|---|
| `project_manifest.md` | Fonte primaria de estado. Hoje indica `UNDEFINED`, contexto nao processado, sem sprint ativa e backlog nao gerado. Isso e coerente para um framework antes da inicializacao, mas precisa ser atualizado quando um produto real for criado. |
| `token_budget.md` | Muito importante. Define `LIGHT CONTEXT <2k`, `NORMAL CONTEXT <6k` e `HEAVY CONTEXT <12k` como guideline. A ideia e boa, mas para auditorias completas de repositorio, como esta, o custo real excede o HEAVY CONTEXT padrao. |
| `engineering_playbook.md` | Bom documento central: Agile + Spec-Anchored, trunk-based leve, PR pequeno, CI verde e sidecars com escopo. Tem forte valor metodologico. |
| `decisoes_governanca_us_spec_bdd.md` | Um dos melhores documentos do repo. Define quando usar Spec, Contract, BDD e Touch List. Ele transforma a IA em executor governado, nao apenas gerador livre. |
| `github_planning.md` | Excelente modelo em 3 niveis: Issues/Milestones, Project pessoal e Project organizacional. Evita fonte dupla de verdade e orienta assignee/team sem hardcode. |
| `context.md` | Centraliza paths, comandos e regras de delegacao. Foi ajustado para tratar checks por deteccao de capacidades reais da stack, sem depender de um campo de modo operacional herdavel. |
| `git_workflow.md` | Bom documento de branch, commit, PR e merge. Alinha com `AGENTS.md` e `engineering_playbook.md`. |
| `definition_of_done.md` | Forte e alinhado a Spec/Contract/BDD, comportamento, testes, PR, rollback e review. |
| `assumptions.md` | Simples e util para registrar suposicoes. Bom para evitar que a IA transforme duvidas em decisoes implicitas. |
| `todo.md` | Backlog tecnico operacional. Bom formato, ja inclui Spec, Contract e BDD. |

### `docs/contracts/`

| Documento | Analise |
|---|---|
| `contract_governance.md` | Define bem quando adotar contract-first por boundary. Ajuda a separar contrato externo de estrutura interna de banco. |
| `http_api_contract_template.yaml` | Bom template OpenAPI 3.1, com metadata de governanca e referencias a `error_standard.yaml`. |
| `error_standard.yaml` | Excelente padrao compartilhado de erro no estilo Problem Details. Ponto de melhoria: substituir exemplos com `example.com` por dominio placeholder do framework ou instrucao clara de troca. |

### `docs/specs/`

| Documento | Analise |
|---|---|
| `spec_template.md` | Template de Spec curta para tarefas que nao exigem Spec governada YAML. Bom escape hatch para evitar burocracia excessiva. |

### `docs/bdd/`

| Documento | Analise |
|---|---|
| `readme.md` | Define que BDD deriva da Spec e nao inventa regra nova. O template `docs/bdd/bdd_template.feature` foi adicionado no refinamento posterior. |

### `docs/adr/`

| Documento | Analise |
|---|---|
| `readme.md` | Bom guia para ADRs. Ainda nao ha ADR real. Seria util criar uma ADR inicial sobre a decisao Agile + Spec/Contract/BDD e outra sobre `copia_integral_frontend` para Figma. |

### `templates/`

| Template | Analise |
|---|---|
| `user_story.md` | Bem completo: narrativa, criterios, governanca, Spec, Contract, BDD, Touch List, testes e DoD. E um dos templates centrais. |
| `product_backlog.md` | Bom para epics, US, rastreabilidade tecnica, roadmap e refinement. |
| `sprint_planning.md` | Bom template, mas deve ser sempre usado em `docs/sprints/`, nao na raiz. |
| `task_breakdown.md` | Forte e alinhado a backend/frontend/testing/docs/devops, Spec, Contract, BDD e GitHub Task Issue. |
| `definition_of_done.md` | Bom template geral; bastante alinhado ao DoD canonico de `docs/definition_of_done.md`. |
| `pr_review_template.md` | Bom checklist pre-PR; complementa `.github/pull_request_template.md`. |
| `context_summary.md` | Importante para reduzir tokens em sessoes longas e handoffs com sidecars. |
| `debug_template.md` | Bom para investigacao segura de bugs, especialmente por instruir a nao alterar comportamento sem avisar. |
| `bug_report.md` | Util, mas mais generico e com emojis. Pode ser alinhado melhor a Spec/Contract/BDD e severidade operacional. |
| `daily_standup.md` | Funciona como template de cerimonia, mas ainda e generico. |
| `retrospective.md` | Bom material de retro, mas parte do conteudo ainda e mais Agile generico do que ScrumAIDev especifico. |
| `postmortem.md` | Completo e util para incidentes, mas pode ser conectado melhor a ADRs, rollback e contratos. |

### `.agents/workflows/`

| Workflow | Analise |
|---|---|
| `init-project.md` | Muito relevante como gateway. Reconhece estados, prioriza Figma e impede acoes prematuras. Bom desenho. |
| `sprint-planning.md` | Bom fluxo. Foi ajustado para reforcar `docs/sprints/sprint_planning_NN.md`. |
| `create-user-story.md` | Forte para refinement, inclui INVEST, paridade Figma, Spec, Contract, testes e backlog. Ponto de melhoria: garantir sempre `docs/stories/`. |
| `feature-development.md` | O workflow mais maduro. Checa GitHub planning, delegacao segura, Figma, governanca, branch/worktree, tasks, testes, PR e DoD. |
| `publish-github-planning.md` | Muito bom. Mantem agente principal como single writer e publica backlog+sprint em duas fases internas. |
| `code-review.md` | Completo para arquitetura, qualidade, performance, seguranca, erro, testes, docs e DoD. |
| `e2e-test.md` | Bom ponto de partida para Playwright, mas tem marcadores `// turbo`, comandos que podem instalar dependencias e foco especifico em Vite/localhost. Deve virar mais agnostico por stack. |
| `deploy.md` | Util, mas tem exemplos muito especificos de dashboard, chat estrategico, FastAPI e servidores. Precisa ser dividido por stack ou virar checklist abstrato. |
| `sprint-retrospective.md` | Bom ritual. Foi ajustado para usar `docs/retrospectives/`. |
| `integrate-backend.md` | Boa ideia para legados, mas ainda curto. Poderia integrar Spec/Contract, risco de dados, estrategia de migracao e seguranca. |

### `.agents/skills/`

| Skill | Analise |
|---|---|
| `architect` | Boa skill para decisoes macro e trade-offs. Pode ganhar referencias diretas a ADR, Spec e Contract. |
| `technical-writer` | Boa para guias e documentos de onboarding. Foi a skill mais adequada para este relatorio. |
| `backend-python` | Util para FastAPI/Django/Postgres/Neo4j. Foi ajustada para se apresentar como adapter de stack e evitar senha literal no exemplo demonstrativo. |
| `react-expert` | Relevante porque o ZIP do Figma atual e React/Vite. Foi ajustada para reforcar `copia_integral_frontend` quando o ZIP trouxer app navegavel. |
| `frontend-vue` | Boa para projetos Vue, embora o insumo atual seja React. |
| `qa-engineer` | Boa skill de testes e edge cases. Foi ajustada para considerar Contract, BDD e DoD. |
| `security-expert` | Boa base OWASP, segredos e threat modeling. Foi conectada ao `error_standard.yaml`. |
| `story-refiner` | Boa intencao e foi atualizada para `docs/stories/`. |
| `skill-creator` | Poderosa para criar e medir skills, com scripts e viewer. Foi marcada como ferramenta auxiliar opcional e nao como fluxo automatico obrigatorio. |

### `.agents/rules/`

| Documento | Analise |
|---|---|
| `coding-standards.md` | Bom baseline cross-stack. Foi ajustado para lembrar Spec, Contract, BDD e `error_standard.yaml` quando aplicavel. |

### `.github/`

| Arquivo | Analise |
|---|---|
| `pull_request_template.md` | Bom e enxuto, mas poderia linkar explicitamente Spec, Contract e BDD como no template de PR dos workflows. |
| `ISSUE_TEMPLATE/epic.yml` | Bom fallback manual para Epic, sem assignee hardcoded. |
| `ISSUE_TEMPLATE/user-story.yml` | Bom fallback manual para US, inclui behavior change e artefatos locais. |
| `ISSUE_TEMPLATE/task.yml` | Bom fallback para task, mantendo `docs/tasks/breakdown_US-XXX.md` como fonte canonica. |
| `workflows/ci.yml` | Foi ajustado para deteccao de capacidades reais (`frontend/`, `backend/`, Docker) e para usar o `Makefile` generico sem depender de um modo operacional herdavel. |
| `workflows/close-milestone.yml` | Boa automacao: le defaults do manifesto e so gerencia milestones com prefixo opt-in (`Sprint:`). |

### `examples/figma/`

| Item | Analise |
|---|---|
| `MeetingFlow-MPI.zip` | ZIP importante: contem app React/Vite navegavel com `package.json`, `src/`, rotas, paginas, componentes, tema e mock data. Pelo contrato atual, e fonte primaria para UI e deve levar a `copia_integral_frontend` em projetos baseados nele. |
| `readme.md` | Guia util para analise automatica de exemplos. Foi atualizado para `MeetingFlow-MPI.zip`, `.agents/` e fontes canonicas operacionais. |
| `.gitkeep` | Mantem a pasta versionada. |

O ZIP `MeetingFlow-MPI.zip` descreve uma aplicacao para gestao de reunioes regionais com participantes, regioes, upload de video/audio/texto/fotos, processamento, atas, relatorios e configuracoes. As rotas identificadas incluem dashboard, regioes, participantes, cadastro de participante, reunioes, cadastro de reuniao, processamento, presenca, visualizacao de reuniao, atas, relatorios e configuracoes.

---

## 5. O Que Esta Bom

1. **Governanca forte para IA.** O repositorio nao deixa o agente operar em modo livre; ele define ordem de leitura, minimo contexto, branch, paths, templates, workflows e saida auditavel.
2. **Controle de contexto e tokens.** A divisao `LIGHT CONTEXT`, `NORMAL CONTEXT` e `HEAVY CONTEXT` e um diferencial real para execucao economica.
3. **Figma como insumo serio, nao decorativo.** A regra de `copia_integral_frontend` evita recriacao ruim ou perda de paridade visual quando o ZIP ja traz um app funcional.
4. **Spec/Contract/BDD reduzem ambiguidade.** Isso ajuda a transformar mudancas em artefatos verificaveis e evita regressao silenciosa.
5. **Planejamento GitHub bem modelado.** A ideia de projetar o planejamento local no GitHub, sem tornar o GitHub fonte primaria, e madura.
6. **Delegacao com single writer.** O modelo de agente principal + sidecars evita conflitos em artefatos canonicos.
7. **Boa base para artigo.** O repositorio ja expressa uma tese: IA produtiva precisa de governanca, economia de contexto e artefatos rastreaveis.

---

## 6. O Que Pode Melhorar

### Melhorias de baixo custo

| Melhoria | Impacto | Custo estimado em tokens |
|---|---|---|
| Manter validador documental para referencias antigas | Alto para onboarding | `LIGHT CONTEXT` a `NORMAL CONTEXT` |
| Monitorar links `.agent` vs `.agents` | Alto para navegabilidade | `LIGHT CONTEXT` |
| Validar continuamente caminhos `docs/sprints/` e `docs/retrospectives/` | Alto para consistencia | `NORMAL CONTEXT` |
| Expandir `docs/bdd/bdd_template.feature` com exemplos reais por projeto | Medio | `LIGHT CONTEXT` |
| Manter `story-refiner` alinhada a `docs/stories/` | Medio | `LIGHT CONTEXT` |

### Melhorias de medio custo

| Melhoria | Impacto | Custo estimado em tokens |
|---|---|---|
| Criar um `Makefile` template com gates que passam em modo template | Alto para CI | `NORMAL CONTEXT` |
| Harmonizar `deploy.md`, `e2e-test.md` e `integrate-backend.md` com Spec/Contract/BDD | Alto | `NORMAL CONTEXT` a `HEAVY CONTEXT` |
| Criar ADRs iniciais sobre ScrumAIDev, Figma-first e Spec/Contract/BDD | Alto para pesquisa/artigo | `NORMAL CONTEXT` |
| Adicionar templates faltantes para Spec YAML governada e BDD | Alto para execucao real | `NORMAL CONTEXT` |
| Criar um `docs/retrospectives/` e documentar a convencao | Medio | `LIGHT CONTEXT` |

### Melhorias de alto custo

| Melhoria | Impacto | Custo estimado em tokens |
|---|---|---|
| Inicializar um produto real a partir de `MeetingFlow-MPI.zip` | Muito alto | `HEAVY+ CONTEXT` |
| Extrair todo o frontend do ZIP para `frontend/` e estabilizar dependencias | Muito alto | `HEAVY+ CONTEXT` |
| Gerar backlog completo, sprints, stories, tasks, specs e contratos para MeetingFlow | Muito alto | `HEAVY+ CONTEXT` |
| Criar suite de validadores automatizados para docs, links, paths e contratos | Alto | `HEAVY CONTEXT` |
| Adaptar `skill-creator` para terminologia e ferramentas ScrumAIDev | Medio/alto | `HEAVY CONTEXT` |

---

## 7. Analise de Gasto de Tokens para Projetos com IA

O `docs/token_budget.md` define:

| Modo | Uso esperado | Estimativa do repo |
|---|---|---|
| `LIGHT CONTEXT` | Tarefa simples e bem definida | < 2k tokens |
| `NORMAL CONTEXT` | Desenvolvimento padrao de US ou feature | < 6k tokens |
| `HEAVY CONTEXT` | Planejamento ou decisao transversal | < 12k tokens |

Na pratica, para projetos reais usando este framework:

| Cenario | Contexto minimo recomendado | Custo provavel |
|---|---|---|
| Corrigir um bug pequeno | Manifesto + arquivo afetado + talvez story | `LIGHT CONTEXT` |
| Criar uma user story | Manifesto + workflow + template + backlog | `NORMAL CONTEXT` |
| Implementar uma US | Manifesto + sprint + story + breakdown + coding standards + arquivos de codigo | `NORMAL CONTEXT` a `HEAVY CONTEXT` |
| Planejar sprint sem Figma | Manifesto + backlog + ultima sprint + templates | `HEAVY CONTEXT` |
| Planejar sprint com ZIP Figma funcional | Manifesto + Figma ZIP + backlog + templates + workflows | `HEAVY+ CONTEXT` |
| Copiar e integrar frontend do ZIP | ZIP + frontend alvo + CI + dependencias + testes | `HEAVY+ CONTEXT` |
| Auditoria completa do framework | Quase todos os documentos e workflows | `HEAVY+ CONTEXT`, acima da guideline de 12k |

Minha recomendacao e adicionar uma categoria explicita:

```text
ULTRA — auditoria de framework, migracao de produto, copia integral de frontend, ou geracao completa de backlog a partir de ZIP funcional.
Arquivos: > 12
Tokens estimados: 20k-60k+, dependendo do tamanho do ZIP/codigo.
Obrigatorio: gerar context_summary.md ao final para reduzir custo das proximas rodadas.
```

Isso nao enfraquece o `HEAVY CONTEXT`; apenas reconhece que algumas tarefas de framework excedem o planejamento transversal normal.

---

## 8. Proposicao de Artigo: ScrumAIDev

### Titulo sugerido

**ScrumAIDev: um framework de governanca, economia de contexto e rastreabilidade para desenvolvimento agil assistido por IA**

### Tese

O uso eficiente de IA em engenharia de software nao depende apenas de modelos melhores. Depende de um sistema operacional de engenharia que diga **o que a IA deve ler, quando deve parar de ler, onde pode escrever, como deve justificar mudancas e como deve preservar rastreabilidade entre necessidade de negocio, comportamento, contrato e implementacao**.

### Contribuicoes do artigo

| Contribuicao | Evidencia no repositorio |
|---|---|
| Economia de contexto como disciplina | `docs/token_budget.md`, `templates/context_summary.md`, regras anti-releitura |
| IA como participante governado | `AGENTS.md`, branch rules, workflow gates |
| Agile + Spec/Contract/BDD | `docs/decisoes_governanca_us_spec_bdd.md`, `docs/contracts/`, `docs/bdd/` |
| Design-to-backlog / Design-to-frontend | `examples/figma/`, `copia_integral_frontend` |
| Planejamento local projetado no GitHub | `docs/github_planning.md`, issue forms e workflow de milestone |
| Delegacao segura entre agentes | sidecars, single writer e write scope |

### Estrutura sugerida do artigo

1. **Introducao:** o problema da IA que codifica rapido, mas perde contexto, escopo e rastreabilidade.
2. **Trabalhos relacionados:** Agile, BDD, contract-first, ADR, trunk-based development e AI-assisted software engineering.
3. **Metodo ScrumAIDev:** camadas do framework, contrato operacional, token budget, workflows e skills.
4. **Governanca de comportamento:** Spec, Contract, BDD, Touch List e Definition of Done.
5. **Figma-first com paridade visual:** quando copiar integralmente o frontend exportado e quando adaptar.
6. **GitHub como projecao operacional:** backlog local como fonte primaria, issues como camada de execucao.
7. **Economia de tokens:** modos LIGHT/NORMAL/HEAVY CONTEXT e proposta ULTRA.
8. **Estudo de caso:** MeetingFlow-MPI.zip como insumo de app React/Vite para gerar backlog e sprint inicial.
9. **Riscos e limitacoes:** documentos desatualizados, necessidade de validadores, dependencia de disciplina humana.
10. **Conclusao:** IA produtiva exige processo, artefatos e limites operacionais.

### Possivel pergunta de pesquisa

> Como um framework de artefatos locais, workflows de IA e politicas de leitura minima pode reduzir custo de contexto, retrabalho e regressao comportamental em projetos ageis assistidos por IA?

---

## 9. Guia Rapido para o Novo Engenheiro

Se voce esta chegando agora, leia nesta ordem:

1. `docs/project_manifest.md` para entender o estado atual.
2. `AGENTS.md` para entender como agentes devem operar.
3. `docs/token_budget.md` para entender custo de contexto.
4. `docs/engineering_playbook.md` para entender o processo macro.
5. `docs/decisoes_governanca_us_spec_bdd.md` para entender quando criar Spec, Contract e BDD.
6. `docs/github_planning.md` se o trabalho envolver Issues, Projects ou Milestones.
7. O workflow especifico em `.agents/workflows/` apenas quando for executar aquele processo.

Nao use o `README.md` como fonte operacional do agente. Ele pode ser util para humanos, mas as regras do repositorio dizem que a IA deve operar a partir do manifesto, AGENTS e docs canonicos.

### Fluxo esperado de um projeto novo

1. Rodar `/init-project` para diagnosticar o estado.
2. Se houver ZIP em `examples/figma/`, tratar como fonte primaria de contexto.
3. Se o ZIP tiver frontend funcional, registrar `copia_integral_frontend`.
4. Rodar `/sprint-planning` para gerar ou revisar backlog e sprint.
5. Publicar planejamento no GitHub com `/publish-github-planning`.
6. Desenvolver stories com `/feature-development`.
7. Revisar com `/code-review`.
8. Validar E2E quando houver UI ou fluxo critico.
9. Deploy somente apos DoD e CI verde.
10. Fechar ciclo com retrospectiva.

### Regra de ouro

Nunca deixe a IA alterar escopo ou comportamento sem artefato rastreavel. Se a mudanca impacta comportamento observavel, API, regra de negocio, seguranca, contrato ou UI relevante, ela precisa passar pela decisao de Spec/Contract/BDD ou registrar dispensa explicita.

---

## 10. Proximas Funcionalidades Recomendadas para o Framework

1. **Validador de consistencia documental:** detectar links quebrados, paths fora do padrao, referencias operacionais a documentacao humana e exemplos obsoletos.
2. **Modo `ULTRA` no token budget:** formalizar auditoria e migracao de ZIP funcional.
3. **Bootstrap de projeto real:** criar `Makefile`, `docs/sprints/`, `docs/stories/`, `docs/tasks/`, `docs/retrospectives/` e placeholders seguros.
4. **Template de Spec YAML governada:** hoje existe Spec curta em Markdown, mas falta um template YAML canonico completo.
5. **Template BDD `.feature`:** criar o arquivo referenciado por `docs/bdd/readme.md`.
6. **ADR inicial do framework:** registrar decisoes centrais para sustentar o artigo e futuras evolucoes.
7. **Refatoracao de workflows genericos:** harmonizar deploy, E2E e retrospective com os paths e artefatos canonicos atuais.
8. **Skill de ScrumAIDev Coach:** uma skill especializada em aplicar este proprio framework, reduzindo necessidade de ler muitos docs.
9. **Pipeline de extracao Figma:** script para listar conteudo do ZIP, identificar rotas/componentes e gerar um resumo de contexto reutilizavel.
10. **Relatorio de custo de IA por sprint:** usar `context_summary.md` e logs de execucao para estimar tokens gastos por tipo de atividade.

---

## 11. Veredito Critico

O repositorio esta em um bom caminho e tem potencial real como framework reutilizavel para desenvolvimento agil assistido por IA. A parte conceitual mais madura e a combinacao de **contrato operacional do agente + token budget + Spec/Contract/BDD + Figma-first + GitHub Planning local-first**.

O maior risco atual nao e falta de ideias; e **inconsistencia residual**. Ha documentos antigos, caminhos divergentes e exemplos de outros dominios que podem confundir um agente ou um engenheiro novo. Antes de usar em outro projeto, eu faria uma sprint curta de hardening documental e automatizaria validacoes simples.

Se a intencao for escrever o artigo ScrumAIDev, este repositorio ja oferece material suficiente para uma versao inicial. Para fortalecer a publicacao, recomendo criar um estudo de caso com o `MeetingFlow-MPI.zip`: gerar backlog, planejar sprint 01, copiar o frontend integralmente e medir o custo de tokens antes/depois de usar `context_summary.md`.

---

## 12. Consumo de Contexto (Estimado)

- **Modo:** `HEAVY+ CONTEXT`
- **Estimativa:** acima da guideline padrao de `HEAVY CONTEXT` (~12k tokens), porque esta tarefa pediu analise ampla de pastas, documentos, workflows, skills, GitHub automation e ZIP de Figma.
- **Justificativa:** foram lidos documentos canonicos, templates, workflows, skills principais, configuracoes GitHub, metadados do ZIP e trechos representativos do app Figma exportado.
- **Otimizacao aplicada:** nao foi lido o `README.md` operacionalmente; o ZIP foi analisado por listagem e trechos-chave, sem extrair todos os 90 arquivos para o contexto.

## 13. Arquivos Utilizados

### Arquivos lidos para contexto

- `docs/project_manifest.md`
- `AGENTS.md`
- `docs/token_budget.md`
- `CONTRIBUTING.md`
- `docs/engineering_playbook.md`
- `docs/context.md`
- `docs/decisoes_governanca_us_spec_bdd.md`
- `docs/github_planning.md`
- `docs/git_workflow.md`
- `docs/definition_of_done.md`
- `docs/assumptions.md`
- `docs/todo.md`
- `docs/adr/readme.md`
- `docs/bdd/readme.md`
- `docs/specs/spec_template.md`
- `docs/contracts/contract_governance.md`
- `docs/contracts/error_standard.yaml`
- `docs/contracts/http_api_contract_template.yaml`
- `examples/figma/readme.md`
- `templates/user_story.md`
- `templates/product_backlog.md`
- `templates/sprint_planning.md`
- `templates/task_breakdown.md`
- `templates/definition_of_done.md`
- `templates/pr_review_template.md`
- `templates/bug_report.md`
- `templates/debug_template.md`
- `templates/context_summary.md`
- `templates/daily_standup.md`
- `templates/retrospective.md`
- `templates/postmortem.md`
- `.agents/workflows/init-project.md`
- `.agents/workflows/sprint-planning.md`
- `.agents/workflows/create-user-story.md`
- `.agents/workflows/feature-development.md`
- `.agents/workflows/code-review.md`
- `.agents/workflows/e2e-test.md`
- `.agents/workflows/publish-github-planning.md`
- `.agents/workflows/deploy.md`
- `.agents/workflows/sprint-retrospective.md`
- `.agents/workflows/integrate-backend.md`
- `.agents/skills/architect/SKILL.md`
- `.agents/skills/technical-writer/SKILL.md`
- `.agents/skills/qa-engineer/SKILL.md`
- `.agents/skills/story-refiner/SKILL.md`
- `.agents/skills/frontend-vue/SKILL.md`
- `.agents/skills/react-expert/SKILL.md`
- `.agents/skills/backend-python/SKILL.md`
- `.agents/skills/security-expert/SKILL.md`
- `.agents/skills/skill-creator/SKILL.md`
- `.agents/skills/skill-creator/references/schemas.md`
- `.agents/skills/skill-creator/agents/analyzer.md`
- `.agents/skills/skill-creator/agents/grader.md`
- `.agents/skills/skill-creator/agents/comparator.md`
- `.agents/rules/coding-standards.md`
- `.github/pull_request_template.md`
- `.github/ISSUE_TEMPLATE/epic.yml`
- `.github/ISSUE_TEMPLATE/user-story.yml`
- `.github/ISSUE_TEMPLATE/task.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/close-milestone.yml`
- `.gitignore`
- `.editorconfig`
- `.gitmessage`
- `ScrumAIDev.code-workspace`
- `.codex`

### Leitura parcial relevante

- `examples/figma/MeetingFlow-MPI.zip`: listagem do ZIP, `package.json`, `src/app/routes.tsx`, `src/app/App.tsx`, `src/imports/pasted_text/meeting-management-design.md`, `supabase/functions/server/index.tsx` e `src/app/data/mockData.ts`.

### Arquivos criados

- `docs/agileaidev_engineer_onboarding.md`

### Arquivos alterados

- `docs/agileaidev_engineer_onboarding.md`
