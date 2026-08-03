[CmdletBinding()]
param(
  [string]$TargetHome = $HOME,
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

Copy-Directory (Join-Path $assets 'agents\chohogi') (Join-Path $agentsHome 'chohogi')
Get-ChildItem -Directory (Join-Path $assets 'agents\skills') | ForEach-Object {
  Copy-Directory $_.FullName (Join-Path $agentsHome "skills\$($_.Name)")
}

Install-GlobalGuidance $newGlobal $oldGlobal

Write-Host 'Chohogi installation complete. Run tooling/verify-install.ps1 against this target.'
