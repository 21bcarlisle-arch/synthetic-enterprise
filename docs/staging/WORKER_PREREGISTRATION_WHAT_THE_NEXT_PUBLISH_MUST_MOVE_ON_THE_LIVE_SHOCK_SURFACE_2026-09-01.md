# [WORKER PREREGISTRATION] What the next publish must move on the live shock surface

**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted
**Filed:** 2026-09-01, **before the run that settles it.** Every number below was read out of the
artefact that is live right now, before any further run or publish.
**Knowledge:** `docs/market_research/what_bill_shock_is.md` — the definition, established and NOT
re-opened.
**Predecessors:** `WORKER_PREREGISTRATION_WHAT_SPLITTING_THE_SHOCK_SERIES_BY_POPULATION_MUST_SHOW`
(landed `98db658f2`) and `WORKER_PREREGISTRATION_WHAT_MAKING_THE_SHOCK_SIGNED_MUST_SHOW` (landed
`da0431897`). Both were graded against the **record**. Neither was graded against the **published
surface**, and this is the one that does that.

## Why this exists

The split landed and the sign landed. **Neither has ever reached a published figure**, and the
surface does not say so.

`site/data/dashboard.json` is generated from `run_output_486eedb40_20260901T142317Z.json`:

    meta.generated_at   2026-09-01T14:36:00Z
    meta.git_commit     c9dd75e47
    source run          486eedb40   (14:23)

`da0431897` landed at **16:58**. So the surface carries the *labels* of the split over a quantity
that two later commits redefined. That is `figures_on_a_superseded_clock`, and it is the sharper
member of the family: **the label reads as proof the correction happened.** A reader sees
`avg_shock_pct_definition: "bill"` and concludes the series means what the definition says. It does
not yet.

Measured ancestry against the run, so this is one variable and not several:

| commit | in the published run? |
|---|---|
| `41cdd5b51` baseline floor | **YES** — already applied |
| `fc1c9a65c` channel reaches the bill | **YES** |
| `a984ad213` population through the reducer | NO — yet the events carry the field, so the run executed uncommitted working-tree code |
| `98db658f2` the split | NO |
| `da0431897` the sign | NO |

**The floor is already in.** So the next publish is not confounded by it, and the only thing that
moves these series is the sign.

## The before state, measured now, on the live artefact

Whole book, 3,161 published shock events (`bill_shock_events`, i.e. bills flagged at the
`BILL_SHOCK_THRESHOLD` of 20% — not all bills):

| population | n | mean % | median % | max % |
|---|---:|---:|---:|---:|
| `payment` (direct debit) | 2,238 | 113.9 | 50.8 | 2,593.1 |
| `bill` (standard credit) | 912 | 93.4 | 45.4 | 1,305.2 |
| `unknown` (no channel) | 11 | 158.1 | 150.7 | 311.5 |
| `out_of_scope` (prepayment) | 0 | — | — | — |
| mixed, all populations | 3,161 | 108.1 | | |

`catchup_driven` on 870 of 3,161 (27.5%). **Events carrying a negative: 0** — of course; every one
was `abs()`-folded before it was written.

`out_of_scope` is 0 because this world has two payment channels and no prepayment household, which
`saas/bill_generator.py:82-89` declares rather than hides. That is correct and is not a prediction.

## The predictions

**P1 — every population's event count FALLS.** The sign fix can only remove events (a bill that
fell stops being a shock); it can add none. *Refuted by* any population's n rising, or by `payment`
or `bill` being unchanged.

**P2 — `max_pct` falls or is equal in every population, and never rises.** Removing members cannot
raise a maximum, and the floor is already applied so nothing new enters at the top. *Refuted by* any
`max_pct` above the figures tabled above.

**P3 — no negative ever appears on the surface.** The fix produces `None`, not a negative.
A negative reaching `avg_shock_pct`, `shock_by_population[*].avg_pct` or
`mixed_all_population_avg_pct` means a signed value was published into a field defined as unsigned.
*Refuted by* any negative anywhere in `monthly_ops`.

**P4 — `mixed_all_population_count` falls by exactly the sum of the per-population falls.** The
mixed figure is kept deliberately so the size of the re-partition is checkable from the artefact
alone; it is only worth keeping if it stays reconcilable. *Refuted by* the sum not tying.

## What is deliberately NOT predicted, and the argument I rejected

**The direction of any population's mean.** I do not file one, because I could not derive one, and a
direction filed after the run would not be a prediction.

I record the argument I considered and **rejected**, because it is the sort that reads as rigorous
and is wrong:

> Every removed event is a decrease. A bill can fall at most to zero, so a decrease is bounded at
> −100%, so every removed value entered the mean at ≤ 100. `payment`'s mean is 113.9 > 100.
> Therefore removing them must **raise** `payment`'s mean, with certainty.

**That is false, and this project has already paid to find out.** A catch-up *refund* bill can carry
a negative total, so the ratio is not bounded at −100%. The value that took the publish cycle down
on 2026-09-01 was **−1.4434469164399073**, i.e. −144.3%
(`WORKER_FINDING_REPEATING_ALARM_RUN_FAILED_AFTER_S_VALUEERROR_BILL_SHOCK_PCT_MUST_BE`). The removed
set therefore straddles the mean and the direction is genuinely open.

If the means move a long way, **that is a result to explain, not a prediction to claim afterwards.**

## What settles it

The next `background/process_run_complete` publish. Read `monthly_ops` in
`site/data/dashboard.json` and grade P1–P4 in this file, beside the predictions, whichever way they
fall.

## What this does NOT close

The `unknown` population is 11 events with no `payment_channel` at all. The sign fix does not touch
attribution, so those 11 will still be unattributed after it. **A shock measure that cannot say
which definition applies to eleven of its own rows has not finished**, and that is a separate item
from this one.
