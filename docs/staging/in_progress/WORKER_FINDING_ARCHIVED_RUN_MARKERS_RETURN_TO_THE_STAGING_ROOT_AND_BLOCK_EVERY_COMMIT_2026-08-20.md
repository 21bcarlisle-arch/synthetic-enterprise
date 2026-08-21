**Severity:** BLOCKING · **Lane:** H_harness

> **STILL OPEN, AND WHAT IS OPEN IS THE CAUSE.** Step 1 below — the instrument — is BUILT
> (`background/staging_root_resurrection_watch.py`, wired into `tools/surgical_land.py::_land_once`
> around `run_gate`, R15-proven three ways in
> `tests/background/test_staging_root_resurrection_watch.py`). Steps 2 and 3 are NOT done: the
> writer is still unidentified and this document still names no cause.
>
> **What unblocks it: the next occurrence.** The condition is not live as I write this (1 root
> marker, 0 twins, `finding_classes --check` green), so there is nothing to measure yet. The
> instrument now records the wall-clock, the per-file mtimes, whether the bytes were already git
> objects, and the process table, against the named landing it happened inside. When a record
> appears in `docs/observability/staging_root_resurrection.jsonl`, read it and close this.
> Do NOT close this on a reading of the code — see "The generalisable half" at the bottom.
>
> **2026-08-21:** still open, still no cause. What is new is a *restore source* — the INDEX — with
> a live specimen found on the shared tree and four operations measured against it, plus two
> corrections to how this document's own instrument should be read. See
> "A restore source nobody has checked".

# Archived run markers keep coming back to the staging root, and while they are there NO commit on this tree can pass the gate

**This document deliberately does not name a cause.** I proposed two and measured both to be
wrong. The evidence is below; the mechanism is an open question, and the next person should
start by instrumenting rather than by reading, because reading is what produced the two wrong
answers.

## The condition

`finding_classes --check` reports TWO ROOMS: a `run_complete_*.md` present in **both**
`docs/staging/` and `docs/staging/done/`. The finding-class consolidation check is wired into
the pre-commit gate, so while this holds **every commit in the repository is refused**,
whatever it touches. It is not specific to one lane's work.

At 2026-08-20T21:30Z: **10 root markers with a `done/` twin**, 1 legitimately pending, 77 runs
completed today. Every twin is a strict superset — the `done/` copy is the root copy plus the
`## Superseded (not published)` footer that `background_worker.retire_superseded_marker()`
appends.

## What is RULED OUT, by measurement rather than by reading

| ruled out | how |
|---|---|
| `supervisor._sync_origin_staging` restoring them from origin | ran its exact set arithmetic against the live tree: `origin_md - local_md` is **0 files**, and 0 of those are run markers. Its `done/`+`in_progress/` exclusion works correctly. |
| `retire_superseded_marker` leaving a copy behind | it is `marker.rename(done_dir / name)` — a move, not a copy |
| the sim producing fresh markers with old names | the returning markers carry timestamps from 07:00–09:40; the sim is producing 19:00+ names |
| a failed commit rolling back the deletion | REAL, and it explains the *earlier* half of this: `git commit -- <pathspec>` restores the working tree when the gate refuses, so each refused attempt undid the deletions and the next attempt found them again. **But it does not explain the current state** — commit `6fbc92732` SUCCEEDED, carrying all ten as `rename {} => done/`, and within minutes all ten were back in the root. |

That last row is the important one. The files were deleted **in a commit that landed and was
pushed**, and they returned anyway.

## Why this matters more than it looks

The gate refusal is not the damage. The damage is that the condition is **invisible to whoever
caused it and expensive for whoever hits it**: it presents as your own commit being refused for
someone else's findings hygiene, so the cost lands on an unrelated lane. Today it took six
commit attempts across roughly ninety minutes of gate time to land one unrelated piece of work,
and another lane had independently cleared one instance of it four hours earlier
(`294447ccf`, *"Also resolves the redundant staging root copy the publisher had already
archived, which was refusing every commit on the tree"*). It came back.

Anything that returns after being fixed by two different parties on the same day is a
mechanism, not an accident.

## Where to look, in order

1. ~~**Instrument the write.**~~ **BUILT 2026-08-20** — `background/staging_root_resurrection_watch.py`.
   No `inotifywait` on this box, and a 1-second daemon would be a new undeclared process, so the
   instrument is a **bracket** rather than a watcher: it censuses the real staging root either
   side of the gate in `surgical_land._land_once` and records anything that appeared, against
   that landing's message and window. That window is not a guess — `git reflog` puts
   `surgical-land` for `6b6f364f5` at **21:26:51**, forty seconds after the identical-mtime batch
   at **21:26:11**, so the reappearance happened *inside* a gate run. A bounded foreground
   `--watch` poller is provided for the live case; nothing starts it.

   The record's discriminating field is **`all_bytes_known_to_git`**: `git hash-object` the bytes
   on disk and ask whether that object is already in the store. True for the whole batch means
   these bytes were committed here before — a checkout/reset/merge/saved-copy **restore**. False
   means something **composed** them. That one boolean rules out an entire half of the candidate
   space and neither of the two wrong answers had it. Alongside it: per-file `mtime_ns` and a
   `single_mtime` flag (one mtime for a batch = simultaneous restore; a spread = a producer
   dripping), `tracked_at_head`, the twin's strict-superset status, and **the process table taken
   at the moment of detection** — the one fact that expires and that no later reading recovers.
2. **Anything that runs `git` against the working tree.** A simultaneous restore of exactly the
   tracked-at-HEAD set is the signature of a checkout, a stash pop, or a reset — not of a
   producer writing files one at a time. `tools/surgical_land.py`, the publish gate's HEAD
   checkout, and the fork/worktree reconcilers are all candidates and none has been checked.

   *Partial, 2026-08-20, and labelled as what it is: **inferred from reading, not measured.***
   `surgical_land`'s every `git` call against the real root is `read-tree` **without `-u`**,
   `add`/`update-index`/`hash-object`/`write-tree` under a throwaway `GIT_INDEX_FILE`, and
   `commit-tree`/`update-ref` — none of which writes the working tree; `_overlay_untracked_data`
   copies root→checkout, the wrong direction. `git worktree list` shows **eleven** other working
   trees against this repo (`/tmp/ep6-worktree`, `/tmp/k3wt`, `.claude/worktrees/agent-*`, …),
   and none of them has been checked. **This is exactly the kind of reasoning that produced the
   two wrong answers — treat it as a hint about where to look, never as a ruling-out.** The
   ruled-out table above is measurements; this paragraph is not, and it is kept separate for
   that reason.
3. **Only then read the publisher.** It was the obvious suspect and it is the one thing
   already proven innocent.

## A restore source nobody has checked: the INDEX (2026-08-21, measured)

Every candidate in step 2 is a *command*. This section names a **state** instead, because a live
specimen of it was sitting on the shared tree this morning and it arms three of the commands
already on that list.

### The specimen, on the real tree

`git status` reported one entry of the shape `AD` — staged as an ADD, absent from the worktree:

| fact | command | value |
|---|---|---|
| index holds the staging-root path | `git ls-files -s docs/staging/WORKER_FINDING_ARCHIVED_RUN_MARKERS_…md` | blob `7bd03a47` |
| HEAD does **not** hold that path | `git cat-file -e HEAD:<root path>` | rc≠0 |
| HEAD holds the *current* doc elsewhere | `git rev-parse HEAD:docs/staging/in_progress/<same name>` | blob `fcb06765` |
| the indexed blob is the **pre-move** version | `git log --oneline -1 b096aeaeb` | committed at the root, later moved to `in_progress/` by `4db804458` |

So the index was still carrying an **older copy of this very document, at the staging root**,
after the document had been moved and rewritten. That is one `git checkout` away from being a
root file again.

### What that state does, measured in a scratch repo rather than read

Four operations against an `AD` entry, each run in a throwaway repo:

| operation | result |
|---|---|
| `git checkout -- .` | **file RESURRECTED in the worktree** |
| `git restore .` | **file RESURRECTED in the worktree** |
| `git stash` + `git stash pop` | **file RESURRECTED in the worktree** |
| `git commit -m … -- <other path>` with a **refusing** pre-commit hook | not resurrected |
| `git commit` with **no pathspec** | ghost **silently committed** into the tree |

Two consequences, and they cut in opposite directions from the ruled-out table above:

1. **The one surviving "REAL" row does not cover this shape.** A *failed* pathspec commit leaves
   an `AD` entry alone — measured. So "a failed commit rolling back the deletion" is not the
   general mechanism; it explains at most the half it was offered for.
2. **The restore is from the INDEX, not from HEAD.** All three resurrecting commands write the
   worktree from the index, at once, with one mtime — which is precisely the *"single
   simultaneous event, not a drip"* signature recorded at 21:26:11.

### This calibrates the instrument, and not in its favour

`staging_root_resurrection_watch.py:188` computes `tracked_at_head` as
`git cat-file -e HEAD:<rel>`. **An index ghost is by construction not at HEAD**, so a
resurrection of this specimen would be recorded with `tracked_at_head: False` — while step 2
above tells the reader to look for *"a simultaneous restore of exactly the **tracked-at-HEAD**
set"*. Applied literally, that sentence discards the specimen it was written to catch.

The companion field needs the same care. `blob_known_to_git` is `cat-file -e` on the hashed
bytes, and step 1 reads `True` as *"these bytes were committed here before"*. **`git add` alone
writes a blob into the object store** — no commit required — so `True` also covers *"some lane
staged these bytes and never committed them"*. The field is sound; the stated reading of it is
narrower than the field.

Neither of these is a reason to distrust the instrument. Both are reasons to not let its
*prose* do the ruling-out, which is the failure this document was opened about.

### What was done about the specimen

The stale entry was dropped with `git reset -- <root path>` (index-only; nothing in the worktree
or in any commit changed, and no other lane's staged entry was touched). The evidence above is
recorded here because the specimen itself is now gone.

**Still not a cause.** Nothing here identifies who wrote that index entry, and this section is
deliberately not filed as the answer. What it does is convert step 2 from a list of commands
with no precondition into a list of commands **plus the state that makes them dangerous** — and
that state is cheap to check for: `git status --porcelain | grep -E '^(A|M|R)D'` was one line
this morning and is a question the tree can be asked at any time.

## The generalisable half

Both of my wrong answers had the same shape: files reappeared, and I reached for an actor with
intent — a producer, a sync — before checking whether my own last action explained it. Three
signals pointed the right way and I walked past all three: the files shared one mtime rather
than a spread, that mtime sat inside a gate run, and other lanes were committing normally
throughout. **When something reappears, timestamp it before theorising about who wants it
there.**

Same lesson as the 504 incident earlier today, which cost four theories before someone
partitioned the observations instead of reasoning about mechanisms.
