[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

& (Join-Path $PSScriptRoot 'export-portfolio.ps1')

& (Join-Path $PSScriptRoot 'export-video.ps1')

& (Join-Path $PSScriptRoot 'validate.ps1')

Write-Host 'Todos los entregables fueron generados correctamente.' -ForegroundColor Green
