**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The stratified fixture constructs one of the two figures its assertion needs and inherits the other

*BLOCKING because it is the only thing standing between origin/main and the republish over one
priced book: `surgical_land` refuses the promotion on these two reds, and the page they guard is
correct.*

**Filed:** 2026-09-18 · **Claim id:** `republish-the-arms-decomposition-over-one-priced-book`
**Subject:** `site/test_the_stratified_concordance_reaches_the_reader.py`
— `test_a_run_whose_belief_DOES_rank_within_the_year_keeps_its_household_reading` (:644)
— `test_the_reading_a_reader_meets_is_the_one_the_producer_DECLARES`
**Established at:** `5167f1281`, promotion applied and reverted in one worktree

---

## The one-variable measurement, taken before any diagnosis

| | `site/test_the_stratified_concordance_reaches_the_reader.py` |
|---|---|
| HEAD's book (09-08) on `THREE_ARM_PATH` | **22 passed, 1 skipped** |
| the 09-18 book promoted, nothing else changed | **2 failed, 21 passed** |

One variable. These two are **caused by the promotion** and are not pre-existing HEAD reds.

## The cause, measured rather than argued

`_auc_reading` composes the earned household sentence only when the **unstratified** bound clears
its null. The reachability fixture `rank_within_year` mutates
`belief_vs_outcome.scored_decisions`, setting `believed_p_retain` to 0.9/0.1 — and that moves the
**within-year** figure only. Measured on the mutated feed over the 09-18 book:

```
within-year auc:      1.0      inside_the_null: False   <- the fixture DID construct this
unstratified auc:     0.5566   inside_the_null: True    <- the fixture never touches this
page says:            "The observed value is INSIDE that interval, so this run does not
                       distinguish the belief from a coin flip in either direction."
```

**The page is right and the control is wrong.** The unstratified figure genuinely sits inside its
null on a 104-decision book, so refusing the household claim is the correct answer. The control
asserts the claim appears, having constructed only one of the two figures its own assertion
depends on.

## It is the SAME CLASS the nine were, in a file that repair never reached

`5167f1281` re-keyed nine controls whose common defect was *borrowing a state of the live artefact
as a witness*. This is the tenth, and it is in `site/`, which that commit did not touch. The
fixture constructs half its precondition and **inherits the other half from whichever run is
promoted** — it passed only because the 09-08 book's unstratified AUC happened to sit outside its
null. A smaller, more honest book takes that away, and the control reports "the gate is refusing
everything" about a gate that is refusing exactly one thing, correctly.

Its own docstring calls it "THE LOAD-BEARING NULL CONTROL" and says the fixture makes the figure
clear "on the page's own arithmetic rather than on a number typed here". The first half is true of
the stratified figure and false of the one the sentence is actually gated on.

## The remedy

The fixture must construct **both** figures, because the assertion needs both. The two are computed
from different inputs — that is the whole defect and it is the thing to establish first: find what
`discrimination_auc` is computed from (it is NOT `scored_decisions`, which is why the mutation does
not move it), and move that population in the same fixture, so the unstratified figure clears its
null by construction.

**Do not widen the assertion to accept the refusal.** The control is load-bearing: a page that
always withdraws tells a reader nothing, and this is the only rung that would notice. Relaxing it
is the failure mode it exists to catch, one level up.

`test_the_reading_a_reader_meets_is_the_one_the_producer_DECLARES` fails from the same cause and
should be re-measured after the fixture is repaired rather than diagnosed separately.

## What this blocks

The promotion and republish are otherwise complete and green: `tests/tools/test_generate_value_arms_data.py`
250 passed, `site/test_the_baseline_comparison_reaches_the_reader.py` 166 passed 2 skipped,
`tests/tools/test_the_renewal_funnel.py` 24 passed, all on the promoted feed at `5167f1281`. The
gate refuses on these two alone. The promoted artefact and regenerated feed are NOT landed and
must be rebuilt from `docs/observability/value_cycle_ab_s1_three_arm_20260918.json`, which is
tracked — nothing is lost.
