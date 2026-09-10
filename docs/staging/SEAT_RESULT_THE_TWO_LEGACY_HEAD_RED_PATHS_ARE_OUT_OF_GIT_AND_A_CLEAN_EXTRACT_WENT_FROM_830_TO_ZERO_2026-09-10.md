**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `remove-the-two-legacy-head-red-tracked-files-with-the-shared-tree-two-step`) · **Class:** controls_that_cannot_fail

# RESULT — the two legacy head-red paths are out of git, and a clean extract went from 830 to zero

The two-step that `bb5f2603e` measured and deliberately deferred is done. Landed as `dcdfd5ebd`
(step 1, land the live bytes) and `e4aa02359` (step 2, leave the index).

## The premise was live, not spent — and the doorbell's own check said the opposite

The doorbell's premise check reported that the cited commit `2e3e4d74a` is "ALREADY an ancestor of
`origin/main`", which reads as *the work has landed by another route*. It has not. `2e3e4d74a` is
an ancestor of `origin/main` and **not of `HEAD`** — the shared tree was 6 commits behind, and the
cited commit sat inside exactly that gap. Both target paths were still present at `origin/main`
when this turn started, so step 2 had never been done anywhere.

`rev-list --count HEAD..origin/main` before believing "already an ancestor". Ancestry is asserted
about `origin/main`; the tree you are standing in can be behind it.

## What was measured, both sides, before and after

`drawable()` run against a `git archive` extract (what any fresh checkout, isolated worktree or
clean HEAD extract reads) and against the shared tree:

| | clean extract | shared tree |
|---|---|---|
| before (`8dd060194`) | **830** red, 1 run | 43 red, 10 runs |
| after (`e4aa02359`) | **0** red, 0 runs | 43 red, 10 runs |

The clean extract's 830 was the 2026-09-02 ENOSPC/tmpfs wreck — `passed: null`, `OSError x760`, a
row `record()` would now refuse for having no pass count. The shared tree is **unchanged**, which
is the half that had to not move: its ten runs of ages are what `load_observed` adopts through
`LEGACY_OBSERVED_PATH`, and abandoning them would reset every `runs_red` to 1.

Zero is the correct reading, not a new false one: a missing store is EMPTY, and the module's
documented fail direction is toward reporting MORE work, never less. It can never read as "nothing
is red". The old false 830 could and did.

## Why two commits, and why `--content-remove` rather than `git rm --cached`

A commit that deletes a path whose worktree copy is dirty **does not delete it** — `git pull`
aborts with "your local changes would be overwritten" and the tree stays behind origin. Both paths
were dirty (1498/837 and 69/30 lines against HEAD). So step 1 landed the working-tree bytes to make
both copies clean everywhere, and only then did step 2 remove them from the index.

`--content-remove` (with `--drops`, so the deliberate deletion is printed rather than exempted
silently) leaves the files **on disk** in the shared tree. That is what keeps the shared tree's
ages alive while a checkout inherits nothing.

## The drawn item stated one thing that is false, and it changes the remaining work

> "Nothing reads them for the draw any more ... **and nothing writes them**"

True of the observation store. **False of the register.** At `origin/main`,
`background/head_red_register.write_register()` still resolves `path or REGISTER_PATH`, and
`REGISTER_PATH` is `docs/staging/reference/HEAD_RED_REGISTER.md` — the path just untracked. The
census rewrites it on every HEAD-green run.

So the register is now written, untracked, and **not gitignored**: it will show as an untracked
file forever and any careless `git add -A` re-tracks it, restoring exactly the defect this landing
removed. The observation store's own control
(`test_the_live_observation_store_is_untracked_and_ignored`) already sets the standard —
*"must be gitignored, not merely absent from the index"* — and the register now fails that
standard while having no control of its own.

**This is the open half and it is deliberately not done here.** `.gitignore` gained 21 lines in
`bb5f2603e`; the shared tree's copy predates them. Editing it from a base 6 commits behind would
land a `.gitignore` that is not a superset of origin's, and risk the merge conflict this whole item
exists to avoid. It is a two-line edit once the tree reaches origin.

## Second open thread: the shared tree cannot fast-forward

`git merge --ff-only origin/main` aborts. Three files are held divergent by another lane
(`background/head_red_register.py`, `background/supervisor.py`, and one staging finding), and a
fourth exists untracked where origin has it tracked. Not this item's work and not clobbered —
recorded because the `.gitignore` half above is blocked behind it.

Note the shape of the collision: the shared tree's `background/head_red_register.py` is the
**pre-move** version (`OBSERVED_PATH` still pointing at the tracked path, no `LEGACY_OBSERVED_PATH`).
Landing that working copy by pathspec would revert `bb5f2603e`'s store move. It is safe only
because nobody committed it.

## Why the landing is safe in either merge order

At this HEAD the module still points `OBSERVED_PATH` at the now-absent tracked path, so a clean
extract reads an empty store. After the merge with origin it points at `.head_red_observed.json`
with the legacy path as a credible-only fallback, so a clean checkout still reads empty. Both
orders give UNOBSERVED in a checkout and 43 in the shared tree; neither gives a false number.

The control that anticipated this landing already handles it:
`test_the_draw_no_longer_reads_the_tracked_bytes_at_all` **skips** when the legacy path is gone
("this test's subject is gone, which is the goal"), and
`test_nothing_writes_the_legacy_tracked_path_any_more` asserts only that the writers do not
*reference* the legacy path — not that it is tracked. Its docstring names this exact follow-through:
*"the exit is a later two-step on the shared tree, not a delete here."*

## What is next

1. Add both legacy paths to `.gitignore`, once the tree is at origin. Without it the register
   churns untracked and is one `git add -A` away from coming back.
2. Give the register the control the observation store has: untracked **and** ignored. It is
   machine state by the same three properties the module already names.
