param(
    [string]$Version = "0.4.0",
    [string]$Source = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

if ([string]::IsNullOrWhiteSpace($Source)) {
    $LocalWheel = Get-ChildItem -Path $ScriptDir -Filter "scrumaidev-$Version-*.whl" -File -ErrorAction SilentlyContinue | Select-Object -First 1
    $RepoRoot = Resolve-Path (Join-Path $ScriptDir "..") -ErrorAction SilentlyContinue

    if ($LocalWheel) {
        $Source = $LocalWheel.FullName
    }
    elseif ($RepoRoot -and (Test-Path (Join-Path $RepoRoot "pyproject.toml"))) {
        $Source = $RepoRoot.Path
    }
    else {
        $Source = "scrumaidev==$Version"
    }
}

if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Installing ScrumAIDev from: $Source"
    uv tool install --force $Source
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Installed. Verifying..."
    scrumaidev version
    exit $LASTEXITCODE
}

if (Get-Command pipx -ErrorAction SilentlyContinue) {
    Write-Host "Installing ScrumAIDev with pipx from: $Source"
    pipx install --force $Source
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    scrumaidev version
    exit $LASTEXITCODE
}

Write-Error "Neither 'uv' nor 'pipx' was found. Install uv (recommended) or pipx, then run this installer again."
