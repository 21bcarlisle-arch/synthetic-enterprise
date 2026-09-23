**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

*RECORDED and not BLOCKING: nothing here is owed by another lane. One disposition is landed, three
deletions are refused with their reasons, and the decision that had been re-asked three times is now
a control that can refuse a commit instead of a paragraph that cannot.*

---

## The item's premise, and what the bytes say

The drawn item described four tracked-at-HEAD files absent from the shared tree's disk, and asked
per file whether the deletion should be LANDED (completing a move) or REVERSED (never a
disposition). It offered a reading for three of them: (1) a genuine stranded archival, (2) and (3)
*"source side of moves whose `done/` copy is ALREADY at HEAD, so these are half-landed and the
deletion completes them"*.

**One of the four was a disposition. Three were losses.** The premise for (2) and (3) — that a
`done/` copy at HEAD means the move is half-landed — is a claim about NAMES, and both times the
bytes behind the names disagreed.

| # | Path | Item said | Bytes say | Done |
|---|---|---|---|---|
| 1 | `WORKER_RESULT_THE_SETTLEMENT_CEILING_..._2026-09-21.md` | stranded archival | `done/` copy is **byte-identical** to HEAD's root blob (`7a0d15e6`, all three copies) | **LANDED** — both sides |
| 2 | `console/DIRECTOR_CONSOLE_2026-08-30.md` | half-landed | room copy is a **strict superset**: 32,798B / 9 turns / 16 sources vs 2,505B / 1 turn / 1 source | **REVERSED** |
| 3 | `drafts/NEXT_PHASE.md` | half-landed | the two are **unrelated documents** sharing a generic filename | **REVERSED** |
| 4 | `.gitkeep` | cosmetic | three modules carry explicit `.gitkeep` ignores; the root genuinely empties | **REVERSED** |

### (1) The one real disposition

`git hash-object` of the shared tree's `done/` copy, HEAD's root blob, and the copy this turn wrote
are all `7a0d15e6409a4c32b3ee8c63ad8f038d6358a34b`. Diffed in both directions: identical. A
content-neutral rename, landed as both sides in one commit.

### (2) The deletion that would have destroyed the director's own ruling

`console/` holds nine turns of 30 August; `done/` holds one. 243 of 279 lines are absent from the
twin, including verbatim: *"Repair it — don't accept the limitation. My ruling on suspending I&C was
that the SIM keeps creating those accounts and only the company's book changes."*

The history explains the inversion, and it is the reverse of the assumed direction. `a1db11325`
archived a mid-conversation snapshot into `done/`. Only afterwards did `e3b580186` — *"the console
capture read a folder that went cold, and six days of the director's words left no trace"* — recover
the real transcript into `console/`. **The twin is older than the record it is the twin of.** Landing
the deletion would have left the one-turn capture as the only surviving copy.

### (3) Two different documents with one name

`drafts/NEXT_PHASE.md` is *"Phase RY: Reputation Feedback Loop"*, filed 2026-07-08.
`done/NEXT_PHASE.md` is *"Proposed Next Phase: 6b — Event-Driven Customer Lifecycle (MVP)"*. They
share no content. This is the archival-paired-by-name class already on file in
`WORKER_RESULT_THE_ARCHIVAL_PAIRED_BY_NAME_WOULD_HAVE_DELETED_THE_DIRECTORS_OWN_RULING_...`,
reaching a second subject.

### (4) `.gitkeep`

Kept. `background/deadmans_switch.py`, `background/supervisor.py` and
`background/staging_watcher.py` each carry an explicit `.gitkeep` ignore, so the file's existence is
already assumed by three readers; and git does not track empty directories, so a fully drained queue
would take `DEFAULT_STAGING_ROOT` with it. The deletion carried no disposition behind it.

---

## The thing worth more than the four dispositions

**This decision has now been taken three times and bought nothing, because a finding cannot refuse a
commit.**

    2026-09-07  the gate flagged the two-rooms condition; a seat consolidated into `console/`.
    2026-09-22  an archival pass was handed the same file and HELD THE DELETION BACK, naming the
                243 missing lines.
    2026-09-23  this item named it again as half-landed, and asked for the deletion.

Each earlier decision was correct and recorded in `docs/staging/`. Neither could stop the third ask,
because the state that provokes it — a name in both rooms — is indistinguishable from outside from a
half-finished move. So the remedy is one leg, not a fourth paragraph:
`tests/background/test_staging_rooms.py::test_an_archive_twin_NEVER_holds_turns_its_record_room_copy_lacks`.

Keyed to the **superset relation** between the rooms, not to today's byte counts — it stays green
while `console/` holds every turn `done/` does, whichever grows. Both legs are mutation-proven and
each fails on the leg written for it: inverting the direction reds the superset assert; deleting the
`console/` copy — the exact act this item asked for — reds the non-empty guard.

---

## My prediction, refuted, and by an answer I had not named

Pre-registered in
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_THE_TRUNCATED_ARCHIVE_TWIN_IS_ONE_DAY_OR_A_CLASS_2026-09-23.md`
before measuring: of the 13 `done/` console twins, **2 of 12** further ones would be short, and I
named refutation in both directions (≥5 short = a class; 0 = a one-off).

**The answer was neither.** 12 of the 13 have no `console/` pair at all, so the question is
unaskable for them: the comparison population is **n = 1**, and that one is the short one. I
predicted a rate over a population that does not exist — a pre-registered count predicting the
instrument rather than the world, which is a shape already on file here.

What this changes: the class fix I had costed is not available and not needed, because there is no
second pairable case. It also sets the control's population at exactly one pair, which is why its
non-empty guard is load-bearing rather than decorative — at n = 1, "the filter matched nothing" and
"the record copy is gone" are the same disk state, and only the guard tells them apart.

## What I did NOT establish

How the thin `done/` copy came to be written — a capture over a partial session set, or a truncation
after the fact. The 2026-09-22 pass left this open on purpose and preserved the copy as the evidence
for it. **I have not repaired or deleted the twin for that reason**: both would have made the
control green by destroying the artefact the open question is about, which is keying a control to
today's answer with extra steps. Both copies stand as they are, and the question stays answerable.

## Shared-tree state

The three reversed deletions were restored on `/home/rich/synthetic-enterprise` from HEAD
(write-if-absent; no working copy overwritten). `room_shrinkage_violations()` — whose **first live
firing** this was, from `57229702e` — named `console/DIRECTOR_CONSOLE_2026-08-30.md` correctly, and
goes green on the restore rather than on a deletion. Its names-not-a-count design earned itself here
on that first firing: the room read **26 on disk against 26 at HEAD**, so a count would have printed
zero and said nothing.
