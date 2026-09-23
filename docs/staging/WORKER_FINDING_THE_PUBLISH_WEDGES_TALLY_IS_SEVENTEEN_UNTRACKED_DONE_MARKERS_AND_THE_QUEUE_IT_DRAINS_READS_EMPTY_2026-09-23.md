# The publish wedge's tally is seventeen untracked done/ markers, and the queue it drains reads empty

**Severity:** RECORDED · **Lane:** H_harness

`last_clean_publish` has stood at 2026-09-21T18:15:57Z for 50 hours. The blocking refusal is landed
and on origin as of `caabe0165`. This note records **how to tell whether it cleared**, because the
obvious instrument says the pipeline is idle when it is in fact wedged.

## The queue this pipeline exists to drain reads ZERO, and that is not "drained"

`pending_run_complete_markers()` returns **0**. Read at face value that is a healthy, empty queue —
and it is the evidence `record_publish_gate_success` requires to close an episode:

> The evidence is `pending_run_complete_markers()`: the queue this pipeline exists to drain, read
> off the real staging directory and therefore INDEPENDENT of the gate's own state (R15
> anti-tautology — a gate-state file that lies cannot make the backlog look drained).

But the runs are completing normally, every ~2.3 hours, most recently 2026-09-23 21:19 BST. They are
**not** absent; they have been moved out of the queue and into `docs/staging/done/` — and then never
committed. `git status` carries **17 untracked `run_complete_*.md` files in `done/`**, unbroken from
`run_complete_20260922T090924Z.md` to `run_complete_20260923T195318Z.md`.

**The move happens, the commit fails, and the marker is what is left behind.** The publisher drains
the queue before it commits, so a wedge caused by the commit leaves the queue looking empty. The
anti-tautology evidence is real — the state file cannot fake it — but the population it counts is
emptied by a step that precedes the one that fails, so **zero-pending is consistent with both a clean
pipeline and a fully wedged one**, and nothing beside it distinguishes them.

The distinguishing instrument is the untracked count in `done/`. The publisher's own source already
knows this shape — *"`run_complete_*.md` moved to done/ and never committed sits untracked forever,
observed"* — but nothing reads it as the wedge's depth gauge.

## What this makes the exit test

`wedge_since` is 2026-09-21T20:40:07Z; the oldest untracked marker is 2026-09-22T09:09Z. 17 markers
is the number of publish cycles that have run and failed to land since, which is the honest tally of
the outage — not `episode_failures: 38`, which counts attempts rather than lost runs.

**So the check that the wedge cleared is not only `last_clean_publish` moving. It is the untracked
count in `docs/staging/done/` going to zero**, and the two should move together. If
`last_clean_publish` advances while 17 markers stay untracked, the publish that stamped it did not
commit what it drained.

## Why the state file's two refusal fields both mislead here

Both were checked rather than believed, and both are stale:

- `blocking_tests: ['FAILED tests/design/test_atom_notes_store.py::test_declarations_match_the_store']`
  — **run just now: 1 passed.** Long dead, and it is the field a reader meets first.
- `fork_state: 'diverged'`, reason *"2 behind, 0 ahead"* — the tree is `0 ahead, 0 behind` origin/main
  now.
- `liveness_surface_refusal: None`, while `liveness_surface_last_publish.cleared_refusal` carries the
  cause that was actually live: a `gate_refusal` whose evidence tail names
  `site/test_the_flat_churn_belief_reaches_the_reader.py` — the three reds `caabe0165` fixed.

The state was last written 22:24 BST, before that landing, so every field in it predates the repair.
**The only field that named the live cause was nested inside a record whose key says the refusal was
cleared.**

## What is established and what is not

Established: the three reds are green, they are committed, they are on origin, and the whole `site/`
tree is 925 passed / 38 skipped at the landed tree. The publisher commits by pathspec
(`git commit -m msg -- <paths>`, not `-A`), so the shared worktree's ratchet red — 5 F401, **all five
in one uncommitted file, `tools/refresh_to_head.py`**, another lane's live work — is not in its
commit tree and does not block it.

Not established: that the next cycle clears. No marker is pending, so no publish can be driven
without minting a run-complete marker for a run that did not happen, which would be manufacturing the
evidence the episode-close rule exists to require. The next natural cycle is due ~22:40 UTC.
