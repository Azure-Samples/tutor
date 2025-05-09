// aoai.bicep
// Azure OpenAI / AI Services module

targetScope = 'resourceGroup'

@description('Name of the Azure AI Services account')
param aiServiceAccountName string

@description('Create or recover the account?')
param deployAccount bool = true

@description('Set true to recover a soft-deleted account')
param restore bool = false

@description('Azure region')
param location string = resourceGroup().location

@description('Pricing tier')
@allowed([ 'S0' ])
param sku string = 'S0'

@description('Custom sub-domain prefix (without suffix)')
param customSubDomainName string

@description('Resource ID of the subnet for private endpoint')
param subnetId string

@description('Model deployment name')
param modelDeploymentName string

@description('Model name (e.g. gpt-4)')
param modelName string

@description('Model version')
param modelVersion string

@description('Capacity units (tokens/min)')
param capacity int = 8000

@description('Tags to apply')
param tags object = {}

// Primary account resource: create or recover
resource openAIService 'Microsoft.CognitiveServices/accounts@2024-10-01' = if (deployAccount) {
  name: aiServiceAccountName
  location: location
  kind: 'AIServices'
  identity: { type: 'SystemAssigned' }
  sku: { name: sku }
  properties: {
    customSubDomainName: customSubDomainName
    apiProperties: { subnet: { id: subnetId } }
    restore: restore
    publicNetworkAccess: 'Disabled'
    networkAcls: {
      defaultAction: 'Deny'
      virtualNetworkRules: [ { id: subnetId, ignoreMissingVnetServiceEndpoint: false } ]
    }
  }
  tags: tags
}

// Existing account reference: used when not deploying
resource openAIExisting 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = if (!deployAccount) {
  name: aiServiceAccountName
}

// Model deployment for newly created account
resource modelDeploymentForAccount 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = if (deployAccount) {
  parent: openAIService
  name: modelDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
  sku: {
    name: 'GlobalStandard'
    capacity: capacity
  }
  tags: tags
}

// Model deployment for existing account
resource modelDeploymentForExisting 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = if (!deployAccount) {
  parent: openAIExisting
  name: modelDeploymentName
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
  sku: {
    name: 'GlobalStandard'
    capacity: capacity
  }
  tags: tags
}

// Outputs
output openAIAccountId string = deployAccount ? openAIService.id : openAIExisting.id
output openAIEndpoint  string = deployAccount ? openAIService.properties.endpoint : openAIExisting.properties.endpoint
output deploymentId     string = deployAccount ? modelDeploymentForAccount.id : modelDeploymentForExisting.id
