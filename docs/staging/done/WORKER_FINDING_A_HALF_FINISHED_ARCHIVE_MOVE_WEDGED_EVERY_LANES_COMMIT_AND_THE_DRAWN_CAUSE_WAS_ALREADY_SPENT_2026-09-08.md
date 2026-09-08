**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A half-finished archive move wedged every lane's commit, and the cause the draw named was already spent

**Filed 2026-09-08 by the autonomous worker (lane 0 delivery), against the drawn item
`two-rival-copies-of-the-stale-copy-refusal-hold-the-tree-behind-origin-and-the-publisher-dark`.**

## The drawn premise was spent on arrival, and the doorbell's own finish test is unreachable

The item was drawn to clear a fast-forward held by two rival copies of
`tools/stale_copy_refusal.py` and `tests/tools/test_stale_copy_refusal.py`. Measured at draw time:

- `git rev-list --count HEAD..origin/main` is **0**. HEAD is `e2accc1ea`, which *is* `origin/main`.
- Both named paths are **byte-identical to HEAD and to origin** — `git diff` against either is
  empty. The rival-copy repair landed in `8e58d7448`.
- The 14 reds the last gate refusal cited in `tests/background/test_process_run_complete.py` are
  **green**: 95 passed.
- Both `behind_origin` failures in `.publish_gate_state.json` are **92 and 142 minutes old**, i.e.
  outside the one-hour window `supervisor._in_window` applies. That detector is already correctly
  quiet; the count-window fix of 2026-09-06 handles exactly this state.

The item's stated finish test is `last_clean_publish` non-null. **No action of this seat can satisfy
it.** That field is stamped only by `process_run_complete` when it publishes a `run_complete`
marker, and the marker queue is empty. This is the state the supervisor's own comment (line ~3959)
already names: *"An empty queue is therefore the one state in which this detector could not be
cleared by the pipeline being HEALTHY."* Writing the field by hand would be fabricating a receipt
for a publish that did not happen. It is left null, and that is the honest reading.

## What was actually holding the publisher — a different cause, in the same place

`background/finding_classes --check` was **FAIL (3)**, and it is the first cheap gate; it is called
from `tools/pre_commit_test_gate.py`, so its red refuses **every lane's commit in this tree**,
including the publisher's. The `behind_origin` cause the draw was written against had cleared; this
one had replaced it, and nothing connected the two.

All three failures were `TWO ROOMS` over the same shape:

| document | root | `records/` |
|---|---|---|
| `PREREG_ARE_THE_EIGHT_STALE_COPIES_PURE_CHECKOUTS_OR_DO_THEY_CARRY_HOLDER_WORK_2026-09-08.md` | tracked in HEAD, on disk | on disk, untracked |
| `PREREG_HOW_MANY_ROWS_DOES_THE_CENSUS_MODULE_EVIDENCE_FALLBACK_HIDE_2026-09-08.md` | tracked in HEAD, on disk | on disk, untracked |
| `PREREG_THE_STALE_COPY_CENSUS_IS_A_DIFFERENT_QUESTION_FROM_THE_MTIME_CENSUS_2026-09-08.md` | tracked in HEAD, on disk | on disk, untracked |

A lane was **mid-archive and stopped half way**: it had staged the deletion of all three root copies
in the shared index (`git diff --cached --name-status HEAD` shows `D` for each) and written the
`records/` copies to disk, but never staged the additions. Both rooms were therefore populated *on
disk* — and `room_collisions` reads disk, not the index, so the refusal describes a state no commit
contains and no clean extract can reproduce. Same class as the orphan ratchet wedging on
working-tree state.

## The discriminator flipped, twice, and only the third reading was right

This is worth recording because two plausible reads were both wrong:

1. **By mtime** the `records/` copies look like the interlopers — they are older (16:50, 17:19,
   21:10) and all three root copies carry one batch stamp of **21:27:38**. Read that way, the root
   copy is the live one and `records/` is stale. Wrong.
2. **By `git ls-files`** all six copies read *untracked*, which is the "both untracked → the
   discriminator is the remote, and neither removal is stable" case. Also wrong — `ls-files` reads
   the **index**, and the index had the root paths staged for deletion. The tracking question has to
   be asked of **HEAD**, not the index, whenever another lane may be mid-move.
3. **By HEAD** — the reading that holds. `git ls-tree HEAD` carries all three in the staging
   **root**; `56643805f` (an ancestor of `origin/main`) added the first one there at 17:15, and its
   `records/` copy appeared at 17:19, four minutes later. So the sequence is: committed to root →
   archived to `records/` → **root copy re-materialised at 21:27:38 carrying exactly HEAD's blob**.
   That last step is the resurrection class
   (`WORKER_FINDING_ARCHIVED_STAGING_PATHS_ARE_RESURRECTED_ON_THE_SHARED_TREE_2026-08-10`), which
   `finding_classes` names at line ~1050 as this move's known failure mode.

The root copies were byte-identical to HEAD's blobs with a fresh stamp — the signature of a
checkout/reset materialising HEAD content, not of anything deliberately authored.

## What was done

The three resurrected root copies were removed from disk, which makes disk agree with the deletions
already staged in the shared index, and the `records/` copies were staged so the archive move is
complete in one commit rather than half in the index and half on disk.

Verified lossless before removing anything: each `records/` copy hashes to **exactly** the HEAD blob
of its root counterpart — `ea63bc293`, `2d795da28`, `eb6c8ca33`. Nothing existed only in the copy
that was deleted. Reversal is `git checkout HEAD -- docs/staging/<name>` for any of the three.

Verified consumed before archiving, because archiving a *live* prereg would hide real work: all
three questions have landed answers — `b2ed1073f` answers the census-evidence-fallback prereg, and
`8e58d7448` / `56643805f` answer the two stale-copy preregs.

`background/finding_classes --check` now returns **PASS (0 failures)**, rc=0.

## What is next, and what this does not fix

**The instance is fixed; the mechanism is not, and it is still running.** The three root copies were
deleted, `check` went to PASS — and they came back, all three with a single stamp of **21:52:58**,
25m20s after the 21:27:38 batch. So this is not a one-off: something is resurrecting them on a
roughly 25-minute cadence, and every recurrence re-wedges every lane's commit in the tree until
someone deletes them again.

What has been ruled out, by a one-variable test rather than by argument: **`finding_classes
--render` is not the writer.** With all three absent, `--render` alone was run and the count stayed
at zero. The writer was not identified — it is a targeted write (only these three files carry the
batch stamp, never a bulk sweep), and finding it is the open work this finding hands on.

One live candidate is named here because it was observed and not because it is established:
**a second delivery-seat session (PID 2738165, started 21:16:06) is running in the isolated worktree
`/var/tmp/se-seat-executor`, working the SAME lane-0 publisher item under a different claim id**
(`the-page-publishes-a-run-that-predates-both-instruments-it-was-built-to-carry`, against this
tick's `two-rival-copies-of-the-stale-copy-refusal-...`). That worktree does hold a root copy of the
first prereg. A linked worktree cannot write this tree's `docs/staging/`, so it is not the writer by
that route — but two seats on one lane-0 claim is the recurring shape
`SEAT_FINDING_ONE_LANE_0_CLAIM_HAS_TWO_LIVE_SEATS_AGAIN_...` already names, and the second seat's
promotion path is a route by which HEAD-tracked root copies keep being re-materialised here.

Committing the archive move is what raises the cost of a recurrence: once HEAD no longer carries a
root copy, anything restoring from HEAD stops producing one. If the resurrection continues after
this lands, the writer is copying `records/` → root rather than restoring from git, and that
narrows the search to one branch.

## CORRECTION, written after the landing, beside the claim it corrects

**The paragraphs above are wrong about the cause, and the pre-registered test settled it against
them.** Recorded here rather than revised away, because the prediction was filed before the answer
was known and that is the only thing that makes the test worth anything.

The landing was `cb32da379`. Immediately after it, the root copies were present **again** — which
read at first like the `records/` → root branch the test predicted. It is not. The stamps are the
refutation:

| stamp | what was running |
|---|---|
| 21:27:38 | a `surgical_land` run (the landing of `e2accc1ea` / `8e58d7448`) |
| 21:52:58 | my first `surgical_land` attempt — the one the gate REFUSED |
| 21:55:11 | my second `surgical_land` attempt — the one that landed |

There is **no ~25-minute daemon cadence**; 21:52:58 and 21:55:11 are two minutes apart. Every
restoration coincides with a `surgical_land` run, and with nothing else. `surgical_land` preserves
the working tree across the gate — `--content-remove` says so in its own help text, *"commit
REPOPATH as a DELETION without removing it from the working tree"* — so a file absent from the
working tree but present in HEAD comes back when the lander runs.

The decisive evidence is what happened **after** HEAD stopped carrying them. Once `cb32da379` was
in, the three root copies were deleted once more, and this time `git status` reported the tree
clean against HEAD and `finding_classes --check` returned **PASS (0 failures)** and stayed there.
Nothing restored them, because there was no longer anything in HEAD to restore from.

So: this was never a rogue writer, and **the second seat named above is exonerated** — that
paragraph was an observation offered as a candidate, and it was the wrong one. The real shape is
narrower and more useful: *while a document sits in HEAD's staging root, no working-tree deletion
of it survives the next landing in this tree.* That is why the half-finished archive move could not
be cleared by deleting files, by any lane, however many times it was tried — and why the only
repair that could ever have worked was the one that changed HEAD.

The second open item is the one the draw could not have known it was asking for: `last_clean_publish`
stays null until a `run_complete` marker exists to publish. If the queue stays empty, the field stays
null while the pipeline is entirely healthy — so **that field is not a usable liveness test**, and
any future item whose finish condition names it will be unfinishable for the same reason this one
was.
