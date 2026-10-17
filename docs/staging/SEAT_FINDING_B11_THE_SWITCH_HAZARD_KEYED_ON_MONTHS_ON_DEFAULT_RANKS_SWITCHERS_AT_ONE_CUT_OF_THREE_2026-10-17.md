**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-slice-11-the-switch-hazard-keyed-on-months-on-default` (Lane 0 delivery)

# B11 slice 11: the switch hazard keyed on months on default ranks switchers better at one cut of three. Cannot tell, leaning the key; not yet for EP17's arm

**DEVELOPMENT.** One book, one seed: `docs/reports/run_output_latest.json` (run at `78f77c34e`,
772 accounts, 212 move-out rows), slice 10's book, read through `tools/run_output_store`.
Predictions filed and on origin before either change existed:
`docs/staging/records/SEAT_PREREG_B11_ELEVENTH_SLICE_THE_SWITCH_HAZARD_KEYED_ON_MONTHS_ON_DEFAULT_2026-10-17.md`
(`103afb271`).

## The answer

- **Step one, the level fix, alone.** Holding the view at the cut cuts slice 10's level drift by
  between half and two thirds. It does not close it: −0.030, −0.019 and −0.026 remain.
- **Step two, the switch key.** Switchers rank better than flat beyond the 95% bound at 2023 only
  (+0.103, lower bound +0.002). They cannot be told from the contract-year rule at any cut.
  **Cannot tell, leaning the key** (F11). By the prereg's rule the key does **not yet** go into
  EP17's arm. EP17's fresh-seed verdict stays the director's open row.

## Step one: freeze the band at the cut (slice 10's all-three-observables rule, graded alone)

HEAD's advancing rule and the frozen rule ran in one process on one book. HEAD reproduces slice 10
to the digit.

| cut | graded | mean p_pc − p_flat, advancing (slice 10) | frozen | whole-book AUC difference vs flat, advancing → frozen |
|---|---|---|---|---|
| 2020 | 253 | −0.081 | **−0.030** | +0.039 → **−0.047** (both cannot tell) |
| 2022 | 256 | −0.055 | **−0.019** | +0.082 → +0.071 (both cannot tell) |
| 2023 | 266 | −0.041 | **−0.026** | +0.130 → +0.099 (both ranks better) |

- **S1a (|drift| smaller at all three cuts): HELD.**
- **S1b (not within 0.01 at 2020, negative at all three): HELD.** The rest of the drift comes from
  the rescale. `c_segment` is fitted over a window whose band mix is not the cut's. At 2020, 50 of
  253 graded accounts are 36+ at the cut, and 36+ months are rare across the fit window. Freezing
  is necessary but not sufficient. A second fix (rescale over the cut's own mix) is not made here.
- **Unpredicted, kept:** freezing moved the whole-book ranking at 2020 from +0.039 to −0.047. So at
  2020, part of slice 10's ranking came from accounts crossing the band over the horizon, not from
  their band at the cut. Both readings straddle zero.

## Step two: the switch hazard keyed on months on default alone, band frozen

The rule is `h_move,seg + c_seg · M(band at cut) · h_switch,seg`, with the move part flat. `M` is
the CMOL 0.54 prior (range 0.44–0.66), shrunk to the book's switch ratio with moves censored.

| cut | 36+ at cut / graded | book switch ratio (obs / exp) | w | M used | level p_pc − p_flat |
|---|---|---|---|---|---|
| 2020 | 50 / 253 | 0.685 (7 / 10.1) | 0.055 | 0.548 | −0.024 |
| 2022 | 86 / 256 | 0.554 (10 / 17.6) | 0.092 | 0.541 | −0.028 |
| 2023 | 114 / 266 | 0.500 (11 / 21.2) | 0.109 | 0.536 | −0.025 |

AUC difference, each paired with the existing DeLong 95% interval on the same accounts:

| cut | outcome | n | key − flat | verdict | key − contract-year | verdict |
|---|---|---|---|---|---|---|
| 2020 | switchers | 63 | +0.017 (−0.034, +0.068) | cannot tell | +0.027 (−0.040, +0.093) | cannot tell |
| 2020 | movers | 44 | +0.036 (−0.024, +0.096) | cannot tell | +0.042 (−0.042, +0.127) | cannot tell |
| 2020 | whole book | 107 left | +0.025 (−0.019, +0.069) | cannot tell | +0.033 (−0.025, +0.092) | cannot tell |
| 2022 | switchers | 35 | +0.036 (−0.058, +0.130) | cannot tell | +0.056 (−0.040, +0.153) | cannot tell |
| 2022 | movers | 25 | +0.037 (−0.056, +0.129) | cannot tell | −0.075 (−0.177, +0.026) | cannot tell |
| 2022 | whole book | 60 left | +0.036 (−0.035, +0.108) | cannot tell | +0.002 (−0.075, +0.078) | cannot tell |
| 2023 | switchers | 30 | **+0.103 (+0.002, +0.205)** | **key ranks better** | +0.075 (−0.024, +0.174) | cannot tell |
| 2023 | movers | 19 | **+0.179 (+0.090, +0.269)** | **key ranks better** | −0.008 (−0.127, +0.111) | cannot tell |
| 2023 | whole book | 49 left | **+0.133 (+0.056, +0.209)** | **key ranks better** | +0.043 (−0.038, +0.123) | cannot tell |

Switcher AUCs (key / flat / contract-year): 0.611 / 0.593 / 0.584 at 2020; 0.540 / 0.504 / 0.484 at
2022; 0.587 / 0.484 / 0.512 at 2023. **Flat ranks switchers below chance at 2022 and 2023.** The
segment key points the wrong way there, so part of the key's "gain" at 2023 is that it overrides
a segment ordering that is itself backwards.

### Each prediction beside its result (wrong ones kept)

- **S2a (both bands graded; M strictly between the book ratio and 0.54): HELD** at all three cuts.
- **S2b (switchers vs flat positive at all three, beyond the bound at 2023 only): HELD.** The
  bound clears by +0.002, which is as thin as a clear can be.
- **S2c (switchers vs contract-year cannot tell at all three, positive at 2020): HELD.**
- **S2d (movers cannot tell at all three, negative point at 2020): WRONG twice.** At 2020 the
  point is +0.036. At 2023 the key ranks movers better beyond the bound. The 1.68 move ratio for
  the 36+ band in the fit window did not carry into the held-back movers. The 2023 mover gain
  matches slice 10's (+0.196) and the contract-year rule's (+0.187), and the key's mover AUC
  equals contract-year's (−0.008). That points to time on book shared by both rules, not a move
  signal.
- **S2e (level negative at every cut, by less than step one's): negative HELD; "by less" WRONG at
  2022** (−0.028 against −0.019). It held at 2020 (−0.024 against −0.030) and only just at 2023
  (−0.025 against −0.026).

### The EP17 rule, applied as written

1. Switchers better than flat beyond the bound at two or more cuts: **no**, only at 2023.
2. No outcome worse than flat beyond the bound at any cut: yes.
3. Switchers not worse than contract-year beyond the bound at any cut: yes.

The first condition fails, so the recommendation is **not yet**.

## What it means, said plainly

Months on default is a key a real supplier holds. Keyed where its prior belongs, on the switch
hazard, it orders switchers the published way at every cut. Only once does it order them well
enough to beat a segment average this sample can bound: 30 switchers at 2023. Against the
contract-year rule it never separates. That is the same quantity seen another way: in this world
every account opens on a fixed term, so months on default and time on book are close to the same
number.

The open questions are not answered by more grading on this book:
- whether the key's rank survives a **fresh seed** (the director's EP17 row);
- whether a world that, unlike this one, lets accounts **open on the default** pulls months on
  default apart from tenure. This is a W2/population question for the seat, not this lane.

## What is landed

`company/analytics/forward_clv.py`:
- the view is held at the cut over the horizon (the fix);
- `run_backtest(switch_on_default=True)` keys the switch part only, needs the register, and is
  refused beside `observables`;
- `observable_multipliers(only=...)`;
- `ranking_between(a, b, outcome)`, which pairs two rules' per-customer p on one partition with
  DeLong's covariance, through the same `_paired_auc` that `_ranking` now calls;
- `Backtest.outcome_of`.

`tests/company/analytics/test_forward_clv_backtest.py` adds three controls. These named
mutations each went red, and a placebo comment stayed green:

| mutation | went red in |
|---|---|
| restore the advancing months | the freeze control |
| drop the move censoring | the switch control |
| prior only, w = 0 | the multiplier control |
| the key reaches nothing | the switch control |
| key the all-cause hazard | the switch control (the every-exit-a-move book) |
| drop the DeLong covariance | the pairing control (a rule against itself) |

## Next, in order (not done here)

1. If the level matters to the next grade, rescale `c_segment` over the cut's own band mix. That
   is the remainder of S1b.
2. Raise with the seat whether a population where some accounts open on the default is a fidelity
   change W2 owes. A real book does not open every customer on a fix.
