$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Run this installer in Windows PowerShell.' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }; gh auth status | Out-Null
$base=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; New-Item -ItemType Directory -Force $base | Out-Null
$source=Join-Path $PSScriptRoot 'kairo_codespace_supervisor.ps1'; $target=Join-Path $base 'kairo_codespace_supervisor.ps1'; Copy-Item $source $target -Force
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$target`""
$logon=New-ScheduledTaskTrigger -AtLogOn
$repeat=New-ScheduledTaskTrigger -Once -At (Get-Date).Date.AddMinutes(1); $repeat.RepetitionInterval='PT5M'; $repeat.RepetitionDuration='P1D'
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -Action $action -Trigger @($logon,$repeat) -Settings $settings -Force | Out-Null
& $target
Write-Host 'KA-IRO supervisor installed; task=KA-IRO-KRISIS-CodespaceSupervisor'
