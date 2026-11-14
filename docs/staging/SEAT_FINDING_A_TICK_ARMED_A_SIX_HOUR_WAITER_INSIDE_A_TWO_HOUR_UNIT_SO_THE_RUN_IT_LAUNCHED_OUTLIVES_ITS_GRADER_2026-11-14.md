**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# A tick armed a six-hour waiter inside a two-hour unit, so the run it launched outlives its grader (2026-11-14)

**What was found.** The worker tick (pid 1724978, `worker-tick.service`, started about 09:39Z) launched the
value-test s.2 published-configuration pair (pid 1875257, `longjob-vt-published-config-redraw.service`,
09:55:28Z) and waited on it with a 6h `tools/wait_for.py` waiter. `worker-tick.service` carries
`TimeoutStartSec=7200`, so systemd kills that tick at about 11:39Z. The long-job unit has
`RuntimeMaxUSec=infinity` and sits in its own cgroup, so the run survives and the tick that was meant to
grade it does not. `wait_for.MAX_DEADLINE_SECONDS` is 6h, which is three times the enclosing unit's cap.
Nothing compares a waiter's deadline with the time its own process has left.

**Read at 11:36Z.** Of the six full-window arm runs (two seeds, three arms each), two have finished. The
third (seed 20260724, level arm) is at 2023-04. About 37 minutes per arm puts the pair's two JSON files in
`/var/tmp/vt-pub-out/` at about **13:30Z**. The seat-executor has the same kind of limit
(`TimeoutStartSec=6600`, drawn 11:35Z). It cannot wait that long and still land through the gates, which take
more than ten minutes, so this seat hands the grade on rather than holding a waiter it would also outlive.

**What it costs.** It costs nothing in compute, because the run finishes anyway. It costs a draw: the grade
falls to whoever re-takes the item after the outputs appear. A tick that holds a waiter past its own kill time
looks busy and cannot finish. That is the R15 shape of a guard that looks armed.

**Smallest fix that can fail.** `wait_for` should refuse, and name the reason, when it is given a deadline
that ends after its enclosing systemd unit's `TimeoutStartSec`. It can read the unit's
`ActiveEnterTimestampMonotonic` plus the timeout from `/proc/self/cgroup` → `systemctl --user show`. When the
remainder is shorter than the deadline, the right move for a tick is to hand off (`seat_continuation
--hand-off`) and let the run notify the next taker.

**Next for the grade.** `seat_continuation` item `value-test-s2-published-pair-grade-if-the-worker-tick-did-not`
has been re-handed with the 13:30Z ETA. Its first step is to check that
`/var/tmp/vt-pub-out/member_published_11111.json` exists, and to grep origin's s.2 for a grade.
