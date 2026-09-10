# SEAT FINDING — the concordance sentence counts DECISIONS in one population and ACCOUNTS in another, and prints the ratio as if it were one

**Severity:** LATENT · **Lane:** A_strategy_governance

**Date:** 2026-09-10 (delivery seat, found while rewording `_UNEARNED_CLAIM_SENTENCE` to name the unit)

**Class:** `measurements_that_mirror`

---

## The short version

`_auc_reading` opens with:

> "Measured on 40 departures and 83 retentions -- **123 decisions on 100 accounts**."

The 123 is the count of decisions the concordance actually scored. The 100 is
`len(priced_accounts)` — every account the value arm put a price to. Those are not the same
population, and 123/100 is not "about one decision each": the 123 scored decisions sit on **17**
accounts, which the feed already publishes one key away.

```
site/data/value_arms.json  decisions.auc_population
  {"retained": 83, "left": 40, "scored_decisions": 123, "accounts": 17}
```

83 × 40 = 3,320 — the ordered-pair count the very next clause prints. So the producer holds the
right account count, in the same block, and the sentence reaches past it for a different one.

## Why it is the class it is

This is *"before dividing two numbers, say out loud what each one counts"* — except nobody
divides, which is what makes it slippery. The sentence sets two figures side by side and lets the
reader do the division. A reader who does it concludes each priced account contributed roughly one
renewal decision, and therefore that the concordance is close to a per-household comparison. It is
the opposite: 123 decisions on 17 accounts averages 7.2 decisions per account, so a single
household can contribute dozens of the 3,320 pairs, and the pairs are dominated by a handful of
long-lived accounts compared against themselves across eras.

That reading points the same way as the household claim this page spent 2026-09-10 withdrawing,
and it survives in the sentence that introduces the withdrawal.

## Why it is not fixed in the commit that found it

The reword that found it (`_UNEARNED_CLAIM_SENTENCE`, landed alongside this file) is scoped to the
claim-bearing clause, which is pinned to a named constant by
`site/test_the_stratified_concordance_reaches_the_reader.py::test_the_reading_a_reader_meets_is_the_one_the_producer_DECLARES`.
The `head` preamble is deliberately NOT pinned — the constant's own comment says so, because
pinning it would make the control one over p-value punctuation. So changing `head` changes bytes
no control is currently keyed to, in a string both branches share, and it deserves its own control
rather than a free ride on a reword's commit.

Fixing it also requires a decision this finding should not pre-empt: whether the honest sentence
names 17 (the accounts the scored decisions sit on) or names both and says what each counts. The
second is probably right — "123 decisions on 17 accounts, drawn from the 100 the arm priced" —
because the gap between 17 and 100 is itself a fact about the sample worth publishing, and a
figure published without the bound its sample size earns is worse than no figure.

## What would settle it

A leg asserting that every account count in this sentence comes from the SAME population as the
decision count beside it — keyed to the property, not to 17, so it stays green when a larger run
moves the number and goes red if the two populations drift apart again.

## What is NOT claimed here

That the concordance figure itself is wrong. 0.627 on 3,320 pairs against a 0.39–0.61 null is
computed over the population the producer says it is. The defect is in what the sentence tells a
reader that population *is*.
