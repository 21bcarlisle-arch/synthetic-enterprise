**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The first cold read finds page arithmetic that does not reconcile, and a margin nobody defined

These are the first cold read's objections that are **not a range checkable on every household**
(record: `docs/staging/records/SEAT_RECORD_THE_FIRST_COLD_READ_ON_THE_4AE8DA9B0F_PAGES_2026-10-27.md`,
run 4ae8da9b0f). The range-shaped ones went to `DOMAIN_INVARIANTS.yaml`. The reader saw only the
rendered page. Quotes are the page's own text.

## Wrong in the world, or on the page as a fact

- **O25, an undefined "gross margin".** Gross is 41–66% of revenue on all six random accounts,
  where GB pass-through puts it at about 10–20%. "Net after cost to serve" is not gross less cost to
  serve: for OCC-f6813bf9f05e, £4,776.92 − £477.25 ≠ £854.29. **Say what "gross" counts before
  anything differences it.** It is likely revenue less wholesale only, with network and policy
  unnamed in between. Same class as *net margin* in CLAUDE.md.
- **O13, a bill with nothing owed.** PROS-2025-0022's first bills total £186.20 with "0 payments"
  and "Nothing owed". Balance ≠ billed − paid.
- **O26, "Paid in total" equals "Revenue billed".** It does so on every account, where stage 5's
  ledger shows less collected (OCC-52fbc3104c5f: collected £4,747.99 against paid £5,062.23).
- **O27, frozen balances never chased.** A balance owed is held flat for two years with no debt
  stage (OCC-f6813bf9f05e at £399.99). Payments equal each invoice 14 days later, which is pay on
  bill, while the page says "a flat monthly amount".
- **O8, true churn at exactly 0.0%.** This is on the world side. PROS-2017-0049 and SYN-2016-031
  show 0.0% at fix ends. Home moves alone make it non-zero. The "CONTENT" household also sits at
  86.2%. The floor is a world question (GAP: no commons rate for moves).
- **O30, a first part-year too low.** OCC-f6813bf9f05e's first quarter is 750 kWh of gas for a
  9,600 kWh/yr home. The Xoserve ALP share is not in the commons (GAP), so this is not yet a row.
- **O4, SVT electricity below the cap.** Feb–Mar 2025 electricity bills sit about 6% under the cap
  while gas sits on it. This is lawful under the cap, but it reads as missing VAT. Whether SVTs were
  priced at the cap is for `svt_rates_active_passive_2016_2025.md` to settle.

## Misleading or cosmetic page copy

- O7: the renewal EV of £26.15 = £113.18 − £87.03, and never applies the 85%. Also, 8% costing £87
  implies a term bill of about £1,088 for a home billing about £2,400 a year.
- O9: a 2024 moment labelled "at the 25 Jan 2019 renewal". O11: a "renewal" on an SVT account, and
  "off by 5.0%" given for percentage points.
- O12: "Three months in" is two months in. O15: "£45.43 credited" against the bill's "£33.57
  credit", with the electricity leg still estimated on the same read date.
- O20, O21: life events after supply ended, a 2024 customer page for a household gone since 2018,
  and "Income stress low" beside 40 missed payments.
- O23: "use did not explain the change" when use rose 18%. O24: a 2021 payment line repeated in
  2022.
- O28: the account header's bill count is one fuel's count. O29: gas–weather r is computed over
  part-years, giving r = −0.30 beside "heating-dominated".
- O32: electricity day-clock text on gas-only smart accounts. O33: three book sizes (752, 707, 1291)
  with no units. O34: bill lines split energy from "Network & environmental", which no GB bill
  does. O35: one p/kWh averaged across both fuels.
- O37: the mover slot's "What closes it" reads as if already done.

## What closes it

O25 first, because it is a definition: write what gross, net and cost to serve each count on the
page that prints them. O13, O26 and O27 are one ledger reading and can likely become an
`INV_BALANCE_IS_BILLED_LESS_PAID` row once the export carries a dated balance. The copy items are
one pass over the cast and stage generators.

## O26, O13, O27 and O25: causes and fixes (2026-10-27, delivery lane)

**The ledger was right about payment and the page was wrong.** On all 1,291 published accounts the
invoices sum to the ledger's raised amounts, and the ledger's balance is the sum of its entries.

- **O26: the page read the wrong field.** `stageJudged` summed each leg's `revenue_gbp`, which is
  the supplier's ex-VAT settlement revenue, and printed it as "Paid in total". It now reads the
  payment ledger (`judgedFigures` in `site/explore/index.html`): billed (VAT included), paid,
  government credit, write-off, and what is owed on the ledger's date. The rows foot.
- **O25: two clocks were mixed and one row was missing.** "Gross margin" was the household's two
  legs, but "Cost to serve" and "Net after cost to serve" were the electricity leg's alone. Nothing
  printed net. Now every figure is summed over every leg, and the column reads: revenue before VAT,
  less wholesale energy, gross margin, less network, policy and capital, net margin, less cost to
  serve, net after cost to serve. The page says what each one counts. Gross is revenue less
  wholesale only (`simulation/hedged_settlement.py`), which is why it runs at 41–66%.
  **Still open:** cost to serve is charged per leg, so a dual-fuel home carries two. The page now
  says so. Whether that is right belongs to B13.
- **O13: two clocks for one bill.** The invoice is dated at its period end, and the ledger raises
  it on issue a few days later. The cast read the balance from the ledger alone, so at a first-bill
  moment it showed the bills and "Nothing owed". `_owed` in `tools/generate_explore_cast.py` now
  takes the bills the page shows, less every other ledger movement known that day. On the published
  book, 7 of the cast's 18 balance rows change. One is `shock_2022` on 2021-12-31, which moves from
  "£0.01 owed" to £311.09.
- **O27: the ledger dropped part of the EBSS credit.** The engine gives the month's whole credit to
  the account, caps the bill's share at the bill, and carries the rest as account credit that later
  bills draw on (`credit_applied_gbp`). `tools/generate_payment_ledger_data.py` posted only the
  capped share, so the bills that the carried credit settled stood owed for ever. On
  OCC-f6813bf9f05e, £400 of credit appeared as £399.99 owed under the old ledger, then £92.19 owed
  under 9d7bd4a5c's. The page ledger now posts `scheme_credit_month_gbp`, as 9d7bd4a5c made the raw
  export do. On the 13a6e5e71d book, accounts whose ledger balance disagrees with the engine's own
  outstanding fell from 182 to 133. The 133 that remain:
  - 76 are bills due after the book date. They are owed on that date, so these are correct.
  - 33 are in credit beyond the engine, and 13 of those are new. They are credit the old ledger
    dropped, for example a £67 January credit on a £6.61 final part-month bill. **GAP:** no refund
    of a credit balance at exit is modelled.
  - 20 owe more for some other reason, and 4 owe more while holding a write-off. One of those
    leaves £19.16 after writing off less than the bill (OCC-87206d346f15g). These are not chased
    here.
  "Payments equal each invoice 14 days later" is the DD collected on the due date. It is not pay
  on bill. Not changed.
- **Life events (4d7f6021a's residue).** Each life event in the supplier's timeline now carries
  `seen_by: "world"`. No route in the run tells the supplier of one.
- **INV_BALANCE_IS_BILLED_LESS_PAID was not added.** The raw export deliberately carries no balance
  (`company/billing/raw_account_export.py`, "nothing derived"). The row would have to rebuild the
  balance from the raw movements. That is for the suite's blind author to judge.

**Reconciled on a regenerated book.** The 2eeb3f0b3 run exists only as a pickled arm, which has no
`per_customer_lifetime` and so cannot drive the page generators. The pages were therefore rebuilt
in `/var/tmp/cust-reconcile-13a6e5e71d` from the full 13a6e5e71d run, which descends from 2eeb3f0b3,
using current ledger code. The page's own `stageJudged()` was then driven over the eleven
cold-read households. On all eleven, paid equals what the ledger collected, billed equals paid +
credit + write-off + owed to the penny, and the column for us foots within a penny. The published
site changes at the next publish.

**Tests that go red on the old code:**
- `site/explore/test_the_judged_stage_reconciles.py`: 752 households printed a paid figure the
  ledger did not collect.
- `tests/tools/test_generate_explore_cast.py::test_the_cast_balance_is_billed_less_paid_on_every_moment`
- `tests/tools/test_generate_payment_ledger_data.py::test_the_months_whole_scheme_credit_is_posted_so_the_bills_it_later_settles_are_not_owed`

The rest of this finding stays open: O8, O30, O4 and the copy items.

## O27 residue: the refund was modelled and the ledger dropped it (2026-10-27, delivery lane)

**K8 page:** `docs/market_research/home_moves.md` §8.8 (GSoP 2015 reg 6D, SI 2019/218: refund any
credit within 10 working days of the final bill). No new rule found; the page already holds it.

**Cause of the 33 "GAP: no refund modelled" was wrong.** The company does refund:
`simulation/credit_refund_events.py` logs one event per leaver closing in credit, paid on the
deadline (`credit_refund.scheduled_refund_date`). The log never reached `billing_ledger.json`, so the
page ledger (`tools/generate_payment_ledger_data.py`) never posted the money leaving. Fixed:
`generate_billing_ledger` carries each event as `refunds` on its account, and the page ledger posts a
`refund_debit`. `total_collected_gbp` is now net of it, so billed = collected + scheme credit +
balance + written off still foots; `total_refunded_gbp` is published beside it.
Tests red on the old code: `test_a_leavers_credit_is_refunded_so_the_closed_account_does_not_hold_it_for_ever`,
`test_the_ledger_carries_each_reg_6d_refund_on_its_account`.

**Measured** (reconciled-book ledger + the shared run's log): the log holds 27 refunds, which is every
closing balance below zero in the run (27 of 857). Accounts in credit at the book date fall 136 to
117. Of the 117, 99 are under 50p or are still-active accounts, where credit is legitimate;
the 4 real-sized leavers remain below.

**Prediction filed before measuring was "all 33 resolve"; it did not hold, the log covers 27.**
The 6 other credits are not leavers' closings (they have no closing balance), so no refund is owed.

**Causes of the 24 that owe more (traced on three accounts; not fixed, not a refund question):**
- OCC-3c914ee8cef5g, OCC-561d240ea21a: one early failed direct debit (£48.94 in 2016, £42.58 in
  2017) ends `BALANCE_OPEN` with no later stage. The page ledger carries it as owed for ever; the
  engine's closing balance for 561d is £0. Two readings differ on whether a never-chased failed debit
  is a debt: this is the O27 "frozen balance never chased" item, an arrears-engine question (no
  debt stage after the second notice) and not a ledger posting defect. Open.
- OCC-423594fbfa6bg (-£4.28 held from 2017): account credit applied (£20.57, £8.41) against bills
  whose paid amount was already netted. A constant offset from one 2017 bill. Open.
- Write-off short of the bill (OCC-87206d346f15g, £19.16): not reproduced in this pass. Open.

## The occupier window's payment outcome has one home (2026-10-28, delivery lane)

**Cause of the two never-chased failed DDs.** OCC-3c914ee8cef5g (£48.94, Mar 2016) and
OCC-561d240ea21a (£42.58, Oct 2017) are bills with `occupier_share` 1.0. The run books such a bill as
the unnamed occupier's debt, billed and never collected (B7 slice 4; `back_billing_and_liability.md`
s.13). The arrears engine skips it. `generate_billing_ledger`'s no-row branch drew its own method
and outcome, so the named payer was shown DD collections on all 836 window/void bills, and a failed
DD on 12 of them.

**Fixed.** A bill wholly inside the window or the void (the engine's own test, share >= 1) is now
`billed_to: occupier | owner`. It has no payment and no case. The page ledger raises it and takes it
off the named payer's balance (`deemed_account`, `total_deemed_gbp`), and the Explore household
figure "billed" leaves it out. A catch-up credit inside the window counts too: left on the payer,
nothing ever drew it. A no-row bill outside the window now raises an error instead of being drawn,
and the real book raises none. Test, red on the old code:
`tests/tools/test_a_bill_inside_the_occupier_window_is_the_deemed_accounts.py`.

**Measured** on run 5e3e9966a5 (1,291 accounts, as of 2025-07-04), old ledger code against new:
failed DDs 1,658 → 1,646; accounts owing more than £1, 181 → 171; accounts in credit by more than £1,
17 → 14; both named accounts £0.

**This is a different book from the 13a6e5e71d reconciliation**, and its counts are not those 4 and
21. The two named accounts are on both books. The residue below is this book's.

**The 3 leavers still in credit**
- OCC-423594fbfa6bg, −£4.28: the constant offset from one 2017 bill traced above. Still open.
- OCC-bec72a04dec8, −£27.79: the month's whole EBSS credit (£51.67, £64.95, …) is larger than the
  bills just after the window. The engine's carry draws £24.29 of the excess and the ledger keeps the
  rest. The engine's closing balance is not in credit, so no reg 6D refund is logged. The engine and
  the ledger size the carry differently on a part-window month. Open.
- PROS-2016-0117, −£44.90: three bills draw down a £95.97 catch-up credit, then the draw stops.
  **Not traced.** My hypothesis is that the carry ends at a contract change.

**The 28 owing more that the simple classes do not explain**
- **5 leavers: a refund paid from an account the ledger never had in credit**
  (PROS-2017-0293 £9.68, PROS-2021-0362 £435.60, SYN-2016-070 £355.33, SYN-2016-144 £18.50,
  SYN-2016-406 £101.92). The run's reg 6D refund reads a closing credit the ledger never holds. The
  ledger collects each bill exactly, and the run's DD balance book does not. That makes the DD
  balance a second two-homes defect. **Open, and the next item.**
- **15: correctly owed on the book date.** Every residual sits on a BALANCE_OPEN case, or on a
  collection or repayment dated after 2025-07-04. The first pass tested the two classes one at a
  time and missed the accounts that have both.
- PROS-2018-0267, £22.83: the residuals are negative on four paid bills, yet the account owes.
  **Not traced.**
- **6: account credit netted against different bills by the engine and the ledger.** These are
  invoice residuals of +x and −x that do not fully cancel (PROS-2016-0187, PROS-2018-0002g,
  SYN-2016-016, SYN-2016-487, OCC-7119d3c0d418g, OCC-a1e9ae835e65). This is the OCC-423594fbfa6bg
  class. Open.
- OCC-87206d346f15g, £19.16: the write-off is the payer's share of a part-window bill. The residue is
  the part-window share, which the ledger still collects from the payer at the full printed total.
  That is the next one-home cut (239 part-window bills). Open.

## The five refunds from a credit the ledger never held: one cause (2026-10-28, delivery lane)

**Cause, traced on all five.** `world_payment_truth.build` keyed every crossed settlement by
BILLING ACCOUNT and gave it to that account's first leg (`cid_of = {account: rs[0].customer_id}`),
always the electricity leg. On a dual-fuel account the household's settlement of a failed GAS bill
became an electricity repayment, priced at the electricity bill for that month. On run 5e3e9966a5
no gas leg holds a single settlement. 523 of them sit on electricity instead: 235 for a month the
electricity leg had paid (pure phantom credit), and 288 doubling a month both fuels failed. The gas
bill the household settled stayed outstanding and was written off at close.
- PROS-2017-0293 (2020-05), PROS-2021-0362 (2023-01), SYN-2016-070 (2016-05), SYN-2016-144
  (2017-02): gas failed, electricity paid; the gas settlement is electricity credit, refunded.
  SYN-2016-144: the £46.55 phantom credit pays the £28.05 final bill, and the £18.50 left is refunded.
- SYN-2016-406: both fuels failed Jan to Jun 2019; each month's gas settlement doubles the
  electricity one, and the surplus is refunded.

So it is not the DD balance book against the ledger. The ledger is right that no credit was held.
The engine's walk took a payment that belonged to the other fuel's contract (SLC 27.16 nets per
contract).

**Pre-registration, filed before the fix is measured.** With each settlement on its own leg:
(1) none of the five is refunded; (2) the run's refund count falls from 27, by at least the five;
(3) the closing-balance write-off falls on those accounts' gas legs by about the settled gas
bills; (4) run-wide bad debt falls, because 523 settled gas bills stop being written off. I do not
know the size of (4).

**Fixed.** The triad's crossed settlement now carries the leg whose bill it settled
(`background/live_payment_triad.py::_cross_settlement`), and `world_payment_truth.build` gives it
to that leg. A repayment plan's instalments are split the same way, by leg, at the same share. The
plan path had the same account-keyed shape but repays nothing on this run, where plans are off.
Test, red on the old code ("no gas leg was ever repaid a settlement"):
`tests/simulation/test_a_settled_gas_bill_is_repaid_on_the_gas_leg.py`.

**Measured on 5e3e9966a5's persisted truth, with each settlement put back on its leg** (this is a
rebuild, not a re-run). Where only one fuel failed, the leg is unambiguous. Where both failed, a
second settlement for the month goes to gas. 291 single settlements in both-failed months stay on
electricity and cannot be assigned from the persisted record; the next run assigns them from the
event. The engine's walk and the refund log were re-run over the result:
- **All five refunds are gone** (1 held). They are £9.68, £435.60, £355.33, £18.50 and £101.92.
- Refunds: 25 → 21, £2,752.98 → £1,838.80. One new refund is right: SYN-2016-115g's settled Aug
  2018 gas bill no longer soaks up its −£6.85 final credit bill, which is now owed back.
  (The probe's "as run" walk gives 25 refunds against the run log's 27. It reproduces the walk to
  within two accounts, and all five are in both.)
- **Bad debt: £20,960.21 → £10,823.88.** This is (4), and its size was not predicted. The P&L wrote
  off 523 gas bills the household had settled. **Every published bad-debt and net figure from a
  run since one payment truth shipped (12 Oct) moves**. The next run carries the correction, and
  the reading for that run must mark each figure that moved.

**Measured on a fresh run (2026-10-28, run at `20e7d66234` against `1691ec0ecd`).** The fix is the
only run-side change between the two books. Every pre-registered prediction about it was met. None of
the five leavers is refunded. Refunds fell from 26 to 21. 522 settlements now sit on gas legs (0
before). Bad debt fell from GBP 19,738.24 to GBP 10,783.88 (-45%), and net rose by the same
GBP 8,954.36. Gross and the provisioned figures did not move. The published 4ae8da9b0f figures (bad
debt GBP 18,495, net GBP 664,130, and every year from 2017) predate the fix, so all of them move.
The year-by-year table and the grade are in
`docs/staging/records/SEAT_PREREGISTRATION_THE_GAS_LEG_SETTLEMENT_FIX_AND_THE_PART_WINDOW_CUT_ON_A_FRESH_RUN_2026-10-28.md`.
The EBSS part-window breaches (12, 5 of them on part-window months) are unchanged, as predicted;
they wait for the next run carrying `3ab3ea925`.

## The part-window share has one home (2026-10-28, delivery lane)

**Cause.** For a bill partly inside the window or the void (0 < share < 1), the engine asks the
named payer for `total × (1 − share)` (`arrears_engine._resolve_bills`). `generate_billing_ledger`'s
payment row collected the full printed total. A paid bill therefore showed the payer paying the
occupier's days. A failed one was written off at the payer's share while the page balance held the
whole bill: OCC-87206d346f15g's £19.16 is that difference.

**Second home, found on the same bills.** Where the unnamed occupier's account held the month's
EBSS credit (`occupier_scheme_credit_gbp`), the engine asks the payer for its share whole. The ledger
still netted the month's £67 from the payer's payment and posted it on the payer's page. Taking the
full total hid this; once the share was right it left five payers in credit by £27 to £59
(OCC-25ff8966357a, OCC-a1e9ae835e65, OCC-c0afcdf9fce8, OCC-eb72725807da, OCC-eb8498f3f8aa).

**Fixed.** A part-window invoice carries `deemed_share_gbp` and `deemed_share_to`. The payment asks
the payer's share only. The page ledger posts the deemed share off the payer's balance on issue,
and it counts in `total_deemed_gbp`. An occupier-held EBSS credit is neither netted from the payer
nor posted to it. Tests, red on the old code: `test_a_part_window_bill_asks_the_payer_for_its_own_share_alone`
("the payer paid 150.0 of a 90.00 share") and `test_an_ebss_credit_the_occupier_held_is_not_the_payers`,
both in `tests/tools/test_a_bill_inside_the_occupier_window_is_the_deemed_accounts.py`.

**Measured** on 5e3e9966a5, old ledger code against new, as of 2025-07-04:
- 238 part-window invoices (the earlier count was 239; one is a credit bill, which has no payment).
  £7,034.38 is the deemed share, and £7,007.26 of it, on 235 paid bills, is no longer taken from
  payers.
- Accounts owing more than £1: 171 → 169. Accounts in credit by more than £1: 14 → 13.
  OCC-87206d346f15g: £19.16 → £0.
- The five refunds still show on this ledger as owed, at their refund amounts. Their refund log
  is the old run's. The leg fix above removes them at the next run (rebuilt: all five gone).

**Open, not this item:** OCC-bec72a04dec8's carry, which needs re-reading on the next run because
this cut changes its part-window month; PROS-2016-0117; PROS-2018-0267; the six credit-netting
accounts (OCC-423594fbfa6bg class).

## A window month the EBSS credit paid read as the payer's (2026-10-28, gas-leg re-measure)

**Found by** re-grading the 1691ec0ecd book with HEAD's ledger code (2bef058eb), before the fresh run
returned. `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` went from 3 to 12, over the exception's ceiling of
3. So the next publish of any book would have been refused.

**Cause.** This was not the ledger cut. 2bef058eb made the ledger follow the engine, and that exposed
an older defect in bill assembly. The world books each window row's energy as `occupier_debt_gbp`,
**net of the deemed account's EBSS credit**. Bill assembly took `occupier_share` as debt over
revenue. So a window month the credit wholly paid had share 0, and a month it partly paid had its
share understated. The arrears engine then asked the named payer for days that were the occupier's,
and that the government's credit had already paid. On the 1691ec0ecd book this was 14 bills,
GBP 1,160, across six OCC accounts. OCC-bec72a04dec8's Dec 2022 to Feb 2023 is the example: the
payer was asked for the whole bill. Before 2bef058eb, the ledger hid this by posting the occupier's
credit on the payer's page.

**Fixed.** `monthly_bill_assembly.occupier_window_share` takes the share as the window rows' revenue
over the month's. A row is in the window when it carries `occupier_debt_gbp`, zero or not. The page
ledger no longer posts a deemed bill's EBSS to the payer. Once the share was right, that posting had
left each of the six payers GBP 67 to 134 in credit. Tests, red on the old code:
- `tests/company/billing/test_a_window_month_the_ebss_credit_paid_is_still_the_occupiers.py`
- `tests/tools/test_a_bill_inside_the_occupier_window_is_the_deemed_accounts.py::test_a_window_month_the_ebss_credit_paid_leaves_the_payers_page_at_nothing`

**Measured on the 1691ec0ecd book, rebuilt with the fixed share** (this is a rebuild; the engine
re-resolves from the bills):
- 14 bills move. Ten become wholly the occupier's and four become part-window.
- The EBSS row breaches 12 → 6. Three are the void months already excepted. Three are months the
  deemed account held at 00:00 on the 1st, with the payer named later that month (guidance 5.4). In
  each case the export carries no window, so these are the grader's. The exception is widened to 6
  with both causes named.
- The six payers' page balances go from GBP 0 to 134 in credit, then to 0 after the page fix.
- Accounts in credit by more than GBP 1: 11, unchanged.

**Not yet measured by a run.** Run `20e7d66234` was queued before this fix, so it grades the old
share. The engine's own resolution changes on these 14 bills, and that needs the run after it.
