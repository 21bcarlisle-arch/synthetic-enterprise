# The independent grading would have reached the page as a bare AUC with no bound and no twin

**Lane:** A_strategy_governance · **Severity:** RECORDED · **Date:** 2026-09-10

## The drawn item, and its premise

Lane 0 drew: *run the A/B pass so an artefact carries `belief_against_control_outcomes.available`,
then let `site/capabilities/` publish it beside the withdrawal.* The premise is **live**, not spent.
`1d9e0a85c` is an ancestor of `origin/main`, so the FIELD landed — but no artefact on disk carries
it. `site/data/value_arms.json` publishes
`the_grading_population_is_not_independent.is_it_available_today: false`, correctly and now read from
the artefact rather than pinned.

## The run

`longjob-value-cycle-ab-20260910` — a full three-arm pass with `--level-arm`, launched into its own
cgroup at 12:24:46Z, writing `docs/observability/value_cycle_ab_s1_three_arm_20260910.json`. The
comparable prior run (`_departure_20260909`) took 37 minutes. **It was still in flight when this
turn ended**; re-ask it with `python3 -m background.launch_liveness --check`. Promotion to the
canonical path and the regenerate are the next turn's work and are NOT claimed here.

## What this turn landed, and why it is not the run

The publishing half was wired but **incomplete in a way only an available artefact would expose**,
which is why no suite caught it: every artefact on disk takes the refusal branch.

1. **The figure had no bound.** `_independent_grading_today`'s available branch published
   `discrimination_auc` and a population count and nothing saying what a signal carrying *no*
   information reaches on a population that size. That is the shape `_auc_null`'s own docstring
   records this file paying for once already — *"THE FIGURE WENT OUT UNBOUNDED"* — and it would have
   arrived on the page the moment the run wrote the field. It now carries `null_bound` from the same
   enumerator every other rank statistic on this page uses, and `cannot_tell` in words.
2. **On the real population the bound cannot be computed, and that is now explicit.** The value arm
   priced 278 renewals; retained×left is far past the exact enumerator's 4,000-pair cap, so
   `_auc_null` refuses with its reason and `cannot_tell` says *"this run carries no interval"*. The
   page's least-bounded figure would otherwise have been its largest sample — exactly backwards.
3. **Only one side of a comparison rendered.** The producer's own docstring says *"READ THIS BESIDE
   `belief_vs_outcome`, never instead of it"*. The whole content of the independent figure is the
   pair. `read_it_beside_the_value_arm_figure` now publishes both gradings of the one belief with
   both nulls, each side naming what its outcome counts.
4. **No difference between the two AUCs is minted.** They grade one belief over heavily overlapping
   rows, so they are not independent measurements and neither bound licenses a reading of the gap.
   The block says what would be needed (a permutation over which outcome vector each row is scored
   against) and publishes no verdict. The commit's filed prediction — *the two AUCs will not be far
   apart* — is therefore gradable by eye against two bounds, and is **not** graded by a number the
   page mints.

Keyed to the property throughout: nothing asserts the two figures are close, or far, or which side
of their nulls they land on.

## Two corrections against my own work, kept beside the result

* **My first draft of the bound test asserted the fixture's 0.61 cleared its null.** Printing the
  null at the real inputs said 0.390–0.610 — 0.61 sits *on* the edge. The figure was a guess where a
  measurement was one command away. The test now exercises **both** sides of the partition (0.61
  renders the sentence, 0.93 withholds it), which is the control the guess would never have earned.
* **My "no difference is minted" test survived its own poison round.** It tokenised `json.dumps` on
  whitespace and kept tokens passing `.replace(".", "").isdigit()` — blind to a leading minus *and*
  to JSON's trailing comma, so it saw neither `-0.0169` nor `0.0169,`. A poison that minted the
  subtraction passed it green. It now walks the structure and tests both signs. **A control that
  cannot fail is why the poison round runs before the battery, not after.**

## Evidence

* `tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py` — 11 pass;
  with `tests/tools/test_run_value_cycle_ab.py`, 203 pass.
* Poison 1 (drop `null_bound`/`cannot_tell`) → 2 red. Poison 2 (mint the subtraction) → 1 red *after*
  the tokeniser was fixed, green before. Both reverted; suite green.

## One thing this turn did NOT do, deliberately

`tests/architecture/test_static_quality_ratchet.py` is red in the shared tree (I001 census 1308 vs
frozen 1309) and **green in a clean HEAD extract**. The count went *down*: another lane has fixed an
I001 in the working tree without freezing it. Freezing it here would bank their work and wedge them,
so this landed by `surgical_land` — which gates the tree the commit would create — and the baseline
is untouched.

## What is next

1. When the run settles, promote `_20260910.json` to `docs/observability/value_cycle_ab_s1_three_arm.json`
   and regenerate `site/data/value_arms.json`. The available branch then renders with nobody editing
   a string.
2. Grade the filed prediction on the page, beside it, whichever way it falls.
