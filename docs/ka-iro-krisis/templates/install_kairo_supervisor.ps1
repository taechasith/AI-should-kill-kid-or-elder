$ErrorActionPreference='Stop'
if ($env:OS -ne 'Windows_NT') { throw 'Run this installer in Windows PowerShell.' }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
gh auth status | Out-Null; if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI authentication failed' }
$base=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; [System.IO.Directory]::CreateDirectory($base) | Out-Null
$source=Join-Path $PSScriptRoot 'kairo_codespace_supervisor.ps1'; if (-not (Test-Path $source)) { throw 'validated supervisor source missing' }
try { [scriptblock]::Create((Get-Content -Raw -LiteralPath $source)) | Out-Null } catch { throw 'supervisor source does not parse' }
$target=Join-Path $base 'kairo_codespace_supervisor.ps1'; Copy-Item $source $target -Force
function New-KairoSupervisorAction([string]$ScriptPath) {
  $powershell=Join-Path $env:SystemRoot 'System32\WindowsPowerShell\v1.0\powershell.exe'
  $arguments="-NoProfile -ExecutionPolicy Bypass -File `"$ScriptPath`""
  return New-ScheduledTaskAction -Execute $powershell -Argument $arguments
}
$task='KA-IRO-KRISIS-CodespaceSupervisor'
$action=New-KairoSupervisorAction $target
# Repetition properties are supplied to the supported ONCE trigger constructor.
$repeat=New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 3650)
$logon=New-ScheduledTaskTrigger -AtLogOn
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -MultipleInstances IgnoreNew
$principal=New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Limited
Register-ScheduledTask -TaskName $task -Action $action -Trigger @($repeat,$logon) -Settings $settings -Principal $principal -Force | Out-Null
$registered=Get-ScheduledTask -TaskName $task -ErrorAction Stop
if(-not $registered){throw 'Scheduled Task verification failed'}
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $target
if ($LASTEXITCODE -ne 0) { throw 'Immediate supervisor validation failed' }
Write-Host 'KA-IRO supervisor installed; task=KA-IRO-KRISIS-CodespaceSupervisor'
