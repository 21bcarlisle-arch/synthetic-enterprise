**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# The 3d3a8ee691 book's 475 invariant breaches, decomposed by account, and the first cause fixed

Found by the autonomous worker on 26 Nov 2026, on the publish-gate wedge draw. The publisher has
refused `docs/reports/run_output_3d3a8ee691_20261125T215702Z.json` three times since 23:56Z on 25
Nov on the domain-invariant gate (rc=82, `domain_invariant_refused`). No test is implicated. The site
has shown the 18 Nov book (6af7fd0bfd) under the "verification paused" banner since 23 Nov.

BLOCKING: the next book is refused unless every class below is cleared or excepted.

## Reproduced

`tools/domain_invariant_runner` evaluators over `docs/state/billing_ledger.json` and
`site/data/customers` give the same counts as `docs/reports/DOMAIN_INVARIANTS.md`. Full breach lists:
the probe below, which removes the runner's five-example limit.

## Measured: what is new in the book

The book is a different population, not the same one with new code. It has 1,382 accounts against
the 20 Nov book's 1,306: 330 added (270 PROS, 50 OCC, 10 SYN `_3` won switches) and 254 dropped.
Fresh-market wins are billed from f80fe39511 on. Before that commit, a win was registered and never
supplied.

| invariant | breaches | on accounts new to this book | distinct accounts |
|---|---|---|---|
| INV_UNIT_RATE_EPG_HOUSEHOLD | 361 (ceiling 350) | 99 | 193 |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 44 | 11 | 17 (C6 among them) |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 14 | 14 | **2** |
| INV_PPM_NOT_CREDIT_BILLED | 12 (excepted) | 0 | 1 (C6) |
| INV_EBSS_CREDIT_EACH_MONTH / _ON_THE_BILL | 10 / 10 (ceiling 7) | 5 / 5 | 8 |
| INV_PERIODS_CONTIGUOUS | 9 | 9 | **2** |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 8 | 0 | 1 (SYN-2016-099) |
| INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT | 8 (1 outside class) | 2 | 8 |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR | 7 (ceiling 1) | 5 | 7 |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 6 (excepted) | 2 | 5 |
| INV_OPENING_IS_THE_PREVIOUS_CLOSING, _BILLED_EX_VAT_RECONCILES, _CLOSED_ACCOUNT_BALANCE_REACHES_ZERO | 1 each | 1 each | **SYN-2016-175_3** |
| INV_OVERDUE_WITHIN_BALANCE | 1 | 0 | SYN-2016-107 |

## Cause 1, fixed in this commit: a won switch's dwelling was never looked up

All 12 entries in the ledger's `exception_queue` belong to two accounts:

- SYN-2016-175_3, a fresh-market win at SYN-2016-175's dwelling. That dwelling is drawn and listed.
- OCC-d5419b4a0f6e, the incoming occupant of SYN-2016-175_3 (`occupier_successions`).

The premise runs at about 2,100-3,500 kWh a month. Both ceiling checks hold those bills:
`vat_by_segment` implied-VAT, and the `slc_6_7` resi plausibility check.
`release_confirmed_domestic` releases such a bill only if `premise_council_tax_listed` is True.
`simulated_council_tax_listing` resolved the address through `incoming_occupant_of` only. A win's link
is `successor_of`. `make_acquired_customer` clones the predecessor's premise: "it IS the same
property". So both accounts read None, and every held month stayed out of the book.

That one hole produces the breaches above on these two accounts in six invariants: 9 contiguity, 1
opening/closing, 2+2 EBSS, 14 carbon panel, 1 revenue reconcile, 1 closing balance.

The fix: `_supply_address_of` follows `successor_of` as well, over the whole live roster. Control:
`test_a_won_switch_and_its_occupier_are_asked_about_the_dwelling_the_win_was_made_at`. It goes red
with the `successor_of` leg removed (mutation checked), and an unlisted win still reads None.

**Prediction, written before any book carries the fix.** On the next book, the eight actual-read
holds on SYN-2016-175_3 release: 2019-03, 2019-12, 2021-02, 2022-01, 2022-12, 2023-03, 2023-12 and
2024-01. Three stay held because they are estimates: SYN-2016-175_3 2019-01, and OCC-d5419b4a0f6e
2024-12 and 2025-01. The 2021-03 `slc_6_7` reconciliation hold (7,346 kWh advance against 1,803.7
billed) is expected to clear once 2021-02 issues, but I cannot yet say that it will. OCC's two estimate
gaps will still breach contiguity and the carbon panel. That is a separate question: an estimate over
the ceiling at a listed dwelling, with no actual read in its tenure.

## Still open, in the order to take them

1. **INV_UNIT_RATE_EPG_HOUSEHOLD, 361 against a ceiling of 350.** The breach rate fell: 10.8% of 3,337,
   against 11.1% of 3,163 when the ceiling was set. The count rose because the book grew. The examples
   sit 0.002-0.009p above 32.381p, the exception's documented print scatter. The ceiling is a count
   keyed to one book's size. That is the "key a control to today's answer" shape: it refuses a
   larger, cleaner book. Either fix its `retired_by` (price the energy line on the printed kWh) or key
   the exception to a share. Decide which; do not raise the number.
   **Taken 26 Nov, keyed to the class.** The cause is measured. The printed kWh is the difference of
   two reads, each printed to a tenth, so it can sit up to 0.1 kWh off the volume the energy line was
   priced on. The printed rate then moves by up to rate x 0.1 / kWh. All 362 of the cb93f7760c
   book's 362 breaches sit inside that bound, and none sits past it. The evaluator now labels a
   breach inside the tenths `printed_kwh_off_the_priced_kwh_by_the_two_read_tenths`. The exception
   lifts that class only, and `max_breached` is dropped. A breach past the tenths carries no class
   and refuses. Control: `test_an_epg_breach_is_labelled_read_tenths_only_inside_the_tenths`. Both
   legs were mutation-checked: dropping the label goes red, and so does labelling every breach.
   `retired_by` is unchanged. Pricing the line on the printed kWh still retires the row.
   Re-graded on the same book with the change, the gate no longer names this row.
2. **EBSS 10 against 7, on 8 accounts (6 OCC).** Monthly EBSS credits of 0 on OCC bills in Oct
   2022-Mar 2023. Check whether an occupier admitted mid-scheme is outside the EBSS crediting loop.
   **Read 26 Nov on the cb93f7760c book: all 8 are the two excepted classes, and the 7 ceiling is a
   count.** The three accounts new to the list read as follows in the run's bills.
   OCC-c38d3a6ca700 2022-10 has occupier_share 0.90 and occupier_scheme_month_credit_gbp 66.
   OCC-cbaae9bbd3fa 2022-10 has occupier_share 0.62 and the same 66. On both, the unnamed
   occupier's deemed account took the 1 Oct credit and the payer was named later that month.
   `account_held_from` is July on both, so the first-period date is not the naming date.
   OCC-33c7f31198b0 2023-02 has occupier_share 0.84 and void_owner_share 0.16, which is a void on
   the 1st. The fix has the EPG shape: label the class in the evaluator and key the exception to
   it. Labelling needs the period's occupier and void shares in the raw export, which carries
   neither today. That is the exception's own `retired_by`, and a real supplier holds its deemed
   window. Build that next. Do not raise 7.
3. **INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS, 44 on 17 accounts, no exception.** New in this
   book. Check whether D48's `same_period_estimate` (11a4387c6f, default off) or the BSC blend moved
   this.
   **Taken 26 Nov: the BSC blend moved it, and the row graded a policy the company no longer
   declares.** All 44 are electricity quote-rung bills. Each meter prints two flat annual figures, one
   on each side of its first actual read. For example, OCC-5c90c6dd919a reads 37.4 for Oct 2024-Jan
   2025, then has a Feb read, then reads 32.3 for Mar-Jun. Since 2026-11-20, every standing policy has
   blended a hold-route PC1/PC3 electricity month's registry EAC toward the held reads at SPAR 0.5
   (`bill_estimate_blends_the_eac_at_spar`). So on the quote rung, a read moves the figure. The row
   still took one median per meter. `same_period_estimate` is off and is not the cause. The row now
   declares `quote_figure_moves_at_each_read` (electricity, PCs 1 and 3, held equal to the company's
   switch and `BSC_BLEND_PROFILE_CLASSES` by the control), and takes the median per read segment.
   Re-graded on the same book: 0 of 30,768, against 44 of 30,927. The 159 bills that are no longer
   graded each sit alone in their segment, so no figure in force can be compared with them. That is a
   real loss of coverage. Grading them would need the blend's own value, and FYC is not on the page.
   Control: `test_a_read_moves_the_quote_figure_where_the_supplier_blends_the_eac_toward_it`. Three
   mutations go red: one segment for all bills, one segment per bill, and dropping `profile_class`
   from `load_printed`. A step inside a segment, a PC2 meter and gas still breach.
4. **INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR, 7 against 1.** Five are on new PROS gas legs.
   b3f3a23f6f re-based gas AQ registration, which may be the cause.
   **Read 26 Nov on the cb93f7760c book: not the excepted class, and not a missing cell.** The six legs
   are PROS-2017-0192g (9 repeats), PROS-2021-0396g (9), PROS-2023-0104g (8), PROS-2023-0169g (4),
   PROS-2023-0234g (4) and SYN-2016-206g (4), plus the book share at 1.29% against a 1% bound. The
   exception covers warm 31-day months on the population split. PROS-2017-0192g instead repeats every
   measured month from 2018-07 to 2019-03 to 0.1 kWh, heating months included: Dec 2479.3, Jan 2535.9,
   Feb 2057.8, Mar 2131.0, the same as the year before. In a standalone probe after
   `adopt_book(GAS_CUSTOMERS)`, the leg resolves cell E484N0156 with 3,653 days, and `get_hdd` differs
   between Jan 2018 and Jan 2019 (8.52 against 10.52). So the run's settled HDD for the leg cannot be
   what the probe reads. The next step is the run's own daily settlement rows for this leg: whether the
   leg's term was settled through `run_gas_term`, or its reads were made some other way (b3f3a23f6f's
   AQ rewrite is one candidate). I cannot yet say which.
   **Taken 26 Nov: five of the six legs sit in cells the committed store does not hold, so they read
   the climate normal.** The book's months for PROS-2017-0192g follow the normal's shape to three
   decimals (Aug/Jul 1.041, Feb/Jul 5.958) and not the cell's (1.248, 11.61). The run printed it as
   `population_70_30_split` with "no fabric trace". The earlier standalone probe resolved a cell only
   because it read the WORKING-TREE store. Someone had run `tools.build_weather_world --build` at 01:24
   on 26 Nov and left the result uncommitted: 1,091 cells against HEAD's 919. The publisher runs on
   committed bytes. E484N0156, E514N0187, E521N0270, E320N0566 and E440N0550 (PROS-2017-0192g,
   -2021-0396g, -2023-0104g, -2023-0169g, -2023-0234g) are new in that build and absent at HEAD.
   SYN-2016-206g's cell E529N0173 is held, and its repeats are warm months (Jul 2019, Jun-Jul 2022,
   Jul 2023), which is the excepted class. This is the fc3129a861 class again: the 330 accounts new
   to the book brought premises beyond every held cell.
   The orphaned build also pulled ERA5 wind, cloud and precipitation from Open-Meteo for 243 held
   cells. Its held temperatures are byte-identical to HEAD's. That is a wider change that would give
   243 premises a fabric trace, so it is not landed here. It stays in the working tree for whoever
   owns it. What lands is fc3129a861's own remedy, `--build --limit 0`, run in a clean worktree
   from HEAD's store: the HadUK temperature pass from the local grids, with nothing fetched.
   **Prediction, filed before any book carries it:** on the first fresh book at or after this commit,
   the five PROS legs stop repeating. INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR falls to 1 or
   fewer leg breaches (SYN-2016-206g), and the book share drops below its 1% bound. If any of the
   five still repeats, this attribution is wrong.
5. SYN-2016-099 (8 page-overdue breaches), SYN-2016-107 (1), and the 1 closing refund outside its
   class. Each is a single account; read each one.
   **Read 26 Nov, not fixed.** SYN-2016-099: the household's credit of 15.89 covered the 0.62 final
   bill and 15.27 of the February bill, which left 1.30. A 0.62 payment on 16 Mar then took the page
   to 0.68 owed. Every dunning step, and the write-off, still says 1.30: the desk's overdue sum does
   not net that payment. SYN-2016-107: the page shows the August electricity bill (due 14 Sep)
   unpaid until 22 Oct, and the page twin grades it fine. The raw-ledger row says nothing was overdue
   on 16 Oct. So the raw export and the page disagree about when that bill was paid.

## Probe

`/tmp/seat_inv/probe.py`, not committed. It wraps `EVALUATORS` to keep `t.breaches` whole, then runs
`load_book(ledger_path=OUT_PATH, printed_path=site/data/customers)`.

## Where it stands (worker tick, 26 Nov 15:00Z)

Every numbered cause above is taken at origin. Item 5's two accounts were fixed later:
SYN-2016-099 by d688a224a6 (issue order) and SYN-2016-107 by 91c32797b3. The 14:55Z publisher cycle
re-graded the 91c32797b3 book and refused it on the same three rows the 001e4f680a finding's 14:50Z
grading attributes to fixes that landed after that run: OVERDUE_WITHIN_BALANCE 1 (PROS-2019-0305),
PAGE_BALANCE 8 (SYN-2016-099), refund 1 outside class (PROS-2023-0338g, 7f90f9563a). No book run at
or after e4dda28119 exists yet. sim_runner is holding until about 15:50Z, so its next run will be
at HEAD. Neither this item's predictions (Cause 1, item 4) nor that finding's can be graded before
that book exists. I did not start a run beside the live publisher. Parked to 27 Nov: grade the
predictions on that book, then close or reopen.

## Graded on the 76f894811d book (delivery seat, 26 Nov 2026 21:5xZ)

Book: `run_output_76f894811d_20261126T155009Z.json`, 1,382 accounts, 54,463 bills. It descends from
7f90f9563a, d688a224a, 91c32797b3, 9ed3dc9787 and e4dda28119. Its ledger was written in a clean
checkout of 76f894811d (fcd2facdcd's route; sim-runner-log 21:02Z). The publisher's own gate,
`docs/reports/DOMAIN_INVARIANTS.md` at 21:11Z, reads **0 unexcepted breaches across 0 invariants, 6
excepted: the publish stands.** I re-ran the same runner (`load_book` with the printed customer files,
then `run`, then `gate`) on a snapshot of that ledger and the completed customer files. It
reproduced the table row for row. Probe outputs: `/var/tmp/grade76/` (not committed).

| prediction (item 4, filed here) | measured | grade |
|---|---|---|
| The five PROS legs stop repeating | PROS-2017-0192g 0 of 9 pairs, PROS-2021-0396g 0 of 27, PROS-2023-0104g 0 of 13, PROS-2023-0169g 0 of 8, PROS-2023-0234g 0 of 9. All five are on the book and graded | **held** |
| INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR at most 1 leg breach (SYN-2016-206g) | 1 breach, SYN-2016-206g: 4 repeats, 2019-07, 2022-06, 2022-07 and 2023-07, all warm months. Flags: PROS-2016-0188g 2, SYN-2016-258g 2 | **held** |
| Book share below its 1% bound | 14 repeats in 3,808 pairs, 0.37% | **held** |

Cause 1 (the actual-read holds) was graded on cb93f7760c. This book's ledger again holds no held bill
that breaches contiguity: INV_PERIODS_CONTIGUOUS is 0 of 107,544.
