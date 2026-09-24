**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The "ceiling" is the probability the dice actually used, and the drawn item had its position in the chain exactly inverted

**Seat, 2026-09-23.** Lane 0 delivery, focus id
`say-what-the-ceiling-is-and-price-what-this-book-can-settle`.

---

## What the item asked, and what it got wrong on the way

The item was right that the quantity `renewal_churn_belief.ceiling` was being published under a
word it had not earned, and right about which column it is. Its account of **where that column sits
in the world's chain was inverted**, and the inversion mattered, because it is the whole reason the
quantity fails to bound anything.

The item said the ceiling is `realized_churn_probability`, "the base its roll starts from, **before**
the passive cap, switching multiplier, price position, income stress and satisfaction that actually
decide who leaves."

`simulation/customer_events.py:782` says the opposite in the code and at line 773 in its own words:

```python
# Phase QA: realized_churn_probability is the true, fully-adjusted (passive
# cap / market conditions / income stress / satisfaction) probability that
# was actually rolled against, captured BEFORE any retention-offer effect.
realized_churn_probability = round(1.0 - effective_p_retain_pre_offer, 4)
```

It is **after** every adjustment the item listed, and before exactly one thing — the retention offer.
The quantity that is the base *before* those adjustments is `churn_probability`, which this same
panel already publishes separately as `seeded_leg`, in those exact words. Measured: the two are
different quantities, mean 0.3446 against 0.1882 across the capture's 102 rows, 937 discordant pairs
out of 5,151.

**Why the inversion mattered.** Under the item's reading the failure to bound has an easy
explanation — a pre-adjustment base is missing the terms that decide departures, so of course it
under-orders. That explanation is unavailable. The truth is the harder one: this *is* the number the
dice rolled against, and it still does not bound, for a reason that is about finite samples rather
than about missing terms.

## What was established, by measurement

**The per-route oracle does not read the column — and reproduces it exactly anyway.**
`tools/measure_churn_heterogeneity.py:1365` uses `realized_churn_probability` for the *all-route*
figure, but the renewal entry scores with `renewal_hazard(row)`, a recomputation from the capture's
four world factors through `departure_risks.build_departure_risks` + `total_departure_probability`.

I predicted this meant the item had named the wrong quantity. **That prediction is refuted.**
Recomputing the hazard for all 102 rows and comparing orderings against the logged column:

| against | concordant | discordant | tied |
|---|---|---|---|
| `realized_churn_probability` | **5,151** | **0** | **0** |
| `churn_probability` (the seeded leg) | 3,410 | 937 | 804 |
| `company_churn_estimate` | 3,063 | 1,962 | 126 |

Identical ordering on every pair, same min/max/mean to four decimals. The recomputation *is* the
column. The item named the right quantity by the wrong route and described it backwards.

**Why it is not a bound.** An ordering by the true probability maximises concordance **in
expectation**. It does not maximise the concordance **realised on one draw** of 102 decisions
carrying 41 departures — that realisation is itself a random variable, and the page already prints
its spread: the permutation interval beside it is 0.276 wide. Anything inside a width that size can
outscore it without anyone having beaten the world.

**The four things it did that a bound cannot do**, all on this page's own rows, all now derived in
code rather than typed:

1. The belief scores **above** it — 0.6706 against 0.5911 on the same 384 pairs.
2. It **failed its own null** (0.5911 inside [0.3620, 0.6380]) while the belief **cleared** its own
   (0.6706 against a 0.6328 upper end).
3. Pooling reverses the order: pooled the ceiling leads 0.6717 to 0.5940; stratified — which is the
   published reading — the belief leads 0.6706 to 0.5911.
4. On the second roll of the same world's dice they swapped: ceiling 0.6486 clears, belief 0.5847
   does not.

## The settlement statement, and why it is a refusal

"Does the per-customer decision discriminate" is **two questions**, and differencing them into one
figure is this project's named recurring failure. They have different evidence and different fates:

| | quantity | carries its own null | sign across the two draws | settled by a finite book |
|---|---|---|---|---|
| A | belief vs chance (excess over 0.5) | yes | **+0.1706, +0.0847** — agrees | not from this evidence |
| B | belief vs the world's own ordering (the gap) | **no** | **+0.0794, −0.0640** — inverts | **no finite book** |

**B has no upper bound, and for two independent reasons.** The difference of two AUCs on the same
rows carries no permutation null of its own — differencing two figures that each have an interval
does not produce an interval — and the two draws put it on opposite sides of zero. A requirement of
the form `(k / value)²` over a denominator whose sign is undetermined does not produce a large
number; it produces no number. Published as that refusal, with the count at each draw's own
magnitude beside it under a key that names the borrowed width.

**And the finding is that the book is not what binds.** At either draw's own gap magnitude the
requirement is **283 and 442 scored decisions** — two to four times this book, plainly reachable on
this world. What is not reachable is a determined sign. The two draws differ in the renewal dice and
nothing else: same world digest, same record, same tariffs, same hazards, same company code. **No
book size makes two rolls of one world agree with each other.** That is a statement about the whole
programme, not about this panel, and it is why "no finite book settles this from this estimate" is
the honest publication rather than a number.

## A prediction of mine that was refuted mid-task

I first reached for a cross-draw t-interval to decide whether each sign was determined, and it gave
the flattering-looking answer for the wrong reason: t(1) is 12.706, so a two-observation interval
contains zero for **every** quantity on this page — question A's as readily as question B's. An
instrument that returns the same verdict for a quantity whose draws agree and one whose draws invert
is measuring the draw count, not the quantity. It was dropped. What is published instead is whether
the two draws **agree on sign** — the whole evidence actually in hand — and, for question A, the
producer's own existing gate in `inference_claim.detectability`, which already withholds a count
wherever a reading fails its own null.

## What landed

* `tools/generate_value_arms_data.py` — `_ceiling_is_not_a_bound` (the four crossings, each asked as
  a property of the draws, never typed) and `_renewal_belief_settlement` (the two questions, priced
  through `detectability` rather than a second implementation of it). `_withdrawn` now carries the
  settlement statement, computed once in the panel and rendered in two places.
* `site/capabilities/index.html` — the table row is no longer labelled "the ceiling"; the label is
  the feed's own name for the quantity, and the correction renders beneath the table in amber. The
  settlement statement renders in `#arms-note` beside the withdrawal register.
* `tests/tools/test_the_ceiling_is_named_for_what_it_is_and_the_book_is_refused.py` — ten legs.
  `test_the_whole_partition_is_reachable` and `test_both_sign_verdicts_are_reachable` are single
  assertions over **both** states, because a verdict function stuck on "not a bound" or a gate stuck
  on "refuse" passes every test written about the firing branch alone.

**Mutation-proven, four mutations, each on a distinct leg:** `is_a_bound` forced False → the
partition control and the undecidable control red; the crossing comparator inverted → the crossing
control and the prose-tie control red; `determined` forced True → both sign controls red; the
borrowed-width flag hardcoded False → the borrowed-width control red. Pristine bytes restored and
checksum-verified after each.

## What is NOT claimed

The feed key `ceiling` is unchanged. A feed key has readers this producer cannot see, and a rename
is a silent break in every one of them; what changed is what the key says about itself and the
label the page prints. Nothing here re-opens the withdrawal — the belief is not claimed to order
departures, and the opposite is not claimed either.

---

## Two things found on the way that are not this item

**1. The shared tree's `tests/tools/test_generate_value_arms_data.py` is a stale revert AND holder
work at once.** Its working copy has mtime `2026-09-22 11:31` against a last commit to its own path
of `2026-09-22 21:51` — ten hours older than the commit it sits on — and carries 1,771 deletions.
It is also holder work: `refresh_to_head` refuses it because the copy supplies **9 names HEAD does
not have** (`CURRENT_RUN_164`, `LATER_RUN_154`, `_book_of`, two `test_a_registry_row_*` functions and
four more). Both tags are true at once, which is the two-door shape: `isolate_hunks --survey` then
`surgical_land --content` for the holder's hunks, and only then `refresh_to_head`.

**This is what was reddening 22 tests for every lane.** In the shared tree those two suites read
`23 failed, 265 passed`; at HEAD they read `317 passed`. The one-variable control settles the
attribution: HEAD plus only this item's four files reads `316 passed, 1 failed`, and that one
failure is this item's own (below). **22 of the 23 are that reverted copy, not anyone's code.** The
stale copy also collects 29 fewer tests than HEAD, so a lane reading only the red count would
conclude its change broke things it never touched.

Not repaired here: landing another lane's nine names is not this item, and the pathspec for this
commit does not include that file's working copy. Its repair belongs to whoever holds it, and the
door is named above.

**2. A control pinned to today's wording, repaired to its own stated property.**
`test_the_ceilings_sentence_names_the_ROUTES_OWN_decision_count` exists — correctly — to stop a
count being typed into prose where it can rot, and its docstring says so: "Fires on: putting any
literal back in that sentence." Its assertion pinned the literal phrase `"these same {} decisions"`.
That is a claim about the current wording, not about the count being derived, so it went red when
the sentence was replaced by a more honest one that names the quantity and still derives the count
from `route`. A control pinned to the current state reds when the code becomes more honest and stays
green when the claim rots — exactly backwards, and this repository's named recurring shape.

Repaired to the property and mutation-proven both ways: the count is driven to two values and the
sentence must contain the driven one and NOT the other, which no typed literal can satisfy at both
drives. Verified — passes on the derived sentence, reds when a literal `102` is put back.

Landed over **HEAD's bytes** via `surgical_land --content`, not over the contested working copy:
`isolate_hunks` separates hunks by author and not by age, so a pathspec commit would have carried
that ten-hour-old revert inside this one.
