# ScrumAIDev 0.1.0rc4

Release candidate que adiciona uma camada de entrada adaptativa (Work
Classification + Discovery + Requirements) ao ScrumAIDev, preenchendo uma
lacuna real: hoje `/create-user-story` parte direto de "descreva a
funcionalidade desejada", sem uma fase explícita de investigação do problema.

## Por que esta RC existe

Ao observar o AWS AI-DLC (AI-Driven Development Life Cycle) durante um
trabalho comparativo, identificamos que a fase de Ideation/Inception dele
resolve bem esse tipo de lacuna. Em vez de copiar a nomenclatura ou a
granularidade do AI-DLC, adaptamos os conceitos (que também não são
exclusivos do AI-DLC — Discovery e Requirements Analysis são vocabulário
padrão de BABOK/Design Thinking/RUP) ao vocabulário e à filosofia de
"rigor proporcional" que o ScrumAIDev já tinha.

O racional completo — incluindo por que optamos por `/scope-idea` em vez de
`/start`, e por que não existe um comando `/stories` separado — está
registrado em `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md`.

## Principais mudanças

- **`/scope-idea`** — nova entrada preferencial para ideia/mudança ainda não
  classificada. Recomenda LIGHT/NORMAL/HEAVY (com revisão humana obrigatória)
  e ativa `/discover` → `/requirements` → `/create-user-story` (Passo 0)
  somente quando a classificação exigir. Distinto de `/init-project`, que
  continua sendo o bootstrap único de um projeto novo.
- **`/discover`** — artefato compacto de Discovery (`docs/discovery/<slug>.md`),
  gate `PROBLEM READY`.
- **`/requirements`** — FR/BR/NFR com completeness scan em seis perspectivas
  (`docs/requirements/<slug>.md`), gate `REQUIREMENTS READY`.
- **`/create-user-story` — Passo 0 (Modo Backlog)** — em vez de um comando
  `/stories` separado, `/create-user-story` ganhou um passo condicional que
  materializa Requirements aprovados em um backlog INVEST pequeno + primeiro
  vertical slice, com seu próprio checkpoint de Review & Adjust.
- **`docs/work_classification.md`** — formaliza que LIGHT/NORMAL/HEAVY
  (quantidade de processo) é um eixo independente do Nível de Maturidade 0-4
  (rigor técnico).
- **`docs/discovery_requirements.md`** — modelo de operação de Discovery e
  Requirements, com seção explícita de inspiração externa.
- **`AGENTS.md`** — Regras Globais 17-21.
- **`docs/adr/ADR-002`** (só no repositório do framework, não instalado) —
  proveniência da ideia e racional de nomenclatura.

## Por que `/scope-idea` e não `/start`

- `/init-project` já é o "início" do ScrumAIDev (bootstrap de projeto). Um
  segundo comando chamado `/start` colidiria conceitualmente com ele.
- O próprio AI-DLC não usa `/start` — o comando dele é `/aidlc [scope]`. Um
  rascunho interno anterior havia usado `/start`, mas esse nome não tinha
  identidade própria nem vínculo real com o AI-DLC; foi só um nome genérico.
- `/scope-idea` comunica exatamente o que o comando faz (delimitar escopo de
  uma ideia) e não colide com nada que o ScrumAIDev já tinha.

## Por que não existe `/stories`

A materialização de backlog a partir de Requirements aprovados foi
incorporada como um passo condicional dentro de `/create-user-story` (que já
existia) em vez de um comando novo e paralelo. Isso evita duplicar
responsabilidade e mantém a superfície de comandos do ScrumAIDev menor.

## Acabamento pós-revisão

Ao revisar esta RC contra a discussão de design que a motivou, dois pontos
foram corrigidos:

- `docs/work_classification.md` agora reforça, nos fluxos NORMAL e HEAVY, a
  cadeia completa `agile delivery → engineering as needed → agentic
  execution` (já documentada em `docs/discovery_requirements.md`, mas antes
  não repetida aqui).
- `examples/agent-evolution/README.md` foi trazido como exemplo ilustrativo
  completo de `/scope-idea` no domínio do `agent-evolution-baseline`,
  atualizado para usar `/scope-idea` e o Passo 0 do `/create-user-story` em
  vez dos nomes `/start`/`/stories` do rascunho interno original.

## O que NÃO foi instalado em projetos derivados (por design)

- `docs/adr/ADR-002_discovery-requirements-inspirado-no-ai-dlc.md` — é
  documentação de proveniência do próprio framework, não do processo que um
  projeto derivado deve seguir (mesmo tratamento já dado ao ADR-001).

## Validação recomendada

1. `python -m pytest -q`.
2. `python scripts/check_agent_docs_sync.py` (confirmar `OK`).
3. Reconstruir o wheel e reinstalar (`uv tool install --force .`).
4. Configurar um projeto descartável com
   `scrumaidev config --harness opencode --pin 0.1.0rc4` e rodar `scrumaidev doctor`.
5. Confirmar que `.opencode/commands/scope-idea.md`, `discover.md` e
   `requirements.md` foram gerados automaticamente pelo adapter (não são
   arquivos estáticos — são derivados de `.agents/workflows/` em tempo de
   `scrumaidev config`).

## Compatibilidade

Mantém a mesma ressalva das RCs anteriores: identificadores internos com
prefixo `agileaidev_` foram preservados por compatibilidade. Nenhuma
`LICENSE` foi incluída nesta RC — a decisão de licença continua em aberto.
