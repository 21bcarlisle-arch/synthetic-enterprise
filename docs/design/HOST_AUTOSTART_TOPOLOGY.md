# Host autostart topology — how Skynet actually starts

**Added 2026-08-12** after a Windows Update reboot left the machine down 22 minutes longer than
the reboot itself required, and **revised the same day** once the autostart was rebuilt. Written
because the IaC principle in CLAUDE.md — *"NO behaviour-determining state lives outside the
readable repo … reconstruct-from-repo-alone is the test"* — was not being met: none of the
Windows-side machinery below was recorded anywhere, so a rebuild from the repo alone produced a
machine that never started itself.

`docs/design/OPS1_DEPLOY_RUNBOOK.md` documents the systemd layer. This file documents the two
layers beneath it, which is where the outage lived.

## The four layers

```
  4. daemons        12 systemd --user services (supervisor, deadmans-switch, ntfy-responder,
                    staging-watcher, file-api, sanity-daemon, dispatcher, naive-organ,
                    sim-runner, token-proxy, worker-seat-manager, background-worker)
                    37 enabled unit files
  3. session        Linger=yes (loginctl) -> the user manager starts at distro boot with NO login
                    claude-tmux.service (system, enabled) -> starts the interactive agent only
  2. WSL distro     Ubuntu; /etc/wsl.conf [boot] systemd=true
  1. Windows host   Task Scheduler starts wsl.exe          <- THE OUTAGE WAS HERE
```

Layers 2–4 are correct and self-starting, and none of them contributed to the outage. `Linger=yes`
means the user manager comes up at distro boot with nobody logged in, and the tmux→systemd
migration completed 2026-07-17, so **once WSL boots the whole stack comes up unaided**.

## Layer 1 — the Windows scheduled tasks

| Task | Trigger | Action | Principal | Status |
|---|---|---|---|---|
| **`SkynetBootStart`** | **Boot** +30s | `wsl.exe -d Ubuntu -e /bin/sh -c "date -Is >> ~/.wsl_autostart_receipt; exec sleep infinity"` | `21bca`, **S4U** | added 2026-08-12 |
| `Start WSL2` | Logon | `wsl.exe -d Ubuntu` | `21bca`, Interactive | kept as fallback |
| `WSL-SSH-Forward` | Boot | `PowerShell -File C:\wsl-ssh-forward.ps1` | `21bca`, Interactive | has never run |
| ~~`SkynetAutoStart`~~ | ~~Logon~~ | ~~`…start_worker.sh`~~ | — | **RETIRED 2026-08-12** |

Distro name as Windows knows it is `Ubuntu`; `Skynet` is the Linux hostname.

### What the outage was

Both tasks that started WSL were **logon**-triggered. An unattended update restart logs nobody
in, so neither fired:

```
09:29:03  MoUsoCoreWorker.exe initiates restart   (Event 1074, "Service pack (Planned)")
09:29:06  WSL VM shuts down gracefully            (journal, boot -1)
09:32:22  TrustedInstaller.exe initiates restart  (Event 1074, "Operating System: Upgrade")
09:33:19  Windows back up                         (Event 6009)
          ... 22 minutes, Windows up, Skynet down ...
09:55:26  a human logs in                         (Security 4624, type 11)
09:55:33  Skynet boots                            (journal, boot 0)
```

Not a delay — unbounded. Every recovery mechanism the project owns (dead-man's switch,
supervisor, staging markers, run-completion protocol) lives at layer 4 and cannot run when layer
1 never fired. Availability rested on someone walking to the machine. Patch Tuesday is monthly.

### Why S4U and not a stored password

The director's decision was "stored credentials, not auto-logon" — declining to trade a security
property for availability. **S4U** (`-LogonType S4U`, "run whether user is logged on or not"
without a saved secret) satisfies that reasoning better than the option chosen, because it keeps
**no secret at rest at all** while producing the same result. Verified rather than assumed: a
registered S4U task ran non-interactively, reached the distro and wrote from inside WSL as
`rich`, `LastTaskResult=0`.

A stored password would also have been awkward here specifically: the account is a **Microsoft
Account** (`MicrosoftAccount\21bcarlisle@gmail.com`), not a local account.

`SYSTEM` was never viable and is recorded so nobody re-proposes it: WSL distros are registered
per-user under `HKCU\…\Lxss`, so SYSTEM cannot see `Ubuntu` at all.

### Why `SkynetAutoStart` was retired rather than repaired

It had been failing on every logon with `LastTaskResult=126` — bash's *found but not
executable*; `background/start_worker.sh` has no execute bit. It was tempting to `chmod +x` it.

**That would have started a second stack.** `start_worker.sh` is idempotent only with respect to
**tmux sessions** (`tmux has-session -t "$name"`), and the daemons no longer run in tmux — they
are 12 systemd `--user` services. Its guard is structurally blind to them, so repairing the task
would have launched tmux duplicates of twelve already-running services on the shared tree.

Its function is fully superseded by the completed tmux→systemd migration, and the empirical
proof is that it has been broken for an unknown period with no operational impact. The task
definition is archived at `C:\Windows\Temp\SkynetAutoStart.retired.xml`.

`start_worker.sh` itself is left alone — still valid for a manual cold start on a machine where
the units are not running, and not worth changing on the strength of this.

## Proving it — `tools/verify_host_autostart.py`

The claim is **not** "the task exists"; it is "WSL came up with nobody logged in". The control
compares two clocks from independent authorities, neither derived from the task being judged:

- WSL's boot time from the Linux kernel's own `/proc/stat` `btime`
- the first **human** interactive logon since host boot, from the Windows Security log (4624)

```
PASS      WSL booted BEFORE any human logon -> it started itself
FAIL      WSL booted AFTER -> a human started it (the 2026-08-12 mode)
UNPROVEN  the question could not be answered from evidence
```

Fail direction is UNPROVEN, never PASS: the Security log needs elevation, and an unreadable log
is an unanswered question. `tests/tools/test_verify_host_autostart.py` proves both directions
with mutations (25 tests).

**One calibration was found by running it, not by reasoning**, and is worth keeping in mind for
any similar control: Windows logs type-2 logons for its own pseudo-accounts (`Font\UMFD-0`,
`Window\DWM-1`) within a second of every boot. Counting those put a "human" at boot+1s forever,
which would have made PASS unreachable and reported FAIL on a perfectly working autostart — a
fail-ALWAYS control, as useless as a fail-open one. The query now excludes machine accounts and
the window/font hosts.

### Current status — NOT YET PROVEN

At the time of writing the verdict is, correctly, **FAIL**: today a human did start it.

```
FAIL: WSL booted 1s AFTER the first interactive logon
  wsl boot          : 2026-08-12T08:55:28+00:00
  first human logon : 2026-08-12T08:55:26+00:00
```

The proof is owed and cannot be faked from here: it requires a **real reboot with no logon**.
Run `python3 -m tools.verify_host_autostart --strict` after the next unattended restart (or
after a deliberate reboot where nobody signs in for a few minutes). PASS is the evidence; until
then this section says UNPROVEN rather than implying the fix works.

## Reconciliation

This table is a hand-transcribed snapshot and will decay the way CLAUDE.md warns prose rules do.
A check that reads the live tasks via `Get-ScheduledTask` and reds on drift is **not built**.
Until it is, treat the table as evidence of what was true on 2026-08-12, not as a live guarantee.
