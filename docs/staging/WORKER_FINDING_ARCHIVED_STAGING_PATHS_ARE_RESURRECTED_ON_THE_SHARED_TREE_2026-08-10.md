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
