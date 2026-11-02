**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Both blind readers raise 2 finding(s) on b40bfa24fc (2026-11-02)

*Written by `background/two_reader_review.py`, the automatic lane of the two-reader trial
(director ruling 28 Oct, review 2026-11-11). Nothing here has been checked. Check each pair at
HEAD like any other finding, and record the outcome for the review. Severity is capped at
MAJOR until a check confirms more.*

- **Commit:** `b40bfa24fc472389b142eff575890d0bfe25b250`, committed 2026-11-02T09:58:31Z.
- **Modules it added:** `sim/ldz_calorific_value.py`, `tools/fetch_national_gas_ldz_cv.py`.
- **Verdicts:** A NEEDS_WORK, B NEEDS_WORK (trust ledger,
  `reading-review-live-2026-11-02:b40bfa24fc:arm{A,B}`).

## Raised by both (pairs from the tool-less matcher; undo any that do not name one defect)

1. **A#1 (MAJOR) `docs/staging/records/SEAT_PREREGISTRATION_HOW_FAR_THE_FIXED_GAS_CV_SITS_FROM_THE_PUBLISHED_PERIOD_AVERAGE_2026-11-02.md:32`** The Result section and the commit message state measured quantities (truncation 0.118%/0.249%, mean R5 39.477, max gap 1.50 MJ/m3 = 3.95%, cross-LDZ spread 1.56/2.70, 89 of 650 LDZ-months differing 5 days after month end, 24 of 19,786 out of 38-41) but no script, tool or test in the tree computes any of them; a grep of *.py finds only sim/ldz_calorific_value.py and tools/fetch_national_gas_ldz_cv.py touching the lake file. The pre-registered predictions are graded against figures nobody can reproduce from the commit.
   **B#1 (MAJOR) `docs/staging/records/SEAT_PREREGISTRATION_HOW_FAR_THE_FIXED_GAS_CV_SITS_FROM_THE_PUBLISHED_PERIOD_AVERAGE_2026-11-02.md:39`** The results (truncation 0.118%/0.249%, mean R5 39.477, spread across areas 1.56/2.70, 89 of 650 LDZ-months differing 5 days after month end, 131/108 runs of 38.0, 24 values outside 38-41) also appear in the commit title and on the page (a_gas_read_is_a_volume_and_the_bill_converts_it.md:165-185). No committed code produces them, and no test pins them: nothing outside the reader, its test, the conversion module and the fetcher imports sim/ldz_calorific_value. The headline quantities cannot be checked against the lake from this tree.
2. **A#4 (MINOR) `sim/ldz_calorific_value.py:123`** The bare-date-means-end-of-day rule exists only in the sim; the CalorificValueFeed Protocol (gas_volume_conversion.py:66) does not state it, and the company test's _Feed compares raw strings (a bare date sorts before same-day timestamps), so fake and real feed disagree for a same-day publication. The 'T' test also mis-handles a space separator: published_cv('NO','2022-08-09','2022-08-09 12:00:00') builds bound '2022-08-09 12:00:00T23:59:59', which sorts before every same-day publication, and returns None instead of the documented 40.3.
   **B#4 (MINOR) `sim/ldz_calorific_value.py:123`** as_of is compared as raw text. as_of='2022-08-09 12:00:00' (space separator) becomes '2022-08-09 12:00:00T23:59:59', which sorts before every '2022-08-09T..' timestamp, so the 10:30 version that day is wrongly excluded. as_of='2022-08-09T10:30' sorts before '2022-08-09T10:30:00', so a version published at exactly 10:30:00 is excluded despite the 'at or before' docstring. Neither input is tested.

## Raised by one reader only (not filed under the vote)

- A#2 (MAJOR): The headline 'off by up to 4% by area' (commit title) is the 1.50 MJ/m3 maximum, which equals exactly 39.5 - 38.0, i.e. an LDZ-month whose R5 is 38.0. That can only come from a month made almost entirely of the SC/WS exact-38.0 runs that G7 (line 113) and PROVENANCE.md say 'behave like a floor or a default rather than a measurement'. So the maximum stand-in error may be measuring a portal default, not gas; the page never makes this link or reports the maximum without those runs.
- A#3 (MINOR): The module docstring still says the daily series 'is not yet in the commons' (lines 12-15), and the STAND_IN comment says it is 'owed as G1' (line 37). The new paragraph at lines 17-20 says it is now in the lake from 1 Nov 2021. Two copies of the same status disagree.
- A#5 (MINOR): curl is run with -s but not -f, so an HTTP error exits 0 and its body (or an empty one) parses as zero rows: a transient failure for one LDZ-year drops that year without error at fetch time. Only the downstream coverage test would notice.
- B#2 (MINOR): The docstring (lines 13-16) and commit say each refusal names which input is missing, including 'before Nov 2021 there is no series'. But a pre-2021 period, e.g. feed=PublishedCalorificValues(), ldz='EA', 2019-06-01..2019-06-30, as_of='2026-01-01', returns 'no CV for EA on gas day 2019-06-01 had been published by 2026-01-01'. That presents a known gap in the lake as late publication, the same message as a genuinely unpublished day.
- B#3 (MINOR): The test fake compares `at <= as_of` as text, so a bare as_of date means the START of that day. The real feed (sim/ldz_calorific_value.py:123) treats it as 23:59:59. With a version at '2024-01-02T10:30:00' and as_of '2024-01-02', the fake returns None and the real feed returns the value. The CalorificValueFeed docstring does not say which format or meaning applies, so the company-side tests run under the opposite rule to production.
