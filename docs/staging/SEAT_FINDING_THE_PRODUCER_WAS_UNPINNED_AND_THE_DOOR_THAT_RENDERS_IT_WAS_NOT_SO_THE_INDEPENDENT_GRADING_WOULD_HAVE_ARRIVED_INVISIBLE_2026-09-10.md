**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# FINDING — the producer was un-pinned and the door that renders it was not, so the independent grading would have arrived invisible

LATENT rather than BLOCKING: nothing is refused by this and no reader has met a wrong page, because
no artefact on disk carries the field yet. It fires on the FIRST A/B pass that writes one — which is
the pass this item exists to run, and which was in flight when the defect was found.

**Filed:** 2026-09-10, delivery seat. Continues
`run-the-ab-pass-and-let-the-independent-grading-reach-the-page`, whose premise was re-measured live
and found unspent: `1d9e0a85c` is an ancestor of `origin/main`, and all eleven
`docs/observability/value_cycle_ab_s1_three_arm*.json` artefacts predate the field.

---

## What was found

`1d9e0a85c` fixed a control-that-cannot-fail in `tools/generate_value_arms_data.py`.
`_independent_grading_today` had published a hard-coded `is_it_available_today: False`; the commit
re-keyed it to read `available` off the artefact, carried the producer's own refusal reason through,
and added a control asserting **both branches can be taken over one artefact differing in one
field**. That work is correct and it is not what this finding is about.

**The page that consumes it was not re-keyed.** `site/capabilities/index.html` renders the block in
one function, and its last line was:

```js
+ " " + prose(g.why_not) + " " + prose(g.what_would_have_to_be_recorded) + "</p>";
```

`why_not` and `what_would_have_to_be_recorded` exist **only on the unavailable branch**. The
available branch returns three different keys — `is_it_available_today`,
`graded_against_the_control_arms_outcomes` and `what_is_still_not_independent` — and the door read
none of them.

## What a reader would have got on the day the run landed

`esc()` maps `null`/`undefined` to `""`, so:

1. The sentence explaining the absence **disappears**, and nothing replaces it.
2. `what_an_independent_population_must_look_like` goes on rendering, in the requirement tense it
   was written in — *"THE OUTCOME MUST NOT BE A FUNCTION OF THE BELIEF BEING GRADED"* — beside an
   artefact that has just met all three. The remedy reads as outstanding on the day it is delivered.
3. **The concordance itself renders nowhere.** The one number the whole block exists to make
   checkable reaches no reader.

Nothing throws, nothing is blank, no control goes red. The page just quietly stops saying anything
about the thing it is describing, and does it in the *pessimistic* direction — which reads as
caution and is exactly as wrong as the flattering kind.

## Why nothing caught it

`test_the_page_says_a_bigger_book_would_not_make_the_grading_population_independent` was already
careful about the trap next door:

```python
# NOT PINNED TO FALSE. ... A `is False` here would go red the day the run supplies the grading
assert isinstance(gap["is_it_available_today"], bool)
```

That is right, and it is the reason this was invisible. The control refuses to pin the FLAG — and
then asserts nothing whatever about what the available branch **renders**. The producer was proven
on both branches; the door was proven on neither. A control over one end of a pointer says nothing
about the other, and the end that was proved is the end that was already fixed.

## The class

**Un-pinning a producer does not un-pin its consumer, and the consumer's pinning is invisible
precisely because the branch it cannot render is the empty string.** The 2026-09-10 cost render one
page over is the same shape at the same seam; this is its twin, found because the pointer was probed
at both ends rather than at the end the commit had touched.

Generalising the habit that found it: when a commit's own message says *"it now reads the artefact's
own available flag"*, the next question is **who renders the branch that was previously unreachable**
— not whether the flag is computed correctly.

## The fix

`site/capabilities/index.html`: the diagnosis paragraph (what the arm's own price moved, and why
dropping those rows is not the repair) renders on **both** branches, because it is a property of the
book and does not become untrue when an independent grading arrives. What follows it is keyed to
`is_it_available_today`:

* **unavailable** — `why_not` and `what_would_have_to_be_recorded`, as before.
* **available** — the concordance, printed beside `belief_vs_outcome`'s own figure so the pair is
  the reading; its retained/left population; the share of priced renewals it covers; the count of
  priced terms that reached no outcome in the control world; and
  `what_is_still_not_independent`, because the OUTCOME becomes independent of the belief and the
  POPULATION does not.

The requirement list's lead-in flips tense with the branch.

## The controls, and the mutations that prove they can fail

Both added to `site/test_the_stratified_concordance_reaches_the_reader.py`, which drives the **real**
door through `site/_live_harness.mjs` over the **published (index)** bytes and the **real** producer.
The fixture bends the three-arm **artefact**, never the page feed — hand-writing the page block would
have asserted only that the render can display a dict built to be displayable.

| control | mutation | result |
|---|---|---|
| `test_a_run_that_HAS_the_independent_grading_puts_the_figure_on_the_page` | restore the pre-fix render (available branch emits `""`) | **RED** |
| `test_a_run_WITHOUT_it_still_says_why_and_does_not_show_a_figure` | render the grading paragraph unconditionally | **RED** |

Each mutation reds its own test and leaves the other green, so neither is tautological and the pair
is not one assertion written twice.

The null control needed a second assertion to earn its teeth. An unconditional paragraph puts no
false *figure* on the page — the fields are absent, so it degrades to "no figure" — and would have
survived a test that only looked for the number. It would still **announce an independent grading
for a run that has none**, so the heading is the subject, not the digits.

23/23 green in that file.

## What is next

The A/B pass itself, which was running while this was written:
`python3 -m tools.run_value_cycle_ab --level-arm --out docs/observability/value_cycle_ab_s1_three_arm_20260910.json`.

The prediction it grades is pre-registered in
`docs/design/PREREGISTRATION_THE_BELIEF_GRADED_AGAINST_AN_OUTCOME_ITS_OWN_PRICE_DID_NOT_CAUSE_2026-09-10.md`,
filed **before** the run: the commit's prose *"the two AUCs will not be far apart"* turned into a
bound (`|Δ| ≤ 0.10`), a direction (`> 0.5`), a gate on the world digest, and the join risk (P3)
that would make the AUC not worth quoting at all.
