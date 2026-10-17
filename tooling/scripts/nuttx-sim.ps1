param([ValidateSet('build', 'run', 'stop', 'status')][string]$Action = 'run')
$ErrorActionPreference = 'Stop'
$scriptPath = Join-Path $PSScriptRoot 'nuttx-sim.sh'
$resolvedPath = & wsl -d Ubuntu-24.04 -- wslpath -a -u $scriptPath.Replace('\', '/')
if ($LASTEXITCODE -ne 0) { throw 'Cannot resolve the WSL script path.' }
$linuxPath = ($resolvedPath -join "`n").Trim()
& wsl -d Ubuntu-24.04 -- bash $linuxPath $Action
if ($LASTEXITCODE -ne 0) { throw "NuttX SIM $Action failed (exit $LASTEXITCODE)." }
