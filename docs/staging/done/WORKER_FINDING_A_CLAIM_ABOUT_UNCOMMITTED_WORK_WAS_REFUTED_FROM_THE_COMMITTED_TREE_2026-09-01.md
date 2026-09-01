**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

**Class:** `uncommitted_and_orphaned_work` (existing class; RECORDED, so out of the register's population by that register's own rule).

# A claim about uncommitted work was refuted from the committed tree, and the method could not have failed

Two lanes worked the SVT capture on 2026-09-01 and reached opposite conclusions about the same
sentence. Merged at `a70a7ceff`, both turn out to have been right about their own tree — but one of
them used a method that **cannot return a negative result honestly**, and it came within one
sentence of instructing the next reader to abandon 421 lines of finished work.

## The sentence

`tools/capture_departure_factors.py` said the second half of the SVT repair was owed, and located it:

> 56 uncommitted lines in `simulation/renewals.py`, in no commit and not on `origin/main`

At `7cb667126` the other lane graded a clean-tree re-run and corrected that locator:

> * `rolls_active_renewal` is not in `renewals.py` and never has been. It is committed, at
>   `simulation/renewal_engagement.py:65`, and is CALLED every renewal at `run_phase2b.py:1771`.
> * The roll's answer feeds exactly one thing, `passive_churn_cap_for`, and then STOPS.
>   `build_renewal_schedule` never receives it.
>
> **A reader who believes the roll is uncommitted goes looking for lost work to recover, and there
> is none to find.**

## What was actually in the tree at that moment

`git diff simulation/renewals.py`, run in the shared worktree while that grading was being written:
**56 uncommitted lines**, adding `from simulation.renewal_engagement import rolls_active_renewal`
and, inside `build_renewal_schedule`, a passive branch calling it and extending the schedule with
`build_svt_schedule`. Beside it, **`tests/simulation/test_svt_assignment.py` — 365 lines, nine tests,
UNTRACKED**, with its R15 mutations already applied and their observed results recorded in its own
docstring.

Both are now committed at `8bf416115`. At the merged HEAD every bullet above is false:
`rolls_active_renewal` is in `renewals.py` at line 42 and line 154; `build_svt_schedule` has a second
call site at line 159 on the passive branch; `build_renewal_schedule` receives the roll. There were
421 lines to find.

## The defect is the method, not the conclusion

The other lane's **diagnosis was correct and is the valuable part** — the gap was the ASSIGNMENT, not
the roll, exactly as the August finding scoped it (*"not a missing rule, a discarded answer"*). The
56 lines ARE that assignment. Two lanes independently identified the same missing piece.

What does not survive is how the locator was refuted. The refutation was reached entirely from the
**committed** tree: a clean checkout of `68ec6825b`, `git show`, committed line numbers, a run whose
provenance file proudly records an empty dirty list. Every one of those instruments is *defined* to
not see uncommitted work.

**So the check could not have failed.** Run against a false claim it returns "not there"; run against
a true claim it returns "not there". A control with one reachable verdict is a constant, and this one
was pointed at the single class of claim it is structurally blind to. The generalisable rule:

> **A claim about uncommitted work cannot be refuted from the committed tree. It is refuted by
> reading the working tree, or it is not refuted.**

The rigour that produced the wrong answer is what makes this worth filing. The clean-tree run was
*better* practice than the thing it corrected — `systemd-run` so it outlived its launcher,
`wait_for.py --pid` and never `pgrep`, a capture stem of its own, provenance hashes, predictions
filed in advance and misses kept. Every one of those was right. **Isolation from the working tree was
the whole point of that setup, and it is exactly what made the tree's contents unreadable.** The
better the hygiene, the more confident the blind spot.

## Why this class, and why it nearly cost the most

`docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` is a BLOCKING register of
21 instances of finished work that never became part of the tree. This is that class with the
mechanism turned around: not work that was forgotten, but work that a correct-looking check
**certified as nonexistent**. `"there is none to find"` is an instruction to stop searching, written
into the one docstring the tool's own header calls *"the sentence a reader consults before deciding
whether re-capturing is worth the wall-clock"*.

The untracked control is the sharper half. `tests/simulation/test_svt_assignment.py` was invisible to
`tests_for('simulation/renewals.py')` — the selection is computed over the committed tree — so no
committed-tree instrument in this repository could see it: not the gate, not `git log`, not a clean
checkout. It is the file that demonstrates the assignment is *correct*, and every automatic route to
it ran through the one place it was not.

## Disposition

- Corrected in `tools/capture_departure_factors.py`'s docstring, beside the paragraph it corrects and
  not in place of it — the wrong locator, the right diagnosis, and the reason the method failed all
  stay legible. The other lane's grading is left standing as filed.
- The work is landed: `8bf416115` (assignment + control + the seven control repairs it forced).
- **Owed, and named rather than done here:** the capture has now been run three times against three
  different trees — the 1,266-row foreign artefact, the 1,373-row native run on the uncommitted tree,
  and the 0-row clean-tree run. None of them is this HEAD, where the assignment is committed for the
  first time. Every downstream figure fitted on any of them is stale by construction, including the
  whole-book block in `simulation/departure_level_anchor.py`'s working-tree copy, which is **still
  uncommitted and still fitted on the foreign artefact**. The re-run from this HEAD is the next
  experiment and it is a different one from all three.
