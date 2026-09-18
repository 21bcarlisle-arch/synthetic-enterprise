**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** publish-wedge-unblock

# The wedging red was one file in no local ref, and the tree had lost eighty-eight more

**Filed:** 2026-09-18 · **Drawn as:** PUBLISH-GATE WEDGE self-refill (RUNG 1, PRIORITY ZERO)
**Found by:** asking what the named red actually *was* before repairing it. It was not a failing
assertion. It was `ModuleNotFoundError`.

---

## The drawn item asked for the wrong thing

The doorbell named one blocking test and said "FIX the red test":

    tests/background/test_a_swept_row_names_which_of_the_three_dispositions_it_was.py
      ::test_A_REDRAWN_ROW_IS_NOT_DONE_AGAIN_and_the_old_credit_does_not_settle_the_new_window

Nothing was wrong with it. Run at HEAD `95250345d` it did not fail — it did not *collect*:

    tests/background/..._dispositions_it_was.py:62: in <module>
        from tests.background.residual_voices import could_not_ask
    E   ModuleNotFoundError: No module named 'tests.background.residual_voices'

`tests/background/residual_voices.py` was **in no local ref and not on disk**. It exists on
`origin/main`, added by `1cbf684ed`. Three test files in the shared worktree already imported it.

**So the red's subject was a file the diff could not reach** — the shape that means a stale working
copy, not a bug. The discriminating measurement is the diff's direction, and it was unambiguous:
the worktree copy of the importing test was **byte-identical to `origin/main`** and 17 lines ahead
of HEAD. The worktree held origin's *tests* and HEAD's *module*.

Writing origin's bytes for that one file cleared it:

    git show origin/main:tests/background/residual_voices.py > tests/background/residual_voices.py
    → 30 passed in 21.77s   (all three importing suites)

## Why the file was missing, which is the part worth keeping

`surgical_land` never writes the shared worktree. It lands bytes to `origin`. So every landing by
a sibling lane widens the gap between origin and this tree, and the only thing that closes it is
`background.origin_reconcile`. The tree was **15 commits behind** when this turn started.

The reconciler refuses while the publish gate holds its run lock:

    GATE_RUNNING: the publish gate holds its run lock, so origin and the shared tree are left
    exactly where it found them

That is the deadlock, and it is circular: **the gate is red because the tree is behind origin, and
the reconciler that would bring the tree to origin will not run while the gate is running.** A
wedged gate runs almost continuously — four `run_complete_*` files were queued, each triggering a
full-suite run — so the reconciler's 5-minute cadence essentially never finds a window.

**A recorded conclusion has inverted, and the module still states the old one.** `origin_reconcile`'s
own docstring records a measurement over 24h to 2026-09-04: the reconciler reached a window on 129
of 165 cadences, `GATE_RUNNING` on only 36, and concludes verbatim:

> The stand-down for the gate was never the binding constraint; this was.

It is now exactly the binding constraint. `95250345d` counted **95 `GATE_RUNNING` refusals today,
104 on 09-17, 737 since 09-02**, and this turn's own live invocation was refused with it. The
docstring is not merely carrying a stale number — its *conclusion* has swapped ends, and it is the
sentence a reader would use to decide this is not worth looking at.

**The prior turn's workaround is dead.** `95250345d` describes "a racer that fires reconcile() the
instant the lock frees" and says it "lives in /var/tmp". There is no such process, and nothing in
`/var/tmp` is newer than Sep 11. It was launched from a bounded tick and died with it. A job that
must outlive its tick goes through `python3 -m background.launch_long_job`; nothing else survives.

## The second layer: the tree had lost 88 tracked files

`background/finding_classes --check` is one of the cheap pre-commit gates, and it was **FAIL (1
failure)** before this turn — refusing *every* lane's commit, naming a file nobody in this lane had
touched:

    ARCHIVE MISSING SEAT_RESULT_A_KEEP_BOTH_MERGE_DROPPED_..._2026-09-17.md:
      named by CLASS_CONTROLS_THAT_CANNOT_FAIL_2026-08-12.md, absent from docs/staging/done/

It was absent from `done/` **on disk only**. HEAD and `origin/main` both carry it there. Widening
the question: 88 tracked files were missing from the shared worktree, and `origin/main` deletes
none of them.

Restoring the ones that were genuinely damage brought the check to **PASS (0 failures)**, and the
restored `tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py` — a
control that had simply been absent — passes 9/9.

## I got this wrong first, and the correction is the finding

**I read all 88 as damage and restored all 88. That took the check from 1 failure to 79.**

86 of them were not damage. They were the **delete-half of legitimate archival moves** — a staging
document consumed and moved to `docs/staging/done/`, with the add-half already present. Restoring
the root copy recreated the document in two rooms, which `finding_classes` refuses precisely
because the rooms make mutually exclusive claims and the doorbell reads the root copy. Re-deleting
those 86 returned the tree to where the archiving lane left it.

**The discriminator, which I should have applied before writing anything:** a tracked file missing
from the worktree is damage **only if no counterpart exists in `done/` or `records/`**. With a
counterpart, the absence *is* the work. Both look identical in `git status` — ` D`, unstaged — and
the flattering reading ("the tree was vandalised") is the one that costs a lane its afternoon.

The last failure was the mirror of the same confusion: an **untracked** root copy of the Playwright
finding sat beside the `done/` copy that both refs carry. The root copy was the stale one; the
`done/` copy carries the `⚠ REFUTED 2026-09-17` banner recording that the finding's own title is
false. Dropped the root duplicate — content is a strict subset.

## What changed, and why none of it is a commit

Every restore wrote **HEAD's bytes**, so those paths now match HEAD and there is nothing to land.
`residual_voices.py` is byte-identical to origin's committed copy. The one deletion was of an
untracked file in no ref. This is a pure worktree repair against a tree that had drifted from its
own HEAD — it contests no lane and sweeps no one's work.

That also means **it is not durable**. The durable fix is the merge, and the merge is what the
deadlock above prevents.

## Pre-registration, filed before its answer

The gate run in flight when this was written (`pytest` pid 497301, parent `process_run_complete`
pid 488487) made its selection *after* `residual_voices.py` was in place, and that selection
includes the named test. **Prediction: it does not fail on that test.** If the run fails, it fails
on something else, and that is a different red than the one this turn was sent at. Recorded here
so the outcome cannot be read back as having been known.

## A third red of the same class, and a trap set for whoever reads it next

`tests/architecture/test_static_quality_ratchet.py` is red on two legs, and its own message tells
the reader to do the wrong thing:

    STALE ruff baseline entries — these codes have FEWER violations than frozen. Good news, but you
    must LOWER (or delete) their baseline counts so the ratchet holds the new floor:
    assert not {'I001': (1308, 1307)}

It is not good news, and there is no new floor. Measured the same way on both trees:

| tree | `ruff check --select I001` |
|---|---|
| clean `origin/main` extract | **1309** |
| this working tree | **1308** |

The worktree is one violation *below* origin because it is behind origin — not because anything was
cleaned. Neither file this turn touched carries I001 (both checked: clean). **Lower the baseline to
1307 and the ratchet goes green now and red the moment the tree reconciles**, naming a file the next
lane never touched. The two legs are the stale worktree reporting itself, exactly like the wedging
red they sit beside; both clear on the merge and neither wants a code change.

Left red deliberately. A control keyed to the day's answer is the failure this repo has paid for
most often, and the remedy the message recommends would install one.

## CORRECTION, same turn: the prediction above rested on a false premise

**The publish gate does not grade the working tree.** It builds a throwaway checkout of HEAD
(`/var/tmp/publish-gate-head-2tsni52o/`, and the log says so: *"the reused HEAD checkout is
DISABLED ... using a throwaway checkout for this cycle"*). Everything above about the worktree's
`ModuleNotFoundError` is true and was worth fixing, but **it was never the gate's red.** The
pre-registration is refuted, and it is refuted at the premise rather than the outcome — the worst
kind, because the measurement was sound and pointed at the wrong tree.

The gate's actual red, reproduced in a clean HEAD extract where the gate sees it, is an ordinary
assertion failure and not an import error at all:

    assert got[CREDITED_ID]["evidence"] == ""
    E  AssertionError: assert 'CANNOT ANSWE...s never asked' == ''

At HEAD, `delivery_lane` already emitted the CANNOT-ANSWER voice while this suite still asserted
`evidence == ""`. **A half-landed pair**: the module side was in, the test side was on origin. So
the prior turn's one-line conclusion — *the repair is on origin* — was right, and the only fix was
ever the merge. My worktree repair fixed a real but different red.

## The fork is closed

`origin_reconcile` cleared a window and refused with `REFUSED_CONFLICT` on exactly one path, which
the publish path itself calls *"a judgement for the seat"*. Resolved and landed as **`d1cb676ad`**
via `surgical_land --merge origin/main --resolve`; the tree went from 15 behind to **7 ahead, 0
behind**, adopting 23 paths from origin including `background/delivery_lane.py`.

**Both lanes made the same repair at different depths, and either side taken whole destroys work.**
Ours (`a5244376c`) re-keyed the three `evidence == ""` legs inline; theirs keyed them to the shared
predicate home `residual_voices.py`, which is the better design. Theirs won every executable
assertion — the test must match the module the merged tree has. But ours was not only a rewrite: it
**added** `test_THE_RESIDUAL_PARTITION_every_reachable_branch_names_what_it_asked_or_what_it_broke_on`,
which theirs does not contain, and a merge adopting one side's rewrite deletes the other's purely
additive work. It was carried over intact.

**A control preserved across a merge must be shown to still fire against the new module, or it is
cover.** Injecting mutation (k) — one constant from every branch of origin's `_nothing_answered` —
reds the carried test on its distinctness leg (`assert 1 == 3 where 1 = len({'MUTANT'})`), exactly
as its own docstring predicts. Restored: 9 passed.

Verified at the new HEAD in a clean extract: the named blocking test **passes**. One apparent new
red, `..._THE_PROSE_SPELLING_OF_A_MODULE_RESOLVES_against_the_real_repo`, is extract locality — a
`git archive` extract has no `.git` — and is green in the real repo (15 passed).

**Not yet pushed.** `origin_reconcile` was refused `GATE_RUNNING` again on the very next attempt.
The gate grades local HEAD, so the wedge should clear without the push; the push is the
reconciler's to make when a window opens, and it is the owner.

## Owed

1. **The deadlock is the standing defect, not this instance.** The reconciler cannot be starved by
   the gate whose redness it is the cure for. Either the reconcile takes a window the gate must
   yield, or the gate stops holding its lock across a full suite. Filed as direction, not built
   here — it is a change to the publish path's locking and wants its own turn and its own control.
2. **`origin_reconcile`'s docstring states an inverted conclusion** and should be corrected beside
   the claim, with both measurements kept.
3. **86 archival delete-halves are sitting unlanded in the worktree.** They are correct, but until
   they land, every lane re-derives whether they are damage. This turn spent a round trip on it.
