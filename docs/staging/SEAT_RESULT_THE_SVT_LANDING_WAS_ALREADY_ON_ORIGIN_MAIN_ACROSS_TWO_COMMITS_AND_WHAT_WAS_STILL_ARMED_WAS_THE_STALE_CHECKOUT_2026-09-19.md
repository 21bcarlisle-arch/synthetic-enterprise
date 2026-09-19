**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** the SVT origin household's exit

# The SVT landing was already on origin/main across two commits, and what was still armed was the stale checkout

**Filed:** 2026-09-19 · **Claim id:**
`verify-and-bind-the-svt-landing-that-was-in-flight-at-0023`
**Class:** `uncommitted_and_orphaned_work` — a stale working copy running backwards over a landed
repair.
**Direction, not an atom.** No exit test was written for it; DONE is this finding plus the
working-tree repair it records.

---

## 0. The answer, before the detail

**The premise was spent, and the item's own draw-time check said so.** Every one of the six paths
the item named is landed on `origin/main` and clean in the shared tree. Nothing was left to land.
The lane already knows it: `--premise-spent` was refused with *"already holds a landing at or after
its last draw — it DELIVERED, and premise-spent is the weaker fact"*.

**What was still live is the one path §9 of the result document could only decline to touch.**
`tests/simulation/test_the_tariff_type_read_has_one_home.py` sat in the shared tree as an eleven-day-old
stale checkout whose diff ran backwards over `dcb8c6d10`, and it was **red**. It is now repaired and
green. That is the whole delivery of this turn.

---

## 1. The premise, re-measured before any work started

The item was drawn to land six paths. It carried its own warning that `dcb8c6d10` was already an
ancestor of `origin/main`. Re-measured at 2026-09-19 01:55 BST:

| path | landed in | on origin/main |
|---|---|---|
| `simulation/renewals.py` | `05684780e` (01:21 BST) | yes |
| `simulation/run_phase2b.py` | `05684780e` | yes |
| `tests/simulation/test_svt_product.py` | `05684780e` | yes |
| `tests/simulation/test_the_svt_origin_household_can_reach_a_fixed_term.py` | `05684780e` | yes |
| `tools/published_route_split.py` | `b721b6acf` (00:34 BST) | yes |
| `docs/staging/records/WORKER_RESULT_…_WAS_ABSORBED_2026-09-18.md` | `b721b6acf` | yes |

`git status --porcelain` is empty on all six. `pgrep -af tools.surgical_land` finds no live
landing — the only match is a worktree session whose *prompt text* contains the string, which is
the false positive the item's own instruction warned about from the other direction.

**The six paths landed as TWO commits, not one**, 47 minutes apart, and the result document travelled
with the tooling half rather than the simulation half. An item that had checked only `05684780e`
would have concluded two of its six paths were unlanded and gone looking for work that was already
in a ref.

**Both SVT suites are green at HEAD in the shared tree:** 18 passed
(`test_svt_product.py`, `test_the_svt_origin_household_can_reach_a_fixed_term.py`, and the four
sibling SVT/gas-leg suites).

## 2. The binding could not be taken, and each refusal named the right reason

Three dispositions were tried in order, and all three refused — correctly:

```
--landed the-svt-household-has-no-route-back-to-a-fixed-term --commit 05684780e
  → bound NOTHING: it is NOT CLAIMED … the claim was swept
--landed verify-and-bind-…-at-0023 --commit 05684780e
  → bound NOTHING: 05684780e is OLDER than this id was FIRST drawn
    (1789777268 <= 1789779273) … an older commit here is genuinely somebody else's work
--premise-spent the-svt-household-has-no-route-back-to-a-fixed-term 05684780e …
  → recorded NOTHING: it already holds a landing at or after its last draw -- it DELIVERED
```

**The lane's books were already right.** The original id is credited with its landing; this turn's
id cannot borrow a commit that predates its own draw; and the third disposition is unavailable
precisely because the first fact is true. *Nothing is owed and nothing needed writing* — the item's
`IF IT LANDED: bind it` clause was an un-re-asked prediction about a claim that had since been
swept, and the refusals are what establish that, not a guess.

**This is the shape to expect, not a defect in the lane.** A drawn item that says "bind it" assumes
its own claim still lives. A swept claim plus a landing newer than the *original* draw but older
than the *successor* draw is a state in which no binding verb applies, and the honest output is a
finding rather than a forced write.

## 3. What was actually still armed

§9 of `WORKER_RESULT_…_WAS_ABSORBED_2026-09-18.md` did the ownership work at landing time and got it
right: `tests/simulation/test_the_tariff_type_read_has_one_home.py` **is not that change** and must
not be landed with it, because its working copy runs backwards over `dcb8c6d10` and would have
re-armed the 158 unlabelled gas terms that repair closed. The landing turn could decline to commit
it. It could not repair it, and did not.

**So it stayed red.** Measured this turn:

```
FAILED tests/simulation/test_the_tariff_type_read_has_one_home.py::
       test_the_two_commodities_are_read_differently_and_that_is_the_finding
AssertionError: assert 'fixed' is None
```

That control is the *pre-repair* one, deleted by the gas-fidelity determination and asserting the
defect the determination closed. Its own docstring said it would go red and be deleted when the
world got better. It did, it was — in HEAD — and the shared worktree was still running the corpse.

**Established purely stale, with zero holder hunks, before touching it.** The decisive test is not
the mtime and not the diff's direction — it is blob identity:

```
worktree blob  6e18fc92697b3a08fd8dbbc98bcb5b57056ff47c
             == 40fe58f85:tests/simulation/test_the_tariff_type_read_has_one_home.py
                (2026-09-07 12:14, an ancestor of HEAD)
HEAD blob      f267d41666c85e07bf87ba918fcf7b005bca26e9
```

**A working copy byte-identical to an ancestor commit contains no lane's uncommitted work**, by
construction. That is what licenses writing over it, and it is a stronger warrant than "the mtime is
old" — an old mtime is consistent with a lane having edited it once and left. Blob identity is not.

**The repair:** `git cat-file blob HEAD:<path> > <path>`, with the displaced bytes copied to
`~/.cache/stale_tariff_type_read_09-07_backup.py` first and permanently recoverable from
`40fe58f85` regardless. Never `git checkout <path>`, which would have been free to sweep whatever
else it found.

**After:** `6 passed in 4.18s`, and `git status --porcelain` on the path is empty — the shared tree
now matches HEAD there.

## 4. What this costs the reader, and what it does not

**The repair leaves no commit**, because its result is *the absence of a diff*. There is no hunk to
land; the tree simply stopped disagreeing with its own HEAD. A reader looking for this turn's work
in `git log` will find only this document, and that is correct rather than a shortfall — but it is
also why the finding has to exist: a working-tree repair that files nothing is indistinguishable
from a turn that did nothing, and re-derivable by nobody.

**One red in this family is NOT this, and was not touched.**
`SEAT_FINDING_THE_UNLABELLED_TARIFF_BRANCH_IS_DEAD_AND_THREE_CONTROLS_PINNED_TO_IT_HAVE_REDDENED_HEAD_2026-09-18.md`
names three controls in `tests/tools/test_the_renewal_funnel.py`. Those are pinned to the same dead
`None` branch, but they are a different file, a different lane's subject, and — unlike this one —
**not** a stale checkout: they are red in HEAD's own bytes. Repairing this path does not discharge
that finding, and anyone reading "the tariff-type reds are cleared" off this document would be
wrong. *One repair does not fix the other; they are the same class at opposite ends.*

## 5. The prediction this turn is willing to be refuted on

The stale checkout has stood since 2026-09-07 — untouched for eleven days, through at least one
landing turn that saw it, named it, and correctly declined to commit it. **If it returns, the cause
is a re-checkout of `40fe58f85`-era bytes by some lane's recovery path, not a lane editing this
file** — because nothing has edited it in eleven days. The falsifier is cheap: if it reappears with
a *different* blob, this paragraph is wrong and someone is genuinely working there.
