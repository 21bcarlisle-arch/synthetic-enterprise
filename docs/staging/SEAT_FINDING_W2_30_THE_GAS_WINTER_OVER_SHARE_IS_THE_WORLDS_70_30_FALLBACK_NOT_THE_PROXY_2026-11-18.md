**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape`

# W2_30: the gas winter over-share is mostly the world's 70/30 fallback, not the DESNZ proxy (2026-11-18)

**Question.** This is the open question from the D48 finding
(`SEAT_FINDING_D48_BILLED_EQUALS_METERED_ON_EVERY_READ_AND_THE_GAS_SHAPE_IS_MORE_SEASONAL_THAN_THE_WORLDS_2026-11-18.md`,
which is still landing from the seat executor's worktree). On the 8a300fa561 book, the company's published gas share
puts +0.0121 of annual use a month more into winter than the world's metered year. Is the world's year too flat
(a W2_30 fidelity defect), or is the 2023–25 DESNZ proxy too peaked (a D48 estimator constant)?

**Method.** No new book was built. The cut recomputes `couple_d48_billing_gap.shape_rows` on the same book, split one
variable at a time. The split variables are the book's `gas_shape_provider_by_customer` and the account-year.
`demand_provider_by_customer` covers electricity accounts only, so its split is empty for gas.

**Pre-registered** (`/tmp/w230/PREREG.md`, written before any split was computed):
- PA1. The legacy fallback's gas year is flatter than fabric's, so its winter bias is larger. **Held.**
- PA2. Fabric's winter bias is under half the fallback's. **Refuted.** It is 61% of the fallback's. The intervals are
  disjoint, so the provider matters, but on this per-account measure fabric still carries a bias.
- PB1. On 2023–25, the proxy's own years, the bias stays at two thirds or more of its all-years size. **Held**, at
  104%. The proxy's era is not the cause.
- Headline prediction: the side is the WORLD. **Held**, with one qualification (the April residual, below).

**Results.** Winter months are Nov–Mar. Belief minus truth is in share of annual use per month, with 95%
account-clustered intervals. Jan/Jul is the kWh-weighted aggregate. That is the quantity the national DESNZ series
measures, so it is what the proxy should be compared against.

| cut | account-years | winter b−t (per account) | Jan/Jul (kWh-weighted) | Jun–Aug share |
|---|---:|---:|---:|---:|
| **DESNZ proxy (belief)** | | | **7.32** | **7.23%** |
| all | 1,453 | +0.0121 [0.0115, 0.0127] | 5.44 | 9.13% |
| fabric_seasonal_split | 351 | +0.0081 [0.0060, 0.0102] | **7.23** | 7.45% |
| population_70_30_split | 861 | +0.0132 [0.0128, 0.0135] | 5.05 | 9.67% |
| no provider recorded (`OCC-…g` accounts) | 241 | (n/a) | 4.82 | 9.87% |
| years 2023–25 | 338 | +0.0126 [0.0118, 0.0133] | 5.04 | 9.77% |
| years 2016–22 | 1,115 | +0.0119 [0.0113, 0.0125] | 5.44 (per-account) | 9.08% |
| use tercile low / mid / high | 484 / 484 / 485 | (n/a) | 4.94 / 5.44 / 5.69 | 9.8 / 9.1 / 8.8% |

**Reading.**
1. **The world's physics agrees with the proxy, and the world's fallback does not.** Premises settled on
   `fabric_seasonal_split` reproduce DESNZ's national year in aggregate (Jan/Jul 7.23 against 7.32; Jun–Aug 7.45%
   against 7.23%). That provider is derived from fabric and weather, not fitted to either series. The 70/30 fallback
   settles 861 of 1,453 gas account-years, and the 241 unrecorded ones read the same. Its Jan/Jul is about 5.0.
   That is the "~5.3x" its constant was calibrated to (`simulation/gas_settlement.py`
   `_GAS_BOILER_HEATING_FRACTION = 0.70`, "calibrated to match DUKES Table 4.3 Jan:Jul ratio ~5.3x"). Two published
   targets disagree: DUKES ~5.3 as quoted in the comment, and DESNZ Energy Trends monthly 2023–25 at 7.3. The world's
   own physics sides with 7.3. The most likely defect is the 5.3 calibration target, which leaves the population
   fallback with too large a flat base.
2. **The proxy's era is ruled out.** The bias on 2023–25, the years the proxy averages, is no smaller than on
   2016–22.
3. **Weighting is ruled out.** I checked whether comparing per-account mean shares against a kWh-weighted national
   share was the mismatch. It is not: the kWh-weighted all-book Jan/Jul is 5.44, against 5.33 per account. Low users
   are flatter (4.94 against 5.69 for high users), but the effect is small next to the fallback's.
4. **Residual on fabric.** In aggregate, fabric matches the proxy's January-to-July ratio. Per account, it still
   reads +0.008 winter. Its truth shares run high in spring (April 9.5% against 7.9%; May 5.7% against 4.1%) and low
   in Dec–Feb. The world heats deeper into spring than the national series shows. That is consistent with an HDD
   physics model that has no seasonal "heating off" behaviour. This is a stated hypothesis, not established. It is
   the smaller, second item.

**Side.** WORLD, mostly. The population 70/30 fallback, applied to about three quarters of gas account-years, is too
flat against both DESNZ and the world's own fabric physics. Do not retune the D48 estimator's gas shares on this
evidence. They are the right yardstick.

**What this does NOT do, and why.**
- It changes no world constant. Moving `_GAS_BOILER_HEATING_FRACTION` is a baseline change. It needs (a) knowledge
  first: what DUKES 4.3 and Energy Trends 4.2/5.5 actually give for the domestic Jan:Jul ratio across 2016–2025, and
  why "5.3x" and 7.3 differ (calendar against actual weather, sales against consumption, the year window). It also
  needs (b) a book. The box belongs to the skip pair until skip0 reads (DIRECTION `not_now`). **GAP:** the domestic
  gas Jan:Jul ratio the baseline should be calibrated to is not established in the knowledge layer.
- **Second, smaller finding.** 74 gas accounts with `OCC-` ids (241 account-years) are absent from
  `gas_shape_provider_by_customer`. The record that exists so that "a customer silently keeping the population
  constant is visible in the run" misses the occupier accounts. Their shape (Jan/Jul 4.82) says they are on the
  fallback.

**Next (handed on, not drawn here).**
1. Knowledge page: the domestic gas monthly shape, reconciling DUKES 4.3 "~5.3x" with ET 4.2/5.5 at 7.3.
2. Then the W2_30 fix: recalibrate the fallback's heating fraction to the established ratio, or widen fabric coverage
   so fewer premises fall back. Grade it on the book after skip0, with this table as the pre-registered baseline.
3. Add the `OCC-` accounts to `gas_shape_provider_by_customer`.

**Reproduce.** The script is `/tmp/w230/cut.py` plus `/tmp/w230/agg.py`, run with `PYTHONPATH=.` from the repo root. It
imports `couple_d48_billing_gap` from the executor worktree until that tool lands. It filters `shape_rows` by
`gas_shape_provider_by_customer[account]` and by year, and computes kWh-weighted month sums per subset.
