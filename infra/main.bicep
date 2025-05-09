//-----------------------------------------------
// main.bicep  – subscription‑scope entry point
//-----------------------------------------------
targetScope = 'subscription'

/*───────────────────────────
   1. Core deployment inputs
───────────────────────────*/
@minLength(1)
@maxLength(64)
param rgName string

@allowed([
  'eastus', 'eastus2', 'westus', 'westus2', 'westcentralus'
  'northeurope', 'francecentral', 'switzerlandnorth', 'switzerlandwest'
  'uksouth', 'australiaeast', 'eastasia', 'southeastasia'
  'centralindia', 'jioindiawest', 'japanwest', 'koreacentral'
])
param location string

@allowed([ 'dev', 'test', 'prod' ])
param environment string = 'dev'

param keyVaultName string = 'tutor-kv'
param subscriptionId string = subscription().subscriptionId

/* ACR settings */
@minLength(5)
@maxLength(50)
param acrName string = 'tutoracr'
var   acrLoginServer = '${acrName}.azurecr.io'

/*--------- OpenAI ---------*/
param openAiAccountName       string = 'tutor-openai'
param openAiCustomDomain      string = 'openai-ctr'
param deployOpenAiAccount     bool   = true
param openAiRestore           bool   = false
param openAiModelDeployment   string = 'tutor-4o'

@allowed([ 'gpt-4o', 'gpt-4o-mini' ])
param openAiModelName         string = 'gpt-4o'
param openAiModelVersion      string = '2024-11-20'
param openAiCapacity          int    = 80

param speechAccountName       string = 'tutor-speech'
param speechCustomDomain      string = 'speech-ctr'
param deploySpeechAccount     bool   = true
param speechRestore           bool   = false


/*──────────── Resources ────────────*/
resource tutorRG 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: rgName
  location: location
}

resource keyVault 'Microsoft.KeyVault/vaults@2021-06-01-preview' existing = {
  scope: tutorRG
  name: keyVaultName
}

/*──────── VNet (returns containerAppsSubnetId) ────────*/
module vnetModule './modules/vnet.bicep' = {
  name: 'deployVnet'
  scope: tutorRG
  params: {
    location: location
    envType: environment
    keyVaultReference: keyVault.name
  }
}

/*──────── Log Analytics ────────*/
module logAnalyticsModule './modules/loga.bicep' = {
  name: 'deployLogAnalytics'
  scope: tutorRG
  params: {
    workspaceName: 'tutor-loganalytics'
    location: location
    retentionInDays: 30
    environment: environment
    keyVaultReference: keyVault.name
    subscriptionId: subscriptionId
  }
}

/*──────── ACR ────────*/
module acrModule './modules/acr.bicep' = {
  name: 'deployContainerRegistry'
  scope: tutorRG
  params: {
    location: location
    environment: environment
    keyVaultReference: keyVault.name
    subscriptionId: subscriptionId
    acrName: acrName
    sku: 'Standard'
  }
}

/*──────── Cosmos DB (unchanged) ────────*/
module cosmosDbModule './modules/cosmos.bicep' = {
  name: 'deployCosmosDb'
  scope: tutorRG
  params: {
    cosmosDbName: 'tutor-cosmosdb'
    location: location
    resourceGroupLocation: tutorRG.location
    environment: environment
    keyVaultReference: keyVault.name
    subscriptionId: subscriptionId
  }
}

/*──────── Container Apps env + first app ────────*/
module containerAppsEnvModule './modules/aca.bicep' = {
  name: 'deployContainerAppsEnv'
  scope: tutorRG
  params: {
    location: location
    infrastructureSubnetId: vnetModule.outputs.containerAppsSubnetId
    logAnalyticsWorkspaceName: logAnalyticsModule.outputs.workspaceName
    envType: environment
    containerAppName: 'tutor-api'
    containerAppImage: '${acrLoginServer}/api:latest'
    acrLoginServer: acrLoginServer
  }
}

/*──────── Azure OpenAI ────────*/
module openAiModule './modules/aoai.bicep' = {
  name: 'deployAzureOpenAI'
  scope: tutorRG
  params: {
    aiServiceAccountName: openAiAccountName
    deployAccount: deployOpenAiAccount
    restore: openAiRestore
    location: location
    customSubDomainName: openAiCustomDomain
    subnetId: vnetModule.outputs.containerAppsSubnetId
    modelDeploymentName: openAiModelDeployment
    modelName: openAiModelName
    modelVersion: openAiModelVersion
    capacity: openAiCapacity
    tags: { project: 'TheTutor', environment: environment }
  }
}

/*──────── Speech Services ────────*/
module speechModule './modules/speech.bicep' = {
  name: 'deploySpeech'
  scope: tutorRG
  params: {
    speechAccountName: speechAccountName
    deployAccount: deploySpeechAccount
    restore: speechRestore
    location: location
    customSubDomainName: speechCustomDomain
    subnetId: vnetModule.outputs.openAiSubnetId
    tags: { project: 'TheTutor', environment: environment }
  }
}

// =================================================================
// Module: Azure Static Web App (enforces HTTPS and CORS policies)
// =================================================================
module staticWebApp './modules/staticwapp.bicep' = {
  name: 'deployStaticWebApp'
  scope: tutorRG
  params: {
    location: location
    repositoryUrl: 'https://github.com/Azure-Samples/tutor.git'
    environment: environment
    keyVaultReference: keyVault.name
  }
}
