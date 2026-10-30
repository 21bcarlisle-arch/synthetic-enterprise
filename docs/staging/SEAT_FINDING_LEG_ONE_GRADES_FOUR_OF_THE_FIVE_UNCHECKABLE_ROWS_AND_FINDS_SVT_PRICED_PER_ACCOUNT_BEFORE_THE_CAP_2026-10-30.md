**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Leg one grades the five uncheckable rows: three now grade on the runner, two get a named grade elsewhere, and the SVT is priced per account before the cap (2026-10-30)

**Source:** the delivery item `leg-one-reads-the-five-uncheckable-rows`. On the raw export
(`/var/tmp/fresh-grade-9553/grade.txt`) five rows read UNCHECKABLE, so leg one's "zero unexplained
breaches" said nothing about them. This is what each one now reads, graded on the 9553d403b7 book
(1,293 accounts) and, for the page row, on the published book. It is BLOCKING because the SVT row
turns up a pricing defect, the ruling's own step 2 subject (the default-tariff price).

## The five rows

| row | before | now | on the 9553d403b7 book |
|---|---|---|---|
| INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW | UNCHECKABLE (no region, no tariff name) | graded, `ev_svt_one_price` | **BREACHED 1,068 of 33,627** account-months, excepted at that ceiling as a filed defect |
| INV_UNIT_RATE_EPG_HOUSEHOLD | UNCHECKABLE (the rate's basis unstated) | graded, `ev_unit_rate_epg_household` | **BREACHED 373 of 3,294** bill periods, excepted as print and volume scatter (below) |
| INV_ESTIMATE_RUN_WITHIN_TENURE | UNCHECKABLE (holds by construction on the export) | graded on the page against the export, `ev_estimate_run_within_tenure` | NOT_IN_EXPORT without the book's pages; **CLEAN 1 of 1** on the published book with its pages |
| INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE | UNCHECKABLE | stays UNCHECKABLE on the runner, on purpose; graded by the site test over the book's rebuilt pages | item 2's grade chain runs that test on its book (`n189.txt`) |
| INV_EV_ADOPTION_ELECTRICITY_ONLY | UNCHECKABLE | stays UNCHECKABLE on the runner, on purpose (the wall); world-side count stated in its gap | **49 asset events on gas legs**, every one on a date the household's electricity leg does not share |

The two rows that stay UNCHECKABLE carry reasons the next cold reader can check:

- **Committed price.** The page's own JavaScript (`stagePriced`) computes the panel. A Python copy
  in the runner would grade a second derivation, not what the reader sees. The row is graded where
  that code runs:
  `EXPLORE_PAGES_DIR=<book pages> pytest site/explore/test_the_committed_price_is_the_tariffs_not_one_bills.py`.
- **EV adoption.** The company holds no asset-change record. An EV, heat pump or PV install is a
  world event (`life_event_history`), and a supplier knows of one only if told. Exporting the stream
  would carry ground truth across the epistemic wall. The world-side count
  (`/var/tmp/five-rows-scripts/ev_world_side.py <run_out>`) gives 25 `ev_acquired`,
  14 `heat_pump_installed` and 10 `solar_install` on gas legs. That is the open defect
  `SEAT_FINDING_AN_EV_LIFE_EVENT_IS_DRAWN_WITHOUT_THE_HOUSEHOLDS_FUEL_LEGS_AND_ITS_EFFECT_IS_A_RAW_BEFORE_AFTER_AVERAGE_2026-10-26.md`,
  and this is the count to watch fall when it is fixed.

## What was read before building

- **Region.** The company records none. Its term record (`account_state_log`) holds one SVT list
  price per fuel and date (`svt_rate_gbp_per_mwh`) and no region key. So by its own record the book
  is one pricing region, and a regional price would show as a breach rather than hide. The
  tariff name is `tariff_type: svt` per fuel: the company sells one default product per fuel.
- **The EPG rate's basis.** In `saas/bill_generator.py` the Treasury's share is carved out of the
  household's energy line, and network and policy costs are a separate line. So a period's
  `unit_rate_p_per_kwh` is the household's energy rate. Measured, not assumed: on EPG-window SVT
  bills, the term rate less the Treasury's share per kWh lands on 32.38p (electricity) and 9.829p
  (gas). Outside the EPG, the printed rate plus `non_commodity_rate/10` is within 0.5% of the term
  rate on 45,477 of 46,667 single-rate periods; the rest are ToU and SME periods, which other rows
  grade. `raw_account_export.FIELDS` now states this basis.

## The defect: before the cap, the SVT is priced per account

On 2017-06-01 the electricity SVT terms in force carry 16 different rates, from 133.33 to
160.43 GBP/MWh. The same term record holds one list price, 140.0. Of the 1,068 breaches, 1,067 are
on the unit rate and 1 on the standing charge. By year and fuel:

| fuel | 2016 | 2017 | 2018 | 2019-2025 |
|---|---|---|---|---|
| electricity | 13 | 174 | 158 | 0 |
| gas | 11 | 473 | 238 | 0 |

By account prefix: SYN 714, OCC 245, PROS 102, C 6. So this is not occupiers' deemed contracts.
666 breaches are above the group's median and 401 below. From 2019 the clamp to the payment
method's cap column makes the SVT one price, which is why the cap years grade 0.

**Cause: not yet traced.** `rate_vs_svt_pct` on the term row varies per account, so the term's
`unit_rate` in `simulation/run_phase2b.py` is set per account somewhere upstream of the state row.
I cannot yet say whether that is the dynamic-pricing premium, a price change that never reaches
accounts already on the SVT, or a VAT basis mixed into some rates (160.0 / 1.2 = 133.33 =
140 / 1.05 is suggestive and unchecked). **Prediction, written before tracing:** most of the
spread is terms struck at a rate the SVT list moved away from, never re-priced when it moved.
**Next:** trace the term rate's source on one breaching account (OCC-6387bf64272a, 16.0 against
13.33 in Aug-Sep 2016), then fix and run fresh.

## The EPG row's 373: scatter, not a price over the EPG

Median excess 0.005p/kWh, largest 0.069p/kWh (0.21%), £5.16 ex-VAT over the whole book. The
scatter is symmetric: about 1,050 bills sit above term-less-receipt and 1,090 below, past the
penny tolerance. So the printed energy line is not priced on exactly the kWh printed beside it.
The household pays the EPG on average, but single bills land either side. The row grades the bill
as printed, so it stays at this count, with `retired_by` the line priced on the printed kWh.

**Noted, not graded:** 146 fixed-term bills in Oct 2022-Jun 2023 carry no Treasury share. The row's
own note records that the EPG also reached fixed tariffs, but the commons holds no scheme text for
how. Until that page is written, nothing here grades it.

## On item 2's book

Item 2's run (fresh-run-ecb7e21fb) was still computing when this landed. Its grade chain runs the
code at ecb7e21fb, which predates these evaluators, so it will read the three rows as UNCHECKABLE.
A detached follow-up (`/var/tmp/five-rows-scripts/follow_ecb7.sh`) waits for that chain's
`ALLDONE`. It then grades the five rows from `/var/tmp/wt-five-rows` (this landing's tree) on its
ledger, pages and cast, and writes `/var/tmp/five-rows-grade-ecb7e21fb/` (`grade.txt`, `ev.txt`,
`committed_price_site_test.txt`). The exceptions' ceilings are this book's counts, re-based on
that grade.
