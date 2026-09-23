**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# RESULT — the memory ceiling now prices the RUN, and the control sitting over it was asserting the conflation as correct

**Filed:** 2026-09-21. Drawn as Lane 0 delivery,
`re-rule-the-memory-ceiling-against-measured-whole-run-rss`. Pre-registration beside this:
`SEAT_PREREG_RE_RULING_THE_MEMORY_CEILING_AGAINST_THE_MEASURED_RSS_CURVE_2026-09-21.md`, written
before any edit.

**This discharges the BLOCKING clause of**
`SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_..._2026-09-21.md`. That document was BLOCKING on one
clause: `site/data/value_arms.json` publishing `memory_ceiling.max_customer_years = 38,275` and the
sentence *"Memory is not what caps this book"*. Both are gone from the feed.

---

## What landed

`premise_population.settled_book_ceiling_customer_years` no longer prices two scale-probe stage
costs times a record rate. It reads the measured whole-run RSS curve
(`docs/observability/settlement_ceiling_slope_20260921.json`) through a new
`load_whole_run_rss_curve`, and evaluates the measured LINE at a budget that is a share of the
guest's **live** `total_mb`.

| | before | after |
|---|---|---|
| what is priced | retained settlement rows | the whole process's peak RSS |
| cost per customer-year | 0.214 MB | **4.340 MB** (measured) |
| ceiling | 38,275 cy | **1,312 cy** |
| slack over the 1,200 budget | "4.5x" (hard-coded) | **1.09x** (derived) |

**The published figure is now reproducible from the artefact.** My independent re-derivation from
the report's own `points` — clean only, lowest as anchor — returns 1,312 against the probe's
separately-computed 1,312.3. Two implementations of the same bound agreeing to rounding is the
cross-check that says neither is a typo.

## The five predictions, scored

1. **≈1,312, reproducing the probe.** ✅ Exactly — 1,312 vs 1,312.3.
2. **`what_binds` stays `SETTLEMENT_CUSTOMER_YEAR_BUDGET`.** ✅ 1,200 ≤ 1,312.
3. **`no_leg_is_reachable` stays true, capacity stays 1,200.0.** ✅ Both unchanged.
4. **`test_the_customer_year_ceiling_is_the_SAME_arithmetic_re_ruled` reds.** ✅ It did.
5. **The figure becomes box-dependent.** ✅ In shape, not yet in evidence — `total_mb` is still
   24,032.1, so this regeneration produced the same 1,312 the probe did. The spread I predicted is
   unobserved and stays a prediction.

Four of five confirmed; the fifth is untested rather than supported, and is labelled so.

## THE FINDING — the control over this number was asserting the defect as correct

`test_the_customer_year_ceiling_is_the_SAME_arithmetic_re_ruled` required the customer-year ceiling
to reproduce `settled_book_ceiling` exactly at the probe's own rate — *"one sum in two units"*. It
was green throughout, it was mutation-shaped, and its docstring named a real defect ("someone
repairs the per-record cost in one of them").

**It was pinning the conflation.** The identity it enforced is the claim that a run's memory cost
IS its retained settlement rows. That is exactly false, by 19.4x on the marginal, and a control
enforcing it could only ever go red when someone fixed it — which is what it did. It made the wrong
number harder to repair than to keep.

This is the recorded shape *"repairing a conflation reds the sibling fixture that HID it"*, and the
instance is worth keeping because the fixture did not look like a fixture: it read as a
cross-check between two functions, which is normally the good kind.

**What replaced it is keyed to a property that survives any re-run**: a process cannot cost less
than one of the structures it holds, so the measured whole-run rate must EXCEED the stage-cost rate
at the same record population. No literal, no identity, and it fires on a revert to stage-cost
arithmetic.

## Also repaired, because the number moving does not move the sentences by itself

**This is the trap the pre-registration named and it is the part worth carrying forward.** The
verdict on the page — `no_leg_is_reachable: true`, `capacity_customer_years: 1200.0` — is
*identical* before and after. Every control keyed to the verdict stayed green across a 29.2x repair
to the number underneath it. Three prose surfaces derived the wrong *reason* from the right verdict
and none of them could notice:

1. `settled_book_ceiling_customer_years`'s `what_it_does_not_bound` — pinned "1,200", "slack by
   4.5x" and "Memory is not what caps this book" inside the function computing the number those
   claims describe. **Deleted.** What remains is the part that is a property of an RSS bound rather
   than of today's box: it does not bound wall clock, priced from the same curve.
2. `_can_this_book_be_built`'s docstring — *"AND ON THAT RULER MEMORY IS NOT WHAT BINDS"*.
   **Corrected in place, with what it used to say kept beside it.**
3. `_what_is_not_established`'s negative branch — *"Memory is not the constraint ... so the open
   question is a DIRECTION one and not a measurement"*. **Now computed** from a new derived key,
   `memory_slack_multiple_over_the_budget`, with three branches (tighter than the budget / nearly
   binds / has room). If the ceiling crosses the budget the sentence follows without an edit.

A new control, `test_the_ceiling_carries_no_claim_pinned_to_todays_answer`, fires on any of the
three literals returning to the function's output — and on an absolute path reaching the feed,
which my first draft of this repair did and which would have published the worktree it ran in.

## Two things I got wrong inside this turn, kept because they are the same class as the defect

1. My first draft published `curve` as an **absolute path**, which names whichever worktree the
   generator ran in — a pointer no reader can follow and a leak. Caught by looking at the output,
   not by a test; a test now exists.
2. My first `what_it_does_not_bound` computed the wall-clock cost as `seconds_per_customer_year ×
   book` — the **bare marginal, unanchored**, which understates the run by its entire fixed cost
   (2,570s against the line's 1,725s). That is precisely the error the function was re-ruled to
   stop making, committed one key below the docstring warning about it. Both are fixed; the second
   is a reminder that knowing the shape of an error does not stop you repeating it in the adjacent
   quantity.

## What is NOT closed

* **The curve has two clean points, not four.** The middle two are contaminated on the x-axis. The
  loader refuses below two rather than falling back, but a two-point line over 1,197–3,135 cy is
  an extrapolation and the return says so (`bound_kind: measured_two_point_extrapolation`, no
  `upper_bound` label). It is not a conservative bound and must not be read as one.
* **The repeat of the 1,200 point** that separates "fixed cost regressed ~900s" from "the box was
  contended" is still owed, from the parent finding. Unchanged by this.
* `site/data/delivery.json` still narrates 38,275 as live. That is a dated stretch record and was
  true when written; it is another lane's generated feed and I have not touched it.
* `simulation/net_new_acquisition.py`'s note already carries the corrected reading (1,312.3, 4.340
  MB/cy, 1.09x, **not moved**) from the lane that landed the curve. My repair agrees with it. Its
  headline *"IT IS WHAT BINDS"* is loose — at 1,200 the budget binds, 8.6% below the memory bound —
  but its own clause 3 states that precisely, so I have left another lane's landed text alone.
