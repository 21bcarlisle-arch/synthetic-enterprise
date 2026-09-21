**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — what I expect the re-ruled memory ceiling to do, written before I ran it

**Filed:** 2026-09-21, before any edit to `simulation/premise_population.py`. Drawn as Lane 0
delivery, `re-rule-the-memory-ceiling-against-measured-whole-run-rss`. The result document that
scores these is beside this one.

The measurement is already taken — `docs/observability/settlement_ceiling_slope_20260921.json` —
so the thing I am predicting is **what happens to the code and the page when the measured curve
replaces the stage-cost arithmetic**, not what the world does. That is a prediction about an
instrument, and it is worth filing precisely because the last one filed about this subject was
wrong on every clause.

## What I am about to change

`premise_population.settled_book_ceiling_customer_years` currently prices two stage costs from an
old scale probe (`settlement_build` + `run_output_serialization`) times a records-per-customer-year
rate. It therefore prices **the retained settlement rows and nothing else the run holds**, and
publishes 0.224 MB/cy against a measured whole-run 4.340. I am replacing the arithmetic with the
measured curve, read from the probe artefact rather than written down.

## Predictions

1. **The re-ruled ceiling lands at ≈1,312 customer-years**, and my independent re-derivation from
   the artefact's `points` (clean only) plus its recorded guest share will reproduce
   `recommendation.bounds.memory.customer_years = 1312.3` to within rounding. If it does not, one
   of the two arithmetics is wrong and I must find out which before landing.
2. **`what_binds` STAYS `SETTLEMENT_CUSTOMER_YEAR_BUDGET`.** 1,200 ≤ ~1,312, so the budget still
   binds — but by 1.09x, not the 4.5x the deleted string claimed. The page's *verdict* does not
   move; only its *reason* does.
3. **`no_leg_is_reachable` stays `true`** and `capacity_customer_years` stays 1,200.0. The
   headline answer on the page is unchanged. **This is the trap in this item**: the number that
   moves is inside `memory_ceiling`, and every gate keyed to the verdict will stay green while the
   sentence that was wrong is still wrong. The controls I write must be keyed to the *reason*.
4. **`test_the_customer_year_ceiling_is_the_SAME_arithmetic_re_ruled` will RED**, and it should.
   It pins the customer-year ceiling to be the same sum as `settled_book_ceiling` in another unit.
   That identity is exactly what this repair breaks — the stage costs price one data structure,
   not the run. It is the sibling fixture that was asserting the conflation as correct.
5. **The published figure becomes box-dependent and will no longer be stable across
   regenerations**, because the budget is a share of the guest's live `total_mb` rather than a
   quoted number. I predict a spread of a few percent between regenerations on a quiet box, and
   more under memory pressure. Anything keyed to the literal will red; that is the correct
   direction and I would rather have it than a quoted memory figure.

## What would refute the whole approach

If the re-derived slope from the clean points disagrees with the artefact's own `marginal`, or if
there are fewer than two clean points, the function must **refuse with a named reason** rather than
fall back to the stage costs. A fallback here would restore the optimistic number under a new name,
which is the worse of the two failures.
