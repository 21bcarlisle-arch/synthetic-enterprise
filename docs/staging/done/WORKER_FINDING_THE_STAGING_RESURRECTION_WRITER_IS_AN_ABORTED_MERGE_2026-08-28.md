**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `unminted`

# The staging-root resurrection writer, named: an aborted `git merge` leaves its partial checkout behind

Three findings have filed this condition without a cause —
`WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_THE_SHARED_TREE_2026-08-10`,
`..._RESURRECTED_TWICE_DURING_A_LIVE_SURGICAL_LAND_2026-08-18`,
`..._ARCHIVED_RUN_MARKERS_RETURN_TO_THE_STAGING_ROOT_AND_BLOCK_EVERY_COMMIT_2026-08-20` — and
`background/staging_root_resurrection_watch.py` was built as an instrument precisely because
*"reading is what produced the two wrong answers."* This is an occurrence with its window
bracketed, so it is filed as evidence rather than as a fourth theory.

## What was observed

`observed-with-evidence`.

- **08:00 (approx.)** `git merge origin/main` was run against a tree where `docs/status/LATEST.md`
  was modified. `origin/main` was then `621a5ee09`, whose tree holds the six `CLASS_*.md`
  registers and the `DIRECTOR_CONSOLE_*.md` transcripts **in `docs/staging/` root** — the
  pre-move layout. The merge **aborted**: *"error: Your local changes to the following files
  would be overwritten by merge: docs/status/LATEST.md. Merge with strategy ort failed."*
- **After the abort**, all six CLASS registers and both console transcripts were present in
  `docs/staging/` root, **untracked** (`??` in `git status`), byte-identical to the copies in
  `docs/staging/reference/` and `docs/staging/console/`.
- **`stat` mtime on all eight: `07:58:29`** — one second, all eight files, inside the aborted
  merge's window.
- `HEAD` at the time already had them only in their rooms (`git ls-tree HEAD docs/staging/` →
  0 matches; `docs/staging/reference/` → 6). So no checkout of HEAD could have produced them,
  and no committed state contained them at that path.

## What is inferred, and how to settle it

`inferred`: that the aborted merge's own partial checkout wrote them. The eight files are
exactly the set that differs between the two trees at that path, the mtimes fall inside the
abort window to the second, and no other writer was active on those paths.

**It is not proven and it is cheap to prove.** The reproduction is synthetic and needs no live
tree: in a scratch repo, commit file A at path P, move it to P2 on a branch, dirty an unrelated
tracked file, then merge the branch that still has it at P — and assert whether P exists
afterwards. `background/staging_root_resurrection_watch.py` is the right home for the assertion
because it already owns the question; this needs its bracket, not a new instrument.

## Why it matters more than it looks

**It explains the shape all three prior findings describe and none could attribute**: files
reappear "on the shared tree", "during a live surgical land", "and block every commit". Every one
of those is a moment when git materialises one tree over another while the working tree is dirty
— which on this repo is nearly always, because daemons rewrite `docs/observability/` and
`site/data/` continuously.

**And it is self-inflicted by the concurrency, not by any module.** Nobody wrote a resurrection
bug. The tree has several writers, one of them merges, and a merge that cannot complete does not
always undo what it has already written.

## What to do about it, and what NOT to

**Do not** add a sweeper that deletes anything in the staging root matching an archived name.
That is the "timid repairer" `staging_two_rooms_repair` already argues for, and widening it to
delete on a name match would let one aborted operation eat a genuinely new document.

**Do**: make an aborted merge leave no residue, by refusing to start one on a dirty tree in the
first place. The tree is *always* dirty here, so the honest form is a wrapper that stashes the
generated-path churn (`tree_divergence.GENERATED_PREFIXES` already enumerates it), merges, and
restores — the same list `seat_continuity._uncommitted_paths` already delegates to. One list, two
consumers, no second opinion.

**Interim, and it is what was done here**: the eight files were verified byte-identical against
their rooms and removed. That is safe only because the identity was checked; a resurrection whose
content DIFFERS is a different condition and must be reported, not swept.

## WORK THIS CREATES

1. The synthetic reproduction, asserted in
   `tests/background/test_staging_root_resurrection_watch.py`, so the cause is proven or the
   theory is killed.
2. If proven: a merge wrapper that parks generated-path churn, so an abort has nothing to leave
   behind.
3. The three prior findings annotated with this cause once (1) settles it — they are the
   evidence that this is a class and not an incident.

## Still live
