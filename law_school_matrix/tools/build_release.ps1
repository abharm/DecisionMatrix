<#!
.SYNOPSIS
Builds a self-contained Windows release of Decision Matrix.

.DESCRIPTION
The resulting ZIP contains only DecisionMatrix.exe and a short readme. User
projects are stored separately in each person's Windows app-data folder, so
the release itself never includes your private decision matrices.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$venv = Join-Path $projectRoot '.build-venv'
$release = Join-Path $projectRoot 'release'
$dist = Join-Path $projectRoot 'dist'

if (-not (Test-Path (Join-Path $venv 'Scripts\python.exe'))) {
    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw 'Python 3.12 or newer is required the first time. Install it from python.org, then run this script again.'
    }
    & py -3.12 -m venv $venv
}

& (Join-Path $venv 'Scripts\python.exe') -m pip install --upgrade pip
& (Join-Path $venv 'Scripts\python.exe') -m pip install -r (Join-Path $projectRoot 'requirements.txt') pyinstaller
& (Join-Path $venv 'Scripts\pyinstaller.exe') --noconfirm --clean --onefile --windowed --name DecisionMatrix --paths (Join-Path $projectRoot 'src') (Join-Path $projectRoot 'src\app\main.py')

New-Item -ItemType Directory -Force -Path $release | Out-Null
Copy-Item (Join-Path $dist 'DecisionMatrix.exe') (Join-Path $release 'DecisionMatrix.exe') -Force
Copy-Item (Join-Path $projectRoot 'tools\release_README.txt') (Join-Path $release 'README.txt') -Force

Compress-Archive -Path (Join-Path $release '*') -DestinationPath (Join-Path $projectRoot 'DecisionMatrix-Windows.zip') -Force
Write-Host "Created $(Join-Path $projectRoot 'DecisionMatrix-Windows.zip')"
