**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Pre-registration: what a departing customer and the supplier would see of the open closing money (2026-10-17, written before the measurement)

Direction item `what-a-departing-customer-sees-of-the-open-closing-money`. It follows
`SEAT_PREREG_THE_MONEY_AN_ESTIMATED_FINAL_BILL_LEAVES_UNRESOLVED_AT_CLOSURE_2026-10-17.md`
(cba9e1540). That record priced the money raw: £13,466.84 gross over 403 closing supply points.

**Premise re-measured.** origin/main carries no instrument or record that applies the bar or the
direct-debit balance to the open closing money. The run output it graded,
`/var/tmp/closing-money-run-20261017.json` (cc23de757), is still on disk. Not spent.

**What is measured.** The open money is what an actual closing read would true up. Nobody takes
that read under the current rule, so this is the money **if it were ever trued up at closure**: for
example from the gaining supplier's opening read. It is the size of what the B3 dispute seed could
be. It is not a flow that happens in the run. For each open closing supply point with a run of
estimates (`tools/closing_estimate_run_money`), there are three steps, in order:

1. **Bar (SLC 21BA).** The demand date is the last bill's `period_end`. The rule is the
   company's own `barred_at_charge_recovery`: each period's true charge against what was
   recovered, with any surplus paying the oldest shortfall. The **incremental** bar is
   bar(true charges) − bar(billed charges), so a bar the billed balance already carries is not
   counted twice. Recovered is what was billed for an account not on direct debit. For a
   direct-debit account it is what the debit collected: the DD book rebuilt with
   `build_dd_balance_book` over the closed set the memory names (last bill month before the run's
   last billed month). The rebuild must reproduce the run's own `dd_balance_book.summary`, or
   the per-account rows are not trusted. An overcharge is never barred. 21BA bars the supplier's
   recovery, not a credit owed.
   *Refined before measuring, while writing the instrument.* The bar is capped at the debit
   the closing demand seeks, as `build_dd_balance_book` caps it: "a supplier loses only what it
   asks for". So the incremental bar is min(debit after true-up, bar(true)) − min(debit before,
   bar(billed)), with the balance taken as 0 for an account not on direct debit.
2. **Recoverable** = open money − incremental bar.
3. **Netting.** For a direct-debit account, B is the billed-basis balance at its last bill
   (positive is credit). The true-up moves it to B′ = B − recoverable. The **new demand** the
   customer would receive is max(−B′, 0) − max(−B, 0). The **absorbed** part is recoverable − new
   demand: a smaller refund, not a bill. For an account not on direct debit, the whole
   recoverable undercharge is a new demand, because there is no balance to absorb it. That is the
   stated simplification: a pay-on-receipt account's balance at closure is taken as settled. For
   an overcharge, the credit owed is |open money| in every channel.

The **dispute seed** is the new demand: money asked of someone who has already left. It is
reported beside the credit owed and never credited, which a customer cannot see at all.

**Predictions:**
- **P1. The bar cuts C7.** C7 is a 42-bill run at about a quarter of its use, ending 2019-06-30.
  The window opens 2018-06-30. Its incremental bar is £3,300 to £3,900, so its recoverable money is
  £1,100 to £1,700. Total incremental bar across all accounts is £3,500 to £5,000, and gas
  contributes under £150 of it, because the median run is 3 bills.
- **P2. Few accounts reach the window.** At most 25 open accounts have any incremental bar.
- **P3. Direct debit absorbs most accounts but not most money.** At least 80% of direct-debit
  undercharge accounts see no new demand. By money, the absorbed share of recoverable
  direct-debit undercharge is 20% to 60%. C7's debit was set from its own under-billed spend, so
  its balance cannot absorb £1k+.
- **P4. The dispute seed** (new demand, both fuels, all channels) is £1,800 to £3,800. C7 is at
  least 35% of it. Fewer than 60 accounts get a new demand above £10.
- **P5. Check, not prediction.** The credit owed and never credited equals the raw overcharge,
  £4,925.29 (£3,491.87 electricity, £1,433.42 gas), by construction.

*Refutation.* If P1's C7 bar is under £3,000, either the run is not one even shortfall (look at
its months) or the DD surplus is paying the old shortfall (Scenario B). Read which before reading
the totals. If P3's count share is below 80%, DD balances at closure are not in credit as often as
assumed. That is a finding about the seasonal balance at the month of leaving.

**Limits carried from the raw record.** A held estimate's billed side is overstated. True charge
is the world's (`true_total_amount_gbp`), which the supplier would only learn from the read that
nobody takes. Prepayment and standard credit are treated alike.

## Graded (same day, 2026-10-17)

`python3 -m tools.closing_estimate_run_money --departing /var/tmp/closing-money-run-20261017.json`
(cc23de757). The rebuilt DD book **reproduces the run's published summary** on all three keys:
694 customers, final balance −£46,217.06, and £31,777.71 barred at final bills. 9 open
accounts on the direct-debit channel have no DD trajectory (no opening amount), and they are
priced as paying what they are billed.

| fuel | direction | open accts | raw open money | 21BA bar it adds | new demand (seed) | absorbed by the balance |
|---|---|---|---|---|---|---|
| electricity | undercharge | 146 | +£7,366.07 | £3,754.75 | **£2,873.96** | £737.36 |
| electricity | overcharge | 128 | −£3,491.87 | −£942.99 | −£1,342.60 | −£1,206.28 |
| gas | undercharge | 64 | +£1,175.48 | £362.94 | **£596.67** | £215.87 |
| gas | overcharge | 65 | −£1,433.42 | −£2.87 | −£794.08 | −£636.47 |

On an overcharge row, a negative new demand is a debit the correction cancels. A negative
absorbed figure is a larger refund. A negative bar is a bar the billed balance carried that the
correction releases. Each row sums: raw = bar + new demand + absorbed.

- **P1 mostly held; the gas leg was refuted.** C7's added bar is **£3,586.08**, inside £3,300 to
  £3,900. Its recoverable money is **£1,431.26**, inside £1,100 to £1,700. All of it is a new
  demand, because C7's debit absorbs nothing. Across the undercharge accounts the bar adds
  £4,117.69, inside £3,500 to £5,000. Net over all accounts it is £3,171.83, because the
  overcharge accounts release £945. **Gas adds £362.94, against a prediction of under £150:
  refuted.** `SYN-2016-471g` alone is a 38-bill gas run, and it adds £212.
- **P2 refuted.** 79 accounts have an added bar, not at most 25: 46 undercharge and 33 overcharge.
  The mechanism was one I did not reason through. Under the running-account rule
  (`barred_unrecovered_gbp`), surplus collections pay the oldest shortfall first. A correction
  to the recent months changes how much surplus was left to pay old debt. So it moves the bar
  even when every corrected month is inside the window. An undercharge in recent months leaves
  less surplus for the old debt, and more of it is barred. An overcharge does the reverse. In 5
  accounts that reverse **raises** the demand: correcting an overcharge leaves the customer asked
  for £328.82 more, £248.99 of it on `SYN-2016-127`. That is the company's rule applied as
  written. Whether a real supplier, or the Ombudsman, would read a correction of an overcharge
  as moving old debt into the window is **not established**: GAP, below.
- **P3 refuted on count, held on money.** 65 of the 155 direct-debit undercharge accounts see no
  new demand. That is 42%, against at least 80%. By money, the balance absorbs £953.23 of
  £3,345.46 recoverable, or **28%**, inside 20% to 60%. The refutation clause named the cause to
  look for, and it is there. **186 of the 291 open direct-debit closing accounts leave in debit**
  on what was billed, summing to −£49,221.56. A level debit at closure is more often short
  than in credit, so it has no credit to absorb an undercharge with. The direction item's premise,
  "a DD balance mostly absorbs" the +£3,726 direct-debit net, is **false on this run**.
- **P4 held.** The dispute seed is the new demand on undercharges, both fuels and all channels:
  **£3,470.63**, inside £1,800 to £3,800. C7 is 41% of it (at least 35% predicted). 53 accounts get a
  new demand above £10 (fewer than 60 predicted). By channel, pay-on-receipt accounts carry £1,078
  of it over 55 accounts, and direct debit carries £2,392 over 90.
- **P5 held, by construction.** The credit owed and never credited is £4,925.29. Of that, £2,137
  would cancel a debit the customer is already asked for, and £1,843 would be a larger refund.

**What a departing customer would see, against the raw £13,466.84 gross.** If the open money
were ever trued up at closure, the 21BA bar would take £4,118 of the £8,541 undercharge. The
direct-debit balance would absorb £953 more. **£3,471 would reach about 145 people as a bill
after they had left, 53 of them above £10, and C7 alone £1,431.** The £4,925 of overcharge is
owed to customers, who cannot see it. Half of it would cancel debts they are already being chased
for. **The money that reaches a departing customer is not the open money.** It is the closing
debit balance: −£49k across 186 accounts, of which the run's own book bars £31.8k at final bills.
The open-estimate seed is a seventh of that and arrives on top of it.

**GAP, registered here.** The running-account rule shifts the bar when recent months are
corrected, and in 5 accounts here a correction of an overcharge raises a demand. This record does
not establish whether that matches Ombudsman practice. Whether the gaining supplier's opening
read would ever reach the losing supplier as a true-up is a practitioner question, and it was not
asked here.

**Limits.** These are the raw record's limits: held estimates, the world's true charge, and
prepayment treated as standard credit. In addition, a pay-on-receipt account's balance at closure
is taken as settled.
