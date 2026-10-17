**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-slice-10-the-hazard-sees-what-a-supplier-holds` (Lane 0 delivery)

# B11 slice 10 result: a hazard that sees what a supplier holds cannot yet tell switchers apart, and the key does not go into EP17's arm

**DEVELOPMENT.** Every figure here comes from one book and one seed, in a world whose engagement
axis was fitted to some of the same sources the priors come from.

The predictions were filed before any observable had been read against a departure:
`docs/staging/records/WORKER_PREREG_B11_TENTH_SLICE_THE_HAZARD_SEES_TARIFF_PAYMENT_AND_MONTHS_ON_DEFAULT_2026-10-17.md`,
landed `dea3bb446`.

## The answer

**Cannot tell.** The per-customer hazard keyed on tariff type, payment method and months on
default does not rank switchers above stayers better than the flat rule beyond the 95% bound at
any of the three cuts. The point estimates all favour it: +0.04, +0.09 and +0.09 AUC.

Over the whole book it ranks better beyond the bound at cut 2023 only. The contract-year rule
does the same at that cut, so the gain there is not the new key's alone.

**The key does not go into EP17's arm.** The rule written beforehand needed switchers ranked
better at two or more cuts; there are none.

## Results

The book is `docs/reports/run_output_latest.json`, run at commit `78f77c34e`, with 772 accounts.
The slice-5 book is gone; see the prereg. Every observable is read from the company's own term
record and bills. Each test is paired against flat with the existing DeLong 95% interval.

| cut | graded | outcome | n | AUC difference (observables − flat) | 95% interval | verdict |
|---|---|---|---|---|---|---|
| 2020 | 253 | whole book | 253 | +0.039 | −0.015, +0.093 | cannot tell |
| 2020 | | switchers | 63 | +0.042 | −0.022, +0.105 | cannot tell |
| 2020 | | movers | 44 | +0.034 | −0.038, +0.107 | cannot tell |
| 2022 | 256 | whole book | 256 | +0.082 | −0.007, +0.172 | cannot tell |
| 2022 | | switchers | 35 | +0.086 | −0.033, +0.205 | cannot tell |
| 2022 | | movers | 25 | +0.078 | −0.040, +0.196 | cannot tell |
| 2023 | 266 | whole book | 266 | +0.130 | +0.037, +0.223 | **per-customer ranks better** |
| 2023 | | switchers | 30 | +0.088 | −0.034, +0.210 | cannot tell |
| 2023 | | movers | 19 | +0.196 | +0.083, +0.310 | **per-customer ranks better** |

The contract-year rule on the same book, whole-book difference against flat:

- 2020: −0.008, cannot tell;
- 2022: +0.035, cannot tell;
- 2023: +0.090 (+0.005, +0.176), ranks better.

At 2023 it also ranks movers better (+0.187). The 2023 mover gain therefore belongs to whatever
the two rules share, which is time on book. Neither rule keys on a move.

**The book's own fit-window ratios at cut 2020**, each standardised for calendar year:

| level | book ratio | prior | weight w | multiplier used |
|---|---|---|---|---|
| fixed vs default | 0.64 | 2.80 | 0.93 | 0.79 |
| prepayment vs DD | 1.17 | 0.55 | 0.64 | 0.95 |
| standard credit vs DD | 1.02 | 1.02 | 0.66 | 1.02 |
| 36+ months on default vs under 36 | 0.97 | 0.54 | 0.08 | 0.57 |

**Attribution.** I ran each observable alone, the other two held at one. This is a diagnostic
added after the result was seen, not a prediction.

- **Months on default alone carries all the ranking.** Whole book: +0.069 at 2020 (just clears
  the bound), +0.068 at 2022, +0.157 at 2023. Switchers: +0.079, +0.067, and +0.127, which
  clears at 2023.
- **Tariff alone ranks worse beyond the bound** at 2020 (−0.128 whole book, −0.196 switchers)
  and at 2023 (−0.099 and −0.116).
- **Payment alone does nothing**: every difference is within ±0.015.

## Each prediction beside its result (wrong ones kept)

- **P1 (reachability): HELD.** All 772 accounts carry a view. At every cut, each observable has at
  least two levels among the graded accounts. At 2020 there are 89 fixed, 35 prepayment,
  33 standard credit and 50 at 36+ months. The control reaches every non-reference level in one
  fixture.
- **P2 (level held within 0.01): WRONG at every cut.** Mean per-customer p minus flat p is
  −0.081, −0.055 and −0.041. The prereg named the mechanism and it is the one that fired. The
  renormalisation holds over the fit window only, and months on default then advance across the
  horizon into the 0.57 band. The single-observable runs confirm it: months on default alone
  drifts by −0.085, −0.073 and −0.046, while tariff and payment alone drift by ≤0.02. **This is a
  defect in the rule as written.** The fix is to renormalise against the horizon's own
  advancing months, or to freeze the band at the cut. It is not made here: that would be a second
  variable on this grade.
- **P3 (directions in the book): one of three held.**
  - Fixed vs default: predicted >1, the book reads **0.64. WRONG.**
  - Prepayment vs DD: predicted <1, the book reads **1.17. WRONG.**
  - 36+ months vs under 36: predicted <1, the book reads **0.97. Held**, barely. It is 0.87 at 2022
    and 0.84 at 2023.

  The prereg's circularity caveat cuts the other way from how it was written: the world does
  *not* reproduce two of the published directions. Two readings are open, and I cannot yet say
  which:
  1. **The quantities differ.** The priors are SWITCHING over a six-month window. The book's
     hazard is all-cause per supplied month. A fixed account leaves at its term end, and
     prepayment homes may move more. The by-cause split could settle this, and it was not run.
  2. **The world departs from the published record.** The research note says the world carries
     these E correlates. This book does not show them in departures.
- **P4 (switchers rank better at ≥1 cut): WRONG.** Cannot tell at all three.
- **P5 (movers cannot tell at all three): WRONG at 2023**, where per-customer ranks movers better.
  The contract-year rule does too, so this is shared time-on-book, not a move signal.
- **P6 (whole-book AUC ≥ flat at every cut; bound cleared at 2020 only): the inequality HELD; the
  location of the bound was WRONG.** The bound cleared at 2023, not 2020.
- **P7 (stayer margin cannot tell at all three): WRONG.** Per-customer is better at 2020 and 2023
  and flat is better at 2022. These verdicts move with P2's level drift (more forecast survival
  gives more forecast margin), so they grade the drift, not knowledge, and are not read as
  either.
- **P8 (observables AUC > contract-year at 2020, point only): HELD.** 0.578 against 0.531.

**F11 reading.** Switchers never clear the bound. The only clear gains are shared with the old
key or come from one prior the book barely supports. The verdict is "cannot tell", without the
"leaning per-customer" the prereg allowed if P4 had held once.

## What it means for the thesis, said plainly

On this book, the observables a supplier holds and the published switching evidence keys on do
not separate leavers from stayers better than the segment average.

- The one key that ranks is **months on default**, and it ranks through its **prior**. With
  w ≈ 0.1, the book's own 0.84–0.97 barely moves it.
- **Tariff type ranks backwards** when keyed on the published direction.

Before a fresh-seed run is spent, this is the question that matters: does the world produce
the departure correlates the published record says real customers carry? If not, targeting by
observable is rigged to fail in this world, which is the director's 2026-10-08 worry approached
from the other side.

## What is landed

The census of channel F (`docs/design/wall_channel_census_baseline.json`) gains two ruled
crossings. They are recorded in its `last_freeze`: `account_state_log` and `bills` are read by
`forward_clv`, which is the same harness-side backtest as its three frozen reads. It feeds no
company decision.

- `company/analytics/forward_clv.py`:
  - `SupplierView` and `AccountHistory.observed`, filled by `book_from_run_output` from
    `account_state_log` and `bills[].payment_channel`;
  - `OBSERVABLE_PRIORS` (cited);
  - `observable_multipliers`, using the gamma-Poisson n/(n+k) with k read from each prior's range;
  - `run_backtest(observables=True)`.
- `tests/company/analytics/test_forward_clv_backtest.py`: three controls. Eight mutations each
  went red and the placebo stayed green:
  1. never fixed;
  2. no channel;
  3. the default count never advances;
  4. prior only (w = 0);
  5. book only (w = 1);
  6. k picked as 10;
  7. the key reaches nothing;
  8. the exit level read at the first month.

  Mutation 8 first survived. That was an equivalence in a fixture whose payment never changed; the
  fixture now exits past 36 months, and it reds.

## Next, in order (not done here)

1. **Split the book's fit-window ratios by cause.** Use the switch hazard with moves censored,
   which already exists in `_fit_hazards`. If fixed and prepayment still read against the
   published direction on switches alone, the world is the suspect: W2's engagement axis is
   carried into churn timing in a way that loses it. If they flip, the all-cause hazard is the
   wrong quantity for these priors.
2. **Fix the P2 level drift**, then re-grade the one key that ranks, months on default, alone.

## Addendum, after the landing: the next step's first leg, run (an unpredicted diagnostic)

The fit-window ratios were re-read by cause with the existing censoring, using
`observable_multipliers(..., censored=...)`. Moves were censored for the switch ratio, and
switches for the move ratio. No prediction was filed for this: it is a reading, not a test.

| level vs reference | switches, 2020 | switches, 2023 | moves, 2020 | moves, 2023 | published (switching) |
|---|---|---|---|---|---|
| fixed vs default | 0.77 | 0.82 | 0.38 | 0.40 | 2.80 |
| prepayment vs DD | 0.98 | 1.16 | 1.67 | 1.30 | 0.55 |
| standard credit vs DD | 1.18 | 1.33 | 0.60 | 0.65 | 1.02 |
| 36+ months on default vs under 36 | **0.68** | **0.50** | 1.68 | 1.35 | 0.54 |

The cell sizes are small. At 2020 the switch exits in the 36+ band number 7.

**What the split says, by observable.**

- **Months on default: reading 1.** On switches alone, the book reproduces CMOL's gradient
  (0.68, 0.50 against 0.54). Moves run the other way, and the all-cause ratio (0.97) was the two
  washing out. The months-on-default prior was right about switching. The hazard it multiplied was
  the wrong quantity for it.
- **Prepayment: mostly reading 2.** Moves inflate the all-cause ratio. Even so, on switches alone
  prepayment leaves at about DD's rate (0.98, 1.16), not the published 0.55. The world's payment
  factor sits on the active-renewal probability, but it does not show up in who switches away.
- **Fixed vs default: a candidate third reading, not yet tested.** In this world every account
  starts on a fixed term, so a "fixed" month is mostly a first-term month of every customer. In
  the published survey, a fixed-tariff household is one that chose to fix. The observable has the
  same name and selects a different population. The ratio is below one on both causes.

**What it changes.** The next grade should key the SWITCH hazard, not the all-cause one, on
months on default alone, after the P2 level fix, and grade it on switchers. Prepayment's missing
switch gradient is a world question for W2: does the engagement axis reach departure timing? It
is named here for the seat. This lane does not decide it.
