[CmdletBinding()]
param([string]$TargetHome = $HOME)

$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'doctor.ps1') -TargetHome $TargetHome
exit $LASTEXITCODE
