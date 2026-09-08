**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — no attainable book can read the effect the skill instrument measured) · **Class:** controls_that_cannot_fail

# RESULT — the unscored decisions are exactly the departures, so the method concordance conditions on survival

The Lane 0 item asked one question with two allowed answers. The measurement returns a third, and
the third is the one that matters.

> *"Take the 32 of 120 priced decisions that `method_skill.drop_out.by_reason.the_priced_term_carried_no_settled_row` discards, and establish whether they are unrecoverable in principle — nothing was billed under the chosen price, ever — or an artefact of the 365-day `_term_period_of` boundary and the run's length."*

**Unrecoverable in principle — and the reason is that they are the renewals where the household
LEFT.** Not attrition, not a boundary artefact: the drop class *is* the churn class. So the
concordation the page publishes as "does the method work" is computed over survivors only.

## The measurement

`the_priced_term_carried_no_settled_row` fires when the settled book carries rows for an account
but none inside the 365 days of the term the arm priced. Against that, `belief_vs_outcome` scores
each priced renewal `retained: true/false` by tallying `event_type == "churned"` in the world's
own `customer_events`. **The two are independent**: one is a failure to join the settled book, the
other is a count in the event log. Neither is computed from the other, and no code path shared
between them could make them agree.

They agree exactly, in every A/B artefact on disk:

| artefact | priced | scored | `..no_settled_row` | renewals the world recorded as churned |
|---|---:|---:|---:|---:|
| `value_cycle_ab_s1_three_arm_20260830.json` | 20 | 6 | **10** | **10** |
| `value_cycle_ab_s1_three_arm_20260830b.json` | 20 | 6 | **10** | **10** |
| `value_cycle_ab_s1_three_arm_20260831.json` | 120 | 86 | **32** | **32** |
| `value_cycle_ab_s1_three_arm.json` | 120 | 86 | **32** | **32** |
| `value_cycle_ab_s1_three_arm_20260903.json` | 104 | 61 | **43** | **43** |
| `value_cycle_ab_gas_admitted_2026-09-07.json` | 94 | 54 | **40** | **40** |
| `value_cycle_ab_gate_reverted_2026-09-07.json` | 94 | 54 | **40** | **40** |
| `value_cycle_ab_leg_id_fixed_2026-09-07.json` | 216 | 170 | **40** | **40** |
| `value_cycle_ab_s1_three_arm_20260908.json` | 214 | 168 | **40** | **40** |

Nine runs, five distinct values, three states of `tools/run_value_cycle_ab.py`, book sizes from 20
to 216 priced decisions. And the identity is a SET identity, not only a count, as far as the
artefacts can be read: joining each run's `dropped_sample` and `scored_sample` against that run's
`belief_vs_outcome.scored_decisions` gives

- **144 of 144** sampled decisions dropped for this reason were departures,
- **82 of 82** sampled decisions the concordance SCORED were retentions,
- **zero counterexamples in either direction.**

## The mechanism, which is obvious once the number is in front of you

A household that leaves at the renewal never begins the term that was priced. The term settles no
day, `folded[(account, term)]` has no entry, and because the account settled under its *earlier*
terms the funnel classifies it as `the_priced_term_carried_no_settled_row` rather than as a failed
join. The final bill lands before `term_start`, so `bisect` attributes it to the previous term.

Nothing was billed under the chosen price. **No re-cut of the 365-day boundary and no longer run
recovers a single one of them — the rows do not exist to be re-attributed.** The half of the item's
question that hoped for a recoverable artefact is answered: there is none, and every artefact on
disk has *zero* drops of this class that are not departures.

## Why this is BLOCKING and not a tidy "unrecoverable, move on"

The item's framing — and `drop_out`'s own published reading — treat this class as a sample-size
bound to be waited out:

> `_skill_drop_out_reading`, live: *"THE SAMPLE CANNOT BE WIDENED FROM THIS BOOK: 168 is what the method has earned, and only a larger settled book adds to it."*

That sentence is misleading in the way that costs most. A larger settled book adds decisions **and
drops the same share of them**, because the exclusion is not random — it is the outcome. The
concordance therefore answers a narrower question than its name and than the page around it:

> **Given the household stayed, did the arm's price rank the joint value it produced?**

It is blind by construction to every decision where the price is what drove the household away,
**and the bias runs in the direction that matters.** Over-pricing is the failure mode the mission
sentence exists to catch — *"value is created and THEN shared"*, transfer is not creation — and
over-pricing shows up as a departure. A departure deletes the decision from the sample instead of
scoring it low. The instrument built to tell value created from value transferred cannot see the
transfers that succeeded well enough to end the relationship.

This is a selection in the ESTIMAND, not a bound on the sample. `A46` (book depth) does not fix
it. The 1,506-decisions-needed ceiling arithmetic does not fix it, and the item's own arithmetic
— *"the 32 dropped would take those 46 accounts to 2.57"* — was never available at any book size.

## The drawn premise was spent twice over

The item's numbers came from `site/data/value_arms.json`, which still publishes the 2026-08-31
run: 120 priced, 86 scored, 46 accounts, 1.87 scored per account. The run of **2026-09-08** —
already on disk when the item was drawn — reads 214 priced, 168 scored, 72 accounts, **2.33 scored
per account** against the 2.38 the ceiling needs. The scoring rate moved, for reasons recorded in
`SEAT_RESULT_THE_BILLING_ACCOUNT_FILTER_TRIPLED_THE_ARMS_DECISIONS...` and not for the reason this
item proposed. **The page is a run behind, which is a second thing owed and is not this finding.**

## The estimand that replaces concordance-over-settled-outcomes

The item asked for this by name if the decisions turned out unrecoverable. It is:

> **Score every priced decision over a FIXED HORIZON from its own term start** — the joint value
> the decision actually produced within, say, 365 days of the price being set — **counting a
> departure as the small-or-zero value it really produced rather than dropping it.**

A household that leaves contributes the pounds it was billed before leaving and nothing after: a
real, computable outcome, and a low one. Under that estimand a price that drove the household away
ranks *below* one that did not, which is the comparison the whole instrument exists to make.
Three properties it must carry, none of which the current cut has:

1. **No conditioning on survival.** The denominator is decisions PRICED, not decisions settled.
2. **The horizon is fixed and declared**, so a decision late in the window is censored explicitly
   rather than silently dropped — that IS a run-length artefact and must be counted as one.
3. **The counterfactual is still required**, so `no_published_counterfactual_rate_for_the_term`
   (6 in the latest run) stays a coverage gap and does not quietly become an outcome of zero.

Not built here. Building it is a world-side read over the settled book on a new key and it needs
its own pre-registration, for the reason the `term_start` pair needed one: two causes moving at
once are unattributable afterwards.

## What landed with this document

1. **`method_skill.survivorship`** in `tools/run_value_cycle_ab.py` — the split, measured per run
   rather than asserted from this document: how many of the class the world recorded as departures,
   how many are NOT attributable to one, and how many SCORED decisions were departures. That last
   count is 0 in every run on disk and a non-zero one **refutes** this finding's reading loudly.
   Fails closed with a named reason when a run publishes no event log — "nobody left" and "we were
   not told who left" are different worlds.
2. **`_skill_survivorship`** in `tools/generate_value_arms_data.py` — passthrough on the same
   fail-closed shape as `_skill_drop_out`. A run predating the split publishes the ABSENCE. The
   corrected sentence is NOT inlined in the generator: a claim about a run that run never made is
   what this page exists to refuse.
3. **Five controls**, mutation-proved. Two poison rounds run BEFORE the real shape is asserted —
   a drop that is not a departure, and a scored decision that is one — because a block that
   reported survivor-conditioning on every input would pass a test written only against today's
   answer. Battery: 5 mutations, 5 killed. The sixth (`no_settled_row = list(dropped_rows)`,
   dropping the reason filter) **SURVIVED** on the first pass — a missing test, not an
   equivalence: the fixture held only one drop, so the filter was unreachable. The fixture now
   carries a `declined` and an `account_has_no_settled_row_anywhere` drop beside it and the
   mutation dies. Recorded because it is the same shape as the item's own question: a class that
   looks like the whole population until something else is put next to it.

## What is next

1. **The page is a run behind.** `site/data/value_arms.json` publishes 2026-08-31; the newest run
   is 2026-09-08. Re-publishing is what puts the survivorship split in front of a reader — the
   generator carries it, and until a run does, the page correctly says it cannot tell.
2. **The rendered surface.** The data layer refuses honestly; no page element reads
   `method_skill.survivorship` yet, so by this project's own rule ("done means the rendered value
   changed") the reader-facing half is NOT done and is not claimed to be.
3. **Pre-register the replacement estimand** before building it, and grade it against this
   document. The prediction worth writing down now: under a fixed-horizon estimand the scored
   population rises from 168 to ~208 on the 2026-09-08 book and the concordance **falls**, because
   the decisions being added are the ones that produced least. If it rises, the arm was
   over-pricing the households it kept, which is a different and worse finding.
4. **`drop_out`'s reading needs correcting where it is generated**, not only qualified here. Left
   deliberately: changing the sentence and adding the block that refutes it in one commit would
   leave nothing able to show the two disagreed. The disagreement is the evidence.
