**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** none — Lane 0
delivery, incidental to "swept-row-join-covers-15-of-81-rows-because-the-stamp-is-new"

**Class:** publish_gate_and_wedge

# A staging document landed in the root alone wedged origin/main, and only a worktree AT origin could unwedge it

Autonomous worker, scheduled tick, 2026-09-16. Found while trying to merge `origin/main` into the
shared tree before starting the drawn Lane 0 work. Repaired in the same commit that carries that
work, because the gate would not pass either of them alone.

**Landed:** the move of
`docs/staging/SEAT_PREREG_THE_WEATHER_CELL_RE_CUT_AND_WHAT_IT_DOES_TO_THE_ACCEPT_BRANCH_2026-09-16.md`
out of the staging root and into `docs/staging/records/`.

---

## What was wrong

`origin/main` tracked that document in the staging **root** with no copy in its room. That is
exactly the state `tests/background/test_staging_rooms.py::test_no_LIVE_reference_or_console
_document_exists_ONLY_in_the_root` refuses, and it was **red at `origin/main` itself** — proven in a
clean `git archive origin/main` extract, not inferred from the shared tree, where a sibling lane had
already written an uncommitted room copy that made the working tree look fine.

It did not wedge every commit, which is why it survived: the pre-commit test gate selects tests for
the files a commit touches, so a commit that touches nothing under `docs/staging/**` never asks the
question. **A merge touches everything.** Two `surgical_land --merge origin/main` attempts were
refused by it, three minutes each.

## Why the obvious repair does not work

Measured on three trees, one variable apart:

| tree | `test_no_LIVE...root` | `finding_classes --check` |
|---|---|---|
| `origin/main` as it stood | **red** (stranded in the root) | green |
| `origin/main` + the room copy | green | **red** (TWO ROOMS) |
| `origin/main` + the room copy − the root copy | green | green |

So the two controls demand opposite things of any tree that holds both copies, and the only state
satisfying both is the **move**. `staging_two_rooms_repair` implements exactly that: it `git rm`s
the redundant root copy.

## Why no diverged branch could perform it

A move is an add plus a **delete**, and a branch can only delete a path it tracks. The shared
tree's `main` was five commits behind and three ahead; its merge-base did not carry the root copy,
so neither did it. In a three-way merge — base lacks the file, ours lacks it, theirs adds it — the
file is added. **Every merge of `origin/main` into that branch reproduces the wedge**, and landing
the room copy first only moves the refusal from one control to the other. There is no ordering of
commits on a diverged branch that reaches the green state.

The repair therefore has to be authored on a checkout that already tracks the root copy: a worktree
**at `origin/main`**, landed there with `tools/surgical_land`, and pushed with
`tools/promote_worktree_landing`. That is what happened here.

## The class

This is the publish-wedge class one rung up: not a red test, but **a red test whose two escape
routes are individually refused by a second control**, so the tree has no legal single-commit path
out of it. The tell is a refusal that survives the obvious fix and is replaced by a *different*
refusal naming the same file. When that happens, stop trying orderings and ask which checkout can
express the deletion.
