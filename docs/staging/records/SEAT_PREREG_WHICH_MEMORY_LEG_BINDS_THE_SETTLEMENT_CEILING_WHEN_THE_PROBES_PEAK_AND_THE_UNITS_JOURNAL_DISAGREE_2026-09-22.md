**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PRE-REGISTRATION — which memory leg binds `SETTLEMENT_CUSTOMER_YEAR_BUDGET`, filed before the measurement

**Filed:** 2026-09-22, before running `weight_drift("sim_run")` or fitting the curve. Drawn as Lane 0
delivery, `the-settlement-ceiling-can-move-now-that-its-curve-has-landed`.

## Why this is pre-registered and not just done

The item asks me to derive the constant from the curve at `c4bee75e3`
(`docs/observability/settlement_ceiling_slope_20260921.json`). Reading the artefact against
`background/resource_headroom.py` turned up a disagreement I did not expect and whose answer I do
not know, so it gets a prediction before it gets a measurement.

**The disagreement.** Both numbers describe the peak RSS of a value-cycle run at
`SETTLEMENT_CUSTOMER_YEAR_BUDGET = 1200`:

| source | peak RSS at budget 1,200 | how it was taken |
|---|---|---|
| `settlement_ceiling_slope_20260921.json` point 1 | **5,507.4 MB** | the probe's own `/proc` sampling of the child it spawned, 2026-09-21 |
| `resource_headroom.CLASS_WEIGHTS_MB["sim_run"]` | **13,824 MB** | systemd's record for `sim-runner.service`, re-derived 2026-08-24 from fourteen OOM kills in one day |

They are 2.51x apart and the ceiling is currently priced on the smaller one:
`premise_population.load_whole_run_rss_curve` reads the probe's `peak_rss_mb`, and
`settled_book_ceiling_customer_years` turns it into the 1,312 customer-years the site now publishes.

## Predictions, before the measurement

1. **`weight_drift("sim_run")` returns `drifted: True`** — i.e. `sim-runner.service`'s journal
   carries an observed peak above 13,824 MB in the last 24h. Stated because the probe's own point 4
   reached 13,920.9 MB and the unit's book has grown since 2026-08-24. *Confidence: low-moderate.
   The competing outcome is `readable: False` — the probe ran ad hoc rather than as the unit, so its
   13,920.9 MB may appear in no journal at all, which would itself be the finding.*
2. **The two figures are not the same quantity.** I predict the probe's `peak_rss_mb` is a
   single-process RSS and systemd's is a cgroup-wide figure (`memory.peak` / `MaxRSS` over the unit
   and every child), so the unit's number legitimately exceeds the probe's and **the probe's curve
   under-prices the memory leg of the real producer.**
3. **The budget-axis fit will put the ceiling ABOVE the landed 1,312**, not below — near 1,330–1,345
   customer-years. Reason: the landed figure's 4.3402 MB/cy is a secant across 1,197 → 3,135.5
   committed customer-years, and on a curve already established as convex a wide secant overstates
   the local slope at the bottom of the range, which understates a ceiling sitting only ~136
   customer-years above the anchor. **This is the direction that flatters, so if it comes out this
   way I take the narrower of the two, not mine.**
4. **The declared `sim_run` weight will NOT need raising as a consequence of my value.** At any
   ceiling near 1,312 the probe's own line implies a ~6,008 MB peak, which is 0.43x of the declared
   13,824 MB. If the weight has to move at all it will be because of prediction 1 — a fact about
   the unit today, independent of this constant.

## What would refute each

1. `weight_drift` returning `drifted: False` with a readable journal, or `readable: False`.
2. Finding the probe samples the child's cgroup, or reads `VmHWM` of a process tree — then the two
   ARE the same quantity and the 2.51x gap is a real regression or a real improvement, not a unit
   error, and the ceiling's basis is in worse trouble than prediction 2 says.
3. A quadratic through points 1–3 on the budget axis evaluating below 1,312.
4. My fitted value landing anywhere near the 13,824 MB book.

## The commitment

Whatever the fit says, the constant ships as the **narrowest** of the legs that are evidence —
memory, wall clock against `publish_freshness.PUBLISH_CADENCE_SECONDS = 604,800`, and the funnel's
own supply — and the note names which leg binds. Point 4 of the curve is excluded from the budget
axis because it refused 0 of 500 wins and is therefore funnel-bound, not budget-bound: it is not a
point about this constant's ceiling. Points 2 and 3 contribute their `customer_year_budget_seen` and
`peak_rss_mb` only, never their contaminated `customer_years_committed`.
