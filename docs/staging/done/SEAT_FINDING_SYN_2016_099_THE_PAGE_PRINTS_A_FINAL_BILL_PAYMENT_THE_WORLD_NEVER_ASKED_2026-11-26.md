**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# SYN-2016-099: the page prints a final-bill payment the world never asked for, so the desk is right and the page is wrong

The autonomous worker found this on 26 Nov 2026, working item 5 of
`SEAT_FINDING_THE_3D3A8EE691_BOOKS_475_INVARIANT_BREACHES_DECOMPOSED_AND_THE_FIRST_CAUSE_FIXED_2026-11-26.md`.
This finding covers `INV_OVERDUE_WITHIN_PAGE_BALANCE`, 8 breaches, all on SYN-2016-099. It refuses
the publish on its own, with no exception.

BLOCKING: the next book refuses while this row breaches.

## What the earlier reading said, corrected

Item 5 read it as "the desk's overdue sum does not net that payment". **That reading is wrong.** Every
`collections_snapshot` path caps the overdue sum at the desk ledger's own balance (`age_balance`,
`age_left_level`, `level_shortfall`). So the desk's ledger really does hold 1.30. The desk is right
and the page is wrong: the 0.62 payment the page prints on 16 Mar 2017 was never collected.

## Measured (3d3a8ee691 book, `world_walk_truth_3d3a8ee691_20261125T215702Z.json`)

Electricity leg, level DD, non-renewal churn on 2017-03-02:

| issued | page line | page running balance |
|---|---|---|
| 2017-02-10 | level DD 15.95 | -15.89 |
| 2017-03-02 | INV27115, final bill, 1 Mar only, 0.62 | -15.27 |
| 2017-03-05 | INV27114, February bill, 16.57 (read delay 3 days, so issued **after** the final bill) | 1.30 |
| 2017-03-16 | "Payment received" 0.62 | 0.68 |

The world's `final_month_nets` row for this bill reads `ledger_balance_gbp -15.89`,
`credit_taken_gbp 0.62`, `ask_gbp 0.0`, `netted_ledger_credit true`, `result success`. On 2 Mar the
leg held 15.89 of level surplus, because the February bill was not issued until 5 Mar. So the world
netted the final bill out of that credit and presented nothing (`nothing_due`). The desk's ledger
has no cash after 10 Feb, so it owes 0.62 + 16.57 - 15.89 = **1.30**. That is the figure the desk
chased and wrote off.

The page takes the triad's `success` for the month (`wpt.truth_outcome`) and pays the bill at its
face (`arrears_engine._resolve_bills`: `amount = payer_ask_gbp(bill)`, with no world ask carried).
The walk runs in period order, so the February bill's 0.62 shortfall against its level collection
has already spent the surplus. The walk therefore asks the final bill at face and prints a 0.62
payment that the world never moved. Page closing balance (`closing_balances`): 0.68. World and
desk: 1.30.

## The class, counted

Of the 265 final bills in the book where the world netted ledger credit and the collection
succeeded, **2** print a non-level payment above the world's ask:

- **SYN-2016-099** 2017-03: face 0.62, asked 0.00, page paid 0.62. The cause is issue order: an
  earlier period was billed after the final bill. This one breaches.
- **SYN-2016-244** 2018-01: face 52.26, asked 25.55, page paid 52.26, then refunded 26.71 on 2 Feb.
  The net cash is the same (25.55) and both sides close at 0, so no invariant breaches. But the page
  prints 26.71 more cash in, and a refund the world never made. The leg was on receipt
  (`standard_credit`) by then, and the walk holds the level surplus to the close instead of netting
  it against the paid final bill. That is a different shape with the same root: the page does not
  read what the world asked.

Probe: inline, not committed. It joins `final_month_nets.rows`, filtered to `netted_ledger_credit`
with `result == success`, to `docs/state/billing_ledger.json` payments on the same leg and month
where `level_dd` is false.

## Recommended fix (not built this turn; why)

Fix the class with one rule: **the page prints the cash the world asked on a final bill.**
`world_payment_truth.build` already carries `debit_asked_gbp` from `final_month_nets` into the told
outcome. Carry `credit_taken_gbp` the same way. In `_resolve_bills`, a told success on that month
pays `face - credit_taken + debit_asked`. Then `balance_settlement_from_outcomes` must post
`credit_taken` as a credit against that bill, met out of the level surplus or left owed if the walk
has already spent it. That is SYN-2016-099's 0.62, which the page then owes at 1.30 like the desk.
The second half is what makes this bigger than one bounded turn. The walk's level surplus is
`level_collection_difference`, not a credit event, so netting it against a paid bill touches the
close, the refund clock and `INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`.

There is an alternative on the world side, and it is the practitioner question here. Should a final
bill be issued before the previous period's regular bill? A real supplier's final bill normally
covers everything since the last bill issued. A February bill raised three days after the final
bill is a shape the world may simply be wrong to produce. The fix that would settle it is: a final
bill is issued no earlier than the leg's last regular bill. That fixes SYN-2016-099 at its origin,
but not SYN-2016-244. GAP: I found no published source either way, and none was searched this turn.
Check the knowledge layer (`docs/market_research/` final bills, home moves s.8.8) before choosing.

**Prediction, written before any fix:** with the page-side rule, SYN-2016-099's page closes at
1.30. The 8 `INV_OVERDUE_WITHIN_PAGE_BALANCE` breaches go to 0. SYN-2016-244 stops printing the
26.71 refund. No other leg in the 265 moves its closing balance.

## Not covered here

SYN-2016-107 (`INV_OVERDUE_WITHIN_BALANCE`, 1) and PROS-2023-0338g (the 1 closing refund outside
its class) stay with the delivery seat's chain claim (`the-epg-exception-is-keyed-to-a-share-not-a-count`).

## Disposition (worker, 26 Nov 2026): fixed at the world, d688a224a

The world-side alternative was taken. A leg's bills are now issued in period order:
`simulation/arrears_engine.bill_issue_date` issues a bill no earlier than the leg's three preceding
month-end bills (`home_moves.md` s.8.8h choice 32, strong logic, GAP on any published bill-run
ordering rule). SYN-2016-099's final bill is now issued with its February bill on 5 Mar. The
world's net then reads February's debit (same-day issue counts, `_leg_balance_on` `<= on`). On the
current ledger, 54 of 54,278 bills move, and every one is a stub that had been issued before an
earlier-period bill on its own leg.

**Prediction, unchanged from above for this leg:** on the next book, INV_OVERDUE_WITHIN_PAGE_BALANCE
goes from 8 to 0, and SYN-2016-099's page and desk close on the same balance. SYN-2016-244 is not
fixed by this. It is split out as
`SEAT_FINDING_SYN_2016_244_THE_PAGE_PRINTS_A_FINAL_BILL_REFUND_THE_WORLD_NEVER_MADE_2026-11-26.md`.

## Graded on the 76f894811d book (delivery seat, 26 Nov 2026 21:5xZ)

Book: `run_output_76f894811d_20261126T155009Z.json`, 1,382 accounts, 54,463 bills. It descends from
7f90f9563a, d688a224a, 91c32797b3, 9ed3dc9787 and e4dda28119. Its ledger was written in a clean
checkout of 76f894811d (fcd2facdcd's route; sim-runner-log 21:02Z). The publisher's own gate,
`docs/reports/DOMAIN_INVARIANTS.md` at 21:11Z, reads **0 unexcepted breaches across 0 invariants, 6
excepted: the publish stands.** I re-ran the same runner (`load_book` with the printed customer files,
then `run`, then `gate`) on a snapshot of that ledger and the completed customer files. It
reproduced the table row for row. Probe outputs: `/var/tmp/grade76/` (not committed).

| prediction (filed here) | measured | grade |
|---|---|---|
| INV_OVERDUE_WITHIN_PAGE_BALANCE 8 -> 0 | 0 of 5,630 | **held** |
| SYN-2016-099's page and desk close on the same balance | The world asks 1.30 at the final bill (0.62 face plus 0.68 debit) and collects it on 20 Mar 2017. Page closing balance 0.00. The desk opens no journey and writes nothing off | **held** |
| (page-side rule) the page closes at 1.30, and SYN-2016-244 stops printing 26.71 | the page-side rule was superseded by d688a224a and never built | not graded |

SYN-2016-244 still prints the 26.71 closing refund on this book, where the world asked 25.55 and took
26.71 of credit. That belongs to its own finding
(`SEAT_FINDING_SYN_2016_244_THE_PAGE_PRINTS_A_FINAL_BILL_REFUND_THE_WORLD_NEVER_MADE_2026-11-26.md`).
