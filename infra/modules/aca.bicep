// aca.bicep – uses dummy image for initial provisioning

targetScope = 'resourceGroup'

@description('Azure region for Container Apps resources')
param location string

@description('Resource ID of the subnet used by the Container Apps managed environment')
param infrastructureSubnetId string

@description('Log Analytics workspace name and location')
param logAnalyticsWorkspaceName string
param logAnalyticsWorkspaceLocation string = location

@description('Deployment environment indicator (dev | test | prod)')
param envType string

@description('Container App name')
param containerAppName string = 'tutor-containerapp'

@description('Container image (from ACR)')
param containerAppImage string = 'tutoracr.azurecr.io/myapp:latest'

@description('ACR name (used to assign pull role to env)')
param acrName string = 'tutoracr'

@description('ACR login server')
param acrLoginServer string = 'tutoracr.azurecr.io'

// Dummy image used temporarily during provisioning
var dummyImage = 'mcr.microsoft.com/oss/nginx/nginx:1.15.5-alpine'

var commonTags = {
  project: 'TheTutor'
  environment: envType
}

// ────────────── Log Analytics Workspace ──────────────
resource workspace 'Microsoft.OperationalInsights/workspaces@2020-08-01' = {
  name: logAnalyticsWorkspaceName
  location: logAnalyticsWorkspaceLocation
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    workspaceCapping: {}
  }
}

// ────────────── Container Apps Environment ──────────────
resource containerAppsEnv 'Microsoft.App/managedEnvironments@2024-08-02-preview' = {
  name: 'tutor-containerapps-env'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    vnetConfiguration: {
      infrastructureSubnetId: infrastructureSubnetId
    }
    publicNetworkAccess: 'Enabled'
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: workspace.properties.customerId
        sharedKey: listKeys(workspace.id, '2020-08-01').primarySharedKey
      }
    }
  }
  tags: commonTags
  dependsOn: [ workspace ]
}

// ────────────── AcrPull Role Assignment ──────────────
resource acr 'Microsoft.ContainerRegistry/registries@2021-09-01' existing = {
  name: acrName
}

resource acrPull 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, containerAppsEnv.id, 'AcrPull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: containerAppsEnv.identity.principalId
    principalType: 'ServicePrincipal'
  }
  dependsOn: [ containerAppsEnv ]
}

// ────────────── Container App ──────────────
resource containerApp 'Microsoft.App/containerApps@2024-08-02-preview' = {
  name: containerAppName
  location: location
  kind: 'containerapps'
  properties: {
    environmentId: containerAppsEnv.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 80
        transport: 'Auto'
        allowInsecure: false
        stickySessions: {
          affinity: 'none'
        }
        ipSecurityRestrictions: [
          {
            name: 'AllowMySubnet'
            ipAddressRange: '10.0.0.0/24'
            action: 'Allow'
            description: 'Internal subnet'
          }
        ]
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system-environment'
        }
      ]
      secrets: [] // optional if needed
    }
    template: {
      containers: [
        {
          name: 'app'
          image: dummyImage
          resources: {
            cpu: 2
            memory: '4Gi'
          }
          env: [
            {
              name: 'ENVIRONMENT'
              value: envType
            }
          ]
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
  tags: commonTags
  dependsOn: [ acrPull ]
}

output containerAppsEnvId string = containerAppsEnv.id
output containerAppId string = containerApp.id
