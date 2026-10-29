**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The overdue row's 2,500 steps on the 209c3350ab book, by cause, and a prediction for the next fresh run (2026-10-29)

**Item:** `the-overdue-rows-820-unexplained-steps-on-the-209c-book` (Lane 0, under the correctness
stretch, `DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`). Row:
`INV_OVERDUE_WITHIN_PAGE_BALANCE`. Book: `fresh-run-209c3350ab`, ledger `/var/tmp/wo-grade-209c/ledger.json`.

## The count now agrees with the row

`lag_occ4.py` re-implemented the row, so it counted 2,526 and its classes summed to that. The new
probe (`/var/tmp/overdue820/probe.py`, run from the 209c3350ab worktree) calls the row's own evaluator,
`domain_invariant_runner.ev_overdue_within_page_balance`, on the page records built as `grade.py` builds
them. It returns **2,500 breaches of 19,491 steps**, the row's figure. `classify.py` then assigns every
breach a cause. Probe output: `/var/tmp/overdue820/b209c.pkl`.

The old probe's split (27 payment lag, 1,679 within 2p, 675 up to £1, 145 above £1) does not
survive being counted on the row's own terms. Measured against the row, nothing breaches by between
10p and £1. The "675 up to £1" were 3p to 7p, mostly, and the 27 "payment lag" steps are not breaches
on the row's rounding at all.

## Causes, every step assigned

| class | steps | households | cause | status |
|---|---|---|---|---|
| A | 2,012 | 117 | **The desk asks the biller's unrounded total, but the page prints a total footed from rounded lines.** `payer_ask_gbp` took `bill["total_amount_gbp"]` (e.g. £16.6788 for OCC-17ff099218d5g's Sep 2020 gas bill). The printed bill sums its penny-rounded lines (`foot_components_to_total`) to £16.67. The desk chases £16.68. The excess equals Σ(unrounded − printed) over the household's open bills, **to the penny, on all 2,012** | fixed in code, this commit |
| A′ | 316 | 22 | The same rounding, on households with 10 to 22 open bills, where the probe's open-bill model (part payments, plan instalments) does not reproduce the sum exactly. Every excess is 1p to 7p, within ½p × the open bills | same fix |
| B | 140 | 18 | **A mover's final bill, part-paid.** The triad decides the bill as failed with `part_paid` paid (`mover_final_bill_outcome`) and keeps the share for the world's truth. The page prints that as a payment received, but only the failure crossed to the desk, so the desk chased the whole bill and the close write-off took it. The excess equals the part paid (plus A's pennies) | fixed in code, this commit |
| C | 32 | 4 | A part-paid final bill where the desk had already taken *some* cash on it, less than the part: OCC-6e59dd8b63e8, OCC-b3b4e19ff255, SYN-2016-016, SYN-2016-083 (e.g. 083: bill £118.33, page part £71.28, desk owed £89.80, so the desk took £28.53 from somewhere) | ~~source of the desk's cash not traced~~ **Traced (156f8dfd6b):** a credit bill the household never used, not cash (083: −£28.53 from Jul 2017). Fixed in `record_period`; see the addendum |
| total | **2,500** | 140 | | |

**Refuted hypothesis for C, kept beside it.** I predicted that the desk's in-loop bill for the month
(the board's `issued_bill_for`, assembled from records settled by month-end) differed from the bill
re-assembled at the leaver's closing read. Rebuilt from `p2b__all_records`, SYN-2016-083's January bill
is £118.33 in-loop, churned and from all records. SYN-2016-016g's February bill is £50.53 all three
ways. The bills agree, so the desk took cash the page does not show as a separate payment. With B's
fix the desk also sees the part, so on these 4 households it will sit *below* the page. The row's
lower bound is nothing, so they stop breaching this row. They will then breach the page/desk
agreement the row does not grade. That is why C stays named here as not traced, rather than
explained.

## Why the pennies moved from about 2,985 to 1,679 (277be7557)

The pennies are per-open-bill rounding (class A). No commit between b2fc50facf and 209c3350ab
touched rounding, so their *rate* held: 2,985 of 32,726 graded steps (9.1%) against 1,679 of 19,491
(8.6%). The count fell because the book printed 13,235 fewer collections steps. The DD was collected
on its date, the credit bill was posted to the desk, and the write-off date became one. All three
closed journeys that used to print overdue figures. 277be7557's prediction ("untouched by any commit")
was right about the mechanism and wrong about the count, because it held the denominator fixed.

## The fixes

1. `saas/money.printed_bill_money` (re-exported at the seam, `bill_assembly.printed_total`) is now the one rule for a
   bill's printed total. `tools/generate_billing_ledger.py` (the page) and
   `simulation/arrears_engine.payer_ask_gbp` (the desk and the engine) both read it, so the desk chases
   the sum the bill states (`docs/market_research/debt_and_collections.md` s.7.2, already cited at the
   ask). Test: `tests/simulation/test_the_desk_asks_the_total_the_bill_prints.py`. It is red before
   the fix (`16.68 != 16.67`) and green after.
2. `background/live_payment_triad.py`: a part-paid final bill's part crosses to both desks as its
   own card payment on the due date. Test: `tests/simulation/test_the_desk_sees_a_final_bills_part_payment.py`.
   It is red before the fix (desk owed £90.00, page £56.64) and green after. It asserts the partition
   (paid, part paid, unpaid) occurs before it asserts the balance.

## Prediction for the next fresh run carrying both fixes (filed before any such run exists)

- **P1.** Class A + A′ falls from 2,328 to **100 or fewer**. Any residual is a share bill, where
  `round(printed × (1 − share))` can still part from the page by a penny.
- **P2.** Class B falls from 140 to **10 or fewer**. A residual would be a card payment the adapter
  observes after the next step's date.
- **P3.** Class C falls from 32 to **0** on this row. Cause: the direction argument above.
- **P4.** The row falls from 2,500 to **under 200** (point 60). The step count will also change, so
  grade the rate as well as the count.
- **P5.** The desk's close write-off on leavers falls by **at most £509.52**, the 24 part-paid final
  bills on the whole book, and by about that amount. I cannot yet say how much of that reaches the
  P&L's bad-debt line, because the P&L books the engine's loss, which already netted the part.
- **P6.** No other row moves by more than its own pennies from fix 1. A bill printed and a payment
  asked can now differ only by an occupier share's rounding.

A grade that refutes P1 or P2 means a cause above is wrong, not merely incomplete.

## Addendum, 2026-10-29 (before any run carries it): class C traced and fixed

Class C (32 steps on 4 households) is a credit bill the household never used, not cash. The page
nets a credit bill off the leg's next bill, but the triad collected the whole bill, so the credit
waited on the desk until it came off a later unpaid bill. Fixed in `record_period`. Traced on the
finding, section "the desk's untraced cash on four part-paid final bills".

- **P-C.** On the next fresh run carrying both this and the part-payment fix, class C is 0 steps,
  and no household breaches the row because of a credit bill held on its desk.
- Replays of the four households, with both fixes, all meet the page or sit within its bound.
