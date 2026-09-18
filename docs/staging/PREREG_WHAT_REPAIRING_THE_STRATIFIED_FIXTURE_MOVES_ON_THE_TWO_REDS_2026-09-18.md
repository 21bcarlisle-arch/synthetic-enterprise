**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# Pre-registration: what repairing the stratified fixture moves, and what it does NOT

**Filed:** 2026-09-18, BEFORE the repair was written
**Claim id:** `repair-the-stratified-fixture-then-land-the-09-18-republish`
**Subject:** `site/test_the_stratified_concordance_reaches_the_reader.py` over the 09-18 book

---

## Replication first, and one correction to the finding it replicates

`docs/staging/SEAT_FINDING_THE_STRATIFIED_FIXTURE_CONSTRUCTS_ONE_OF_THE_TWO_FIGURES_ITS_ASSERTION_NEEDS_AND_INHERITS_THE_OTHER_2026-09-18.md`
is confirmed on the mechanism and **wrong on one fact about the tree**, which is recorded here
beside the confirmation rather than quietly fixed:

| | measured now, `5d4e422bb` |
|---|---|
| the book at `THREE_ARM_PATH` on HEAD | **`..._20260910.json`** (md5 `bd0936be`), not the 09-08 book the finding names |
| that book, this file | 22 passed, 1 skipped |
| the 09-18 book promoted, nothing else changed | **2 failed, 20 passed, 1 skipped** |

The finding says "22 passed / 2 failed 21 passed"; the pass count is 20 with one skip, and the
baseline book is 09-10. Neither changes the diagnosis. The cause is confirmed exactly as written:

```
unstratified auc  0.5566   null 0.3871 - 0.6129   inside_the_null TRUE    <- the fixture never touches this
within-year auc   0.4574                          inside_the_null TRUE
```

## The predictions, written before the repair

**P1 — the fixture repair works and is book-independent.** Recomputing `discrimination_auc` from the
same mutated rows, through the producer's own `_pooled_within_year_auc` (whose docstring states that
call over the whole population reproduces `discrimination_auc` to full precision), gives a perfectly
separated population: **AUC 1.0, outside the 0.3871-0.6129 null, above it** → the earned branch.
`test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading` goes green on the
09-18 book **and stays green on the 09-10 book**, because the fixture no longer inherits anything.

**P2 — that repair does NOT fix the second red, and the finding is wrong to expect it to.** The
finding says `test_the_reading_a_reader_meets_is_the_one_the_producer_DECLARES` "fails from the same
cause and should be re-measured after the fixture is repaired". It is the same CLASS and not the
same instance: that test takes the **live** feed as its subject and never calls the fixture, so no
change to `rank_within_year` can reach it. Prediction: after P1 lands, that test is **still red**.

**P3 — its own defect is a two-state control over a four-state producer.** It derives `earned` from
the within-year block alone and then asserts one of the two claim constants is on the page. The
producer reaches EITHER constant only from `_auc_reading`'s final `else` — which needs the
**unstratified** bound available, resolved, outside its null and not below it. On a run inside its
null the producer declares **neither** sentence, and a control with no branch for that asserts the
presence of a sentence its own producer never wrote. Same inheritance, opposite end.

**P4 — the repaired pair is 23 passed, 0 failed** on the 09-18 book, with the objective null control
still skipping or not according to whether the tree's HEAD moved the renewal objective.

## What would refute each

P1: the mutated feed's `null_bound.inside_the_null` is anything but `False`, or the 09-10 book reds.
P2: the second test goes green on the fixture repair alone — then the finding was right and this is.
P3: the producer turns out to publish a claim constant from a non-`else` branch.
P4: any count other than 23/0.

## The rule being applied, and the one being refused

Applied: *key a control to the property, not to today's answer* — a fixture that must construct BOTH
figures its assertion depends on, and a control that asks the PRODUCER which claim it declares
rather than re-deriving the gate in the test.

Refused: widening `HOUSEHOLD_CLAIM`'s assertion to accept the refusal. That leg is the only rung
that would notice a page which always withdraws, and relaxing it is the failure mode it exists to
catch one level up.
