# W1_6b — Merit-order reconstructibility: measured evidence (2026-07-28)

**Atom:** `W1_6b_merit_order_reconstruction` (lane `W1_market_weather`, front `SIM_ACTORS` open).
**Build:** `sim/merit_order_reconstruction.py` + `tests/sim/test_merit_order_reconstruction.py`
+ `simulation/run_merit_order_reconstructibility.py`.
**DISCOVER/FRAME (discharged):** `docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md`,
`docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md`.
**Discipline:** R12 (the measurement is a DIAGNOSTIC, never a target) · R13 (baseline changed for
fidelity-to-reality reasons only, blind to company P&L) · no ground-truth fabrication (FRAME §4).

---

## What was built

A structural, typed short-run-marginal-cost (SRMC) dispatch engine that returns the SRMC of the
**marginal (last-dispatched) plant** against residual demand `RD = demand − renewables`, replacing
the globally-fitted `gas_floor · (A0 + A1·x + A2·max(0,x−X_TIGHT)^p)` reduced form in
`sim/price_engine.py`. Three regimes, all from the stack — **not a fitted multiplier**:

1. **Oversupply** (`RD < must-run floor`): renewables/nuclear flood the system; price collapses
   toward the curtailment floor (the low/negative prices `gas_floor_alone` cannot reach).
2. **Ordinary** (CCGT band): the marginal CCGT efficiency slides from best-build (53.7% HHV, low
   load) to worst-vintage (band midpoint anchored to the DUKES fleet-average, high load), so
   ordinary-day price rises with residual demand through **declining marginal efficiency** — a
   grounded merit-order shape, not `A1·x`.
3. **Tight** (`RD > must-run + CCGT`): peakers/reserve; convex climb toward the £6,000/MWh ceiling.

**Every constant is grounded (cited) or a NAMED GAP** — see the module docstring and the DISCOVER.
Carbon uses the **grounded, time-invariant Carbon Price Support (~£18/tCO2, HMRC, 1 Apr 2016 →
31 Mar 2028)**; the EU/UK-ETS **market** carbon price is a NAMED R10 GAP (`ets_price_gbp_per_tonne`
defaults to `0.0`, wired through every function for when a citable series is later sourced).

---

## Measured result — exit criterion 3a (Board Spec 004)

`env PYTHONPATH=. python3 simulation/run_merit_order_reconstructibility.py`, real
Historical-Ground-Truth join (82,760 calm-window settlement periods, 2016-03-01..2020-12-31),
**ordinary hours only** (`x = RD/DISPATCHABLE ≤ X_TIGHT = 0.70`), MAE £/MWh, per calm year-cell:

| cell | n (ordinary) | SSP mean | MAE gas_floor_alone | MAE reconstruction | lift | wins? |
|------|-------------:|---------:|--------------------:|-------------------:|-----:|:-----:|
| 2016 |  6,454 | 28.96 | 12.01 | 12.72 | **−0.72** | no |
| 2017 |  8,946 | 36.55 | 12.95 | 14.71 | **−1.76** | no |
| 2018 |  9,495 | 51.36 | 15.48 | 15.37 | +0.11 | **YES** |
| 2019 | 10,653 | 36.03 | 18.66 | 15.02 | **+3.64** | **YES** |
| 2020 | 12,544 | 29.36 | 20.58 | 17.33 | **+3.25** | **YES** |

**Exit criterion 3a (beat `gas_floor_alone` in EVERY calm cell): 3/5 cells → NOT MET (losing: 2016, 2017).**

## The finding (R12 diagnostic — NOT a cue to tune)

- **The structural repair works where it was supposed to.** The reconstruction wins the two
  renewables-heavy calm cells **2019 (+3.64) and 2020 (+3.25)** — exactly the cells where the live
  reduced form posted NEGATIVE per-cell lift (−0.79, −3.22 in the fidelity ledger). Adding real
  carbon + VOM and letting price collapse in oversupply reconstructs those hours from fundamentals.
- **It loses the low-carbon early cells (2016, 2017).** The ordinary-hour markup over the bare gas
  floor GROWS from ~+£6.6/MWh (2016) to ~+£14.2/MWh (2020). That growth is **not** residual-demand
  driven (2020 has the *lowest* median x yet the *largest* markup) — it tracks the real **EU-ETS
  carbon price surge** (≈€5 in 2016 → ≈€25 by 2019). With only the **flat CPS-only** carbon
  available, the reconstruction over-predicts 2016/2017 (when true ETS+CPS carbon was low) and the
  markup it adds overshoots.
- **The binding missing input is the EU/UK-ETS market carbon time-series** — a NAMED R10 GAP the
  DISCOVER (§4b) explicitly could not source from a citable published series, and which R13/FRAME §4
  forbid fabricating from memory. This measurement PROVES that gap is load-bearing: it is the single
  input whose absence blocks full ordinary-day reconstructibility. **No interim tuning was applied**
  (no per-cell fits, no regime-partition coefficients, no recalibration — R12/FRAME §3c).

## Exit criteria status

| # | criterion | status |
|---|-----------|--------|
| 1 | ordinary-day reconstructibility beats `gas_floor_alone` per calm cell | **PARTIAL — 3/5** (2018/2019/2020 win; 2016/2017 blocked on the ETS-series gap) |
| 2 | unmoved-baseline invariant (frozen naive-family ruler) | **MET** — `gas_floor_alone` reproduces gas/`THERMAL_EFFICIENCY`(0.50)/zero-carbon; family id checked by identity (`test_R15_frozen_ruler_...`) |
| 3 | R15 mutation — mis-ordered stack + aggregate-hiding both FIRE the check | **MET** — `test_R15_a_mis_ordered_stack_fires...`, `test_R15_verdict_is_per_cell_not_aggregate_hiding` |

## Next required work (queued, not fixed on sight — SELF_INTERRUPT_DISCIPLINE)

A **DISCOVER** pass to source a citable EU-ETS (2016-2020) / UK-ETS (2021-2024) annual-average
market carbon-price series (DISCOVER §4b names the candidate sources: ICE/EEX settlement data, the
DUKES annex tables, the UK ETS Authority reports). Wiring that series into
`ets_price_gbp_per_tonne` closes cells 2016/2017 **without any curve-fitting** — the reconstruction
is already structurally complete; it is starved of one grounded input, not mis-shaped.

**Level:** proposed L1 (engine + falsifiable test built; 2 of 3 exit criteria met; criterion 1
partial with a named, non-fabricable data blocker). Any level move stays `blocked_on:
director_level_up` (FRAME §4). This is not L3: the headline reconstructibility criterion is honestly
not yet met.
