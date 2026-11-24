**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: on SAP plus GB's real net export, the price leg's crisis MAE falls by £5.2 and its post-crisis bias goes to zero, on its own form (2026-11-24)

*Autonomous worker, 24 Nov 2026. Item 4 of the weather-to-price steer (BLOCKING finding, G_data_learning).
Pre-registered in
`docs/staging/records/WORKER_PREREG_DOES_GB_NET_EXPORT_ON_THE_SAP_SPLICE_TAKE_THE_PRICE_LEGS_CRISIS_MISS_ON_ITS_OWN_FORM_2026-11-24.md`
(`1b2731aac`). That record reached origin before the `ne` arm ran. Run in a worktree at `95af8ab77` with
`sim/cache` linked in. The probe is unchanged from the filed one: sha256 `0de881e9…`, checked before the run.
The outputs are `/var/tmp/wpc_ne/out_base.json` and `out_ne.json`. **Nothing in `sim/` changes.***

## Outcomes

These are for the leg alone, on real daily x, on SAP. Figures are monthly and demand-weighted, in £/MWh, as
MAE / bias. Net export was added to INDO in both the refit and the record x, on all 157,010 half-hours, with
0 missing.

| Form | Arm | Coefficients | HH MAE | Pre | Crisis | Post | Post without 2025 |
|---|---|---|---|---|---|---|---|
| R L0 | base | 0.5170 / 0.9296 / 1.3960 | 30.99 | 4.65 / +1.33 | 18.46 / −8.20 | 5.82 / +4.08 | 6.23 / +5.85 |
| R L0 | **ne** | 0.5240 / 0.9980 / 1.7427 | 31.13 | **4.62** / +0.83 | **13.29** / −5.69 | 5.99 / **−0.30** | **4.91** / +2.11 |
| W L0 | base | 0.4732 / 0.9629 / 1.3681 | 31.33 | 4.99 / +2.27 | 17.80 / −10.08 | 5.83 / +4.83 | 5.40 / +4.55 |
| W L0 | **ne** | 0.4512 / 1.0853 / 1.4653 | 31.40 | 4.90 / +1.95 | **12.79** / −7.41 | **5.15** / −0.01 | 4.86 / +0.25 |

**Bias by year:**

| Arm | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|---|---|
| R base | −1.96 | +2.77 | +5.39 | +2.40 | −1.47 | −1.20 | −17.85 | +3.31 | +7.74 | −1.24 |
| R **ne** | −1.89 | +3.18 | +4.77 | +1.57 | −1.96 | **−4.21** | **−8.50** | +0.09 | +2.86 | **−7.52** |
| W base | −0.41 | +4.05 | +6.71 | +2.75 | −1.32 | −0.38 | −18.48 | +0.11 | +5.66 | +5.66 |
| W **ne** | −0.12 | +4.74 | +6.40 | +2.02 | −1.81 | −3.31 | −8.40 | −3.70 | +0.12 | −0.80 |
| net export, MW | −1,914 | −1,781 | −2,200 | −2,444 | −2,075 | −2,831 | +506 | −2,668 | −3,793 | −3,863 |

`synthetic_price` reproduces the leg within 1.1e-13 a day in both arms.

| # | Prediction | Outcome |
|---|---|---|
| NE-P0 | `base` reproduces the SAP R L0 and W L0 rows exactly | **Held** (run before filing, disclosed) |
| NE-P1 | 2022 moves toward zero by at least £6 | **Held.** −17.85 → −8.50 (+9.35) |
| NE-P2 | Crisis MAE falls by at least £2 | **Held.** 18.46 → 13.29 |
| NE-P3 | Post bias falls by at least £1.5 | **Held.** +4.08 → −0.30 |
| NE-P4 | Post bias lands inside ±£3 | **Held.** −0.30 |
| NE-P5 | Pre-crisis MAE moves by less than £0.50 | **Held.** 4.65 → 4.62 |
| NE-P6 | 2024 falls more than 2023 | **Held.** −4.88 against −3.22 |
| NE-P7 | W moves the same way as R on P1-P3 | **Held.** 2022 +10.1, crisis −5.0, post −4.8 |

Eight of eight held. P1's bet was that the leg would move 2022 by less than the chain's +9.6. It moved +9.35,
so the bet was right by £0.25. That margin is too thin to read anything into.

## What the rule says

**(a) fires.** P2 and P4 both hold, and pre-crisis MAE falls slightly instead of rising. The one-leg form on SAP
plus net export is the leg a build would ship. That build waits on two things, and is not done around either:

1. The forward net-flow K8 section, electricity page §5, which is still owed. Forward years need a net-export
   path. Real FUELHH flow cannot cross into forward years.
2. The DIRECTION `not_now` hold on the SAP splice.

## Stated plainly, beside the headline

- **Post MAE on R rose, from 5.82 to 5.99, while the bias went to zero.** All of that rise is 2025: its bias went
  from −1.24 to −7.52. Without 2025, post MAE falls from 6.23 to 4.91. On W, 2025 is −0.80. So the R-basis 2025
  miss sits on AGWS renewables, not on net export. The candidate is the AGWS finding
  (`WORKER_FINDING_ELEXONS_PUBLISHED_AGWS_WIND_HOLDS_ABOUT_HALF_THE_METERED_WIND_IN_THREE_WINDOWS_2026-11-24.md`)
  or a 2025 window like it. **That is a candidate, not an attribution.** 2025 is also a part year.
- **2021 got worse, from −1.20 to −4.21.** Its imports are the largest before the crisis, at 2.8 GW. This was not
  predicted and is not attributed.
- **The crisis is still the leg's worst regime.** 2022 is −8.50 and crisis MAE is £13.3. Net export carries about
  half of 2022's miss on the leg's form, against about nine-tenths on the chain's form (`c2f65d9e9`). The
  difference between the two forms is not measured here.
- **Half-hourly MAE moves by less than £0.15 on either basis.** The gain is in the daily and monthly level, not in
  within-day fit.
- These are the leg on REAL inputs. They are not the chain, and they are not a forward forecast. They say which
  leg a build should ship, not how well forward years will price.

## Next

1. **Build-terms B1-B3, rerun on SAP plus net export.** They are demand by year, solar out and FUELHH wind, on
   this record's `ne` rows as control. That is the inputs result's Next 2, now on the form rule (a) names.
2. **The forward net-flow K8 section** (electricity page §5). It is what lets a build use this term at all.
3. The R-basis 2025 residual (−7.52 against W's −0.80), read against the AGWS windows finding.

Reverse: delete this record.
