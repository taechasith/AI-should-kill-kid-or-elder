# Real-host acceptance check. It performs no provider generation request.
$ErrorActionPreference='Stop'
$CodespaceName='laughing-space-waffle-9795jw95xg64f7j79'
$Repo='taechasith/AI-should-kill-kid-or-elder'
$RemoteWorktree='/workspaces/ka-iro-krisis-v2-codespace'
$supervisor=Join-Path $PSScriptRoot 'kairo_codespace_supervisor.ps1'
$installer=Join-Path $PSScriptRoot 'install_kairo_supervisor.ps1'
foreach($script in @($supervisor,$installer)) { if(-not(Test-Path $script)){throw "missing script: $script"}; try{[scriptblock]::Create((Get-Content -Raw -LiteralPath $script))|Out-Null}catch{throw "PowerShell parse failed: $script"} }
if(-not(Get-Command gh -ErrorAction SilentlyContinue)){throw 'GitHub CLI missing'}
gh auth status|Out-Null; if($LASTEXITCODE -ne 0){throw 'GitHub CLI authentication failed'}
$info=gh api "/user/codespaces/$CodespaceName"|ConvertFrom-Json; if($info.repository.full_name -ne $Repo){throw 'unexpected Codespace repository'}
& $installer
if($LASTEXITCODE -ne 0){throw 'installer failed'}
if(-not(Get-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -ErrorAction SilentlyContinue)){throw 'scheduled task missing'}
Get-ScheduledTaskInfo -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor'|Out-Null
$installed=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS\kairo_codespace_supervisor.ps1'
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $installed
if($LASTEXITCODE -ne 0){throw 'manual supervisor run failed'}
$health=gh codespace ssh -c $CodespaceName -- "cd $RemoteWorktree && bash scripts/kairo_health.sh"
if($LASTEXITCODE -ne 0){throw 'remote health check failed'}
$state=$health|ConvertFrom-Json
if($state.runner -notin @('PRELIVE','RUNNING','QUOTA_WAIT','ROLLOVER','DONE','BLOCKED','STOPPED')){throw 'invalid remote health state'}
Write-Host "KA-IRO real-host acceptance passed; remote state=$($state.runner)"
