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

## Graded (same day, 2026-10-17)

A fresh run finished at 04:56 BST. It was launched from an isolated worktree at cc23de757, and
its `producing_commit` is cc23de757. Two auto-salvage commits landed in that worktree during the
run. They touched only run artefacts (`docs/observability/*`, `docs/context-handshake-latest.md`),
not code. The output (`/var/tmp/closing-money-run-20261017.json`, not committed, 94 MB) was read
with `python3 -m tools.closing_estimate_run_money`. That gives 606 closing supply points. 47
settled rows carry a book true-up, and all 47 match the instrument to the penny.

**The money an estimated final bill leaves open, beside what the forced read used to settle:**

| fuel | direction | open accounts | open money (cc23de757) | forced read settled (bdd6d1657) | (2248e3baf) |
|---|---|---|---|---|---|
| electricity | undercharge left unrecovered | 146 | **+£7,366.07** | +£6,832 | +£7,850.31 |
| electricity | overcharge never credited | 128 | **−£3,491.87** | −£3,085 | −£2,877.04 |
| gas | undercharge left unrecovered | 64 | **+£1,175.48** | +£985 | +£958.63 |
| gas | overcharge never credited | 65 | **−£1,433.42** | −£1,188 | −£1,179.31 |

- **P1 held.** 403 closing supply points end on an estimated last bill, inside 395 to 410. Two
  forced reads stay actual, against at most 4: `C4g` and `PROS-2024-0110g`. Both are smart gas
  meters, and neither has a run of estimates before it. No traditional forced read stays actual.
- **P2 held, sign and size.** Electricity nets **+£3,874.20 undercharged**. Undercharge is £7,366,
  inside £6,500 to £10,000. Overcharge is −£3,492, inside −£2,500 to −£4,500. **C7 decides the
  sign**, as predicted. It is a smart meter out of smart mode on direct debit. Its last bill was
  2019-06-30, and it leaves **+£5,017.34** (35,247 kWh) open over a 42-bill run. That is 37% of all
  gross open money. Its run is 42 bills here, not the 50 months it ran on the old books. The world
  drew C7 differently, as the attribution limit allowed.
- **P3 held.** Without its largest account, open electricity nets **−£1,143.14**, inside −£2,500
  to +£500. Away from C7, traditional electricity leaves 265 accounts net −£1,090. The estimates
  slightly over-bill at closure. That is consistent with no bias, but it is not shown to be.
- **P4 held.** Gas undercharge is £1,175 (£800 to £1,600). Gas overcharge is −£1,433 (−£1,000 to
  −£2,000). Gas nets **−£257.94**, inside ±£600. The largest gas account is `PROS-2019-0326g`, a
  smart meter, at −£327. Without it, gas nets +£69.
- **P5 held.** Gross unresolved money, |under| + |over| over both fuels, is **£13,466.84**. That is
  inside £11,000 to £18,000, against £12,865 the forced reads settled on 2248e3baf. The runs are
  short: median 3 bills, mean 4.95, max 49. The median account leaves £6.43 either way. The ten
  largest accounts carry 57.5% of the gross.

**By payment channel (open, net).** Direct debit carries **+£3,725.63**. Electricity direct debit
is +£6,580 / −£2,680 across 109 / 90 accounts, and gas direct debit is +£926 / −£1,101. Prepayment
and standard credit together are under £1,100 gross per fuel. So a direct-debit balance would net
most of this money against the account in the real process. This raw figure is not what a
departing customer would see.

**What this means.** The read rule moved money in the predicted direction and roughly at the
predicted size, so nothing here was surprising enough to need a cause. About £13.5k gross across 403
closing accounts over nine and a half years is now settled by nobody. Of that, £8.5k is undercharge
and £4.9k is overcharge. Without one pathological meter, the two directions nearly cancel
(electricity −£1.1k, gas +£0.1k). So the CoT dispute seed (scope brief B3) is mainly **many small
balances in both directions plus one large undercharge**. That one is C7, an out-of-smart-mode meter
unread for three and a half years. Its size is a finding about read coverage, not about the
closing rule. Whether the supplier's read-chase should have reached C7 before closure was not
checked here.

**Limits, carried.** (1) Money is raw: the SLC 21BA back-billing bar is not applied, and it would
cut C7's recoverable undercharge to the last 12 months. The direct-debit balance is not netted.
(2) A held estimate went out as £0, but the bill list keeps its estimated total, and no `held`
flag reaches the bill list. So the open undercharge is understated and the open overcharge is
overstated, by an amount this instrument cannot see. That bias runs toward overcharge, so it
argues against our own sign (F11), and the electricity undercharge holds anyway. (3) Attribution:
the forced-to-open move (408 forced on the old books, 2 now) belongs to 600be30bc. The money's size
also carries every other change since bdd6d1657. Electricity undercharge moved +£534 against
bdd6d1657, which is inside the £1,018 the two baselines differ by without the rule.
