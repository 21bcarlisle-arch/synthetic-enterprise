**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE4_ia_register_and_nav`

# RESULT — the archival was landed in three parts, and the part nobody had measured was 192 documents that had reached no ref at all

**Filed 2026-09-16 by the autonomous worker (scheduled tick)**, against the drawn Lane 0 direction
*"SITE4 is held at zero by a staging archival of 644 paths that nobody committed"*. The previous
turn adjudicated the eleven findings OPS11 read as live and landed the seven that had earned it.
This turn took the remaining drift, and the drift was not the shape the direction described.

## What the direction said the problem was, and what it actually was

The direction, and the message this seat itself wrote on `ef3a69183`, both described the drift as an
archival whose deletions had landed while the `done/` copies had not. That is true of part of it and
**false of the largest part**, and the correction is kept here beside the claim rather than quietly
applied.

`git status --short docs/staging/` showed 623 changed paths at the start of this turn. Decomposed:

| Population | Count | What it actually was |
|---|---|---|
| Deleted from the staging root, `done/` copy on disk, byte-identical | 87 | a real archival move, unlanded |
| Deleted from the root, BLOCKING at HEAD | 9 | archival that would bury a live blocker |
| Deleted from the root, `done/` copy OLDER than HEAD's root copy | 2 | not a move — a content drop |
| Untracked in `done/`, root copy already gone from HEAD | 399 | **never a move at all** |

That last row is the one that was mis-stated. Of the 399, **192 appear in no reachable ref under
either room** — not at the root before the move, not in `done/` after it. 136 `run_complete`
records, 38 SEAT documents, 16 WORKER findings, 1 PLANNER mint: 423,288 bytes that existed on one
disk and nowhere else. They were not un-archived and they were not recoverable from history,
because no part of them had ever been committed. Some of the remainder were reachable only through
`e8f3a2618` — *"preserved shared-tree worktree state before ff to origin/main 20260903T1104Z"* — a
**dangling** commit, on no branch and not an ancestor of HEAD, which `git gc` deletes.

## The three commits, and the evidence each rests on

Three commits, kept separate so each carries its own receipt rather than one mixed one.

1. **`ef3a69183`, 174 paths.** The 87 byte-identical moves whose severity at HEAD is RECORDED or
   LATENT, deletion and `done/` copy in one commit. `git show -M --summary` detects **87 renames**,
   so the move is visible as a move rather than as a delete beside an add. No lane's BLOCKING set
   changes, because none of the 87 was BLOCKING.
2. **`b6a147bb7`, 6 paths.** Three of the nine BLOCKING archivals, checked in two steps rather than
   read as prose: `parse_discharge` reports `released=True` for all three, meaning every artefact
   each cites is landed; and the five cited falsifiers were then **run**, and all five pass.
   Step two is the one the `done/` route never performs — a cited artefact existing is not the
   artefact refuting anything.
3. **The `done/` cabinet, 398 paths of 399.** Pure additions. Each had its root copy already absent from
   HEAD, so nothing lands in two rooms, and `done/` is outside
   `finding_severity.classifiable_documents`' non-recursive root glob, so no lane's BLOCKING set
   moves on it either.

## The mechanism, stated because it is what makes the read load-bearing

`classifiable_documents` globs `*.md` **non-recursively**. The previous turn established that this
makes the `done/` move itself the discharge. This turn found the second half of the same hole:
**`false_discharges` iterates that same root-only list**, so the one control that checks a discharge
claim against the filesystem cannot see a document that has already been moved. A finding that
claims a discharge it has not earned is caught while it sits in the root, and stops being checked at
the exact moment it is discharged. That is why 3 of the 9 could be settled here in minutes and the
other 6 cannot be settled cheaply at all.

## What is still held back, and it is six files and two

**Six BLOCKING archivals carrying no `Discharged` field**, needing the per-file adjudication the
eleven got. Named with lanes, because a count is not a work list:

- `A_strategy_governance` (4) — the decomposition class's reachability leg; the nine-seed floor's
  publish path; the departure headline's mean-over-shoppers; the Lane 0 pair move's remaining third.
- `W2_customer_generator` (1) — the producer's named witness diverging from the control's real one.
- `G_data_learning` (1) — the proof page telling a reader a larger figure was smaller.

**Two REPEATING_ALARM ledgers**, `SEAT_CLAIM` and `SEAT_CONTINUITY`, both dated 2026-08-26. These
are daemon-appended documents and their `done/` copy is *older* than HEAD's root copy — the
CONTINUITY one is missing 45 lines and the 2026-09-15 entries that HEAD carries. Archiving them
would drop committed content while wearing an archival's clothes. Both have been superseded by
2026-09-15 refilings that are live in the root, so the lifecycle is legitimate and only the
direction of the copy is wrong.

## What this means for SITE4

Unchanged and unchanged in kind: `SITE4_ia_register_and_nav` stays at `level_current: 0`. Its four
named blockers are the same four the previous turn left — unbuilt repairs, not an uncommitted
archival — and `level_zero_contradicted_by_its_own_controls --atom SITE4_ia_register_and_nav` names
exactly those four and no others, before and after all three commits. **No level move is recorded
here, because none was earned.** The drawn direction predicted SITE4 would move once the archival
landed; the archival has now substantially landed and SITE4 did not move. The prediction is kept
here rather than revised.

## The one that is worth building next, and it is one clause

The cheapest control that would have caught this whole turn's subject, and that fails on today's
tree rather than on a fabricated fixture:

    a commit that moves a document into done/ must leave the BLOCKING set no larger than it found
    it, OR the document must carry a Discharged field whose cited falsifiers are landed AND pass

The second half already exists as `parse_discharge` plus a pytest node-id run; what is missing is
that nothing applies it at the moment of the move. Nine documents this turn would have been
partitioned by that clause into exactly the 3 and the 6 it took a manual pass to separate.
