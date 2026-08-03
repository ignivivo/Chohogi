[CmdletBinding()]
param(
  [string]$TargetHome = $HOME,
  [switch]$DryRun,
  [switch]$AdoptExisting
)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$assets = Join-Path $sourceRoot 'assets'
$agentsHome = Join-Path $TargetHome '.agents'
$codexHome = Join-Path $TargetHome '.codex'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$markerName = '.chohogi-owner.json'

function Test-ChohogiOwned([string]$Destination) {
  $marker = Join-Path $Destination $markerName
  if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) { return $false }
  try {
    $value = Get-Content -LiteralPath $marker -Raw -Encoding utf8 | ConvertFrom-Json
    return $value.package -eq 'chohogi'
  } catch { return $false }
}

function Install-ManagedDirectory([string]$Source, [string]$Destination) {
  if (Test-Path -LiteralPath $Destination) {
    if (-not (Test-Path -LiteralPath $Destination -PathType Container)) {
      throw "Installation collision: $Destination is not a directory."
    }
    $owned = Test-ChohogiOwned $Destination
    if (-not $owned -and -not $AdoptExisting) {
      throw "Installation collision: $Destination is not marked as Chohogi-owned. Inspect it, then rerun with -AdoptExisting only if it is a prior Chohogi installation."
    }
    if ($DryRun) { Write-Host "Would replace managed Chohogi directory $Destination"; return }
    Remove-Item -Recurse -Force -LiteralPath $Destination
  } elseif ($DryRun) {
    Write-Host "Would install $Source -> $Destination"; return
  }

  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination) | Out-Null
  Copy-Item -Recurse -Force -LiteralPath $Source -Destination $Destination
  @{ package = 'chohogi'; installedAt = (Get-Date).ToUniversalTime().ToString('o') } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $Destination $markerName) -Encoding utf8
}

function Install-GlobalGuidance([string]$Source, [string]$Destination) {
  $begin='<!-- chohogi:global-guidance:start -->'; $end='<!-- chohogi:global-guidance:end -->'
  $block=Get-Content -LiteralPath $Source -Raw -Encoding utf8
  $old=if(Test-Path $Destination){Get-Content -LiteralPath $Destination -Raw -Encoding utf8}else{''}
  if($DryRun){Write-Host "Would update managed Chohogi guidance block in $Destination"; return}
  New-Item -ItemType Directory -Force -Path (Split-Path -Parent $Destination)|Out-Null
  if($old.Contains($begin) -and $old.Contains($end)){
    $updated=[regex]::Replace($old,"(?s)$([regex]::Escape($begin)).*?$([regex]::Escape($end))",[System.Text.RegularExpressions.MatchEvaluator]{param($m)$block},1)
  } elseif($old.Contains('chohogi:defer=no-flow-no-write')) { $updated=$block
  } elseif([string]::IsNullOrWhiteSpace($old)) { $updated=$block
  } else { $updated=$old.TrimEnd()+"`n`n"+$block+"`n" }
  Set-Content -LiteralPath $Destination -Value $updated -Encoding utf8
}

if (-not (Test-Path (Join-Path $sourceRoot 'manifest.yaml'))) { throw 'Run from a complete Chohogi checkout.' }

$oldGlobal = Join-Path $codexHome 'AGENTS.md'
$newGlobal = Join-Path $assets 'codex\AGENTS.md'
if ((Test-Path $oldGlobal) -and -not $DryRun -and -not (Get-Content -LiteralPath $oldGlobal -Raw -Encoding utf8).Contains('chohogi:global-guidance:start')) {
  $backup = Join-Path $codexHome "AGENTS.pre-chohogi-$stamp.md"
  Copy-Item -LiteralPath $oldGlobal -Destination $backup
  Write-Host "Backed up existing global guidance to $backup"
}

Install-ManagedDirectory (Join-Path $assets 'agents\chohogi') (Join-Path $agentsHome 'chohogi')
Get-ChildItem -Directory (Join-Path $assets 'agents\skills') | ForEach-Object {
  Install-ManagedDirectory $_.FullName (Join-Path $agentsHome "skills\$($_.Name)")
}
Install-GlobalGuidance $newGlobal $oldGlobal

Write-Host 'Chohogi installation complete. Run tooling/verify-install.ps1 against this target.'
