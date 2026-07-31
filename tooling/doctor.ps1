[CmdletBinding()]
param([string]$TargetHome = $HOME)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$requiredSource = @(
  'manifest.yaml',
  'assets\codex\AGENTS.md',
  'assets\agents\chohogi\trunk\conductor.md',
  'assets\agents\chohogi\roots\constitution.md',
  'assets\agents\chohogi\amyloplast\index.yaml'
)
$requiredSkills = @('learning', 'homeostasis', 'accessibility', 'core-web-vitals', 'grill-me', 'performance', 'react-async-state-safety', 'security-and-hardening')
$errors = [System.Collections.Generic.List[string]]::new()

foreach ($item in $requiredSource) {
  if (-not (Test-Path (Join-Path $sourceRoot $item))) { $errors.Add("Missing source asset: $item") }
}
foreach ($name in $requiredSkills) {
  $path = Join-Path $sourceRoot "assets\agents\skills\$name\SKILL.md"
  if (-not (Test-Path $path)) { $errors.Add("Missing source skill: $name") }
}

$forbidden = 'codex-native-meta-harness|learning-loop|operating-harness|adoption-ledger'
$activeSource = Join-Path $sourceRoot 'assets'
$matches = @(Get-ChildItem -Recurse -File $activeSource | Select-String -Pattern $forbidden)
if ($matches.Count -gt 0) { $errors.Add('Active source still contains retired controller names or reference-ledger paths.') }

$installedGuidance = Join-Path $TargetHome '.codex\AGENTS.md'
if (-not (Test-Path $installedGuidance)) { $errors.Add("Missing installed global guidance: $installedGuidance") }
foreach ($name in $requiredSkills) {
  $installed = Join-Path $TargetHome ".agents\skills\$name\SKILL.md"
  if (-not (Test-Path $installed)) { $errors.Add("Missing installed skill: $name") }
}
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\conductor.md'))) { $errors.Add('Missing installed conductor.') }

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  exit 1
}
Write-Host 'Chohogi doctor: PASS (source and installed assets are self-contained).'
