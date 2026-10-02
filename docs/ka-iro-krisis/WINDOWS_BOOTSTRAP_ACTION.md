# Windows supervisor bootstrap action

One local Windows action is required before unattended multi-day provider execution. It installs the non-scientific external Codespace supervisor using the already authenticated GitHub CLI; it does not store credentials or modify any scientific artifact.

Run this exact single line in Windows PowerShell:

```powershell
$dst="$env:TEMP\bootstrap_kairo_supervisor.ps1"; gh api -H "Accept: application/vnd.github.raw+json" "/repos/taechasith/AI-should-kill-kid-or-elder/contents/docs/ka-iro-krisis/templates/bootstrap_kairo_supervisor.ps1?ref=ka-iro-krisis-v2" | Set-Content -Path $dst -Encoding utf8; powershell -ExecutionPolicy Bypass -File $dst
```

Expected Scheduled Task: `KA-IRO-KRISIS-CodespaceSupervisor`.

The completed executor/lifecycle checkpoint is `ka-iro-krisis-executor-lifecycle-v3` (the earlier `ka-iro-krisis-executor-v1` tag remains preserved as its historical checkpoint).

Successful bootstrap prints `KA-IRO bootstrap succeeded.` To verify later, run:

```powershell
Get-ScheduledTask -TaskName KA-IRO-KRISIS-CodespaceSupervisor
```

The task uses the current user's authenticated `gh` session to supervise only the named existing Codespace and resumes only through `bash scripts/kairo_resume.sh`.
