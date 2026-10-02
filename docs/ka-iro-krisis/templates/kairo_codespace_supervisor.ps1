# KA-IRO operational infrastructure. Uses the caller's existing gh auth only.
$ErrorActionPreference = 'Stop'
$CodespaceName = 'laughing-space-waffle-9795jw95xg64f7j79'
$Repo = 'taechasith/AI-should-kill-kid-or-elder'
$RemoteWorktree = '/workspaces/ka-iro-krisis-v2-codespace'
$ResumeCommand = "cd $RemoteWorktree && bash scripts/kairo_resume.sh"
$HealthCommand = "cd $RemoteWorktree && bash scripts/kairo_health.sh"
$Base = Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; $LogDir = Join-Path $Base 'logs'; $Lock = Join-Path $Base 'supervisor.lock'
New-Item -ItemType Directory -Force $LogDir | Out-Null
function Write-SafeLog([string]$Message) { "$(Get-Date -Format o) | $Message" | Add-Content (Join-Path $LogDir 'supervisor.log'); Get-ChildItem $LogDir -File | Where-Object Length -gt 1048576 | ForEach-Object { Move-Item $_.FullName ($_.FullName + '.1') -Force } }
if (Test-Path $Lock) { $age = ((Get-Date) - (Get-Item $Lock).LastWriteTime).TotalMinutes; if ($age -lt 20) { exit 0 }; Remove-Item $Lock -Force }
New-Item -ItemType File -Force $Lock | Out-Null
try {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
  gh auth status | Out-Null
  $info = gh api "/user/codespaces/$CodespaceName" | ConvertFrom-Json
  if ($info.repository.full_name -ne $Repo) { throw 'unexpected Codespace repository' }
  if ($info.state -ne 'Available') {
    Write-SafeLog "start requested state=$($info.state)"; gh api --method POST "/user/codespaces/$CodespaceName/start" | Out-Null
    for ($i=0; $i -lt 40; $i++) { Start-Sleep -Seconds 15; $info = gh api "/user/codespaces/$CodespaceName" | ConvertFrom-Json; if ($info.state -eq 'Available') { break } }
  }
  if ($info.state -ne 'Available') { Write-SafeLog 'availability timeout'; exit 1 }
  $health = gh codespace ssh -c $CodespaceName -- $HealthCommand
  Write-SafeLog "health=$health"
  $state = ($health | ConvertFrom-Json).runner
  if ($state -in @('DONE','BLOCKED','RUNNING')) { exit 0 }
  if ($state -eq 'QUOTA_WAIT') { $next = ($health | ConvertFrom-Json).next_resume_utc; if ($next -and ([datetime]$next -gt (Get-Date).ToUniversalTime())) { exit 0 } }
  $launch = "cd $RemoteWorktree && (flock -n /tmp/ka-iro-launch.lock bash -c 'nohup bash scripts/kairo_resume.sh >/tmp/ka-iro-autonomous.log 2>&1 & echo `$! > /tmp/ka-iro-autonomous.pid' || true)"
  gh codespace ssh -c $CodespaceName -- $launch | Out-Null
  Write-SafeLog 'idempotent resume launch requested'
} catch { Write-SafeLog "error=$($_.Exception.Message)"; exit 1 } finally { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
