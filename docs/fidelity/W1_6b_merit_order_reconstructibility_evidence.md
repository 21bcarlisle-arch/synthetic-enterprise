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

---

## Re-audit (2026-07-30, W1_6b BUILD fork, re-verify-don't-re-stamp)

Independently re-ran everything rather than trusting the 2026-07-28 record.

- **`pytest tests/sim/test_merit_order_reconstruction.py`**: 12/12 passed at the time of re-audit
  (10 pass + 2 real-data tests, since `sim/cache/` — gitignored — was present in the checkout used
  for the real-data re-run). `env PYTHONPATH=. python3 simulation/run_merit_order_reconstructibility.py`
  reproduced the **exact same table** as this doc (82,760 rows; 2016 −0.72, 2017 −1.76, 2018 +0.11,
  2019 +3.64, 2020 +3.25; 3/5 → NOT MET). The claimed measurement is real and reproducible, not stale.
- **`sim/price_engine.py` does NOT call into `merit_order_reconstruction.py` anywhere** — confirmed by
  grep. The engine is a standalone analysis/measurement module, not yet wired into the live simulated
  price path. This matters for the level verdict below.
- **R15 mutation audit, one control per exit criterion** (`tests/sim/test_merit_order_reconstruction.py`
  §4, added this pass):
  1. **Criterion 1** (`per_cell_reconstructibility` / `reconstructibility_verdict`) — NOT tautological:
     monkeypatching the reconstruction to be literally identical to `gas_floor_alone` correctly drives
     `mae_lift` to 0 and `n_won` to 0 (`test_R15_criterion1_control_not_tautological_...`). **But a real
     FAIL-OPEN was found and is NOT fixed here** (out of this fork's `file_scope`):
     `reconstructibility_verdict({})` returns `met=True` vacuously on empty input (empty `losing_cells`
     set) — a caller handed empty/malformed data would see "exit criterion 3a: MET" with zero evidence
     behind it. Pinned as a strict-xfail (`test_R15_KNOWN_GAP_reconstructibility_verdict_fails_open_on_empty_cells`)
     naming the exact fix (`simulation/run_merit_order_reconstructibility.py` needs an explicit
     `if not cells: return not-met` guard) for whoever owns `simulation/`.
  2. **Criterion 2** (frozen ruler) — confirmed genuinely independent, not just present-by-identity: a
     mutation test (`test_R15_frozen_ruler_survives_a_price_engine_mutation`) monkeypatches
     `price_engine.THERMAL_EFFICIENCY` and proves `gas_floor_alone_price_gbp_per_mwh` here does NOT move
     (value-bound at import time). The existing identity check on `_NAIVE_FAMILY_IDS` still holds.
  3. **Criterion 3** (R15 mutation controls themselves) — independently re-verified by hand outside
     pytest: reversing the merit stack and inflating a single plant's SRMC both correctly flip
     `is_merit_order_monotone` to `False`; a hand-built crisis-carry cell dict
     (`{"2019": losing -3.0, "2022": winning +20.0}`) correctly returns `met=False` with `"2019"` in
     `losing_cells` despite a positive `aggregate_lift` of +17.0. Both fire on their named defect; both
     already-existing tests are genuine, not decorative.
- **No fabricated data used**: no network probe was attempted (none needed — no new external series was
  sourced this pass); the EU/UK-ETS carbon-price NAMED GAP remains open exactly as recorded on 2026-07-28.

### Honest level verdict: still proposed L1, not L2/L3

Evidence supporting L1 (not L0): a real, grounded, falsifiable SRMC engine exists; it reproduces its
claimed measurement exactly on real Elexon/gas data; its R15 controls are genuine (mutation-verified
both ways this pass, not merely asserted).

Evidence AGAINST L2/L3:
- **Criterion 1 (the headline reconstructibility claim) is still 3/5, not 5/5** — unchanged since
  2026-07-28, correctly NOT tuned to close the gap (R12/R13). The remaining gap is the same NAMED,
  non-fabricable EU/UK-ETS carbon-price time series (2016/2017 losing cells).
- **The engine is not wired into `sim/price_engine.py`** — it exists as a parallel, standalone
  measurement module. "Ordinary-day SSP substantially reconstructible" per the atom's own wording is
  not yet true of the LIVE simulated price path, only of this offline analysis.
- **A real fail-open was found this pass** in `reconstructibility_verdict`'s handling of empty input
  (see above) — a control that cannot fail on its own null case is exactly the R15 pattern this project
  treats as disqualifying evidence until fixed; it is queued (xfail-pinned), not silently absorbed.

Recommended `level_current`: **1** (unchanged from the prior proposal). `level_target: 3` requires, at
minimum: (a) the ETS-series DISCOVER closing 2016/2017 without curve-fitting, (b) the empty-input
fail-open closed, (c) a director/twin decision on whether "reconstructible" requires live wiring into
`price_engine.py` or stands as a standalone diagnostic capability. None of these are one-way doors; all
are queued as follow-on work, not blocked on this report.

---

# Residuals (a), (b), (c) closed — 2026-08-03 BUILD fork

All three named residuals from the 2026-07-30 re-audit were worked this tick. The headline is that
**(a) produced a result that FALSIFIES the FRAME's own hypothesis**, and the honest number went
DOWN. It is recorded as-is.

## (b) The empty-input FAIL-OPEN — CLOSED, and closed as a CLASS (R10)

`reconstructibility_verdict({})` returned `met=True` on empty input. Fixed, and the strict-xfail pin
(`test_R15_KNOWN_GAP_...`) is deleted and replaced by a real passing test.

Per **R10 an absurdity-class defect may not be closed with an instance fix**, so the whole family was
audited. A **second, previously unreported instance of the same defect was found**:
`is_merit_order_monotone([])` also returned **True** — `zip(s, s[1:])` is empty for a 0- or 1-element
stack and `all([]) is True`, so the merit-order ordering control PASSED with no pair to order.

The class is now: *every function in this atom that renders a judgement must be NOT-MET on (i) empty
or missing evidence and (ii) non-finite (NaN/inf) evidence, rejected FIRST before any comparison* —
because `nan < x` is silently False and would otherwise decide a verdict by accident rather than by
intent. Three members, all guarded:

| control | empty-evidence defect | now |
|---|---|---|
| `reconstructibility_verdict` | `{}` → `met=True` | not-met + `vacuous=True` + `not_met_reason` |
| `is_merit_order_monotone` | `[]` / 1 plant → `True` | `False` (ordering is a claim about a PAIR) |
| `per_cell_reconstructibility` | NaN MAE scored by accident | explicit `evidence_finite` flag |

The **class guard is automatic, not a hand-kept list**: the test DISCOVERS the family by introspecting
both modules for public callables whose name carries a judgement marker and fails if the discovered set
disagrees with `VACUITY_GUARDED_CONTROLS`. Mutation 6 below proves that works.

**The guards changed no measured value** — the re-run reproduced the 3/5 table bit-identically, so they
are pure fail-closed additions, not a silent re-measurement.

## (a) The EU/UK-ETS carbon series — SOURCED (network WAS available), and it made the score WORSE

The prior pass recorded "no network probe was attempted". **The network was in fact available.** A real,
primary, machine-read series was obtained — full probe log (including 6 failed probes) in
`docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md`:

- **EU-ETS 2016-2020** — EUA annual **volume-weighted primary auction clearing price**, computed from
  EEX's own `Emission Spot Primary Market Auction Report` 2012-2025 archive (per-auction rows, weighted
  by auction volume). EEX is the platform the allowances are actually auctioned on. *Caveat, stated:
  auction clearing price, not continuous secondary-market spot.*
- **FX** — ECB official daily reference rate `EXR.D.GBP.EUR.SP00.A`, annual mean, ECB Data Portal API.
- **UK-ETS 2021** — DESNZ statutory determination, the one year that is a genuine same-year auction VWAP
  (£47.96/t).
- **UK-ETS 2022-2024 — still a NAMED GAP, deliberately not filled.** The statutory series turns
  FORWARD-REFERENCING from 2022 (the figure labelled year N is the Dec-N UKA futures contract as traded
  during year **N-1**). Applying it year-for-year would misalign the cost with its own calendar year, and
  deriving a same-year spot from it would be fabrication. Those years fall back to CPS-only and are named
  in `ETS_SERIES_NAMED_GAP_YEARS`.

Derived carbon (GBP/tCO2, on top of the flat ~£18 CPS): **2016: 4.31 · 2017: 5.08 · 2018: 13.57 ·
2019: 21.64 · 2020: 21.81 · 2021: 47.96**. The EUR series and the FX series are stored separately and
multiplied in code, so the derivation stays visible rather than baked into a constant.

### Criterion 1: 3/5 → **2/5**. The FRAME's hypothesis is FALSIFIED.

| cell | MAE floor | MAE recon (CPS-only) | lift | MAE recon (grounded ETS) | lift | wins? |
|------|----------:|---------------------:|-----:|-------------------------:|-----:|:-----:|
| 2016 | 12.01 | 12.72 | −0.72 | 13.44 | **−1.43** | no |
| 2017 | 12.95 | 14.71 | −1.76 | 15.48 | **−2.53** | no |
| 2018 | 15.48 | 15.37 | +0.11 | 16.74 | **−1.26** | **no (was YES)** |
| 2019 | 18.66 | 15.02 | +3.64 | 16.01 | **+2.65** | YES |
| 2020 | 20.58 | 17.33 | +3.25 | 16.53 | **+4.05** | YES |

The FRAME asserted that wiring the ETS series "closes cells 2016/2017 **without any curve-fitting**".
**That was wrong about the sign.** The real EUA price is strictly POSITIVE in every year, so adding it
can only RAISE the reconstructed price — it cannot reduce an over-prediction. 2016/2017 got worse and
2018 flipped from a marginal win to a loss.

**The series stays anyway (R13).** A GB CCGT in 2019 genuinely paid CPS + EUA ≈ £39.6/tCO2. Modelling
that as zero is factually false about the world. Reverting it to protect a 3/5 score would be tuning an
INPUT to flatter an OUTPUT — precisely what R12/R13 forbid. **3/5 bought by pretending the EU ETS did
not exist is worth less than an honest 2/5.**

### The finding that actually matters: a TREND error became a LEVEL error

Mean signed error (reconstruction − real SSP), ordinary hours:

| cell | bias, CPS-only | bias, grounded ETS | (naive gas floor's own bias) |
|------|---------------:|-------------------:|-----------------------------:|
| 2016 | **+3.24** | +4.87 | −6.63 |
| 2017 | +3.42 | +5.35 | −6.72 |
| 2018 | +1.21 | +6.33 | −8.91 |
| 2019 | −3.86 | +4.07 | −13.98 |
| 2020 | **−4.95** | +3.01 | −14.15 |
| **spread** | **8.39 (SIGN FLIPS)** | **3.32 (consistent)** | 7.52 |

With flat carbon the error **swings sign** across the window: the model mis-tracks how the world
CHANGED. With the real, correctly time-varying carbon the error becomes uniformly positive and its
spread **more than halves** — a near-constant ~+£4.7/MWh level offset. Adding a true input converted a
**trend error into a level error**, which is what a genuine fidelity improvement looks like even when an
MAE-vs-naive-floor criterion scores it lower. This is pinned as a falsifiable test
(`test_grounded_carbon_makes_the_bias_a_LEVEL_offset_not_a_TREND_error`), not just asserted here.

**Named, unaddressed cause of the residual offset:** SSP is the **imbalance cash-out SELL price**, which
sits systematically below the wholesale marginal *energy* price an SRMC stack reconstructs. Criterion 3a
may therefore be grading a wholesale reconstruction against a non-wholesale target — a
**measurement-validity question about the criterion's construction**. It is recorded here and
deliberately **NOT** used to rewrite the criterion in this atom's own favour. Note the naive gas floor's
own bias also grows (−6.6 → −14.2) exactly as real carbon rose, which is consistent with the same story.

## (c) Live wiring into `sim/price_engine.py` — DONE, default deliberately unchanged

The prior pass filed this as needing "a director/twin decision". Under NEVER_ASK_WITHOUT_RECOMMENDING and
THE STANDARD **it does not** — it was assessed on the merits and taken.

`synthetic_price()` now takes `engine=` (`"reduced_form"` default | `"merit_order"`). The SRMC engine is
therefore **live and callable on the real price path**, which is what residual (c) actually asked for; it
is no longer a standalone offline module.

**Recommendation taken: wire it, do NOT flip the default yet.** Reasoning, decided blind to company P&L
(R13 — margin was never inspected, and the grading metric is MAE against real Elexon SSP):

- FOR making it default: structurally it is how a real GB price forms (marginal plant SRMC, not a fitted
  multiplier on a gas floor); it reaches regimes the reduced form cannot (oversupply collapse, the £6,000
  cash-out ceiling); it wins the renewables-heavy cells where the reduced form posts negative lift.
- AGAINST, and decisive for now: it **loses 3 of 5 calm cells to even the naive gas floor**, so
  defaulting to it would knowingly import a measured regression into the live path. It is also measured
  only on calm ordinary hours (82,760 periods) — there is **no measurement at all** on crisis years
  (2021-2022) or on tight hours, whereas the reduced form's constants were fit across the full
  2016-2025 window (n=157,106). Promoting on a partial measurement is the control-set hole this project
  has been bitten by before.

This is **not** deferral-because-it-is-big: the wiring is done. What is declined is flipping the default,
and that refusal rests on a measurement, not on effort. The default flips when criterion 1 genuinely
clears — a one-line change.

Fail-closed on the new seam: `engine="merit_order"` **raises** without an explicit `year` (the SRMC stack
is time-indexed; a silent year default would price everything off one arbitrary vintage and still look
like it worked), and an unknown engine name raises rather than falling through to the default.

## Criterion 2 (the frozen ruler): **DID NOT MOVE** — verified, not assumed

This is the proof the pricing became RIGHT rather than TUNED. Re-verified this pass:

- `THERMAL_EFFICIENCY == 0.50`, unmoved; `gas_floor_alone` still present in
  `background/fidelity_emitter._NAIVE_FAMILY_IDS` by identity; `gas_floor_alone_price(30.0) == 60.0`.
- **The entire `MAE_floor` column is bit-identical across every run in this document** — 12.01, 12.95,
  15.48, 18.66, 20.58 — before the guards, after the guards, under CPS-only carbon, and under the
  grounded ETS series. The ruler was never touched; only the thing being measured moved.

## R15 mutation log — 7 mutations, each fired on its own named defect

Every guard was mutated OUT, the suite run, the firing test recorded, then restored **by hand** (never
`git checkout`, which would have wiped the edit).

| # | mutation | tests that FIRED |
|---|---|---|
| 1 | `reconstructibility_verdict` empty-evidence guard disabled | instance test + **class** empty-evidence test |
| 2 | malformed/non-finite cell guard disabled | instance test + **class** non-finite test |
| 3 | `is_merit_order_monotone` vacuous-stack guard disabled | class empty-evidence test + single-plant test |
| 4 | non-finite SRMC rejection disabled | class non-finite test |
| 5 | per-cell finiteness guard forced True | per-cell non-finite test |
| 6 | **added an unguarded new control** `sneaky_new_verdict` | registry-vs-introspection test named it exactly |
| 7 | `engine=` selection falls through to the default | all 3 live-wiring tests |

Mutation 6 is the one that matters for R10: it proves the class guard catches a NEW unguarded control
automatically, so the defect class cannot silently regrow. Mutation 7 additionally caught a **real bug I
had introduced** — `price_engine.synthetic_price` was passing `ets_price_gbp_per_tonne=0.0` explicitly,
which silently overrode the grounded series on the live path. Fixed.

## Honest level verdict: **L1 → L2**, and explicitly NOT L3

Evidence **FOR L2**: the atom's headline named gap (the ETS series) is CLOSED from primary sources for
2016-2021, with provenance and a probe log; the engine is LIVE on the real price path, not a standalone
module; a real fail-open is fixed and generalised to its whole class with an automatic, introspection-
driven guard; 7 mutations prove every control fires on its own named defect; the frozen ruler is
verified unmoved.

Evidence **AGAINST L3** — the level is not proposed and should not be granted:
- **Criterion 1 is 2/5, worse than the 3/5 it started at.** The headline claim "ordinary-day SSP
  substantially reconstructible" is *not* demonstrated. This is the single dominant reason.
- **The merit-order engine is not the default price path**, so the live simulated price is still the
  reduced form. The capability is reachable, not in force.
- **Criterion 3a's own validity is now in question** (SSP is an imbalance price, not a wholesale price).
  An exit criterion whose construction is suspect cannot support a promotion.
- **No measurement exists on crisis years or tight hours** — the coupled triad's "no world atom reaches
  L3 until the company has been tested against it and the gap measured" is unsatisfied.

## Left undone, and why

1. **UK-ETS 2022-2024 same-year carbon** — refused rather than fabricated (forward-referencing statutory
   series). Needs ICE UKA settlement data; queued, not guessed.
2. **The +£4.7/MWh level offset** — diagnosed and pinned but not fixed. The prime suspect (SSP vs
   wholesale basis) would change what criterion 3a *measures*, and changing an exit criterion while
   holding the atom that it grades is exactly the conflict of interest R15/exit-test integrity forbids.
   It belongs to a separate FRAME.
3. **Flipping the default engine** — gated on criterion 1 clearing honestly, per (c) above.
4. **Crisis-year / tight-hour measurement** — not in this atom's calm-window scope; named as the L3
   blocker above.

---

# Addendum, 2026-08-03 (later worker tick) — the validity question, settled by an ORACLE rather than by an argument

The section above left item 2 open and said why it had to be left open:

> **The +£4.7/MWh level offset** — the prime suspect (SSP vs wholesale basis) would change what
> criterion 3a *measures*, and changing an exit criterion while holding the atom that it grades is
> exactly the conflict of interest R15/exit-test integrity forbids. It belongs to a separate FRAME.

That reasoning still holds, so **criterion 3a is NOT changed here.** What this tick adds is the thing
that resolves the question without touching the criterion: an **independent measurement**, and then an
**oracle test** that puts the criterion itself on trial using data the engine had no part in producing.

## What was built

`sim/market_index_history.py` — Elexon **MID** (Market Index Data): the volume-weighted price of actual
short-term wholesale trades, per settlement period, from the same Insights API as SSP. This is the price
a merit-order SRMC stack is a model *of*. **147,290 raw records → 73,272 volume-weighted periods**,
2016-09-12 → 2020-12-31, cached to `sim/cache/elexon_mid_full.json` (gitignored, like the demand/AGWS
caches; rebuild with `python3 -m sim.market_index_history`).

The harness now reports **both targets, side by side, always**. The SSP path is untouched:
`per_cell_reconstructibility()` returns exactly what it always did, keeping the shipped control's
contract and its mutation proofs intact.

### R12 pre-commitment, recorded before the MID numbers were read

Adding a second target right after scoring 2/5 is what goal-seeking looks like from outside. So the
pre-commitment was written into the module docstring first: the SSP verdict remains the ratified
criterion and is never overwritten; both are always printed; **and if MID made the reconstruction look
worse, that would be the finding and it would stand.** The target is justified by what MID *is*, not by
what it clears.

## The measurement

| cell | n_ord | mean | MAE_floor | MAE_recon | lift | wins? | span |
|---|---|---|---|---|---|---|---|
| **SSP — ratified criterion 3a** ||||||||
| 2016 | 6,454 | 28.96 | 12.01 | 13.44 | −1.43 | no | full year |
| 2017 | 8,946 | 36.55 | 12.95 | 15.48 | −2.53 | no | full year |
| 2018 | 9,495 | 51.36 | 15.48 | 16.74 | −1.26 | no | full year |
| 2019 | 10,653 | 36.03 | 18.66 | 16.01 | +2.65 | YES | full year |
| 2020 | 12,544 | 29.36 | 20.58 | 16.53 | +4.05 | YES | full year |
| | | | | | | **2/5** | |
| **MID — traded wholesale price** ||||||||
| 2016 | 1,722 | 34.21 | 11.76 | 4.82 | +6.94 | YES | **part year** 09-12.. |
| 2017 | 8,858 | 38.12 | 9.68 | 5.97 | +3.71 | YES | full year |
| 2018 | 9,443 | 51.85 | 11.14 | 8.35 | +2.79 | YES | full year |
| 2019 | 10,543 | 36.48 | 15.67 | 7.53 | +8.14 | YES | full year |
| 2020 | 12,477 | 28.76 | 16.18 | 8.87 | +7.31 | YES | full year |
| | | | | | | **5/5** | |

Same engine, same frozen naive ruler, same ordinary-hour mask. **Only the target differs.** Against the
price it actually models, the reconstruction's error roughly **halves** (2017: 15.48 → 5.97) and it beats
the naive floor in every cell.

## The oracle test — and it REFUTED the hypothesis that motivated the work

The tempting conclusion from that table is "criterion 3a is measuring the wrong thing." The two
instruments are genuinely far apart on ordinary hours — **MAE(SSP, MID) = 12.30 £/MWh**, correlation
**0.655**, with SSP carrying roughly twice MID's dispersion (sd 18–22 vs 7.5–13). That gap is *larger
than the lift the criterion grades*, which makes it very easy to argue the criterion is unpassable.

**That argument is wrong, and a measurement says so.** Score the **real traded price** as if it were the
predictor — the best any wholesale model could possibly do — against SSP, under criterion 3a unchanged:

| cell | MAE_floor | MAE of the REAL traded price | lift | beats the naive floor? |
|---|---|---|---|---|
| 2016 | 13.47 | 11.25 | +2.22 | YES |
| 2017 | 12.93 | 12.66 | +0.28 | YES |
| 2018 | 15.39 | 13.19 | +2.20 | YES |
| 2019 | 18.54 | 12.08 | +6.46 | YES |
| 2020 | 20.57 | 11.71 | +8.86 | YES |

**5/5.** A perfect wholesale model passes criterion 3a. So the criterion is **passable**, it is **valid**
as a test of reconstruction, and it **stands unchanged**. The 2/5 shortfall is the **engine's**, not the
target's. The suspicion recorded in item 2 above is hereby **refuted by measurement**, not argued away —
and this is the outcome that cost the atom something, which is the point: had the oracle failed, the
criterion would have been the thing that was wrong.

`test_criterion_3a_is_VALID_because_the_real_traded_price_passes_it` keeps the refutation standing: if a
later change to the naive ruler or the ordinary-hour mask ever makes the true price fail its own
criterion, the criterion has become invalid and the suite says so loudly.

### What the residual actually is, now that it is decomposed

- reconstruction → MID error (the model's own wholesale error): **4.8 – 8.9 £/MWh**
- MID → SSP spread (the instrument gap, irreducible for *any* wholesale model): **11.3 – 13.2 £/MWh**

2017's oracle margin is **+0.28** — the true price barely clears the naive floor. In the low-price early
years a flatter predictor scores well against a noisy cash-out target, which is why the naive floor is
hard to beat there and why the engine's remaining ~3 £/MWh of wholesale error is enough to lose the cell.
That is a **quantified, falsifiable** account of the shortfall, replacing "SSP might be the wrong target."

## Honest bounds, stated rather than buried

- **MID coverage begins 2016-09-12** (bisected against the live API: 09-10 returns 0 records, 09-12 a
  partial 40, 09-13 a full 96). The calm window opens 2016-03-01, so the **2016 MID cell is a PART YEAR
  (~30%)** and is *not* like-for-like with the full-year SSP 2016 cell. 2017 and 2018 are full years and
  both flip from loss to win, so the finding does not rest on 2016.
- Rows outside MID coverage carry **no `mid` key at all** — never a carry-back, an interpolation or a
  zero. `test_rows_outside_mid_coverage_carry_no_substitute_value` enforces it.
- The measured tests **SKIP** without the caches. A skip is not a pass.

## Two live-API fail-opens found and guarded (R15)

Both were **observed**, not hypothesised:

1. **A too-wide range returns HTTP 200 with an empty `data` list.** A 31-day window returned `{"data":
   []}` with a 200, while the same window in 7-day chunks returned ~1,490 records/week. Silently reading
   that as "no trading occurred" would punch undeclared holes in the series. An empty in-coverage window
   now raises.
2. **A reporting provider publishes price 0.00 on volume 0.00.** `N2EXMIDP` does this in every period
   sampled across 2016-2020 while `APXMIDP` carries the real trades. A naive mean across providers would
   **halve every wholesale price in the series**.

### A tautology in my own test, caught only by mutating

The chunk-width control originally asserted the issued window width against `MAX_RANGE_DAYS` — **the same
constant that produced it**. Mutating `MAX_RANGE_DAYS` 7 → 31 made the fetcher issue 31-day windows and
the test **still passed**, because it re-derived its own expectation from the mutated value. It now
asserts against the **literal 7**, the width measured against the live API, as an independent oracle.

This is the R15 TAUTOLOGY pattern (*checked value derived from the same source it checks*) appearing in a
test written by someone who had just read the rule — and, as with the `min(x) == min(x)` case in
`H_GAP`, **reading the test did not find it and mutating the source did.**

Also worth recording honestly: the zero-volume test does **not** prove the `volume <= 0` guard. Volume-
weighting already neutralises a 0/0 provider (it contributes 0 to both numerator and weight), so that
test passes with or without the line — it proves the *weighting*. What the line uniquely guards is
**negative** volume, which subtracts from the denominator (unguarded: £290.0 from a £50 trade). That is
now its own test, and it is the one that fires when the guard is removed.

## R15 mutation ledger — 7 mutations, each firing its own named test

| # | mutation | test that fired |
|---|---|---|
| 1 | volume-weighting → flat mean across providers | `..._is_volume_weighted_across_genuinely_reporting_providers` |
| 2 | empty in-coverage chunk → silent hole instead of raise | `..._empty_response_inside_coverage_raises...` |
| 3 | coverage-start guard removed | `..._before_coverage_start_raises_as_a_named_gap` |
| 4 | `MAX_RANGE_DAYS` 7 → 31 | `..._range_is_chunked_no_wider...` (**only after the tautology was fixed**) |
| 5 | missing MID filled with SSP | `..._rows_outside_mid_coverage_carry_no_substitute_value` + part-year test |
| 6 | non-200 response → `[]` instead of raise | `..._non_200_raises_rather_than_returning_empty` |
| 7 | `volume <= 0` guard removed | `..._negative_volume_is_rejected...` |

Baseline restored **byte-identical** after every mutation (`diff` against pre-mutation copies).

The R10 class registry did its job unprompted: adding `per_cell_reconstructibility_vs_target` **broke
the suite immediately**, because the introspection-driven family guard saw a new judgement function with
no vacuity guard and no registration. It was registered and given its own empty-evidence case — which
has **two** null forms, not one: no rows at all, and rows that exist but carry no value for the requested
target. The guard was honoured, not weakened.

## Level verdict: **L1 → L2**, still explicitly NOT L3

The prior section proposed L1 → L2 and it was never recorded in the map. That proposal is now recorded,
with this tick's evidence added to it.

One of the four reasons that section gave AGAINST L3 is **discharged**: *"criterion 3a's own validity is
now in question"* — it was put on trial and it passed. The other three stand, unchanged:

- **Criterion 1 is 2/5 against SSP.** The atom's headline claim, "ordinary-day SSP substantially
  reconstructible", is still not demonstrated on its own ratified target. This remains the dominant
  reason and it is **not** softened by the MID result: winning 5/5 against wholesale is a different claim
  from the one the atom makes.
- **The merit-order engine is not the default price path** — reachable, not in force.
- **No crisis-year or tight-hour measurement**, so the coupled-triad rule is unsatisfied.

## Left undone (updated)

1. **UK-ETS 2022-2024 same-year carbon** — still refused rather than fabricated.
2. **The remaining wholesale error (4.8–8.9 £/MWh)** — now the real target, and now measurable directly
   against MID rather than through 12.30 £/MWh of cash-out noise. This is what a further engine
   improvement should be graded on.
3. **Flipping the default engine** — still gated on criterion 1 clearing honestly.
4. **Crisis-year / tight-hour measurement** — MID covers 2021-2022 too, so the crisis-cell measurement
   this atom lacks is now buildable from the same source.
