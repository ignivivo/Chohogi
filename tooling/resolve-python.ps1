function Resolve-ChohogiPython {
  [CmdletBinding()]
  param()

  if ($env:CHOHOGI_PYTHON) {
    if (-not (Test-Path -LiteralPath $env:CHOHOGI_PYTHON -PathType Leaf)) {
      throw "CHOHOGI_PYTHON does not point to an executable file: $env:CHOHOGI_PYTHON"
    }
    return [pscustomobject]@{ Executable = $env:CHOHOGI_PYTHON; Arguments = @() }
  }

  function Test-PythonExecutable([string]$Executable, [string[]]$Arguments) {
    try {
      & $Executable @Arguments -c 'import sys; assert sys.version_info >= (3, 8)'
      return $LASTEXITCODE -eq 0
    } catch { return $false }
  }

  $python = Get-Command python -ErrorAction SilentlyContinue
  if ($python -and (Test-PythonExecutable $python.Source @())) {
    return [pscustomobject]@{ Executable = $python.Source; Arguments = @() }
  }

  $launcher = Get-Command py -ErrorAction SilentlyContinue
  if ($launcher -and (Test-PythonExecutable $launcher.Source @('-3'))) {
    return [pscustomobject]@{ Executable = $launcher.Source; Arguments = @('-3') }
  }

  # Codex Desktop's bundled runtime is a last-resort, current-session capability.
  # It is discovered dynamically and is never an installation requirement.
  $runtimeRoot = if ($env:USERPROFILE) { Join-Path $env:USERPROFILE '.cache\codex-runtimes' } else { $null }
  if ($runtimeRoot -and (Test-Path -LiteralPath $runtimeRoot -PathType Container)) {
    $runtimeDirectories = @(Get-ChildItem -LiteralPath $runtimeRoot -Directory | Sort-Object LastWriteTimeUtc -Descending)
    foreach ($runtimeDirectory in $runtimeDirectories) {
      $candidate = Join-Path $runtimeDirectory.FullName 'dependencies\python\python.exe'
      if ((Test-Path -LiteralPath $candidate -PathType Leaf) -and (Test-PythonExecutable $candidate @())) {
        return [pscustomobject]@{ Executable = $candidate; Arguments = @() }
      }
    }
  }

  throw 'Python 3 was not found. Install Python 3 or set CHOHOGI_PYTHON to its executable path.'
}
