**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `is-a-gas-premises-registered-aq-its-first-year-of-true-use`

# Is a gas premise's registered AQ its first year of true use? (26 Nov 2026)

Filed by the delivery seat. Follows
`SEAT_FINDING_THE_GAS_AQ_FIX_CLEARS_ITS_ROW_AND_TIPS_NEW_GAS_ACCOUNTS_TO_OVER_BILLING_2026-11-26.md`,
which left four causes for new gas accounts billing 6-11% over their true use and named this as the
one-variable test for cause 1.

## Pre-registration (written before any number below was computed)

**Quantity.** For each domestic gas premise on one seed of the current world: the sum of
`meter_read_log.true_consumption_kwh` over the 365 days from acquisition, divided by the registry
AQ the company was handed by `register_gas_premises_on_their_own_reads`
(`simulation/run_phase2b.py`). Premises whose supply does not cover the full 365 days are excluded
and counted separately. Reported as median and IQR, overall and by acquisition-year cohort.

**Source.** The 001e4f680a book (`docs/reports/run_output_001e4f680a_20261126T090839Z.json` on the
shared tree; one seed, built after b3f3a23f6f), read only. No new run, no publish, if the book
carries both the registered AQ and the meter truth.

**Readings, fixed now:**
- median about 0.9 (below 0.95): cause 1 holds. World gas demand is not `aq x multiplier`, so the
  registered AQ is not the meter's own year, and the registration rule's premise is wrong.
- median about 1.0 (0.97 to 1.03): the AQ is the meter's year; the over-billing sits in the first
  months (weather, 2022-23 demand reduction) and is what a real supplier does with a normal-year AQ.
- between those, or a cohort pattern that differs from the overall: reported as such, not forced
  into either reading.

The ratios to beat: billed/true 1.112, account median 1.089, on bills before the first actual read
on 001e4f680a. A true/AQ ratio of r would explain an over-bill of about 1/r.

## Result 1: the registered AQ is not the meter's first year. Median 0.915

The 001e4f680a book carries everything needed, so no run was made. It has the registered AQ in
`opening_registry_kwh_by_customer` (written after phase 2b's rewrite;
`simulation/run_phase4c_on_phase2b.py:1041`). It has the truth in `meter_read_log`, row-aligned with
`bills` (54,278 = 54,278 matched on id and period_end), and acquisition in `account_held_from`. The
first-year truth is pro-rated by day over the bills that straddle the 365-day edge.

The population is the 515 domestic gas billing legs. 441 are graded. 74 are excluded because their
supply ended before 365 days (2016: 28, 2024: 27, 2025: 13, others 4-7). None was excluded for a
missing registry figure or a coverage gap.

| Cohort | n | true first year / registered AQ, median (IQR) | pooled |
|---|---|---|---|
| all | 441 | **0.915** (0.845-0.990) | 0.900 |
| 2016 | 268 | 0.924 (0.873-0.983) | 0.923 |
| 2017 | 26 | 0.945 (0.865-1.009) | 0.894 |
| 2018 | 19 | 0.876 (0.757-0.946) | 0.826 |
| 2019 | 30 | 0.908 (0.813-0.992) | 0.879 |
| 2020 | 24 | 1.009 (0.855-1.056) | 0.964 |
| 2021 | 28 | 0.855 (0.683-0.924) | 0.804 |
| 2022 | 15 | 0.876 (0.741-0.930) | 0.817 |
| 2023 | 21 | 0.827 (0.776-0.915) | 0.828 |
| 2024 | 10 | 0.872 (0.792-0.954) | 0.854 |

By the pre-registered rule this is the "about 0.9" reading. 1/0.915 = 1.093, which is close to the
1.089 account median it was asked to explain. The split by shape provider does not change it:
fabric_seasonal_split 0.926 (n=209), population_70_30_split 0.913 (n=232).

## Result 2: the mechanism is weather, and cause 1 as written is refuted

The pre-registration tied "about 0.9" to cause 1: demand is not `aq x multiplier`. A second
measurement shows that is not why the ratio is 0.9. The world's domestic gas day is
`aq x mult x (f x HDD_day / HDD_ref + (1-f) / 365)` (`simulation/gas_settlement.py`,
`resi_daily_gas_kwh`). Here f = 0.85 and HDD_ref = 2,060.9, the sum of `REFERENCE_MONTHLY_HDD`, the
1991-2020 England & Wales monthly normal. So a premise's year should come to
`registered AQ x (f x h + 1 - f)`, where h is the premise cell's own HDD over that year divided by
HDD_ref.

The weather was read with the book's population adopted (`adopt_book`, as `run_phase2b` does). 355
premises were graded. 86 resolve to no cell outside the run and fall back to the normal, so they are
ungraded here.

| Cohort | n | cell HDD / reference | predicted | measured | measured / predicted |
|---|---|---|---|---|---|
| all (IQR) | 355 | 0.911 (0.839-0.988) | 0.924 | 0.930 | **1.000 (0.997-1.005)** |
| 2016 | 257 | 0.911 | 0.924 | 0.927 | 1.000 |
| 2017 | 15 | 0.973 | 0.977 | 1.009 | 1.000 |
| 2018 | 9 | 0.914 | 0.927 | 0.937 | 0.998 |
| 2019 | 18 | 0.894 | 0.910 | 0.911 | 1.001 |
| 2020 | 15 | 1.023 | 1.020 | 1.009 | 1.000 |
| 2021 | 14 | 0.845 | 0.868 | 0.876 | 0.999 |
| 2022 | 6 | 0.946 | 0.954 | 0.954 | 1.002 |
| 2023 | 15 | 0.800 | 0.830 | 0.852 | 1.006 |
| 2024 | 6 | 0.896 | 0.912 | 0.914 | 0.993 |

So the world's gas use is exactly `aq x multiplier x weather`, to within 0.5% at the quartiles, in
every cohort. Nothing else in demand lowers it. Cause 2 (the multiplier falling after acquisition)
would show up as measured / predicted below 1, and it does not. The whole shortfall is that the
premise cells are warmer than the reference normal: median HDD 9% below it. A note on method: a
first attempt without `adopt_book` read every premise on the normal (h = 1.01). That would have
"ruled weather out". It is recorded here so the next probe loads the book first.

## What this means

The defect is a sentence in `docs/market_research/a_gas_meter_points_aq_is_made_from_its_own_reads.md`
s3: "The world's level has no weather in it, so this figure is weather-normal by construction." The
level is the year at the **national 1991-2020 E&W normal**. A real AQ is put on the seasonal-normal
weather of the meter's own LDZ (Xoserve, quoted [H] on the same page). The world's meters live on 1
km HadUK-Grid cells, which run warmer than that normal for two reasons (`sim/weather_hdd.py`
docstring): urban cells are about 1.2 C warmer, and 2016-25 was warmer than 1991-2020. The
registration therefore hands each premise an AQ about 7-8% above its own normal-weather year
(1/0.930), and the hold-window over-billing follows from that.

How much of that 7-8% a real supplier would also see is not established. If the LDZ seasonal-normal
basis is climate-adjusted and local, a real AQ sits closer to the cell's year than this one does.
That is a knowledge question (which normal Xoserve uses, how local it is, how it is revised), and K2
forbids picking the answer. It is filed as GAP 4 on the knowledge page and handed on. No world code
is changed here.

The pre-fix figures are consistent with this. The drawn level had no multiplier, so its errors were
the multiplier and the weather together, which cancelled to 0.97 overall.

Unexplained residual: 1/0.930 = 1.075, against a 1.089 median over-bill before the first read. The
remaining ~1.3 points sit in which months the unread bills fall in (the first-months shape). They
are not sized here.

Probes: `/tmp/seat_aqyear/{probe,hdd2,byprov}.py`. They are throwaway and read only the shared
tree's 001e4f680a book.
