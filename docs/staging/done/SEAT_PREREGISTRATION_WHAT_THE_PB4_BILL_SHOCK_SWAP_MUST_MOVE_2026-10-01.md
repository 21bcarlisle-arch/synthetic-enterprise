**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: what swapping the bill-shock base onto the experienced shock must move

**Filed 2026-10-01 before either capture ran.** Claim `swap-pb4-bill-shock-base-onto-the-experienced-shock`.

## The change

`customer_events._bill_shock_base` was `1 - effective_retention_probability`, i.e.
`churn_probability(k) * (1 - win)` with `k` = shocked MONTHS in the 12 before the renewal. It is now
`churn_probability(1 if experienced shock else 0) * (1 - win)`, passive cap unchanged. One event per
year. The old base rides on the event as `sim_month_count_bill_shock_base`.

## The pair

A = `origin/main` `e9b79073d`, B = A + the swap. Same seed, same anchor block, captured with
`tools/capture_departure_factors.py`. Then fit B (`fit_whole_book`), capture C under the new block.

## Predictions

1. **Base level falls at tenure 2+, rises a little at tenure 1.** Old: 0 shocked months at tenure 1
   against 6.86 later, so base ≈ 0.05 vs ≈ 0.25 (before the win leg). New: about 3/31 shocked at a
   first renewal and 21/63 later, so ≈ 0.053 vs ≈ 0.060. The mean renewal-route `sim_bill_shock_base`
   in B is under half of A's.
2. **The tenure gradient of the base almost vanishes.** In B the tenure-2+ to tenure-1 ratio of mean
   base is under 1.3. In A it is over 3.
3. **Renewal-route expected departures fall in every fitted year in B**, because `bill_shock_base`
   is one of the three hazards the anchor multiplies. The SVT route is unchanged, because it is built
   with `bill_shock_base=0.0`. **So the whole-book expected rate in B is below A in every fitted
   year**, and the refit raises all seven anchors.
4. **Headline company result:** fewer departures is a stickier book, so B's net margin may rise
   over A's. That is a change of the world, not of the company. It is reported, not targeted.
   C's margin falls back from B's.
5. **The band test (`test_the_worlds_realised_departure_rate_is_inside_the_published_band`) stays
   XFAIL.** Its subject is the renewal-route mean, which is a selected shopping population. The
   anchor is fitted to the whole book. A whole-book refit cannot put the renewal route inside a
   whole-market band, and it should not be made to.

## Added 2026-10-01 after A and B were read and before C ran

6. **C, the capture under the refitted block, lands the whole book inside its published band in at
   least 4 of the 6 refitted years** (2017-2021 and 2024). The fit is exact on B and approximate on
   C, because raising the level changes who is on the book. 2023 stays out low, as it is on A. 2022
   stays unfitted.
7. **C's renewal-route mean base matches B's within 0.005.** The anchor does not touch the base.

## A and B, graded (captured 2026-10-01, `e9b79073d` ± the swap, default seed)

| | A (month count) | B (one event a year) |
|---|---|---|
| renewal rows / SVT decisions | 108 / 2,031 | 115 / 2,142 |
| mean base, first decision in the capture | 0.0685 | 0.0257 |
| mean base, later decisions | 0.1000 | 0.0262 |
| later / first | 1.46 | 1.02 |

Whole book, expected departures over accounts, under the live block:

| year | target | A | B |
|---|---|---|---|
| 2017 | 14.00 | 14.39 | 14.32 |
| 2018 | 20.00 | 19.51 | 16.67 |
| 2019 | 21.30 | 24.65 | 19.59 |
| 2020 | 23.00 | 22.84 | 17.23 |
| 2021 | 18.40 | 15.87 | 14.17 |
| 2023 | 12.50 | 9.02 | 8.96 |
| 2024 | 16.10 | 14.18 | 10.49 |

- **P1: half right, and the tenure-1 half cannot be graded on this instrument.** The base fell by
  about four times at later decisions (0.100 to 0.026). The capture carries no tenure field, so
  "first" here means the first decision of an account inside the capture. That is not the first
  renewal: A's "first" mean of 0.0685 implies shocked months, which no first renewal can have. The
  capture now records `sim_experienced_bill_shock` and `sim_month_count_bill_shock_base`, so C can
  split by tenure properly.
- **P2: right for B (1.02 < 1.3). Not shown for A (1.46, not > 3)**, for the same instrument reason.
- **P3: right.** The whole book fell in all 7 fitted years. The refit raises 6 anchors over the
  live block. **2017 falls**, because A already sat 0.39pp above its target. The prediction "raises
  all seven" was wrong on 2017.
- **P4: not yet read.**

## C, graded (captured 2026-10-01 under the third-pass block, swap applied, default seed)

Committed beside A and B as `docs/reports/pb4_{a,b,c}_*_departure_factors.json` with their SVT
siblings. C was produced by code that is in no commit yet. The patch is in
`docs/design/UNLANDED_PB4_SWAP_AND_THIRD_PASS_ANCHOR_2026-10-01.md`.

| year | band | C whole book | verdict | refit on C |
|---|---|---|---|---|
| 2017 | 13.5–14.0 | 14.00 | inside | 7.031166 |
| 2018 | 19.5–20.0 | 20.00 | inside | 5.29532 |
| 2019 | 20.7–21.3 | 21.22 | inside | 8.652498 |
| 2020 | 22.5–23.0 | 21.67 | **low** | 19.572026 |
| 2021 | 17.9–18.4 | 16.07 | **low** | 18.730372 |
| 2023 | 8.9–12.5 | 8.81 | low, unfittable on A, B and C | — |
| 2024 | 12.5–16.1 | 15.42 | inside | 17.134335 |

- **P6: right.** 4 of 6 refitted years are inside. 2023 stays out low and 2022 stays unfitted.
- **P7: right.** Mean base 0.0257 / 0.0266 against B's 0.0257 / 0.0262.
- **Year one, split properly now that the capture carries the shock.** 31 first renewals are
  defined and 2 are shocked (6%). 60 later renewals are defined and 20 are shocked (33%). 13 are
  prepayment and out of scope. So year-one shock is defined and non-zero. The old count had 0
  shocked months at every first renewal against 0.099 mean base at later ones (C's
  `sim_month_count_bill_shock_base`). The year-one level assumes zero read error, per
  `SEAT_FINDING_A_FABRIC_PREMISES_REGISTRY_EAC_IS_NOW_ITS_OWN_READS_AND_YEAR_ONE_SHOCK_IS_SET_BY_AN_UNSIZED_READ_ERROR_2026-10-01.md`.
- **P5 (band test stays XFAIL): right.** C's renewal-route means run 22–51%, and that is the
  subject the test reads. It cannot sit inside a whole-market band.
- **P4 (margin): not read.** Reading it needs a full run with the published output, and that run
  belongs with the landing pass.
