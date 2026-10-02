# ScrumAIDev 0.1.0rc2

Release candidate preparada para publicação em um novo repositório Git.

## Principais mudanças

- CLI oficial `scrumaidev` com `version`, `config`, `doctor` e `uninstall`.
- Runtime separado do repositório-fonte.
- Adapter OpenCode gerando slash commands em `.opencode/commands/` sem override de modelo.
- Manifesto `.scrumaidev/manifest.json` com versão, harness, hashes e proveniência.
- Instalação com preflight para evitar configuração parcial em caso de conflito.
- `--dry-run`, `--force` e saída JSON para automação/experimentos.
- Preservação de `AGENTS.md` já existente por meio de bridge delimitada.
- Seeds de projeto preservados no uninstall por padrão.
- Instaladores PowerShell e POSIX capazes de instalar do source checkout, de um wheel local de release ou de um registry quando disponível.
- Testes executáveis diretamente em um checkout limpo via `python -m pytest -q`.
- Workflow de GitHub Release inclui wheel, instaladores e checksums.

## Validação recomendada antes da promoção

1. Executar `python -m pytest -q` em Windows e Linux.
2. Instalar com `installer/install.ps1 -Source .` no Windows.
3. Configurar um projeto descartável com `scrumaidev config --harness opencode --pin 0.1.0rc2`.
4. Executar `scrumaidev doctor`.
5. Confirmar que os slash commands aparecem no OpenCode.
6. Validar `/init-project` em um projeto de teste, fora da rodada experimental oficial.

## Compatibilidade

Alguns identificadores históricos internos com prefixo `agileaidev_` foram preservados nesta RC para evitar quebra de compatibilidade. Uma migração de nomenclatura deve ser tratada separadamente antes de uma versão estável caso seja desejada.
