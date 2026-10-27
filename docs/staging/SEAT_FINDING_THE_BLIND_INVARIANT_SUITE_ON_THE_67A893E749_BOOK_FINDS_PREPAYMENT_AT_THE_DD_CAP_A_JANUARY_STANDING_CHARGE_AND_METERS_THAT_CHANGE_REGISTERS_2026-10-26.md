**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `price-cap` -- `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`

# SEAT FINDING: the blind invariant suite, run on the 67a893e749 arm-A book, finds prepayment billed at the DD cap, a standing charge that moves on 1 January, and meters that change register count under one serial

This is step 4 of `docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`,
done as far as the direction asked (delivery lane, `the-domain-invariant-suite-is-written-blind-and-run-on-the-book`).
It is **not wired into the publish gate**. That waits until each breach class below is fixed or named
as a dated exception.

## What was built

- **`docs/design/DOMAIN_INVARIANTS.yaml`**: 33 invariants, 201 rows, each row with a source locator or
  a named GAP. It was written by an agent that read only `site/knowledge/`, `docs/market_research/`
  and `docs/domain_artefact_library/`. Its `meta.files_read` lists every file it opened, and
  `meta.blindfold_disclosure` names the code constants it saw quoted inside research notes and did
  not use. It is committed **verbatim**: nothing in it was changed after the results were seen.
- **`tools/domain_invariant_runner.py`**: reads only the raw export
  (`company.billing.raw_account_export`, its one repository import, held by a test). It prints
  breaches (the file's `breach` severity) and flags (its `flag` severity) per invariant, each over
  its own denominator. An invariant it cannot run reports UNCHECKABLE, NOT_IN_EXPORT,
  NO_EVALUATOR or UNREACHED, never clean.
- **The agent corrected the brief.** I had written "a read at least every two years". That was
  the inspection duty, repealed from April 2016. For 2016–2025 the duty is SLC 21B.4, which requires
  all reasonable steps to obtain a reading at least once a year. That is a duty of effort, so the
  file grades it as a flag.

## The book

- Arm A of the mandate run (`/var/tmp/mandate-run-out-67a893e749`, origin 67a893e749, seed 42,
  default book).
- The ledger was rebuilt into `/tmp` by the trunk's generator at 884eedc669, because 67a893e749's
  generator exports no `contracted_terms`. The raw export was then taken for every account.
- Nothing was committed from the book. Scripts are in `/tmp/inv/scripts/`.
- Size: **1,291 accounts** (1,289 domestic, 2 SME), 52,782 bill periods.
- **An account is one fuel on one meter.** The export carries no household link. So the file's
  heating-class proxy ("the same customer_id also holds gas") is never true, and the all-domestic
  band is used.

## The breach table

| invariant | status | breached | flagged | checked |
|---|---|---|---|---|
| INV_UNIT_RATE_SVT_ELEC | BREACHED | 496 (9.2%) | 0 (0.0%) | 5392 |
| INV_UNIT_RATE_SVT_ELEC_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 2291 |
| INV_UNIT_RATE_SVT_GAS | CLEAN | 0 (0.0%) | 0 (0.0%) | 4713 |
| INV_UNIT_RATE_SVT_GAS_PRE_CAP | CLEAN | 0 (0.0%) | 0 (0.0%) | 1768 |
| INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER | BREACHED | 501 (94.7%) | 0 (0.0%) | 529 |
| INV_UNIT_RATE_FIXED | FLAGGED | 0 (0.0%) | 8 (0.6%) | 1339 |
| INV_UNIT_RATE_EPG_HOUSEHOLD | UNCHECKABLE | | | |
| INV_STANDING_CHARGE_SVT_ELEC | BREACHED | 2986 (14.0%) | 0 (0.0%) | 21305 |
| INV_STANDING_CHARGE_SVT_GAS | BREACHED | 4226 (25.7%) | 0 (0.0%) | 16468 |
| INV_STANDING_CHARGE_FIXED | CLEAN | 0 (0.0%) | 0 (0.0%) | 16111 |
| INV_ANNUAL_USE_ELEC_ACCOUNT | FLAGGED | 0 (0.0%) | 12 (0.7%) | 1751 |
| INV_ANNUAL_USE_GAS_ACCOUNT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1422 |
| INV_ANNUAL_USE_BOOK_MEDIAN | CLEAN | 0 (0.0%) | 0 (0.0%) | 12 |
| INV_READ_DUTY_ANNUAL | FLAGGED | 0 (0.0%) | 310 (27.5%) | 1126 |
| INV_SETTLEMENT_ACTUAL_SHARE_ELEC | FLAGGED | 0 (0.0%) | 1 (100.0%) | 1 |
| INV_BILL_AT_LEAST_TWICE_YEARLY | CLEAN | 0 (0.0%) | 0 (0.0%) | 46403 |
| INV_OPENING_READ | CLEAN | 0 (0.0%) | 0 (0.0%) | 1291 |
| INV_PAYMENT_PPM_AND_DD_NOT_CONCURRENT | CLEAN | 0 (0.0%) | 0 (0.0%) | 1291 |
| INV_PAYMENT_AMOUNT_SIGN | BREACHED | 83 (0.2%) | 23 (0.1%) | 43489 |
| INV_DD_CADENCE | FLAGGED | 0 (0.0%) | 77 (0.2%) | 35003 |
| INV_DD_STEP_CHANGE | FLAGGED | 0 (0.0%) | 1529 (4.2%) | 36139 |
| INV_PPM_NOT_CREDIT_BILLED | UNCHECKABLE | | | |
| INV_FUEL_IDENTIFIER | CLEAN | 0 (0.0%) | 0 (0.0%) | 52782 |
| INV_GAS_SINGLE_REGISTER | CLEAN | 0 (0.0%) | 0 (0.0%) | 584 |
| INV_CROSS_FUEL_PRICE_SCALE | CLEAN | 0 (0.0%) | 0 (0.0%) | 9856 |
| INV_EV_ADOPTION_ELECTRICITY_ONLY | UNCHECKABLE | | | |
| INV_PERIODS_CONTIGUOUS | BREACHED | 1 (0.0%) | 0 (0.0%) | 104273 |
| INV_BACK_BILLING_12M | FLAGGED | 0 (0.0%) | 188 (0.5%) | 37538 |
| INV_PERIOD_CONSUMPTION_NON_NEGATIVE | CLEAN | 0 (0.0%) | 0 (0.0%) | 54198 |
| INV_READ_MONOTONIC | BREACHED | 29 (0.2%) | 0 (0.0%) | 17026 |
| INV_PERIOD_MATCHES_READS | NOT_IN_EXPORT | | | |
| INV_VAT_RATE | NOT_IN_EXPORT | | | |
| INV_NON_COMMODITY_WITHIN_ALL_IN | NOT_IN_EXPORT | | | |

The units are in the runner's `--json` output: term × cap window, bill period, account-year,
account, or pair of reads.

## What each breach is, measured rather than argued

**1. Prepayment accounts are charged the direct-debit cap unit rate, which is above the prepayment cap**
- Covers all 496 of `INV_UNIT_RATE_SVT_ELEC`.
- Every breaching term-window belongs to an account whose payments in that window are all
  prepayment.
- The rate is the DD cap level to within 0.2% in every window. It sits 1.8–4.1% above the
  prepayment column, from Apr 2020 to Apr 2025: 15 windows, roughly 25–58 term-windows each.
- Against the DD column, no window breaches.
- The 26 Oct cap check (`SEAT_FINDING_THE_DEFAULT_TARIFF_TERM_RATE_AGAINST_THE_PUBLISHED_CAP`)
  found 0 above. It graded every term against the DD level and named payment method as what it
  could not see. This is that blind spot, measured.
- **A real defect.** SLC 28AD bounds a prepayment default tariff by the prepayment level. The
  world prices every SVT at the GB direct-debit level whatever the payment method.
- **Gas too (added 2026-10-27).** The suite could not see gas prepayment until the commons carried
  the gas cap per payment method. On the same book, `INV_UNIT_RATE_SVT_GAS` now breaches 462 of
  4,713. All of them are prepayment (462 of 581 prepayment term-windows), at 1.2–5.0% over the
  prepayment column. Pre-registration and result:
  `records/SEAT_PREREGISTRATION_THE_BLIND_SUITES_GAS_UNIT_RATE_ROWS_TAKE_THE_COMMONS_GAS_FLOOR_AND_NON_DD_CEILINGS_2026-10-27.md`.
  A fix to the pricing must therefore cover both fuels.
- **Fixed 2026-10-27, both fuels.** The run loop now re-prices each domestic SVT segment at
  min(its payment method's cap column, the published DD level), with the method read from the
  company's own register on the segment's first day. K8 page:
  `docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`, choice 6. Test:
  `tests/simulation/test_a_prepayment_default_tariff_is_priced_at_the_prepayment_cap.py`.
  - The book was re-priced offline through the new reader. The old reader reproduces every
    capped-window SVT rate; its only misses are 2016–18 pre-cap rows, which the fix does not touch.
    The register's method matched the book's payments on 39,417 of 39,417 rows.
  - Result: `INV_UNIT_RATE_SVT_ELEC` **496 → 0**, `INV_UNIT_RATE_SVT_GAS` **462 → 0**.
    `_MULTI_REGISTER` 501 → 493, all of it class 3. The pre-cap rows and floor flags stay at 0.
  - The rate is applied at run time, so the closing reading needs a fresh run.
  - Named remainders:
    - `_account_state_svt_rate` (the company's "own default tariff" a fix is compared against)
      and the re-fix log's `withdrawn_default_rates` still read the DD level for a prepayment leg.
      Both are comparison readers, not billed rates, and both overstate a prepayment household's
      alternative by about 1–5%.
    - A meter moved to prepayment for debt is not on the method register (a GAP on the page;
      that route ships at 0).

**2. The SVT standing charge changes on 1 January, not when the cap does**
- Covers `INV_STANDING_CHARGE_SVT_ELEC` (2,986 breaches) and `_GAS` (4,226).
- For electricity, the charge sits at £0.24/day from Jun to Dec 2021, then jumps to £0.40/day on
  **1 Jan 2022**. The April 2022 level arrived three months early. Against a Jan–Mar 2022 DD cap of
  £0.2368/day, that is **1.7× the cap** on 538 bill periods.
- The smaller breaches (2–11%) fall wherever the cap moved during a calendar year and the
  charge did not follow. For example, Apr 2025 electricity: cap £0.4963/day, charged £0.512/day.
- The gas ratios (1.00–1.04, DD-only windows) fit the same mechanism. I have **not** traced gas
  period by period, so for gas the mechanism is a reading, not a measurement.
- **A real defect**, and crisis-relevant: it puts revenue into the Jan–Mar 2022 quarter. Under the
  ruling's step 2 ("mark every published figure that moves"), the crisis P&L needs re-running once
  this is fixed.

**3. Meters that change register count under one serial**
- Covers all 501 of `INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER` and all 29 of `INV_READ_MONOTONIC`.
- 97 electricity accounts ever show two registers. **66 of them switch** between one register and
  two under the **same `meter_serial`**: 45 switch once, 21 switch 2–4 times. The register readings
  jump at each switch.
- Example: C7 reads 18,568.6 on its single register on 31 Dec 2017. It reads 2,140.6 / 6,156.5 on
  two registers from 1 Jan 2018, and 27,879.6 on one register again by Jan 2019.
- All 29 backwards actual-to-actual reads are on these 66 accounts.
- All 501 multi-register "breaches" are their single-register SVT spells, charged the single-rate
  cap. The file classes meter type per account, so those spells are graded against the lower
  two-register ceiling.
- The 31 accounts that always have two registers produce **no** breach.
- **A real defect** in how a meter's registers are made, not a pricing breach. A meter exchange
  would carry a new serial and an opening read.

**4. Payments with no amount**
- Covers all 83 of `INV_PAYMENT_AMOUNT_SIGN`.
- 98 payment records carry `payment_amount_gbp: None`: 68 DD, 17 standard credit, 13 prepayment.
  83 of them are DD or prepayment, so they fall in this invariant.
- A further **218** carry `payment_method: None`. No invariant covers that, and it is named here
  so it is not lost.
- There are also 23 negative DD amounts. The file says how the export encodes a DD return is
  unknown, so they are flags.

**5. One gap between bills**
- `INV_PERIODS_CONTIGUOUS`, 1 of 104,273.
- PROS-2017-0336 has no bill period for 1 Dec 2017 – 31 Jan 2018. Its reads are continuous
  across the gap, so February bills 4,986 kWh in 28 days. The two missing months are folded into
  one bill.
- The same account is 27,309 kWh a year in 2019, the largest flag under
  `INV_ANNUAL_USE_ELEC_ACCOUNT`.

**Flags, which are evidence to explain, not breaches**
- **Read duty (12 months):** 310 of 1,126 credit accounts (27.5%) go more than 366 days without an
  actual read. This agrees with
  `SEAT_FINDING_A_THIRD_OF_HOUSEHOLDS_GO_MORE_THAN_A_YEAR_ON_ESTIMATES_WITHOUT_THE_READ_DUTY_FIRING_2026-10-26.md`.
- **Settlement:** 94.3% of matured electricity kWh is bounded by an actual read, against the
  file's 97% performance standard.
- **Back-billing proxy:** 188 catch-up periods (0.5%).
- **DD step changes over 2×:** 1,529 of 36,139 pairs (4.2%).
- **More than two DDs in a month:** 77 account-months.
- **Fixed terms below their struck-window floor:** 8, all struck Nov 2022 – Jan 2023 against the
  EPG-window floor.
- **Electricity annual use above the NEED p99:** 12 of 1,751 account-years (0.69%). The 99.9%
  upper bound at that n is 1.73%, so no book-level flag.

**And one result the file's one-sided check passes but which is not normal: no heavy gas tail**
- **0 of 1,422** complete gas account-years are above the NEED p99 (34,300 kWh). About 14 are
  expected. Under p = 0.01, the chance of seeing none is about 7×10⁻⁷.
- The book-level check is one-sided (too many above), so it reads clean. A world with no
  heavy-gas homes cannot show what the 2022 crisis did to them.
- I am filing this as a population-calibration question for the world lane, not as a breach.

**What could not be checked, and why (fail closed)**
- **Not in the export:** `INV_VAT_RATE`, `INV_PERIOD_MATCHES_READS` and
  `INV_NON_COMMODITY_WITHIN_ALL_IN` are NOT_IN_EXPORT. No period carries `vat_rate`,
  `consumption_kwh` or `non_commodity_rate_gbp_per_mwh`, although `raw_account_export.FIELDS`
  declares all three.
- **The file says the export cannot answer them:** `INV_UNIT_RATE_EPG_HOUSEHOLD` (the export does
  not say whether its rate is before or after the EPG), `INV_PPM_NOT_CREDIT_BILLED` (no bill
  record) and `INV_EV_ADOPTION_ELECTRICITY_ONLY` (no event stream) are UNCHECKABLE.
- **The ruling's list against the export:** two of its five families, "events consistent with
  the fuels held" and "payment method consistent with billing", cannot be reached from the raw
  export at all. The export would need a bill record with its type and an event stream. That is
  the next export change this suite asks for.

## The predictions, filed at 22:31Z before the invariants file existed, graded as written

- **P1, 0 SVT term-windows above the cap: REFUTED.** 496 are above, all on prepayment accounts
  against the prepayment column. Against DD, 0 held, as the 26 Oct check found.
- **P2, SVT 0 below the floor; fixed >0 below the floor in the 2021–22 crisis: half held.** SVT
  held at 0. Fixed is 8, but none are 2021 fixes: the file grades a fix at the window it was
  struck in, so a pre-crisis fix never meets the crisis floor. The mechanism I predicted was wrong.
- **P3, 5–20% at two years and about a third at twelve months:** the two-year premise was wrong
  (see the correction above). At twelve months it is 27.5%, roughly as predicted.
- **P4, prepayment households with estimated credit bills >0: CANNOT BE GRADED.** The file rules
  it out, correctly: a consumption period on a prepayment account is not a credit bill. My stub
  check had counted estimated reads on prepayment accounts (4,190 of 6,367) and would have filed
  that as the defect.
- **P5, 0 gas periods on electricity-only accounts: HELD,** but trivially, because every account
  is a single fuel.
- **P6, under 2% of account-years outside the outer band: HELD.** Electricity is at 0.69%. Gas is
  at 0%, which is itself finding 5.
- **P7, 0 backwards reads: REFUTED.** There are 29, all on the register-switching accounts.

## What would close this

- **Fix:** (1) the prepayment unit rate against the prepayment cap; (2) a standing charge that
  steps with the cap windows; (3) register changes that come with a meter exchange (a new serial
  and an opening read); (4) the unset payment amounts and methods.
- **Then** re-run the runner on a fresh book (`python3 tools/domain_invariant_runner.py --ledger
  <ledger>`).
- **Each breach left after that** gets a dated exception row. Only then does the runner go into
  the publish gate, as the ruling's step 4 asks.
- **Export:** add the three NOT_IN_EXPORT fields, a bill record, and an event stream, so the
  ruling's two unreached families can run.

## Breach class 2, fixed 2026-10-27: the standing charge now steps on the cap's own dates

**Where it was.** `simulation/policy_costs.py` held each fuel's standing charge as a table keyed
by calendar year. Each row was the day-weighted blend of the cap periods in force that year. A
blend gets a year's total right and every individual day wrong. Every SVT **and fixed** settlement
row read it per day (`hedged_settlement`, `gas_settlement`, `customer_state_layer.as_void_row`),
and the bill sums those rows. `saas/non_commodity.standing_charge_rate` is only a fallback for
records that carry no charge, and nothing in this book reaches it.

**The fix.** The two readers now serve the cap period in force on the date asked, taken from
`docs/domain_artefact_library/regulatory/ofgem_cap_standing_charges.json`. Where two periods
overlap, the one that starts latest wins. The year tables are deleted.

**Gas, traced period by period** (the finding had not done this). It is the same mechanism.
Before the fix, the charge ran from 0.95× to 1.074× the cap depending on the window:
- over the cap in Oct 2020–Mar 2021 (1.031×), Oct 2021–Mar 2022 (1.044×) and Jul–Sep 2025 (1.074×);
- under it in Oct–Dec 2022 (0.957×) and Oct–Dec 2025 (0.951×).

**Electricity before the fix:**
- Oct 2021–Mar 2022 window: **1.698×** the cap (40.22p on every day from 1 Jan).
- Apr–Sep 2022: 0.888×. Oct–Dec 2022: 0.869×.
- Jan–Mar 2024: 1.106×. Jan–Mar 2025: 0.860×.

The full per-window, per-fuel table was printed before the test was written. After the fix,
every day from 2016 to 2025 equals its cap period's figure exactly.

**Tests** (`tests/simulation/test_standing_charge_reproduces_the_cap_model.py`):
- Every run day is charged the cap period in force.
- No day is charged above the blind suite's own DD ceiling row. This covers all 21 capped windows
  for both fuels, graded against `DOMAIN_INVARIANTS.yaml`, not against the artefact the code reads.
- The Jan–Mar 2022 electricity instance is named as its own test.
- Restoring the year blend turns 5 tests red. Adding 0.01p to every period turns 4 red.

**Re-run of the suite.** The charge is applied at **run time**, not at export, so a ledger
regenerated from the 67a893e749 book still carries the old charge. A true closing reading needs a
fresh run.

What was done instead:
1. Every one of the 52,782 bill periods' standing-charge line was re-priced day by day with the
   new reader (`/tmp/svt_sc/reprice.py`, not committed).
2. Before that, the method was checked: the old reader reproduces the printed per-day rate on all
   52,782 periods (0 mismatches).
3. The runner was then run on the re-priced export:
   - `INV_STANDING_CHARGE_SVT_ELEC`: 2,986 breaches → **0** of 21,305.
   - `INV_STANDING_CHARGE_SVT_GAS`: 4,226 breaches → **0** of 16,468.
   - `INV_STANDING_CHARGE_FIXED`: stays clean.

What the re-pricing cannot show is second-order effects. A different bill moves DD amounts,
arrears and the company's later decisions, and only the fresh run will show those.

**What it moves.** Figures are for the standing-charge line, ex-VAT, whole 67a893e749 book. The
published book's own figures will differ in size but follow the same mechanism.

| period | before | after | change |
|---|---|---|---|
| 2022 Q1 | £11,915.88 | £8,535.61 | **−£3,380.27 (−28%)** |
| 2022 Q2 | | | +£993.58 |
| 2022 Q3 | | | +£1,010.46 |
| 2022 Q4 | | | +£1,410.07 |
| FY2021/22 | | | −£3,269.57 |
| FY2022/23 | | | +£2,549.41 |
| FY2024/25 | | | +£2,910.37 |
| calendar 2021 | | | −£6.39 |
| calendar 2022 | | | +£33.85 |
| calendar 2025 | | | +£1,550.28 |

The 2025 change comes from Jan–Mar 2025, which had been charged at the 51.23p blend against a
59.57p cap, and the book ends in mid-2025.

**Published figures that move:**
- every monthly or quarterly revenue and margin series: `dashboard.json` `monthly_ops`,
  `sim_data.json` `monthly` and `bm`;
- any Apr–Mar split;
- the 2025 annual line;
- every Jan–Mar 2022 bill and Explore example;
- per-customer bill totals in any window where the blend and the cap differed.

**Published figures that barely move:** the annual crisis figures for 2021 and 2022. The blend
was right for the calendar year, so they shift by under £40 on this book. This is the honest
reading: the defect moved crisis revenue between quarters, not into or out of the crisis years.

**Not fixed here:**
- Breach class 1. Every account is still charged the DD level. The world has no prepayment or
  standard-credit standing-charge column.
- A fixed term's standing charge still follows the cap per day instead of being held at its
  strike. `INV_STANDING_CHARGE_FIXED` is clean, but that is a separate reading for the D lane to
  take up.

## Breach class 3, fixed 2026-10-27: a register keeps one id and one index for the life of its serial

Pre-registration, filed before the rebuild:
`records/SEAT_PREREGISTRATION_A_METER_REGISTER_KEEPS_ONE_ID_AND_ONE_INDEX_FOR_THE_LIFE_OF_ITS_SERIAL_2026-10-27.md`.

**Correction to the direction that drew this.** The direction asked for register count to be a
property of the meter, changing only through an exchange, with a test that no serial reports two
counts. That premise is wrong for the meters it affects:
- The count follows the TERM. `company/pricing/tou_desk.offers_tou` sells ToU on chosen terms to
  smart and HH meters only, and never on a default tariff. No per-period or per-year draw is
  involved.
- SLC 28AD makes a Multi-Register Tariff a contract "regardless of the metering equipment
  employed". A smart or HH meter is reconfigured for a ToU tariff, not exchanged.
- Smart status is stamped once, at acquisition, so the book holds no mid-account install that
  should have issued a new serial.

So the control is keyed to the property physics fixes: one register id names one register, and an
index never runs backwards. It is not keyed to a count.

**Where the defect was.** `tools/generate_billing_ledger._printed_registers` numbered ToU registers
by their position on the bill (`1` and `2`). The single-rate register was also `1`. A one-band ToU
stub printed its band's label on the total index.

**The fix.**
- Fixed ids: total `1` under every tariff, Peak `2`, Off-peak `3` (`REGISTER_ID`).
- A one-band stub reads its band's own index.
- The raw export takes a stub register's own reads.

**Test.** `tests/tools/test_a_meter_register_keeps_one_id_and_one_index_for_the_life_of_its_serial.py`.
- It asserts that its book reaches one register, two registers and a one-band stub, then:
  one label per (serial, register_id), no index running backwards, and every period's volume
  rebuilt from its own registers.
- On HEAD's unfixed code, 2 of its 4 tests are red. Reverting only the export change reds 1.

**Re-run.** Same 67a893e749 arm-A run, ledger rebuilt by HEAD 00c082202f before and after, so only
the generator differs (`/tmp/regid/`, not committed).

| measure | before | after | predicted |
|---|---|---|---|
| accounts / bill periods | 1,291 / 52,782 | 1,291 / 52,782 | unchanged: held |
| (serial, register_id) carrying two labels | 39 | **0** | >0 then 0: held |
| successive reads on one register going backwards, any read type | 31 | **0** | |
| `INV_READ_MONOTONIC` breaches (actual-to-actual) | 29 | **0** of 16,963 | 29 then 0: held |
| serials printing both one-register and two-register periods | 39 | 39 | about 66 both: count wrong, invariance held |
| `INV_UNIT_RATE_SVT_ELEC_MULTI_REGISTER` | 501 | 501 | about 501 both: held |

Every other invariant row is byte-identical before and after.

- **Register-switching serials: 0 that switch identity. 39 still switch count, and that is
  lawful.** My count (39) is not the finding's 66. Mine counts printed register count per
  electricity period on HEAD's generator. The finding's figure came from 884eedc669's ledger by a
  method I have not reproduced. I cannot yet say which accounts for the difference.

**The 501 are explained, not fixed: a dated exception, 2026-10-27.**
- On the accounts the suite classes as multi-register (two or more register ids on the account),
  all **1,753 of 1,753** SVT periods print one register. All **1,416** two-register periods are
  fixed terms. The other 2 fixed periods are one-band stubs.
- So every breach is a single-rate default spell graded against the multi-register cap. The
  cause is the file's `applies_to.meter` proxy, which is per account.
- The file's own statement ("a multi-register ... default electricity tariff") and SLC 28AD both
  class by TARIFF.
- The same proxy also drops those 1,753 periods from `INV_UNIT_RATE_SVT_ELEC`, so they are
  currently graded against **neither** cap correctly.
- The fix belongs to the runner: class each term by the registers its own periods print. That is
  a marked correction to the blind file's proxy, made beside it, not a quiet rewrite. Handed on as
  the next item.

**Knowledge:** item 7 of `docs/market_research/a_tou_tariff_needs_the_households_choice_not_its_meter.md`
(written in this commit, K8).
