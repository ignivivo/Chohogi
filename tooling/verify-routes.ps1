[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$dailyRoutes = @('product-decision', 'delivery', 'debugging')
$branches = @('learning', 'homeostasis')
$flows = @($dailyRoutes + $branches)
$selectionKinds = @('direct', 'defer', 'daily-route', 'branch')
$mutationAuthorities = @('none', 'requested')
$deferMarker = '<!-- chohogi:defer=no-flow-no-write -->'
$deferRequiredArtifacts = @('evidence-gap', 'no-change', 'reentry-condition')
$requiredSections = @('role', 'entry', 'negative-scope', 'input', 'method', 'optional-capabilities', 'exit', 'next')

function Test-NonEmptyString {
  param($Value)
  return $Value -is [string] -and -not [string]::IsNullOrWhiteSpace($Value)
}

function Test-ExactStringSet {
  param($Value, [string[]]$Expected)
  if (-not ($Value -is [System.Array])) { return $false }
  if ($Value.Count -ne $Expected.Count) { return $false }
  if (@($Value | Where-Object { -not (Test-NonEmptyString $_) }).Count -gt 0) { return $false }
  $actual = [System.Collections.Generic.HashSet[string]]::new([string[]]$Value)
  return $actual.SetEquals([string[]]$Expected)
}

function Test-StringArray {
  param($Value)
  return ($Value -is [System.Array]) -and @($Value | Where-Object { -not (Test-NonEmptyString $_) }).Count -eq 0
}

function Validate-DeferPolicyText {
  param([string]$Label, [string]$Text)
  if (([regex]::Matches($Text, [regex]::Escape($deferMarker))).Count -ne 1) {
    return @("$Label must contain exactly one defer no-flow/no-write marker.")
  }
  return @()
}

function Validate-RouteText {
  param([string]$Route, [string]$Text)
  $errors = [System.Collections.Generic.List[string]]::new()
  $routeMarker = "<!-- chohogi:route=$Route -->"
  if (([regex]::Matches($Text, [regex]::Escape($routeMarker))).Count -ne 1) {
    $errors.Add("Route $Route must contain exactly one route marker.")
  }

  $positions = [System.Collections.Generic.List[object]]::new()
  foreach ($section in $requiredSections) {
    $marker = "<!-- chohogi:section=$section -->"
    if (([regex]::Matches($Text, [regex]::Escape($marker))).Count -ne 1) {
      $errors.Add("Route $Route must contain exactly one section marker: $section")
      continue
    }
    $positions.Add([pscustomobject]@{ Section = $section; Start = $Text.IndexOf($marker); Marker = $marker })
  }
  if ($positions.Count -ne $requiredSections.Count) { return $errors.ToArray() }

  $previous = -1
  foreach ($position in $positions) {
    if ($position.Start -le $previous) {
      $errors.Add("Route $Route section markers are not in required order.")
      return $errors.ToArray()
    }
    $previous = $position.Start
  }
  for ($index = 0; $index -lt $positions.Count; $index++) {
    $position = $positions[$index]
    $end = if ($index + 1 -lt $positions.Count) { $positions[$index + 1].Start } else { $Text.Length }
    $body = $Text.Substring($position.Start + $position.Marker.Length, $end - ($position.Start + $position.Marker.Length))
    if ([string]::IsNullOrWhiteSpace($body)) { $errors.Add("Route $Route section is empty: $($position.Section)") }
  }
  return $errors.ToArray()
}

function Validate-FixtureDocument {
  param($Data)
  $errors = [System.Collections.Generic.List[string]]::new()
  if (-not ($Data -is [pscustomobject])) { return @('Route fixture document must be a JSON object.') }
  if ($Data.schemaVersion -ne 3) { $errors.Add('Route fixture schemaVersion must be 3.') }
  if (-not (Test-ExactStringSet $Data.selectionKinds $selectionKinds)) { $errors.Add('Route fixture selectionKinds must exactly declare direct, defer, daily-route, and branch.') }
  if (-not (Test-ExactStringSet $Data.mutationAuthorities $mutationAuthorities)) { $errors.Add('Route fixture mutationAuthorities must exactly declare none and requested.') }

  $fixtures = $Data.fixtures
  if (-not ($fixtures -is [System.Array]) -or $fixtures.Count -lt 14) {
    $errors.Add('Route fixtures must contain at least 14 cases.')
    return $errors.ToArray()
  }

  $ids = [System.Collections.Generic.HashSet[string]]::new()
  $coveredDaily = [System.Collections.Generic.HashSet[string]]::new()
  $coveredBranches = [System.Collections.Generic.HashSet[string]]::new()
  $directCount = 0
  $deferCount = 0
  $index = 0
  foreach ($fixture in $fixtures) {
    $index++
    $label = "fixture #$index"
    if (-not ($fixture -is [pscustomobject])) { $errors.Add("$label must be an object."); continue }
    $fixtureId = $fixture.id
    if (-not (Test-NonEmptyString $fixtureId)) { $errors.Add("$label has no non-empty string id."); $fixtureId = $label }
    elseif (-not $ids.Add($fixtureId)) { $errors.Add("Duplicate fixture id: $fixtureId") }

    if (-not (Test-NonEmptyString $fixture.request)) { $errors.Add("$fixtureId has no non-empty string request.") }
    $expected = $fixture.expected
    if (-not ($expected -is [pscustomobject])) { $errors.Add("$fixtureId has no expected object."); continue }
    $kind = $expected.kind
    $flow = $expected.flow
    if ($selectionKinds -notcontains $kind) { $errors.Add("${fixtureId}: expected.kind must be direct, defer, daily-route, or branch.") }
    elseif ($kind -eq 'direct' -or $kind -eq 'defer') {
      if ($kind -eq 'direct') { $directCount++ } else { $deferCount++ }
      if ($null -ne $flow) { $errors.Add("${fixtureId}: $kind kind must use null flow.") }
    }
    elseif ($kind -eq 'daily-route') {
      if ($dailyRoutes -notcontains $flow) { $errors.Add("${fixtureId}: daily-route must select a daily route.") }
      else { [void]$coveredDaily.Add($flow) }
    }
    elseif ($kind -eq 'branch') {
      if ($branches -notcontains $flow) { $errors.Add("${fixtureId}: branch must select a branch.") }
      else { [void]$coveredBranches.Add($flow) }
    }

    $forbidden = $fixture.forbiddenFlows
    if (-not (Test-StringArray $forbidden) -or $forbidden.Count -eq 0 -or @($forbidden | Where-Object { $flows -notcontains $_ }).Count -gt 0) {
      $errors.Add("${fixtureId}: forbiddenFlows must be a non-empty list of known flow names.")
    }
    else {
      if ((@($forbidden | Select-Object -Unique)).Count -ne $forbidden.Count) { $errors.Add("${fixtureId}: forbiddenFlows cannot contain duplicates.") }
      if ($forbidden -contains $flow) { $errors.Add("${fixtureId}: selected flow cannot be forbidden.") }
      if ($kind -eq 'defer' -and -not (Test-ExactStringSet $forbidden $flows)) { $errors.Add("${fixtureId}: defer must forbid every known flow.") }
    }

    if ($mutationAuthorities -notcontains $fixture.mutationAuthority) { $errors.Add("${fixtureId}: mutationAuthority must be none or requested.") }
    $artifacts = $fixture.requiredArtifacts
    if (-not (Test-StringArray $artifacts) -or $artifacts.Count -eq 0) { $errors.Add("${fixtureId}: requiredArtifacts must be a non-empty string list.") }
    elseif ($kind -eq 'defer') {
      $missingArtifacts = @($deferRequiredArtifacts | Where-Object { $artifacts -notcontains $_ })
      if ($missingArtifacts.Count -gt 0) { $errors.Add("${fixtureId}: defer must require evidence-gap, no-change, and reentry-condition (missing: $($missingArtifacts -join ', ')).") }
    }
  }

  $missingDaily = @($dailyRoutes | Where-Object { -not $coveredDaily.Contains($_) })
  $missingBranches = @($branches | Where-Object { -not $coveredBranches.Contains($_) })
  if ($directCount -eq 0) { $errors.Add('Fixtures must cover at least one direct outcome.') }
  if ($deferCount -eq 0) { $errors.Add('Fixtures must cover at least one defer outcome.') }
  if ($missingDaily.Count -gt 0) { $errors.Add("Fixtures do not cover daily routes: $($missingDaily -join ', ')") }
  if ($missingBranches.Count -gt 0) { $errors.Add("Fixtures do not cover branches: $($missingBranches -join ', ')") }
  return $errors.ToArray()
}

function Copy-FixtureDocument {
  param($Data)
  return ($Data | ConvertTo-Json -Depth 20 | ConvertFrom-Json)
}

function Run-NegativeMutationChecks {
  param($Data, [string]$ProductDecisionRouteText, [string]$GuidanceText, [string]$ConductorText)
  $errors = [System.Collections.Generic.List[string]]::new()

  $missingRequest = Copy-FixtureDocument $Data
  $missingRequest.fixtures[0].request = ''
  if (@(Validate-FixtureDocument $missingRequest).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: empty request') }

  $contradictoryFlow = Copy-FixtureDocument $Data
  $contradictoryFlow.fixtures[2].expected.flow = 'delivery'
  if (@(Validate-FixtureDocument $contradictoryFlow).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: selected flow forbidden by its fixture') }

  $branchAsDailyRoute = Copy-FixtureDocument $Data
  $branchAsDailyRoute.fixtures[2].expected = [pscustomobject]@{ kind = 'daily-route'; flow = 'homeostasis' }
  if (@(Validate-FixtureDocument $branchAsDailyRoute).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: branch encoded as a daily route') }

  $deferWithFlow = Copy-FixtureDocument $Data
  foreach ($fixture in $deferWithFlow.fixtures) {
    if ($fixture.expected.kind -eq 'defer') {
      $fixture.expected.flow = 'learning'
      break
    }
  }
  if (@(Validate-FixtureDocument $deferWithFlow).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: defer outcome selecting a flow') }

  $deferWithPartialForbiddenFlows = Copy-FixtureDocument $Data
  foreach ($fixture in $deferWithPartialForbiddenFlows.fixtures) {
    if ($fixture.expected.kind -eq 'defer') {
      $fixture.forbiddenFlows = @('learning')
      break
    }
  }
  if (@(Validate-FixtureDocument $deferWithPartialForbiddenFlows).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: defer outcome not forbidding every flow') }

  $deferWithoutReentryCondition = Copy-FixtureDocument $Data
  foreach ($fixture in $deferWithoutReentryCondition.fixtures) {
    if ($fixture.expected.kind -eq 'defer') {
      $fixture.requiredArtifacts = @('evidence-gap', 'no-change')
      break
    }
  }
  if (@(Validate-FixtureDocument $deferWithoutReentryCondition).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: defer outcome without all required artifacts') }

  $duplicateMutationAuthorities = Copy-FixtureDocument $Data
  $duplicateMutationAuthorities.mutationAuthorities += 'requested'
  if (@(Validate-FixtureDocument $duplicateMutationAuthorities).Count -eq 0) { $errors.Add('Negative fixture mutation was accepted: duplicate mutation authority') }

  $marker = '<!-- chohogi:section=method -->'
  if (@(Validate-RouteText 'product-decision' $ProductDecisionRouteText.Replace($marker, '')).Count -eq 0) { $errors.Add('Negative route mutation was accepted: missing method section marker') }
  if (@(Validate-DeferPolicyText 'Global guidance' $GuidanceText.Replace($deferMarker, '')).Count -eq 0) { $errors.Add('Negative policy mutation was accepted: missing global defer marker') }
  if (@(Validate-DeferPolicyText 'Conductor' $ConductorText.Replace($deferMarker, '')).Count -eq 0) { $errors.Add('Negative policy mutation was accepted: missing conductor defer marker') }
  return $errors.ToArray()
}

$errors = [System.Collections.Generic.List[string]]::new()
$guidanceText = $null
$conductorText = $null
$guidance = Join-Path $root 'assets\codex\AGENTS.md'
if (-not (Test-Path -LiteralPath $guidance)) { $errors.Add("Missing global guidance: $guidance") }
else {
  $guidanceText = Get-Content -LiteralPath $guidance -Raw -Encoding utf8
  if (-not $guidanceText.Contains('trunk/routes/<flow>.md')) { $errors.Add('Global guidance does not direct selected daily routes to trunk/routes/<flow>.md.') }
  $errors.AddRange([string[]]@(Validate-DeferPolicyText 'Global guidance' $guidanceText))
}

$conductor = Join-Path $root 'assets\agents\chohogi\trunk\conductor.md'
if (-not (Test-Path -LiteralPath $conductor)) { $errors.Add("Missing conductor: $conductor") }
else {
  $conductorText = Get-Content -LiteralPath $conductor -Raw -Encoding utf8
  if (-not $conductorText.Contains('routes/<flow>.md')) { $errors.Add('Conductor does not direct selected daily routes to routes/<flow>.md.') }
  $errors.AddRange([string[]]@(Validate-DeferPolicyText 'Conductor' $conductorText))
  foreach ($route in $dailyRoutes) { if (-not $conductorText.Contains("``$route``")) { $errors.Add("Conductor does not name daily route: $route") } }
}

$routeTexts = @{}
foreach ($route in $dailyRoutes) {
  $routePath = Join-Path $root "assets\agents\chohogi\trunk\routes\$route.md"
  if (-not (Test-Path -LiteralPath $routePath)) { $errors.Add("Missing route: $routePath"); continue }
  $routeTexts[$route] = Get-Content -LiteralPath $routePath -Raw -Encoding utf8
  $errors.AddRange([string[]]@(Validate-RouteText $route $routeTexts[$route]))
}

$fixturePath = Join-Path $root 'assets\agents\chohogi\trunk\evals\route-fixtures.json'
$data = $null
if (-not (Test-Path -LiteralPath $fixturePath)) { $errors.Add("Missing route fixture file: $fixturePath") }
else {
  try { $data = Get-Content -LiteralPath $fixturePath -Raw -Encoding utf8 | ConvertFrom-Json }
  catch { $errors.Add("Invalid fixture JSON: $($_.Exception.Message)") }
}
if ($null -ne $data) {
  $errors.AddRange([string[]]@(Validate-FixtureDocument $data))
  if ($routeTexts.ContainsKey('product-decision') -and $null -ne $guidanceText -and $null -ne $conductorText) { $errors.AddRange([string[]]@(Run-NegativeMutationChecks $data $routeTexts['product-decision'] $guidanceText $conductorText)) }
}

if ($errors.Count -gt 0) {
  [Console]::Error.WriteLine('Chohogi route verification: FAIL')
  $errors | ForEach-Object { [Console]::Error.WriteLine("- $_") }
  exit 1
}
Write-Host 'Chohogi route verification: PASS (route contracts, fixtures, and negative mutations are valid).'
