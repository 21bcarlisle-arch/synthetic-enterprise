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

### Traced (30 Oct): the renewal chain's per-account writers, and the prediction was wrong

**The prediction is refuted.** No SVT term was struck at a list price that later moved. Every
segment is re-struck at the list price each window. Read off the 9553d403b7 book's
`rate_decomposition_log`, matched to the state row by its contracted rate: all 2,489 off-list
pre-cap SVT terms (of 4,366) **entered the chain at the list price**. The company's renewal-rate
chain (`company/pricing/renewal_rate_chain.py`) then moved them:

| writer | terms | 2016 | 2017 | 2018 |
|---|---|---|---|---|
| 1, portfolio premium | 2,348 | 30 | 1,177 | 1,141 |
| 2, margin surcharge | 75 | 14 | 30 | 31 |
| both | 66 | 4 | 36 | 26 |
| unexplained | **0** | | | |

Writer 1 reads the portfolio margin at the account's own term start, so accounts on the same day
carry premia struck on different days. Writer 2 reads the account's own last margin:
OCC-6387bf64272a's first stint lost £19.84 on £39.94, so its next SVT segment took +20%, 133.33 to
160.0. That is the 16.0p. Writers 3 and 3b already refused a default tariff
(`UPLIFTABLE_TARIFF_TYPES`). From 2019, writer 4's clamp to the cap pulled every raised rate back to
one price, which is why the cap years grade 0. **Two side readings, both checked:** 133.33 = 140/1.05
is the list price taken back to ex-VAT, the same basis on every account, not a VAT mix. And my first
join read 74 terms as "off-list before the chain". That was my join, not the book: on an
anniversary the declined fixed offer and the SVT segment share (account, fuel, date), and those
state rows are at the list price.

**Fixed:** writers 1 and 2 do not move a default tariff (`CAPPED_TARIFF_TYPES`). K8 page:
`docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`, choice 8, with choice 7 corrected
beside its claim. Controls: `tests/company/pricing/test_a_default_tariff_is_one_list_price_before_the_cap.py`
and the seam suite's `test_no_renewal_is_both_learned_on_and_capped`. Both go red with the gate
reverted. The seam suite's old reorder mutant (surcharge lifted past the clamp) is now
**equivalent by construction**: no term both learns and is capped. The new control holds the
property that makes it equivalent. Revenue the writers added on this book: about £8.2k ex-VAT over
2016-18 (EAC-weighted). The fix removes it, which errs against our own thesis.

**Not traced:** the 1 standing-charge breach. Writers 1 and 2 move only the unit rate, so this fix
does not reach it.

**Pre-registration for the fresh run at the fix commit (written before it runs).**
`INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW` goes from 1,067 unit-rate breaches to **0**. The
standing-charge breach stays at **1**, cause unknown. Pre-cap SVT revenue falls by £5k-£12k ex-VAT
against the 9553d403b7 book. Second-order movement (margin history, churn) means no other
figure's move is attributable to this change from that run alone.

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

**Graded (30 Oct, from the c8e57d43d tree on item 2's ledger, `/var/tmp/fresh-grade-ecb7e21fb/ledger.json`).**
The follower died with its worktree at 01:49. It was re-armed as the systemd unit
`follow-five-rows-ecb7e21fb` against a static export of c8e57d43d. The two ledger rows were graded
by hand as soon as the ledger existed: `INV_SVT_ONE_PRICE_PER_REGION_METHOD_WINDOW` **1,068 of 33,626**,
`INV_UNIT_RATE_EPG_HOUSEHOLD` **373 of 3,294**. These are the 9553d403b7 book's counts, so the ceilings
stand and only the scopes are re-based. The SVT run predates the writers-1-2 gate (ed8684442), so
1,068 is the expected reading. The two rows that need the book's pages (estimate run, committed price)
arrive in `/var/tmp/five-rows-grade-ecb7e21fb/` when the chain's `ALLDONE` is written.

**The page rows, read (30 Oct, from `/var/tmp/five-rows-grade-ecb7e21fb/`, written at the chain's `ALLDONE`).**
- `INV_ESTIMATE_RUN_WITHIN_TENURE`: **CLEAN, 0 of 1** on the ecb7e21fb pages. One estimate run is printed on
  the book's pages, so this row says little until a book prints more.
- `INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE`: the site test over the rebuilt ecb7e21fb pages,
  **10 passed**. That is the run-side grade. The runner row stays UNCHECKABLE, as designed.
- `INV_EV_ADOPTION_ELECTRICITY_ONLY`, world side: **49 asset events on gas legs** (25 `ev_acquired`,
  14 `heat_pump_installed`, 10 `solar_install`). Each is on a date the electricity leg does not share. The
  count is the same as on the 9553d403b7 book, so the life-event defect is still open.
- The two ledger rows are the counts above: 1,068 and 373.

## The fresh run at the fix (launched 30 Oct, written before any output exists)

`launch_long_job` job `fresh-run-3dc5a92948`, at origin 3dc5a92948. That commit carries ed8684442, the
writers-1-2 gate. Worktree: `/var/tmp/fresh-run-wt-3dc5a92948` (locked). Script:
`/var/tmp/fresh-run-scripts/arm.py`. Output: `/var/tmp/fresh-run-out-3dc5a92948`. The launch queued behind
another lane's landing. The grade chain is the systemd unit `grade-chain-3dc5a92948`
(`/var/tmp/svt-fix-run-scripts/chain.sh`). When `DONE.json` exists it writes the following to
`/var/tmp/fresh-grade-3dc5a92948/`: the ledger, the five rows with examples (`grade_five.txt`), pre-cap SVT
revenue (`svt_revenue.txt`), and then the full suite (`grade.txt`).

**The revenue measure, fixed before the run.** `svt_revenue.py` takes domestic bills dated 2016-2018 whose
period-start term is `svt` in `account_state_log`, and sums commodity + non-commodity + standing charge,
ex-VAT. On the two pre-fix books it reads **£346,790.33** (9553d403b7) and **£346,790.28** (ecb7e21fb), from
8,950 bills and commodity £190,740. So the ecb7e21fb fixes did not move this measure, and any move on the
fresh book comes from the SVT gate plus whatever second-order effects follow from it. Its term count:
**2,490 of 4,366** pre-cap SVT terms are off the ex-VAT list price (`svt_rate/1.05`, 1e-3 tolerance). The
trace above found 2,489. The difference is one term at the tolerance edge, and the trace's join was by
contracted rate.

**Predictions, added to the pre-registration above, not replacing it:**
1. SVT row: **0** unit-rate breaches and **1** standing-charge breach. Off-list pre-cap SVT terms go from 2,490
   to **0**.
2. Pre-cap SVT revenue ex-VAT falls by **£5k-£12k**, to between £334.8k and £341.8k. The bill count moves
   only through second-order churn, so it stays within ±2% of 8,950.
3. EPG row: **373 ±15**. The gate does not reach the 2022-23 cap era, because the clamp already made those
   rates one price. Any move is second-order: a different book means different households in the window.

## The predictions, graded on the fresh 3dc5a92948 book (2026-10-30)

All three **held**:
1. SVT row 0 on the unit rate and 1 on the standing charge (SYN-2016-101g gas, Mar 2018, still untraced). Off-list
   pre-cap SVT terms 2,490 -> 0.
2. Pre-cap SVT revenue ex-VAT 346,790.28 -> 340,391.67 (-6,398.61) on 8,950 bills.
3. EPG row 373.

The exception's ceiling is now 1. The full grade is in `docs/staging/records/SEAT_RECORD_THE_3DC5A92948_BOOK_GRADED_AND_ITS_PAGES_BUILT_2026-10-30.md`.
