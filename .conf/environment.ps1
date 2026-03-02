function ExecuteCommand($command) {
    Write-Host "Executing: $command"
    Invoke-Expression $command
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error executing command: $LASTEXITCODE"
        Write-Host "Error output: $($error[0])"
        exit $LASTEXITCODE
    }
}

$rootFolder = (Get-Item -Path "$PSScriptRoot\..").FullName
Set-Location -Path $rootFolder

if (-not (Test-Path ".venv")) {
    ExecuteCommand "py -3.13 -m pip install --upgrade uv"
    ExecuteCommand "py -3.13 -m uv venv .venv"
}

ExecuteCommand ".\.venv\Scripts\Activate.ps1"
ExecuteCommand "uv pip install --python .venv -e .\lib[dev]"

$services = @(
    "apps/avatar",
    "apps/configuration",
    "apps/essays",
    "apps/questions",
    "apps/upskilling"
)

foreach ($service in $services) {
    ExecuteCommand "uv pip install --python .venv -e .\$service[dev]"
}

ExecuteCommand "uv pip install --python .venv pre-commit ruff"
Write-Host "Environment setup complete."
