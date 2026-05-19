param(
    [ValidateSet('start', 'stop', 'restart', 'status', 'health', 'check')]
    [string]$Action = 'start',

    [ValidateSet('all', 'avatar', 'configuration', 'essays', 'questions', 'upskilling', 'chat', 'evaluation', 'lms-gateway', 'insights')]
    [string[]]$Services = @('all'),

    [switch]$NoFrontend,

    [switch]$Reload,

    [switch]$DebugBackend,

    [int]$HealthTimeoutSeconds = 90
)

$ErrorActionPreference = 'Stop'

$workspaceFolder = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$runtimeRoot = Join-Path $workspaceFolder '.tmp\local-dev'
$logRoot = Join-Path $runtimeRoot 'logs'
$commandRoot = Join-Path $runtimeRoot 'commands'
$pidFile = Join-Path $runtimeRoot 'pids.json'

$serviceDefinitions = [ordered]@{
    'avatar'        = @{ Cwd = 'apps\avatar\src';        Port = 8081; Health = 'http://localhost:8081/health'; DebugPort = 5681 }
    'configuration' = @{ Cwd = 'apps\configuration\src'; Port = 8082; Health = 'http://localhost:8082/health'; DebugPort = 5682 }
    'essays'        = @{ Cwd = 'apps\essays\src';        Port = 8083; Health = 'http://localhost:8083/health'; DebugPort = 5683 }
    'questions'     = @{ Cwd = 'apps\questions';         Port = 8084; Health = 'http://localhost:8084/health'; DebugPort = 5684 }
    'upskilling'    = @{ Cwd = 'apps\upskilling';        Port = 8085; Health = 'http://localhost:8085/health'; DebugPort = 5685 }
    'chat'          = @{ Cwd = 'apps\chat\src';          Port = 8086; Health = 'http://localhost:8086/health'; DebugPort = 5686 }
    'evaluation'    = @{ Cwd = 'apps\evaluation\src';    Port = 8087; Health = 'http://localhost:8087/health'; DebugPort = 5687 }
    'lms-gateway'   = @{ Cwd = 'apps\lms-gateway\src';   Port = 8088; Health = 'http://localhost:8088/health'; DebugPort = 5688 }
    'insights'      = @{ Cwd = 'apps\insights\src';      Port = 8089; Health = 'http://localhost:8089/health'; DebugPort = 5689 }
}

function Initialize-RuntimeFolder {
    New-Item -ItemType Directory -Path $runtimeRoot, $logRoot, $commandRoot -Force | Out-Null
}

function Get-SelectedServices {
    if ($Services -contains 'all') {
        return @($serviceDefinitions.Keys)
    }

    return @($Services)
}

function Read-PidRecords {
    if (-not (Test-Path $pidFile)) {
        return @()
    }

    $content = Get-Content -Path $pidFile -Raw -ErrorAction SilentlyContinue
    if ([string]::IsNullOrWhiteSpace($content)) {
        return @()
    }

    try {
        $records = $content | ConvertFrom-Json -ErrorAction Stop
        return @(ConvertTo-FlatPidRecords -Records $records)
    }
    catch {
        Write-Host "Ignoring unreadable PID file: $pidFile"
        return @()
    }
}

function Write-PidRecords($Records) {
    Initialize-RuntimeFolder
    $normalizedRecords = @(ConvertTo-FlatPidRecords -Records $Records)
    ConvertTo-JsonArray -Records $normalizedRecords | Set-Content -Path $pidFile -Encoding utf8
}

function Repair-PidFile($Records) {
    if (-not (Test-Path $pidFile)) {
        return
    }

    $normalizedRecords = @(ConvertTo-FlatPidRecords -Records $Records)
    if ($normalizedRecords.Count -eq 0) {
        Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
        return
    }

    Write-PidRecords -Records $normalizedRecords
}

function Expand-RecordList($Value) {
    if ($null -eq $Value) {
        return @()
    }

    if ($Value -is [System.Array]) {
        $items = @()
        foreach ($item in $Value) {
            $items += @(Expand-RecordList -Value $item)
        }
        return @($items)
    }

    return @($Value)
}

function Get-ObjectPropertyValue($Object, [string]$Name, $DefaultValue = $null) {
    if ($null -eq $Object) {
        return $DefaultValue
    }

    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property -or $null -eq $property.Value) {
        return $DefaultValue
    }

    return $property.Value
}

function ConvertTo-FlatPidRecords($Records) {
    $flatRecords = @()
    foreach ($record in @(Expand-RecordList -Value $Records)) {
        $name = [string](Get-ObjectPropertyValue -Object $record -Name 'Name' -DefaultValue '')
        if ([string]::IsNullOrWhiteSpace($name)) {
            continue
        }

        if ($name -ne 'frontend' -and -not $serviceDefinitions.Contains($name)) {
            continue
        }

        $pidValue = 0
        if (-not [int]::TryParse([string](Get-ObjectPropertyValue -Object $record -Name 'Pid' -DefaultValue ''), [ref]$pidValue)) {
            continue
        }

        if ($pidValue -le 0) {
            continue
        }

        $url = [string](Get-ObjectPropertyValue -Object $record -Name 'Url' -DefaultValue '')
        $debugPort = 0
        [void][int]::TryParse([string](Get-ObjectPropertyValue -Object $record -Name 'DebugPort' -DefaultValue '0'), [ref]$debugPort)

        if ([string]::IsNullOrWhiteSpace($url)) {
            if ($name -eq 'frontend') {
                $url = 'http://localhost:3000'
            }
            else {
                $url = [string]$serviceDefinitions[$name].Health
            }
        }

        if ($debugPort -eq 0 -and $name -ne 'frontend') {
            $debugPort = [int]$serviceDefinitions[$name].DebugPort
        }

        $flatRecords += [pscustomobject]@{
            Name = $name
            Pid = $pidValue
            Url = $url
            StartedAt = [string](Get-ObjectPropertyValue -Object $record -Name 'StartedAt' -DefaultValue '')
            DebugPort = $debugPort
            OutLog = [string](Get-ObjectPropertyValue -Object $record -Name 'OutLog' -DefaultValue (Join-Path $logRoot "$name.out.log"))
            ErrLog = [string](Get-ObjectPropertyValue -Object $record -Name 'ErrLog' -DefaultValue (Join-Path $logRoot "$name.err.log"))
        }
    }

    return @($flatRecords)
}

function ConvertTo-JsonArray($Records) {
    $recordsToWrite = @(ConvertTo-FlatPidRecords -Records $Records)
    if ($recordsToWrite.Count -eq 0) {
        return '[]'
    }

    $items = @($recordsToWrite | ForEach-Object { ConvertTo-Json -InputObject $_ -Depth 5 })
    return "[`n$($items -join ",`n")`n]"
}

function Test-ProcessAlive([int]$ProcessId) {
    return $null -ne (Get-Process -Id $ProcessId -ErrorAction SilentlyContinue)
}

function Stop-ProcessTree([int]$ProcessId, [hashtable]$Visited = $null) {
    if ($null -eq $Visited) {
        $Visited = @{}
    }

    if ($ProcessId -le 0 -or $Visited.ContainsKey($ProcessId) -or $ProcessId -eq $PID) {
        return
    }

    $Visited[$ProcessId] = $true
    $children = Get-CimInstance Win32_Process -Filter "ParentProcessId=$ProcessId" -ErrorAction SilentlyContinue
    foreach ($child in @($children)) {
        Stop-ProcessTree -ProcessId ([int]$child.ProcessId) -Visited $Visited
    }

    $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
    if ($process) {
        Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
    }
}

function ConvertTo-PowerShellLiteral([string]$Value) {
    return "'" + ($Value -replace "'", "''") + "'"
}

function ConvertTo-NormalizedText([string]$Value) {
    if ($null -eq $Value) {
        return ''
    }

    return ($Value -replace '/', '\').ToLowerInvariant()
}

function Test-CommandLineInTutorScope([string]$CommandLine) {
    $text = ConvertTo-NormalizedText -Value $CommandLine
    if ([string]::IsNullOrWhiteSpace($text)) {
        return $false
    }

    $workspace = ConvertTo-NormalizedText -Value $workspaceFolder
    $runtime = ConvertTo-NormalizedText -Value $runtimeRoot
    return ($text.Contains($workspace) -or $text.Contains($runtime) -or $text.Contains('.tmp\local-dev'))
}

function Test-CommandLineHasDevMarker([string]$CommandLine) {
    $text = ConvertTo-NormalizedText -Value $CommandLine
    return ($text -match 'uvicorn|debugpy|pnpm|next(\.cmd)?|local-dev\.ps1|start-service\.ps1|\.tmp\\local-dev')
}

function Test-CommandLineTargetsName([string]$CommandLine, [string[]]$TargetNames) {
    $text = ConvertTo-NormalizedText -Value $CommandLine
    foreach ($targetName in @($TargetNames)) {
        if ($targetName -eq 'frontend') {
            if ($text -match '\\commands\\frontend\.ps1' -or (($text -match 'pnpm|next(\.cmd)?') -and $text -match 'frontend')) {
                return $true
            }

            continue
        }

        if (-not $serviceDefinitions.Contains($targetName)) {
            continue
        }

        $escapedName = [regex]::Escape($targetName)
        $servicePort = [int]$serviceDefinitions[$targetName].Port
        $debugPort = [int]$serviceDefinitions[$targetName].DebugPort
        $matchesTarget = $text -match "\\commands\\$escapedName\.ps1"
        $matchesTarget = $matchesTarget -or (($text -match 'start-service\.ps1') -and $text.Contains($targetName))
        $matchesTarget = $matchesTarget -or ($text -match "--port\s+$servicePort")
        $matchesTarget = $matchesTarget -or ($text -match "127\.0\.0\.1:$debugPort")
        if ($matchesTarget) {
            return $true
        }
    }

    return $false
}

function Get-StartTargetNames {
    $targetNames = @()
    foreach ($service in Get-SelectedServices) {
        $targetNames += $service
    }

    if (-not $NoFrontend) {
        $targetNames += 'frontend'
    }

    return @($targetNames | Select-Object -Unique)
}

function Get-AllTargetNames {
    $targetNames = @($serviceDefinitions.Keys)
    $targetNames += 'frontend'
    return @($targetNames)
}

function Get-TargetPorts([string[]]$TargetNames) {
    $ports = @()
    foreach ($targetName in @($TargetNames)) {
        if ($targetName -eq 'frontend') {
            $ports += 3000
            continue
        }

        if ($serviceDefinitions.Contains($targetName)) {
            $ports += [int]$serviceDefinitions[$targetName].Port
            $ports += [int]$serviceDefinitions[$targetName].DebugPort
        }
    }

    return @($ports | Select-Object -Unique)
}

function Get-ProcessSnapshot {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Select-Object ProcessId, ParentProcessId, Name, CommandLine)
}

function New-ProcessLookup($Processes) {
    $lookup = @{}
    foreach ($process in @($Processes)) {
        if ($null -ne $process.ProcessId) {
            $lookup[[int]$process.ProcessId] = $process
        }
    }

    return $lookup
}

function Get-ProtectedProcessIds([hashtable]$ProcessLookup) {
    $protectedIds = @{}
    $currentId = [int]$PID
    while ($currentId -gt 0 -and -not $protectedIds.ContainsKey($currentId)) {
        $protectedIds[$currentId] = $true
        if (-not $ProcessLookup.ContainsKey($currentId)) {
            break
        }

        $parentId = [int]$ProcessLookup[$currentId].ParentProcessId
        if ($parentId -le 0) {
            break
        }

        $currentId = $parentId
    }

    return $protectedIds
}

function Get-ListenerProcessIds([int[]]$Ports) {
    $listenerIds = @()
    foreach ($port in @($Ports | Select-Object -Unique)) {
        try {
            $listenerIds += @(Get-NetTCPConnection -State Listen -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess)
        }
        catch {
        }
    }

    return @($listenerIds | Where-Object { $_ } | Select-Object -Unique)
}

function Test-ScopedTutorDevCommand([string]$CommandLine, [string[]]$TargetNames) {
    return ((Test-CommandLineInTutorScope -CommandLine $CommandLine) -and
        (Test-CommandLineHasDevMarker -CommandLine $CommandLine) -and
        (Test-CommandLineTargetsName -CommandLine $CommandLine -TargetNames $TargetNames))
}

function Test-PidRecordActive($Record) {
    $pidValue = [int]$Record.Pid
    if (-not (Test-ProcessAlive -ProcessId $pidValue)) {
        return $false
    }

    $process = Get-CimInstance Win32_Process -Filter "ProcessId=$pidValue" -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        return $false
    }

    return (Test-ScopedTutorDevCommand -CommandLine ([string]$process.CommandLine) -TargetNames @([string]$Record.Name))
}

function Test-SafeTutorDevProcess($Process, [int[]]$ListenerProcessIds, [hashtable]$ProcessLookup, [string[]]$TargetNames) {
    $processId = [int]$Process.ProcessId
    $commandLine = [string]$Process.CommandLine
    if (-not (Test-CommandLineHasDevMarker -CommandLine $commandLine)) {
        return $false
    }

    if (Test-ScopedTutorDevCommand -CommandLine $commandLine -TargetNames $TargetNames) {
        return $true
    }

    if ($ListenerProcessIds -contains $processId) {
        return $true
    }

    $parentId = [int]$Process.ParentProcessId
    while ($parentId -gt 0 -and $ProcessLookup.ContainsKey($parentId)) {
        $parent = $ProcessLookup[$parentId]
        if (Test-ScopedTutorDevCommand -CommandLine ([string]$parent.CommandLine) -TargetNames $TargetNames) {
            return $true
        }

        $parentId = [int]$parent.ParentProcessId
    }

    return $false
}

function Get-SafeTutorDevProcessRootId($Process, [int[]]$ListenerProcessIds, [hashtable]$ProcessLookup, [hashtable]$ProtectedProcessIds, [string[]]$TargetNames) {
    $root = $Process
    $parentId = [int]$Process.ParentProcessId
    while ($parentId -gt 0 -and $ProcessLookup.ContainsKey($parentId) -and -not $ProtectedProcessIds.ContainsKey($parentId)) {
        $parent = $ProcessLookup[$parentId]
        if (-not (Test-SafeTutorDevProcess -Process $parent -ListenerProcessIds $ListenerProcessIds -ProcessLookup $ProcessLookup -TargetNames $TargetNames)) {
            break
        }

        $root = $parent
        $parentId = [int]$parent.ParentProcessId
    }

    return [int]$root.ProcessId
}

function Get-SafeTutorDevProcessIds([string[]]$TargetNames) {
    $targetPorts = @(Get-TargetPorts -TargetNames $TargetNames)
    $processes = @(Get-ProcessSnapshot)
    $processLookup = New-ProcessLookup -Processes $processes
    $protectedProcessIds = Get-ProtectedProcessIds -ProcessLookup $processLookup
    $listenerProcessIds = @(Get-ListenerProcessIds -Ports $targetPorts)
    $safeProcessIds = @{}

    foreach ($process in $processes) {
        $processId = [int]$process.ProcessId
        if ($protectedProcessIds.ContainsKey($processId)) {
            continue
        }

        if (Test-SafeTutorDevProcess -Process $process -ListenerProcessIds $listenerProcessIds -ProcessLookup $processLookup -TargetNames $TargetNames) {
            $rootProcessId = Get-SafeTutorDevProcessRootId -Process $process -ListenerProcessIds $listenerProcessIds -ProcessLookup $processLookup -ProtectedProcessIds $protectedProcessIds -TargetNames $TargetNames
            if (-not $protectedProcessIds.ContainsKey($rootProcessId)) {
                $safeProcessIds[$rootProcessId] = $true
            }
        }
    }

    return @($safeProcessIds.Keys | Sort-Object)
}

function Get-AliveRecordedProcessIds($Records, [string[]]$TargetNames) {
    $aliveProcessIds = @()
    foreach ($record in @(ConvertTo-FlatPidRecords -Records $Records)) {
        if (($TargetNames -contains $record.Name) -and (Test-PidRecordActive -Record $record)) {
            $aliveProcessIds += [int]$record.Pid
        }
    }

    return @($aliveProcessIds | Select-Object -Unique)
}

function Stop-SafeTutorDevProcesses([string[]]$TargetNames, [int[]]$PreserveProcessIds = @(), [string]$MessagePrefix = 'Stopping stale local Tutor dev process tree') {
    $preserveLookup = @{}
    foreach ($processId in @($PreserveProcessIds)) {
        $preserveLookup[[int]$processId] = $true
    }

    $processIds = @(Get-SafeTutorDevProcessIds -TargetNames $TargetNames)
    foreach ($processId in $processIds) {
        if ($preserveLookup.ContainsKey([int]$processId)) {
            continue
        }

        if (Test-ProcessAlive -ProcessId ([int]$processId)) {
            Write-Host "$MessagePrefix (PID $processId)"
            Stop-ProcessTree -ProcessId ([int]$processId)
        }
    }
}

function Get-ActivePidRecords($Records) {
    $activeRecords = @()
    foreach ($record in @(ConvertTo-FlatPidRecords -Records $Records)) {
        if (Test-PidRecordActive -Record $record) {
            $activeRecords += $record
        }
    }

    return @($activeRecords)
}

function Get-AvailableLogPath([string]$Path) {
    if (-not (Test-Path $Path)) {
        return $Path
    }

    try {
        Remove-Item -Path $Path -Force -ErrorAction Stop
        return $Path
    }
    catch {
        $directory = Split-Path -Path $Path -Parent
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($Path)
        $extension = [System.IO.Path]::GetExtension($Path)
        $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss-fff'
        $candidate = Join-Path $directory "$baseName.$timestamp$extension"
        Write-Host "Log file is locked; writing to $candidate"
        return $candidate
    }
}

function New-ServiceCommandFile([string]$Name) {
    $definition = $serviceDefinitions[$Name]
    $startServiceScript = Join-Path $PSScriptRoot 'start-service.ps1'
    $commandFile = Join-Path $commandRoot "$Name.ps1"
    $reloadArgument = if ($Reload) { '' } else { ' -NoReload' }
    $debugArgument = if ($DebugBackend) { " -DebugBackend -DebugPort $($definition.DebugPort)" } else { '' }
    $content = @"
`$ErrorActionPreference = 'Stop'
Set-Location -Path $(ConvertTo-PowerShellLiteral $workspaceFolder)
& $(ConvertTo-PowerShellLiteral 'powershell') -NoProfile -ExecutionPolicy Bypass -File $(ConvertTo-PowerShellLiteral $startServiceScript) -Service $(ConvertTo-PowerShellLiteral $Name)$reloadArgument$debugArgument
"@
    Set-Content -Path $commandFile -Value $content -Encoding utf8
    return $commandFile
}

function New-FrontendCommandFile {
    $commandFile = Join-Path $commandRoot 'frontend.ps1'
    $content = @"
`$ErrorActionPreference = 'Stop'
Set-Location -Path $(ConvertTo-PowerShellLiteral $workspaceFolder)
. $(ConvertTo-PowerShellLiteral (Join-Path $PSScriptRoot 'load-env.ps1')) -EnvFile $(ConvertTo-PowerShellLiteral (Join-Path $workspaceFolder '.env'))
cmd.exe /d /c "pnpm --dir frontend dev --hostname 127.0.0.1 --port 3000"
"@
    Set-Content -Path $commandFile -Value $content -Encoding utf8
    return $commandFile
}

function Start-ManagedProcess([string]$Name, [string]$CommandFile, [string]$Url, [int]$DebugPort = 0) {
    $records = @(Read-PidRecords)
    $existing = $records | Where-Object { $_.Name -eq $Name } | Select-Object -First 1
    if ($existing -and (Test-PidRecordActive -Record $existing)) {
        Write-Host "$Name already running on $Url (PID $($existing.Pid))"
        return $records
    }

    $stdout = Get-AvailableLogPath -Path (Join-Path $logRoot "$Name.out.log")
    $stderr = Get-AvailableLogPath -Path (Join-Path $logRoot "$Name.err.log")

    $process = Start-Process -FilePath 'powershell' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $CommandFile) -WorkingDirectory $workspaceFolder -RedirectStandardOutput $stdout -RedirectStandardError $stderr -WindowStyle Hidden -PassThru
    if ($DebugPort -gt 0) {
        Write-Host "Started $Name on $Url (PID $($process.Id), debug 127.0.0.1:$DebugPort)"
    }
    else {
        Write-Host "Started $Name on $Url (PID $($process.Id))"
    }

    $records = @($records | Where-Object { $_.Name -ne $Name })
    $records += [pscustomobject]@{
        Name = $Name
        Pid = $process.Id
        Url = $Url
        StartedAt = (Get-Date).ToString('o')
        DebugPort = $DebugPort
        OutLog = $stdout
        ErrLog = $stderr
    }
    return $records
}

function Wait-Endpoint([string]$Name, [string]$Url, [int]$TimeoutSeconds) {
    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
            Write-Host "$Name health PASS ($([int]$response.StatusCode))"
            return $true
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    Write-Host "$Name health FAIL ($Url)"
    return $false
}

function Start-LocalStack {
    Initialize-RuntimeFolder
    $targetNames = @(Get-StartTargetNames)
    $records = @(Read-PidRecords)
    Repair-PidFile -Records $records
    $preserveProcessIds = @(Get-AliveRecordedProcessIds -Records $records -TargetNames $targetNames)
    Stop-SafeTutorDevProcesses -TargetNames $targetNames -PreserveProcessIds $preserveProcessIds
    $records = @(Get-ActivePidRecords -Records (Read-PidRecords))
    Write-PidRecords -Records $records

    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'test-env.ps1')

    foreach ($service in Get-SelectedServices) {
        $definition = $serviceDefinitions[$service]
        $commandFile = New-ServiceCommandFile -Name $service
        $debugPort = if ($DebugBackend) { [int]$definition.DebugPort } else { 0 }
        $records = @(Start-ManagedProcess -Name $service -CommandFile $commandFile -Url $definition.Health -DebugPort $debugPort)
        Write-PidRecords -Records $records
    }

    if (-not $NoFrontend) {
        $records = @(Start-ManagedProcess -Name 'frontend' -CommandFile (New-FrontendCommandFile) -Url 'http://localhost:3000')
        Write-PidRecords -Records $records
    }

    Test-LocalHealth -TimeoutSeconds $HealthTimeoutSeconds
    Write-Host "Logs: $logRoot"
}

function Stop-LocalStack {
    $records = @(Read-PidRecords)
    Repair-PidFile -Records $records
    if ($records.Count -eq 0) {
        Write-Host 'No local-dev processes are recorded.'
    }

    foreach ($record in $records) {
        if (Test-PidRecordActive -Record $record) {
            Write-Host "Stopping $($record.Name) (PID $($record.Pid))"
            Stop-ProcessTree -ProcessId ([int]$record.Pid)
        }
        elseif (Test-ProcessAlive -ProcessId ([int]$record.Pid)) {
            Write-Host "Ignoring stale $($record.Name) PID record (PID $($record.Pid))"
        }
        else {
            Write-Host "$($record.Name) already stopped"
        }
    }

    Stop-SafeTutorDevProcesses -TargetNames (Get-AllTargetNames) -MessagePrefix 'Stopping orphaned local Tutor dev process tree'

    Remove-Item -Path $pidFile -Force -ErrorAction SilentlyContinue
}

function Show-LocalStatus {
    $records = @(Read-PidRecords)
    $activeRecords = @(Get-ActivePidRecords -Records $records)
    Repair-PidFile -Records $activeRecords
    if ($activeRecords.Count -eq 0) {
        Write-Host 'No local-dev processes are recorded.'
        return
    }

    $activeRecords | ForEach-Object {
        [pscustomobject]@{
            Name = $_.Name
            Pid = $_.Pid
            Running = (Test-ProcessAlive -ProcessId ([int]$_.Pid))
            Url = $_.Url
            DebugPort = $_.DebugPort
            OutLog = $_.OutLog
            ErrLog = $_.ErrLog
        }
    } | Format-Table -AutoSize
}

function Test-LocalHealth([int]$TimeoutSeconds = 3) {
    $failed = $false
    foreach ($service in Get-SelectedServices) {
        $definition = $serviceDefinitions[$service]
        if (-not (Wait-Endpoint -Name $service -Url $definition.Health -TimeoutSeconds $TimeoutSeconds)) {
            $failed = $true
        }
    }

    if (-not $NoFrontend) {
        if (-not (Wait-Endpoint -Name 'frontend' -Url 'http://localhost:3000' -TimeoutSeconds $TimeoutSeconds)) {
            $failed = $true
        }
    }

    if ($failed) {
        exit 1
    }
}

function Invoke-CheckCommand([string]$Name, [scriptblock]$Command) {
    Write-Host "Running $Name"
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Name failed with exit code $LASTEXITCODE"
    }
}

function Invoke-LocalChecks {
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'test-env.ps1')
    Invoke-CheckCommand -Name 'frontend lint' -Command { pnpm --dir frontend lint }
    Invoke-CheckCommand -Name 'frontend typecheck' -Command { pnpm --dir frontend typecheck }
    Invoke-CheckCommand -Name 'e2e list' -Command { pnpm --dir frontend e2e:list }
    Invoke-CheckCommand -Name 'backend tests' -Command { python -m pytest tests -q }
}

switch ($Action) {
    'start' { Start-LocalStack }
    'stop' { Stop-LocalStack }
    'restart' {
        Stop-LocalStack
        Start-LocalStack
    }
    'status' { Show-LocalStatus }
    'health' { Test-LocalHealth -TimeoutSeconds 3 }
    'check' { Invoke-LocalChecks }
}