// vnet.bicep
targetScope = 'resourceGroup'

@description('Name of the virtual network')
param vnetName       string = 'tutor-vnet'

@description('Azure region for the VNet')
param location       string

@description('Key Vault secret reference (for tagging)')
param keyVaultReference string

@description('Deployment environment (dev | test | prod)')
param envType        string


// ────────────────────────────────────────────────────────────
// Network Security Groups
// ────────────────────────────────────────────────────────────
resource managementNSG 'Microsoft.Network/networkSecurityGroups@2020-11-01' = {
  name: 'mgmt-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-SSH'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '22'
          sourceAddressPrefix: '*' 
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1000
          direction: 'Inbound'
        }
      }
    ]
  }
  tags: {
    environment: envType
    keyVaultReference: keyVaultReference
  }
}

resource dataNSG 'Microsoft.Network/networkSecurityGroups@2020-11-01' = {
  name: 'data-nsg'
  location: location
  properties: {
    securityRules: [
      {
        name: 'Allow-AppTraffic'
        properties: {
          protocol: 'Tcp'
          sourcePortRange: '*'
          destinationPortRange: '443'
          sourceAddressPrefix: '*'
          destinationAddressPrefix: '*'
          access: 'Allow'
          priority: 1000
          direction: 'Inbound'
        }
      }
    ]
  }
  tags: {
    environment: envType
    keyVaultReference: keyVaultReference
  }
}

// ────────────────────────────────────────────────────────────
// Virtual Network with subnets & service endpoints
// ────────────────────────────────────────────────────────────
resource virtualNetwork 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [ '10.0.0.0/22' ]
    }
    subnets: [
      {
        name: 'management'
        properties: {
          addressPrefix: '10.0.0.0/23'
          networkSecurityGroup: { id: managementNSG.id }
          serviceEndpoints: [
            { service: 'Microsoft.CognitiveServices' }
            { service: 'Microsoft.ContainerRegistry' }           // ← add this
          ]
        }
      }
      {
        name: 'data'
        properties: {
          addressPrefix: '10.0.2.0/24'
          networkSecurityGroup: { id: dataNSG.id }
          serviceEndpoints: [                        // Enable service endpoint
            { service: 'Microsoft.CognitiveServices' }
          ]
        }
      }
    ]
  }
  tags: {
    environment: envType
    keyVaultReference: keyVaultReference
  }
}

// ────────────────────────────────────────────────────────────
// Outputs for downstream modules
// ────────────────────────────────────────────────────────────
@description('Subnet ID for Container Apps (management)')
output containerAppsSubnetId string = resourceId(
  'Microsoft.Network/virtualNetworks/subnets',
  vnetName, 'management'
)

@description('Subnet ID for AI workloads (data)')
output openAiSubnetId      string = resourceId(
  'Microsoft.Network/virtualNetworks/subnets',
  vnetName, 'data'
)
