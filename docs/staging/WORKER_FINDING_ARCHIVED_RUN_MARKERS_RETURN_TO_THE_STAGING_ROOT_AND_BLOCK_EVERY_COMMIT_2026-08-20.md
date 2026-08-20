**Severity:** BLOCKING · **Lane:** H_harness

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

1. **Instrument the write.** No `inotifywait` on this box; a small watcher that stats the ten
   paths every second and records the wall-clock of each reappearance would settle in minutes
   what an hour of reading did not. The one strong clue already in hand: an earlier batch all
   returned with an **identical mtime (21:26:11)** — a single simultaneous event, not a drip.
   Whatever does this restores the set at once.
2. **Anything that runs `git` against the working tree.** A simultaneous restore of exactly the
   tracked-at-HEAD set is the signature of a checkout, a stash pop, or a reset — not of a
   producer writing files one at a time. `tools/surgical_land.py`, the publish gate's HEAD
   checkout, and the fork/worktree reconcilers are all candidates and none has been checked.
3. **Only then read the publisher.** It was the obvious suspect and it is the one thing
   already proven innocent.

## The generalisable half

Both of my wrong answers had the same shape: files reappeared, and I reached for an actor with
intent — a producer, a sync — before checking whether my own last action explained it. Three
signals pointed the right way and I walked past all three: the files shared one mtime rather
than a spread, that mtime sat inside a gate run, and other lanes were committing normally
throughout. **When something reappears, timestamp it before theorising about who wants it
there.**

Same lesson as the 504 incident earlier today, which cost four theories before someone
partitioned the observations instead of reasoning about mechanisms.
