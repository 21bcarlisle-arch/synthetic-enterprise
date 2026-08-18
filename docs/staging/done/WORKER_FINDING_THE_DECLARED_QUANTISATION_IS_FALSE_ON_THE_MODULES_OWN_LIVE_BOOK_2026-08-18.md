# WORKER FINDING — the register's declared quantisation is an unscoped literal, and it is false on a book this module itself builds

**Severity:** BLOCKING · **Lane:** D_billing_metering

**Discharged:** `tests/tools/test_couple_w2_11_d5.py::test_the_predicted_runs_are_the_shipped_sweeps_runs`, `tests/tools/test_couple_w2_11_d5.py::test_the_published_runs_are_this_books_and_not_the_registers_literal`, `tests/tools/test_couple_w2_11_d5.py::test_the_run_at_the_origin_is_the_one_a_reader_is_standing_in`, `tests/tools/test_couple_w2_11_d5.py::test_the_stress_axis_null_control_reproduces_the_declaration`, `tests/tools/test_couple_w2_11_d5.py::test_every_pinned_stress_tier_falsifies_the_declaration`, `tests/tools/test_couple_w2_11_d5.py::test_the_stress_axis_control_fires_on_its_own_named_defects`, `tests/tools/test_couple_w2_11_d5.py::test_the_stress_axis_control_fires_on_a_bad_measurement`, `tests/tools/test_couple_w2_11_d5.py::test_pinning_the_axis_to_one_stress_tier_hides_the_defect`, `tests/tools/test_couple_w2_11_d5.py::test_the_collapsed_runs_derivation_is_the_gaps_in_the_threshold_multiset`, `tools/couple_w2_11_d5.py` — landed 2026-08-18 by the RUNG-1c blocking draw, taking recommendation 1 then 2 as recommended. The runs are derived per run from the book actually scored and stamped beside the band; the register keeps its literal WITH the stress mix it was measured on; and the axis the draw-size sweep is invariant along is swept over 12 books with no scorer call. Evidence and the corrections below: section 8 of the design doc named under Raised.

**What the fix found that the finding did not, and it changes the control:** the finding's own headline — the run at the origin measuring 7 days against a declared 2 — is a JOIN, not a split, so the obvious predicate (is a declared run broken up here) reads the very book that produced the finding as AGREEING, and scored it 1 of 7 rather than 6 of 7. Exactness had to be enforced in both directions. Second, comparing run TUPLES makes the null control red for a reason unrelated to the stress mix, because the register's first run is non-contiguous (a declared pair member unioned in from outside the book's range); the comparison is over boundaries instead. With both corrected, ALL THREE pinned tiers falsify the declaration and the null control is exactly green — stronger than the finding claimed, which asserted only the all-high book.

**Still owed, flagged rather than left implied:** `docs/observability/coupled_gap_ledger.json` carries no run list for this atom until a run rewrites it, for the same reason its sibling gave — that entry is written as a side effect of run_phase2b, not by a write-ledger invocation, so no honest single command in this tick refreshes it.

**Raised:** 2026-08-18, worker tick, D28 DISCOVER pass 6 (LANE 3 idle draw). Derivation and
full evidence: `docs/design/D28_DETECTION_EXIT_THRESHOLD_PREDICTOR.md` §7.
**Owner:** `tools/couple_w2_11_d5.py` — the `file_scope` of `H27_payment_belief_gap`
(`loop_stage: harden`) as well as of D28/D31, so this is drawable now.
**Intended rank (P-1):** top of `D_billing_metering`, directly beneath the finding it is the
unfixed half of.
**QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE).

## What was observed

`ORGAN_QUERY_GRID["flagged_via_reconciliation"]` publishes three claims about where the
detection reading stops resolving: the two saturation edges, and `collapsed_runs` — sixteen
groups of counterfactual companies declared to publish one bit-identical figure. On
2026-08-18 the RUNG-1c blocking draw gave the edges everything an unscoped literal needs:
`saturates_above_scope`, a `draw_size_axis` over 25 books, a population sweep
(`measure_recon_band_population_axis`), a control that puts the declaration on trial
(`check_recon_band_population_axis`), and a per-run derivation so the published component is
the scored book's own band rather than the register's number.

`collapsed_runs` sits in the same dict literal and received none of the five. It carries no
scope, no population axis, no per-run derivation, and `check_recon_band_population_axis` does
not read it — that control trials `lower_edge_invariant`, `upper_spread_by_seed`,
`upper_edge_range` and `saturates_above_scope`, and nothing else. The only thing that ever
checks the runs is `_check_saturation_and_collapse`, against a sweep of `build_scenario` at
n=300, seeds 7/11/23 — the population the declaration was authored on.

**And it is the runs, not the edges, that the published sentence sends the reader to.**
`organ_query_grid_saturation_caveat` is stamped into `det.note` AND
`det.components["recon_saturation_caveat"]`, and it ends: *"Between them it is quantised, not
continuous: movement in these headlines is not readable as days of company error outside the
declared runs."* The edges now travel with their scope. The runs the sentence defers to do
not.

## The counterexample is this module's own harness

`_publish_one_book` (`tools/couple_w2_11_d5.py:7091`) is this module's own harness for the
shipped live composer — it drives `LivePaymentTriad.measure_and_write` and reads back what it
published. It builds 300 customers × 3 monthly periods with `income_stress_value="high"` for
every one of them (`tools/couple_w2_11_d5.py:7110`), and it is not alone: those two words
appear exactly twice in the repo, there and at
`tests/background/test_live_payment_triad.py:46`. **Every book built for a `LivePaymentTriad`
anywhere outside `run_phase2b` pins every customer to the same stress tier.** Swept through the
shipped `score_triad`
over `k` in [−10, +40] (51 counterfactual companies, one integer per day):

| | declared | measured on `_publish_one_book`'s book |
|---|---|---|
| runs inside [−10, +40] | 7 | 9 |
| declared runs the sweep reads APART | — | **6 of 7** |
| collapses the register does not name | — | **8** |
| the run containing `k = 0` | `(0, 1)` — 2 days | `(−5 … +1)` — **7 days** |
| widest undeclared collapse | — | `(26 … 40)` — 15 days |

`(17…24)`, declared as one eight-day collapse, splits into `(17…21)`, `(22, 23)`, `(24, 25)`.
`(−4, −3)`, `(0, 1)`, `(6, 7)`, `(11, 12, 13)` and `(28, 29)` are all read apart.

**Mechanism, and it is already in the tree.** `days_late` on that book takes no value below
30 — every customer is high-stress, so nobody pays mildly late. The predictor landed on
2026-08-18 gives `k*(c) = min(as_of − due, cover − due − 1) − grace + 1`, which on a negative
is `days_late − grace`; the reading changes between `k` and `k+1` iff some scored movable case
has `k* = k+1`. So the collapsed runs ARE the gaps in the book's `k*` multiset, and a book
with a hole in `days_late` has a hole in its resolution.

## The null control, which must stay green or the above is reading noise

Two ways of moving the sample without moving the law, both run this tick:

* **The register's own book.** `build_scenario(300, seed=7)`, same sweep, same range: 24
  distinct readings, and `(−4, −3)`, `(0, 1)`, `(28, 29)` reproduce exactly. The run
  containing `k = 0` is `(0, 1)`, as declared. (Seed 7 alone reads several declared runs
  joined — consistent with the declaration being the intersection over seeds 7/11/23, not a
  disagreement with it.)
* **The producer is NOT the variable.** The live producer with the offline book's own
  `_STRESS_MIX` drawn per customer, 300 × 3, due dates staggered over 21 days: 16 distinct
  readings and the run containing `k = 0` is `(0, +1)` — the declaration holds across a change
  of producer. It is the stress mix that breaks it, not `LivePaymentTriad`.

Also measured and discarded as explanations: denominator size (the run at the origin is
invariant at 120 / 360 / 720 cases), book length (invariant at 3 and 18 monthly periods), and
due-date spread (1 / 7 / 21 days moves total resolution 5 → 9 → 10 readings and does not move
the run at the origin).

## What is NOT established (R9)

Whether `docs/observability/coupled_gap_ledger.json` currently carries a caveat whose declared
runs are false **is `inferred`, not observed.** That entry is written by `run_phase2b` from a
book with real per-customer stress values, and with a real mix the declaration reproduces. No
honest single command in this tick sweeps the real run's book. The defect filed here is that
the declaration is unscoped and uncontrolled across populations — demonstrated false on a book
this module builds — not that the live artefact is wrong today.

## Recommendation, and what I would do

1. **Derive `collapsed_runs` per run, as `recon_saturation_band_days` now is.** The predictor
   already computes it: the runs are the gaps in the scored movable `k*` multiset, with no
   `score_triad` call. Measured this tick, it reproduces the swept run structure EXACTLY on
   both books — `_publish_one_book`'s and `build_scenario(300, seed=7)` — at 0.02 s against
   the sweep's ~17 s, about 950×. The published caveat would then defer to the scored book's
   own runs instead of the register's.
2. **Give the register's literal the scope its siblings got**, and extend
   `check_recon_band_population_axis` to trial `collapsed_runs` on a population axis that
   varies the stress mix, not only the draw size — the axis built on 2026-08-18 varies
   `n_customers` and seeds, which is exactly the axis this defect is invariant along.
3. Do nothing. Rejected: the sentence that ships tells a reader the reading is readable in
   days outside sixteen named runs, and there is a book in this file for which that is false
   in six of the seven places the sweep can check.

**Recommended: 1, then 2.** 1 removes the class (a published sentence moves when its subject
moves — the D19/D20/D22/D23/D25 rule this entry's edges were brought under and its interior
was not); 2 keeps the register honest as a declaration under trial rather than deleting it.
1 is cheap and already proven; 2 is where the R15 mutation work goes.

## Reversal

Nothing was changed. This document, `docs/design/D28_DETECTION_EXIT_THRESHOLD_PREDICTOR.md`
§7 and note 7 of the atom's store record are the whole output; no code in `file_scope` was
touched and no level moved.
