**Lane:** W2_customer_generator · **Atom:** `W2_36_unbilled_energy_arises_the_way_it_does_in_reality`
**Knowledge:** unbilled-energy-and-revenue-assurance

# Pre-registration: the money an estimated final bill leaves unresolved at closure (2026-10-17, written before the fresh run returned)

Direction item `the-money-an-estimated-final-bill-leaves-unresolved-at-closure`. It follows
600be30bc (`WORKER_PREREG_W2_36_THE_CLOSING_READ_IS_ACTUAL_ONLY_WITH_A_REASON_2026-10-17.md`). That
replay counted 320 closure true-ups that no longer happen. It could not price them.

**Premise re-measured.** No run output at or after 600be30bc existed when this was drawn. The
shared tree's latest book is bdd6d1657, and the sim-runner was deferring: four imported files on
the shared tree are not the commit's bytes. So the premise is not spent.

**What the money is.** Take each supply point whose account closed in the run. That set is
`simulation.household.supply_points_that_left`: the departures, the home movers, and every gas leg
of either. It is the set the bill assembly asks the closing read for. Then take the run of estimated
bills that ends at its last bill. Every estimated bill carries its true total beside its billed
total, so the run's money is sum(true − billed). This is the sum `_resolve_catchup` forms when an
actual read arrives. Positive is an **undercharge the supplier never recovers**. Negative is an
**overcharge never credited**. The money is raw: no SLC 21BA bar, no direct-debit balance. The
instrument is `tools/closing_estimate_run_money.py`. On the 2248e3baf book it reproduces the book's
own `catchup_raw_delta_gbp` on all 235 closing rows that carry one, to the penny.

**Instrument facts read before predicting (old rule, what the forced read used to settle).**
On 2248e3baf there are 609 closing supply points. 408 of their last reads were forced, and 320 of
those had a run of estimates, which matches the replay's 408 and 320.

| fuel | direction | accounts | money settled by the forced read |
|---|---|---|---|
| electricity | undercharge | 115 | +£7,850.31 |
| electricity | overcharge | 104 | −£2,877.04 |
| gas | undercharge | 57 | +£958.63 |
| gas | overcharge | 43 | −£1,179.31 |

On the bdd6d1657 book the four cells are +£6,832, −£3,085, +£985 and −£1,188 (408 forced, 321
with a run). One account dominates electricity: **C7**, a smart meter that is out of smart mode
(`is_not_in_smart_mode("C7")` is True), was unread for 50 months and billed at about a quarter of
its use. Its forced read settled +£5,984.42 on its last bill (bdd6d1657: +£4,906.55). Without C7,
electricity nets about −£1,011. Direct-debit accounts carry +£5,004 of the forced total.

**Predictions** for the fresh run (at origin cc23de757, which includes 600be30bc):
- **P1.** Between 395 and 410 closing supply points end on an estimated last bill (`open`). At most
  4 forced reads stay actual (C2 found 2 of 16 smart forced reads stay actual).
- **P2. Sign: electricity is left net undercharged, and C7 decides it.** C7 is out of smart mode,
  so its £5–6k run stays open and grows by its final month. Electricity undercharge left open:
  £6,500 to £10,000. Electricity overcharge never credited: −£2,500 to −£4,500.
- **P3.** Without the largest single account, open electricity money nets between −£2,500 and
  +£500. Away from one pathological meter, estimates at closure err in both directions about
  equally.
- **P4.** Gas undercharge left open: £800 to £1,600. Gas overcharge never credited: −£1,000 to
  −£2,000. Gas nets within ±£600.
- **P5.** Gross unresolved money (|under| + |over|, both fuels) is £11,000 to £18,000, against
  £12,865 that the forced reads settled on 2248e3baf. Each open run is one bill longer than the
  run the forced read used to close (the last month is now estimated as well), and the 88 forced
  closings that had no run now carry a one-bill run.

*Refutation.* If P1 comes in under 395, the rule is not reaching the closing set the assembly
names, or the closing set has moved. If P2's sign is negative, C7's trajectory changed in the
world, not because of the read rule; check C7 before reading the total. If P3 falls outside its
range, the estimate's error at closure is biased, and the residual is owed a cause before anyone
reads it as noise.

**Attribution limit, stated before the answer.** The fresh run differs from both baselines by
every commit landed since them, not only by 600be30bc. The forced-to-open move is attributable,
because only 600be30bc changes a closing read's status. The money's size also moves with
everything else that changed. bdd6d1657 is the nearer control; the gap between the two baselines
(electricity undercharge £7,850 against £6,832) is the order of drift to expect without the rule.
