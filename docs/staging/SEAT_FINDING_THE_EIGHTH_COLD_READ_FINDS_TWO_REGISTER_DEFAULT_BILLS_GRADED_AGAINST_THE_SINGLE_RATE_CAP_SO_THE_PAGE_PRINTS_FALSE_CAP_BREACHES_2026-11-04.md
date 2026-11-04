**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# N19. Two-register default bills are graded against the single-rate cap at the household's own day/night mix, so the page prints cap breaches that are not breaches (2026-11-04)

**Source.** Reader objections O1 and O2 in the eighth cold read
(`records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`), confirmed by the seat on the
b3ce2a4e73 pages.

**What the page prints.** The renewal slot (SYN-2016-592) prints this under every moment: "This household breaks a
published rule 53 times. Electricity bill of 28 Feb 2019: 16.89p/kWh all-in including VAT, against a ceiling of
16.52p/kWh for a default tariff then". The storage slot (PROS-2020-0189) prints the same kind of note for its
June 2022 bill. A pricing reader takes either as a supplier admitting a cap breach.

**What the record shows.**
- Every bill in the book that carries a `default_tariff_excess_p_per_kwh` is a **two-register electricity bill
  (profile class 2)**: 626 bills on 11–14 households a year, 2019–2025. No single-register bill carries one.
- SYN-2016-592, Feb 2019: Day 733.2 kWh at 13.332p and Night 278.3 kWh at 3.352p (energy). The all-in rate at
  the household's own mix (72% day) is 16.09p ex-VAT.
  - Recorded excess: 0.3699p. That is 16.09p less the **single-rate** cap of 15.723p ex-VAT.
  - SLC 28AD.31(a) grades an Economy 7 tariff at an assumed 58% / 42% split. At that split the bill is
    **14.64p** against the multi-register cap of **14.63p**
    (`docs/domain_artefact_library/regulatory/ofgem_cap_multi_register_unit_rates.json`, Jan–Mar 2019). It is
    at the cap, within rounding.
- June 2025: Day 26.07p and Night 9.33p. At 58/42 the bill is about 24.5p ex-VAT, against a multi-register cap
  of about 24.6p. The recorded excess is 3.36p.
- The suite's `INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER` weights 0.58/0.42 and is CLEAN on 353 term-windows. It
  agrees with the seat, and it disagrees with the record the page reads.

**Cause, read in the code.** `company/compliance/domain_invariants.default_tariff_invoice_excess_p_per_kwh`
(line 427) takes `get_cap_unit_rate_for_date` for every electricity invoice. That is the single-rate ceiling. It
divides the bill's own charge by its own kWh. It never calls `get_multi_register_cap_unit_rate_for_date`, which sits
in the same module of the commons, and it never applies the 58/42 split. `tools/generate_billing_ledger.py:622`
records the result. `tools/generate_explore_cast.coverage_breaches` prints it, and so does
`tools/grade_svt_invoices_over_ceiling.py`.

**Why it matters beyond the page.** The function is the household side of the ceiling
(`DEFAULT_TARIFF_INVOICE_WITHIN_HOUSEHOLD_CEILING`). A real breach on a two-register home and a false one look
the same to it. The cast's `above_cap` census (22 of 751 households) is this artefact.

**What a fix needs.** Before the build, the knowledge on `docs/market_research/slc_28ad_multi_register_cap_test.md`
(the commons) and `a_storage_heated_homes_default_tariff_is_two_rate.md`. Then the function grades a multi-register
invoice at the 58/42 split against the multi-register cap. The 626 bills re-grade to their true count, which this
seat predicts is 0.

**The row this owes (ruling step 6).** It must be written blind from SLC 28AD.31 and the multi-register artefact:
a default-tariff two-register invoice is within the multi-register cap at the assumed split. A note the page
prints as "breaks a published rule" must agree with that row.

**Reverse.** Delete this file. Nothing outside `docs/staging/` was touched.
