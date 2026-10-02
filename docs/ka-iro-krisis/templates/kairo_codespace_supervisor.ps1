# KA-IRO operational infrastructure. It uses only the caller's existing gh auth.
$ErrorActionPreference = 'Stop'
$CodespaceName = 'laughing-space-waffle-9795jw95xg64f7j79'
$Repo = 'taechasith/AI-should-kill-kid-or-elder'
$RemoteWorktree = '/workspaces/ka-iro-krisis-v2-codespace'
$HistoricalCheckout = '/workspaces/AI-should-kill-kid-or-elder'
$Branch = 'ka-iro-krisis-v2'
$Base = Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; $LogDir = Join-Path $Base 'logs'; $Lock = Join-Path $Base 'supervisor.lock'
New-Item -ItemType Directory -Force $LogDir | Out-Null
function Write-SafeLog([string]$Message) { "$(Get-Date -Format o) | $Message" | Add-Content (Join-Path $LogDir 'supervisor.log'); Get-ChildItem $LogDir -File | Where-Object Length -gt 1048576 | ForEach-Object { Move-Item $_.FullName ($_.FullName + '.1') -Force } }
function Remote([string]$Command) { & gh codespace ssh -c $CodespaceName -- $Command; if ($LASTEXITCODE -ne 0) { throw "remote Codespace command failed: $Command" } }
function Ensure-RemoteWorktree {
  $exists=$true
  try { Remote "test -e $RemoteWorktree/.git" | Out-Null } catch { $exists=$false }
  if (-not $exists) {
    Write-SafeLog 'isolated worktree absent; safe rehydration requested'
    Remote "git -C $HistoricalCheckout fetch origin $Branch --tags" | Out-Null
    # This creates a new detached worktree only. It never resets, checks out, or writes the historical checkout.
    Remote "git -C $HistoricalCheckout worktree add --detach $RemoteWorktree origin/$Branch" | Out-Null
  }
  Remote "git -C $RemoteWorktree fetch origin $Branch --tags" | Out-Null
  $head=(Remote "git -C $RemoteWorktree rev-parse HEAD").Trim()
  $originHead=(Remote "git -C $RemoteWorktree rev-parse origin/$Branch").Trim()
  if ($head -ne $originHead) { throw "isolated worktree HEAD does not match origin/$Branch" }
}
if (Test-Path $Lock) { $age=((Get-Date)-(Get-Item $Lock).LastWriteTime).TotalMinutes; if($age -lt 20){exit 0}; Remove-Item $Lock -Force }
New-Item -ItemType File -Force $Lock | Out-Null
try {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
  gh auth status | Out-Null; if($LASTEXITCODE -ne 0){throw 'GitHub CLI authentication failed'}
  $info=gh api "/user/codespaces/$CodespaceName" | ConvertFrom-Json; if($info.repository.full_name -ne $Repo){throw 'unexpected Codespace repository'}
  if($info.state -ne 'Available') { Write-SafeLog "start requested state=$($info.state)"; gh api --method POST "/user/codespaces/$CodespaceName/start" | Out-Null; if($LASTEXITCODE -ne 0){throw 'Codespace start failed'}; for($i=0;$i-lt40;$i++){Start-Sleep 15;$info=gh api "/user/codespaces/$CodespaceName"|ConvertFrom-Json;if($info.state -eq 'Available'){break}} }
  if($info.state -ne 'Available'){throw 'Codespace availability timeout'}
  Ensure-RemoteWorktree
  $health=Remote "cd $RemoteWorktree && bash scripts/kairo_health.sh"; Write-SafeLog "health=$health"; $state=($health|ConvertFrom-Json).runner
  if($state -in @('DONE','BLOCKED','RUNNING')){exit 0}; if($state -eq 'QUOTA_WAIT'){ $next=($health|ConvertFrom-Json).next_resume_utc; if($next -and ([datetime]$next -gt (Get-Date).ToUniversalTime())){exit 0} }
  Remote "cd $RemoteWorktree && bash scripts/kairo_launch.sh" | Out-Null
  Write-SafeLog 'idempotent resume launch requested'
} catch { Write-SafeLog "error=$($_.Exception.Message)"; exit 1 } finally { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
