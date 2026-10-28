**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Pre-registration: the meter label taken from the billed reads, graded on the 129e7de698 book (2026-10-28)

**Item.** `the-meter-type-has-one-home`, answering
`SEAT_FINDING_THE_THIRD_COLD_READ_FINDS_THE_METER_TYPE_PRINTED_FROM_TWO_RECORDS_THAT_DISAGREE_2026-10-28.md`.

## What the trace established before this was written

These were measured before anything below was predicted.
- **The two records.** The cold read's scratch render (`/var/tmp/third-read-scripts/pages.py`) rebuilt
  the customer records from the fresh book. It did not rebuild `explore_hh_days.json`, so the day clock
  read the 26 Oct feed while the header read the fresh book. The production chain
  (`process_run_complete`) does rebuild both, in the right order. So the *disagreement* is a
  property of that render.
- **The header label was the wrong record.** `_meter` asked `saas.customers` at page-build time. In a
  fresh process that book carries no smart flag for a drawn household. On the 129e7de698 book,
  **273 of 1,293 accounts** were billed on smart reads (`meter_read_log.meter_type`) and labelled
  "Traditional". Only 9 labels agreed with a smart read. The day clock's "smart meter" sentence on
  SYN-2016-479 and PROS-2025-0153 was the *true* one: 15 of 15 and 1 of 1 of their reads are smart.
- **The fix.** The label now comes from the latest read in the run's `meter_read_log`. The day clock
  chooses its sentence from that same field on the household's electricity record. Rebuilt on the
  129e7de698 book, all 1,293 labels agree with the reads: 282 Smart, 1,011 Traditional.

## What this moves, and the prediction

`INV_SMART_METER_BILLED_ON_ITS_OWN_READS` grades only accounts whose printed label is "Smart". So its
population goes from 9 accounts (7 fuel-years) to 282. Its exception (`max_breached: 4`, all on C2) was
written over the 9.

**Prediction, written before the run:**
- Fuel-years graded: 15–20.
- **Breached: 0–2.** C2's estimates are diluted among 282 accounts.
- **Flagged (share below 1%): at least 4 fuel-years.** A communicating smart meter in this world seldom
  needs an estimate.
- **I cannot yet say** whether any fuel-year sits above its upper bound (electricity 15%, gas 25%).
  Moving 273 accounts into the row could also expose a new breach class. If it does, that class is a
  finding, not an exception to widen.

**Method.** One variable. The same scratch-graded book is built twice from this worktree. The only
difference is the printed `meter_type`: the old `saas.customers` label, then the billed-read label.
Only this row is run.

## Results

*(appended below after the run; nothing above is edited)*

Graded 2026-10-28. Built from this worktree over `/var/tmp/fresh-run-out-129e7de698` and
`/var/tmp/third-read/ledger.json`, with `/tmp/meter-grade/grade_one.py`. That script is the third
read's `grade.py` with one change: the printed `meter_type` is either the old label or the new one.

| | old label (`saas.customers`) | new label (billed reads) |
|---|---|---|
| accounts labelled Smart | 9 | 282 |
| fuel-years graded | 7 | **20** |
| breached | 4 (C2 and C2g, excepted, `max_breached: 4`) | **0** |
| flagged, share below 1% | 1 (electricity 2019, 0 of 9) | **0** |
| flagged, run of more than 6 estimates | 1 (C2) | **21**, on 14 accounts |

- **Fuel-years 15–20: held** (20).
- **Breached 0–2: held** (0). The four C2 fuel-years fall inside their bands once C2 sits among 282
  accounts. C2's own run of seven estimates is still flagged. The C2 exception is now unreached. It
  retires on the next fresh run that carries this fix, by its own `retired_by`.
- **At least 4 fuel-years flagged below 1%: refuted.** None are. Smart bills in this world are
  estimated more often than 1% in every fuel-year. My belief that "a communicating smart meter
  seldom needs an estimate" was wrong for this world's read model.
- **Not predicted:** 21 account-level flags, each a run of seven estimated bills on an account billed
  on smart reads. 13 of the 21 are gas legs. PROS-2020-0126 carries six of them (two electricity, four
  gas). These runs were always on the book. They were invisible because those accounts were
  labelled Traditional. They are flags, not breaches, so the publish stands. Whether seven estimates
  in a row are plausible on a SMETS meter in smart mode is a question for the read-duty rows. It
  goes to the hand-off, not to an exception.
