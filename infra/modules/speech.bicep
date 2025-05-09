// speech.bicep
// Azure Speech Services module

targetScope = 'resourceGroup'

@description('Name of the Speech Services account')
param speechAccountName string

@description('Create or recover the account?')
param deployAccount bool = true

@description('Set true to recover a soft-deleted account')
param restore bool = false

@description('Azure region')
param location string = resourceGroup().location

@description('Pricing tier')
@allowed([ 'S0' ])
param sku string = 'S0'

@description('Custom sub-domain prefix')
param customSubDomainName string

@description('Subnet resource ID for private access')
param subnetId string

@description('Tags to apply')
param tags object = {}

resource speechService 'Microsoft.CognitiveServices/accounts@2024-10-01' = if (deployAccount) {
  name: speechAccountName
  location: location
  kind: 'SpeechServices'
  identity: { type: 'SystemAssigned' }
  sku: { name: sku }
  properties: {
    customSubDomainName: customSubDomainName
    apiProperties: { subnet: { id: subnetId } }
    restore: restore
    publicNetworkAccess: 'Disabled'
    networkAcls: { defaultAction: 'Deny', virtualNetworkRules: [ { id: subnetId, ignoreMissingVnetServiceEndpoint: false } ] }
  }
  tags: tags
}

resource speechExisting 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = if (!deployAccount) { name: speechAccountName }

output speechAccountId string = deployAccount ? speechService.id : speechExisting.id
output speechEndpoint   string = deployAccount ? speechService.properties.endpoint : speechExisting.properties.endpoint
