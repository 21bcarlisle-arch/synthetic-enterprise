# Pre-registration: C35's retention rise through the company's own code, at both B11 hazard ends

**Written 2026-10-17, before any code for the rise exists.** Claim `c35-the-share-travels-as-a-retention-tariff-rise`
(Lane 0). Knowledge: `docs/market_research/a_retention_price_that_shares_the_value_an_action_creates.md` §§2–4b.
DEVELOPMENT.

## What is being built, and how it differs from §4b's count

§4b counted rescues with the WORLD's inputs: each renewal's true P(stay), and the rate a stayer is
actually billed. This build gives the company the same decision using only what it holds:

- **margin:** the renewal's own flat margin, (offer − cost floor) × annual MWh / 12. These are the
  company's figures, the same as §4b.
- **hazard:** the per-account departure p from `company/analytics/forward_clv.py`, turned into a
  constant monthly hazard as `1 − (1 − p)^(1/held-back months)`. It is read at the two ends slice 13
  brackets: the full fit window, and the cut-year window (`hazard_fit_from_year = cut`). The cut is
  the year before the renewal, floored at 2016.
- **staying response:** the page's published slope, 0.0015 P(stay) per £/yr (Deller et al. 2021),
  which adds 0.0015·d to the monthly hazard for a rise of £d a month.
- **cap:** the headroom under the default as the company sees it. That is the published default
  (`company.crm.save_offer.published_default_rate_ex_vat`, ex VAT, EPG-net) minus the company's own
  Fixed Retention Tariff offer, × annual MWh / 12. **Before 2019 no per-fuel default was published.**
  That is a GAP the company holds, so the rise fails closed there.
- **floor:** ours ≥ 0 with the hazard held, and also with the slope applied. Requiring both refuses
  the §4b trap: a "rise" that reaches zero only by driving a loss-making account away. The household
  is no worse off: the rise paid over its expected supplied months is at most its benefit over the
  horizon.

## Predictions

The book is the published book (`docs/reports/run_output_latest.json`, 772 accounts). The renewals
are §4b's 260 (192 accounts): 136 start before 2019 (2016: 3, 2017: 99, 2018: 34) and 124 from 2019.

- **R1.** All 136 pre-2019 renewals are refused, with the GAP named in the reason, at both ends.
  This holds by construction. It is filed so that the difference from 314 is accounted for before it
  is seen.
- **R2.** On the 124 renewals from 2019, for each effect, the company's count at each hazard end is
  within ±8 of §4b's world-arm count on the same renewals. The reason: the count is decided by
  headroom, and the company's default and the world's are the same published cap except through the
  EPG, where only 2023 renewals fall.
- **R3.** Summed over the three effects, the two hazard ends differ by at most 10 cases.
- **R4.** The total at each end is 170–215 of 780. That is below 314, and R1 is the reason.
- **R5.** At both ends, the median rise needed is within £0.25 a month of what the advice gives up,
  for each effect.
- **R6.** Every rescued case clears the household's floor.
- **R7.** The forward_clv monthly hazard sits below the world's (1 − P(stay))^(1/12) reading at the
  median: §4b's h0 median was 4.1% a month. The prediction is a full-window median between 1.0% and
  2.5% a month.
- **R8.** At cuts 2021–2023 the cut-year window's median hazard is below the full window's. At cuts
  2018–2019 the two are within 30% of each other.
- **R9.** With the switch off, `decide` returns byte-identical decisions on a fixture book, with or
  without renewal terms on the accounts.

## Results, graded beside each prediction (2026-10-17, same day, after the code)

The instrument is `python3 -m tools.retention_rise_count /var/tmp/retention_rise/probe_default.json`.
The probe file is §4b's, and it is not in the tree. In the same process, the §4b script (`per_renewal.py`) reproduces **314 / 780**. That
is the control.

| effect | full window | cut-year window | from 2019: company / §4b world arm | median rise £/mo |
|---|---|---|---|---|
| £2, 0.1 pt | 71 / 260 | 71 / 260 | 71 / 71 | 2.03 |
| £2, 0.3 pt | 71 / 260 | 71 / 260 | 71 / 71 | 2.00 |
| £3, 0.3 pt | 69 / 260 | 69 / 260 | 69 / 68 | 3.03 |
| **all** | **211 / 780** | **211 / 780** | 211 / 210 | |

- **Refusals** (both ends): 408 for no published default (= 136 × 3), 158 for a rise above the headroom
  under the default, and 3 where the advice needs no rise.
- **Not one refusal is on the household floor**, and none is on a rise the slope cannot pay for.
- **The household keeps** a median 40% of its gross benefit (full window) and 38% (cut-year window).
  §4b gave 53–54%. The company's hazard is lower than the world's, so the household is expected to
  pay the rise for more months.
- **By year, effect (£2, 0.3 pt):** 2016 0/3, 2017 0/99, 2018 0/34, 2019 20/28, 2020 39/40,
  2021 4/29, 2023 0/2, 2024 3/10, 2025 5/14.
- **The hazard at both ends** (median monthly, full / cut-year), by cut:

  | cut | full | cut-year |
  |---|---|---|
  | 2016 | 0.0072 | 0.0072 |
  | 2017 | 0.0306 | 0.0297 |
  | 2018 | 0.0157 | 0.0156 |
  | 2019 | 0.0226 | 0.0206 |
  | 2020 | 0.0251 | 0.0206 |
  | 2022 | 0.0094 | 0.0039 |
  | 2023 | 0.0112 | 0.0048 |
  | 2024 | 0.0103 | 0.0102 |

  The median over the renewals is 0.0157 (full) and 0.0156 (cut-year).

- **R1 HELD.** All 408 pre-2019 cases are refused, with the GAP named.
- **R2 HELD, more tightly than predicted.** From 2019 the counts are 71/71, 71/71 and 69/68: within
  1, against a ±8 bound.
- **R3 HELD, at its extreme.** The two ends differ by 0 cases. The hazard moves the rise (and so what
  the household keeps) but not whether a case is rescued.
- **R4 HELD.** 211 is inside 170–215.
- **R5 HELD.** The medians are 2.03, 2.00 and 3.03, against 2, 2 and 3.
- **R6 HELD, and it is weaker than it reads.** Every rescue clears the floor by construction, and no
  case was refused on it.
- **R7 HELD.** The full-window median is 0.0157, inside 1.0–2.5%. That is about a third of the
  world's 4.1%.
- **R8 HELD where gradable.** There is no cut 2021, because no renewal starts in 2022. At cuts 2022
  and 2023 the cut-year window is lower (0.0039 against 0.0094, and 0.0048 against 0.0112). At 2018
  and 2019 the two ends are within 10%. **Not predicted:** cut 2020 is 18% lower on the cut-year
  window too.
- **R9 HELD.** The default-off `decide` gives byte-identical reprs to origin/main's on a fixture book,
  with and without renewal terms (`/var/tmp/retention_rise/byte_identical.py`).

**The difference from 314, explained.** 314 − 211 = 103:

- **104** are the world arm's rescues on renewals before 2019. The world bills a stayer against its
  own default table there. The company holds no published per-fuel default for those years, so it
  refuses (the §4c GAP).
- **1 case the other way.** PROS-2019-0008 is an electricity renewal on 2020-01-16. At both ends the
  company rescues it with a £3.03 rise against its own headroom of £3.23 a month; the world arm does
  not. **I cannot yet say why.** Two candidates fit and neither has been checked. The world's default
  for that date may sit within £0.20 a month of the published one. Or the world arm's grid
  interpolation of what a stayer pays may fall short of a £3.03 rise.

**One input choice, stated.** The hazard cut is clamped at the account's own hazard, `min(c, h)`, so
the hazard with the action never goes negative. That touches 6 cases on the full window and 9 on the
cut-year window. None of them is rescued with or without the clamp, so it moves no count.
