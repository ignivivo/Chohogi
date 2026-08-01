[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw 'Python is required for the supplemental skill packaging check.' }

if ($python.Name -eq 'py') {
  & $python.Source -3 (Join-Path $PSScriptRoot 'verify-skills.py')
} else {
  & $python.Source (Join-Path $PSScriptRoot 'verify-skills.py')
}
exit $LASTEXITCODE
