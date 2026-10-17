**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Claim:** `b11-slice-12-rescale-the-observable-key-over-the-cuts-own-band-mix` (Lane 0 delivery)

# Pre-registration: B11 slice 12, rescale the per-customer key over the cut's own mix

Written 2026-10-17 at origin `e3cd17232`, before the change exists. Not edited after the run;
results go in a separate finding, each graded beside its prediction here.

**Known and therefore NOT predicted.** Slice 11's finding
(`docs/staging/SEAT_FINDING_B11_THE_SWITCH_HAZARD_KEYED_ON_MONTHS_ON_DEFAULT_RANKS_SWITCHERS_AT_ONE_CUT_OF_THREE_2026-10-17.md`):
on this book, with the view frozen at the cut, mean p_pc − p_flat is −0.030 / −0.019 / −0.026 for
the all-three-observables rule and −0.024 / −0.028 / −0.025 for the switch key, at cuts
2020 / 2022 / 2023, and its AUC table.

## The one variable

Today `c_segment` (the per-segment `seg_scale`) makes each segment's fit-window MONTHS average a
key of one. The change: it makes each segment's accounts ON SUPPLY AT THE CUT average a key of one,
each at its view at the cut. Everything else is held: the multipliers (still fitted on the window),
the frozen view, the flat hazard, the horizon. The cut's on-supply population and its views are
what a supplier holds at the cut, so no held-back month is read.

By construction the cut population's mean MONTHLY hazard then equals the flat rule's in each
segment (the switch part's, for the switch key). What can remain is not a hazard level: it is the
concavity of p = 1 − Π(1 − h) over the horizon (a spread of hazards with the flat mean gives a
lower mean p), plus the `min(1, h)` clamp. So a residual is EXPECTED and is negative.

## The book

`docs/reports/run_output_latest.json` read through `tools/run_output_store` from the shared tree
(slice 10/11's book, run at `78f77c34e`, 772 accounts). Cuts 2020, 2022, 2023. One book, one seed:
**DEVELOPMENT.** Control first: the fit-window rule reproduces slice 11's levels to the digit in
the same process, or nothing below is read.

## Predictions

- **R1 (observables, level).** Mean p_pc − p_flat is negative at all three cuts and strictly
  smaller in magnitude than slice 11's frozen −0.030 / −0.019 / −0.026.
- **R2 (observables, how small).** Within 0.01 at 2022 and 2023; NOT within 0.01 at 2020, whose
  horizon is the longest (60 months), so the concavity term is largest there.
- **R3 (switch key, level).** Negative at all three, strictly smaller in magnitude than
  −0.024 / −0.028 / −0.025, and within 0.01 at all three: only the switch part is spread, and the
  key has one multiplier near 0.54.
- **R4 (ranking moves little).** A per-segment constant cannot reorder accounts within a
  segment, only across them. Switch key, switchers vs flat: the AUC difference moves by under
  0.02 at every cut against slice 11's +0.017 / +0.036 / +0.103.
- **R5 (EP17).** The rule in slice 11's prereg still reads "not yet" (switchers beyond the bound
  against flat at fewer than two cuts). No outcome turns worse than flat beyond the bound.

Calibration in the large (mean p − realised rate) for flat, fit-window and cut rescale is reported
beside the levels and NOT predicted: matching the flat level is the grade asked for; whether the
flat level is itself right is a separate question (slice 6 found both rules over-predict).

**F11.** A level within 0.01 is "level-honest against flat", never "level-honest".

## Controls, named before they are written

- Over the cut's population each segment's mean key at the cut is one; over the fit window it is
  not (a book whose cut mix differs from its window mix). Mutation: rescale over the window
  regardless of the argument → red.
- An unknown `rescale_over` is refused with its reason; `rescale_over="cut"` without a key is
  refused (nothing to rescale).
