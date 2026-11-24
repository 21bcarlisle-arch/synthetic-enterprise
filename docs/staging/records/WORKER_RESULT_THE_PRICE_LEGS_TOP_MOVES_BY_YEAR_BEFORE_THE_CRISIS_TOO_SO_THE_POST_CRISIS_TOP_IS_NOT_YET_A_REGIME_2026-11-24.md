**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the price leg's top moves by year before the crisis too, so the post-crisis top is not yet a regime (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_IS_THE_PRICE_LEGS_POST_CRISIS_TOP_A_STABLE_CHANGE_OR_A_FEW_DAYS_ON_SAP_2026-11-24.md`
(`160f9fa88`). It landed locally at 20:44:24, and the probe ran at 20:45. **Unlike the earlier arms, it was not
on origin before the run.** The local commit time is the only evidence of order. The probe ran in a worktree at
`160f9fa88`, with `sim/cache` linked from the main tree. Output is `/var/tmp/top_sap/out.json`. **Nothing in
`sim/` changes.***

**Probe amendment, beside the claim.** The probe as registered (sha256 `3cd56b57…`, kept at
`/var/tmp/top_sap/probe_as_registered.py`) failed on its first fit. It built the post-crisis indicator over
every day but multiplied it by the masked days. The fix passes the masked indicator into the fit
(sha256 `d9d4e330…`). It is two lines, and the registered design is unchanged. No output was produced before
the fix.

## Outcomes (monthly, demand-weighted, £/MWh: MAE / bias, real c)

| Arm | post-top coef | pre | crisis | post | post without 2025 | 2025 |
|---|---|---|---|---|---|---|
| T0 (S1, control) | — | 3.07 / −0.31 | 9.33 / −3.14 | 4.89 / +2.44 | 4.62 / +2.12 | 5.68 / +3.43 |
| **T1** (post year held out) | −0.0151 / −0.0121 / −0.0189 | = T0 | = T0 | **4.62 / −0.27** | 4.15 / −0.41 | 6.03 / +0.13 |
| T2 (oracle) | −0.0152 | = T0 | = T0 | 4.29 / −0.01 | 3.73 / −0.11 | 5.98 / +0.28 |

Refitting with the post-crisis term also moves the low-gas hinge, from −0.101 to about −0.124 (T1 every
year, T2). T1 changes two things on post days, not one.

The top by calendar year (days at 14 GW or more; ratio of mean price to mean floor):

| Year | days | record | T0 | record − T0 |
|---|---|---|---|---|
| 2016 | 190 | 1.432 | 1.230 | +0.20 |
| 2017 | 161 | 1.243 | 1.238 | +0.01 |
| 2018 | 152 | 1.119 | 1.223 | −0.10 |
| 2019 | 143 | 1.151 | 1.248 | −0.10 |
| 2020 | 85 | 1.311 | 1.228 | +0.08 |
| 2021 | 119 | 1.287 | 1.221 | +0.07 |
| 2022 | 152 | 1.255 | 1.235 | +0.02 |
| 2023 | 66 | 1.180 | 1.247 | −0.07 |
| 2024 | 41 | 1.143 | 1.280 | −0.14 |
| 2025 | 36 | 1.234 | 1.280 | −0.05 |

| # | Prediction | Outcome |
|---|---|---|
| H-T0 | T0 reproduces S1's rows | **Held**, to every printed figure |
| H-T1 | 2023, 2024 and 2025 each have a record top 0.03 or more below T0's | **Held.** −0.07, −0.14, −0.05. These are calendar years, so 2023 includes crisis days in H1 |
| H-T2 | Each pre-crisis year is within ±0.06 of T0 | **Refuted, badly.** Only 2017 is. 2016 is +0.20, 2018 and 2019 are −0.10, 2020 is +0.08 |
| H-T3 | T1's coefficient is negative every year, in [−0.04, −0.005] | **Held.** −0.012 to −0.019 |
| H-T4 | T1 post bias in [+1.2, +2.2]; MAE in [4.2, 4.9] | **Bias refuted:** −0.27, a move of 2.71 and not about 1. **MAE held:** 4.62 |
| H-T5 | T2 post bias in [+0.9, +1.9], and T2 below T1 | **Refuted.** −0.01, which is above T1's −0.27 |
| H-T6 | T1 and T2 leave pre and crisis within ±0.10 | **Held, but it could not fail.** The probe replaces post days only, so pre and crisis are T0's by construction. This is an equivalence, not a test |

Three of seven held as tests (H-T6 is not counted). The size estimate was wrong: the term starts at 12 GW,
not 14, and it moved the hinge too, so it is not a top term. It is a post-crisis slope over all of
12 GW and above, plus a deeper hinge.

## What the rule says, and why it is not the whole answer

- **Rule (a) fires as written.** H-T1 holds in all three post years, T1's sign is negative for every held-out
  year, and the bias moves by £2.71, which is more than the £0.8 threshold.
- **H-T2 says the premise is not established.** The rule assumed the pre-crisis top was stable, and it is not.
  Before the crisis, the top moves by year through −0.10 to +0.20 around the pre-crisis fit. 2018 and 2019 sat
  as low as 2023-25. So a post-crisis shortfall of −0.05 to −0.14 is within the range the pre-crisis years
  already show. **A date term for "after 2023" is not supported, so none is built.** The K8 step that rule (a)
  names is still owed. It is not a question of what flattened the top after 2023. It is a question of what
  moves the top from year to year.
- **Seen after the run, so it is a hypothesis, not a result.** The years with a neighbour shortfall in
  electricity page §5b are 2016, 2017 (Nov), 2020 (Jul), 2021 (Nov-Dec) and 2022. Their tops are 1.43, 1.24,
  1.31, 1.29 and 1.26, all 1.24 or more. The years without one are 2018, 2019, 2023, 2024 and 2025, at 1.12,
  1.15, 1.18, 1.14 and 1.23, all 1.23 or less. The split is clean on ten years and was found by looking. It
  needs its own arm, at the month and with the prediction filed first, before it can carry any weight.
- **What T1 shows anyway.** A post-crisis level change can take the price leg's post bias to about zero on
  real gas running (oracle −0.01). The leg's remaining post-crisis error is level and shape, not noise. It is
  just not attributable to "after the crisis" while the pre-crisis years scatter this much.

## Next, still item 4

1. Pre-register an arm, at the month and on days at 14 GW or more: does a month with a neighbour shortfall
   (§5b's definition, GB-France monthly net flow at or below zero) price the top above the pre-crisis fit,
   and a month without one below it? State the post-hoc observation above as seen.
2. The shippable record-years build keeps S1's pre-crisis top. Until arm 1 says otherwise, the top's by-year
   spread (−0.14 to +0.20 of the floor on 14 GW+ days) is stated beside every forward figure. That build is
   carried by the SAP splice finding.

Reverse: delete this record.
