[CmdletBinding()] param([Parameter(Mandatory=$true)][string]$Result)
$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'resolve-python.ps1')
$python=Resolve-ChohogiPython
$pythonPath=$python.Executable
& $pythonPath @($python.Arguments) (Join-Path $PSScriptRoot 'validate-replay-result.py') $Result
exit $LASTEXITCODE
