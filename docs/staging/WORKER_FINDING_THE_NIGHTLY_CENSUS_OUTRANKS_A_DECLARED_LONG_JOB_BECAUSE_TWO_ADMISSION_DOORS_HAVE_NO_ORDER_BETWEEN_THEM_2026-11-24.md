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

## Second instance, 27 Nov 2026: measured, and the cut above would not have caught it

The delivery seat recorded this on its direction `the-admission-gate-counts-shared-pages-and-starves-every-run`. That direction guessed that `resident_census` counted RSS and so double-counted shared pages. **Measurement refutes the guess.**

- **The 11,981 MB was a reservation, not a measured resident.** `resident_census` has read Pss since 2026-10-08. At 12:37Z it read the census's pytest (pid 3382024) at Pss 4,436 MB against RSS 4,445 MB, so there is no shared-page over-count to remove. The 11,981 MB the queue logs named was the census's `resource_headroom` ledger row, `weight_mb` = `CLASS_WEIGHTS_MB["head_green_census"]`. `co_residence` counts that weight as max(RSS, reserved).
- **The weight is low, not high.** `weight_drift("head_green_census")` reads `under`: a 14,384 MB cgroup peak over 12 runs in -30d (cgroup peaks include page cache, about 1.6 GB of it at 12:37Z). Counting less would admit into memory that the census reaches later in its run, so the admission count was left alone.
- **Arrival order was not the cause.** The census queued at 03:31Z and was admitted to pytest at 08:01Z. anchor7 (about 11:10Z), the S2 pair (about 11:39Z), memgrowth (about 11:49Z) and S3 losses (about 08:44Z) all queued after it. The `_queued_for_room` cut proposed above, which defers the census while a queued long job exists, would not have stopped this. What kept the box was **a resident census that could not complete**. At 12:38Z it was 16,616 s into its 17,400 s bound with 24,362 tests run of about 39k. That is the 16 Nov finding's "no census has completed since 4 Nov", still true.
- **Action.** The seat stopped `head-green-census.service` at 12:39:10Z. The S2 gas-quoted pair (off and arm, `5e075efa94`) was admitted at 12:38:54Z, as the reservation was withdrawn. anchor7, memgrowth and S3 losses are still queued. They are now held by memory against the two S2 legs' declared 7,500 MB peaks, which is a true count, and they admit themselves as those legs end. None of them was cancelled or relaunched. What this pass reached is copied to `/var/tmp/head_census_progress_stopped_20261127.tsv`.
- **How the census is re-run.** The transient unit `census-requeue-behind-five.service` runs `/var/tmp/se-census-requeue/requeue.sh`. It polls every 120 s and starts `head-green-census.service` only once all five long jobs, `-queued` units included, are inactive, with a 24 h deadline. If the nightly timer has already re-run the census by then, it does nothing. Its log is `/var/tmp/census-requeue-behind-five.log`. To run it by hand: `systemctl --user start head-green-census.service`.
- **The cut this instance argues for** (H_harness; recommendation, not built here). The census should not be admitted to a pass it cannot finish. Either bound it below its own unscoped duration and shard it, or have it give way when a declared long job queues behind its reservation. Arrival order alone decides nothing that matters here.
