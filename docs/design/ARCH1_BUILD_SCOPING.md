# ARCH1 next slice — BUILD scoping + evidence (2026-07-15)

Framed turn on "route the saas run-path through `build_sim_interface()` so the RSS-collapse
is measured → earn a level, below-target 29→28." **Outcome: framing revealed the honest
scope is a large, high-blast-radius migration, not a one-turn wiring — and I will not fake a
level to hit the number (RULE 0 WALL: honesty about levels; R12 anti-goal-seek). Here is the
evidence and the real path.**

## Finding 1 — the seam is NOT on the heavy run path [observed]
A "life" is `python3 -m saas.reporting.annual_report`, which calls
`simulation.run_phase4c_on_phase2b.main()` and consumes its `all_records` output. That path
constructs **no `SimInterface`** — `build_sim_interface()` / `RecordedSimInterface` have
**zero callers** in the run path (only `company/portal/app.py` and the capture tool use the
seam). So setting `SIM_RECORDED_TRACE` does **nothing** to the real run: the mock built last
session is architecturally **disconnected** from the memory-heavy path. Routing the run
through the seam is a migration of the core sim/company run, not a wiring tweak.

## Finding 2 — the memory IS in the (replayable) world, not the output [observed, profiled]
Profiled a truncated 2016 life (`SIM_FAST_MODE=1`, `report_end=2016-12-31`):
- peak RSS **737 MB** (consistent with `tournament_runner`'s measured 0.77 GB @ 2016).
- `all_records` = **115,292 records**, yet **freeing the entire run output released only 63 MB**
  (~8.5% of 737 MB). The other ~90% is the **world + machinery** built during the run
  (weather/curve/price data + engines), and it scales with the window (0.77 GB @ 2016 →
  5.67 GB @ full 9.5 yr).

This **supports** the FRAME's premise (the replayable exogenous world dominates the RSS, not
the endogenous output) — I checked it because linear-window-scaling was ambiguous, and the
del-and-remeasure settles it in the FRAME's favour. So the memory win is plausibly real.

## The honest consequence for the level
- **L1** ("a mock life runs at materially lower measured RSS") and **L2** ("mock composes
  with A8, workers>1 measured + gap measured") BOTH require a mock life to actually run
  through the seam. Neither is earnable without Finding-1's migration. **No level moved this
  turn; below-target stays 29 — deliberately, not for lack of trying.** Faking L2 would be
  goal-seeking a metric into a high-blast-radius change on the live run — exactly what R12/
  R13 and "a framed turn, not a rushed one" forbid.

## The real path (multi-turn, gated on one more measurement)
1. **Gate first (cheap, safe):** profile the ~674 MB non-output RSS to split it EXOGENOUS
   (replayable: weather/curve/price world) vs ENDOGENOUS (live: customer book, billing, risk
   committee). This fraction **bounds the achievable win** — if most is endogenous machinery,
   the mock helps little and ARCH1 needs re-framing; if most is exogenous, the migration is
   justified. This is the R4 smallest-closed-loop test the whole atom rests on. (`tracemalloc`
   is insufficient — the memory is largely numpy/C; needs an RSS-checkpoint or `memray` pass.)
2. **Then migrate incrementally, seam by seam:** make the run get its exogenous world through
   `build_sim_interface()` so a recorded life skips the bulk world-load — starting with the
   single largest exogenous consumer, measured before/after, on a branch, with the full suite
   as the gate (this path IS the live board-pack run — high blast radius, no big-bang).
3. **L1 lands** when one mock life completes with the same fitness-JSON shape at materially
   lower measured RSS; **L2** when the tournament shows workers>1 + the COUPLED_TRIAD gap.

## Note — an existing cheaper lever (not ARCH1's, but relevant)
`tournament_runner` already unlocks parallelism for **truncated** lives (2016 = 0.77 GB →
many workers) by passing a smaller `per_life_rss_bytes`. ARCH1's distinct value is
**full-window fidelity at low memory**, which is precisely what needs the migration — truncation
trades fidelity for memory; the mock trades a measured, bounded gap instead.
