# Monthly Maintenance Checklist

Staged 2026-07-06 (`docs/staging/MAINTENANCE_RUNBOOK.md`, Tier 2). Philosophy: this is an
unattended autonomous system, so stability beats freshness -- no component should
surprise-update mid-week. Updates are deliberate monthly events, each followed by a daemon
restart (R2: a new binary is not deployed until the process using it restarts) and a
watchdog kill-test.

Triggered automatically on the 1st of each month by `background/staging_watcher.py`, which
writes a `docs/staging/maintenance_due_<YYYYMM>.md` marker and NTFYs Rich through its
existing new-staged-file notification path -- no separate cron/dispatcher wiring needed.

## Checklist

1. **Ubuntu security patches** -- `sudo apt update && sudo apt upgrade` (WSL2; confirm
   `unattended-upgrades` is installed and enabled for security-only, as the between-windows
   safety net).
2. **Claude Code** -- `claude --version` + `claude doctor`; confirm the auto-updater is
   healthy (it self-updates by default -- verify, don't assume). Note the current version in
   the maintenance log.
3. **Node/nvm rule** -- never upgrade node casually. The watchdog and all launchers use the
   absolute nvm path (`/home/rich/.nvm/versions/node/v24.16.0/bin/claude`). If node MUST
   upgrade: update every launcher path (`grep -rn '.nvm/versions/node'`), restart all
   daemons, run both kill-tests. Treat as Tier 1-adjacent.
4. **Ollama + model** -- version check; upgrade only with a reason; `qwen3:14b` is pinned.
5. **pip** -- `pip list --outdated` review; upgrade only pytest/security-relevant items; run
   the full test suite after any change.
6. **After any update** -- restart all tmux daemons (watchdog, staging-watcher,
   autonomous-runner, dispatcher, ntfy-responder, sim-runner, file-api, token-proxy), then a
   deliberate kill-test of the claude session; confirm clean auto-relaunch.
7. **Expiry ledger** (check dates, NTFY at 30 days out): GitHub PAT expires 2026-10 (bridge +
   machine pushes die silently without it -- renew and update the stored token); Cloudflare/GH
   Pages tokens if any; Tailscale key expiry on both nodes.
8. **Disk/system** -- `df -h` (run-history and cache directories grow over time), WSL memory,
   `git gc` if the repo has bloated.
9. **Log the run** in `docs/operations/maintenance-log.md` (date, versions, actions taken,
   test/kill-test results).

## Host settings (keep; set by the director 2026-11-07 after a ~60h outage)

The on-box dead-man's switch shares fate with the host, so these settings, and the advisor's off-box check of
origin, are what keep the machine up and its silence noticed. Confirm each at every monthly run:
Windows never sleeps on mains power; `.wslconfig` carries `vmIdleTimeout=-1` and `memory=24GB`; the scheduled task
"Keep WSL running" exists and runs at log-on; Tailscale key expiry is disabled and Tailscale starts with Windows.

**The advisor's cloud stall check (advisor-run control; director's ruling, 14 Nov 2026).** Owner: the advisor.
A scheduled task in Anthropic's cloud named "Poesys stall check", running since 7 Nov at 08:17, 12:17, 16:17 and
20:17 UK time, off this box and off GitHub's scheduler. It reads origin's commits on `main`, ignoring `advisor:`,
`[ADVISOR-STAGED]` and banner-only commits, and pushes one alert to the director's phone when the last machine commit
is **6 hours or more** old, then one reminder a day at 08:00 while the stall lasts. Blind spot: it sees the
commit gap only, so a failed unit while commits still land is the on-box watchdog's and the GitHub off-box
dead-man's to catch; both stay. Worst-case detection is about 12-14h for an evening stop, which he accepted:
"6 hrs is fine". It cannot tell a long quiet job from a stall, so during a long run keep one machine commit
landing every 6 hours (the seat's direction record will do), or say in the next commit that it is not practical.
