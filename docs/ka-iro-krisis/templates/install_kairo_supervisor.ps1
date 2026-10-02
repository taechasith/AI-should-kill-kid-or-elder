$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Run this installer in Windows PowerShell.' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
gh auth status | Out-Null; if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI authentication failed' }
$base=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; New-Item -ItemType Directory -Force $base | Out-Null
$source=Join-Path $PSScriptRoot 'kairo_codespace_supervisor.ps1'; if (-not (Test-Path $source)) { throw 'validated supervisor source missing' }
$target=Join-Path $base 'kairo_codespace_supervisor.ps1'; Copy-Item $source $target -Force
$action=New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$target`""
$logon=New-ScheduledTaskTrigger -AtLogOn
# Daily recurrence renews the five-minute repetition indefinitely; no daily user logon is required.
$daily=New-ScheduledTaskTrigger -Daily -At 00:01
$daily.RepetitionInterval='PT5M'; $daily.RepetitionDuration='P1D'
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Register-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -Action $action -Trigger @($logon,$daily) -Settings $settings -Force | Out-Null
& $target
Write-Host 'KA-IRO supervisor installed; task=KA-IRO-KRISIS-CodespaceSupervisor'
