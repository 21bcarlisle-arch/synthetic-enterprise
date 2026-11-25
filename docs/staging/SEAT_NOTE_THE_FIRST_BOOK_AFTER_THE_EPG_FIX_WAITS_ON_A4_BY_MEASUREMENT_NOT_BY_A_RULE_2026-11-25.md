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
