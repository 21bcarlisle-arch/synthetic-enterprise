**Severity:** BLOCKING · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

*Lane, stated because the choice is load-bearing and the alternative was available. This document
classifies into `uncommitted_and_orphaned_work`, whose register is `H_harness`. It is filed
`A_strategy_governance` instead, so it appears under that register's* `Refused consolidation — out
of lane, still live` *rather than being folded in. The reason is the subject, not the routing: the
gate here was RIGHT —* `staging_rooms --check` *printed the correct count of 27 on every commit.
What was wrong was the drawn item's claim about the tree, which is how work is directed rather than
how it is tested. The effect is also that §5's three open items keep a live reader, and that is
stated rather than left to be noticed, because a consolidated instance carries no queue presence of
its own.*

The Lane 0 item `nineteen-staging-dispositions-are-done-and-uncommitted` asked for one thing:
*"Commit the staged staging-root deletions and archival moves already sitting in the index by
pathspec `docs/staging/`."* Both halves of that sentence are wrong about the bytes, and carrying
it out literally would have un-archived 107 findings and destroyed 10 documents that survive
nowhere else. 27 genuine archival moves were landed instead. This is BLOCKING on the 107 — the
shared index still carries them and the next lane to run `git add docs/staging/` or commit that
index inherits the same trap.

## 1. What the item claimed, and what was there

| | item's claim | measured on the shared tree, 2026-09-23 |
|---|---|---|
| count | 19 | 116 staged entries under `docs/staging/` |
| kind | "deletions and archival moves" | **107 `AD`** + 9 `D ` staged; 31 ` D` and 66 `??` unstaged |
| net effect of committing the index | census −19 | **107 findings un-archived**, 6 documents destroyed |

The "19" matches nothing in the tree. It is not the staged count (116), the deletion count (40),
the move count (27), or the discard count (10).

**And the repo's own instrument already said 27.** `background/staging_rooms.py --check` prints
`STRANDED ARCHIVAL: 27 document(s) are archived into a sub-room ON DISK and still sit in the root
at HEAD`, and names the same 27 this landing moves — arrived at independently, by a different
route, from the same tree. The item's 19 was stale against a gate that runs on every commit. The
count was available for the asking and the item did not ask it.

## 2. The 107 — an index that would run the archive backwards

`git status` grades all 107 `AD`: **A**dded to the index, **D**eleted from the working tree. Every
one is a `SEAT_*`/`WORKER_*` document dated 2026-09-16..19, and for every one:

* it is **not** on disk at the staging root (`on_disk=0, missing=107`);
* its twin **is** on disk at `docs/staging/done/` (`done_twin_on_disk=107`);
* HEAD already has it at `docs/staging/done/` and **only** there (`also_at_root_in_HEAD=0`).

So the archival move for all 107 **already landed**. The index entries are residue: a tool staged
the root copies, the move then removed them from the working tree, and nothing has re-read the
index since. They are not a disposition awaiting a commit — they are the ghost of a disposition
that completed.

**Committing that index adds 107 root copies back beside their `done/` originals.** The queue would
gain 107 items overnight, every one of them already dispositioned, and the census the item was
raised to repair would be wrong by 107 in the opposite direction. The item's stated door —
pathspec `docs/staging/` — is what fires it.

The saving grace is narrow and worth naming, because it is why this has not already happened: a
*pathspec* commit refreshes the index from the working tree, so `git commit -- docs/staging/`
resolves the `AD` entries to absent and drops them. A bare `git commit` after any `git add`, or any
door that commits the index as it stands, does not. **The hazard is live and it is one command
away.**

## 3. The 10 that survive nowhere, and why they were NOT landed

Of the 40 deletions under `docs/staging/`, ten have no surviving copy anywhere in `docs/` — not in
`done/`, not in any other room:

```
SEAT_FINDING_ARCHIVING_A_FINDING_FALSIFIES_A_COMMONS_ARTEFACTS_POINTER_...2026-09-22.md
SEAT_FINDING_THE_SITE_LANE_REFUSED_ON_TWO_DOORS_PINNED_TO_THE_SHAPE_...2026-09-22.md
SEAT_RESULT_THE_CEILING_IS_THE_PROBABILITY_THE_DICE_USED_...2026-09-23.md
SEAT_RESULT_THE_PAGE_STOPPED_COPYING_THE_SEED_PRICE_...2026-09-22.md
SEAT_RESULT_THE_SEED_PRICE_CAN_ONLY_BE_ASKED_IN_THE_STATE_WHERE_IT_HAS_NO_ANSWER_2026-09-22.md
SEAT_RESULT_THE_STALE_KNOWLEDGE_MAP_IS_DISCARDED_...2026-09-23.md
records/PREREG_WHAT_SHAPE_IS_THE_SEED_PRICES_INTERVAL_ON_A_MEAN_OF_UNDETERMINED_SIGN_2026-09-22.md
records/PREREG_WHAT_THE_REPUBLISHED_SEED_PRICE_LOOKS_LIKE_WHEN_IT_IS_DERIVED_INSTEAD_2026-09-22.md
records/SEAT_RESULT_THE_FLAT_CHURN_BELIEF_NOW_REACHES_A_READER_...2026-09-22.md
records/WORKER_PREREG_W1_14_HOW_MUCH_OF_THE_HOUSEHOLD_POPULATION_THE_CELL_STORE_ALREADY_SERVES_2026-09-20.md
```

Six of the ten are **already staged** (`D `), so they are inside the item's pathspec and a pathspec
commit lands them. They were not landed, because `background/staging_rooms.py` states the protocol
in its own docstring:

> *"WHY A ROOM AND NOT A DELETION... Every file this module relocates stays inside `docs/staging/`
> and stays committed. That is not timidity: this project has twice found a control go QUIET rather
> than loud when the structure..."*

**An outright deletion is not a disposition this repo recognises.** Three of the ten are
pre-registrations — the artefact class whose whole value is that it cannot be revised after the
answer is known. Landing their deletion on the strength of a bare index read destroys the only
evidence that those experiments were designed before their results. The working-tree deletions
stand; HEAD still holds every one of the ten, and this document is the record of why they were
left there rather than a decision to discard them.

## 4. What WAS landed — 27 archival moves

Root/`records/` → `done/`, destination untracked on the shared tree, content preserved:

* **24** byte-identical to HEAD (pure moves, reproduced from HEAD bytes in an isolated worktree —
  no other lane's bytes were read);
* **3** where the archive copy differs, each difference a genuine disposition annotation.

The three needed their direction established one at a time, and **one of them ran backwards**:

| document | shared tree's `done/` copy | direction taken |
|---|---|---|
| `SEAT_RESULT_THE_CEILING_COST_CURVE_IS_CONVEX_...` | 209L, `BLOCKING`, **no addendum** | HEAD's root copy (364L) — it carries the `DISCHARGED`/`RECORDED` header and a 142-line addendum the archive copy predates |
| `WORKER_RESULT_THE_TWO_CEILINGS_SHARE_A_RULER_...` | 228L, additions only | `done/` copy — adds a `CORRECTION` block |
| `run_complete_20260922T064617Z.md` | 21L, additions only | `done/` copy — adds the `Superseded (not published)` stamp |

**The first one is the finding inside the finding.** Its archive copy is a *stale snapshot* taken
before the document was discharged. An archival move implemented as "take the `done/` bytes" —
which is what "commit the moves already in the index" means — would have silently reverted a
severity discharge and deleted a 142-line self-correction, and the diff would have read as a
routine file move. **A move is only content-neutral once you have checked that it is; the direction
has to be established per file, and here it was not the same for all three.**

## 5. What this leaves open

1. **The 107 ghosts are still in the shared index.** They need dropping (`git reset -- <paths>`),
   which is a shared-tree index operation and cannot be done from an isolated worktree. Until then
   any door that commits the index rather than a pathspec un-archives them.
2. **The 10 deletions are undecided**, not resolved. Either they are archived to `done/` like
   everything else, or someone states in the record why these ten are the exception. The three
   pre-registrations should not be the case that establishes the exception.
3. **The census still will not balance**, and this document is why: the number it is short by was
   never 19, and 10 of the 40 outstanding deletions should not be landed at all. Any repair keyed
   to "filed minus dispositioned" needs to decide first whether a deleted-and-unarchived document
   counts as dispositioned. It currently counts as neither.

## 6. The class

**An item's count is a claim about the tree, and a claim about the tree is an un-re-asked
prediction.** This one named a number (19), a kind ("deletions and archival moves") and a door
("pathspec `docs/staging/`"), and the bytes refuted all three — the count by 6x, the kind by
inversion (107 of the 116 staged entries run the archive *backwards*), and the door by consequence.
None of that cost anything to check: four `git status` reads and a basename join, before any of it
was believed.
