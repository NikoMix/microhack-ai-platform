[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [string]$Location = "swedencentral",

    [string]$ParametersFile = (Join-Path $PSScriptRoot "..\main.bicepparam"),

    [string]$DeploymentName = ("contoso-ai-{0:yyyyMMddHHmmss}" -f (Get-Date)),

    [switch]$SkipConfirmation
)

$ErrorActionPreference = "Stop"

Write-Host "Cost guardrail: this template creates Azure OpenAI/Azure AI Services, AI Search Basic, Container Apps, Log Analytics, App Insights, and Storage." -ForegroundColor Yellow
Write-Host "Expected workshop posture: Container Apps min replicas defaults to 0; delete the resource group after the lab to stop spend." -ForegroundColor Yellow
Write-Host "Estimated cost depends on region/model quota and usage. Review pricing before deploying: https://azure.microsoft.com/pricing/calculator/" -ForegroundColor Yellow

if (-not $SkipConfirmation) {
    $confirmation = Read-Host "Type DEPLOY to create/update resource group '$ResourceGroupName' in '$Location'"
    if ($confirmation -ne "DEPLOY") {
        Write-Host "Deployment cancelled."
        exit 0
    }
}

az group create --name $ResourceGroupName --location $Location --tags workload=contoso-ai-assistant scenario=ttt-microhack costControl=delete-after-lab | Out-Null

Write-Host "Running what-if before deployment..."
az deployment group what-if `
    --name $DeploymentName `
    --resource-group $ResourceGroupName `
    --template-file (Join-Path $PSScriptRoot "..\main.bicep") `
    --parameters $ParametersFile `
    --parameters location=$Location

if (-not $SkipConfirmation) {
    $confirmation = Read-Host "Review the what-if output. Type APPLY to deploy"
    if ($confirmation -ne "APPLY") {
        Write-Host "Deployment cancelled after what-if."
        exit 0
    }
}

az deployment group create `
    --name $DeploymentName `
    --resource-group $ResourceGroupName `
    --template-file (Join-Path $PSScriptRoot "..\main.bicep") `
    --parameters $ParametersFile `
    --parameters location=$Location

Write-Host "Deployment complete. To stop spend, run infra\scripts\teardown.ps1 -ResourceGroupName $ResourceGroupName."
