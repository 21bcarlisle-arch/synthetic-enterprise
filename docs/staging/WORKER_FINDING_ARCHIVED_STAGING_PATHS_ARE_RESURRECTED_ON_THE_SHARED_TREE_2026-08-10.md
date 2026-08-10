# [WORKER-FINDING] Archived staging paths get resurrected on the shared tree, so a drain reads as undone

**Found:** 2026-08-10, during the backlog-triage drain (Groups A/B of
`DIRECTOR_PRIORITY_BACKLOG_TRIAGE_AND_INTERLEAVE_2026-08-10`).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight — **the mechanism is not
identified** and the machine is not blocked: the commit landed intact and the tree is not reverted.
**Rank:** promote the moment a second drain tick loses work to it, because it makes a *completed*
disposition read as *unprocessed* on the next doorbell.

## Observed, with evidence

Twice in one tick, every staging path I had `git mv`'d out of `docs/staging/` reappeared on disk at
its OLD path, byte-identical to the version in the then-current HEAD, while the rename stayed
correctly staged in the index.

```
event 1  ~15:25    15 files back in docs/staging/, mtime 15:25, identical to HEAD ad3c247f8
event 2   15:33:13 the same 15 files back again, all within the same second
```

`observed-with-evidence` for both events: the first was caught by `git status` showing each file as
BOTH a staged rename (`R docs/staging/X -> docs/design/refs/X`) and an untracked `?? docs/staging/X`;
`git show HEAD:docs/staging/X | diff -q - docs/staging/X` reported identical for all 15, 0 mismatches.
The second was caught by re-counting the root after the commit: 64 expected, 79 present, and
`ls --time-style` put all 15 at exactly `15:33:13`.

**The tree was NOT reverted, and this is the important negative result.** After event 2:
`git status --porcelain | grep -E "^ D|^D "` = **0 deletions**; `docs/design/refs/` and
`docs/domain_artefact_library/scope_briefs/` both intact; HEAD still my commit `314f16912`. So this
resurrects *copies*; it does not roll the working tree back to an older commit. Event 2 happened
AFTER those paths had already left HEAD, which rules out a plain `git checkout -- .` against
current HEAD.

A publisher (`process_run_complete.py` pid 2836157, started 15:26 on
`run_complete_20260810T141805Z.md`) was live across both events, at 94.9% CPU running the gate.

## Why it matters more than a stray file

The drain's whole unit of work is *a file leaving `docs/staging/`*. The supervisor's doorbell scans
that directory, so a resurrected copy re-lists a dispositioned document as "unprocessed staging" on
the next tick — the same shape as the `in_progress/` doorbell that re-granted a turn every ~2
minutes. Left alone, the triage page's `<20` exit condition can never be reached: each tick
archives files that are back before the next tick reads the directory. A worker that trusted the
count instead of re-measuring would report a drain it did not achieve.

I removed the duplicates both times (each verified byte-identical to the committed copy at its new
canon path first, 15/15 and then 15/15 again — never a blind `rm`), which is why the root reads 64.

## The second-order defect, which is the one that actually cost work

**A pathspec commit silently downgrades a staged rename to an add if the old path comes back
before the gate finishes.** `git commit -- <paths>` resolves its pathspecs against the WORKING
TREE, not the index. My `git mv`s were correctly staged as renames; the pre-commit gate then ran
for a minute or two; the resurrection fired at 15:33:13 *inside* that window; and by the time git
resolved the pathspecs the old paths existed again. `314f16912` therefore recorded 15 `A` entries
at the new canon paths and **no deletions at the old ones** — every Group A doc tracked in two
places at once, with the commit reporting success.

`observed-with-evidence`: `git show --name-status 314f16912 -- <old> <new>` shows `A` for the new
path and no entry at all for the old one, while `git ls-tree -r origin/main` listed both copies.

The cure used, and the one to reach for again: **`python3 -m tools.surgical_land`**. It builds a
throwaway index from HEAD and gates the tree the commit WOULD create, so it does not re-read a
working tree a concurrent writer is editing. Landed as `d32277e3a`, receipt verified (tree
`47cc1bb5b`, 15 paths, gate-rc 0). This is a second, independent reason the surgical-landing tool
exists beyond the dirty-index merge case its ruling describes.

**Generalisation worth keeping: on this shared tree, a pathspec commit is not safe for a rename or
any deletion.** It is fine for content edits, where a racing writer can only cost you a stale
blob; for a path that must *stop existing*, use `surgical_land`.

## What I did NOT establish

- **Which process writes them.** `grep` over `background/` and `tools/` for
  `checkout` / `restore` / `read-tree` finds only `tools/surgical_land.py` (throwaway index) and
  `process_run_complete.py`'s two calls — and both of the latter run with `cwd` set to a *checkout
  dir*, not `PROJECT_DIR` (`_refresh_checkout_to`, line ~1189; the gate's `read-tree`, line ~1322).
  Neither should touch the real tree. `inferred`, not observed: something in the publish path
  copies or extracts into `PROJECT_DIR`, or a writer outside these two files does.
- **Whether it is periodic or event-driven.** Two events ~8 minutes apart is not a period.
- **Whether non-staging paths are affected.** I only checked paths I had moved.

## The smallest closed-loop test (R4), for whoever draws this

`git mv` one throwaway file out of `docs/staging/`, leave the rename staged, and poll the old path
once a second with the publisher running. That names the interval, and `fuser`/`inotifywait` on
`docs/staging/` during the window names the writer. Do that before proposing any fix — the two
plausible cures (a copy that should be a move; an extract whose destination is wrong) have
different blast radii, and one of them is on the publish path, which is not somewhere to guess.

## Related

- The `in_progress/` re-surfacing doorbell (CLAUDE.md): deliberate there, accidental here.
- `feedback_autoprocessor_sweeps_inflight_site_edits` — same family: a concurrent writer on one
  working tree interacting with another lane's staged-but-uncommitted state.
