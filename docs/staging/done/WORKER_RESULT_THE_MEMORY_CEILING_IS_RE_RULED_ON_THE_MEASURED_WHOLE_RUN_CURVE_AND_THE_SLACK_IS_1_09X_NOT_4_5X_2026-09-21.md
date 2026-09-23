**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none (LANE 0
DELIVERY, direction not an atom) · **Class:** figures_on_a_superseded_clock

**Knowledge:** consumed `docs/observability/settlement_ceiling_slope_20260921.json` (landed at
`c4bee75e3`). No number was invented; the one judgement call is named in §4.

# The memory ceiling is re-ruled on the measured whole-run curve, and the slack is 1.09x not 4.5x

**Drawn as LANE 0 DELIVERY, 2026-09-21.** Discharges clause 3 of the BLOCKING finding
`SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_..._2026-09-21.md`.

---

## What was wrong

`premise_population.settled_book_ceiling_customer_years` priced the settled book's memory ceiling
from **two scale-probe stage costs** — `settlement_build` plus `run_output_serialization` — times a
records-per-customer-year rate. Every part of that was defensible except its **subject**. It priced
the retained settlement rows and nothing else the run holds, so it answered *"how much memory do
the settlement records cost"* and was published as *"how big a book can this box settle"*.

The 2026-09-21 repair at `c58350e2e` had already fixed a 59.7x error in the **pessimistic**
direction (re-ruling the record population from the half-hourly I&C rate to the folded daily rows).
It left an error of similar size in the **optimistic** one, because the thing being priced was
never the run's footprint.

## The measurement, and the arithmetic it replaces

Four points on the live path (`tools.run_annual_report._run_and_extract`, full window — the same
call `background/sim_runner.py` makes), two of them clean:

| committed customer-years | peak RSS (MB) | clean |
|---|---|---|
| 1,197.0 | 5,507.4 | yes |
| 1,995.2 | 8,504.7 | no — another process rewrote the campaign record mid-run |
| 2,799.3 | 12,501.8 | no — same |
| 3,135.5 | 13,920.9 | yes |

Marginal cost between the two clean points: **4.3402 MB per customer-year**, against the **0.224
MB/cy** the stage-cost sum implied. A factor of **19**, optimistic.

| | published until today | re-ruled |
|---|---|---|
| memory ceiling | 38,275 cy | **1,312 cy** |
| slack over `SETTLEMENT_CUSTOMER_YEAR_BUDGET` (1,200) | "4.5x" | **1.09x** |
| overstatement | — | **29.2x** |

## What landed

**`simulation/premise_population.py`.** `load_settlement_ceiling_slope()` and
`measured_whole_run_rss_curve()` read the probe's own artefact and refuse at every step the probe
itself refuses at. `settled_book_ceiling_customer_years` now reads that curve; the stage-price
arithmetic is **deleted, not kept as a fallback** — falling back would restore exactly the number
this repair removes, silently, on any box where the curve had not been run.

Three things in the return changed shape rather than value:

* The line is **anchored, not proportional**. The run's fixed cost is large, so `peak_rss /
  customer_years` charges the fixed part to the variable one. The ceiling is read off
  `anchor_cy + (budget - anchor_rss) / slope`. A proportional reading of the same curve gives
  1,384; the anchored one gives 1,312, and the difference is the 312 MB the run costs before it
  settles anything.
* `bound_kind` is no longer the unconditional `"upper_bound"`. It grades **itself**:
  `measured_interpolation` when the answer falls inside the span the probe stood on,
  `measured_extrapolation` otherwise. Today's answer is an interpolation — 1,312 sits between 1,197
  and 3,135, so the probe measured both sides of it. That is a stronger claim than the old label
  and it is keyed to where the answer lands, so it re-grades when the budget or the curve moves.
* The hard-coded `what_it_does_not_bound` string is gone. It pinned `'1,200'`, `'slack by 4.5x'`
  and `'Memory is not what caps this book'` — all three now refuted — **inside the function that
  computes the number they describe**. The replacement names no live figure; the three literals
  appear only as a record of what was deleted.

**`tools/generate_value_arms_data.py`.** The caller drops its `records_per_customer_year` argument.
`_what_is_not_established` no longer asserts *"memory is not the constraint"*; it prints the
measured MB/cy, the ceiling, and the ratio, and says the open question now has two halves.

**`site/data/value_arms.json`** regenerated. The page no longer publishes 38,275 anywhere.

## The one judgement call, named

**Which budget the ceiling is read against.** The old default was the scale probe's box budget
(`report["box"]["budgets"]["rss_bytes"]`, 8,186 MB) — chosen on 2026-08-12 for a probe *process*.
The subject here is a whole run that has to fit beside the daemons, so the budget is now the
probe's own `bounds.memory`: **25% of total guest memory**, 6,008 MB, read from the artefact rather
than restated. That share is the probe's documented choice, with its reason on the artefact ("share
is of TOTAL, not AVAILABLE: sizing to a momentary `available_mb` sets a ceiling that was true for
one second").

It matters, and the sweep is why it is stated rather than buried: 15% → 758 cy, 20% → 1,035, **25%
→ 1,312**, 33% → 1,755, 50% → 2,696. Two of those are below the budget that binds. **Nobody has
defended 0.25**, and that is now the load-bearing unestablished number in this chain.

## What the repair does NOT move, which is why it went unnoticed for so long

`what_binds` is still `SETTLEMENT_CUSTOMER_YEAR_BUDGET` — 1,200 is still the smaller of the two —
so `capacity_customer_years` and **every multiple derived from it are unchanged**. The wrong number
never reached the arithmetic. It only reached the prose, and the prose is what licensed *"memory is
not the constraint"*. A figure can be 29.2x wrong, published, and invisible to every consumer of
the block it sits in, because the block's consumers took the `min` and the other side won.

## Controls, and the one that could not fail

Four controls in `tests/simulation/test_premise_population.py`, three of them mutation-proven
against their own legs (tree hash verified restored after the sweep):

| mutation | verdict |
|---|---|
| restore a stage-price fallback when the curve is missing | KILLED by `test_a_missing_curve_REFUSES_rather_than_falling_back_to_stage_prices` |
| drop the anchor — read the curve proportionally | KILLED by `test_the_customer_year_ceiling_moves_with_the_MEASURED_curve` |
| pin `bound_kind` to the flattering word | KILLED by `test_the_ceiling_grades_ITSELF_interpolation_or_extrapolation` |

**The first control was written wrong and the mutation proved it.** The first draft monkeypatched
`load_scale_probe_report` to raise and asserted the ceiling did not move. It passed under the
fallback mutation — because the fallback branch is only reachable when the CURVE is missing, and
the test never made it missing. The control was asserting something true for a reason that had
nothing to do with the defect. The repair points `SETTLEMENT_CEILING_SLOPE_DIR` at an empty
directory so the artefact is **genuinely absent** rather than stubbed, and pairs it with an
assertion that the stage prices are still perfectly readable in that same test — so the refusal is
a refusal to *use* them, not an artefact of an empty box.

**The control this replaces was green throughout.**
`test_the_customer_year_ceiling_is_the_SAME_arithmetic_re_ruled` asserted the two ceilings were
"one sum in two units", and it stayed green the whole time the customer-year ceiling was 29.2x
optimistic — **because both sides shared the defect**. Making them agree was the wrong property to
pin: `settled_book_ceiling` prices the scale probe's instrument correctly, and a whole run holds
far more than its settlement rows. An identity between two functions is only a control when the two
are supposed to have the same subject.

## Owed

1. **0.25 is undefended.** The share of the guest a run may hold now sets the ceiling directly, and
   no artefact argues for it. It is the same shape as the 1,200 the constant's own note already
   calls historical — one rung further out.
2. **The 1,200 repeat point** (owed item 2 of the blocking finding) is still owed: it separates
   "the run's fixed cost regressed" from "the box was contended". The August clean point was
   4,193 MB at the same budget; September's is 5,507.4.
3. **`tools/settlement_ceiling_probe.py` is still uncommitted** on the shared tree, mid-run by
   another lane. Not touched here.
