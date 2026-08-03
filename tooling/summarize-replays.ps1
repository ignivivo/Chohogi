param([Parameter(Mandatory = $true, ValueFromRemainingArguments = $true)][string[]]$ResultFiles)

$ErrorActionPreference='Stop'
. (Join-Path $PSScriptRoot 'resolve-python.ps1')
$python=Resolve-ChohogiPython
$pythonPath=$python.Executable
& $pythonPath @($python.Arguments) (Join-Path $PSScriptRoot 'summarize-replays.py') @ResultFiles
exit $LASTEXITCODE
