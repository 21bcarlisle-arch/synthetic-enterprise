**Severity:** LATENT · **Lane:** H_harness

> **PARKED IN `in_progress/` 2026-08-26 — DIAGNOSED AND FIXED; ONE SUB-ITEM STILL OPEN.**
>
> **The condition is answered.** The arm's answers came from a bound because
> `renewal_margin_uplift` — its only production caller — passed six of `decide_margin`'s twenty
> company observables and let the rest default. Two defaults did it: the billed `revenue_gbp`
> includes the standing charge, so the "current rate" was an ALL-IN £/MWh compared against a
> commodity-only offer (£55/MWh of phantom headroom on a small domestic account); and no ceiling
> reached the search, so the cap landed afterwards as chain writer 4 and `ceiling_bound` was
> structurally unable to fire. Fix landed `8b450a839`, mechanism recorded `2293612ba`
> (`docs/design/THE_VALUE_CYCLE_REALISED_AB.md`). Measured on a real account shape: chosen margin
> £193.00 → £60.00/MWh. Six R15 controls, four mutation-proven to red on the pre-fix mechanism.
>
> **STILL OPEN:** the confirming re-run of `tools/run_value_cycle_ab` — two full ten-year runs,
> started 2026-08-26, writing to `docs/observability/value_cycle_ab_2026-08-26_observables_threaded.json`
> **beside** the old artefact rather than over it.
>
> **What unblocks archiving this:** that artefact existing, and its `decision_shape` read against
> the pre-fix figures (`priced` 66, `endpoint_bound` 36, `clamped_by_the_price_cap` 27, median
> chosen margin £100.50/MWh). `clamped_by_the_price_cap` is now a CONTROL and must read **0** for
> every priced renewal — the arm searches under the same ceiling writer 4 applies, so a priced
> renewal it still clamped means the two reads have come apart. Then
> `python3 -m background.delivery_lane --release value-arm-answers-a-bound` and archive to
> `docs/staging/done/`.
>
> **Do not re-diagnose this.** If the re-run died, re-run it; the mechanism is settled.

# [SEAT] value-arm-chooses-a-bound-not-a-customer was claimed and has not moved for 2.0h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] value-arm-chooses-a-bound-not-a-customer was claimed and has not moved for 2.0h
Nothing has landed in the tree since it was claimed. The claim is released and the work is drawable by any lane.
What the seat said it was doing: In `company/pricing/value_based_renewal.py`, diagnose why expected value rises monotonically in margin across the whole region the churn model supports, so the "choice" is whichever bound binds first
```

## What is known without diagnosing anything

- Signature: `seat-claim:value-arm-chooses-a-bound-not-a-customer` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-25T21:30:15+00:00
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
