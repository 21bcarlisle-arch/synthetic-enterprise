**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted`

# A 60-hour host outage that the on-box dead-man's switch could not report (2026-11-07)

**Source.** The director's reading of 7 Nov, relayed by the advisor
(`advisor/done/DIRECTOR_READING_USAGE_46PCT_SATURDAY_0836_AND_SKYNET_IS_BACK_2026-11-07.md`), and
`docs/observability/sim-runner-log.md`: the last line before the gap is `2026-11-05 03:11 UTC`, and the next is
`2026-11-07 15:24 UTC Simulation runner started`.

**What was lost.** About 60 hours with nothing landed (Thu 5 Nov ~03:30 to Sat 7 Nov ~15:20 GMT):
- the run on be1e7e0101 started at 02:37Z on 5 Nov produced no book;
- the fd91027799 book (finished 02:26Z on 5 Nov) sat ungraded through the whole invariant gate;
- the grade of 26c891276 on a fresh book (`grade-nil-ask-and-cleared-settlement-on-fresh-book`) had no book to
  run on. The run at 8c7489e0d9 that started at 15:47Z on 7 Nov carries it.

**Why the dead-man's switch could not help.** It runs on Skynet. When Windows went down or WSL stopped, the
switch, the NTFY watchdog and everything they watch stopped together. A watchdog that shares fate with the host
can report a dead process but never a dead host. No signal reached the director. He found it by asking.

**The answer, already in place.** It is off the box: the advisor's scheduled cloud task reads origin at 08:17,
12:17, 16:17 and 20:17 UK time. It pushes one alert after 6-10 hours with nothing meaningful landed, and sends a
daily 08:17 reminder while a stall lasts. The director's host fixes reduce how often the host goes down
(`docs/operations/MAINTENANCE.md` "Host settings", and the 7 Nov entry in `maintenance-log.md`). The off-box check
makes sure the next outage is noticed. No new on-box control is proposed: anything on the box shares the same fate.

**Open.** The outside check reads "meaningful landing" from origin. A machine that is up but landing only
heartbeats would look the same as one that is down, and that is the right alert in both cases. Nothing to build.

**Reverse.** Delete this file and the two operations entries. Nothing else changed.

## Causes of both stops, and the off-box check (8 Nov, on the director's 13:22 "yes")

**Correction to "Open" above.** The advisor's cloud check is not enough on its own. The director ruled the
dead-man's single push off the box, and it is built (below).

**5-7 Nov (about 60h): the host stopped the WSL VM. Windows stayed up.**
- The Windows System log shows continuous uptime: 1,825,468s at 5 Nov 12:00 and 1,998,251s at 7 Nov 12:00, with
  no shutdown, sleep or update restart in between.
- The guest's journal (`journalctl -b -2`) ends at 03:31:46Z mid-run (a sim run printing progress lines), with no
  shutdown sequence and no OOM line. At 03:31:52Z the host deleted the guest's virtual NIC (Hyper-V-VmSwitch 233,
  then 69 "port deleted" at 03:32:00). The guest was stopped from the host side, not from inside.
- Nothing names who stopped it: no WSL, LxssManager or vmwp crash in the Application log, and Windows Error
  Reporting shows only the recurring LiveKernelEvent 193 every ~4h, which runs through 3-4 Nov too with no stop.
  **We cannot tell** whether it was `wsl --shutdown`, a WSL service fault, or host memory pressure on vmmem.
- What would let us tell next time: a host-side record of the WSL VM's state (a Windows scheduled task logging
  `wsl --list --verbose` and vmmem's working set every few minutes to a file the guest can read on restart).
  That is a host change, so it is the director's to approve, and it is not proposed as a gate.
- 7 Nov 14:56:09Z: an unexpected Windows shutdown (Kernel-Power 41, EventLog 6008), then a boot at 15:24. This is
  consistent with a hard power-off of a machine found unresponsive. At 15:45 came a user-approved restart for
  Windows 11 26H2 (User32 1074, MoNotificationUx).

**3-4 Nov (about 24h): not a stop. The machine was up, and every invocation failed to authenticate.**
- The ops heartbeat ran every 30 min throughout: the longest gap from 4 Oct to 8 Nov outside 5-7 Nov is 2.9h.
- From 3 Nov 09:15Z to 4 Nov 09:05Z, `worker-tick-log.md` shows every dispatched `claude -p` exiting `rc=1` with
  "Failed to authenticate: OAuth session expired and could not be refreshed". The 4 Nov 08:34 steer (wire the
  long-lived token) was the fix.
- A heartbeat check cannot see this shape. A box that is up but landing nothing is the advisor's cloud check
  (meaningful landings on origin), which stays.

**The off-box check.** In the private ops repo, commit 2b628fed8:
- `.github/workflows/off-box-deadman.yml` runs hourly at :23.
- `tools/offbox_deadman.py` reads three box-only signals: the ops heartbeat, the public `liveness` branch
  heartbeat, and the newest `t@t`-committed commit on public main. Advisor commits are excluded.
- It sends the single NTFY push when all three are over 6h old (`dead`), once per outage (cache key = newest
  signal). Each of the three is written only by the box, so this tells a dead machine from a broken heartbeat
  push. If the ops heartbeat is stale but another signal is fresh, the run reads `path_broken`: a warning on the
  run, never a push. The topic is the Actions secret `NTFY_TOPIC`, set from the env file and never printed.
- **Proof:** 6 tests, including all three verdicts reachable. A dispatched run on GitHub forced stale
  (`threshold_hours=0.01`, dry run) decided `dead`; a live dispatched run decided `alive`.
- **Replayed hourly over 4 Oct-8 Nov (835 checks):** exactly one push, at 5 Nov 10:16Z for the 03:29Z outage, and
  no false push. The measured false-alarm rate on that history is 0. The 2 `path_broken` hours fall inside the
  outage, where the last box commit postdates the last heartbeat. They delay the push by about an hour.
- **Unproven leg:** the `curl` to ntfy.sh from GitHub has not sent a real push, because the only way to prove it
  is a false alarm on his phone.
- **Reverse:** delete the workflow, `tools/offbox_deadman.py` and `tests/test_offbox_deadman.py` in the ops repo,
  then `gh secret delete NTFY_TOPIC --repo 21bcarlisle-arch/synthetic-enterprise-ops`.
