$ErrorActionPreference = 'Stop'

# Caminho do .env
$envFilePath = "src\.env"

# Função para extrair variável do .env
function Get-EnvValue($name) {
    return (Get-Content $envFilePath | Where-Object { $_ -match "^$name\s*=" }) -replace '.*=\s*"?([^"]+)"?', '$1'
}

# Variáveis do .env
$sub = Get-EnvValue 'SUBSCRIPTION_ID'
$location = Get-EnvValue 'LOCATION'
$rgName = Get-EnvValue 'RESOURCE_GROUP'
$vnetName = Get-EnvValue 'VNET_NAME'
$subnetName = Get-EnvValue 'MANAGEMENT_SUBNET_NAME'

# Definir subscription atual
Write-Host "✅ Subscription: $sub"
az account set --subscription $sub

# Lista de contas de IA e seus parâmetros de restauração
$accounts = @(
  @{ Name = Get-EnvValue 'AZURE_OPENAI_ACCOUNT_NAME';    Param = 'openAiRestore' },
  @{ Name = Get-EnvValue 'AZURE_SPEECH_ACCOUNT_NAME';    Param = 'speechRestore' },
  @{ Name = Get-EnvValue 'AZURE_VISION_ACCOUNT_NAME';    Param = 'visionRestore' },
  @{ Name = Get-EnvValue 'AZURE_DOC_ACCOUNT_NAME';       Param = 'docRestore' }
)

# Detecta e configura restore
$restoreParams = @{}

foreach ($acct in $accounts) {
  $name = $acct.Name
  $param = $acct.Param

  # Obter todos os soft-deletados na região e filtrar pelo nome
  $deleted = az cognitiveservices account list-deleted `
    --output json | ConvertFrom-Json

  $match = $deleted | Where-Object { $_.name -eq $name }

  if ($match) {
      Write-Host "🔁 Soft-deleted: $name. Adding '$param=true'"
      $restoreParams[$param] = $true
  } else {
      $restoreParams[$param] = $false
  }
}

Write-Host "🔧 Parâmetros de restauração: $($restoreParams | Out-String)"

# Garante que endpoint esteja no subnet
function Set-CognitiveServicesEndpoint {
    Write-Host "🔧 Verificando endpoint Microsoft.CognitiveServices..."
    $endpoints = az network vnet subnet show `
        --resource-group $rgName `
        --vnet-name $vnetName `
        --name $subnetName `
        --query "serviceEndpoints[].service" -o tsv

    if (-not ($endpoints -contains 'Microsoft.CognitiveServices')) {
        Write-Host "🔁 Adicionando endpoint Microsoft.CognitiveServices..."
        az network vnet subnet update `
            --resource-group $rgName `
            --vnet-name $vnetName `
            --name $subnetName `
            --service-endpoints Microsoft.CognitiveServices | Out-Null
    }
}

# Inicia deploy principal
function Deploy-MainTemplate {
    $paramArgs = @("rgName=$rgName", "location=$location")
    foreach ($kvp in $restoreParams.GetEnumerator()) {
      $paramArgs += "$($kvp.Key)=$($kvp.Value)"
    }
  
    # Montar a string de parâmetros
    $joinedParams = $paramArgs -join ' '
  
    # Montar e imprimir o comando antes de executar
    $command = "az deployment sub create --location $location --template-file .\infra\main.bicep --parameters $joinedParams --verbose --debug"
    Write-Host "🔧 Executando comando:"
    Write-Host $command
  
    # Capturar a saída do comando
    $output = & az deployment sub create `
      --location $location `
      --template-file ".\infra\main.bicep" `
      --parameters $paramArgs
  
    return $output
  }

try {
    Write-Host "🚀 Iniciando deploy da infraestrutura principal..."
    Set-CognitiveServicesEndpoint
    $result = Deploy-MainTemplate
    Write-Host "🔧 Resultado do deploy: $($result | Out-String)"
    if (($null -ne $result | Out-String | Select-String 'ERROR')) {
        throw "❌ Deploy returned ERROR in output"
    }
    Write-Host "✅ Deploy finalizado com sucesso!"
} catch {
    Write-Host "❌ Falha no deploy: $_"
    Write-Host "📋 Listando operações com erro..."
    az deployment operation sub list `
        --name main `
        --query "[?properties.provisioningState=='Failed']" `
        --output table
    exit 1
} finally {
    Write-Host "⚙️ Script finalizado em $(Get-Date -Format o)"
}
