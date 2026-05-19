$ErrorActionPreference = 'Stop'
$workspaceFolder = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$envFile = Join-Path $workspaceFolder '.env'
$frontendEnvFile = Join-Path $workspaceFolder 'frontend\.env.local'

if (-not (Test-Path $envFile)) {
    throw "Missing root .env file: $envFile"
}

if (-not (Test-Path $frontendEnvFile)) {
    throw "Missing frontend .env.local file: $frontendEnvFile"
}

$required = @(
    'COSMOS_ENDPOINT',
    'COSMOS_DATABASE',
    'PROJECT_ENDPOINT',
    'MODEL_DEPLOYMENT_NAME',
    'MODEL_REASONING_DEPLOYMENT',
    'ENTRA_AUTH_ENABLED'
)

$content = Get-Content -Path $envFile
foreach ($name in $required) {
    $match = $content | Select-String -Pattern "^$name=(.*)$"
    if (-not $match) {
        throw "Missing required variable in .env: $name"
    }

    $value = $match.Matches.Groups[1].Value.Trim().Trim('"')
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Required variable is empty in .env: $name"
    }
}

$frontendContent = Get-Content -Path $frontendEnvFile
if (-not ($frontendContent | Select-String -Pattern '^NEXT_PUBLIC_APIM_BASE_URL=')) {
    throw 'Missing required variable in frontend/.env.local: NEXT_PUBLIC_APIM_BASE_URL'
}

Write-Host 'Environment check passed. Required local variables are present; values were not printed.'
