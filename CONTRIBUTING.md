# 🤝 Guia de Contribuição — ScrumAIDev

Bem-vindo! Este guia explica como usar e contribuir com o framework.

Este processo é agnóstico de IDE, editor ou agente. Integrações específicas de ferramenta são opcionais e não substituem as regras canônicas do repositório.

---

## Usando o Framework em Seu Projeto

O ScrumAIDev é distribuído como uma CLI instalável — o repositório do framework não precisa ser clonado como base do seu projeto.

### 1. Instalar a CLI (uma única vez)

```bash
# a partir de um checkout do repositório ScrumAIDev
uv tool install .
# ou: .\installer\install.ps1 -Source .   (Windows)
# ou: ./installer/install.sh .            (Linux/macOS)
```

### 2. Configurar o seu projeto (novo ou existente)

```bash
cd /caminho/do/seu/projeto
scrumaidev config --harness opencode --pin 0.3.0   # ou: --harness codex | --harness claude
scrumaidev doctor
```

Isso instala `.agents/`, a projeção do harness (`.opencode/commands/`, `.agents/skills/scrumaidev-*` ou `.claude/`), `docs/`, `templates/` e `AGENTS.md` (ou uma bridge segura, se o projeto já tiver um `AGENTS.md` próprio). Veja `README.md#quick-start` para o passo a passo completo, incluindo `--dry-run` e `uninstall`.

### 3. Trazer uma ideia nova para o backlog

No chat do seu agente de IA:
```
/scope-idea Descreva sua ideia ou mudança aqui.
```

Para trabalho LIGHT PROCESS, isso executa direto. Para NORMAL/HEAVY PROCESS, `/scope-idea` ativa automaticamente `/discover` → `/requirements` → `/create-user-story` (Passo 0 — Modo Backlog) antes de propor Stories — sempre com revisão humana obrigatória em cada proposta. Veja `docs/discovery_requirements.md`.

Se a estrutura de pastas do projeto ainda não existir, rode `/init-project` primeiro.

### 4. Ou, partindo de um protótipo/código já existente

Adicione exemplos de design em `examples/figma/` (ZIPs do Figma, imagens, código legado) e execute:
```
/sprint-planning
```

---

## Fluxo de Trabalho Básico

```
/scope-idea → [/discover → /requirements] → /create-user-story → /sprint-planning → /feature-development → /code-review → /deploy → /sprint-retrospective
```

Esta é a mesma sequência do diagrama em `README.md#-o-ciclo-de-vida-ágil-com-ia` (versão em texto vs. versão em Mermaid); ao alterar uma, atualize a outra.

`/discover` e `/requirements` só entram para trabalho classificado como NORMAL/HEAVY PROCESS; para LIGHT PROCESS ou para uma Story já compreendida, `/create-user-story` pode ser usado diretamente.

Consulte `.agents/workflows/` para a lista versionada de workflows operacionais. O `README.md`, quando existir, é documentação humana e não substitui as fontes canônicas.

---

## Referências Canônicas

- `docs/engineering_playbook.md`: visão geral do processo.
- `docs/decisoes_governanca_us_spec_bdd.md`: regra canônica de US, Spec e BDD.
- `docs/git_workflow.md`: branch, commit, PR e merge.
- `docs/context.md`: comandos locais, paths e checks.
- `docs/definition_of_done.md`: critérios finais de conclusão.

---

## Configurar o Template de Commit

```bash
# Ativar o template de commit globalmente para este projeto
git config commit.template .gitmessage
```

---

## Autoria e Uso de IA

Este projeto incentiva o uso de agentes de IA para acelerar o trabalho, mas os créditos de autoria em `main` são sempre humanos.

- **Nunca use `Co-authored-by:`** para um agente de IA, em nenhum commit. Essa é a palavra-chave que o GitHub interpreta como coautoria — é ela que precisa ser evitada, não a menção à IA em si.
- **Registre a assistência de IA no commit final de squash-merge** usando um trailer não-padrão que o GitHub não interpreta como autoria: `Assisted-by: <agente> (model: <modelo>, <autonomous|supervised>)`. Exemplo: `Assisted-by: Claude Code (model: claude-sonnet-5, supervised)`. Isso preserva o registro de forma durável no `git log`/`git blame` de `main` — mais robusto do que depender só da descrição do Pull Request, que pode não sobreviver a uma migração de repositório ou ferramenta.
- A descrição do PR deve continuar detalhando o que a IA ajudou a fazer (contexto, não apenas o rótulo).
- **Responsabilidade:** quem abre ou aprova o PR é responsável pelo conteúdo integrado, revisado por um humano, independentemente da ferramenta usada para produzi-lo.
- Commits em branches de trabalho (antes do squash) podem conter qualquer anotação de IA sem problema — o que importa é a mensagem final que chega em `main`.

---

## Contribuindo com Melhorias no Framework

### Como contribuir

1. Fork o repositório
2. Sincronize a `main`
3. Crie uma branch curta seguindo `docs/git_workflow.md`
4. Faça suas alterações seguindo os padrões do repositório
5. Rode os checks documentados em `docs/context.md`
6. Commit com Conventional Commits e scope
7. Abra um Pull Request usando o template do repositório
8. Aguarde CI verde, aprovação e conversas resolvidas
9. Faça merge via `Squash & Merge`

### O que aceita contribuição

| Área | O que melhorar |
|---|---|
| `templates/` | Novos templates de artefatos ágeis |
| `.agents/workflows/` | Novos workflows ou aprimoramentos dos existentes |
| `.agents/skills/` | Novas personas ou refinamento das existentes |
| `examples/` | Exemplos concretos e preenchidos |
| `docs/` | Documentação do processo |

### Boas práticas para contribuições

- **Templates:** mantenha genéricos, sem referências a projetos específicos
- **Workflows:** prefira instruções curtas, com links para a fonte canônica, evitando boilerplate repetido
- **Skills:** siga o padrão `SKILL.md` com frontmatter YAML + seções `Capability` e `Exemplo`
- **Commits:** use Conventional Commits com scope, por exemplo `feat(api): ...` e `docs(repo): ...`

---

## Dúvidas?

Abra uma issue ou consulte as referências canônicas em `docs/` e `.agents/workflows/`.
