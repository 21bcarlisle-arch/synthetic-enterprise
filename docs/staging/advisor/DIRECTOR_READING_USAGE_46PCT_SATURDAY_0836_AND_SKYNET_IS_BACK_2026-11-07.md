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
