**Severity:** LATENT · **Lane:** H_harness

# [SEAT] value-cycle-ab-rerun-after-the-observables-fix was claimed and has not moved for 2.0h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] value-cycle-ab-rerun-after-the-observables-fix was claimed and has not moved for 2.0h
NO PATHS WERE EVER BOUND to this claim, so nothing about it could be observed -- it is released on the clock, not because the work was seen to stall. Bind the paths of each landing as it lands (`delivery_lane.record_landing`) and this becomes a real signal. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Run the A/B again on the fixed chain and read what it says. `python3 -m tools.run_value_cycle_ab --out docs/observability/value_cycle_ab_2026-08-26_observables_threaded.json` -- the `--out` argument e
```

## What is known without diagnosing anything

- Signature: `seat-claim:value-cycle-ab-rerun-after-the-observables-fix` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T11:32:40+00:00
- Repeats before escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Discharged 2026-08-28

**The claimed work is done.** `python3 -m tools.run_value_cycle_ab --level-arm` ran on the current
world at 2026-08-28T10:47:24Z and wrote `docs/observability/value_cycle_ab_s1_three_arm.json`. The
result is not a formality: the baseline arm now reproduces the published run to 6.75e-09 of a pound
(`site/data/value_arms.json` → `realised.is_the_published_supplier.same_supplier = true`, after two
days of divergence), and the headline reversed — per-customer £154,699 against flat rules £159,423,
selection −£9,627.

**Acceptance:** `site/test_the_baseline_comparison_reaches_the_reader.py::test_the_published_supplier_claim_reaches_the_reader`
is the control that was RED on this condition and is now green; it asserts the published run and the
baseline arm are the same supplier and fails when they diverge. That test, not this document, is
what will notice next time.

**What the alarm got right, on the record:** its own text said "NO PATHS WERE EVER BOUND to this
claim, so nothing about it could be observed — it is released on the clock, not because the work was
seen to stall." That was accurate. The claim really had not moved for two days, and the reason the
rerun finally happened is that the site lane refused a commit — a bound control caught what an
unbound claim could only guess at. The repair the alarm asked for (bind paths at
`delivery_lane.record_landing`) is still owed and is not done here.

**What it created:** `docs/staging/WORKER_PREREGISTRATION_WHAT_THE_CHASE_OFF_RUN_MUST_SHOW_2026-08-28.md`,
because the rerun's result has two candidate causes and separating them is now the open question.

## Still live
