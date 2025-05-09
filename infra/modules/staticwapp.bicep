targetScope = 'resourceGroup'

@description('The name of the Static Web App resource.')
param staticWebAppName string = 'tutor-staticweb'

@description('The location for the Static Web App resource.')
param location string

@description('The repository URL for the Static Web App (GitHub URL).')
param repositoryUrl string

@description('The branch to use from the repository.')
param branch string = 'main'

@description('The folder path within the repository where your application code is located.')
param appLocation string = 'app'

@description('The folder path within the repository where your API code is located (use an empty string if not applicable).')
param apiLocation string = 'api'

@description('The folder path within the repository where your build artifacts are located.')
param appArtifactLocation string = 'build'

@description('Keyvault secret for the Log Analytics Workspace.')
param keyVaultReference string

@description('Environment indicator to adjust address space accordingly')
param environment string


resource staticWebApp 'Microsoft.Web/staticSites@2022-03-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    repositoryUrl: repositoryUrl
    branch: branch
    buildProperties: {
      appLocation: appLocation
      apiLocation: apiLocation
      appArtifactLocation: appArtifactLocation
    }
  }
  tags: {
    project: 'TheTutor'
    environment: environment
    keyVaultReference: keyVaultReference
  }
}

output staticWebAppId string = staticWebApp.id
