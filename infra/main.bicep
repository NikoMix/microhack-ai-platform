targetScope = 'resourceGroup'

@description('Azure region for all resources. Choose a region where Azure OpenAI and the requested model deployments are available.')
param location string = resourceGroup().location

@description('Short environment name used in resource names and tags.')
@minLength(2)
@maxLength(12)
param environmentName string = 'contoso'

@description('Token appended to globally-unique names. Defaults to a deterministic value for this resource group and environment.')
@minLength(4)
@maxLength(12)
param resourceToken string = substring(toLower(uniqueString(resourceGroup().id, environmentName)), 0, 8)

@description('Tags applied to all resources.')
param tags object = {
  workload: 'contoso-ai-assistant'
  scenario: 'ttt-microhack'
  repo: 'NikoMix/microhack-ai-platform'
}

@description('Container image for the FastAPI app. Replace with a private registry image after wiring CI/CD image publishing.')
param containerImage string = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'

@description('Azure OpenAI chat model deployment name.')
param chatDeploymentName string = 'gpt-4o-mini'

@description('Azure OpenAI chat model name.')
param chatModelName string = 'gpt-4o-mini'

@description('Azure OpenAI chat model version.')
param chatModelVersion string = '2024-07-18'

@description('Azure OpenAI embedding model deployment name.')
param embeddingDeploymentName string = 'text-embedding-3-small'

@description('Azure OpenAI embedding model name.')
param embeddingModelName string = 'text-embedding-3-small'

@description('Azure OpenAI embedding model version.')
param embeddingModelVersion string = '1'

@description('Azure OpenAI deployment capacity in thousands of tokens per minute for Standard deployments.')
@minValue(1)
@maxValue(100)
param openAiDeploymentCapacity int = 10

@description('AI Foundry model deployment name.')
param foundryDeploymentName string = 'foundry-gpt-4o-mini'

@description('Azure AI Search SKU. Basic is cost-conscious for workshops; standard is recommended for larger teams.')
@allowed([
  'basic'
  'standard'
])
param searchSkuName string = 'basic'

@description('Set to true to use semantic ranker on AI Search. Requires a region/SKU where semantic ranker is available.')
param enableSearchSemanticRanker bool = true

@description('Container App minimum replicas. Keep this at 0 to stop compute spend when idle.')
@minValue(0)
@maxValue(5)
param containerMinReplicas int = 0

@description('Container App maximum replicas.')
@minValue(1)
@maxValue(20)
param containerMaxReplicas int = 3

var baseName = toLower(replace(environmentName, '-', ''))
var suffix = resourceToken
var uniqueSuffix = '${baseName}${suffix}'

var logAnalyticsName = 'log-${baseName}-${suffix}'
var appInsightsName = 'appi-${baseName}-${suffix}'
var identityName = 'id-${baseName}-${suffix}'
var aiServicesName = 'cog-ai-${baseName}-${suffix}'
var aiHubName = 'aih-${baseName}-${suffix}'
var aiProjectName = 'aip-${baseName}-${suffix}'
var openAiName = 'cog-oai-${baseName}-${suffix}'
var searchName = substring('srch-${uniqueSuffix}', 0, 60)
var storageName = substring('st${uniqueSuffix}', 0, 24)
var contentSafetyName = 'cog-cs-${baseName}-${suffix}'
var containerEnvironmentName = 'cae-${baseName}-${suffix}'
var containerAppName = 'ca-${baseName}-${suffix}'

var cognitiveServicesOpenAiUserRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd')
var cognitiveServicesUserRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
var azureAiDeveloperRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '64702f94-c441-49e6-a78b-ef80e0188fee')
var searchIndexDataContributorRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
var searchIndexDataReaderRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '1407120a-92aa-4202-b7e9-c0e197c71c8f')
var storageBlobDataContributorRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
var monitoringMetricsPublisherRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3913510d-42f4-4e42-8a64-420c390055eb')

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2025-02-01' = {
  name: logAnalyticsName
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  tags: tags
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    DisableLocalAuth: true
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: identityName
  location: location
  tags: tags
}

module storageAccount 'modules/storage-account.bicep' = {
  name: 'storage-${storageName}'
  params: {
    name: storageName
    location: location
    tags: tags
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2025-01-01' existing = {
  name: storageName
}

resource aiServices 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: aiServicesName
  location: location
  tags: tags
  kind: 'AIServices'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  sku: {
    name: 'S0'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiServicesName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: false
  }
}

resource aiFoundryDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: aiServices
  name: foundryDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: openAiDeploymentCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: chatModelName
      version: chatModelVersion
    }
    raiPolicyName: 'Microsoft.DefaultV2'
  }
}

resource aiHub 'Microsoft.MachineLearningServices/workspaces@2025-04-01-preview' = {
  name: aiHubName
  location: location
  tags: tags
  kind: 'Hub'
  dependsOn: [
    storageAccount
  ]
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    friendlyName: 'Contoso AI Assistant Hub'
    description: 'AI Foundry hub for the Train-the-Trainer MicroHack.'
    applicationInsights: appInsights.id
    storageAccount: storage.id
    publicNetworkAccess: 'Enabled'
  }
}

resource aiProject 'Microsoft.MachineLearningServices/workspaces@2025-04-01-preview' = {
  name: aiProjectName
  location: location
  tags: tags
  kind: 'Project'
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    friendlyName: 'Contoso AI Assistant Project'
    description: 'Project for the agentic RAG reference application.'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

resource openAi 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: openAiName
  location: location
  tags: tags
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAiName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: false
  }
}

resource chatDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: openAi
  name: chatDeploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: openAiDeploymentCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: chatModelName
      version: chatModelVersion
    }
    raiPolicyName: 'Microsoft.DefaultV2'
  }
}

resource embeddingDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-04-01-preview' = {
  parent: openAi
  name: embeddingDeploymentName
  sku: {
    name: 'Standard'
    capacity: openAiDeploymentCapacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: embeddingModelName
      version: embeddingModelVersion
    }
  }
}

resource search 'Microsoft.Search/searchServices@2025-05-01' = {
  name: searchName
  location: location
  tags: tags
  sku: {
    name: searchSkuName
  }
  properties: {
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
    }
    disableLocalAuth: true
    encryptionWithCmk: {
      enforcement: 'Unspecified'
    }
    hostingMode: 'Default'
    networkRuleSet: {
      bypass: 'AzureServices'
      ipRules: []
    }
    partitionCount: 1
    publicNetworkAccess: 'enabled'
    replicaCount: 1
    semanticSearch: enableSearchSemanticRanker ? 'standard' : 'disabled'
  }
}

resource contentSafety 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: contentSafetyName
  location: location
  tags: tags
  kind: 'ContentSafety'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: contentSafetyName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

resource containerEnvironment 'Microsoft.App/managedEnvironments@2025-02-02-preview' = {
  name: containerEnvironmentName
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
}

resource containerApp 'Microsoft.App/containerApps@2025-02-02-preview' = {
  name: containerAppName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerEnvironment.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        allowInsecure: false
        external: true
        targetPort: 8000
        transport: 'http'
      }
    }
    template: {
      containers: [
        {
          name: 'api'
          image: containerImage
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: managedIdentity.properties.clientId
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsights.properties.ConnectionString
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openAi.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_CHAT_DEPLOYMENT'
              value: chatDeployment.name
            }
            {
              name: 'AZURE_OPENAI_EMBEDDING_DEPLOYMENT'
              value: embeddingDeployment.name
            }
            {
              name: 'AZURE_AI_FOUNDRY_ENDPOINT'
              value: aiServices.properties.endpoint
            }
            {
              name: 'AZURE_AI_FOUNDRY_PROJECT_NAME'
              value: aiProject.name
            }
            {
              name: 'AZURE_AI_SEARCH_ENDPOINT'
              value: 'https://${search.name}.search.windows.net'
            }
            {
              name: 'AZURE_CONTENT_SAFETY_ENDPOINT'
              value: contentSafety.properties.endpoint
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: containerMinReplicas
        maxReplicas: containerMaxReplicas
        rules: [
          {
            name: 'http-scale'
            http: {
              metadata: {
                concurrentRequests: '20'
              }
            }
          }
        ]
      }
    }
  }
}

resource openAiUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(openAi.id, managedIdentity.id, cognitiveServicesOpenAiUserRoleId)
  scope: openAi
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: cognitiveServicesOpenAiUserRoleId
  }
}

resource aiServicesUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiServices.id, managedIdentity.id, cognitiveServicesUserRoleId)
  scope: aiServices
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: cognitiveServicesUserRoleId
  }
}

resource aiHubDeveloperAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiHub.id, managedIdentity.id, azureAiDeveloperRoleId)
  scope: aiHub
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: azureAiDeveloperRoleId
  }
}

resource aiProjectDeveloperAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(aiProject.id, managedIdentity.id, azureAiDeveloperRoleId)
  scope: aiProject
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: azureAiDeveloperRoleId
  }
}

resource searchContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, managedIdentity.id, searchIndexDataContributorRoleId)
  scope: search
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchIndexDataContributorRoleId
  }
}

resource searchReaderAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(search.id, managedIdentity.id, searchIndexDataReaderRoleId)
  scope: search
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: searchIndexDataReaderRoleId
  }
}

resource storageBlobAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storage.id, managedIdentity.id, storageBlobDataContributorRoleId)
  scope: storage
  dependsOn: [
    storageAccount
  ]
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: storageBlobDataContributorRoleId
  }
}

resource contentSafetyUserAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(contentSafety.id, managedIdentity.id, cognitiveServicesUserRoleId)
  scope: contentSafety
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: cognitiveServicesUserRoleId
  }
}

resource appInsightsMetricsAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(appInsights.id, managedIdentity.id, monitoringMetricsPublisherRoleId)
  scope: appInsights
  properties: {
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: monitoringMetricsPublisherRoleId
  }
}

@description('Container App HTTPS URL.')
output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'

@description('User-assigned managed identity client ID for DefaultAzureCredential AZURE_CLIENT_ID.')
output managedIdentityClientId string = managedIdentity.properties.clientId

@description('Azure OpenAI endpoint.')
output azureOpenAiEndpoint string = openAi.properties.endpoint

@description('Azure AI Foundry account endpoint.')
output azureAiFoundryEndpoint string = aiServices.properties.endpoint

@description('Azure AI Foundry hub resource ID.')
output azureAiFoundryHubResourceId string = aiHub.id

@description('Azure AI Foundry project resource ID.')
output azureAiFoundryProjectResourceId string = aiProject.id

@description('Azure AI Search endpoint.')
output azureAiSearchEndpoint string = 'https://${search.name}.search.windows.net'

@description('Azure AI Content Safety endpoint.')
output azureContentSafetyEndpoint string = contentSafety.properties.endpoint

@description('Application Insights connection string. This is not a secret and is emitted for app configuration.')
output applicationInsightsConnectionString string = appInsights.properties.ConnectionString
