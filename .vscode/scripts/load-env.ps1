param(
    [string]$EnvFile = (Join-Path $PSScriptRoot "..\..\.env")
)

$resolvedEnvFile = Resolve-Path -Path $EnvFile -ErrorAction SilentlyContinue
if (-not $resolvedEnvFile) {
    throw "Environment file not found: $EnvFile"
}

foreach ($line in Get-Content -Path $resolvedEnvFile) {
    if ($line -match '^\s*$' -or $line -match '^\s*#') {
        continue
    }

    $parts = $line -split '=', 2
    if ($parts.Count -ne 2) {
        continue
    }

    $name = $parts[0].Trim()
    $value = $parts[1].Trim()
    if ($value.StartsWith('"') -and $value.EndsWith('"') -and $value.Length -ge 2) {
        $value = $value.Substring(1, $value.Length - 2)
    }

    [System.Environment]::SetEnvironmentVariable($name, $value, 'Process')
}
