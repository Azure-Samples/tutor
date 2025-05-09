targetScope = 'resourceGroup'

@description('The name of the Log Analytics Workspace.')
param workspaceName string = 'tutor-loganalytics'

@description('The location for the Log Analytics Workspace.')
param location string

@description('The retention period in days for the Log Analytics data.')
param retentionInDays int = 30

@description('Keyvault secret for the Log Analytics Workspace.')
param keyVaultReference string

@description('Environment indicator to adjust address space accordingly')
param environment string

@description('Subscription Id for resource references')
param subscriptionId string = subscription().subscriptionId

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: workspaceName
  location: location
  properties: {
    retentionInDays: retentionInDays
    // For tighter security, disable public network access.
    publicNetworkAccessForIngestion: 'Disabled'
    publicNetworkAccessForQuery: 'Disabled'
  }
  tags: {
    project: 'TheTutor'
    environment: environment
    keyVaultReference: keyVaultReference
    subscriptionId: subscriptionId
  }
}

output workspaceId string = logAnalytics.id
output workspaceCustomerId string = logAnalytics.properties.customerId
output workspaceName string = logAnalytics.name
