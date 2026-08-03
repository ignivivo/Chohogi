function Resolve-ChohogiPython {
  [CmdletBinding()]
  param()

  if ($env:CHOHOGI_PYTHON) {
    if (-not (Test-Path -LiteralPath $env:CHOHOGI_PYTHON -PathType Leaf)) {
      throw "CHOHOGI_PYTHON does not point to an executable file: $env:CHOHOGI_PYTHON"
    }
    return [pscustomobject]@{ Executable = $env:CHOHOGI_PYTHON; Arguments = @() }
  }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python) { return [pscustomobject]@{ Executable = $python.Source; Arguments = @() } }

  $launcher = Get-Command py -ErrorAction SilentlyContinue
  if ($launcher) { return [pscustomobject]@{ Executable = $launcher.Source; Arguments = @('-3') } }

  # Codex Desktop's bundled runtime is a last-resort, current-session capability.
  # It is discovered dynamically and is never an installation requirement.
  $runtimeRoot = if ($env:USERPROFILE) { Join-Path $env:USERPROFILE '.cache\codex-runtimes' } else { $null }
  if ($runtimeRoot -and (Test-Path -LiteralPath $runtimeRoot -PathType Container)) {
    $runtimeDirectories = @(Get-ChildItem -LiteralPath $runtimeRoot -Directory | Sort-Object LastWriteTimeUtc -Descending)
    foreach ($runtimeDirectory in $runtimeDirectories) {
      $candidate = Join-Path $runtimeDirectory.FullName 'dependencies\python\python.exe'
      if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        return [pscustomobject]@{ Executable = $candidate; Arguments = @() }
      }
    }
  }

  throw 'Python 3 was not found. Install Python 3 or set CHOHOGI_PYTHON to its executable path.'
}
