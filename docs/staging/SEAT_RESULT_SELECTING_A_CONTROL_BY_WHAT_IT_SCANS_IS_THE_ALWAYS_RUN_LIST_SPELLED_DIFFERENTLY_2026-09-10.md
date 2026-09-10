**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `decide-what-selects-a-control-whose-subject-is-a-whole-package`) · **Class:** controls_that_cannot_fail

# RESULT — selecting a control by what it SCANS is the always-run list spelled differently

Answers the Lane 0 delivery question: *what should select a control whose subject is a whole
package?* The previous seat left three doors and recommended door 3 — change the selector so a test
declaring a directory subject is selected by changes to that directory — **"scoped by measurement
first, because the whole argument against it is a cost nobody in this thread has looked at."**

I looked at the cost. **Door 3 is refuted on measurement, and it collapses into door 1.**

## First: the number this class was carrying could not be re-run

`SEAT_RESULT_THE_STEM_SELECTOR_CANNOT_REACH_TWENTY_SEVEN_WHOLE_TREE_RATCHETS` reports **27**
members. That census was an uncommitted throwaway script — nothing in the tree reproduces it, so the
figure could not be re-run, disputed, or watched for growth. It is now a committed tool,
`tools/whole_tree_subject_census.py`, implementing the **pre-registered predicate copied unnarrowed**
from `docs/staging/records/PREREG_HOW_MANY_WHOLE_TREE_RATCHETS_CAN_THE_STEM_SELECTOR_NEVER_REACH_2026-09-10.md`.

Re-derived from that same stated predicate, the answer is **109**, not 27.

| quantity | previously published | re-derived | note |
|---|---|---|---|
| unreachable whole-directory-subject tests | 27 | **109** | same stated predicate, committed implementation |
| …where the walk is *provably* the counted population | not reported | **18** | `--strict-dataflow` |
| already on `CONTROL_TESTS` (reachable) | 3 | **5** | leg 3 discharges these |

I am **not** claiming 109 is the truer number and 27 the wrong one. The predicate over-counts by
construction — legs 1 and 2 are proximity-in-a-module, not dataflow — and the two implementations
differ in how widely they read leg 2 and in whether `site/*.py` tests are in the population. The
finding is not "27 was wrong"; it is that **a number nobody can reproduce cannot be compared to
anything, which is the same shape as the defect the census exists to measure.** The over-count now
has a measured size (109 loose, 18 strict) rather than an apology, and the predicate has
deliberately not been narrowed after seeing the answer.

## The measurement that refutes door 3

Modelled over the **last 40 real non-merge commits**, against `select_targets` as the gate actually
computes it. The widened rule is the honest reading of "select by what it scans": a staged path
under root R selects every censused test naming R as a subject. Root granularity is not a
simplification I chose — it is *the finest granularity the source can support*, because what a test
declares in its own text is a directory, never a file set.

| pool | selected today (median) | ADDED by subject-selection | commits adding nothing |
|---|---|---|---|
| all 109 | 18 files | min 31, **median 50**, max 75 | **0 of 40** |
| strict 18 | 18 files | min 6, **median 12**, max 14 | **0 of 40** |

**The load-bearing cell is the last column, and it is zero in both rows.** Subject-selection fires
on every single commit in the sample. Even the *most* narrowly-scoped commit of the forty pulls in
31 of the 109, and 6 of the 18. It never targets; it always fires.

That is the refutation, and it is arithmetic rather than opinion: a rule that fires on every commit
and takes two-thirds of its pool on the median commit **is an always-run list**. Door 3 does not
avoid door 1's cost — it pays a similar cost, and adds a derivation that can be wrong in both
directions on top. Given the choice between a list you can read and a heuristic that reaches
approximately the same set by inference, the list is strictly better: it is auditable, each entry
states what it costs, and it cannot silently change its mind when someone edits a docstring.

**Why it cannot be fixed by a better derivation.** Every commit touches one of these roots — that is
what a root *is* here. To narrow below the root you would need the test to declare which *files* it
scans, which is precisely the population it exists to discover and cannot enumerate in advance.

## So what does close the class

Not a longer list of 109. **The strict-dataflow 18 is the affordable, defensible unit**, and it is
now measured rather than argued:

- **390 tests, 43.8s** for the whole strict pool as one invocation, measured on this machine.
- Against the live budget finding (`…HOOK_BUDGET_IS_SPENT_BY_TWO_TEST_FILES`, 393s of 600s already
  spent by two files): **+7.3%**, taking spent to ~437s of 600s. Affordable, and *not* comfortably
  so — which is a fact about how little headroom that budget has, and belongs in the record rather
  than rounded away.

Two of the 18 (`tests/test_isolation_guards.py`) are **red in this shared tree** — live-ledger
fingerprints written by other lanes' test processes, not by this work. Adding a red file to a list
that runs on every code commit wedges every lane, which is strictly worse than the defect being
fixed; that is the lesson the withheld `test_seat_guard_daemons.py` line already recorded once. So
**the 18 are not being added in this commit**, and grading each one green in a clean HEAD extract is
what the next increment does. I would rather leave that stated than land a wedge.

## What landed

- `tools/whole_tree_subject_census.py` — the pre-registered predicate as a committed, re-runnable
  tool. `--strict-dataflow` bounds the over-count; `--cost N` models the widening over real commits.
- `tests/tools/test_whole_tree_subject_census.py` — six falsifiers keyed to the **predicate**, not
  to today's count, so an honest repair to the tree does not read as a regression.
- `docs/design/orphan_baseline.json` — **one row**, declaring the census deliberately dormant, the
  same way `tools.git_subject_census` and the other on-demand censuses are recorded.

**Why a hand-added row and not `--freeze`, said out loud because the ratchet offers the freeze
first.** `freeze()` writes `module_count` from the tree it runs in, and this is a shared tree
carrying ~1,240 modified paths across several lanes. A freeze taken here would bank *those lanes'*
reachability as the floor — the orphan list beside it would be this working tree's answer, not the
repository's, and the disagreement would be invisible afterwards. One row, with `module_count` left
at 1,128 exactly where it was, changes only the fact it states.

**The wiring I wanted and did not take.** The honest caller is `tools/pre_commit_test_gate.py`
itself — the census's subject is that file's selector, and a paragraph there would put the
re-runnable count in front of the next reader of those nine comments. I built it and **backed it
out**: this tree is three commits behind origin, and origin's `fcbf92b9b` added the ninth
`CONTROL_TESTS` entry (`test_seat_guard_daemons.py`) *and* the nine `refuse_if_foreign` guards that
make it green **in one commit**. Landing origin's gate bytes onto a HEAD without the guards splits
that pair, and the gate duly went red naming all nine entrypoints. The pair is atomic and taking
half of it is a defect, so the citation goes in once this tree is at origin. That is the first item
below, not a loose end.

**Mutation-proven, poison round run before the green was believed** — three separate poisons, each
reddening the control that names its defect, green returning on restore:

| poison | went red |
|---|---|
| predicate refuses everything | `test_the_predicate_can_say_yes` (+2) |
| leg 2 stops being required | `test_both_legs_are_load_bearing` |
| leg 3 stops discharging | `test_leg_three_excludes_a_listed_test` |

The positive leg is written first and deliberately: a predicate that refuses *everything* passes
every refusal test, and this census's whole failure mode is quietly returning the empty set.

## Prediction recorded beside the result

I predicted before running the cost model that subject-selection would fire on **roughly half** of
commits and be affordable at the strict pool. **The first half was wrong, and wrong in the direction
that decides the question**: it fired on 40 of 40. Had it been half, door 3 would have been the
right answer and I would have built it. It was not close.

## What is next

0. **Advance this tree to origin, then cite the census from `pre_commit_test_gate.py`** — the
   backed-out wiring above. Blocked only on the tree being three behind; `origin_reconcile` gated
   the merge clean and pushed it, but the shared tree would not advance past two paths another lane
   holds uncommitted (`background/head_red_register.py`, and a staging finding whose working copy is
   a stale rival of origin's).
1. Grade each of the 18 strict members green in a **clean HEAD extract** (not this shared tree), and
   add the green ones to `CONTROL_TESTS` with their measured cost stated, as the eight existing
   entries do. The two `test_isolation_guards.py` reds are a separate question about test isolation.
2. The remaining 91 loose members are **not** owed a line each. The census is what makes the class
   countable; whether any individual member is load-bearing is a judgement its own lane should make
   when it next touches that tree.
3. **Not proposed: a meta-control refusing a new whole-tree-subject test unless it is listed.**
   CLAUDE.md's "a control that only guards your own controls is usually not worth having" applies,
   and it could not fix the 109 already here.
