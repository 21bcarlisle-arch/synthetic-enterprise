**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Electricity's pre-2020 year-end under-bill is one account: an unread EV home billed on the TDCV fallback for 50 months. It is not the season, and nothing in the code changed in 2020 (2026-10-16)

**Fate (2026-10-16):** ATOM -- D48 harden. This answers `done/SEAT_FINDING_D48_ELECTRICITY_DECEMBER_ESTIMATES_UNDER_BILL_BY_A_TENTH_IN_EVERY_PRE_2020_YEAR_2026-10-14.md`. The company's estimator is cleared. The world half (below) is the seat's to route.

*Worker tick, 2026-10-16. Run `run_output_2248e3baf_20261013T134447Z` (the one the Expert Hour graded), read through `company.billing.billing_accuracy.estimated_billing_outstanding_grade` itself. No ledger was regenerated.*

## Pre-registration, and what was seen before it

Seen before anything was written down, so this is NOT a prediction: the K1 grade at every month end sits at +8 to +12% from 2016-06 to 2020-02, then -0.7% at 2020-03. **That is a level, not a season.**

Pre-registered at 2026-10-16T12:25:37Z, before the per-bill split:

| | Prediction | Result |
|---|---|---|
| P1 | The season hypothesis (+ in Nov-Feb, - in May-Aug) is refuted: pre-2020 electricity is positive and flat across calendar months | **Held** |
| P2 | The pre-2020 level lives in the trailing-read path (>= +7% every month) | **Refuted.** Trailing-path electricity is -6.7% to +3.6% before 2020 and about the same after. The level is in the OPENING path (no read yet): +9.5% to +24.9% in every month before 2020, -19% to +1% after |
| P3 | After 2020-03, trailing electricity is within +-3% every month | Mostly held (Feb +5.5%, Apr -4.5%, Dec +4.6%) |
| P4 | Gas has no step at 2020-03 | Held for the trailing path |

Pre-registered at the next step: **P5**, without C7 the grade is within +-4% at every month end from 2016-07 to 2020-02, and the 2020-02 to 2020-03 step falls under 3 points. **Held.** **P6**, C7's only electricity read is billed in 2020-03. **Held** (2020-03-31).

## The cause

**C7** is an authored-roster home: single occupant, EV, smart meter, demand provider `hh_metered_reads`. Its consumption feed shows EV charging at about 1 kWh per half-hour from midnight to 04:00.

- It used **56,308 kWh in 51 months** (about 13.2 MWh a year) and was billed **14,530 kWh**.
- Its registration carried no EAC, so `opening_estimate_kwh` billed the TDCV MEDIUM fallback (3,100 kWh a year). That is the designed behaviour.
- `simulation.meter_reads` draws C7 as both `is_not_in_smart_mode` and `is_hard_to_read`. So 50 of its 51 bills are estimates, and **one read on 2020-03-31 trues up +41,778 kWh** against 13,010 billed (+321%).

K1 grades each run open at a month end by that run's closing true-up, pooled by kWh. C7's single run is open at every month end from 2016-01 to 2020-02, so the same +41,778 kWh enters all 50 grades. That is the whole "level", and the 2020 "step" is that one read arriving.

**Electricity K1 grade, net true-up share, with and without C7.** Quarter ends; every month is in the probe output.

| Month end | With C7 | Without C7 |
|---|---|---|
| 2016-06 | +22.9% | +2.2% |
| 2016-12 | +9.3% | -0.5% |
| 2017-06 | +9.0% | -0.9% |
| 2017-12 | +11.0% | +1.7% |
| 2018-06 | +10.7% | -0.9% |
| 2018-12 | +9.1% | -1.2% |
| 2019-06 | +10.0% | -0.9% |
| 2019-12 | +8.1% | -2.5% |
| 2020-02 | +9.8% | -1.2% |
| 2020-03 | -0.7% | -0.7% |
| 2020-12 to 2024-12 | -0.4% to +4.8% | identical |

**The code bisect is clean.** `unread_month_estimate`'s profile has no year key. The only date-keyed input on the estimate path is the TDCV table (1 Oct 2017, 1 Apr 2020), and it moves C7's fallback the wrong way: a lower TDCV from April 2020 would raise under-billing, not end it.

**Not the cause:** the electricity season profile. With C7 removed, no month carries a seasonal sign.

## What remains true, and whose it is

1. **World (the seat routes this; not fixed here).** `demand_provider_by_customer` says C7's demand is a half-hourly metered series, while the read feed says its meter is out of smart mode and hard to read, and its registration hands the supplier no EAC. Each draw is legitimate on its own. Together they give a meter with years of settlement history and no EAC, which the industry's D0019/EAC flow would not produce. Separately, `legacy_pc1_rescaled` homes realise **+21.9% (2016 cohort) and +10.6% (later)** above their own registry EAC across the decade, while `fabric_physics` homes sit at -1.5% / -3.2%. `eac_scaled_shape_fn` is meant to make the annual integral equal the EAC, so whatever layers on top of it in the legacy path adds about a fifth. That is a W-lane question, measured here only through bills.
2. **Measure (D48, company).** K1 pools kWh across runs and states no concentration, so one account set the published electricity year-end figure for four years and an Expert Hour read it as a population bias. The cheap remedy is to publish the largest run's share of the graded net beside the share. It is proposed here and not built.
3. **By-product, gas.** Trailing-path gas realises +19% to +51% over its estimate in April to June, in both eras. That is a spring miss in the gas profile and belongs with `SEAT_FINDING_A_GAS_HOMES_SEASON_MISS_IS_THE_WINTER_AND_LIGHTING_IS_THE_ONE_TERM_OFF_ITS_SOURCE_2026-10-09.md`.
4. **Not checked:** whether the company makes any effort to get a read from an account it has estimated for 50 months in a row (SLC 21B: at least one read a year). The 21BA bar applies to C7's catch-up from 2018-05, and that is K3's figure, not this one. **Answered 2026-10-16** in `WORKER_FINDING_C7_AND_286_OTHER_RUNS_OVER_TWELVE_MONTHS_NONE_BILLED_PAST_THE_BAR_AND_NOTHING_ASKS_FOR_A_READ_2026-10-16.md`. No effort is made, but no catch-up is billed past the bar: C7's £4,581.30 old share is barred at its final bill. Item 2's concentration figure is now built.

*Probe scripts: the per-month grade calls `estimated_billing_outstanding_grade` per fuel at every month end; the split recomputes true/estimated per estimated bill by opening or trailing path, calendar month and era. Both are about 40 lines over the committed run output.*
