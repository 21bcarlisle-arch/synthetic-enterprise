**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- a machine finding about the publish path's own clock

# A worker session that runs the publisher late in its tick is killed mid-landing, and the attempt records no outcome (2026-11-26)

**What happened.** The 19:32Z worker-tick spawned a bounded `claude -p` session. That session landed
44bf4cd13f at 20:58Z, which re-froze the Channel F growth that refused the 20:51Z publish. It then
re-ran `process_run_complete` itself on `run_complete_20261126T155009Z.md`. That publisher started at
20:58Z and reached `Publish landing: ... declared as drops` at 21:12Z. At 21:32:33Z systemd killed
worker-tick.service on `TimeoutStartSec=7200`, and the publisher went with it, because it was in the
same cgroup.

**What this means.** The sim-runner log has no `Commit/push failed` line after 21:12Z, and the marker
in `done/` still carries the 20:51Z `commit_refused` stamp. So the wedge record holds a refusal
whose cause had already been repaired, and a fresh attempt that never got a verdict. A reader counts
that as one more failed cycle, but the gate never refused anything. The surgical landing takes
about 20 minutes under load, and a whole publisher cycle takes about 35 to 40 minutes. A session
that starts one with less time than that left in its tick will lose it.

**Smallest fix to weigh.** Before a bounded worker starts a publisher cycle, it compares the time
left in its tick with the publisher's own deadline (`_publisher_deadline_seconds()`). If the cycle
cannot finish, it leaves the marker for `background_worker`'s sweep, which runs outside the tick's
cgroup. Then it says so in the log. A second option is to have a killed publisher stamp
`killed_by_tick_timeout` from a SIGTERM handler, so the record shows an interruption and not a
silent hole. Neither has been built.

**Evidence.** `journalctl --user -u worker-tick.service` 19:32:33Z to 21:32:34Z ("start operation
timed out. Terminating", 2h 1.379s wall clock). See also `docs/observability/sim-runner-log.md`
from 20:58Z to 21:32Z. The 21:33Z re-run was started from the 21:32Z tick's session, which had about
two hours left; see its outcome in the work item.

## The re-run, and a second cause the record did not show (21:33Z to 21:52Z)

The re-run got past Channel F and was then refused for a different reason: *"this is the PRIMARY
checkout and its HEAD 44bf4cd13 is 2 commit(s) behind origin/main (d415a9787)"*. The killed session
had landed 44bf4cd13f locally but never pushed it, and origin then took 7ead3bb0c3 and d415a97872. So
the fix that cleared the gate was stranded where the publisher could not fast-forward. This is the
same family as the kill: a session that lands the cure and then dies before pushing it leaves the
cure unreachable. Repaired by `surgical_land --merge origin/main` (0ad923f28), pushed at about
22:00Z, followed by a third publisher attempt.

## The third refusal, and what is left on disk (22:42Z to 23:15Z)

The third attempt (21:54Z) fast-forwarded and was refused by one real red test:
`site/explore/test_a_catch_up_bills_vat_is_the_vat_of_the_lines_above_it.py::test_inv5940_...`.
It pinned the 6af7fd0bf book's £21.57 catch-up. The new book's April 2023 bill carries £77.28 and
renders correctly (VAT £8.86 = 5% of the £177.21 above it). The test is re-keyed to the property in
the working tree: 6 green, and it is mutation-killed when the catch-up row moves below VAT. **If it
is not on origin when you read this, land it.** The landing was in progress, waiting on another
lane's gate lock, when the session's own tick deadline came. The message is at
`/tmp/seat_land_msg_vatpin_2026-11-26.txt`, and the paths are this file, that test, and
`docs/work/items/seat-finding-the-cash-forecast-provision-...-ranks-worse.yaml` (parked). Then
re-run `python3 -m background.process_run_complete docs/staging/done/run_complete_20261126T155009Z.md`
from a session with at least 50 minutes of its tick left. Not yet attributed: why that catch-up grew
from £21.57 to £77.28 between the two books.
