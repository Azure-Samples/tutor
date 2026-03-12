[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('dev', 'prod')]
    [string]$Environment,

    [Parameter()]
    [string]$SubscriptionId,

    [Parameter()]
    [switch]$Execute,

    [Parameter()]
    [switch]$PruneAcrImages,

    [Parameter()]
    [switch]$WaitForDelete,

    [Parameter()]
    [string]$ConfirmResourceGroup
)

$ErrorActionPreference = 'Stop'

function Invoke-AzJson {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $raw = & az @Args -o json 2>$null
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $null
    }

    return $raw | ConvertFrom-Json
}

$resourceGroup = "tutor-$Environment"
$apimName = "tutor-$Environment-apim"
$acaEnvironmentName = "tutor-$Environment-acae"

if (-not [string]::IsNullOrWhiteSpace($SubscriptionId)) {
    & az account set --subscription $SubscriptionId
}

$account = Invoke-AzJson -Args @('account', 'show')
if (-not $account) {
    throw 'Azure CLI is not authenticated. Run: az login'
}

Write-Host "Target subscription: $($account.name) [$($account.id)]"
Write-Host "Target environment: $Environment"
Write-Host "Target resource group: $resourceGroup"

$rgExists = (& az group exists --name $resourceGroup).Trim()
if ($rgExists -ne 'true') {
    Write-Host "Resource group '$resourceGroup' does not exist. Nothing to deprovision."
    exit 0
}

$resources = Invoke-AzJson -Args @('resource', 'list', '-g', $resourceGroup)
if ($resources) {
    Write-Host "Resources currently in '$resourceGroup':"
    $resources |
        Select-Object name, type, location |
        Format-Table -AutoSize
}

$apim = Invoke-AzJson -Args @('apim', 'show', '-g', $resourceGroup, '-n', $apimName)
$apimLocation = if ($apim) { $apim.location } else { '' }

if (-not $Execute) {
    Write-Host "Dry-run mode: no destructive actions executed."
    Write-Host "Run with -Execute -ConfirmResourceGroup $resourceGroup to proceed."
    exit 0
}

if ($ConfirmResourceGroup -ne $resourceGroup) {
    throw "Confirmation mismatch. Pass -ConfirmResourceGroup $resourceGroup to execute."
}

if ($PruneAcrImages) {
    Write-Host 'Pruning environment-specific ACR repositories...'

    $acrServers = & az containerapp list -g $resourceGroup --query "[].properties.configuration.registries[].server" -o tsv 2>$null |
        Where-Object { -not [string]::IsNullOrWhiteSpace($_) } |
        Sort-Object -Unique

    foreach ($acrServer in $acrServers) {
        $acrName = ($acrServer -replace '\.azurecr\.io$', '')
        if ([string]::IsNullOrWhiteSpace($acrName)) {
            continue
        }

        Write-Host "Scanning ACR '$acrName' for environment repositories..."
        $repositories = & az acr repository list -n $acrName -o tsv 2>$null |
            Where-Object { $_ -like "tutor/*-$Environment" }

        foreach ($repository in $repositories) {
            Write-Host "Deleting repository $repository from $acrName"
            & az acr repository delete -n $acrName --repository $repository --yes --only-show-errors | Out-Null
        }
    }
}

Write-Host "Deleting resource group '$resourceGroup'..."
& az group delete --name $resourceGroup --yes --no-wait | Out-Null

if ($WaitForDelete) {
    Write-Host "Waiting for resource group '$resourceGroup' deletion to complete..."
    & az group wait --name $resourceGroup --deleted --interval 20 --timeout 5400 | Out-Null
}

$existsAfter = (& az group exists --name $resourceGroup).Trim()
if ($existsAfter -eq 'true') {
    throw "Resource group '$resourceGroup' still exists after delete request."
}

if (-not [string]::IsNullOrWhiteSpace($apimLocation)) {
    $deletedApim = & az apim deletedservice show --service-name $apimName --location $apimLocation -o json 2>$null
    if (-not [string]::IsNullOrWhiteSpace($deletedApim)) {
        Write-Host "Purging soft-deleted APIM '$apimName' in $apimLocation..."
        & az apim deletedservice purge --service-name $apimName --location $apimLocation --yes | Out-Null
    }
}

$acaEnvStillExists = $false
& az containerapp env show -g $resourceGroup -n $acaEnvironmentName -o none 2>$null
if ($LASTEXITCODE -eq 0) {
    $acaEnvStillExists = $true
}

if ($acaEnvStillExists) {
    throw "ACA environment '$acaEnvironmentName' still resolvable after deprovision."
}

$apimStillExists = $false
& az apim show -g $resourceGroup -n $apimName -o none 2>$null
if ($LASTEXITCODE -eq 0) {
    $apimStillExists = $true
}

if ($apimStillExists) {
    throw "APIM '$apimName' still resolvable after deprovision."
}

Write-Host "Deprovision completed for environment '$Environment'."
