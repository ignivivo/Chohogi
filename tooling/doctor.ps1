[CmdletBinding()]
param([string]$TargetHome = $HOME)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$requiredSource = @(
  'manifest.yaml',
  'assets\codex\AGENTS.md',
  'assets\agents\chohogi\trunk\conductor.md',
  'assets\agents\chohogi\trunk\routes\product-decision.md',
  'assets\agents\chohogi\trunk\routes\delivery.md',
  'assets\agents\chohogi\trunk\routes\debugging.md',
  'assets\agents\chohogi\trunk\evals\route-fixtures.json',
  'assets\agents\chohogi\roots\constitution.md',
  'assets\agents\chohogi\amyloplast\index.yaml',
  'assets\agents\skills\homeostasis\references\skill-lifecycle.md'
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
elseif (-not (Get-Content -LiteralPath $installedGuidance -Raw -Encoding utf8).Contains('trunk/routes/<flow>.md')) { $errors.Add('Installed global guidance does not reference the selected daily route contract.') }
foreach ($name in $requiredSkills) {
  $installed = Join-Path $TargetHome ".agents\skills\$name\SKILL.md"
  if (-not (Test-Path $installed)) { $errors.Add("Missing installed skill: $name") }
}
$installedLifecycle = Join-Path $TargetHome '.agents\skills\homeostasis\references\skill-lifecycle.md'
if (-not (Test-Path $installedLifecycle)) { $errors.Add('Missing installed skill lifecycle reference.') }
$installedConductor = Join-Path $TargetHome '.agents\chohogi\trunk\conductor.md'
if (-not (Test-Path $installedConductor)) { $errors.Add('Missing installed conductor.') }
elseif (-not (Get-Content -LiteralPath $installedConductor -Raw -Encoding utf8).Contains('routes/<flow>.md')) { $errors.Add('Installed conductor does not reference daily route contracts.') }
foreach ($route in @('product-decision', 'delivery', 'debugging')) {
  $installedRoute = Join-Path $TargetHome ".agents\chohogi\trunk\routes\$route.md"
  if (-not (Test-Path $installedRoute)) { $errors.Add("Missing installed route: $route") }
}
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\route-fixtures.json'))) { $errors.Add('Missing installed route fixtures.') }

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  exit 1
}
Write-Host 'Chohogi doctor: PASS (source and installed assets are self-contained).'
