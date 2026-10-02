# KA-IRO operational infrastructure. Uses caller's existing gh auth only.
$ErrorActionPreference = 'Stop'
$CodespaceName = 'laughing-space-waffle-9795jw95xg64f7j79'
$Repo = 'taechasith/AI-should-kill-kid-or-elder'
$RemoteWorktree = '/workspaces/ka-iro-krisis-v2-codespace'
$HistoricalCheckout = '/workspaces/AI-should-kill-kid-or-elder'
$Branch = 'ka-iro-krisis-v2'
$Base = Join-Path $env:LOCALAPPDATA 'KAIROKRISIS'; $LogDir = Join-Path $Base 'logs'; $Lock = Join-Path $Base 'supervisor.lock'
New-Item -ItemType Directory -Force $LogDir | Out-Null
function Write-SafeLog([string]$Message) { "$(Get-Date -Format o) | $Message" | Add-Content (Join-Path $LogDir 'supervisor.log'); Get-ChildItem $LogDir -File | Where-Object Length -gt 1048576 | ForEach-Object { Move-Item $_.FullName ($_.FullName + '.1') -Force } }
function Remote([string]$Command) { & gh codespace ssh -c $CodespaceName -- $Command; if ($LASTEXITCODE -ne 0) { throw 'remote Codespace command failed' } }
if (Test-Path $Lock) { $age=((Get-Date)-(Get-Item $Lock).LastWriteTime).TotalMinutes; if($age -lt 20){exit 0}; Remove-Item $Lock -Force }
New-Item -ItemType File -Force $Lock | Out-Null
try {
  if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }; gh auth status | Out-Null; if($LASTEXITCODE -ne 0){throw 'GitHub CLI authentication failed'}
  $info=gh api "/user/codespaces/$CodespaceName" | ConvertFrom-Json; if($info.repository.full_name -ne $Repo){throw 'unexpected Codespace repository'}
  if($info.state -ne 'Available'){ Write-SafeLog "start requested state=$($info.state)"; gh api --method POST "/user/codespaces/$CodespaceName/start" | Out-Null; if($LASTEXITCODE -ne 0){throw 'Codespace start failed'}; for($i=0;$i-lt40;$i++){Start-Sleep 15;$info=gh api "/user/codespaces/$CodespaceName"|ConvertFrom-Json;if($info.state -eq 'Available'){break}} }
  if($info.state -ne 'Available'){throw 'Codespace availability timeout'}
  # Safe rehydration only when the isolated worktree is absent. The historical checkout is never reset or switched.
  $rehydrate="set -eu; w='$RemoteWorktree'; h='$HistoricalCheckout'; b='$Branch'; if [ ! -e \"`$w/.git\" ]; then test -d \"`$h/.git\"; git -C \"`$h\" fetch origin \"`$b\" --tags; git -C \"`$h\" worktree add --detach \"`$w\" \"origin/`$b\"; fi; git -C \"`$w\" fetch origin \"`$b\" --tags; test \"`$(git -C \"`$w\" rev-parse HEAD)\" = \"`$(git -C \"`$w\" rev-parse origin/`$b)\""
  Remote $rehydrate
  $health=Remote "cd $RemoteWorktree && bash scripts/kairo_health.sh"; Write-SafeLog "health=$health"; $state=($health|ConvertFrom-Json).runner
  if($state -in @('DONE','BLOCKED','RUNNING')){exit 0}; if($state -eq 'QUOTA_WAIT'){ $next=($health|ConvertFrom-Json).next_resume_utc; if($next -and ([datetime]$next -gt (Get-Date).ToUniversalTime())){exit 0} }
  Remote "cd $RemoteWorktree && (flock -n /tmp/ka-iro-launch.lock bash -c 'nohup bash scripts/kairo_resume.sh >/tmp/ka-iro-autonomous.log 2>&1 & echo `$! > /tmp/ka-iro-autonomous.pid' || true)" | Out-Null
  Write-SafeLog 'idempotent resume launch requested'
} catch { Write-SafeLog "error=$($_.Exception.Message)"; exit 1 } finally { Remove-Item $Lock -Force -ErrorAction SilentlyContinue }
