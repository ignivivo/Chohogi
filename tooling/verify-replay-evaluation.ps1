$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'resolve-python.ps1')
$python=Resolve-ChohogiPython
$pythonPath=$python.Executable
& $pythonPath @($python.Arguments) (Join-Path $PSScriptRoot 'verify-replay-evaluation.py')
exit $LASTEXITCODE
