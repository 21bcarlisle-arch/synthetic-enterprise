**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `put-the-registry-gas-aq-on-the-meters-own-cell`

# Pre-registration: a gas premise's first year over its registered AQ, once the AQ is on the meter's own cell (26 Nov 2026)

Filed by the delivery seat **before** any book was built on this change. The build is
`register_gas_premises_on_their_own_reads` (`simulation/run_phase2b.py`), described in
`docs/market_research/a_gas_meter_points_aq_is_made_from_its_own_reads.md` s6. Before it, the
001e4f680a book read a median of **0.915**
(`docs/staging/done/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md`).

## Quantity

This is the same quantity and method as that finding: for each domestic gas billing leg whose supply
covers 365 days, `meter_read_log.true_consumption_kwh` over the 365 days from acquisition, divided by
`opening_registry_kwh_by_customer`. It is reported as median and IQR, overall and by acquisition-year
cohort. It is graded on the first book built on or after this landing's sha. The finding measured
first-year use = AQ x (f x h + 1 - f) to within 0.5%, so the expected values follow from the new
formula and ET 7.1:

## Readings, fixed now

- **2016 cohort (about 60% of the graded legs): median 0.98, with 0.96-1.00 as the pass band.**
  The read year is calendar 2016, GB g = 2,021 / 2,060.9 = 0.981, and 0.85 x 0.981 + 0.15 = 0.984.
- **Overall: median 0.97 (0.95-0.99).**
- **Cohorts 2021-2024: median 0.88-0.95, still below 1.** Their read years ran warm (g 0.864-0.98
  in GB), and the 1991-2020 basis does not remove that (GAP 5). This is the predicted residual, not
  a failure.
- **Refuted if** the overall median is below 0.95 or above 1.01, or the 2016 cohort falls outside
  0.96-1.00. If so, the cell-versus-GB offset is not what carried the 0.915, and that gets
  reported, not explained away.
- **Downstream, informative only:** the account median over-bill before the first read (1.089 on
  001e4f680a) should fall toward about 1/0.97, roughly 1.03 plus the ~1.3-point first-months
  residual.

## Graded (27 Nov 2026): REFUTED

Graded on `run_output_601887d76a_20261126T232042Z.json`. Overall median 0.940 (n=441) and 2016 cohort 0.942 (n=268), both outside their bands. The
cause is the prediction's own premise. 266 of the 268 legs in the 2016 cohort have a first year that runs into the
warmer 2017, while their read year is calendar 2016. Using each leg's own first-year and read-year
cell HDD, measured over predicted is 1.002, so the build holds. Full grade:
`docs/staging/done/SEAT_FINDING_THE_GAS_AQ_ON_THE_METERS_OWN_CELL_GRADED_REFUTED_ON_ITS_PREMISE_THE_BUILD_HOLDS_2026-11-27.md`.
