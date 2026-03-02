Param(
    [Parameter(Mandatory = $false)]
    [string]$Location = "eastus",

    [Parameter(Mandatory = $false)]
    [string]$StateResourceGroup = "tutor-state-rg",

    [Parameter(Mandatory = $false)]
    [string]$StateStorageAccount = "tutortfstate",

    [Parameter(Mandatory = $false)]
    [string]$StateContainer = "tfstate"
)

$ErrorActionPreference = "Stop"

Write-Host "Creating state resource group '$StateResourceGroup' in '$Location'..."
az group create --name $StateResourceGroup --location $Location | Out-Null

Write-Host "Creating state storage account '$StateStorageAccount'..."
az storage account create `
  --name $StateStorageAccount `
  --resource-group $StateResourceGroup `
  --location $Location `
  --sku Standard_LRS `
  --min-tls-version TLS1_2 | Out-Null

Write-Host "Creating blob container '$StateContainer'..."
az storage container create `
  --name $StateContainer `
  --account-name $StateStorageAccount `
  --auth-mode login | Out-Null

Write-Host "Terraform remote state bootstrap complete."
Write-Host "Next: terraform init -backend-config=backend.hcl"
