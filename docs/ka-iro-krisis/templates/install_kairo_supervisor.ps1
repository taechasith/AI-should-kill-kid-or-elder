$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Run this installer in Windows PowerShell.' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
gh auth status | Out-Null; if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI authentication failed' }
$base=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; New-Item -ItemType Directory -Force $base | Out-Null
$source=Join-Path $PSScriptRoot 'kairo_codespace_supervisor.ps1'; if (-not (Test-Path $source)) { throw 'validated supervisor source missing' }
try { [scriptblock]::Create((Get-Content -Raw -LiteralPath $source)) | Out-Null } catch { throw 'supervisor source does not parse' }
$target=Join-Path $base 'kairo_codespace_supervisor.ps1'; Copy-Item $source $target -Force
$task='KA-IRO-KRISIS-CodespaceSupervisor'; $run="powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$target`""
# schtasks MINUTE/MO is recurring indefinitely and works on supported Windows 10/11 hosts.
& schtasks.exe /Create /TN $task /SC MINUTE /MO 5 /TR $run /RU "$env:USERDOMAIN\$env:USERNAME" /IT /F | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Scheduled Task registration failed' }
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
Set-ScheduledTask -TaskName $task -Settings $settings | Out-Null
if (-not (Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue)) { throw 'Scheduled Task verification failed' }
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $target
if ($LASTEXITCODE -ne 0) { throw 'Immediate supervisor validation failed' }
Write-Host 'KA-IRO supervisor installed; task=KA-IRO-KRISIS-CodespaceSupervisor'
