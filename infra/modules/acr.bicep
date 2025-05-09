targetScope = 'resourceGroup'

@description('Name for the Azure Container Registry')
param acrName string = 'tutoracr'

@description('Azure region for the Container Registry')
param location string

@description('SKU for the Container Registry (Basic, Standard, Premium)')
@allowed([ 'Basic', 'Standard', 'Premium' ])
param sku string = 'Standard'

@description('Deployment environment indicator (dev | test | prod)')
param environment string

@description('Key Vault secret reference (for tagging)')
param keyVaultReference string

@description('Subscription Id for resource references')
param subscriptionId string = subscription().subscriptionId

resource acr 'Microsoft.ContainerRegistry/registries@2021-09-01' = {
  name: acrName
  location: location
  sku: {
    name: sku
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    adminUserEnabled: false
  }
  tags: {
    project: 'TheTutor'
    environment: environment
    keyVaultReference: keyVaultReference
    subscriptionId: subscriptionId
  }
}

output acrId string = acr.id

@description('Login server for the ACR')
output acrLoginServer string = acr.properties.loginServer
