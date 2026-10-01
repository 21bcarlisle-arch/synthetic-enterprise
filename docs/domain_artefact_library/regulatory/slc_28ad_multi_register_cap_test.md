# SLC 28AD: how the default tariff cap grades a multi-register or time-of-use tariff

**Type:** REGULATION COMMONS artefact. This file records the TEXT and its citation, readable by
every lane. Each lane's *reading* of it stays its own.

**Why it exists.** The worker finding
`WORKER_FINDING_THE_EAC_READ_ERROR_IS_UNBIASED_AND_WIDE_AND_THE_CAP_BINDS_A_TOU_TARIFF_AT_ITS_ASSUMED_SPLIT_2026-10-01.md`
read the assumed-split test from Ofgem's 2018 *draft* 28AD, because the in-force URL redirected.
This file holds the in-force text, which confirms the test.

## Sources (fetched and extracted 2026-10-01)

| # | source | status |
|---|---|---|
| S1 | Ofgem, *Standard conditions of electricity supply licence, consolidated to 18 July 2022* (a copy hosted at cdn01.sefe-energy.com/media/iymkhy2d/electricity-supply-standard-licence-conditions-consolidated-current-version.pdf) | quoted verbatim below. Ofgem's own banner says consolidated conditions "are not formal Public Register documents and should not be relied on". |
| S2 | Ofgem, same document, consolidated to 14 April 2022 (ofgem.gov.uk/sites/default/files/2022-05/Electricity%20Supply%20Standard%20Consolidated%20Licence%20Conditions.pdf) | identical wording in every paragraph quoted here |
| S3 | Ofgem, *Notice of statutory consultation on a proposal to modify SLC 28AD*, 27 August 2025 (ofgem.gov.uk/sites/default/files/2025-08/Notice-of-proposed-licence-modifications-Gas-and-Electricity-Supply-Licences-licence-condition-28AD.pdf) | its marked-up 28AD carries 28AD.34–.37 and the 42%/58% split unchanged |
| S4 | Ofgem, *Default tariff cap level model* v1.31 (`Default-tariff-cap-level-v1.31.xlsx`, sheets `ElecMulti_Other_Benchmark` / `ElecMulti_Other_Nil` and the `ElecSingle_` pair) | the levels table below |

The 2025-08 consolidated URL (`.../2025-08/Electricity-Supply-Standard-Consolidated-Licence-Conditions.pdf`)
redirects to a landing page for automated fetches. That is the redirect the worker hit.

## The text (S1, verbatim)

> **28AD.2** Unless a direction has been issued by the Authority pursuant to paragraph 28AD.32 in
> order to comply with 28AD.1, the licensee must ensure that for each of its Tariffs the aggregate
> Charges for Supply Activities applicable to any Relevant 28AD Customer at any consumption level
> (x kWh) in respect of a 28AD Charge Restriction Period do not exceed the Relevant Maximum Charge.

> **28AD.3** For all Single-Register Tariffs, compliance with the Charge Restriction will be
> assessed against the Relevant Maximum Charge determined on the basis of the Benchmark Metering
> Arrangement values for Single-Rate Metering Arrangements. [...]

> **28AD.4** For all Multi-Register Tariffs, compliance with the Charge Restriction will be
> assessed against the Relevant Maximum Charge determined on the basis of the Benchmark Metering
> Arrangement values for Multi-Register Metering Arrangements.

> **28AD.34** For the purpose of assessing compliance of Multi-Register Tariffs with the Charge
> Restriction pursuant to paragraph 28A.4 in calculating the aggregate amount of all Charges for
> Supply Activities, consumption in different periods will be weighted using an Assumed
> Consumption Split determined in accordance with paragraph 28A.21.

> **28AD.36** The Assumed Consumption Splits shall apply across Great Britain, reflect annual
> consumption patterns, and be determined as follows:
> (a) in respect of each Economy 7 Tariff, off-peak and peak consumption levels of 42% and 58%,
> respectively, shall be the Assumed Consumption Split, subject to any direction from the
> Authority issued pursuant to paragraph 28AD.38;
> (b) in respect of each Multi-Register Tariff (other than an Economy 7 Tariff), the Assumed
> Consumption Split shall be based on historic consumption data or, in the absence of historic
> data, on a reasonable estimate of the average consumption split, subject to any direction from
> the Authority issued pursuant to paragraph 28AD.38.

> **28AD.37** In respect of each Multi-Register Tariff (other than an Economy 7 Tariff), the
> licensee must: (a) notify the Authority in Writing of the Assumed Consumption Split with
> accompanying relevant data relating to the historic consumption of their customers [...] no less
> than three months before the beginning of each relevant 28AD Charge Restriction Period [...]

*(28AD.34 and .35 cross-refer to "28A.4" and "28A.21". That is the consolidation's own drafting,
carried over from the prepayment cap. 28AD.36 is the paragraph that sets the split.)*

**Definitions (S1, verbatim):**

> ‘Multi-Register Metering Arrangement’ means using one or more Electricity Meters for the purpose
> of a Tariff whereby a Domestic Customer’s electricity consumption at certain times, or for
> certain purposes (for example, heating), or both, is separately recorded - on one or more
> registers - and includes any contractual arrangement whereby the Domestic Customer is charged on
> the basis of Time of Use Rates (regardless of the metering equipment employed);

> ‘Multi-Register Tariff’ means a Tariff whereby a Domestic Customer incurs Charges for Supply
> Activities on the basis of a Multi-Register Metering Arrangement;

> ‘Economy 7 Tariff’ means a Tariff whereby a Domestic Customer is charged on the basis of two
> separate Unit Rates, where in each period of 24 hours the peak electricity consumption level is
> recorded during 17 ‘day/normal’ hours and the off-peak electricity consumption level is recorded
> during seven ‘night/low’ hours;

> ‘Relevant 28AD Customer’ means a Domestic Customer supplied by virtue of the Electricity Supply
> Licence held by the licensee and which is subject to an Evergreen Supply Contact, a Deemed
> Contract or a 28AD Default Fixed Term Contract;

## What the text settles

1. **A smart ToU tariff is a Multi-Register Tariff**, "regardless of the metering equipment
   employed". It is graded against the **Multi-Register** benchmark (28AD.4), never the single-rate
   one.
2. **The weighting is the tariff's Assumed Consumption Split, not any household's realised split**
   (28AD.34, .35). For Economy 7 that is 42% off-peak and 58% peak. For any other multi-register
   tariff it is the supplier's historic average split, notified to Ofgem (28AD.36(b), .37).
3. **The test holds "at any consumption level (x kWh)"** (28AD.2). The Relevant Maximum Charge is
   a nil-consumption allowance (the standing charge) plus a per-kWh slope. So a tariff passes at
   every x only if its standing charge and its assumed-split unit rate are each at or below the
   cap's.
4. **The cap binds default contracts only:** Evergreen (SVT), Deemed, and default fixed-term
   contracts. A fixed tariff the customer chose is outside 28AD.

## The two benchmarks, side by side (S4, ex-VAT, direct debit)

This is the median over the model's 15 Total rows (14 regions plus GB). The unit rate is
(benchmark − nil) ÷ benchmark kWh. Single-rate is ÷3,100 and multi-register is ÷4,200, the bases
the model's own headers give for every period before January 2026. The standing charge is
nil ÷ 365.

**Uncorroborated:** the multi-register column has NOT been checked against a published Economy 7
cap series. The single-rate column, built the same way, reproduces the published cap
(`tools/ofgem_cap_unit_rate_composition` cross-check).

| cap period from | 1-rate p/kWh | multi-reg p/kWh | MR ÷ 1R | 1-rate SC p/day | MR SC p/day |
|---|---|---|---|---|---|
| 2019-01-01 | 15.72 | 14.63 | 0.930 | 21.53 | 21.61 |
| 2019-04-01 | 17.67 | 16.47 | 0.932 | 22.30 | 22.38 |
| 2019-10-01 | 16.99 | 15.76 | 0.928 | 22.39 | 22.47 |
| 2020-04-01 | 16.77 | 15.61 | 0.931 | 23.19 | 23.27 |
| 2020-10-01 | 16.15 | 14.93 | 0.924 | 23.19 | 23.27 |
| 2021-04-01 | 18.00 | 16.56 | 0.920 | 23.69 | 23.77 |
| 2021-10-01 | 19.78 | 18.38 | 0.929 | 23.68 | 23.76 |
| 2022-04-01 | 26.94 | 25.41 | 0.943 | 45.31 | 45.40 |
| 2022-10-01 | 49.25 | 46.54 | 0.945 | 46.28 | 46.37 |
| 2023-01-01 | 64.14 | 63.87 | 0.996 | 46.28 | 46.37 |
| 2023-04-01 | 47.91 | 47.12 | 0.983 | 51.26 | 51.35 |
| 2023-07-01 | 28.54 | 27.29 | 0.956 | 51.26 | 51.35 |
| 2023-10-01 | 25.96 | 24.98 | 0.962 | 51.64 | 51.64 |
| 2024-01-01 | 27.12 | 26.23 | 0.967 | 51.63 | 51.62 |
| 2024-04-01 | 23.35 | 22.11 | 0.947 | 58.57 | 58.55 |
| 2024-07-01 | 21.31 | 19.97 | 0.937 | 58.62 | 58.60 |
| 2024-10-01 | 23.34 | 22.19 | 0.951 | 59.58 | 59.54 |
| 2025-01-01 | 23.67 | 22.66 | 0.957 | 59.57 | 59.53 |
| 2025-04-01 | 25.74 | 24.53 | 0.953 | 49.63 | 49.62 |
| 2025-07-01 | 24.56 | 23.37 | 0.951 | 46.82 | 46.77 |
| 2025-10-01 | 25.21 | 24.13 | 0.957 | 49.04 | 48.99 |

Two facts follow. The standing charges are equal to within 0.1p/day. The multi-register unit-rate
cap is 0.4–8% below the single-rate cap. **So a ToU pair that is revenue-neutral, at its own
assumed split, to a flat rate at the single-rate cap sits above its lawful ceiling.**

**Not carried here.** The model's notes show the multi-register benchmark consumption changing in
2026, from P15b (January 2026) and again from P16b (July 2026), with "3,400 kWh" in the current
header. The P15b value is not stated anywhere this pass could find. Rows from 2026 need that
schedule witnessed first, as `tools/ofgem_cap_unit_rate_composition.BENCHMARK_KWH_SCHEDULE` does
for single-rate.
