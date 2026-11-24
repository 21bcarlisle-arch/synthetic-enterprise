**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: on the chain's own form, the demand year term exposes a price leg that runs £7 low after the crisis (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_THE_CHAINS_BUILD_TERMS_ON_ITS_OWN_PRICE_FORM_DEMAND_BY_YEAR_SOLAR_OUT_AND_WIND_ON_FUELHH_2026-11-24.md`
(`f0cfdf4f4`), which was promoted to origin before the probe ran. Probe `/var/tmp/wpc_build/measure_b.py`, sha256
`24eaceab…`, unchanged. Run in a worktree at `f0cfdf4f4`. Output `/var/tmp/wpc_build/out_b.json`.
**Nothing in `sim/` changes.***

## Outcomes (monthly, demand-weighted, £/MWh: MAE / bias)

| Arm | Pre | Crisis | Post | Post without 2025 |
|---|---|---|---|---|
| B0 shipped (control) | 6.50 / −5.29 | 17.20 / +2.39 | 8.19 / +1.84 | 8.12 / +0.18 |
| B1 + demand year term | 5.98 / −3.46 | 16.79 / −5.06 | 7.70 / −3.74 | 8.08 / −4.65 |
| B2 + solar out (refit) | **5.28** / −3.83 | **15.62** / −6.74 | **6.87** / −4.33 | **7.26** / −5.59 |
| B3 + wind on FUELHH (refit) | 5.13 / −2.77 | 16.31 / −7.16 | 8.62 / −5.09 | 8.76 / −7.93 |
| Leg on real x, AGWS w+s basis | 5.48 / −3.11 | 14.62 / −3.33 | 9.84 / −7.99 | 8.03 / −5.57 |
| Leg on real x, AGWS wind basis | 5.31 / −3.34 | 15.50 / −4.82 | 9.47 / −7.71 | 8.21 / −5.86 |
| Leg on real x, FUELHH wind basis | 5.07 / −2.26 | 17.26 / −6.33 | 7.76 / −7.24 | 7.95 / −7.28 |

**Bias by year:**

| Year | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| B0 | −9.17 | −4.56 | −4.32 | −3.85 | −4.99 | −8.79 | +13.19 | −4.11 | +1.89 | +6.81 |
| B3 | −4.27 | −0.40 | +0.41 | −2.72 | −6.29 | −9.14 | +0.71 | −14.40 | −5.60 | +3.44 |

**Refits** (A0 / A1 / A2, half-hourly MAE): R 0.2918 / 1.0790 / 2.8276, 31.53. S 0.2694 / 1.0384 / 2.9973, 31.96.
W 0.2732 / 1.0534 / 3.0214, 31.95. The fit uses the 157,010 half-hours that carry both wind series. On the full
157,106, R reproduces `fit_price_leg` to six decimals.

| # | Prediction | Outcome |
|---|---|---|
| B-P0 | B0 reproduces the shipped chain and `fit_price_leg` | **Held.** Max daily difference £0.00, and A0-A2 identical to 6 dp |
| B-P1 | B1 biases in the four filed bands | **Held.** −3.46, −5.06, −3.74, −4.65 |
| B-P2 | B1 pre MAE in [5.0, 6.3]; post MAE in [8.5, 11.0], above B0 | **Half wrong.** Pre 5.98 held. Post MAE FELL to 7.70. The bias flipped sign, but the monthly error spread fell |
| B-P3 | B2 moves each bias by < £1.5 and each MAE by < £1.0 | **Wrong, in the crisis.** Bias moved 1.68 and MAE moved 1.17. Pre and post held |
| B-P4 | B3 \|chain x̄ − record x̄\| < 0.01 in every year | **Wrong in 2 of 10 years.** 2016 −0.015 and 2025 +0.103. The other eight are within 0.007 |
| B-P5 | B3 pre-crisis bias range over 2016-20 < £4.0 | **Wrong.** £6.70 (−6.29 in 2020 to +0.41 in 2018), wider than B0's 5.32 |
| B-P6 | B3 post bias in [−8, −1]; crisis MAE ≤ 17.20; pre MAE ≤ 6.50 | **Held.** −5.09, 16.31, 5.13 |
| B-P7 | The leg on real W-basis inputs has post bias ≤ −2 | **Held.** −7.24, and −7.7 to −8.0 on the other two bases |

Four of eight held, one was half wrong, and three were wrong.

## What the rule says

- **Nothing ships.** B-P4 failed, and the filed rule says a construction failure is a result about the
  construction, not the price. On MAE alone, B3 met (a): pre −1.37, crisis −0.89, post +0.43. That is stated
  so that no later step reads "nothing shipped" as "the terms failed".
- **Where B-P4 failed, located after the run:** both years are `renewable_capacity_trend`'s end clamps
  (`_clamped_year`). 2016 takes 2017's fleet, so the chain's 2016 wind runs 3,790 MW against AGWS's 3,111 MW.
  2025 takes 2024's fleet, so it runs 4,574 MW against AGWS's 9,005 MW. In 2025, s_y (FUELHH/AGWS, 0.81)
  multiplies a fleet that was never matched to that year. The 2025 gap of 3.6 GW of residual is the
  "2025 renewables 4.9 GW under the record" that the gas-running arm named. It is now placed: the clamp,
  on a record year.
- **(b)'s hypothesis is confirmed, though (b) did not fire on its own terms**, because post MAE fell. B0's
  post-crisis bias of +0.18 (without 2025) is a cancellation. The chain's demand runs 1.7-2.3 GW too high after
  the crisis, and the price leg runs too low. Run on REAL daily x, with no chain, the leg is £7.2-8.0 low
  after the crisis on every basis (−5.6 to −7.3 without 2025). It is £2.3-3.3 low before. **Forward years
  inherit this.** They price at a demand with no year term, so they carry the cancellation only while the
  forward demand gap happens to offset the leg. That is an accident, not a mechanism.
- **(c) did not fire.** No step moved any regime's MAE by more than £2 (the largest was B3 post, +1.75).

## What it shows beyond the rule

- **Solar out is the cleanest term.** Against B1 it lowers MAE in all three regimes (−0.70, −1.17, −0.83).
  It is a definitional fix: INDO is already net of embedded solar, so subtracting AGWS solar counts it twice.
  It is the EP13 defect, which `295e9ad64b` fixed in the carbon dispatch on 30 Sep and which §4a of the
  electricity page found still live here.
- **FUELHH wind (B3) helps pre-crisis and hurts post-crisis** in the chain (post MAE 6.87 → 8.62, and 2023's
  bias −11.6 → −14.4), while it HELPS the leg on real inputs post-crisis (9.47 → 7.76). **I cannot yet say why.**
  B3's 2023 mean x matches the record (gap 0.000), so the miss is in x's distribution, not its mean. The
  candidate is the chain's narrow wind range (its windiest day is 12.8 GW against the record's 21.0 GW, from
  step B). Scaling by s_y = 1.23 widens the low-price tail less than the record's own spread does. That is a
  candidate, not an attribution.
- **2020 gets worse under every arm** (−4.99 → −6.29). COVID's demand collapse sits in Δ_y (−1.0 GW), and the
  leg prices the lower x too low. This is the same low-x shape question as §1b.

## Next

1. **The price leg's post-crisis level**, now measured on the shipped form: £7-8 low on real inputs. This is
   the §1b shape arm (a low-x depth that scales with the floor), pre-registered against the leg-on-real
   rows above as its control. It runs before any build, because each build term so far has moved the chain
   onto the leg's own error.
2. **The end-year clamps on record years.** 2016 and 2025 are record years and should take their own matched
   fleet. The clamp is a forward-year rule. This is a one-variable arm on `renewable_capacity_trend`'s use
   inside the record, and B-P4 is its control.
3. **Then rerun B1-B3** with both in place. On these figures, the build that would ship is B2 (solar out
   and demand by year), with B3's wind basis waiting on the distribution question above.

Reverse: delete this record.
