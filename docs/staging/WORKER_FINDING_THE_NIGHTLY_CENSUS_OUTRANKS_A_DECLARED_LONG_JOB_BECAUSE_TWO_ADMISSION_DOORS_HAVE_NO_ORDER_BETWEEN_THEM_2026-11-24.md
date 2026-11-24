**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The nightly census outranks a declared long job, because two admission doors have no order between them

Found by the worker, 24 Nov 2026, on the delivery seat's direction `s12g-rankq-gets-the-box-ahead-of-the-census`.

**Owner:** lane H_harness. The ranking belongs in `tools/head_green_census.py::_queued_for_room`, which is the census's own admission. `background/launch_long_job.py` is where the waiting row is lost.

## What happened (measured, not inferred)

- The `head-green-census.service` pass was admitted at 03:31:51 GMT by `resource_headroom.queued` and reserved about 11 GB (pid 1883975; its pytest is pid 3481599).
- `value-test-s12g-rankq` was launched at about 06:03 and queued in `longjob-value-test-s12g-rankq-queued`. Its log says it fits "only once these have gone: pid 1883975 ... [head-green-census.service]". That is 26,325 MB of declared load against a 23,010 MB ceiling.
- It waited 3h34m. In that time its log shows **13 `HELD: landings come before experiments` lines, each naming a different landing pid**.
- At 09:37:32Z the census was 3h35m into a 17,400 s bound and had reached 22,727 tests. About 8.5k tests remained (`tests/tools` alone has 8,283). At its average rate of about 106 per minute it would have hit the bound after roughly another 80 minutes, without completing. The seat stopped it: `systemctl --user stop head-green-census.service`. **To restart it:** `systemctl --user start head-green-census.service`, or let `head-green-census.timer` fire tonight. The progress file `/var/tmp/head_census_progress_irofj_h6.tsv` keeps what this pass reached.
- rankq was admitted 13 s later, at 09:37:45Z, and is running (`/var/tmp/longjob-value-test-s12g-rankq.log`). **Once the room was free, the landings hold did not re-hold it**, so this pass has no starvation instance to record. No release lever was used.

## The class (two defects; the second makes the first worse)

1. **There is no order between the two doors.** Heavy work passes `resource_headroom.queued`, and long jobs pass `launch_long_job.co_residence`. Both count one ledger, but neither ranks against the other: whoever is resident first keeps the box. So a nightly diagnostic that the bound cuts short anyway, and which then completes nothing, outranks the thesis's live test simply by arriving first. Nobody ranked the census above rankq; there was nothing in which to rank it.
2. **A memory refusal costs the job its place in the landings queue.** On each 60 s retry the job first goes through `_wait_for_pending_landings`, which is FIFO. Once the landings ahead of it clear, `landing_hold_reason` deletes its waiter row, and then `co_residence` refuses for memory. On the next retry `mine is None`, so it is re-appended behind whatever landing is pending at that moment. That is why there are 13 different landing pids in its log. The hold is FIFO only within one attempt. Across attempts the job goes to the back every time, and the two holds alternate.

## The cut proposed (smallest one that can fail)

- In `_queued_for_room`, the census refuses admission, with a named reason, while any `longjob-*-queued.service` unit is active. A declared long job that is waiting outranks the diagnostic. The census already defers with a reason on `observed`, so this adds one more deferral cause, not a new mechanism. Control: a fake active queued unit makes the census defer, and with no queued unit it is admitted. Both legs go in one assertion over the partition.
- In `launch_long_job`, the waiter row is kept until co-residence also admits, or until the queue deadline is reached, rather than withdrawn on landing-clearance alone.
- **Not proposed:** pre-empting a census that has already been admitted. A stop is a judgement for the seat, as this pass made it; automated, it would kill every census whenever any job queued.
