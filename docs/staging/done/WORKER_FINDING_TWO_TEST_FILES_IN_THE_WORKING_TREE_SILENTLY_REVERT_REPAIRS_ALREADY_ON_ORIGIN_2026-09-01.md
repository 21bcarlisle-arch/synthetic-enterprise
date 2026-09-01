**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS1_process_manifest_reconstruction`

# Two test files in the working tree silently revert repairs already on origin, and one of them re-points a control at the live artefact

**Found:** 2026-09-01, working the LANE 0 delivery item *the-publish-loop-is-rejecting-its-own-push-and-widening-the-fork-it-rejects-over*.
Not by a control — by attributing a pathspec before committing it.

## What was found

The direction named `background/fork_salvage.py` and `background/fork_reconciler.py` as confirmed
superseded drafts and told me to take the upstream copy. Both are in fact now **byte-identical to
`origin/main`** — `git diff origin/main -- <path>` is empty for each, so there is nothing to take.
They still read ` M` in `git status` only because they differ from *local* `HEAD`.

But two files in the same sweep are superseded drafts that nobody has named, and they are **test**
files, not modules:

| path | worktree vs `origin/main` | what the worktree copy undoes |
|---|---|---|
| `tests/background/test_tree_divergence.py` | −14 lines | the `tmp_path` repair of 2026-08-31 (`16fe54aa4`) |
| `tests/background/test_fork_salvage.py` | −40 lines | `test_ANY_writer_can_declare_its_worktree_in_use_not_just_the_executor` (`7a995e2b1`) |

Both are **unstaged working-tree modifications that delete work already on the trunk**. Neither is a
draft of something newer; each is an older copy of a file the trunk has since improved.

## Why it matters, and it is not symmetric

`test_fork_salvage.py`'s worktree copy drops the control proving the live-writer exemption is keyed
to *any* writer rather than to one module's path — the control that exists because this daemon
committed `SALVAGE(auto)` into the delivery seat's own worktree on 2026-08-31. That is a deletion of
evidence, and it is the subject of the live BLOCKING finding in this same lane.

`test_tree_divergence.py`'s worktree copy is worse than a deletion, because it is **active**:

```python
out = td.write_artifact(m, td.PROJECT_DIR / "docs" / "observability" / "tree_divergence.json")
```

That is the pre-repair line. Every run of the suite *from the working tree* overwrites the **live**
`docs/observability/tree_divergence.json` with a measurement taken over whatever the test tree
happened to look like. `docs/observability` became a protected surface on 2026-08-31 precisely
because 6,421 lines of one ledger turned out to be pytest output and a reader of it reported a usage
limit that never existed. The repair is on origin; the working tree is running the defect.

The live artefact is currently **sane** — it reads `base: {ahead: 1, behind: 0}` with real lane
attribution, which is a real publish cycle's measurement, because the publish gate runs its suite in
a throwaway `git archive` checkout of HEAD (`/var/tmp/publish-gate-head-*`) and not in this tree. So
the hazard is **latent, not realised**: it fires the moment any lane runs that test file from the
shared worktree. That is a thing lanes do routinely.

## What I did NOT do, and why

I did not restore either file. `git checkout <path>` is a wall in CLAUDE.md — it destroys unstaged
work with no reflog — and writing the upstream bytes over the top by hand is the same act wearing
different clothes. I do not know which lane holds these, or whether one is mid-edit. What I could do
without deciding for anybody is keep them **out of my pathspec**, which I did: the divergence leg
landed `background/process_run_complete.py`, `background/publish_cause.py` and four test files by
exact name, so neither reversion was swept onto the trunk under my commit's claim.

## The general shape, which is the part worth keeping

**A ` M` in `git status` is a direction-free fact.** It says the worktree differs from local `HEAD`;
it does not say which side is newer, and on a tree whose `HEAD` has been up to twenty commits behind
`origin/main` this week, "modified" and "stale" are indistinguishable without asking. The existing
memory *a modified file can be a superseded draft of work already landed on origin* covers modules.
This is the same class reaching **controls**, where the cost is different in kind: a superseded
module is a bug, a superseded control is the **silent removal of the thing that would have caught
the bug**, and it removes it without ever going red.

`docs/observability/tree_divergence.json` already measures per-lane worktree drift — 236 source
files, oldest 94.93h. It counts files that differ from `HEAD`. It does **not** ask, for any of them,
whether `origin/main` already holds something newer. That is one comparison against a ref the module
already fetches, and it would have named both of these without a human reading a diff.

## What would settle it

For each drifted path, `git diff origin/main -- <path>`: empty means already-landed residue (drop
it), non-empty in the *deleting* direction against a commit that is an ancestor of `origin/main`
means a **reversion**, and only the remainder is genuine in-flight work. I ran this by hand over the
whole `git status` set to attribute my own pathspec; it took one loop and found two files that four
orientations of prose had not.

**Not proposed here:** a watcher, a register, or a dashboard panel. Two files of evidence justify at
most one comparison added to a measurement that already runs.
