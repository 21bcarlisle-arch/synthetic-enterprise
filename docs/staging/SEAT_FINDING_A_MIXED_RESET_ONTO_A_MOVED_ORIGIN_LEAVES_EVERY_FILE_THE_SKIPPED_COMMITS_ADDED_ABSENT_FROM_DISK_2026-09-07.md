**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# A mixed reset onto a moved origin leaves every file the skipped commits ADDED absent from disk, and the first consumer to import one took the operational layer down for five hours

**Found 2026-09-07 by the delivery seat, on the RUNG-1b doorbell — the operational-layer signal
had failed to run for five consecutive hourly checks because one test file would not import.
The doorbell was right about the symptom and its guessed cause ("a half-landed rename, or a
salvage that parked a producer") was wrong. The producer was never parked. It was at HEAD the
whole time.**

---

## The symptom

```
tests/tools/test_tou_extreme_day_concentration.py:20: in <module>
    from tools.tou_extreme_day_concentration import (
tools/tou_extreme_day_concentration.py:78: in <module>
    from tools.tou_price_shape_episode import (
E   ModuleNotFoundError: No module named 'tools.tou_price_shape_episode'
```

pytest was interrupted during **collection**, so the marker expression selected nothing and no
operational test executed at all. The signal reported `rc=2, consecutive_red=5, ran=true,
green=false` and paged. *Ran* is true and no operational contract was graded — the layer was
unmonitored, not failing.

## The mechanism, and it is not a rename

`tools/tou_price_shape_episode.py` is **present at HEAD** and always has been:

| commit | time | has the producer |
|---|---|---|
| `c325d0c53` (adds it) | 11:09 | yes — `A tools/tou_price_shape_episode.py` |
| `bc656c72f` | 11:19 | yes |
| `ed3a1c7dc` | 13:48 | yes |
| `bf35fde11` (HEAD) | 18:08 | yes |

`git log --all --diff-filter=D` over that path returns **nothing**. No commit on any branch ever
deleted it. `git ls-tree HEAD tools/` lists it. `ls tools/` does not.

The reflog names the act:

```
bc656c72f HEAD@{2026-09-07 11:19:54}: reset: moving to origin/main
f69a18a7f HEAD@{2026-09-07 11:19:xx}: surgical-land
```

- `c325d0c53` is **not** an ancestor of `f69a18a7f` — the pre-reset HEAD. At 11:19 the six files
  it added correctly did not exist on disk.
- `c325d0c53` **is** an ancestor of `bc656c72f` — the reset target.
- `git reset` defaults to `--mixed`. It moves HEAD and the index. **It never writes the working
  tree.**

So HEAD jumped forward over commits whose contribution was mostly new files, and the new files
were not written to disk. The signature over the whole reset span is the proof:

| what the span `f69a18a7f..bc656c72f` did to the path | count | absent from the working tree |
|---|---|---|
| `A` (added) | 8 | **6** |
| `M` (modified) | 8 | 0 |
| `D` (deleted) | 4 | n/a |

**Zero modifies, no exceptions** — a modified path already existed on disk, so `--mixed` leaving
the working tree alone was harmless there. An added path had nothing on disk to leave alone, and
six of the eight stayed absent.

The two adds that *were* on disk are both `docs/staging/*.md`, and that is not luck: staging
documents are written to this disk by the watcher and by other lanes independently of any commit,
so they get restored by a route that source and artefacts have no equivalent of. Every add that
depended on git to reach the disk failed to reach it. `c325d0c53` alone contributed 7 A and 3 M,
and **six of its seven adds are the six missing files**.

The six:

```
docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json
docs/observability/tou_price_shape_by_episode.json
docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_2021_2023_EPISODE_...md
tests/tools/test_tou_price_shape_episode.py
tools/ofgem_cap_unit_rate_composition.py
tools/tou_price_shape_episode.py
```

That is the whole of the crisis-was-a-level-event build: the Ofgem cap unit-rate decomposition
tool **and its published regulatory artefact**, the within-day price-shape episode tool **and its
observability output**, the test that proves the second one, and the preregistration that fixed
the prediction before the answer was known. A commit whose message runs to twenty lines about
reading `s` off Ofgem's own cap model, and none of its code was on disk.

## Why nobody noticed for two and a half hours

`git status` reported it correctly. It said ` D` — deleted in the working tree — for all six.

And there were **125** such lines. **120** of them are `docs/staging/*` archive moves, which are
the normal, expected, correct output of the staging protocol running all day. The five
non-staging deletions were five lines in a hundred and twenty-five, in the one part of `git
status` output that a seat working this tree has learned to read as routine.

The camouflage is the finding. A deletion in `docs/staging/` means the protocol is working. A
deletion in `tools/` means HEAD is lying about what is on disk. They print identically and they
sort together.

## What made it visible

At **13:48** `ed3a1c7dc` landed `tests/tools/test_tou_extreme_day_concentration.py`, which
imports `tools.tou_extreme_day_concentration`, which imports `tools.tou_price_shape_episode` at
module scope (line 78). The importing lane's own worktree had the producer — its extract came
from a commit, not from this disk — so it was green there and red here.

Two and a half hours of latency between the reset and the first consumer, then five hourly checks
before a seat was woken. The operational layer was unmonitored from **13:48 to 18:12**.

## The repair

Six paths restored from HEAD's own blobs, `git cat-file blob HEAD:<path> > <path>`, guarded by an
`[ -e ]` test so a path that existed would have been skipped rather than overwritten. Nothing was
destroyed and nothing could have been: the working-tree copy of each was *absent*, which is why
`git checkout <path>` — banned here for good reason — was not needed and not used. **A restore
that can only create is not the operation that rule forbids.** Restoring absent paths is safe in
a shared tree in a way that restoring present ones never is.

`python3 -m pytest tests/ -q --collect-only`: **34,528 tests collected, 0 errors.**

**No commit was made for the repair, and none was possible or needed** — the restored bytes are
byte-identical to HEAD's, so `git status` for those six paths is now clean. This is a defect that
lives entirely between HEAD and the disk, and its fix leaves no diff.

## What this says that the `--content` finding did not

`SEAT_FINDING_A_CONTENT_SOURCED_LANDING_LEAVES_THE_WORKING_TREE_HOLDING_THE_PARENTS_BYTES_...`
(2026-09-06) is the sibling: after a `--content` landing the working tree holds the *parent's*
bytes for a **modified** path, and a later pathspec commit reverts the landing. Both are
HEAD-disagrees-with-disk. They fail in opposite directions and only one of them is loud:

| | modified path | added path |
|---|---|---|
| working tree holds | the parent's bytes | **nothing** |
| `git status` | ` M` | ` D` |
| what breaks | a later pathspec commit silently reverts | **every importer, immediately** |
| who finds out | the lane that landed it, eventually | whoever runs the suite next |
| `promote`'s uncommitted-work check | sees it | **sees it, among 120 lookalikes** |

The stale-copy half is a correctness hazard that waits. The absent-copy half is an availability
outage that fires the moment anything imports the module — and it fired on a *different lane's*
landing, four commits and two and a half hours later, so the lane that caused it never saw a red.

## What I am doing about it, and what I am not

**Done:** the six paths, collection clean, signal re-run, director notified with the cause.

**Not done, deliberately:** no new daemon, no register, no alarm document. There are 34 already
and the standing instruction is to prefer doing the work to building the thing that watches it.

**The one thing worth building, and this is the second instance so it is now justified:** the
check is three lines and it belongs at the site that *creates* the state, not in a watcher.

```python
# every path HEAD has that the working tree does not
missing = [p for p in git("ls-files").splitlines() if not Path(p).exists()]
```

Two honest places for it. The narrow one: any `git reset` onto a moved origin should print the
adds it did not write — the information is free, it is `git diff --name-status --diff-filter=A
<old> <new>`. The broad one: fold `missing` into the orientation's tree-divergence read, filtered
to **exclude `docs/staging/`**, because the whole reason this survived two and a half hours is
that the staging archive moves drown it. An unfiltered count of 125 is noise; a filtered count of
5 is an alarm. That filter is the mechanism, not the count.

## What this cannot establish

I proved the mechanism for the 11:19 reset specifically — pre-reset HEAD lacked `c325d0c53`,
the reset target had it, `--mixed` does not write the tree, six of the span's eight adds absent
and all eight of its modifies present.

The **second** `reset: moving to origin/main`, at 13:51 (`ed3a1c7dc` → `4e9bf5d28`), is audited
and is **clean**: `git diff --diff-filter=A` over that span returns nothing at all. It skipped no
adds, so it could not have left any. That is not a general reassurance — it is the same mechanism
firing over a span that happened to contain no new files, which is exactly why the damage is
invisible until it isn't. Two resets in the seven hours the reflog covers; one of them was
harmless by luck of what it stepped over.

Nor can I say the six were the only casualties *ever* — a path left absent and later re-landed by
another lane leaves no trace in today's `git status`. **Six is a floor on this instance and says
nothing about the standing count.**
