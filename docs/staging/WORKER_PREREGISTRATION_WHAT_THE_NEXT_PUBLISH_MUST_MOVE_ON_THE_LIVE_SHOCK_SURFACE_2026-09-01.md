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

---

# GRADED, 2026-09-01, against the publish that settled it

The publish landed at `318066998`. `site/data/dashboard.json` now reads:

    meta.generated_at   2026-09-01T16:06:49Z
    meta.git_commit     64e586f3b            (this file's own commit)
    source run          run_output_98db658f2_20260901T155311Z.json

**One thing about that provenance has to be said before any grading, because it is the same defect
this file was written about.** The run output is stamped `98db658f2` and timed 15:53:11Z;
`da0431897` — the sign fix — landed at 15:58:15Z, **five minutes later.** By its stamp this run
predates the change being graded. It does not: the event count below is 1,748, which is `da0431897`'s
own pre-registered P2 to the unit, and no code path other than the sign fix produces it. **The run
executed working-tree code that was not yet committed**, exactly as the ancestry table above recorded
for `a984ad213`. The grading stands because the artefact carries the fingerprint of the change; the
provenance stamp does not, and would have been the wrong thing to trust. That the run stamp cannot be
relied on to say what code ran is a real defect and it is not this item's.

## The after state, measured on the live artefact

| population | n | mean % | median % | max % |
|---|---:|---:|---:|---:|
| `payment` (direct debit) | 1,231 | 152.5 | 62.8 | 2,593.1 |
| `bill` (standard credit) | 512 | 117.3 | 56.1 | 1,305.2 |
| `unknown` (no channel) | 5 | 142.3 | 144.3 | 295.6 |
| `out_of_scope` (prepayment) | 0 | — | — | — |
| mixed, all populations | 1,748 | 142.2 | | |

`catchup_driven` 454 of 1,748 (26.0%), from 870 of 3,161 (27.5%).

## P1–P4

**P1 — every population's count falls. CONFIRMED.** `payment` 2,238 → 1,231; `bill` 912 → 512;
`unknown` 11 → 5; `out_of_scope` 0 → 0. No population rose; neither `payment` nor `bill` was
unchanged, which was the named refuter.

**P2 — no `max_pct` rises. CONFIRMED, and it is the weakest of the four.** `payment` 2,593.1 →
2,593.1 and `bill` 1,305.2 → 1,305.2 — both *equal*, not lower. Recorded plainly: a prediction that
"falls or is equal" and comes back equal on both real populations was nearly unfalsifiable by this
run. It survived, and it earned very little.

**P3 — no negative anywhere on the surface. CONFIRMED.** Swept every numeric field of `monthly_ops`
across all 113 months — `avg_shock_pct`, `median_shock_pct`, `max_shock_pct`, both CI bounds,
`mixed_all_population_avg_pct` and all five fields of all four populations. Zero negatives. The
fail-closed guard in `simulation.contact_propensity` is still armed and still never saw one.

**P4 — `mixed_all_population_count` falls by exactly the sum of the per-population falls.
CONFIRMED.** 3,161 → 1,748, a fall of 1,413; the per-population falls are 1,007 + 400 + 6 + 0 =
1,413. The mixed figure is still reconcilable and therefore still worth keeping.

## The thing that was not predicted, explained rather than claimed

**Every real population's mean rose a long way** — `payment` 113.9 → 152.5, `bill` 93.4 → 117.3,
mixed 108.1 → 142.2. This file refused to predict a direction, so none of that is a hit.

The arithmetic of it, which is checkable from the two tables alone: the removed events entered the
old mean at an implied mean magnitude of **66.7%** (`payment`), **62.8%** (`bill`) and **65.9%**
(mixed), against survivors at 152.5%, 117.3% and 142.2%. **A bill that fell was, on this book, a
much milder movement than a bill that rose** — so dropping the falls raises what is left. Same
mechanism as `da0431897`'s P4 at year level, now confirmed at event level.

**And the rejected argument is refuted on the record, not merely reasoned about.** The argument said
removing decreases must raise every mean *with certainty*, because a decrease is bounded at −100%.
`unknown`'s mean **FELL**, 158.1 → 142.3: its six removed events entered at an implied 171.3%, above
its own survivors. Six rows, so it proves nothing about magnitudes — but it does not need to. It
needed to be non-empty, and a single population moving the other way is enough to show the removed
set genuinely straddles, which is what the certainty argument denied. **Had that argument been
accepted this grading would have recorded a refutation.** It is the only part of this exercise that
changed what I believe.

## What this closes, and what it does not

**Closes:** the split and the sign have both reached the published surface, and the surface's labels
are now true of the quantity underneath them. `figures_on_a_superseded_clock` is discharged for this
field.

**Does not close, and neither is absorbed here:**

1. **`unknown` is 5 events with no `payment_channel`.** It was 11 and it is 5 because six of them
   were decreases, not because any were attributed. The gap is unchanged in kind.
2. **`financial.annual[].avg_bill_shock_pct` is still ONE MEAN SPANNING BOTH POPULATIONS**, on this
   same published surface, over a larger sample than the series just split — 6,094 computable bills
   against 1,748 flagged events — and with no `n` and no bound of any kind beside it. On the run
   behind the live page: `bill` n=1,696 mean 38.40%, `payment` n=4,366 mean 45.58%, `unknown` n=32
   mean 23.15%, published as a single ~43%. It carries an `avg_bill_shock_pct_population` note that
   says which *bills* it covers and is silent on which *households* — so it reads as settled while
   being the identical mixed-subject failure one level up. **That is the next item and it is filed
   with its own pre-registration.**
