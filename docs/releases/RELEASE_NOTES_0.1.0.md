# ScrumAIDev 0.1.0

Primeira versão estável do ScrumAIDev instalável, promovendo a linha
0.1.0rc4 depois de três RCs de restauração de governança, adição de
Work Classification/Discovery/Requirements e limpeza de consistência.
Nenhum comportamento de runtime mudou além do listado abaixo — esta é
principalmente uma promoção de versão e uma decisão de licenciamento,
mais um bug real encontrado e corrigido durante o smoke test final.

## Por que promover agora

As três RCs anteriores fecharam, em sequência: conteúdo de governança que
havia sido perdido no empacotamento inicial da CLI (rc3), a camada de
entrada adaptativa Work Classification/Discovery/Requirements (rc4), e uma
auditoria de consistência de documentação/nomenclatura (rc4, continuação).
A suíte de testes está verde, `scripts/check_agent_docs_sync.py` não aponta
divergência, e não há mais item pendente das rodadas de auditoria. O
critério de promoção — `docs/release_checklist.md` — foi executado
integralmente contra um wheel construído a partir deste commit.

## Licença

Adicionado `LICENSE`: um aviso interino e restritivo de "todos os direitos
reservados / uso autorizado apenas". A equipe ainda não decidiu uma licença
definitiva; em vez de deixar essa decisão em aberto indefinidamente (como
nas RCs anteriores), este release torna o padrão explícito:

- Uso permitido sem autorização adicional: avaliação, uso pessoal, pesquisa
  não comercial (incluindo pesquisa acadêmica).
- Uso que requer autorização por escrito do titular dos direitos:
  redistribuição, sublicenciamento, publicação de trabalhos derivados, e
  qualquer uso comercial.
- Software fornecido "como está", sem garantias.

Isso substitui a ausência de licença (que nunca implicou uso irrestrito) por
um padrão explícito, e será substituído quando a equipe decidir uma licença
definitiva (provavelmente uma licença open source aprovada pela OSI).
Refletido em `pyproject.toml` (`license = {file = "LICENSE"}` +
classificador `License :: Other/Proprietary License`) e linkado em
`README.md`. `REPOSITORY_SETUP.md` foi atualizado para não mais afirmar que
o pacote "não presume uma licença".

## Bug encontrado e corrigido durante o smoke test

`scrumaidev uninstall` removia todos os arquivos gerenciados, mas deixava
para trás uma árvore de diretórios vazios sob `.agents/skills/<nome>/...`,
porque a limpeza final varria uma lista fixa e achatada de caminhos (incluía
`.agents/skills`, mas nenhuma das subpastas por skill). Encontrado ao rodar
o smoke test de um wheel recém-construído em um venv limpo, contra um
projeto descartável. Corrigido substituindo a lista fixa por uma varredura
bottom-up de cada raiz gerenciada (`.agents`, `.opencode`, `.scrumaidev`)
via `os.walk(topdown=False)`: `rmdir` só é bem-sucedido em um diretório
genuinamente vazio, então qualquer arquivo que o usuário tenha adicionado em
qualquer ponto da árvore continua protegendo aquele ramo (e seus pais) de
remoção. Dois testes novos em `tests_cli/test_cli_runtime.py` cobrem o caso
corrigido e o caso de preservação.

## Outra correção não relacionada, encontrada de passagem

`build/` e `src/scrumaidev.egg-info/` estavam rastreados no Git desde o
início do histórico do projeto, apesar de serem artefatos de build puros,
regenerados por `pip wheel`/`setuptools`. Removidos do rastreamento e
adicionados ao `.gitignore` (ao lado da entrada `dist/` já existente).

## Versão

`0.1.0rc4` → `0.1.0` em `pyproject.toml`, `src/scrumaidev/__init__.py`,
`installer/install.ps1`, `installer/install.sh`, e em todos os
exemplos/pins de documentação (`README.md`, `CONTRIBUTING.md`,
`REPOSITORY_SETUP.md`). `tests_cli/test_version_consistency.py` garante que
as quatro declarações autoritativas concordem entre si a partir de agora.

## Validação executada (não apenas recomendada)

Checklist de `docs/release_checklist.md`, rodado contra um wheel construído
a partir deste commit, instalado em um venv limpo (não o ambiente de
desenvolvimento) e exercitado contra diretórios de projeto descartáveis:

- [x] `python -m pytest -q` — 20/20 passou.
- [x] `python -m unittest scripts.test_agileaidev_gate scripts.test_check_agent_docs_sync` — 35/35 passou.
- [x] Wheel construído sem `__pycache__`, `.pyc`, `examples/`, ou conteúdo
      maintainer-only (onboarding/ADR/scripts de CI) — 96 arquivos no payload.
- [x] `scrumaidev config --harness opencode --pin 0.1.0` em projeto limpo —
      `status: ok`.
- [x] `scrumaidev doctor` — `status: ok`, sem erros/avisos.
- [x] OpenCode descobre os 13 comandos slash (um adapter por workflow),
      nenhum sobrescreve o modelo da sessão ativa.
- [x] `AGENTS.md` pré-existente no projeto alvo recebe bridge delimitada
      (`<!-- scrumaidev:start -->`), conteúdo original preservado.
- [x] `scrumaidev uninstall` preserva artefato seed editado
      (`docs/context.md`) e remove por completo `.agents/`, `.opencode/` e
      `.scrumaidev/` (ver correção acima).
- [x] Sequência completa re-executada após a correção do uninstall, contra
      o wheel reconstruído, para confirmar que a correção resolve o achado
      de ponta a ponta.

## O que NÃO foi feito nesta promoção (deliberadamente)

- Nenhuma tag Git ou push foi criado. Criar `v0.1.0` e publicar a release
  (que dispara `.github/workflows/cli-release.yml` e o registro de hashes
  SHA256) é uma ação com efeito em sistemas compartilhados e fica a critério
  da equipe, como um passo separado e deliberado.
- Nenhum conteúdo de LICENSE ou de versão foi incorporado ao payload de
  runtime instalado em projetos configurados — as mudanças de licença e
  versão são metadados do próprio repositório do framework.

## Compatibilidade

Mantém a mesma ressalva das RCs anteriores: identificadores internos com
prefixo `agileaidev_` foram preservados por compatibilidade.
