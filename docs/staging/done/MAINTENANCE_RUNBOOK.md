[PROJECT] Monthly maintenance runbook -- keep the stack patched WITHOUT surprise updates. Backlog/low priority: build after the P1 site work; the runbook doc itself is quick.

PHILOSOPHY: unattended autonomous system => stability over freshness. No component should surprise-update mid-week; updates are deliberate monthly events followed by daemon restarts (R2: a new binary is not deployed until the process using it restarts) and a watchdog kill-test.

CREATE docs/operations/MAINTENANCE.md with this monthly checklist, and wire a reminder: dispatcher/cron NTFYs Rich + queues a maintenance turn on the 1st of each month.

MONTHLY CHECKLIST:
1. Ubuntu security patches: sudo apt update && sudo apt upgrade (WSL2; check unattended-upgrades is installed+enabled for security-only as the between-windows safety net).
2. Claude Code: claude --version + claude doctor; confirm auto-updater healthy (it self-updates by default -- verify, don't assume). Note current version in the maintenance log.
3. NODE/NVM RULE: never upgrade node casually -- the watchdog + all launchers use the absolute nvm path (/home/rich/.nvm/versions/node/v24.16.0/bin/claude). If node MUST upgrade: update every launcher path (grep for .nvm/versions/node), restart all daemons, run both kill-tests. Treat as Tier 1-adjacent.
4. Ollama + model: version check; upgrade only with a reason; qwen3:14b is pinned.
5. pip: pip list --outdated review; upgrade only pytest/security-relevant items; full test suite after any change.
6. AFTER ANY update: restart all tmux daemons (watchdog, staging-watcher, autonomous-runner, dispatcher, ntfy-responder, sim-runner, file-api, token-proxy), then deliberate kill-test of the claude session; confirm clean auto-relaunch.
7. EXPIRY LEDGER (check dates, NTFY at 30 days out): GitHub PAT expires 2026-10 (bridge + machine pushes die silently without it -- renew and update the stored token); Cloudflare/GH Pages tokens if any; Tailscale key expiry on both nodes.
8. Disk/system: df -h (the 123MB+ caches and run history grow), WSL memory, git gc if repo bloated.
9. Log the run in docs/operations/maintenance-log.md (date, versions, actions, test/kill-test results).
