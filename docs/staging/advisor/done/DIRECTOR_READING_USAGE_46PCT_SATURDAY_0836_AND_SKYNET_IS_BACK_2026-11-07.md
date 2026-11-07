**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-READING] Usage at 46% on Sat 7 Nov, 08:36 GMT. Skynet was down for about 60 hours and is back. There is no need to go slow before Monday (2026-11-07)

**Type:** READING, through the advisor channel. These are the director's words from chat:

- Sat 7 Nov, 08:36 GMT: "How is progress? Usage is 46%"
- Sat 7 Nov, 15:28 GMT: "Not sure what went wrong but I have rebooted."

## What happened

- **Skynet was offline from about Thu 5 Nov 03:30 to Sat 7 Nov 15:20 GMT.** The machine landed nothing for about 60 hours.
- **The cause:** Skynet runs in WSL on Windows. Windows went down or WSL stopped, and the on-box dead-man's switch and the NTFY watchdog went with it. No alert could reach the director.
- **The director has fixed it today, at the machine:**
  - Windows never sleeps on mains power.
  - `.wslconfig` now has `vmIdleTimeout=-1`, added to the existing `memory=24GB`. It is confirmed: MemTotal reads 24,610,700 kB after the reboot.
  - A scheduled task called "Keep WSL running" starts WSL at log-on and holds it open.
  - WSL is updated to 3.0.3.
  - Tailscale key expiry is disabled, and Tailscale starts with Windows.
  - Windows Update is installed.
  - Claude Code is updated from 2.1.308 to **2.1.319**, using NVM's npm.
  - After the reboot, all nine services came back on their own (linger is yes), and the long-lived token test returned "ok".
- **The advisor added a check outside Skynet.** A scheduled cloud task reads origin at 08:17, 12:17, 16:17 and 20:17 UK time. It pushes the director one alert when nothing meaningful has landed for 6–10 hours, and sends a daily reminder at 08:17 for an ongoing stall. It is silent otherwise.

## The reading and the pace

- Usage is **46%**, and the reset is Mon 9 Nov 03:00 GMT. That leaves 54 points over about 59 hours from 15:50 Saturday, roughly **0.9 points an hour** [derived].
- **Your 15:29 commit says "slow until Mon 03:00Z".** Do not go slow. The 5 Nov reading asked to hold about 0.6 points an hour so the week would last. The 60-hour outage has since left far more headroom than that.
- **Work at your normal pace.** Priority:
  1. **Get a verified book ready for the 9 Nov publish.** It carries this week's fixes: the EPG revenue booking, the pre-cap defaults, cost to serve, heating draws and the settlement fixes.
  2. **Continue the correctness stretch.**
  3. **The queued steers** (the advisor's 5 and 7 Nov staged files).
- **Keep about 10 points in reserve for the Monday run and its grading.**

## Ask

- **Restart onto the new CLI.** Every running `claude` process holds the old binary until it restarts. The reboot restarted the services. Confirm in Done that new seats run 2.1.319.
- **Record the outage as a finding.** Note what was lost, about 60 hours. Name why the on-box dead-man's switch could not help: it shares fate with the host. Record the outside check as the answer, and record the director's WSL and Windows fixes in the infrastructure docs.

## Done

(seat executor, 7 Nov ~16:00Z, claim `grade-the-fd91027799-book-through-the-whole-invariant-gate`)

- **Pace.** The dial read `slow` until Mon 03:00Z (set 15:26Z). Set to `normal` with no expiry at 15:56Z:
  `python3 -m background.tick_mode normal`. To reverse: `python3 -m background.tick_mode slow --until 2026-11-09T03:00Z`.
  The ~10-point reserve for Monday's run and grade is noted. The dial has no setting between `normal` and `slow`,
  so it is held by not drawing extra work after Sunday evening rather than by the dial.
- **Priority 1, a verified book for 9 Nov.** The runner relaunched at 15:47Z on 8c7489e0d9, which carries every
  fix named here, including 26c891276. The fd91027799 book is graded through the whole gate (the B3CE finding).
  The grade found that **no saved book carried the level DD schedule** (N20): `extract_report_data` dropped
  `level_dd_collections`, so the page ledger collected 96.5% of DDs at their bill. That is fixed in this commit,
  with a control. The run in flight predates the fix, so the book for Monday is the runner's next one.
- **New CLI.** `/home/rich/.nvm/versions/node/v24.16.0/bin/claude --version` reads `2.1.319`. That is the binary
  every launcher uses, and this seat-executor (spawned 15:55Z, after the reboot) runs from it.
- **The outage is a finding:** `docs/staging/SEAT_FINDING_A_SIXTY_HOUR_HOST_OUTAGE_THE_ON_BOX_DEAD_MANS_SWITCH_COULD_NOT_REPORT_2026-11-07.md`.
  About 60 hours lost. The on-box switch shares fate with the host. The advisor's off-box check of origin is the answer.
- **Host fixes recorded** in `docs/operations/MAINTENANCE.md` ("Host settings", checked monthly) and in
  `docs/operations/maintenance-log.md` (7 Nov entry).
