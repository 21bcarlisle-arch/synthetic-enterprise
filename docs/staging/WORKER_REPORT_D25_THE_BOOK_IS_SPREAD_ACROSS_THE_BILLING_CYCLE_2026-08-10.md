# WORKER REPORT — D25: the book is spread across the billing cycle

**Date:** 2026-08-10 · **Atom:** `D25_ageing_resolution_is_the_harness_calendar` **L0 → L2**
**Closes:** the reshape `WORKER_FINDING_THE_AGEING_RESOLUTION_IS_THE_HARNESS_CALENDAR_2026-08-10.md` minted
**Mints:** `D26_detection_grace_line_has_no_book_beside_it` (L0, idle) — the residual, spun out not fixed on sight
**R12:** every published ageing figure on this pair MOVED, and not one of them was chosen. The spread was fixed
at the cycle length — the only non-arbitrary choice — before any post-reshape figure was read.

## What was wrong

The W2_11↔D5 triad's AGEING dimension publishes **buckets of ordinal displacement**, so it can only see a
company dating error where that error carries an invoice **across** a 30/60/90 boundary. Every account in the
book fell due on the **same three dates**, so every truly-overdue invoice sat at 30, 51 or 72 days overdue at
`as_of` — three distances, all arithmetic over `FIRST_DUE_DATE`, `PERIOD_SPACING_DAYS`, `N_PERIODS` and
`AS_OF_BUFFER_DAYS`. The smallest company error the headline could resolve was therefore a property of the
**harness's calendar**, not of the company being graded: 8 days of over-ageing (the direction that posts an
early dunning letter) were bit-identical to perfect dating, and companies +1d and +12d out published one number.

## The change — one change, and it is the real-world twin

`build_scenario` now draws a per-account **billing-cycle offset** (`_billing_cycle_offset`, its own named
sha256 substream, C-S2) so the book is spread over `BILLING_CYCLE_SPREAD_DAYS = PERIOD_SPACING_DAYS` — the
cycle length itself. A domestic supplier bills a cohort of accounts a day; it does not put the whole book on
one date. The fidelity fix and the resolution fix are the same change.

The book now spans a **contiguous 30..92 days** overdue at `as_of` (63 distinct ages at n=600, 3 before).
`as_of` is taken from the latest due date the **cycle** can produce, not the latest this **draw** produced, so
`AS_OF_BUFFER_DAYS` keeps its stated job ("every account's newest invoice is at least this far past due") at
every population size and the reading cannot depend on how many customers were sampled.

## Measured — the four drifts that named the atom

Same declared `organ_terms_drift_days` counterfactual company (world and truth-side bucket rule untouched),
n=300, seeds 7/11/23, and the same sweep the finding used:

| drift | flat book (before) | staggered book (after) |
|---|---|---|
| −8 d (over-ages by a working week) | **bit-identical to baseline** | **moves, every seed** |
| −1 d | bit-identical to baseline | moves, every seed |
| +1 d | moves | moves |
| +12 d | **same number as +1 d** | **distinct from +1 d** |

`DIMENSION_DRIFT_RESOLUTION["ageing"]` is re-derived: `invisible_drifts: ()`, `collapsed_pairs: ()`,
`debt_atom: None`. The four drifts stay declared as `visible_drifts` rather than dropped once fixed — a future
flattening of the book then fails **by name** instead of quietly narrowing the caveat.

Seed 7, n=300 ageing headline: **0.078649 → 0.112963**. Diagnostic, never a target (R12).

## The new control, and why it is not the sweep again

The drift sweep answers *"did drift k move the reading"* by re-scoring, and can only report on drifts somebody
declared. `measure_ageing_resolution` **predicts the same quantity from the population and the truth-side
bucket rule alone** — no scorer, no consumer, no organ — as the minimum distance from any invoice to the next
bucket boundary in each direction. Boundaries are **derived by walking `truth_side_rule("ageing")`**;
hand-listing 30/60/90 would be the D21 tautology in miniature.

It reproduces the flat book's measured asymmetry **exactly** — 9 days over-ageing, 1 day under-ageing, an
accident nobody designed — so `check_ageing_resolution` can put two independent computations of one quantity
against each other: every declared drift at least as large as the prediction must have MOVED, every smaller
one must not have.

### R15, both ways

- The **flat book is REFUSED by name** in the over-ageing direction. It is kept reachable as a *declared*
  parameter — `build_scenario(cycle_spread_days=1)` — not a test monkeypatch (the D20 rule).
- A **lying prediction** (resolution overstated to 20d) is caught by the sweep's own readings.
- An **empty book** and a book with **no boundary beside it** are VIOLATIONS, not the fail-open `None`
  R15 names third.
- The register's mutation suite gains **the post-D25 rot** (an entry claiming the headline still cannot see a
  drift it now sees — a debt entry outliving its debt) and **the all-SIGHTED register**, the mirror of the
  all-blind one and only reachable now that a second entry is sighted.
- **C-S2 proven:** every customer's stress tier, payment method and outcome are bit-identical between the flat
  and staggered books — the offset draws from its own substream, so this changed *when* the book is billed and
  nothing else.

## The caveat now describes the book the figure came from

`score_triad` also scores **live** run_phase2b populations whose calendar no sweep has ever visited, and until
this atom those readings carried a caveat written about the offline scenario's three due dates. The resolution
is now measured per-book and stamped into the ageing `note` **and** `components`
(`ageing_resolution_days`, `ageing_resolution_book`), and printed in the CLI beside the flat book — read back
**off the published components**, so a stamping that silently stopped cannot be papered over by the printer
recomputing it.

## What was NOT done, and why

The **DETECTION** dimension is still blind at +1d, and it must be: its blindness is the reconciliation
**grace line**, not the bucket grid — the youngest invoice in the book is 30 days overdue and the grace window
is far shorter, so nothing sits *beside* the line that detector reads. Same class as the defect D25 closed,
one boundary further out. Its register entry named D25 as owner; a debt entry outliving its debt is exactly the
rot this register's mutations fire on, so it is **re-pointed at newly-minted `D26`** (L0, idle) rather than
fixed on sight (self-interrupt discipline: the supply of findings is infinite).

## Evidence

- `tools/couple_w2_11_d5.py` — `BILLING_CYCLE_SPREAD_DAYS`, `_billing_cycle_offset`,
  `build_scenario(cycle_spread_days=…)`, `ageing_bucket_boundaries`, `measure_ageing_resolution`,
  `check_ageing_resolution`, the re-derived register entries, the per-book caveat, the CLI block.
- `tests/tools/test_couple_w2_11_d5.py` — **284 green** (was 271).
- **177 green** across the sibling coupled-pair suites (`test_couple_cohort`, `test_couple_fabric`,
  `test_couple_supply_start`, `test_couple_w2_4_c6`, `test_couple_w2_5_c7`, `test_d6_ageing_metric_shape`,
  `test_d7_ageing_measures`, `test_generate_proof_coupled_gaps`, `test_live_payment_triad`,
  `test_gap_ledger_reconciler`).
- `python3 -m tools.epistemic_wall` exit 0 · `python3 -m tools.level_promotion_gate` exit 0.
- Level move recorded self-certified in `docs/observability/gate_authorizations.jsonl` (R16).
