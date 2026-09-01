**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

**Class:** `uncommitted_and_orphaned_work` (existing class, so this instance is born archived).

# The owed C1b landing is seven control repairs, and the roll's own control was never in git either

`WORKER_PREREGISTRATION_WHAT_A_NATIVE_SVT_CAPTURE_MUST_SHOW_2026-09-01.md`, graded at `68ec6825b`,
closes with three owed items and this is the first of them, verbatim:

> 1. **Land the C1b roll**, or this capture is unreproducible from any commit.

`tools/capture_departure_factors.py`'s committed docstring says the same thing the same way — the
roll is *"56 uncommitted lines in `simulation/renewals.py`, in no commit and not on `origin/main`"*,
and the second half of the repair is *"still owed"*. Both sentences describe a **filing action**: the
code exists, it works, somebody needs to type the commit. A reader budgets minutes.

**It is not a filing action. Landing those 56 lines turns seven green controls red**, and the record
contains no sentence that says so.

## Measured, both sides, on the same three files

The pre-commit gate's own selection for the changed file:

```
$ python3 -c "from tools.pre_commit_test_gate import tests_for; print(tests_for('simulation/renewals.py'))"
tests/company/crm/test_renewals_book.py
tests/simulation/test_renewals.py
tests/simulation/test_renewals_approval_routing.py
```

At **clean HEAD** (`git archive HEAD` into a scratch tree — no worktree, nothing touched):

```
43 passed in 0.23s
```

In the **working tree**, the same three files, the only difference being the uncommitted C1b roll:

```
7 failed, 36 passed in 0.24s
FAILED tests/simulation/test_renewals.py::test_multiple_terms_all_have_notice_date
FAILED tests/simulation/test_renewals_approval_routing.py::test_outcome_neutral_tariff_identical_with_and_without_approval_wiring
FAILED tests/simulation/test_renewals_approval_routing.py::test_non_routine_move_is_routed_through_submit_resolve_with_real_latency
FAILED tests/simulation/test_renewals_approval_routing.py::test_non_routine_move_shows_pending_on_the_human_operable_queue_mid_flight
FAILED tests/simulation/test_renewals_approval_routing.py::test_all_routine_moves_still_log_completed_events_unchanged
FAILED tests/simulation/test_renewals_approval_routing.py::test_replaying_a_non_routine_build_is_idempotent_on_the_shared_log
FAILED tests/simulation/test_renewals_approval_routing.py::test_every_governance_decision_is_transacted_strictly_before_it_takes_effect
```

**Every one of the seven is the control working correctly on a subject that is no longer there.**
Six of them fail on their own NON-VACUITY guards — `assert any(e.status == "pending" for e in
events)` — because their fixtures are resi customers built across a term boundary, and after C1b a
passive resi household rolls onto SVT at its anniversary instead of being handed another fixed term.
No second fixed term means no struck rate, no `PRICING_MOVE`, and nothing for the approval workflow
to route. The seventh quantified 42 days' notice over *every row in the schedule*, and an SVT segment
has no notice by construction. **Not one of the seven is a bug in C1b.** That is what makes the
record's framing expensive rather than merely incomplete: the repair is real work with no defect
under it, so a reader who budgeted minutes finds nothing wrong and has no reason to suspect the
estimate.

## The part the gate could not have told anyone

`tests/simulation/test_svt_assignment.py` — nine tests, R15 mutations applied and recorded in its own
docstring, naming the absorbing-SVT first draft and the inertia-hazard interlock — **is untracked.**
It is the control that says the roll is *correct*, and it has been sitting outside git beside the
roll it guards for the whole time the roll has been outside git.

So it is not in `tests_for('simulation/renewals.py')` either, and it could not be: **the selection is
computed over the committed tree, and an untracked control is invisible to it.** Had anyone landed
the roll by the ordinary route, the gate would have run three files, two of which go red, and the
one file that demonstrates the change is right would never have been selected. The gate would have
reported the change as a pure regression. This is the known class *a selection-based test gate is
blind to a consumer it did not select*, with the sharper edge that here the unselected consumer is
the **exculpatory** one.

## Why this sat for three stretches

The focus note says the capture was *"named in focus for three consecutive orientations and
relaunched zero times"* and reads that as a scheduling failure. The capture itself was: it died with
its launching tick, which is a class already written down. **But item 1 of what the capture owes did
not sit for want of scheduling.** It sat because every document that mentions it — the prereg's owed
list, the capture tool's docstring, the archived finding
`WORKER_FINDING_THE_SVT_RECORDER_IS_IN_GIT_AND_THE_ROLL_THAT_FILLS_IT_IS_NOT_2026-09-01.md` — states
the *fact* that the roll is uncommitted and none of them states the *cost* of committing it. A
worker drawing it on a bounded tick reads "land the C1b roll", runs the gate, sees seven reds it did
not cause, and has no way in the time available to tell a regression from six vacuity guards and a
scope change. **The honest move at that point is to leave it, which is what happened, three times.**

**The generalisable shape: a filed "owed next" item states what is missing and almost never states
what supplying it costs, and the cost is where the item actually stalls.** An owed item whose price
is not in the record will be re-drawn, re-read and re-abandoned by every bounded invocation that
meets it, and each abandonment leaves the record looking exactly the same as the last.

## Disposition — repaired in this commit, not merely filed

- The roll is landed, with `tests/simulation/test_svt_assignment.py` landed **in the same commit**.
  A seam is not landed until its control is, and this one had further to travel than usual: the
  control was not late, it was untracked.
- `test_multiple_terms_all_have_notice_date` is re-keyed to the **property** — 42 days' notice is a
  property of a contract ending — and drives the active and passive legs explicitly rather than
  reading whichever way the roster happens to roll `C1` (which is passive, and yields exactly one
  fixed term, so the naive scoped repair passed over an empty list: the first version of this fix
  was itself vacuous). The SVT complement is **asserted, not skipped**: a segment that acquired a
  42-day notice would be a fixed term wearing a new label. Mutation-proven — setting the SVT
  `notice_date` back 42 days in `simulation/svt_product.py` turns it red, reverted after.
- The six approval-routing tests get one autouse fixture forcing the roll active, patched on
  `simulation.renewals` where the name is **bound** (patching `simulation.renewal_engagement` would
  leave the top-level import in place and do nothing — the tests passing is the proof it reaches).
  Their subject is approval routing *given a renewal*; C1b decides whether there is one. C1b's own
  behaviour stays `test_svt_assignment.py`'s subject, which holds both the OFF and the ON.

## Still owed, and NOT repaired here

Items 2 and 3 of the prereg's list are untouched and stay owed: failing `tools/population_anchor`'s
five 2022 consumers closed (that file is outside this stretch's pathspec), and re-running the capture
now the producer is in git to confirm the whole-book block is byte-stable. **The block in
`simulation/departure_level_anchor.py`'s working-tree copy is another lane's, fitted on the foreign
1,266-row artefact, and was deliberately not committed here** — the prereg refused to adopt it on one
capture and finding (b) of that grading establishes the artefact it was fitted on is not this world.
