[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'resolve-python.ps1')
$python = Resolve-ChohogiPython
& $python.Executable @($python.Arguments) (Join-Path $PSScriptRoot 'verify-routes.py')
exit $LASTEXITCODE
