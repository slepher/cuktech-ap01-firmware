param(
  [Parameter(Position=0)][string]$Operation = 'status',
  [Parameter(Position=1, ValueFromRemainingArguments=$true)][uint32[]]$Values = @()
)
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'sim-control.py'
$resolvedPath = & wsl -d Ubuntu-24.04 -- wslpath -a -u $scriptPath.Replace('\', '/')
if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve the WSL control path.' }
$linuxPath = ($resolvedPath -join "`n").Trim()
& wsl -d Ubuntu-24.04 -- python3 -B $linuxPath $Operation @Values
if ($LASTEXITCODE -ne 0) { throw "AP01 SIM request failed (exit $LASTEXITCODE); inspect the structured reply." }
