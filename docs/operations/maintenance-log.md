# Maintenance Log

One entry per monthly maintenance run (see `docs/operations/MAINTENANCE.md`). Newest first.

Format per entry: date, versions checked (Claude Code / node / Ollama / key pip packages),
actions taken, test suite result, kill-test result.

## 2026-11-07: unplanned, at the machine, after a ~60h host outage (director)

- **Cause of the outage:** Windows went down or WSL stopped (about Thu 5 Nov 03:30 to Sat 7 Nov 15:20 GMT).
  Finding: `docs/staging/SEAT_FINDING_A_SIXTY_HOUR_HOST_OUTAGE_THE_ON_BOX_DEAD_MANS_SWITCH_COULD_NOT_REPORT_2026-11-07.md`.
- **Host settings now in force (keep them; see MAINTENANCE.md "Host settings"):** Windows never sleeps on mains;
  `.wslconfig` has `vmIdleTimeout=-1` beside `memory=24GB` (MemTotal 24,610,700 kB after reboot); a scheduled task
  "Keep WSL running" starts WSL at log-on and holds it open; WSL 3.0.3; Tailscale key expiry disabled and Tailscale
  starts with Windows; Windows Update installed.
- **Claude Code:** 2.1.308 -> 2.1.319 via nvm's npm. Seat check 15:56Z: the nvm binary every launcher uses
  (`/home/rich/.nvm/versions/node/v24.16.0/bin/claude --version`) reads `2.1.319`, and the seat-executor spawned at
  15:55Z runs from it.
- **Services:** all nine came back on their own (linger yes); the long-lived token test returned "ok".
- **Outside check (advisor):** a scheduled cloud task reads origin at 08:17, 12:17, 16:17 and 20:17 UK time and
  pushes one alert when nothing meaningful has landed for 6-10 hours.
