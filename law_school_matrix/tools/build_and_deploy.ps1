<#!
.SYNOPSIS
Builds Decision Matrix and replaces the desktop application's executable.

.DESCRIPTION
Edit the files under src, close DecisionMatrix.exe if it is open, then run this
script. It invokes build_release.ps1 and copies the resulting executable and
readme into the specified application folder.
#>
[CmdletBinding()]
param(
    [string]$Destination = (Join-Path ([Environment]::GetFolderPath('Desktop')) 'DM Application')
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$running = Get-Process -Name DecisionMatrix -ErrorAction SilentlyContinue
if ($running) {
    throw 'Close Decision Matrix before deploying an update, then run this script again.'
}

& (Join-Path $PSScriptRoot 'build_release.ps1')
New-Item -ItemType Directory -Force -Path $Destination | Out-Null
Copy-Item (Join-Path $projectRoot 'release\DecisionMatrix.exe') (Join-Path $Destination 'DecisionMatrix.exe') -Force
Copy-Item (Join-Path $projectRoot 'release\README.txt') (Join-Path $Destination 'README.txt') -Force
Write-Host "Updated $Destination"
