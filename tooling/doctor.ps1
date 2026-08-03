[CmdletBinding()]
param([string]$TargetHome = $HOME)

$ErrorActionPreference = 'Stop'
$sourceRoot = Split-Path -Parent $PSScriptRoot
$requiredSource = @(
  'manifest.yaml',
  'tooling\resolve-python.ps1',
  'tooling\verify-replay-evaluation.py',
  'assets\codex\AGENTS.md',
  'assets\agents\chohogi\trunk\conductor.md',
  'assets\agents\chohogi\trunk\execution-allocation.md',
  'assets\agents\chohogi\trunk\capability-selection.md',
  'assets\agents\chohogi\trunk\skill-adoption.md',
  'assets\agents\chohogi\trunk\context-packet.md',
  'assets\agents\chohogi\xylem\execution-methods.md',
  'assets\agents\chohogi\xylem\provenance.json',
  'assets\agents\chohogi\trunk\routes\product-decision.md',
  'assets\agents\chohogi\trunk\routes\delivery.md',
  'assets\agents\chohogi\trunk\routes\debugging.md',
  'assets\agents\chohogi\trunk\evals\route-fixtures.json',
  'assets\agents\chohogi\trunk\evals\execution-fixtures.json',
  'assets\agents\chohogi\trunk\evals\capability-fixtures.json',
  'assets\agents\chohogi\trunk\evals\replay-result.schema.json',
  'assets\agents\chohogi\trunk\evals\replay-result.example.json',
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
elseif (-not (Get-Content -LiteralPath $installedGuidance -Raw -Encoding utf8).Contains('<!-- chohogi:global-guidance:start -->')) { $errors.Add('Installed global guidance does not retain the managed Chohogi adapter block.') }
foreach ($name in $requiredSkills) {
  $installed = Join-Path $TargetHome ".agents\skills\$name\SKILL.md"
  if (-not (Test-Path $installed)) { $errors.Add("Missing installed skill: $name") }
}
$installedLifecycle = Join-Path $TargetHome '.agents\skills\homeostasis\references\skill-lifecycle.md'
if (-not (Test-Path $installedLifecycle)) { $errors.Add('Missing installed skill lifecycle reference.') }
$installedConductor = Join-Path $TargetHome '.agents\chohogi\trunk\conductor.md'
if (-not (Test-Path $installedConductor)) { $errors.Add('Missing installed conductor.') }
elseif (-not (Get-Content -LiteralPath $installedConductor -Raw -Encoding utf8).Contains('routes/<flow>.md')) { $errors.Add('Installed conductor does not reference daily route contracts.') }
$installedAllocation = Join-Path $TargetHome '.agents\chohogi\trunk\execution-allocation.md'
if (-not (Test-Path $installedAllocation)) { $errors.Add('Missing installed execution-allocation contract.') }
elseif (-not (Get-Content -LiteralPath $installedAllocation -Raw -Encoding utf8).Contains('<!-- chohogi:execution-choice=internal -->')) { $errors.Add('Installed execution-allocation contract does not retain controller boundary.') }
$installedCapability = Join-Path $TargetHome '.agents\chohogi\trunk\capability-selection.md'
if (-not (Test-Path $installedCapability)) { $errors.Add('Missing installed capability-selection contract.') }
elseif (-not (Get-Content -LiteralPath $installedCapability -Raw -Encoding utf8).Contains('<!-- chohogi:provider-authority=capability-only -->')) { $errors.Add('Installed capability-selection contract does not retain provider boundary.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\skill-adoption.md'))) { $errors.Add('Missing installed skill-adoption contract.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\context-packet.md'))) { $errors.Add('Missing installed context packet contract.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\xylem\execution-methods.md'))) { $errors.Add('Missing installed xylem execution methods.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\xylem\provenance.json'))) { $errors.Add('Missing installed xylem provenance.') }
foreach ($route in @('product-decision', 'delivery', 'debugging')) {
  $installedRoute = Join-Path $TargetHome ".agents\chohogi\trunk\routes\$route.md"
  if (-not (Test-Path $installedRoute)) { $errors.Add("Missing installed route: $route") }
}
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\route-fixtures.json'))) { $errors.Add('Missing installed route fixtures.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\execution-fixtures.json'))) { $errors.Add('Missing installed execution fixtures.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\capability-fixtures.json'))) { $errors.Add('Missing installed capability fixtures.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\replay-result.schema.json'))) { $errors.Add('Missing installed replay result schema.') }
if (-not (Test-Path (Join-Path $TargetHome '.agents\chohogi\trunk\evals\replay-result.example.json'))) { $errors.Add('Missing installed replay result example.') }

$managedTrees = @(
  @{ Source = Join-Path $sourceRoot 'assets\agents\chohogi'; Destination = Join-Path $TargetHome '.agents\chohogi' },
  @{ Source = Join-Path $sourceRoot 'assets\agents\skills'; Destination = Join-Path $TargetHome '.agents\skills' }
)
foreach ($tree in $managedTrees) {
  if (-not (Test-Path $tree.Source) -or -not (Test-Path $tree.Destination)) { continue }
  Get-ChildItem -Recurse -File -LiteralPath $tree.Source | ForEach-Object {
    $relative = $_.FullName.Substring($tree.Source.Length).TrimStart('\')
    $installedPath = Join-Path $tree.Destination $relative
    if (-not (Test-Path $installedPath)) { $errors.Add("Managed asset missing from installed tree: $relative"); return }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash -ne (Get-FileHash -Algorithm SHA256 -LiteralPath $installedPath).Hash) {
      $errors.Add("Managed asset differs from Git source: $relative")
    }
  }
}

if ($errors.Count -gt 0) {
  $errors | ForEach-Object { Write-Error $_ }
  exit 1
}
Write-Host 'Chohogi install integrity: PASS (source and installed assets are self-contained and synchronized).'
