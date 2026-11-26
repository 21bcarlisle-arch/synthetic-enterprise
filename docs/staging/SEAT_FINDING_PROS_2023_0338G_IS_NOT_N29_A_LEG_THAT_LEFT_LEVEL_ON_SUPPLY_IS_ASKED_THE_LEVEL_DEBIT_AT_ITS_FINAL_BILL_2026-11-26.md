**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`

# PROS-2023-0338g is not the N29 class: a leg that left level DD on supply is still asked the level debit at its final bill, so it pays an open bill twice and is refunded the excess

The delivery seat wrote this on 26 Nov 2026, working the claim
`the-page-and-the-n29-set-off-close-the-last-two-refusal-rows`.

BLOCKING: the one closing refund outside its exception's class
(`INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT`) refuses every book on this world until it is fixed.
Neither of the two remedies the direction named is that fix.

## The premise, re-measured: both named builds are already spent

- **The 91c32797b3 book's prediction** is already on origin, in 945306b995
  (`SEAT_FINDING_THE_001E4F680A_REFUSAL_PROS_2019_0305_...`, "Prediction for the 91c32797b3 book"). It is not
  re-filed here. One reading follows from it. d688a224a has now landed, so the publisher regenerates the
  ledger with the issue-order rule. Its own branch therefore predicts **INV_OVERDUE_WITHIN_BALANCE 1
  (PROS-2019-0305)** on this book.
- **The page-side fix 470513f81b recommended for SYN-2016-099** was superseded by the world-side fix
  d688a224a (a leg's bills are issued in period order). That fix is on origin, but the 91c32797b3 book does
  not carry it. So that book still reads INV_OVERDUE_WITHIN_PAGE_BALANCE 8. The first book on a commit at or
  after d688a224a is the test. Building the page rule as well would fix one defect twice.
- **`n29-close-set-off-nets-issued-debt` was built on 18 Nov** (home_moves.md s.8.8e choice 30). Since then
  the decision has moved into the supplier (`company/billing/credit_refund.HouseholdCloseDebts`). Its
  `retired_by` names a build that exists. The 7 in-class rows still breach on the 001e4f680a book, so that
  build does not retire them, and that is the exception's own recheck question (`recheck_by: 2026-11-26`,
  today). It is not answered here.

## PROS-2023-0338, read (001e4f680a run, regenerated ledger `/tmp/seat_pw/ledger_head.json`)

Both legs were on level DD from 17 Nov 2023. Both first collections failed (electricity 2 x 32.55, gas
2 x 71.12). From Jan 2024 the household paid on receipt (`standard_credit`). Gas has its 28-day closing
statement (issued 1 Feb 2024, asked 77.60). Both legs churned at renewal on 16 Nov 2024.

| leg | walk's open debt before the final bill | final bill face | page payment on it | `debit_paid` | walk's close | refund |
|---|---|---|---|---|---|---|
| electricity | 18.61 (Jun 2024 bill, failed, part met by a repayment's excess) | 16.02 | **58.68** on 15 Dec | 42.66 | -24.05 | 24.05, 31 Dec |
| gas | 6.48 (Dec 2023 bill remainder) | 37.89 | **75.05** on 30 Nov | 37.16 | -30.68 | 30.68, 13 Dec |

The walk closes each leg at `outstanding - debit_paid` (`arrears_engine.balance_settlement_from_outcomes`,
the s.8.8f choice 26-27 term): 18.61 - 42.66 = -24.05, and 6.48 - 37.16 = -30.68. The debit is the
triad's `_final_bill_debit`, which is `ledger_balance - barred` on the final bill's issue day
(`background/live_payment_triad.py`). On that day each leg's ledger still held its **October regular bill,
issued and not yet paid**:

- electricity on 1 Dec held INV20401, 39.24, paid separately on 11 Dec (page balance 57.85 before the final
  bill);
- gas on 16 Nov held INV20414, 57.23, paid separately on 17 Nov (page balance 63.71).

So the final bill asked the October bill again as "the scheme's debit". The household paid it twice, once on
its own and once inside the final payment. The close then refunded the excess on both fuels. The breach the
evaluator sees is gas refunded 30.68 while electricity's page owes 34.63. That is real, but it is an artefact
of the double ask. Neither leg was ever owed a credit.

**Why the guard lets it through.** The debit half is gated on `customer_id in self._legs_ever_level`. That
set is "has EVER presented a level collection", and it is never cleared. s.8.8f is explicit: the final bill
is the closing demand of a leg that leaves level **at** that bill. A leg that left level DD **while still
supplied** (S7) gets the 28-day closing statement instead, "and only that". PROS-2023-0338 left in Jan 2024
and gas got its closing statement. Ten months later both final bills still asked a level debit.

The walk has a second effect, from the same cause. The 42.66 the household paid is subtracted at close, but it
never meets the outstanding June bill. So that 18.61 is **also written off** (`leg: close`, 1 Dec 2025)
although the household paid it. The bad-debt line carries money the world collected.

## Ranked explanations considered

1. **The debit is asked of a leg that is no longer on level (above).** Every figure reconciles to the penny.
2. **The N29 set-off misses a repayment collected after the refund day.** That is the walk's own named limit
   on `later_cash_out`. I built it and replayed it before ruling it out. Pre-registration
   (`/var/tmp/n29r/PREDICTION.txt`, filed before either arm): P1 predicted this event's set-off would become
   30.68. **P1 was refuted.** Base and fix both give 218 events and GBP 1,642.85 of set-off, so no event moves.
   No repayment is dated after the refund day on this leg. The repayments are Jan and Feb 2024. The edit is
   reverted and not landed: a change that moves 0 of 218 events on the real book has nothing to prove here.
3. **The evaluator is wrong.** No. The page's 34.63 on 13 Dec is what the ledger says the household had been
   asked for and had not paid. The page is right that money was asked; the world was wrong to ask it.

## The class, counted on this book

There are 8 breaching refunds. I checked each household's other leg for a final-bill payment above face
together with a closing statement. **1 of 8 has that shape: PROS-2023-0338.** It is also the 1 the evaluator
labels outside class. PROS-2020-0102g, -2023-0166 and SYN-2016-294 also pay above face on the debt leg. None
has a closing statement, and none breaches outside class, so those read as ordinary level leavers' debits.
I cannot say from this book how many non-breaching legs carry the shape: a household with one fuel, or with
both legs over-asked, is refunded without breaching anything.

## Recommended fix (world, not built this turn; why)

Ask the debit half (and net the surplus half) only of a leg **on level at its final bill**: the triad's
`_leg_level_floor` (set when a bill presents a level collection, popped when one does not) rather than
`_legs_ever_level`. Knowledge first (K8): this is s.8.8f's own answer, so the page needs one numbered choice
stating it, citing this finding. Then:

- the control: a leg that leaves level on supply, pays on receipt and then moves out is asked its final
  bill's face. It must also assert that a leg on level at its final bill is still asked its debit, so both
  sides of the partition are taken at once;
- a census of `final_month_nets` rows where `ever_level` is true but the leg was off level at the final bill,
  BEFORE landing. It moves world asks on every such leg, and the 436-leg D5 census did not split by it.

It is not built this turn because a world change that moves an unknown number of asks must be printed at
real inputs first, and that census needs a run.

**Prediction, written before any fix:** on a book carrying it, PROS-2023-0338's final payments are 16.02 and
37.89. Neither leg is refunded. Electricity's June remainder is owed at close (18.61) and gas owes its 6.48.
INV_A_CLOSING_REFUND_IS_WITHIN_THE_HOUSEHOLD_CREDIT has **0 breaches outside its class**. The 7 in-class
rows do not move.

No exception is widened and no ceiling is raised here.
