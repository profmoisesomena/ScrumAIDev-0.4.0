# ScrumAIDev 0.1.0rc3

Release candidate que reconcilia o pacote instalável (0.1.0rc1/rc2) com um snapshot
mais recente do framework-fonte (`AgileAIDev_review`, distribuído como repositório
clonável antes da CLI), que continha regras de governança, passos de workflow e
autotestes ausentes do pacote CLI.

## Por que esta RC existe

O empacotamento em CLI (0.1.0rc1) partiu de um snapshot do framework anterior à
adição das Regras 14-16 do `AGENTS.md`, do mecanismo de clarificação
`[PRECISA CLARIFICAR]`, da checagem de consistência entre artefatos no
`/code-review` e de outros itens de governança. Rodar o experimento comparativo
ScrumAIDev × AWS AI-DLC contra essa versão incompleta enfraqueceria a validade da
comparação — dois dos pontos identificados como fracos do ScrumAIDev frente ao
AI-DLC/Spec Kit (clarificação formal e verificação cruzada de artefatos) já
existiam no próprio framework e haviam sido perdidos no empacotamento.

## Principais mudanças

- `AGENTS.md` — Regras Globais 14, 15 e 16 restauradas (autoria de IA em commits,
  marcador `[PRECISA CLARIFICAR]`, `docs/templates_overrides/`), com índice de
  documentos de governança e log de mudanças de governança. Propagado ao payload
  instalável (`.scrumaidev/AGENTS.md` nos projetos configurados).
- `/code-review`: Passo 0 condicional de checagem de consistência entre
  US/Sprint/Spec/Contract/BDD.
- `/create-user-story` + `templates/user_story.md`: passo/subseção explícitos de
  "Pontos de Esclarecimento".
- `/feature-development` + `templates/task_breakdown.md`: "Checagem de
  Princípios" condicional (simplicidade, dependências novas, Touch List).
- `docs/decisoes_governanca_us_spec_bdd.md`: modelo de persistência de User
  Stories (`Done` = histórico congelado).
- `docs/adr/ADR-001_governanca-opcional-vs-spec-driven.md` restaurado, com nota
  de atualização reconciliando com a decisão de distribuir uma CLI instalável.
- `CONTRIBUTING.md` e `.github/pull_request_template.md`: seção/checklist de
  "Uso de IA" (apenas no repositório do framework, não instalado).
- `scripts/check_agent_docs_sync.py` + testes (`test_agileaidev_gate.py`,
  `test_check_agent_docs_sync.py`) e job `framework-tests` no `ci.yml` (apenas
  no repositório do framework, não instalado).

## O que NÃO foi instalado em projetos derivados (correto, por design)

Itens abaixo existem apenas no repositório do ScrumAIDev, nunca em
`src/scrumaidev/runtime/core/`, porque descrevem o próprio framework, não o
processo que um projeto derivado deve seguir:

- `docs/adr/ADR-001...`, `CONTRIBUTING.md`, `.github/*`
- `scripts/check_agent_docs_sync.py` e seus testes
- A seção "Testes do Próprio Framework" de `docs/context.md` (o payload
  instalado mantém apenas a numeração original de seções, sem essa seção)

## Licença — deliberadamente adiada

Esta RC não inclui um arquivo `LICENSE`. A escolha da licença ainda está em
discussão com a equipe; `REPOSITORY_SETUP.md` já registra que o pacote não
presume uma licença para o projeto. Adicionar isso fica para uma RC futura,
quando a decisão estiver tomada.

## Validação recomendada antes de promover/rodar o experimento

1. Executar `python -m pytest -q` (testes da CLI) em Windows.
2. Executar `python -m unittest scripts.test_agileaidev_gate -v` e
   `python -m unittest scripts.test_check_agent_docs_sync -v`.
3. Executar `python scripts/check_agent_docs_sync.py` e confirmar `OK`.
4. Reconstruir o wheel e reinstalar (`uv tool install --force .`).
5. Configurar um projeto descartável com
   `scrumaidev config --harness opencode --pin 0.1.0rc3` e rodar `scrumaidev doctor`.
6. Confirmar que `.scrumaidev/AGENTS.md` do projeto configurado contém as
   Regras 14-16.
7. Só então recriar `START_SCRUMAIDEV_R1` no experimento comparativo.

## Compatibilidade

Mantém a mesma ressalva da 0.1.0rc2: identificadores internos com prefixo
`agileaidev_` (`scripts/agileaidev_gate.py`, `agileaidev_level`) foram
preservados por compatibilidade e devem ser tratados em uma migração de
nomenclatura separada antes de uma versão estável.
