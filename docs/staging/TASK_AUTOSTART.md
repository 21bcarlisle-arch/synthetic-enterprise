# Task: Auto-start on Windows reboot

## Steps

### 1. Update start_worker.sh
Add if not present:
- file-api tmux session running uvicorn on 0.0.0.0:8765
- tailscale funnel 8765 (no sudo needed)

### 2. Register Windows Task Scheduler task
Run from WSL2:
powershell.exe -Command "$action = New-ScheduledTaskAction -Execute 'wsl.exe' -Argument '-d Ubuntu bash -c "sleep 10 && /home/rich/synthetic-enterprise/background/start_worker.sh"'; $trigger = New-ScheduledTaskTrigger -AtLogOn; Register-ScheduledTask -TaskName 'SkynetAutoStart' -Action $action -Trigger $trigger -RunLevel Highest -Force"

### 3. Verify
powershell.exe -Command "Get-ScheduledTask -TaskName SkynetAutoStart"

## Completion
make check, commit, push, NTFY: SkynetAutoStart registered.