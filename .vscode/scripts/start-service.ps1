param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('avatar', 'configuration', 'essays', 'questions', 'upskilling', 'chat', 'evaluation', 'lms-gateway', 'insights')]
    [string]$Service,

    [switch]$NoReload,

    [switch]$DebugBackend,

    [int]$DebugPort = 0
)

$ErrorActionPreference = 'Stop'
$workspaceFolder = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
. (Join-Path $PSScriptRoot 'load-env.ps1') -EnvFile (Join-Path $workspaceFolder '.env')

$services = @{
    'avatar'        = @{ Cwd = 'apps\avatar\src';        App = 'app.main:app'; Port = 8081; DebugPort = 5681 }
    'configuration' = @{ Cwd = 'apps\configuration\src'; App = 'app.main:app'; Port = 8082; DebugPort = 5682 }
    'essays'        = @{ Cwd = 'apps\essays\src';        App = 'app.main:app'; Port = 8083; DebugPort = 5683 }
    'questions'     = @{ Cwd = 'apps\questions';         App = 'app.main:app'; Port = 8084; DebugPort = 5684 }
    'upskilling'    = @{ Cwd = 'apps\upskilling';        App = 'app.main:app'; Port = 8085; DebugPort = 5685 }
    'chat'          = @{ Cwd = 'apps\chat\src';          App = 'app.main:app'; Port = 8086; DebugPort = 5686 }
    'evaluation'    = @{ Cwd = 'apps\evaluation\src';    App = 'app.main:app'; Port = 8087; DebugPort = 5687 }
    'lms-gateway'   = @{ Cwd = 'apps\lms-gateway\src';   App = 'app.main:app'; Port = 8088; DebugPort = 5688 }
    'insights'      = @{ Cwd = 'apps\insights\src';      App = 'app.main:app'; Port = 8089; DebugPort = 5689 }
}

$definition = $services[$Service]
$serviceFolder = Join-Path $workspaceFolder $definition.Cwd
$python = Join-Path $workspaceFolder '.venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    $python = 'python'
}

$libPath = Join-Path $workspaceFolder 'lib\src'
$env:PYTHONPATH = "$libPath;$serviceFolder;$env:PYTHONPATH"

Write-Host "Starting Tutor service '$Service' on http://localhost:$($definition.Port)"
Write-Host "Swagger UI: http://localhost:$($definition.Port)/docs"
Set-Location -Path $serviceFolder
if ($DebugPort -eq 0) {
    $DebugPort = [int]$definition.DebugPort
}

$uvicornArgs = @($definition.App, '--host', '127.0.0.1', '--port', $definition.Port)
if (-not $NoReload) {
    $uvicornArgs += '--reload'
}

if ($DebugBackend) {
    Write-Host "Debugpy listening for '$Service' on 127.0.0.1:$DebugPort"
    & $python -m debugpy --listen "127.0.0.1:$DebugPort" -m uvicorn @uvicornArgs
}
else {
    & $python -m uvicorn @uvicornArgs
}

