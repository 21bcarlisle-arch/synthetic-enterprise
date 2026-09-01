**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Class:** `uncommitted_and_orphaned_work` (existing class, so this instance is born archived).

# A staged control landed in another lane's commit, and its evidence did not

`tests/architecture/test_a_test_module_imports_a_name_that_exists.py` is on `origin/main` at
`adf4bed6e`, whose subject is class registers. Nothing in that commit's message mentions the
control, why its scope was changed, or the three measurements that justified the change. The code
is landed and the reasoning for it is in no commit. This file is that reasoning.

## What happened, in order

I drew Lane 0's "five controls in the working tree and in no commit". Two had already landed and
`6fed05942` had ruled on three; a sixth and seventh had appeared since. Of those, this one was the
only control **green at HEAD alone** and therefore landable with nothing else. I edited it, staged
it with `git add`, and started a pathspec commit under `shared_tree_lock`.

The gate refused that commit on `tests/background/test_fork_reconciler.py::test_evaluate_worktree_
reap_enforce_removes_only_eligible` — a red belonging to no work of mine, in a file I did not
touch. Measured again once the tree settled: **71 passed**. It was another lane mid-edit in the
shared tree, and it cost a full gate cycle.

While that cycle ran, `adf4bed6e` landed from another lane and **carried my staged file with it**,
along with `simulation/renewals.py`, `tests/background/test_class_debt.py` and six staging records.
The content that landed is mine, repair included — `git show adf4bed6e:<path>` contains
`_tracked_test_modules` and `ls-files`, and the working tree is clean against it. What did not land
is the message, so the commit that carries the control says nothing about it.

**This is the BLOCKING finding's shape, one level down.** `WORKER_FINDING_A_DAEMON_COMMITTED_INTO_
THE_FIRST_UNATTENDED_WRITERS_WORKTREE` records `fork_salvage` committing into live worktrees twice
in ninety minutes. Here no daemon was involved and nothing was lost: a `git add` puts a path in the
SHARED index, and the next lane to run a broad commit owns it. Staging is how you tell git "this is
mine"; in this tree it is also how you hand it to whoever commits next. The pathspec discipline in
CLAUDE.md protects the tree from *my* commit. It does not protect *my* staged work from anyone
else's.

## The evidence that should have been in the message

**The repair, and why it is not cosmetic.** As written the control walked
`TESTS.rglob("test_*.py")` — the FILESYSTEM. Its verdict therefore depended on whichever scratch
files other lanes had on disk when it ran. That is the ruff ratchet's failure one level down: a
control demanding a property of the shared working tree refuses every lane's commit whenever any
lane is mid-edit, and the lane it blocks is never the lane that broke it. `6fed05942` had just
finished paying for that exact mechanism.

Not hypothetical. Run against a `git archive HEAD` checkout with the five untracked controls copied
in beside it, it failed naming `tests/background/test_class_debt.py`, whose subject
`background/class_debt.py` was untracked — **a red manufactured entirely by which uncommitted files
sat next to it**, on a tree where it was green. The measurement method produced the finding.

The subject is now `git ls-files`, with an explicit filesystem fallback for the no-`.git`
`git archive` export the publish gate grades HEAD in — where every file present is by construction
tracked, so the two populations coincide. Without that fallback the control would have gone red at
exactly the moment it matters and become the wedge it exists to prevent.

**Mutation-proven on disk in an isolated clone**, `python3 -B` throughout, and NOT in the shared
tree — the publisher was mid-run and manufacturing a red there lands in another lane's hook chain:

| case | verdict |
|---|---|
| exported HEAD, tracked files only (the publish-gate condition) | 4 passed |
| a broken `from background.nonexistent_module_xyz import ...` file present but **UNTRACKED** | 4 passed — immune to another lane's scratch, which is the repair |
| **the same file, one `git add` later**, nothing else changed | **RED**, naming it |

It fires exactly when the offender enters the repository and not before. The population floors
(1,400 modules / 7,800 edges) already guard the fail-open direction.

## Verdicts, measured alone in their own clean HEAD checkouts

One control per checkout, because a COMBINED checkout is what manufactured the red above.

| control | at `6fed05942` | at `adf4bed6e` | why |
|---|---|---|---|
| `test_a_test_module_imports_a_name_that_exists` | **GREEN** | landed | no subject dependency |
| `test_class_debt` | RED | landed | `background/class_debt` landed with it |
| `test_svt_assignment` | RED | **RED**, 1 failure | anchor 0.2 vs expected 0.05 — still red *after* `simulation/renewals.py` landed in `adf4bed6e`, so the subject is not only renewals |
| `test_a_departure_route_carries_its_denominator` | RED | **RED**, 2 failures | `KeyError: 'svt_decisions'` — `saas/reporting/annual_report.py` still uncommitted |
| `test_settlement_ceiling_probe` | RED | **RED**, 11 failures | `tools.settlement_ceiling_probe` has no attribute `menu` at HEAD |

Every red is its SUBJECT being uncommitted, not a defect in the control. That confirms
`6fed05942` rather than correcting it: I reproduced all three of its verdicts independently.

## What `6fed05942` could not see about itself

It filed a finding about controls left uncommitted, and **its own session left two more** — this one
at 07:56 and `test_class_debt` at 08:00, either side of its 07:53 and 08:03 commits. That is not
carelessness, and it is the strongest evidence the finding is right about the mechanism rather than
about five files: the gate refuses, the prose gets written, the payload stays on disk, and nothing
reads the difference. One of the two was landable the whole time — green at HEAD, blocked by
nothing, just never staged.

## What is owed

Nothing to build. `6fed05942`'s recommendation (a) stands and is now half-discharged by ordinary
means: the two controls whose subjects landed, landed with them. The three that remain are the same
three, waiting on the same three lanes.

The one thing this adds is a caution with no mechanism attached, because a mechanism here would be a
control guarding controls: **`git add` in this tree is not a private act.** Stage immediately before
committing, or expect the next lane's commit to carry it under a message that does not describe it.
