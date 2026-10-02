# One-click bootstrap. Every repository download is fail-closed before execution.
$ErrorActionPreference = 'Stop'
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw 'GitHub CLI missing' }
gh auth status | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'GitHub CLI authentication failed' }
$dir = Join-Path $env:TEMP 'KAIROKRISIS-bootstrap'
New-Item -ItemType Directory -Force $dir | Out-Null
$base = '/repos/taechasith/AI-should-kill-kid-or-elder/contents/docs/ka-iro-krisis/templates'
function Get-ValidatedScript([string]$Name) {
  $target = Join-Path $dir $Name
  $temporary = "$target.download"
  Remove-Item $temporary -Force -ErrorAction SilentlyContinue
  & gh api -H 'Accept: application/vnd.github.raw+json' "$base/$Name?ref=ka-iro-krisis-v2" 1> $temporary
  if ($LASTEXITCODE -ne 0) { Remove-Item $temporary -Force -ErrorAction SilentlyContinue; throw "download failed: $Name" }
  if (-not (Test-Path $temporary) -or (Get-Item $temporary).Length -eq 0) { Remove-Item $temporary -Force -ErrorAction SilentlyContinue; throw "empty download: $Name" }
  try { [scriptblock]::Create((Get-Content -Raw -LiteralPath $temporary)) | Out-Null }
  catch { Remove-Item $temporary -Force -ErrorAction SilentlyContinue; throw "invalid PowerShell download: $Name" }
  Move-Item -LiteralPath $temporary -Destination $target -Force
}
Get-ValidatedScript 'kairo_codespace_supervisor.ps1'
Get-ValidatedScript 'install_kairo_supervisor.ps1'
& (Join-Path $dir 'install_kairo_supervisor.ps1')
if (-not (Get-ScheduledTask -TaskName 'KA-IRO-KRISIS-CodespaceSupervisor' -ErrorAction SilentlyContinue)) { throw 'Scheduled Task registration failed' }
Write-Host 'KA-IRO bootstrap succeeded.'
