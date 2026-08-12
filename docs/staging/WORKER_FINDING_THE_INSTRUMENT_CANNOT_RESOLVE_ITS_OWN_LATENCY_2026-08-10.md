# WORKER FINDING — the latency dimension reads its own grace parameter back, and calls it the company's latency

**Severity:** BLOCKING · **Lane:** H_harness

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #7 on `H27_payment_belief_gap` (2→3)
**Advances:** `D23_organ_query_grid_cannot_resolve_latency` (minted here, **not** built here)
**Verdict:** **HELD AT L2.** L3 means "this harness measures what it says it measures". A seventh
consecutive Hour found something in a published headline.
**R12:** nothing was tuned. Every published figure is bit-identical before and after this tick —
`mean_lag_days` 2.132353, `mean_lag_days_without_dd_channel` 5.0 (n=600, seed 7).

## Why this dimension, and why now

Hour #4 set the promotion criterion in advance — *two consecutive clean Hours* — and named the
`ageing` dimension as the one never given an Hour of its own. Hours #5 and #6 took it and found two
defects (`D21`, `D22`). That leaves **`detection_latency`** as the last dimension never examined on
its own terms, and it is the one carrying the most exemptions: exempt from the coverage-only
residual (a non-zero reading there is correct), and the sole `covered_by` entry in the direction
register. D21's lesson was that *the control believed the exemption* — so the dimension with the
most exemptions is where to look next.

## The finding — the counterfactual arm is a harness constant (observed, R9)

`detection_latency_gap`'s docstring states the independence claim explicitly:

> reconciliation's is the earliest date at which the company's OWN `expected_collection_misses`
> organ returns the invoice — **asked of the organ itself, never re-derived here** (R15
> independence: a harness re-implementation of `due + grace` would be a tautology that could not
> fail if the organ's rule changed).

The organ *is* asked. It is asked at exactly one date per period, and `score_triad` builds that date
itself:

```python
candidates = sorted({
    r.due_date + timedelta(days=reconciliation_grace_days) for r in periods
})
```

That is the harness re-implementation of `due + grace`, promoted from a computed value to the
**only place the question is ever put**. Independent in form; tautologous in value. A reading taken
by querying an organ on a grid of the harness's own making is quantised to that grid, and the
resolution is a property of the harness, not of the company being graded.

### Measured, not argued

Via the declared `organ_reconciliation_drift_days` counterfactual (added in this tick): the
company's own reconciliation detector fires `k` days later, the world and every truth-side rule
untouched, so all movement is the company's detector moving, by construction.

| organ drift (company only) | recon first-knowledge mean | latency headline | detection gap |
|---|---|---|---|
| **−20 d** (flags 15 days *before* due) | **5.0** | **2.132353** | **0.012100** |
| **−5 d** (flags the day it falls due) | **5.0** | **2.132353** | **0.012100** |
| −1 d | 5.0 | 2.132353 | 0.012100 |
| **0 d (as shipped)** | **5.0** | **2.132353** | **0.012100** |
| +1 d | **26.0** | 7.124088 | 0.024362 |
| +7 d | 26.0 | 7.124088 | 0.024362 |
| +21 d | 26.0 | 7.124088 | 0.024362 |

Bit-identical at seeds 7/11/23 (n=300 and n=600). Two blindnesses, in opposite directions:

**Improvement — unbounded.** `recon_lag_days` is the constant **5** for all 204 dated cases at seed
7. Zero variance. That is `reconciliation_grace_days`, a harness input parameter, echoed back. So
`mean_lag_days_without_dd_channel` — the counterfactual arm the docstring calls *"the whole point of
the dimension"*, and which its own comment insists is *"a reading rather than a constant"* — is not
a reading of the company at all, and `dd_channel_days_earlier` is that constant minus the DD lag.
A supplier that halved its reconciliation time would see this number not move. **Not one test in
the repository fires on any improvement drift.**

**Degradation — quantised to 21 days** (`PERIOD_SPACING_DAYS`). A one-day-later detector cannot fire
at its period's only candidate, so the next candidate that dates it belongs to the *next period*,
21 days on. A 1-day degradation is published as **+21.0 days**, a 21× overstatement, and +1/+7/+21
are one number. The last period has no later candidate at all, so its cases leave the population
(undated 0 → 59, n=600 seed 7).

### What fired, and what it said

A permanent source mutation of the organ (`item.days_overdue < grace_days` → `< grace_days + 1`,
restored and verified by `md5sum -c`) fires **seven** tests in the pair's suite:

```
test_detection_latency_coverage_witnesses_ride_beside_the_mean
test_detection_residual_is_misallocation_not_a_never_observed_blind_spot
test_the_miss_direction_can_still_fire
test_shared_quantity_declarations_are_measured_not_asserted[7-None]
test_shared_quantity_declarations_are_measured_not_asserted[23-12]
test_the_two_dimensions_score_the_same_cases_and_the_residual_is_belief_side
test_the_shared_quantity_control_fires_on_a_register_that_lies
```

**Not one names latency.** The dimension whose entire subject is *how late the company learns* has
no control that fires on the company learning later — the seven that fire are counting witnesses
and shared quantities, and the first of them fails on `assert c["n_recon_detected_undated"] == 0`,
a pinned generated value whose diagnostic points a reader at coverage bookkeeping. In the
improvement direction, nothing fires at all.

## What was built (HARDEN) — the class, not the instance

**`ORGAN_QUERY_GRID`** — the register, keyed on the **reading** rather than the dimension, because
the same grid feeds two of them. Each entry declares which company drifts it can and cannot see, and
the measured step. `measure_organ_query_grid_resolution` re-derives every declaration each run by
re-scoring the same population against the drifted company; `check_organ_query_grid_resolution`
returns named violations. It prints in the CLI as well as the suite, for the reason the direction
control does: the reader about to quote a latency in days is exactly the one who needs to be told
what it can resolve.

**It is differential on purpose**, and the differential is the evidence. The second entry —
`flagged_via_reconciliation`, a *set membership* off the same grid, feeding `detection` — has no
step in days to declare, but shares the improvement blindness exactly: a detector that fires
earlier still fires at the same single candidate and flags the same set. **That the date reading and
the set reading go blind together is what makes this a finding about the GRID rather than about the
latency formula.**

**`organ_reconciliation_drift_days`** — the counterfactual as a declared `score_triad`/`measure`
parameter rather than a test's `monkeypatch` (the D20 rule: a counterfactual a reader cannot find in
the repo is not part of the design). Verified to reproduce the monkeypatch measurement digit for
digit before anything was built on it.

**The caveat travels with the number** — `organ_query_grid_caveat`, `organ_query_grid_step_days` and
`organ_improvement_is_visible` are stamped **at source** in `detection_latency_gap.components`, so
they reach all three coupled pairs calling the scorer, with the step *interpolated from the
register* rather than retyped.

### R15, both ways

- **Inert probe** — a runner that ignores the drift: the vacuity guard fires and the diagnostic
  names the *probe* ("moved NOTHING anywhere in the register"), not the reading. Without it, a drift
  parameter that silently stopped drifting would hand every invisibility declaration a free pass.
- **Repaired grid** — a D23-shaped runner whose reading tracks the organ day for day: the
  `invisible_drifts` declarations fire **by name**, the violation names `D23` as the atom to
  re-derive, and the quantisation pin fires with `published as 1.0 days, not the declared 21.0`.
  This is the direction that matters: a debt entry that outlives its debt misleads worse than none
  (the D22 second rule).
- **Lying register** — an entry declaring a blindness with no `debt_atom`: unowned-hole violation.
- Plus two characterization pins that **must fail when D23 lands** and say so in their own assertion
  messages.

## Why this is a mint and not a fix on sight

Giving the grid a real resolution moves `mean_lag_days`, `mean_lag_days_without_dd_channel` and
`dd_channel_days_earlier` on **all three** coupled pairs that call this scorer, and every gap-ledger
entry written before it would become non-comparable. That is `D23`, minted at L0 with the
measurement attached. What lands today is the measurement and the honesty: the number now says in
its own components what it cannot see.

## Why H27 is still at L2

Seven Hours, seven defects, none predicted by the Hour before it. The arrival rate is not falling.
Hour #4's criterion — **two consecutive clean Hours**, stated in advance — has not been approached,
and this is again the tick that changed the instrument. Taking L3 on the reputation of a build one
tick old is the move every prior release refused.

**Where Hour #8 should start.** Three leads, in the order I would take them:

1. **The other grid readings.** `ORGAN_QUERY_GRID` has two entries because two readings come off
   `candidates`. `snapshot()` is asked at `as_of` **only** — one point, no grid — which is the same
   defect shape with the grid degenerate to a single date. Whether `ageing` and `belief` are
   as_of-quantised in the same way is a measurement nobody has taken; `DIMENSION_AS_OF_CONTRACT`
   sweeps whether the *headline moves* with `as_of`, which is a different question from whether the
   headline can *resolve the company* at a fixed `as_of`.
2. **`n_recon_detected_undated == 0` is a pinned generated value** in
   `test_detection_latency_coverage_witnesses_ride_beside_the_mean` — the shape the project has a
   standing rule against. It is the first test to fire on an organ drift and its diagnostic sends
   the reader to the wrong place.
3. **`DETECTION_LATENCY_NO_NORMALISER_REASON` is correct and now insufficient.** "An absolute mean
   in days" is true; what a reader needs beside it is the *resolution* of those days, which until
   today was 21 in one direction and infinite in the other. Whether the other dimensions' declared
   normalisation notes have the same gap between what they deny and what they establish is one
   sweep, not four readings.

## Tests

**9 new** in `tests/tools/test_couple_w2_11_d5.py` (**244 green**, was 235). **135 green** across
every sibling coupled-pair suite (`test_live_payment_triad`, `test_couple_cohort`,
`test_couple_w2_4_c6`, `test_couple_w2_5_c7`, `test_couple_fabric`, `test_couple_supply_start`,
`test_d7_ageing_measures`). Size ratchet green with the mint and the register append.
