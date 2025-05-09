targetScope = 'resourceGroup'

@description('The name of the Cosmos DB account.')
param cosmosDbName string

@description('The location for the Cosmos DB account.')
param location string

@description('The resource group location (used for failover settings).')
param resourceGroupLocation string

@description('Keyvault secret for the Log Analytics Workspace.')
param keyVaultReference string

@description('Environment indicator to adjust address space accordingly')
param environment string

@description('Subscription Id for resource references')
param subscriptionId string = subscription().subscriptionId

resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2021-04-15' = {
  name: cosmosDbName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: resourceGroupLocation
        failoverPriority: 0
      }
    ]
    isVirtualNetworkFilterEnabled: true
  }
  tags: {
    project: 'TheTutor'
    environment: environment
    keyVaultReference: keyVaultReference
    subscriptionId: subscriptionId
  }
}

output cosmosDbId string = cosmosDb.id
