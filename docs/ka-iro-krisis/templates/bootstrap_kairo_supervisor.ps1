$ErrorActionPreference='Stop'
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }; gh auth status | Out-Null
$dir=Join-Path $env:TEMP 'KAIROKRISIS-bootstrap'; New-Item -ItemType Directory -Force $dir | Out-Null
$base='/repos/taechasith/AI-should-kill-kid-or-elder/contents/docs/ka-iro-krisis/templates'
foreach($name in @('kairo_codespace_supervisor.ps1','install_kairo_supervisor.ps1')) { gh api -H 'Accept: application/vnd.github.raw+json' "$base/$name?ref=ka-iro-krisis-v2" | Set-Content -Path (Join-Path $dir $name) -Encoding utf8 }
& (Join-Path $dir 'install_kairo_supervisor.ps1')
if (-not (Get-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -ErrorAction SilentlyContinue)) { throw 'Scheduled Task registration failed' }
Write-Host 'KA-IRO bootstrap succeeded.'
