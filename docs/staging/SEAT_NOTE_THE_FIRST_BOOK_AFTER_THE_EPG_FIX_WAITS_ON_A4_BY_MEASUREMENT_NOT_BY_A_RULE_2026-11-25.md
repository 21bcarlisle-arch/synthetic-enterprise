# The first book after the EPG fix waits on A4 because the box is full, not because a rule is wrong

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Seat note, 2026-11-25 05:25Z. Drawn: `the-first-book-after-the-epg-fix-publishes`.*

## What refuses the book now

- **land11 ended at about 04:21Z.** From 04:21Z the refusal changed from `budget exhausted`
  (12,000 + 6,000 + 7,066 > 23,010) to `cycle_admission`'s long-job yield
  (`background/sim_runner.py`, the `decision.get("long_jobs")` branch). A cycle defers to any
  resident long job, even when the declared arithmetic fits.
- **The 'could not change what refused the last one' branch (`book_admission`) no longer refuses.**
  `next_book_requires.yaml` lapsed on 24 Nov and is logged as not applied. The queued-unit leg
  last fired at 03:06Z, on `longjob-a4-ep1-dated-rate-value-arm-queued.service`, which became
  the running A4 unit at 03:08Z. No `longjob-*-queued*` unit is active now. No fix is owed there.
- origin/main (5e5f596949) descends from b14889688, so `code_admission` has nothing to hold.

## Why the yield is left in place: measured, it refuses too

The direction's premise was that 12,000 + 7,066 MB fits inside 23,010 MB. That holds on declared
figures. It does not hold on the box, measured at 05:22Z:

| what | MB |
|---|---|
| MemAvailable | 12,827 |
| A4 resident (PSS), `VmHWM == VmRSS` so it is still growing | 6,111 |
| A4 growth still to come, up to its declared 12,000 | ~5,900 |
| room left once A4 reaches its declared peak | ~6,900 |
| what a cycle needs: weight plus the 1,024 floor | 8,090 |

Other residents nobody declared hold about 3.4 GB: seat-executor 2,181 MB, the small daemons, and
about 1.7 GB of kernel and other memory the census does not see. That is more than the 1,024 MB the
budget sets aside. The rule I would replace the yield with is "measured availability less each long
job's growth still to come". It refuses this cycle too, by about 1.2 GB. Landing a change to an OOM
guard that cannot admit anything before A4 ends buys nothing, so I left the rule as it is.

**Prediction, filed before the answer:** A4 is declared to run for 900 minutes from 03:08Z, so it
should end by about 18:08Z. The first sim-runner cycle after it ends admits the book, with
`admitted:` in the log and no `DEFERRED` line. If A4 ends and the cycle still defers, the reason it
logs is the next thing to fix.

## Still owed once the book is built

Run the bills grade (`process_run_complete.billing_grade_refusal` →
`tools/grade_svt_invoices_over_ceiling.py`) and `company/compliance/domain_invariants.py` on that
book. If either refuses it, list the breaches by account and fix the class with a mutation.

## Re-measured 08:25Z (worker tick): the prediction still stands

A4's child (pid 2690439) is at 10,452 MB RSS, with a 10,663 MB high-water mark and 387 MB swapped,
so about 1,160 MB of its declared 12,000 is still to come. It grew as this note said it would.
MemAvailable is 9,036 MB, and a transient 1 GB operational pytest is part of what holds it. The
replacement rule gives 9,036 − 1,160 − 7,066 = 810 MB, which is below the 1,024 floor. It still
refuses. Between 07:21Z and 08:21Z the log alternated between `measured memory too tight` (7.5–7.9 GB
available) and the long-job yield. Both describe the same full box. The yield stays in place.
Nothing new is owed until A4 exits (expected by ~18:08Z).

## Re-measured 10:57Z (re-draw): land11 is gone, A4 alone holds the book, the yield still stays

- Every cycle from 09:31Z to 10:56Z logs the same reason: `cycle_admission`'s long-job yield, naming
  only `longjob-a4-ep1-dated-rate-value-arm.service` (468 of its declared 900 minutes).
  `longjob-land11-...` is `failed` and holds no memory. `queued_long_jobs()` returns `[]` and
  `next_book_requires.yaml` has lapsed, so `book_admission` (the line-540 branch) has nothing to
  refuse. origin/main (ff9933dacd) descends from b148896885.
- A4's child, pid 2690439, holds 7,340 MB RSS (VmHWM 10,663 MB, 43 MB swapped). MemAvailable is
  12,351 MB. Those are sample()'s figures plus /proc/2690439/status.
- The replacement rule ("measured availability less growth still to come") gives two answers,
  depending on what it counts as still to come:
  - Counting growth from the high-water mark: 12,351 − (12,000 − 10,663) − 7,066 = 3,948 MB, which
    is over the 1,024 floor.
  - Counting growth from current RSS, which is the honest worst case since A4's RSS rose and fell
    6.1 → 10.4 → 7.3 GB this morning: 12,351 − 4,660 − 7,066 = 625 MB, which is under the floor.
  A rule that admits only because A4 is between peaks is the 19:07Z kill shape. Getting it wrong
  kills a thesis run that has done 7.8 hours of work. Waiting costs about 7 hours of book latency.
  **The yield stays in place.**
- This re-draw changes nothing. The 05:25Z prediction stands: the first cycle after A4 exits
  (expected by about 18:08Z) logs `Starting` or `admitted`, with no `DEFERRED` line. The item is
  handed on with a time gate after that.
