**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

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

## Still live
- **2026-08-28** — still live. 1 repeats over 3.5h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `land-the-suspended-book-and-rerun-on-residential` (first seen 2026-08-26)
- `rerun-the-ab-on-the-dual-fuel-book-and-attribute-the-divergence` (first seen 2026-08-26)
- `the-ceiling-priced-half-the-book` (first seen 2026-08-26)
- `lane-zero-progress-signal-is-a-constant` (first seen 2026-08-26)
- `rerun-the-ab-and-publish-the-three-unread-instruments` (first seen 2026-08-27)
- `separate-price-from-prediction-with-a-ladder` (first seen 2026-08-27)
- `run-both-instruments-at-full-window` (first seen 2026-08-27)
- `land-the-alarm-that-was-written-about-this-tail` (first seen 2026-08-27)
- `size-then-run-the-full-window-instruments` (first seen 2026-08-27)
- `reconcile-the-directors-red-census` (first seen 2026-08-27)
- `land-s1-price-sensitivity-and-regrade-the-belief` (first seen 2026-08-27)
- `the-noise-floor-must-patch-the-symbol-the-decision-calls` (first seen 2026-08-27)
- `land-the-widened-world-past-the-two-reds-that-refused-it` (first seen 2026-08-28)
- `land-the-widened-world-then-run-the-three-arm-ab-once` (first seen 2026-08-28)
- `measure-the-widened-world-once-and-bring-its-error-bar-with-it` (first seen 2026-08-28)
- `measure-the-decision-surface-the-ab-actually-has` (first seen 2026-08-28)
- `reconcile-the-two-net-margins-the-ab-publishes-for-the-same-arm` (first seen 2026-08-28)
- `rerun-the-three-arm-ab-on-the-repaired-clock-and-restate-the-headline` (first seen 2026-08-28)
- `repair-the-published-treasury-clock-and-register-the-class` (first seen 2026-08-28)
