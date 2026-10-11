**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history`

# Pre-registration: B11 slice 7, the departure level at later cuts and split by cause

Written 2026-10-11, before any backtest at cut 2022 or 2023 and before any cause-separated
calibration had been computed. Claim `b11-later-cut-and-regime-caveated-departure`. It lands in the
same commit as the code that measures the cause split, and that commit precedes the measurement.
Results go in a separate finding. This file is not edited after the run.

## The run and what is already known

`/var/tmp/b11s5_run/run_output_b11s5.json` (run at `3f1ebfac3`, home moves on), as slices 5 and 6.
At cut 2020 the flat rule's calibration is +0.241 (+0.180, +0.303) and per-customer's +0.361.
Slice 6's calendar-year table is the input to every number below. The numbers are arithmetic on
that table, which counts every account on supply. They are not measurements on the graded cohort,
so a cohort that churns differently from the book will move them.

## Predictions

The flat rule's pooled hazard over the fit window, applied for the held-back horizon, against the
held-back pooled rate over the same horizon:

| cut | horizon | fit rate | held-back rate | flat p | realised | miss |
|---|---|---|---|---|---|---|
| 2020 | 54 | 0.0205 | 0.0096 | 0.673 | 0.407 | +0.27 |
| 2022 | 30 | 0.0180 | 0.0091 | 0.420 | 0.241 | +0.18 |
| 2023 | 18 | 0.0166 | 0.0110 | 0.261 | 0.181 | +0.08 |

The cut-2020 row is a check of the method against a known answer: the measured flat miss is +0.241,
so the arithmetic runs about 0.03 high there.

- **P1. Cut 2022, flat:** calibration between +0.12 and +0.24, and its interval excludes zero.
  This is slice 6's point 3.
- **P2. Cut 2023, flat:** calibration between +0.03 and +0.13. Its interval is predicted to exclude
  zero, but narrowly enough that "cannot tell" is the likeliest way this prediction fails.
- **P3. Per-customer stays above flat at both cuts.** The tenure table's oldest contract years
  carry 2017–2019's churn, which is the slice-6 shape.
- **P4. Neither rule ranks at either cut:** the paired AUC difference is "cannot tell".

## The cause-separated level

New code: the flat rule's segment hazard split into a switch hazard (moves censored) and a move
hazard (switches censored), both on the fit window. Each graded account gets a cumulative incidence
of switching and of moving over the horizon, as competing risks. The two incidences sum to the flat
all-cause p by construction. Each is graded against the realised share of graded accounts that
switched and that moved.

Arithmetic on the table, for the competing-risk incidences:

| cut | switch predicted | switch realised | move predicted | move realised | switch ratio | move ratio |
|---|---|---|---|---|---|---|
| 2020 | 0.489 | 0.220 | 0.184 | 0.186 | 0.35 | 0.79 |
| 2022 | 0.289 | 0.147 | 0.130 | 0.094 | 0.45 | 0.64 |
| 2023 | 0.179 | 0.110 | 0.082 | 0.072 | 0.59 | 0.84 |

- **P5. At cut 2020 the switch term carries the whole miss.** Switch calibration is at least +0.15
  and its interval excludes zero. Move calibration is within ±0.06 and its interval includes zero.
- **P6. At cut 2022 the switch term carries most of the miss.** The switch miss is at least 2× the
  move miss. 2023's move rate, 0.0023, is the lowest in the record, so the move term may also miss
  here; its interval is predicted to include zero.

## What would refute the slice-6 reading

If at cut 2020 the move term misses as much as the switch term, the "move hazard transferred"
claim in slice 6's point 4 is wrong, and a cause-separated survival carries no less regime risk than
the all-cause one. If at cut 2023, which includes the collapse in its fit window, the flat level is
inside its interval, then the level can be fitted once the regime is in view, and the caveat should
say "until the regime is in the fit window" rather than "always".

## Decision rule, written before the run

- If P5 holds, the departure level is published as two terms. The move term is stated as the part
  that transferred. The switch term carries the caveat that its level is regime-dependent, with
  the cut-2020 miss as the evidence. No calibrated constant replaces either term.
- If P5 fails, the level is published all-cause, with a regime caveat on the whole of it.
