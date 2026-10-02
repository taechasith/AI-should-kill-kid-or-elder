# Windows supervisor bootstrap action

One local Windows action is required before unattended multi-day provider execution. It installs the non-scientific external Codespace supervisor using the already authenticated GitHub CLI; it does not store credentials or modify any scientific artifact.

Run this exact single line in Windows PowerShell:

```powershell
$root=Join-Path $env:LOCALAPPDATA 'KAIROKRISIS\bootstrap'; [System.IO.Directory]::CreateDirectory($root)|Out-Null; $dst=Join-Path $root 'bootstrap_kairo_supervisor_v3.ps1'; $tmp="$dst.download"; Remove-Item $tmp -Force -ErrorAction SilentlyContinue; gh api -H "Accept: application/vnd.github.raw+json" "/repos/taechasith/AI-should-kill-kid-or-elder/contents/docs/ka-iro-krisis/templates/bootstrap_kairo_supervisor.ps1?ref=ka-iro-krisis-v2" 1> $tmp; if ($LASTEXITCODE -ne 0 -or -not (Test-Path $tmp) -or (Get-Item $tmp).Length -eq 0) { Remove-Item $tmp -Force -ErrorAction SilentlyContinue; throw "KA-IRO bootstrap download failed" }; try { [scriptblock]::Create((Get-Content -Raw $tmp)) | Out-Null } catch { Remove-Item $tmp -Force -ErrorAction SilentlyContinue; throw "KA-IRO bootstrap download is invalid" }; [System.IO.File]::Copy($tmp,$dst,$true); Remove-Item $tmp -Force; powershell -NoProfile -ExecutionPolicy Bypass -File $dst
```

Expected Scheduled Task: `KA-IRO-KRISIS-CodespaceSupervisor`.

The completed executor/lifecycle checkpoint is `ka-iro-krisis-executor-lifecycle-v4` (the earlier `ka-iro-krisis-executor-v1` tag remains preserved as its historical checkpoint).

Successful bootstrap prints `KA-IRO bootstrap succeeded.` To verify later, run:

```powershell
Get-ScheduledTask -TaskName KA-IRO-KRISIS-CodespaceSupervisor
```

The task uses the current user's authenticated `gh` session to supervise only the named existing Codespace and resumes only through `bash scripts/kairo_resume.sh`.

This version first runs `test_kairo_windows_host.ps1`. It parses the production PowerShell files, verifies GitHub CLI authentication and the expected Codespace, installs/replaces the task, invokes the supervisor once, and checks remote health. It reports success only if every one of those checks succeeds; it sends no provider-generation request.
