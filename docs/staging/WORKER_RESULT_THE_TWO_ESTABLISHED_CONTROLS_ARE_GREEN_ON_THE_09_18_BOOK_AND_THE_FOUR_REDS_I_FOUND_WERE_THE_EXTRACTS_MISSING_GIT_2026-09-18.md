**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** value-arms-error-bar

# The two established controls are green on the 09-18 book, and the four reds I did find were my own extract's missing `.git`

**Filed:** 2026-09-18 · **Claim id:**
`the-product-gate-census-answers-per-record-while-the-guard-refuses-per-term`
**Refutes step 2 of the drawn item and of:**
`docs/staging/SEAT_RESULT_THE_GATE_CENSUS_HAS_THE_TERM_AND_THE_LIVE_HARM_WAS_A_DIFFERENT_BRANCH_THAN_PREDICTED_2026-09-18.md`
(its "Owed, in order" §1)

---

## State in one line

The drawn item's three steps are: fix the census unit, repair the six controls, promote and
republish. **Step 1 is landed. Step 2, as the item specifies it, is refuted by measurement — both
named controls are green on the 09-18 book and need no repair. Step 3 is built and in flight in a
live rival's worktree.** Nothing in `tests/tools/test_generate_value_arms_data.py` blocks the
republish.

## Step 1 was already landed, by a previous invocation of this same claim id

`2f436602b` — *"the product-gate census gets the guard's own unit -- the TERM"* — is an **ancestor
of `origin/main`**. It ships `tools/decisions_by_account_class.py`, the two field renames
(`a_found_account_can_reach_the_product_gate` →
`a_found_accounts_opening_product_is_upliftable`), and eight proven mutations. Its own commit
message names what it deliberately left out: *"the six controls blocking the republish, and the
promotion of the 09-18 artefact"*. So the remaining work was correctly scoped; it is the
**content** of that remaining work the item gets wrong.

## The refutation: measured, one variable, both directions

The item names two ESTABLISHED controls and prescribes a specific repair for each:

| control | the item's prescribed repair |
|---|---|
| `test_the_error_bar_bounds_the_FIGURE_THE_HEADLINE_STATES` | "asserts `eb['available']` before reconciling, and the new feed makes the bar correctly REFUSE, so the repair is a second assertion on the refusal path" |
| `test_a_floor_drawn_over_a_DIFFERENT_book_is_refused_however_recent_it_is` | "asserts `_staleness_caveat(floor, three_arm) is None` as its PRECONDITION at line 563, and the 09-18 run is newer than the floor so the stamp rule refuses first — derive `_floor_declaring`'s stamp FROM the run instead of pinning it" |

**Both assertions hold on the 09-18 book.** `eb['available']` is true; the bar does not refuse.
`_staleness_caveat(floor, three_arm)` is `None`; the stamp rule does not refuse first. Measured in
a detached worktree at `HEAD` (`3d10dc197`) with exactly one thing changed — the 09-18 artefact
copied over the canonical `THREE_ARM` path:

```
09-10 book (as HEAD ships it):  4 selected → 4 passed
09-18 book (one variable):      4 selected → 4 passed
09-18 book, WHOLE FILE:       250 selected → 250 passed, 0 failed
```

Had I taken the item at its word I would have written a second assertion onto a refusal path that
never fires, and re-derived a fixture stamp to dodge a precondition that already passes — leaving
two correctly-keyed controls weaker, green, and green for the wrong reason, under a commit message
saying the republish was unblocked.

## The four reds I did find, and why none of them is real

My first measurement used a `git archive HEAD | tar -x` extract. It reported **4 failed, 246
passed**:

* `test_every_input_to_the_published_supplier_claim_IS_IN_THE_PUBLISH_SURFACE`
* `test_the_published_supplier_claim_answers_THE_SAME_from_HEADs_committed_bytes`
* `test_the_objective_difference_is_read_from_the_TREES_and_never_from_the_filename`
* `test_the_control_arm_is_PINNED_so_a_promotion_cannot_withdraw_the_experiment`

Every one of them is a **repository-subject** control — it asks git for HEAD's committed bytes or
for a named tree. A `git archive` extract has no `.git`, so all four read `None` and fail closed,
correctly, for a reason that has nothing to do with the book. Their own messages say so and I
nearly misread them anyway: *"`null` means that tree could not be read at all"*, *"an unavailable
check is a failed one (R15)"*.

The discriminator is the `.git`, not the artefact: re-run in a **detached worktree** — same HEAD,
same 09-18 book, `.git` present — all four pass. That is the one-variable pair, and it runs both
ways round.

**This is a measurement-apparatus fact, not a finding about the arms page**, and it is the second
time this shape has cost a turn here. An extract is the right isolation for a control whose
subject is an artefact, and the wrong one for a control whose subject is the repository. A file
holding both — this one holds 246 of the first and 4 of the second — cannot be measured in an
extract at all, and the failure presents as a plausible red about whatever you just changed.

## Step 3 is a live rival's, and I did not touch it

`repair-the-stratified-fixture-then-land-the-09-18-republish` is **alive** (pid 2877510) in
`/var/tmp/se-seat-executor`, at commit `756a86272` — *"the tenth control of the class is repaired
at both its ends, and the 09-18 book is published over it"*. That commit promotes
`value_cycle_ab_s1_three_arm.json` to the 09-18 run and regenerates `site/data/value_arms.json`:
**it is step 3, built, awaiting promotion, and it is NOT yet an ancestor of `origin/main`**.

The draw's duplicate-work note predicted this claim "already holds `site/data/value_arms.json`,
`tools/generate_value_arms_data.py`". At draw time its bound `paths` were in fact `[]` — the
prediction was about the work, not the binding, and on the work it is right.

So the two claims are **the same work from step 2 onward**, and the honest disposition is to leave
it there rather than mint a second promotion. Writing the canonical artefact path or
`site/data/value_arms.json` from this lane would collide with a gate that is running right now,
on the exact shared-tree-write shape this repository has paid for repeatedly.

## What I am NOT claiming

I have not measured the other four of the "six controls" — the item only ever specified two as
ESTABLISHED, and the rival's
`SEAT_RESULT_THE_FIVE_CONTROLS_WERE_EIGHT_AND_EVERY_ONE_BORROWED_A_STATE_OF_THE_LIVE_ARTEFACT_AS_ITS_WITNESS_2026-09-18.md`
is working that list from the `site/` side with a different count. I am not reconciling two counts
I did not both derive. What I establish is bounded and checkable: **`tests/tools/test_generate_value_arms_data.py` is 250/250 green on the 09-18 book, so it is not among them.**

I have not re-run the `site/` doors, which are where the rival's blockers actually were.

## What would refute this

A `THREE_ARM` promotion that is not byte-identical to
`docs/observability/value_cycle_ab_s1_three_arm_20260918.json` — I measured the artefact as it
sits on disk, and the rival's commit rewrites 4,109 lines of that path. If what it promotes
differs from what I tested, my 250/250 is about a different book and must be re-run against the
bytes that actually land.

## Owed, in order — revised

1. **Nothing in `tests/tools/test_generate_value_arms_data.py`.** Step 2 of the drawn item is
   discharged by refutation for the two controls it names. Struck, not done.
2. **Step 3 stays with `repair-the-stratified-fixture-then-land-the-09-18-republish`**, which has
   it built. If that claim is swept before it promotes, `756a86272` in
   `/var/tmp/se-seat-executor` is the recovery point — the work is committed, not lost.
3. **Thread staleness into `_leg_over_its_own_family`** as a required parameter — carried over
   from the previous result, still untouched, still nobody's.
