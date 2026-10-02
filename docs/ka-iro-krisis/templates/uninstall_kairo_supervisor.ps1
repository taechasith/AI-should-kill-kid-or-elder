$ErrorActionPreference='Stop'
Unregister-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -Confirm:$false -ErrorAction SilentlyContinue
$base=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; Remove-Item (Join-Path $base 'kairo_codespace_supervisor.ps1') -Force -ErrorAction SilentlyContinue
Write-Host 'Removed only KA-IRO supervisor task/files; logs were preserved.'
