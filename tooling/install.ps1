[CmdletBinding()]
param(
  [string]$TargetHome = $HOME,
  [switch]$MigrateLegacy,
  [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$assets = Join-Path $sourceRoot 'assets'
$agentsHome = Join-Path $TargetHome '.agents'
$codexHome = Join-Path $TargetHome '.codex'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

function Copy-Directory([string]$Source, [string]$Destination) {
  if ($DryRun) { Write-Host "Would install $Source -> $Destination"; return }
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
  if (Test-Path $Destination) { Remove-Item -Recurse -Force -LiteralPath $Destination }
  Copy-Item -Recurse -Force -LiteralPath $Source -Destination $Destination
}

if (-not (Test-Path (Join-Path $sourceRoot 'manifest.yaml'))) { throw 'Run from a complete Chohogi checkout.' }

$oldGlobal = Join-Path $codexHome 'AGENTS.md'
$newGlobal = Join-Path $assets 'codex\AGENTS.md'
if ((Test-Path $oldGlobal) -and -not $DryRun) {
  $backup = Join-Path $codexHome "AGENTS.pre-chohogi-$stamp.md"
  Copy-Item -LiteralPath $oldGlobal -Destination $backup
  Write-Host "Backed up existing global guidance to $backup"
}

Copy-Directory (Join-Path $assets 'agents\chohogi') (Join-Path $agentsHome 'chohogi')
Get-ChildItem -Directory (Join-Path $assets 'agents\skills') | ForEach-Object {
  Copy-Directory $_.FullName (Join-Path $agentsHome "skills\$($_.Name)")
}

if ($DryRun) { Write-Host "Would install $newGlobal -> $oldGlobal" }
else {
  New-Item -ItemType Directory -Force -Path $codexHome | Out-Null
  Copy-Item -Force -LiteralPath $newGlobal -Destination $oldGlobal
}

if ($MigrateLegacy) {
  $legacySkills = @('codex-native-meta-harness', 'learning-loop')
  foreach ($name in $legacySkills) {
    $path = Join-Path $agentsHome "skills\$name"
    if (Test-Path $path) {
      if ($DryRun) { Write-Host "Would remove legacy discovery asset $path" }
      else { Remove-Item -Recurse -Force -LiteralPath $path; Write-Host "Removed legacy discovery asset $path" }
    }
  }
  $legacyHarness = Join-Path $agentsHome 'harness'
  if (Test-Path $legacyHarness) {
    if ($DryRun) { Write-Host "Would remove legacy harness source $legacyHarness" }
    else { Remove-Item -Recurse -Force -LiteralPath $legacyHarness; Write-Host "Removed legacy harness source $legacyHarness" }
  }
}

Write-Host 'Chohogi installation complete. Run tooling/doctor.ps1 against this target.'
