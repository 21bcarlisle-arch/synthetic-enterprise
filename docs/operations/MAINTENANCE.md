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
