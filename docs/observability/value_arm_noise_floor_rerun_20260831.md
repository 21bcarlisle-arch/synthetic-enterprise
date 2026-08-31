# The bound that decides "cannot resolve" was from another world — re-measured, and it WIDENED

**2026-08-31, delivery seat.** The spread first, the verdict second. That order is the point: a
bound read after its verdict is chosen is not a bound.

## The two runs, and the check that they are one world

| | error bar (noise floor, `all`) | point estimate (three-arm) |
|---|---|---|
| finished | 2026-08-31T07:05:53Z | 2026-08-31T03:47:57Z |
| producing commit | `4240e1478` | `fe4df178b` |
| price level | £52.50–£53.25/MWh | £54.25/MWh |
| accounts re-drawn | 68–69 | — |

`fe4df178b` is an ancestor of `4240e1478`. **55 paths differ between the two trees and 0 of them
are paths a run can read** (`_INERT_TO_A_RUN`: observability, reports, status, staging, state,
tests, and the composer itself). So `_staleness_caveat` clears — *derived from the two commits, not
asserted here*. The caveat it replaces named the real defect: the previous floor was measured
2026-08-29T17:04:23Z, before the market could defend against a company that undercuts it, and it
carried no `producing_commit` at all.

## The spread, before any verdict is restated

| | old floor (08-29) | new floor (08-31) |
|---|---|---|
| `selection_gbp` σ | £2,577.80 | **£3,776.27** |
| band (min, max) | −£4,273.97, +£872.96 | **−£4,094.21, +£3,453.76** |
| mean | −£1,614.30 | −£396.05 |
| SEM | £1,488.29 | £2,180.23 |
| seeds / passes | 3 / 9 | 3 / 9 |

**The bound widened by 46%.**

### One reading to refuse before it is made

`elasticity_draws` falls 2,020 → 377. That is **not** a collapse in sample size and must not be
read as one: `price_elasticity_for_customer` is a pure function of `(customer_id, seed)`, so that
field counts **call sites** — re-reads of the same draws — and is, in this project's own words
from the 08-29 decomposition, "a sample size for nothing at all". The independent unit is
`accounts_redrawn` = **68–69**. The old artefact predates that field and does not record it, so the
two runs' independent sample sizes **cannot be compared**. I cannot say the instrument got weaker
and I am not saying it.

## The verdict, re-derived

**Selection leg — the per-customer claim. The refusal SURVIVES.**
£2,574.37 against ±£3,776.27, ratio **1.47**. The point estimate now sits *inside* the measured
band and so does zero, so the page still says **CANNOT RESOLVE**, in either direction.

This is a better refusal than the one it replaces, and in a way that matters: against the old floor
the point estimate sat **outside** the band (−£4,274…+£873), so that spread was not a bound on this
figure at all — the page was refusing for a reason that was itself unmeasured. It now refuses
against a bound measured in the same world. **The refusal is evidence.**

**Headline leg — a direction, for the first time.**
£12,071.08 against its own ±£2,291.07 → the arm-vs-control contrast clears its floor, and the page
states the direction it came out: the per-customer engine earned £12,071 MORE than flat rules. That
sentence has been gated on this bound since it was written; the gate is not new, only reachable.

## The movement is UNATTRIBUTABLE, and it flatters us in one leg

At least four things moved between the two floors: the competitor gained the ability to defend;
C1a/C1b's standard-variable product took the priced count from 20 of 1,369 to **120 of 1,953**; the
realised price level fell ~£60 → ~£53/MWh; the departure-level anchor landed. **More than one thing
changed, so I cannot attribute either the widening or the newly-stateable direction to any of
them.** Prediction 4 of `WORKER_PREREGISTRATION_WHAT_THE_RERUN_ARMS_MUST_SHOW_ABOUT_THE_PRICED_COUNT`
recorded exactly this in advance — *"an improvement is as suspect as a loss here"* — and it is
recorded as **HELD**, which is the only reason the £12,071 direction is publishable without a claim
about why.

## What a larger settled book would and would not buy down at 120 — NOT ANSWERED HERE

The priced side carried **0.9999** of the variance at 20 priced. Whether it still does at 120 is
the question the `only`/`except` legs answer and **they are still running** (launched with the
`all` leg; `only` in flight at the time of writing, `except` queued). Until `--decompose` runs on
them, `floor_decomposition` remains the 08-29 split — 20 priced of 1,369 — and the page **refuses
to quote any remedy from it**, because the remedy is denominated in the priced count and that count
has moved. That refusal is correct and is the state this note leaves the page in. It is **owed
work, not a finding**.

## A control that could not fire until today

Repairing the bound made `contrast_bounds` available for the first time, and that exposed a
**scope-wider-than-its-claim** defect in `test_the_page_names_a_winner_only_where_the_contrast_cleared_its_floor`:
four directional phrases were checked as one flat tuple against the **selection** leg's spread
alone, but two of them name the **arm-vs-control** contrast. The composer has always gated each
against its own spread (`_BOUNDED_CONTRASTS`). The control could not fire before: while
`contrast_bounds` was unavailable both groups were suppressed together, and on the 08-29 run both
contrasts were unresolvable at once (£607 vs ±£990; £1,816 vs ±£2,578), so the OR never diverged
from the AND. Today they disagree for the first time, and the flat tuple made the page's *correct*
refusal on the selection leg veto its *earned* direction on the headline leg.

Split by subject, plus the rung the ladder was missing — a decomposition measured on another book
is refused *with its reason on the surface*, not silently. Mutation-proven in memory against 8
cases (both contrasts, both directions, both new rungs); all 8 behaved as required.

**The honest caution on that repair:** the failing assertion was blocking a claim that flatters us,
and I changed the test rather than the page. What makes that defensible is that the composer's
per-contrast gating predates today and was never in question, the control's own comment says "the
contrast cleared its **own** floor", and the repair reds in *both* directions — a page that goes
back to asserting and a page that goes on refusing both fail it now.
