**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-slice-12-rescale-the-observable-key-over-the-cuts-own-band-mix` (Lane 0 delivery)

# B11 slice 12: rescaling the key over the cut closes the level to flat, and moves it away from what happened

**DEVELOPMENT.** One book, one seed: `docs/reports/run_output_latest.json` (run at `78f77c34e`,
772 accounts), slice 10/11's book, read through `tools/run_output_store` from the shared tree.
The predictions were filed and on origin before the change existed:
`docs/staging/records/SEAT_PREREG_B11_TWELFTH_SLICE_RESCALE_THE_KEY_OVER_THE_CUTS_OWN_BAND_MIX_2026-10-17.md`
(`688f823b9`). Control: in the same process the fit-window rule reproduces slice 11's levels to the
digit (−0.0300 / −0.0194 / −0.0255 and −0.0241 / −0.0284 / −0.0246).

## The answer

- **The level drift against flat was the rescale's population.** Rescaling over the accounts on
  supply at the cut, each at its view there, closes it to under 0.01 at every cut for both keys.
- **Ranking does not move.** For the switch key the per-customer order is *identical* at all
  three cuts, because the three segments' hazards do not overlap. So the rescale is a pure level
  change there. EP17's rule still reads **not yet**: switchers clear flat at 2023 only.
- **Matching flat is the wrong target for the level.** At every cut the flat rule over-predicts
  held-back departure: +0.241, +0.181 and +0.072 (mean p − realised rate). The rescale moves the
  per-customer level *toward* flat and so *away* from what happened, at every cut and for both
  keys. The fit-window drift that slice 11 called a defect was, by accident, the better-calibrated
  level. **"Level-honest against flat" is not "level-honest"** (F11, as the prereg said).

## The levels

Mean p_pc − p_flat over graded accounts. Calibration is mean p − realised rate.

| cut | graded | realised rate | flat calibration | key | level, fit window → cut | per-customer calibration, fit window → cut |
|---|---|---|---|---|---|---|
| 2020 | 253 | 0.423 | +0.241 | observables | −0.030 → **−0.008** | +0.211 → +0.233 |
| 2020 | | | | switch key | −0.024 → **−0.004** | +0.217 → +0.237 |
| 2022 | 256 | 0.234 | +0.181 | observables | −0.019 → **−0.004** | +0.161 → +0.177 |
| 2022 | | | | switch key | −0.028 → **−0.003** | +0.152 → +0.178 |
| 2023 | 266 | 0.184 | +0.072 | observables | −0.026 → **−0.002** | +0.047 → +0.071 |
| 2023 | | | | switch key | −0.025 → **−0.001** | +0.048 → +0.071 |

The rescale makes each segment's mean monthly hazard at the cut equal to flat's. What remains is
the concavity of p = 1 − Π(1 − h) over the horizon, so it is negative, and it is largest at the
longest horizon (2020, 60 months).

## Ranking (switch key; fit window and cut give the same numbers)

| cut | outcome | key − flat (95%) | key − contract-year (95%) |
|---|---|---|---|
| 2020 | switchers (63) | +0.017 (−0.034, +0.068) | +0.027 (−0.040, +0.093) |
| 2022 | switchers (35) | +0.036 (−0.058, +0.130) | +0.056 (−0.040, +0.153) |
| 2023 | switchers (30) | **+0.103 (+0.002, +0.205)** | +0.075 (−0.024, +0.174) |
| 2023 | movers (19) | **+0.179 (+0.090, +0.269)** | −0.008 (−0.127, +0.111) |
| 2023 | whole book | **+0.133 (+0.056, +0.209)** | +0.043 (−0.038, +0.123) |

For the observables key the whole-book AUC difference moved slightly at 2020 (−0.047 → −0.053)
and 2022 (+0.071 → +0.058), and not at 2023 (+0.099). All three are under 0.02, and none changes
a verdict.

## Each prediction beside its result (wrong ones kept)

- **R1 (observables: negative at every cut, smaller in magnitude than slice 11): HELD.**
- **R2 (within 0.01 at 2022 and 2023, NOT at 2020): WRONG at 2020.** It is −0.008. The concavity
  term at a 60-month horizon is smaller than I priced it. Most of slice 11's −0.030 was the
  window's mix, not the curve.
- **R3 (switch key: negative, smaller, within 0.01 at all three): HELD.**
- **R4 (switchers vs flat moves by under 0.02): HELD**, trivially. The movement is zero, because
  the order is identical. I did not predict that.
- **R5 (EP17 still "not yet"; nothing turns worse than flat beyond the bound): HELD.**
- **Not predicted, the main result:** the calibration moves the wrong way at every cut.

## What it means

The `rescale_over` argument is landed. **The default stays `"fit_window"`.** Of the two levels,
one matches the flat rule and the other is closer to what happened. On this book neither one is
right, because the reference they are scaled to is wrong. The over-prediction at 2020 is +0.24,
and it dwarfs the 0.03 this slice closed. That is the switch level: the fit window holds the
2021–22 crisis exits (`LIMITATION_SWITCH_LEVEL_IS_THE_REGIME`; slice 6). For any per-customer
arm, the level question to answer next is the flat hazard's regime, not the key's normalisation.
For a ranking arm (EP17), the level does not matter, and the rescale changes nothing.

## Landed

- `company/analytics/forward_clv.py`: `run_backtest(rescale_over=...)` over
  `RESCALE_POPULATIONS = ("fit_window", "cut")`, refused when unknown or when no key is given, and
  recorded on `Backtest.key_rescaled_over`. It is passed through `backtest_run_output`.
- `tests/company/analytics/test_forward_clv_backtest.py::test_a_key_rescaled_over_the_cut_averages_the_flat_hazard_there_and_over_the_window_does_not`:
  over a one-month horizon p is the hazard, so the cut rescale's mean p equals flat on the cut's
  accounts, for both keys, and the window rescale's does not. Mutation: the `"cut"` branch never
  taken → red. The window arm is the control that the two populations differ on the fixture.

## Next (not done here)

1. EP17's fresh-seed verdict is still the director's open row. This slice adds nothing to it.
2. If a per-customer *level* is ever used (a margin or CLV figure, not a rank), grade it against
   the realised rate. The flat regime level is the larger defect: slice 6's subject, unsolved.
