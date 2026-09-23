**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `uncommitted_and_orphaned_work`

# Nothing in the belief's chain has landed, the pile is seven paths and not five, and my own promotion of the artefact was wrong

**Claim:** `the-belief-landed-and-every-artefact-downstream-still-describes-the-old-one`
**Premise re-measured at draw:** both cited commits are ancestors; the work is **not** spent.

This turn re-ran the chain, tried to land it, was refused by eleven reds, and found that the
sentence the previous invocation of this same claim left behind is wrong in the one place that
decides what the next invocation does.

## The correction that matters most, because the next lane will otherwise trust it

`docs/staging/SEAT_RESULT_THE_BELIEFS_DOWNSTREAM_CHAIN_IS_RE_DERIVED_AND_ITS_READING_CANNOT_BE_TAKEN_IN_THE_SHARED_TREE_ALONE_2026-09-23.md`
says, under *"The landing is split"*: **"The producer half landed."**

It did not. Asked of git rather than of the note:

```
$ git log --oneline -2 -- tools/churn_belief_size_response.py
54aaedd20  (2026-09-22 16:08)  the 154-account book the arms were scored over ...
7179a7087                      the company's churn belief is flat in household size ...

$ git diff HEAD --stat tools/churn_belief_size_response.py
 tools/churn_belief_size_response.py | 455 ++++++++---  (393 insertions, 62 deletions)
```

The last commit to that path predates `fc390b918`. **Nothing in this chain is landed** — producer,
artefact, feed, generator and site door are all still only in the shared working tree, and that
note is itself unlanded. A split-landing sentence written by an invocation that landed neither half
is the most expensive kind of inherited claim: it retires the producer half from the next lane's
attention while leaving it entirely undone.

## The pile is SEVEN paths, not the five the item named

The draw named five. The gate refused the commit of those five (plus my own two) with eleven reds,
and the missing members are the producer's own test suites, which at HEAD still assert the
pre-`fc390b918` belief:

| Red | What it asserts at HEAD |
|---|---|
| `tests/tools/test_churn_belief_size_response.py::test_the_knee_is_a_bill_and_not_a_consumption` | the claim `0637be0f1` refuted |
| `...::test_the_belief_is_flat_in_size_exactly_where_the_world_is_not` | the claim `fc390b918` inverted |
| `...::test_the_arms_book_is_identified_and_a_near_miss_is_refused` | |
| `...::test_the_artefact_publishes_both_books_and_says_which_one_the_reading_quotes` | |
| `tests/tools/test_generate_value_arms_data.py` × 4 | incl. a `TypeError: NoneType` on the withdrawn field |
| `site/test_the_flat_churn_belief_reaches_the_reader.py` × 3 | green in the shared tree, red on HEAD's model |

Both test files are **dirty in the shared tree** with the repairs already written — by the previous
invocation of this same claim. So the pile is:

```
tools/churn_belief_size_response.py           docs/observability/churn_belief_size_response.json
tools/generate_value_arms_data.py             site/data/value_arms.json
site/test_the_flat_churn_belief_reaches_the_reader.py
tests/tools/test_churn_belief_size_response.py        <- NOT named by the draw
tests/tools/test_generate_value_arms_data.py          <- NOT named by the draw
```

The three site-door legs are the same defect seen from the other end: they pass in the shared tree
and fail on HEAD's model, because the tree they were written against is not the tree the gate
builds.

## My own promotion was wrong, and the evidence I offered for it did not support it

I promoted `docs/observability/churn_belief_size_response.json` from `WATCHED_DERIVED_ARTEFACTS`
into `COVERED_DERIVED_ARTEFACTS`, on the reasoning that
`test_a_watched_derived_artefact_that_reproduces_must_be_promoted` fires the moment the artefact is
regenerated — which is true, and is why the control exists. **The evidence I gave was worthless.**

I ran the producer twice across two different HEADs (`5e64bb852`, then `60cd120df` after a merge)
and got byte-identical output, and read that as "a function of its commit, carrying no tree stamp".
Both runs stood in a tree carrying another lane's uncommitted `BILL_STRESS_MAX_RATIO` ceiling in
`company/crm/churn_model.py`. **Byte-identical across two HEADs with the same dirty dependency is
evidence that the dependency did not move, not that the artefact is a function of any commit.** The
prior note had already measured the difference the ceiling makes — 10 deaf legs and a 13,358 kWh
deaf edge in the shared tree against 4 deaf legs and no edge at HEAD.

Reverted. The reasoning is recorded in the constant's own comment beside the empty set, so the next
lane meets the refuted argument at the point of temptation rather than in a staging file.

## What is genuinely new: the spread has three answers, and one of them is not a quantity

The prior note graded the finding's pre-registered prediction at 6.8× (electricity) and 7.1× (gas),
and was **right** to record it as directional only — a ratio of probabilities and a ratio of
multipliers are not the same quantity and must not be differenced. I add the parameter it did not
sweep. Measured over the 244 legs of the arms' book, one variable moved (each leg's own
consumption), in the shared tree:

| probe | belief min | belief max | spread |
|---|---|---|---|
| 250 → 300 GBP/MWh (rise) | 0.0613 @ 100 kWh | 0.7483 @ 41,576 kWh | 12.21× |
| 250 → 275 GBP/MWh (rise) | 0.0606 @ 100 kWh | 0.4283 @ 41,576 kWh | 7.06× |
| 250 → 225 GBP/MWh (**cut**) | **0.0** on 117 of 244 legs | 0.0789 @ 35 kWh | **not a quantity** |

Two things follow.

**The spread is under-specified without the rate direction and the move size.** "The belief's
spread across the book" has three answers depending on parameters the prediction never named. The
flattering one (12.21× against the world's 11.57×) is the one a hurried grader publishes alone, and
it is also the one that invites the very division the prior note correctly refused.

**Under a cut the ordering INVERTS** — the highest churn probabilities sit on the *smallest*
households. That is the size term working correctly: a bigger household responds more to the same
percentage, and responding more to a cut means leaving less. Nothing is published from the cut
direction: a ratio over a zero minimum is the unbounded-quotient class this repository has already
cleared sixteen instances of.

**The 117 exact zeros are filed as a question, not an answer.** A churn probability of identically
0.0 says "this customer will certainly never leave". Whether that is a floor doing its job or a
clamp hiding one belongs to whoever owns `company/crm/churn_model.py`, and is not settled here.

## What is owed, in the order it has to happen

1. **`company/crm/churn_model.py`'s `BILL_STRESS_MAX_RATIO` ceiling must land first.** Until it
   does, this chain's artefact is a measurement of another lane's uncommitted work and no reading
   taken from it is a property of any commit. Everything below is blocked on it.
2. **Then land all seven paths in one commit** — the two test suites are not optional extras, they
   are what makes the other five green.
3. **Only then may the artefact be promoted** into `COVERED_DERIVED_ARTEFACTS`.
4. **The site lane is separately wedged** by two reds at clean HEAD in
   `site/test_the_baseline_comparison_reaches_the_reader.py`, already filed in
   `SEAT_FINDING_ORIGIN_MAIN_CARRIES_SEVEN_REDS_THAT_NO_COMMITS_GATE_SELECTION_REACHES_2026-09-22.md`.
   The page half cannot land through that whatever happens to 1–3.

**This is BLOCKING and the reason is the ordering, not the size.** Any lane that redraws this item
and trusts either "the producer half landed" or the five-path pile will spend a whole invocation
re-deriving that it cannot commit.
