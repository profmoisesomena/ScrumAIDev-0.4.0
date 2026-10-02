# Publicar o ScrumAIDev em um novo repositório GitHub

Este pacote corresponde à primeira versão estável (`0.1.0`) do ScrumAIDev instalável.

## 1. Criar o repositório

Crie um repositório vazio no GitHub, sem README, `.gitignore` ou licença automática.

> Este pacote inclui um `LICENSE` interino e restritivo (uso autorizado apenas — ver o arquivo na raiz), enquanto a equipe não define uma licença definitiva. Antes de tornar o repositório público, revise `LICENSE` e substitua-o quando a decisão de licenciamento for tomada.

## 2. Inicializar o Git local

Na raiz deste pacote:

```powershell
git init
git add .
git commit -m "feat: ScrumAIDev installable 0.1.0"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

## 3. Validar antes da tag

```powershell
python -m pytest -q
python -m pip wheel . --no-deps -w dist
```

Teste a instalação local:

```powershell
.\installer\install.ps1 -Source .
scrumaidev version
```

Em um projeto de teste:

```powershell
scrumaidev config --harness opencode --pin 0.3.0 --dry-run
scrumaidev config --harness opencode --pin 0.3.0
scrumaidev doctor
```

## 4. Criar a release candidate

```powershell
git tag -a v0.1.0 -m "ScrumAIDev 0.1.0"
git push origin v0.1.0
```

A workflow `.github/workflows/cli-release.yml` construirá o wheel e anexará à GitHub Release:

- `scrumaidev-0.1.0-py3-none-any.whl`
- `install.ps1`
- `install.sh`
- `SHA256SUMS.txt`

## 5. Estrutura da distribuição

O repositório contém o código-fonte completo, documentação, exemplos e testes. A CLI, porém, instala nos projetos usuários somente o runtime operacional necessário. Exemplos e infraestrutura de manutenção não são projetados no projeto alvo.

## 6. Promoções futuras de versão

Para qualquer bump de versão futuro (RC ou não), altere de forma coordenada:

- `pyproject.toml`
- `src/scrumaidev/__init__.py`
- `installer/install.ps1` e `installer/install.sh` (versão padrão)
- referências de versão em README/CONTRIBUTING
- changelog/release notes

`tests_cli/test_version_consistency.py` falha automaticamente se as quatro primeiras divergirem entre si. Então crie a tag correspondente, por exemplo `v0.2.0` ou `v1.0.0`, conforme a política de versionamento escolhida.
