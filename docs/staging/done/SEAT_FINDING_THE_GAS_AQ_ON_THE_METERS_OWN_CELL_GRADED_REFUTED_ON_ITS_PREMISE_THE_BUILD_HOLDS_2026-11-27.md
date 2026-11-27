**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `grade-the-gas-aq-on-the-meters-own-cell-first-year-ratio`

**Disposition (27 Nov 2026):** graded. The pre-registration is REFUTED as written. The build it graded does what it says to within 0.2%. No build follows from this; the residual below 1 is what a real weather-normal AQ does in a warm year.

# The gas AQ on the meter's own cell, graded: the prediction fails, the build holds (27 Nov 2026)

Grades `docs/staging/records/SEAT_PREREG_THE_GAS_AQ_ON_THE_METERS_OWN_CELL_FIRST_YEAR_RATIO_2026-11-26.md`
on the first book built on 601887d76a:
`docs/reports/run_output_601887d76a_20261126T232042Z.json` (producing_commit 601887d76a, generated
2026-11-27T01:17Z, world digest cdba75ebb9197b33, homes 6bbaf9bc65f762aa). The method is the one in
`docs/staging/done/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md`
(`/tmp/seat_aqyear/probe.py`, unchanged), plus a weather decomposition (`/tmp/seat_aqgrade/decomp.py`,
which runs `adopt_book` first).

## The reading against the bands

The quantity is first-year `meter_read_log.true_consumption_kwh` over `opening_registry_kwh_by_customer`. The denominator is the domestic gas legs with a full 365-day supply: 441 graded out of 539. 98 were excluded because their supply ran under 365 days. None were excluded for having no registry AQ or for a coverage gap.

| | pre-registered | measured | verdict |
|---|---|---|---|
| Overall median | 0.97 (0.95-1.01) | **0.940** (IQR 0.917-0.973, pooled 0.918) | **outside: refuted** |
| 2016 cohort (n=268, 61%) | 0.98 (0.96-1.00) | **0.942** (IQR 0.928-0.968) | **outside: refuted** |
| Cohorts 2021-2024 | 0.88-0.95, below 1 | 0.850 / 0.931 / 0.872 / 0.949 | 2021 and 2023 below the range; 2022 and 2024 inside |

On 001e4f680a the overall median was 0.915. It moved to 0.940, which is about 40% of the movement the prediction expected.

## Why it is refuted: the prediction's premise, not the build

The pre-registration computed the 2016 cohort as `0.85 x g + 0.15` with g for calendar 2016. That is
right only if a leg's first year is its read year. The build's read year is the 365 days before
`max(acquisition, run start + 365)`, so for every leg acquired during 2016 it is calendar 2016. But
only 2 of the 2016 cohort's legs were acquired on 2016-01-01. The other 266 have a first year that runs
into 2017 (GB 1,889 HDD against 2,021 in 2016). The model the earlier finding confirmed predicts each leg's ratio as

    (f x h_first_year + 1 - f) / (f x h_read_year + 1 - f) x (f x g + 1 - f)

with h being that leg's own cell HDD over a year divided by 2,060.9, and f = 0.85. Over the 355 legs whose two years are both on the world's weather (86 more read a climate normal on some day and are left out), it gives:

| cohort | n | h read year | h first year | g (GB) | predicted | measured | measured/predicted |
|---|---|---|---|---|---|---|---|
| all | 355 | | | | 0.941 | 0.946 | **1.002** (IQR 0.998-1.009) |
| 2016 | 257 | 0.963 | 0.911 | 0.983 | 0.938 | 0.943 | 1.002 |
| 2017 | 15 | 0.953 | 0.973 | 0.953 | 1.000 | 1.000 | 0.998 |
| 2018 | 9 | 0.972 | 0.914 | 0.944 | 0.912 | 0.919 | 1.003 |
| 2019 | 18 | 0.873 | 0.894 | 0.964 | 0.983 | 0.987 | 1.002 |
| 2020 | 15 | 0.963 | 1.023 | 0.927 | 0.999 | 1.002 | 1.000 |
| 2021 | 14 | 0.981 | 0.845 | 0.963 | 0.837 | 0.854 | 1.016 |
| 2022 | 6 | 0.909 | 0.946 | 0.917 | 0.962 | 0.964 | 1.008 |
| 2023 | 15 | 0.849 | 0.800 | 0.871 | 0.863 | 0.873 | 1.008 |
| 2024 | 6 | 0.829 | 0.896 | 0.873 | 0.960 | 0.964 | 0.997 |

What this establishes:

1. **The build registers what its formula says, at the meter's own cell.** The measured value is within 0.2% of the predicted
   value at the median in every cohort except 2021 (1.6%, n=14). The cell-versus-GB offset is carried: in 2016 the
   cell read year is 0.963 against a GB g of 0.983, so the meter keeps the 2% it ran warmer than the station.
2. **The 2016 shortfall is a mismatch between the first year and the read year.** That cohort's first year
   was 5.4% warmer than its read year in HDD (0.911 against 0.963). That alone takes the ratio from 0.984
   down to 0.938. A real Xoserve AQ behaves the same way: it is the last read year weather-normalised, and the
   following year is whatever the weather is. A first year that is warmer than normal uses less than its AQ.
   So this is fidelity, not a defect, and no build is opened for it.
3. **The cell-versus-GB offset did not carry the 0.915 on its own.** As the pre-registration's
   refutation clause requires, this is said plainly: putting the AQ on the cell moved the median 0.025.
   The rest of the old 0.915 was the first year's own weather, which a weather-normal AQ cannot
   foresee and should not (foresight through the seam is refused, knowledge page s6 (a)).

## Not measured

- The downstream pre-read over-billing (1.089 on 001e4f680a, which the pre-registration listed as
  informative only) was not re-read on this book. Its expected value is now about 1/0.94 plus the
  residual of roughly 1.3 points from the first months, not 1/0.97.
- GAP 5 (the warm lean of the 1991-2020 basis) is unchanged by this grade and still open on the
  knowledge page.
