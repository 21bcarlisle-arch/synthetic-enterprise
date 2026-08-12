# Host autostart topology — how Skynet actually starts, and the layer that does not

**Added 2026-08-12** after a Windows Update reboot left the machine down for 22 minutes longer
than the reboot itself required. Written because the IaC principle in CLAUDE.md — *"NO
behaviour-determining state lives outside the readable repo … reconstruct-from-repo-alone is the
test"* — was not being met: **none** of the machinery below was recorded anywhere in this repo,
and a rebuild from the repo alone produces a machine that never starts itself.

`docs/design/OPS1_DEPLOY_RUNBOOK.md` documents the systemd layer *inside* WSL. This file
documents the two layers beneath it, which is where the 2026-08-12 outage actually lived.

## The four layers

```
  4. daemons          supervisor, sanity_daemon, ntfy_responder, staging_watcher,
                      deadmans_switch, file_api        <- systemd --user, PPID = systemd --user
  3. session          Linger=yes (loginctl), claude-tmux.service enabled
  2. WSL distro       Ubuntu, /etc/wsl.conf [boot] systemd=true
  1. Windows host     Task Scheduler starts wsl.exe    <- THE GAP IS HERE
```

Layers 2–4 are correct and self-starting. `Linger=yes` means the user manager comes up at distro
boot with no login, and `claude-tmux.service` is `enabled`. **Once WSL boots, the whole stack
comes up unaided.** Nothing in layers 2–4 contributed to the outage.

## Layer 1 — the Windows scheduled tasks (observed 2026-08-12)

| Task | Trigger | Action | Runs as | Last result |
|---|---|---|---|---|
| `Start WSL2` | **Logon** | `wsl.exe -d Ubuntu` | `21bca`, Interactive | `267009` (running) |
| `SkynetAutoStart` | **Logon** | `wsl.exe -d Ubuntu bash -c "sleep 10; …/background/start_worker.sh"` | `21bca`, Interactive | **`126`** |
| `WSL-SSH-Forward` | Boot | `PowerShell.exe -File C:\wsl-ssh-forward.ps1` | `21bca`, Interactive | `267011` (never run) |

Distro name as Windows knows it: `Ubuntu` (not "Skynet" — that is the Linux hostname).

## Defect 1 — the starters are logon-triggered, so an unattended reboot leaves the box down

Both tasks that start WSL fire on **logon**. A Windows Update restart logs nobody in, so neither
fires. Observed 2026-08-12:

```
09:29:03  MoUsoCoreWorker.exe initiates restart      (Event 1074, "Service pack (Planned)")
09:29:06  WSL VM shuts down gracefully               (journal, boot -1)
09:32:22  TrustedInstaller.exe initiates restart     (Event 1074, "Operating System: Upgrade")
09:33:19  Windows back up                            (Event 6009)
          ... 22 minutes with Windows up and Skynet down ...
09:55:26  user logs in                               (Security 4624, logon type 11)
09:55:27  both WSL tasks fire                        (Task Scheduler LastRunTime)
09:55:33  Skynet boots                               (journal, boot 0)
```

The gap is not a delay — it is unbounded. Absent a human logging in, the machine stays down
indefinitely. Every recovery mechanism the project owns (dead-man's switch, supervisor, staging
markers, the run-completion protocol) lives at layer 4 and cannot run when layer 1 never fired.
**Availability currently rests on someone walking to the machine.** Patch Tuesday is monthly, so
this recurs on a known cadence.

## Defect 2 — `SkynetAutoStart` has been failing silently

`LastTaskResult=126`. Bash returns 126 for *found but not executable*, and
`background/start_worker.sh` is mode `-rw-rw-r--` with no execute bit. The task has been failing
on every logon.

**Do not fix this by `chmod +x` alone.** The daemon stack already comes up via `Linger=yes` +
`claude-tmux.service`, so repairing the task may start a SECOND copy of the daemons on a shared
tree with concurrent writers — the failure class CLAUDE.md already warns about. Decide whether
this task should exist at all before making it work; a broken task and a duplicate-stack task are
not obviously ordered.

## Recommended remedy for defect 1 — NOT applied, needs a decision

Add a **boot trigger** to the WSL starter. The wrinkle is real and is why this is written down
rather than done: a boot-time task running as `SYSTEM` starts *SYSTEM's own* WSL instance, which
is a different VM from the user's and not the one an interactive terminal attaches to. The
options, with their costs:

- **Boot trigger, run as `21bca` with "run whether user is logged on or not"** — correct instance,
  requires storing the account password in Task Scheduler.
- **Windows auto-logon** — simplest and makes the existing logon triggers correct as written,
  but leaves the console unlocked at boot.

Both trade a security property for availability, which makes it the director's call rather than
a mechanical fix.

## Reconciliation

This file is a hand-transcribed snapshot and will decay exactly the way the prose rules CLAUDE.md
warns about do. The mechanism version — a check that reads the live tasks via
`Get-ScheduledTask` and diffs them against the table above, red on drift — is **not built**. Until
it is, treat the table as evidence of what was true on 2026-08-12, not as a live guarantee.
