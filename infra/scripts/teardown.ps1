[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroupName,

    [switch]$SkipConfirmation
)

$ErrorActionPreference = "Stop"

Write-Host "Cost guardrail: deleting the lab resource group is the recommended way to stop all Azure spend for this MicroHack environment." -ForegroundColor Yellow
Write-Host "This permanently removes Azure OpenAI deployments, AI Search indexes, Storage data, Container Apps, logs, and telemetry in '$ResourceGroupName'." -ForegroundColor Yellow

if (-not $SkipConfirmation) {
    $confirmation = Read-Host "Type DELETE to remove resource group '$ResourceGroupName'"
    if ($confirmation -ne "DELETE") {
        Write-Host "Teardown cancelled."
        exit 0
    }
}

az group delete --name $ResourceGroupName --yes --no-wait
Write-Host "Delete submitted. Check status with: az group exists --name $ResourceGroupName"
