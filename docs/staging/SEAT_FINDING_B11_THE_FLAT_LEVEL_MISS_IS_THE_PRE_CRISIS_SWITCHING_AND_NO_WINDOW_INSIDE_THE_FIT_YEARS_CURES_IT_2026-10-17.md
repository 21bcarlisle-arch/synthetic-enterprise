**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `B11_forward_clv_backtested_on_held_back_history` (parked; row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `b11-slice-13-why-the-flat-switch-level-over-predicts-held-back-departure` (Lane 0 delivery)

# B11 slice 13: the flat level's miss is the pre-crisis switching, and no window inside the fit years cures it

**DEVELOPMENT.** This is one book and one seed: `docs/reports/run_output_latest.json`, slice
10–12's book (772 accounts), copied from the shared tree. The predictions were written before
anything was read:
`docs/staging/records/SEAT_PREREG_B11_THIRTEENTH_SLICE_WHY_THE_FLAT_SWITCH_LEVEL_OVER_PREDICTS_HELD_BACK_DEPARTURE_2026-10-17.md`.
The control is that, in the same process, the default window reproduces slice 12's flat calibration
to the digit: +0.241 / +0.181 / +0.072. Each figure comes from `backtest_run_output(book, cut,
hazard_fit_from_year=…)` at `51ec26010`, with no code changed.

## The answer

- **The miss is switching, and it is the pre-crisis years' switching.** The switch term carries
  83–95% of the flat over-prediction at every cut. The move term's interval holds zero at every
  cut. At all three cuts, the 2017–2020 years alone carry more than the whole excess switch hazard.
- **Slice 12's premise is corrected here.** It said "the fit window holds the 2021–22 crisis
  exits". At cut 2020 the window holds no 2021–22 month. At the later cuts 2021 sits above the
  held-back switch rate and 2022 below it, and together they contribute about zero: −0.0001 of a
  +0.0074 excess at 2022, and −0.0002 of +0.0056 at 2023. The crisis years neither carry the miss
  nor offset it.
- **The window that starts after the crisis does not cure it. It flips the sign.** At cut 2023 the
  window from 2023 gives a flat calibration of **−0.089 (−0.136, −0.043)**, against +0.072 for the
  full window. That is a larger miss in the other direction. 2023 was the trough, and 2024–25
  switching recovered. The move term goes negative under it too (−0.027), because 2023 was also a
  low-move year.

## The book by calendar year (every account on supply; per account-month)

| year | months at risk | switch rate | move rate |
|---|---|---|---|
| 2016 | 2,697 | 0.0037 | 0.0063 |
| 2017 | 4,665 | 0.0178 | 0.0043 |
| 2018 | 4,041 | 0.0173 | 0.0047 |
| 2019 | 3,489 | 0.0152 | 0.0077 |
| 2020 | 3,192 | 0.0160 | 0.0056 |
| 2021 | 2,967 | 0.0084 | 0.0061 |
| 2022 | 2,994 | **0.0010** | 0.0043 |
| 2023 | 3,105 | 0.0035 | 0.0026 |
| 2024 | 3,244 | 0.0052 | 0.0059 |
| 2025 (to June) | 1,654 | 0.0067 | 0.0024 |

This is the same shape as slice 6's book, to the second figure in most years.

## The excess hazard by fit-window year

The table uses the identity h_fit − h_hb = Σ_y w_y (h_y − h_hb). It is pooled over segments and
counts switches only. Each term is year y's contribution to the excess.

| cut | h_fit | h_hb | excess | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020 | 0.0148 | 0.0048 | +0.0100 | −0.0002 | +0.0034 | +0.0028 | +0.0020 | +0.0020 | | | |
| 2022 | 0.0123 | 0.0049 | +0.0074 | −0.0001 | +0.0025 | +0.0021 | +0.0015 | +0.0015 | +0.0004 | −0.0005 | |
| 2023 | 0.0113 | 0.0057 | +0.0056 | −0.0002 | +0.0021 | +0.0017 | +0.0012 | +0.0012 | +0.0003 | −0.0005 | −0.0002 |

Each row's terms sum to its excess exactly. In the same identity the move excess is
+0.0011 / +0.0016 / +0.0005, a tenth to a fifth of the switch excess.

## The miss by cause (flat rule, full window)

| cut | all-cause | switch (95%) | move (95%) | switch share |
|---|---|---|---|---|
| 2020 | +0.241 | +0.229 (+0.176, +0.282) | +0.012 (−0.035, +0.059) | 95% |
| 2022 | +0.181 | +0.151 (+0.109, +0.193) | +0.030 (−0.007, +0.066) | 83% |
| 2023 | +0.072 | +0.063 (+0.025, +0.101) | +0.009 (−0.022, +0.040) | 88% |

## The window: the one variable (cut 2023) and three readings

| cut | hazard window | flat calibration (95%) | switch | move | per-customer |
|---|---|---|---|---|---|
| 2023 | 2016–2023 (default) | +0.072 (+0.025, +0.119) | +0.063 | +0.009 | +0.007 |
| **2023** | **2023 only: the one variable** | **−0.089 (−0.136, −0.043)** | −0.062 | −0.027 | −0.081 |
| 2023 | 2022–2023 (reading) | −0.090 (−0.137, −0.044) | −0.078 | −0.012 | −0.086 |
| 2023 | 2021–2023 (reading) | −0.043 (−0.090, +0.004) | −0.043 | −0.000 | −0.060 |
| 2022 | 2016–2022 (default) | +0.181 (+0.129, +0.233) | +0.151 | +0.030 | +0.037 |
| 2022 | 2021–2022 (reading) | +0.016 (−0.036, +0.068) | −0.018 | +0.034 | −0.054 |
| 2022 | 2022 only (reading) | −0.103 (−0.155, −0.051) | −0.118 | +0.015 | −0.094 |

The readings were not predicted and are not graded. The window that opens in 2021 lands inside
its interval at both cuts. **It is not adopted.** It was chosen after its answer was seen. Its
success depends on 2021's eight good switching months balancing 2022's collapse, and that balance
belongs to this one regime turn. It is not a property a supplier could have known at the cut.

## Each prediction beside its result

- **D1 (switch ≥ 80% of the miss; move interval holds zero, every cut): HELD.** The switch share
  is 95% / 83% / 88%, and every move interval holds zero.
- **D2 (2017–2020 each above the held-back switch rate; 2016 not, with its term negative): HELD.**
  2016's switch rate is 0.0037 against 0.0048 held back, and its term is −0.0002.
- **D3 (the 2021 and 2022 terms sum negative at 2022 and 2023; 2022 is the lowest year): HELD on
  sign only, and that is weaker than it reads.** The sums are −0.0001 and −0.0002, which is about
  zero against the excess. 2021 alone sits ABOVE the held-back rate. "Pull the level down" was
  wrong in magnitude: the pair is neutral. F11 applies, so I record this as "the crisis years do
  not carry the miss", not "they offset it". 2022 is the lowest year, at 0.0010.
- **D4 (2017–2020 carry more than the whole excess at 2022 and 2023): HELD.** At 2022 they carry
  +0.0076 of +0.0074, and at 2023 +0.0062 of +0.0056.
- **W1 (window from 2023 at cut 2023: negative, point in [−0.10, −0.01]): HELD** at −0.089.
- **W2 (|calibration| ≥ 0.04, no cure): HELD.** It is 0.089, larger than the full window's 0.072.

## What it means

1. **The flat level is a mean over a regime that ended.** Four pre-crisis years switched at three
   to four times the post-crisis rate. Every window that holds them over-predicts. Every window
   that holds only the trough under-predicts. A window chosen from inside the fit years cannot know
   which regime the held-back years will be in, so **the level is not identified by the book at
   the cut.** This is the same conclusion as slices 6 and 7, now on a second book with the
   decomposition by year added.
2. **The two windows bracket the realised rate here, and that is a reading, not a method.** At
   cuts 2022 and 2023, the full window and the cut-year-only window bracket what happened. A
   two-window band would have held the truth at both. At 2020 it would not have: every pre-cut year
   switched far above the held-back rate. A band read from the fit years fails at the one cut
   where the regime turns after the cut. That is when a forecast is needed most.
3. **For any per-customer LEVEL used for margin or CLV:** the switch term must carry a regime
   band from outside the book, for example the published GB switching record by year. The move
   term can be taken as fitted, as in slice 7. No fit-window choice substitutes for that. It is a
   design choice for the level's first consumer. Nothing consumes the level today
   (`company/crm/next_best_action.py` borrows only the paired comparison), so nothing is owed now.
4. **The ranking verdict (EP17) is untouched.** A window moves every segment's hazard by one
   factor, so it moves the level, not the order. EP17's fresh-seed verdict is still the director's
   open row.

## Landed

This file and the pre-registration. **No code changed.** The prereg's decision rule allowed
sharpening the `LIMITATION_SWITCH_LEVEL_IS_THE_REGIME` wording. I did not do it. The existing
wording is still true. The string is also rendered into `saas/reporting/annual_report.py`'s held-back
section, so rewording it would move a published surface, and this one-book result does not earn
that.

## The book's switching against the published record (added after landing; not pre-registered)

*Corrected beside the claim: this section first read "research the GB switching record by year".
That record was already in the knowledge map's "Switching rates" row: DESNZ QEP table 2.7.1, over
all GB domestic electricity accounts.* The book's switch rate is annualised as 1 − (1 − h)^12:

| year | book | published | ratio |
|---|---|---|---|
| 2016 | 4.4% | 15.82% | 0.28 |
| 2017 | 19.4% | 18.20% | 1.06 |
| 2018 | 18.9% | 19.06% | 0.99 |
| 2019 | 16.8% | 20.82% | 0.81 |
| 2020 | 17.6% | 20.21% | 0.87 |
| 2021 | 9.7% | 15.57% | 0.62 |
| 2022 | 1.2% | 3.06% | 0.39 |
| 2023 | 4.2% | 6.33% | 0.66 |
| 2024 | 6.1% | 9.03% | 0.68 |
| 2025 (to June) | 7.7% | 10.40% | 0.74 |

**The regime the flat level misses is the GB record's own regime, and the world reproduces its
shape.** Across 2017–20 the book sits at 0.8–1.1× the record. From 2021 on it sits at 0.4–0.7×. So
the world's post-crisis trough is about 1.4× deeper than the record's, relative to its pre-crisis
level: a post/pre ratio of 0.25 in the book against 0.37 in the record. 2016 is low because the
book was founded that year, and a first-year fixed-term book has little to switch out of. The
second effect, the deeper trough, makes the slice's level miss larger than a supplier on the real
record would have seen. It does not change the miss's direction or its cause. The knowledge map
already carries the world's departure level against this record as a separate, open subject ("The
world's departure LEVEL" row), so nothing new is filed for it here.

## Next (not done here)

- **Company side.** A switch-term level that carries a regime band from the published record, as
  the record stood at the cut, is the candidate design. It would have to reach the company as an
  observable through `company/interfaces/sim_interface.py`, never as a fetched runtime input (W6).
  It waits for the level's first consumer.
