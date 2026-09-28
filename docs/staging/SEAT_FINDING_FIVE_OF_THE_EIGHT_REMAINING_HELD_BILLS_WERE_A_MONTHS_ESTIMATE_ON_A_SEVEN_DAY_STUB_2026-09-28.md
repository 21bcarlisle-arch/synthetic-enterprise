**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_payment_channel_dd_consistency_invariant`

# FINDING — five of the eight bills still held were the estimator billing a month on a 7-day stub

Claim: `held-bills-are-never-reissued`. Follows
`SEAT_FINDING_THE_RESI_BILL_CONSUMPTION_FLOOR_HELD_195_REAL_SUMMER_GAS_BILLS_2026-09-28.md`, which took
the held population from 203 to 8 and called the 8 "SME-scale ceiling holds, correct holds".
**Five of them were not.** They were a billing error that the gate caught.

## Measured before any change (2026-09-28, HEAD `acd8567d8`, `docs/reports/run_output_latest.json`)

`validate_bills` holds 8, and every one of them also trips `vat_by_segment`:

| account | period | days | kWh billed | basis | true kWh |
|---|---|---:|---:|---|---:|
| SYN-2016-055 | 2025-06-01..07 | 7 | 735.8 | estimated | 41.9 |
| PROS-2019-0302 | 2025-06-01..07 | 7 | 771.4 | estimated | — |
| PROS-2019-0308g (gas) | 2025-06-01..07 | 7 | 2,162.9 | estimated | — |
| PROS-2023-0096 | 2025-06-01..07 | 7 | 548.7 | estimated | — |
| PROS-2025-0041 | 2025-06-01..07 | 7 | 494.2 | estimated | 87.7 |
| PROS-2016-0098 | 2016-03-23..31 | 9 | 968.7 | actual | 968.7 |
| PROS-2016-0098 | 2020-03-01..21 | 21 | 1,537.1 | actual (forced catch-up) | 1,537.1 |
| PROS-2016-0092 | 2017-02 | 28 | 2,066.9 | actual | 2,066.9 |

**Cause of the five:** `simulation.meter_reads.simulate_read` estimated as the MEAN kWh of the last
three actual BILLS, whatever their length. So a 7-day stub was estimated at a whole month's
consumption. It works the other way too: a 3-day opening stub's kWh became the estimate for every
following full month (PROS-2022-0063: 26 kWh estimated for months that used 291–373).

**Established practice, not a new constant:** a supplier estimate is a daily rate times the days
billed. The EAC/AQ is an annual figure, and it is pro-rated to the days in the period. No number is
introduced here. The window (3 actuals) is unchanged.

## Which pro-rata form, settled by measuring (replay over the 7,607 estimated bills in the same file)

| estimator | total abs error, kWh | bias, kWh | resi-envelope holds among estimates |
|---|---:|---:|---:|
| per-bill mean (HEAD) | 1,719,583 | −124,072 | 5 |
| mean of per-bill daily rates × days | 1,688,069 | −91,463 | 13 |
| **pooled: Σ kWh / Σ days × days** | **1,689,183** | −114,494 | **1** |

Averaging the rates lets one short stub set a third of the rate for months, and that alone
adds 8 holds. Pooling weights each actual by its days. On the 192 estimates a stub touches, the
pooled form cuts absolute error from 103,096 to 65,805 kWh (−36%).

Out of scope, noted: the headline error (1.7 GWh on 4.1 GWh true) is mostly seasonality. A
trailing-3 window ignores the season, and a real EAC/AQ is profiled. That is a separate fidelity
item, and nothing here changes it.

## Change

`simulate_read` takes `trailing_actual_days` and `period_days`. Given both, the estimate is pooled
pro-rata. `company/billing/monthly_bill_assembly.build_monthly_bills` threads each actual's
`days_in_period` and this bill's own days, and `generate_meter_read_log` threads them from the
bills. The `ReadArrivalFeed` Protocol declares both, defaulted.

## Pre-registration (for the next full run; the replay is a one-variable model of it)

- H1: held 8 → **4**: PROS-2016-0092 2017-02, and PROS-2016-0098 2016-03, **2016-04** and 2020-03.
  The new one is PROS-2016-0098's April 2016 estimate. The account's true use is 2,500–3,100 kWh a
  month (~33 MWh/yr of electricity). HEAD estimated it at 969 kWh because the 9-day stub's
  969 kWh was treated as a month. Pooled, it is 3,229 kWh, above the resi ceiling, and the gate
  holds it for the right reason.
- H2: no 2025-06-07 stub bill is held.
- H3: bills on the actual-read path are byte-identical. Only estimated bills, the catch-ups that
  reconcile them, and anything downstream of their amounts move.

Mutations: reverting to the per-bill mean reds both new world tests. Averaging rates instead of
pooling reds `test_a_short_opening_stub_is_pooled_by_its_days_not_averaged_as_a_rate`. Dropping the
day counts at the company call site reds
`test_the_billing_run_hands_the_feed_the_day_counts_an_estimate_is_pro_rated_by`.

## Still open: the four holds that remain are never re-issued

All four are actual or estimated reads over the resi ceiling, on two accounts. PROS-2016-0098 runs
at SME-scale electricity for years under a resi label. A real supplier's exception queue would
re-check that account's premises and use, then either **reclassify it**, which moves VAT from
5% to 20% and adds CCL and a contract type, **or confirm it as domestic** and release the bills.
Both end in an issued bill. Nothing here does either, so the energy stays bought and never billed.
That is the unbuilt follow-up named in `company/billing/pre_bill_validation.py`, now down to a
population of two accounts. Which way it goes needs the world to say what PROS-2016-0098 is. It is
a classification question, not a billing one.
