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
2. **EBSS 10 against 7, on 8 accounts (6 OCC).** Monthly EBSS credits of 0 on OCC bills in Oct
   2022-Mar 2023. Check whether an occupier admitted mid-scheme is outside the EBSS crediting loop.
3. **INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS, 44 on 17 accounts, no exception.** New in this
   book. Check whether D48's `same_period_estimate` (11a4387c6f, default off) or the BSC blend moved
   this.
4. **INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR, 7 against 1.** Five are on new PROS gas legs.
   b3f3a23f6f re-based gas AQ registration, which may be the cause.
5. SYN-2016-099 (8 page-overdue breaches), SYN-2016-107 (1), and the 1 closing refund outside its
   class. Each is a single account; read each one.

## Probe

`/tmp/seat_inv/probe.py`, not committed. It wraps `EVALUATORS` to keep `t.breaches` whole, then runs
`load_book(ledger_path=OUT_PATH, printed_path=site/data/customers)`.
