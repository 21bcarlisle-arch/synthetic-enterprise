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
