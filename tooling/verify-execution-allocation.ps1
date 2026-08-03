[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python is required for execution-allocation verification.' }

if ($python.Name -eq 'py') {
  & $python.Source -3 (Join-Path $PSScriptRoot 'verify-execution-allocation.py')
} else {
  & $python.Source (Join-Path $PSScriptRoot 'verify-execution-allocation.py')
}
exit $LASTEXITCODE
