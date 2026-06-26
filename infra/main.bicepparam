using './main.bicep'

param location = 'swedencentral'
param environmentName = 'contoso'
param containerImage = 'mcr.microsoft.com/azuredocs/containerapps-helloworld:latest'
param chatDeploymentName = 'gpt-4o-mini'
param chatModelName = 'gpt-4o-mini'
param chatModelVersion = '2024-07-18'
param embeddingDeploymentName = 'text-embedding-3-small'
param embeddingModelName = 'text-embedding-3-small'
param embeddingModelVersion = '1'
param foundryDeploymentName = 'foundry-gpt-4o-mini'
param openAiDeploymentCapacity = 10
param searchSkuName = 'basic'
param enableSearchSemanticRanker = true
param containerMinReplicas = 0
param containerMaxReplicas = 3
param tags = {
  workload: 'contoso-ai-assistant'
  scenario: 'ttt-microhack'
  owner: 'microhack-trainer'
  costControl: 'delete-after-lab'
}
