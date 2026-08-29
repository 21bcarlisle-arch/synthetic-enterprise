**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `A48_enterprise_value_is_the_method_not_the_book`

# Pre-registration: what the sourced-cost re-run must show, written before it finishes

**Written 2026-08-28 ~21:00 BST, while the run is executing.** Filed now so the prediction cannot be
fitted to the answer.

## What changed, and why the arms might move

`0850eadcd` (20:46 BST) deleted `saas/growth_mandate.COST_PER_ACQUISITION = {"resi": 150.0,
"SME": 400.0}` and pointed the live campaign at `saas/opex_ledger`'s sourced PCS commission
(£27.50 single-fuel per billing account) with the I&C trail moved to an ongoing per-kWh
`broker_commission_gbp()`. Campaign acquisition spend fell **£135,285 → £23,708.90**.

The published arms artefact (`docs/observability/value_cycle_ab_s1_three_arm.json`,
`generated_at` **2026-08-28T14:08:48Z**) predates that commit by five hours. **Every arm figure now
on the site is denominated in the invented costs.** That is what this re-run is for.

The arms are *not* obviously insulated from the change. `simulation/run_phase2b.py:199` builds its
book from `live_population()`, and `simulation/live_population.py:213` puts the campaign's
**winners** into that book — `won = [c for c in _won_customer_dicts(_campaign(_pre_growth_book(seed),
seed)) ...]`, filtered at the win against `campaign_quotes_paid_for`. Acquisition price gates how
many quotes the campaign can pay for, quotes gate wins, wins are book. So there is a live path from
the constant to the arm figures.

## The prediction: all three arms move by ~£0

**I predict the control, value and level arms come back materially unchanged** — within run-to-run
noise, most likely bit-identical — and that the £111,576 saving shows up in the annual report's
opex (account 6300) and *not* in the arm comparison.

The mechanism, and it is falsifiable: **the quote population does not change with the price.**
`0850eadcd` measured the same campaign at both prices and reported £129,285 over **1,066 quotes**
invented vs £23,709 over **that same 1,066-quote population** sourced — £121.28/quote vs
£22.24/quote, same denominator. Identical quotes → identical wins → identical book → the arms score
the same settled records. And acquisition spend is not one of them: `run_value_cycle_ab`'s
`GROSS_TO_NET_LINES` is levies, network, capital cost and bad debt, summed from
`phase2b.all_records`. There is no acquisition line between gross and net.

## The tension I am holding, which is the interesting part

**A 5.4× price cut that buys no extra quotes is strange on its face.** If `campaign_quotes_paid_for`
genuinely gates on affordability, cheaper quotes should buy more of them. That it does not means the
binding constraint is somewhere else — the prospect stock (`PROSPECTS_PER_YEAR`), or the budget is
not actually enforced at the quote. The second is already filed independently:
`WORKER_FINDING_THE_FOUNDER_BOOK_EXPOSES_A_CAMPAIGN_THAT_KEEPS_QUOTING_AFTER_THE_BUDGET_STOPS_2026-08-28.md`.

So the two outcomes and what each would mean:

- **Arms unchanged (predicted).** The sourcing repaired the company's P&L by £111,576 and moved the
  published comparison by nothing. The reader is owed exactly that sentence, and the honest headline
  is that the arm comparison never saw acquisition cost at all. It also *corroborates* the
  budget-not-enforced finding: price fell 5.4× and bought no extra book.
- **Arms moved.** My prediction is refuted and the mechanism is not what I have written above — the
  campaign *is* affordability-capped, the book grew, and the 1,066-quote figure in `0850eadcd`'s
  message was measured under conditions that do not hold in the A/B's own run. If that happens the
  correction goes beside this paragraph, not over it, and `0850eadcd`'s attribution split
  (4.4% cutoff / 78.0% sourcing) needs re-deriving too.

## What is being run

`python3 -m tools.run_value_cycle_ab --level-arm`, three full passes, ~30 min on the prior run's
rate (12 passes in 124 min, `three_arm_and_floor_run.log`). Output goes to a **new** path
(`value_cycle_ab_s1_three_arm_sourced.json`), not over the published artefact, so the two can be
diffed and so a publish running concurrently cannot read a half-written file. Promoting it to the
canonical path and restating the site is the next tick's work.

**The noise floor is not being re-run here, and that bounds what this can say.** The 2026-08-27
floor put `selection_gbp` at mean +£504 with sd £4,402 and range £8,781 across three seeds — wider
than most effects in the table. A delta smaller than that is not distinguishable from the seed
draw, and I will not read one as if it were.

---

## STATUS 2026-08-29 12:05Z — the run this file preregistered never produced its artefact

**Written beside the prediction, not over it.** `docs/observability/value_cycle_ab_s1_three_arm_sourced.json`
does not exist, in the working tree or in any commit. Whatever happened to the 2026-08-28 21:00 BST
run, it did not reach the path this file names, so **the prediction above has been ungradeable
since it was written** and the arms on the live page are still the 2026-08-28T14:08:48Z ones
denominated in the invented costs. That is a fact about this record, not about the prediction: the
prediction stands exactly as filed and is graded below when there is something to grade it with.

**The replacement run is executing now** and it is strictly wider than the one preregistered here,
because it also repairs the superseded-clock defect this file's last paragraph names as its own
bound. Both legs, ONE session, off today's book, to new paths:

```
docs/observability/value_cycle_ab_s1_three_arm_20260829.json    (--level-arm, 3 passes)
docs/observability/value_cycle_ab_s1_noise_floor_20260829.json  (seeds 11111,22222,33333, 9 passes)
log: docs/observability/arms_rerun_20260829.log
```

The seeds are the SAME three the 2026-08-27 floor used. A floor re-drawn on different seeds would
not be comparable with the one it replaces, and the whole point of re-running the floor is to stop
quoting an error bar measured on a different book from the figure it bounds.

**What does NOT change about the prediction.** It was filed before any of this and is graded on its
own terms: all three arms materially unchanged, with the £111,576 acquisition saving showing up in
opex (account 6300) and not in the arm comparison. The reading rule stated above still binds and
now binds harder — **no delta smaller than the NEW floor's own spread may be read as an effect.**
The old floor's £4,402 sd against a £504 mean is why that bar is expected to swallow most of what
the table shows, and the new floor is being measured precisely so the bar quoted is the one that
belongs to this book.

**One thing the prediction did not anticipate and should be graded against too.** It reasoned from
a fixed 1,066-quote population. Today's campaign record is 505 wins with 415 refused by the
settlement budget — a uniform 17.89% sample — so the *book* the arms score is now a sample of the
company's wins rather than all of them. If the arms have moved, that mechanism is a candidate
alongside the two the prediction names, and it was not on the list.

**Estimated completion.** ~12 passes at roughly 10 min each on this machine, so ~2 hours from
2026-08-29T11:53:54Z. This tick is bounded and will end first; the grading is the next tick's
first job, and this section is what makes it findable.
