$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$EntryPoint = Join-Path $ProjectRoot "src\venv_manager\__main__.py"
$IconPath = Join-Path $ProjectRoot "src\venv_manager\assets\app.ico"
$AssetsPath = Join-Path $ProjectRoot "src\venv_manager\assets"

Set-Location $ProjectRoot

$PythonCommand = "python"
if (-not (Get-Command $PythonCommand -ErrorAction SilentlyContinue)) {
    $PythonCommand = "py"
} else {
    & $PythonCommand --version *> $null
}
if ($LASTEXITCODE -ne 0 -and (Get-Command py -ErrorAction SilentlyContinue)) {
    $PythonCommand = "py"
}

$Args = @(
    "--name", "VenvManager",
    "--onefile",
    "--windowed",
    "--clean"
)

if (Test-Path $IconPath) {
    $Args += @("--icon", $IconPath)
}

if (Test-Path $AssetsPath) {
    $Args += @("--add-data", "$AssetsPath;venv_manager\assets")
}

$Args += $EntryPoint

& $PythonCommand -m PyInstaller @Args

$ExePath = Join-Path $ProjectRoot "dist\VenvManager.exe"
if (-not (Test-Path $ExePath)) {
    throw "Build failed: dist\VenvManager.exe was not created."
}

Write-Host "Built $ExePath"
