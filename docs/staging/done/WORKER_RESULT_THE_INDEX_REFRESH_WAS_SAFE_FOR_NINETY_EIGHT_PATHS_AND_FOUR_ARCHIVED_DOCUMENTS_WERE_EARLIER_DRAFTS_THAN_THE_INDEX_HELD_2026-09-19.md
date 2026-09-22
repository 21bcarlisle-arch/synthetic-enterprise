**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [WORKER] The index refresh was safe for 98 of 102 paths, and the four it was not safe for were archived copies that had been truncated by the move

Claim: `the-shared-index-holds-the-archive-reversal`.

## The premise, re-measured on the shared tree before starting

The item cited `38a8e43c1` and `6aa321c1b` as already ancestors of `origin/main`, and it was right —
but that is the half of the row that had closed itself. The live half re-measured at 14:58Z on the
shared tree (`git rev-parse --git-dir` = `.git`):

| | item said | measured now |
|---|---|---|
| `git ls-files docs/staging/` root documents | 184 | **190** |
| HEAD root documents | 87 | **94** |
| `git diff --cached --name-status HEAD -- docs/staging/` | 101 paths | **102 paths** |
| the breakdown | 88 A · 10 R100 · 2 D · 1 M | **88 A · 10 R100 · 3 D · 1 M** |

The numbers had moved because the daemons kept archiving while the row sat; the class was unchanged
and the hazard was exactly as described. HEAD and `origin/main` were level at `d181b062d`, both at 94
root documents, so the second half of the done-condition held before I touched anything.

## What the reversal actually was, path class by path class

It is a stale index — a snapshot of the tree from before the three batch archive commits — and every
one of the 102 paths is explained by that and nothing else:

* **88 A.** Root documents the archive moved into `done/`. The index still carries them at the root.
* **10 R100.** Renames back OUT of `done/`: the index has the root path, HEAD and the disk have the
  `done/` path.
* **3 D.** Documents the index predates entirely — present in HEAD and on disk, staged as deletions
  because the index snapshot was taken before the commits that added them.
* **1 M.** `WORKER_RESULT_THE_FABRICATED_ROW_WAS_ALREADY_GONE...` — the index holds a *shorter*
  revision than HEAD.

The working tree agrees with HEAD throughout. This was never a working-copy problem.

## The check I ran before the reset, and the four it caught

A `git reset -- docs/staging/` discards index blobs. For 98 of the 102 paths that loses nothing: the
`R`/`D`/`M` paths restore to HEAD's bytes, which are in the commit graph, and 84 of the 88 adds are
**byte-identical** to the copy now sitting in `done/`. I checked that by hash rather than by name,
which is what found the exception.

**Four staged adds held bytes that existed nowhere else in the tree:**

| document | index | `done/` |
|---|---|---|
| `SEAT_RESULT_THE_SAME_NINE_PATHS_WERE_STRANDED...2026-09-17` | 10,308 B | 8,456 B |
| `SEAT_RESULT_THE_STRANDED_WEATHER_MACHINERY_WAS_ONE_LAND_SHORT...2026-09-17` | 11,717 B | 10,364 B |
| `SEAT_RESULT_THE_WEATHER_CELL_ARTEFACT_WAS_THE_STALE_ONE...2026-09-16` | 14,194 B | 10,323 B |
| `WORKER_RESULT_THE_PER_CELL_WEATHER_STORES_TEMPERATURE_RE_DERIVES_EXACTLY...2026-09-16` | 11,280 B | 9,463 B |

In every case the index copy is the **later** revision and the archived copy is an earlier draft. The
direction is not inferred from the byte counts — it is legible in the text:

* the `done/` copy of SAME_NINE_PATHS says *"its outcome is recorded in §8 below"* **and has no §8**;
  the index copy has §8, with the resume's measured result in it.
* the `done/` copy of STRANDED_WEATHER says *"The full HadUK re-derive was launched and is reported
  in §6"* and §6 still lists it as owed; the index copy discharges it — 1,709,604 values, 100%
  within 0.001 C — and **strikes the owed line rather than deleting it**, which is this project's own
  correction discipline and is the strongest evidence of which way round the two drafts go.
* the other two are strict supersets: the index adds 59 and 21 lines and removes none.

So the archive move published a truncated document in four places. A reader of `done/` would have
found a forward reference to a section that does not exist, in a document whose whole point was that
a claim was measured rather than inherited.

## What I did

1. Wrote the four index blobs to their `done/` paths on disk. Recorded the four blob shas in
   `/var/tmp/index_recovery_blobs_2026-09-19.txt` before the reset, so the recovery was reversible
   from the object store even if the write had failed.
2. Under `background.tree_lock.shared_tree_lock`, **re-measured the cached diff inside the lock**
   (still 102 — no lane had staged anything under `docs/staging/` in the interval), re-ran the
   byte-preservation check on every `A` path, and only then `git reset -q -- docs/staging/`.
   The check is arranged to refuse and exit rather than reset if any staged add's bytes are
   unpreserved; it is not a comment saying I looked.
3. Verified inside the same run: `git diff --cached --name-only HEAD -- docs/staging/` **empty**,
   index root documents **94**, HEAD root documents **94**.

`git reset -- <pathspec>` is mixed and pathspec-scoped: it does not touch the working tree, so it is
not the `git checkout <path>` / `git stash` class CLAUDE.md forbids. Scope verified after the fact —
the six staged paths belonging to other lanes (`docs/direction/DIRECTION.yaml`,
`docs/direction/decisions.jsonl`, `docs/observability/agent_status.json`, `site/data/delivery.json`,
`site/data/tick_heartbeat.json`, `tests/background/test_an_items_own_do_not_draw_before_is_read_by_the_draw.py`)
are untouched, and the 24 untracked root documents that are the live work queue are untouched.

## What is now visible that was masked, and is not mine

With the index refreshed, `git diff --name-only HEAD -- docs/staging/` shows ~19 unstaged paths.
These are not damage — they are the genuine working-tree state the stale index was hiding: a further
batch of root documents already archived on disk but not yet committed out of the root in HEAD, plus
`docs/staging/.gitkeep`. That is the *next* archive batch, sitting where it always was. The refresh
did not create it and does not clear it.

## The refutation the item asked for, and where it stands

The item named it: *the index agreeing today and diverging again after the next batch archive, which
would mean the landing path itself — not this cleanup — is the subject.* That test is not settled by
this turn and cannot be, because it needs a batch archive to run after the refresh. It is worth
saying plainly that the four truncated documents are **evidence for the landing path being the
subject**: a mover that leaves the index holding a newer copy than the one it wrote into `done/` is
reading the root document from a stale index rather than from disk, and that is a property of the
mover, not of today's sediment.

## Bound

98 of 102 paths were free; 4 were not, and nothing in the item or in the previous turn's write-up
predicted them. A blanket `git reset` run on the item's description alone would have destroyed the
finished text of four result documents, and the destruction would have been silent — the file names
all survive in `done/`, so every count the archive alarm reads would have gone on saying the set was
a clean rename.
