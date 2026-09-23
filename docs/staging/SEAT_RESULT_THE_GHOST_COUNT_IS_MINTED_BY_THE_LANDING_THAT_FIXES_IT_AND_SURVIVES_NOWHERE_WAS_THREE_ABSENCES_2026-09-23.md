**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

*Filed BLOCKING on §7 and dropped to RECORDED in `57229702e`, later the same turn, with the sentence
below left standing rather than edited: it was true when written and the turn did not end where it
said it would. Dropped HERE and not in a second document, so this claim and the lane's books cannot
disagree. §7's own "not landed here" is corrected in place at the end of that section.*

*BLOCKING on §7 alone, which is new here and not inherited: the control that exists to make a
deletion from `records/` loud reported `0 violation(s)` while three documents were missing from it.
§§1–6 are discharged — the shared index is clean and the three documents are restored. The prior
document this continues,
`SEAT_RESULT_THE_UNCOMMITTED_STAGING_DISPOSITIONS_WERE_27_MOVES_NOT_19_AND_THE_ITEMS_OWN_DOOR_WOULD_HAVE_UNARCHIVED_107_2026-09-23.md`,
may now drop to RECORDED: its §5.1, §5.2 and §5.3 are all closed below.*

## 1. What the item asked, and what was actually there

Lane 0 item `the-107-index-ghosts-and-the-ten-unarchived-staging-deletions`, three asks:

| ask | item's claim | measured on the shared tree, 2026-09-23 22:15–22:25 |
|---|---|---|
| (1) drop the stale `AD` index entries | 107 | **134** — and the 107 was right when written (§2) |
| (2) decide the deletions that survive nowhere | 10, "three are PREREGs" | **3**, all in `records/`; the other 7 were never deleted (§5) |
| (3) refresh a stale working copy, 139L vs HEAD 213L | live and time-sensitive | **spent** — disk, index, HEAD and `origin/main` all 241L |

Ask (3) was closed by the reconcile merge `fd5301b3f` between the hand-off and the draw. Nothing was
done for it and nothing needed to be.

**The duplicate-work check cited this turn's own draw.** It named
`the-107-index-ghosts-and-the-ten-unarchived-staging-deletions` as "already held by another writer";
the claim was 61 seconds old with `paths: []` — my own. Carried on, correctly.

## 2. The ghost count is minted by the landing that fixes it

The item said 107. I measured 134 and then asked which commit deleted each root copy:

| commit that removed the root copy | of the 134 | what it was |
|---|---|---|
| `22c07b232` | 105 | the first staging archival batch |
| **`6bd209c0b`** | **27** | **"land the 27 archival moves that had already happened"** |
| `b45f13ca1` | 1 | the last stranded archival |
| `05c7923f8` | 1 | the BLOCKING finding closed by the operation it called impossible |

105 + 1 + 1 = **107**. The item's number was exact at the moment it was written, and was wrong
thirteen minutes later, because `6bd209c0b` — *the landing that discharged the very document the
item cites* — minted 27 fresh ghosts of the class its own §5.1 was raised about.

**The mechanism, which is the reusable part.** An archival move lands by committing the `done/` copy
and deleting the root copy at HEAD. Any root copy still sitting in the index then becomes `AD` —
added-to-index, absent-from-disk — the instant that deletion reaches HEAD. So the ghost population
is not a residue that sits still and waits to be counted: **it is a function of the archival
landings, and every archival landing increases it by the number of its own moves.** A count of it is
spent by the next landing, and the landing most likely to be next is the one raised to fix it.

This is the class *"an item's count is a claim about the tree, and a claim about the tree is an
un-re-asked prediction"* one turn further on, and the interesting part is that re-asking was not
enough on its own: the number had to be re-asked **after** the remedy, not before it. A count taken
before a landing and acted on after it is stale by construction, however carefully it was taken.

## 3. What licensed the reset: the direction, per file, on all 134

`git reset` on an `AD` entry discards the staged blob, and an unreferenced blob is garbage. The
staged blob is the ROOT copy; the surviving copy is the `done/` twin at HEAD. So the reset is only
safe where HEAD's `done/` copy is not *older* than the index's root copy — the
*an-archival-move-is-not-content-neutral* trap the prior document caught one of, in the other
direction, and paid for by checking.

Compared index blob against HEAD's `done/` twin for all 134:

* **125** byte-identical — pure residue, nothing to weigh;
* **9** differ, and in **all nine the `done/` copy is the later revision.** Three are strict
  supersets (`+8L`, `+46L`, `+3L`). In the other six, every line the index copy has and `done/`
  lacks is the **superseded original** of a line `done/` revised: two are a severity discharge
  (`BLOCKING` → `RECORDED`) plus a `CLOSED` block of 9 and 17 lines; four are cross-reference
  pointers updated from `docs/staging/X` to `docs/staging/done/X` or `docs/staging/records/X`.

Zero of the nine carried work HEAD lacked. Re-verified **after** the reset, on the bytes rather than
the plan: of the 134, documents whose content is absent from both HEAD's `done/` and disk — **0**.

**Reversibility, recorded before the write.** `refs/seat-recovery/index-ghosts-20260923` →
tree `f6381f958e8c9499fdda698a6cd6518e2fe72e45` is the ENTIRE pre-reset index, every other lane's
staged blob included. Nothing done here needs a recovery that ref cannot serve.

## 4. Done: the index

155 staged entries → 21. Zero `AD` remain. The 12 entries outside `docs/staging/` are byte-for-byte
the same 12 as before — the pathspec list was built from `git status -z`, never from a directory.

A second lane took `index.lock` mid-operation (a scoped `git commit` of the liveness heartbeat, its
pre-commit hook running). Waited on it in the foreground; it landed as `b6a4f2a5c` and the reset
already done was unaffected, because a pathspec commit does not read the rest of the index. The lock
was not removed.

## 5. "Survives nowhere" was three different absences

The prior document listed ten deletions with "no surviving copy anywhere in `docs/`". Asked of each
of the 14 deletion entries: does HEAD have it, does the index have it, is it **on disk**?

* **7 are phantom.** HEAD has them, the index says deleted, and **the document is sitting on disk at
  its own path, byte-identical to HEAD** (67L, 148L, 179L, 167L, 160L, 101L, 64L — all `SAME`).
  Nothing was ever deleted. This is the same index-only-residue class as the 134, mirrored: an
  entry dropped from the index rather than added to it. Reset, not decided.
* **4 are room-to-room moves with the content surviving** (§8).
* **3 are genuinely absent from disk, HEAD the only copy, all three in `records/`.**

**Not restored since.** The seven files' mtimes are 2026-09-22 11:37 to 2026-09-23 15:30 — the
latest is six hours *before* `6bd209c0b` landed at 21:43. They were on disk, at their own paths,
when they were called survive-nowhere.

The phrase covered three absences that come apart: absent from `done/`, absent from the **index**,
absent from **disk**. Seven documents were absent from the first two and present in the third, and
the remedy owed differs completely — `git reset` versus restoring bytes versus a real decision.
CLAUDE.md's rule is *"before measuring a thing, say what it is… the cause split follows from the
definition; never let the definition be inferred from the split."* Here the definition was inferred
from a single `done/`-twin lookup, and the split it produced put 7 accidents and 3 judgements in one
bucket of 10.

## 6. Done: the three, and the repo had already decided them

The item offered a choice — archive to `done/` like everything else, or record why these are the
exception. **Neither: they are restored, and it is not my call.**
`background/staging_rooms.py::RECORDS_DIRNAME` rules on it in the director's words (2026-09-03):

> *"`records/` and not `done/`, and that distinction is load-bearing. `done/` means dispositioned and
> out of the way; `staging_archive_policy` may fold an archived document once it is old and
> unreferenced. A pre-registration must stay READABLE for exactly as long as the claim it graded is
> published… Filing it as done would put the machine's own falsifiability record on an archive
> path."*

So `done/` was never available for these three, and no exception needs recording: **a deletion from
`records/` is not a disposition this repo recognises, it is an accident.** Restored from HEAD —
55L, 80L and 86L; the two staged deletions reset. `records/` is now fully clean against HEAD.

Two are pre-registrations; the third, `SEAT_RESULT_THE_FLAT_CHURN_BELIEF_NOW_REACHES_A_READER_…`, is
a result filed in `records/` beside its own prediction, which is what the room is for.

## 7. THE NEW DEFECT — the floor keyed to the answer it was written on

Three documents were missing from `records/` and `staging_rooms --check` printed:

```
Population floors: 0 violation(s)
```

`POPULATION_FLOORS = {reference: 6, console: 2, records: 38}`, and `records/` holds **377 at HEAD**.
The room must lose **340 documents** before that control says a word. It is keyed to the population
on 2026-09-03, the day the floor was written, and the room has grown 10x since.

Its own two declarations name the property it is not checking:

> `"""Rooms holding fewer documents than they held when the floor was set."""`

> *"A pre-registration is never deleted and never archived, so this can only rise. A drop means the
> machine's own falsifiability record is being tidied away, **which is the one thing in this folder
> that must never happen quietly**."*

Monotonicity is declared; a static literal is implemented; and the gap between them is 339
documents of silence. This is CLAUDE.md's *"key a control to the property, not to today's answer"*
exactly — *"a control pinned to the current state goes red when the code becomes more honest and
stays green when the claim rots"* — and the rot is measured: the one thing that must never happen
quietly happened quietly, and was found by hand.

**Stated plainly because it bears on the finding's own strength: `0 violation(s)` was predicted, not
discovered.** I read the literal `38` and the room's size before running `--check`, so the reading
confirmed an expectation rather than refuting one. The finding is the 339-document gap, which is
arithmetic on two numbers in the file, not the green light.

**The fix is the property**: compare each room's population against its population at HEAD, so any
drop in the working tree is loud the moment it appears and the bound maintains itself. Not landed
here — it is a `background/` change with its own gate selection and it needs a control that fails
when mutated, and this document's landing is the record. `--check` already exits 1 today (one
stranded archival, one sediment violation) and is not in the blocking hook chain, so a room-keyed
floor cannot wedge another lane.

> **DISCHARGED in `57229702e`, later the same turn. The paragraph above is left standing rather than
> revised, for the reason it names one section earlier: a prediction edited after its answer is not a
> prediction, and "not landed here" was true when written.**
>
> `room_shrinkage_violations()` keys the floor to HEAD, names what went missing rather than counting
> it, and is wired into `render()` and the `--check` exit. `head_room_documents()` is a sibling of
> `head_root_documents()` 140 lines above it — same subprocess shape, same `readable`/`why` contract,
> one directory level down, which is exactly what that function discards. **The literal floors stay**,
> because HEAD dropping below the migration baseline is a loss that has already LANDED and a ruler
> made of HEAD cannot see that by construction. Two subjects, neither derivable from the other.
>
> Four controls, each mutation run and reverted. The load-bearing one asserts **both legs on one
> tree state** — the full room silent in the same call the robbed room is loud — because a version
> that flagged every room would pass a one-leg test, which is this repo's most-repeated trap.
> Mutating its ruler from HEAD to `POPULATION_FLOORS` reds it, and that mutation *is* the defect
> this section reports. Two more close the fail-open legs: an empty read of a floored room, and an
> unreadable git. Proven against the real defect and not only in a tmp tree — removing exactly
> today's three documents from `records/` on the live tree prints `Population floors: 0 violation(s)`
> beside `ROOM SHRINKING records/: 3 document(s) ... (374 on disk, 377 at HEAD)`, all three named.
>
> **One mutation came back green and was not accepted as an equivalence.** The unreadable-git
> mutation was first written `return [] or [...]`, which is a no-op — `[]` is falsy, so the
> expression evaluates to the original list. The control was never exercised. Re-run as a real
> replacement of the branch body, it fires. Recorded because CLAUDE.md's rule is that a silent
> mutation is a missing test or an equivalence and *never* the flattering one — and here it was
> neither: it was a defect in the mutation.
>
> **No live-tree assertion, deliberately.** `console/DIRECTOR_CONSOLE_2026-08-30.md` is genuinely
> absent from the shared tree's disk right now (§8), so a live assert would red every lane for a
> condition this turn did not cause. The advisory `--check` already exits 1, so the doorbell shouts
> without wedging anybody. That deletion is now the leg's first live subject.

## 8. What remains, named rather than left to be noticed

Four ` D` entries under `docs/staging/`, none of them survive-nowhere:

* `WORKER_RESULT_THE_SETTLEMENT_CEILING_IS_A_CONSEQUENCE_OF_ITS_CURVE_…_2026-09-21.md` — the one
  genuine stranded archival; `staging_rooms --check` names it. `done/` copy on disk, not at HEAD.
  Needs a landing of both sides, with the direction established per file.
* `console/DIRECTOR_CONSOLE_2026-08-30.md` and `drafts/NEXT_PHASE.md` — source side of moves whose
  `done/` copy is already at HEAD. Half-landed; the deletion completes them.
* `docs/staging/.gitkeep` — cosmetic, but a deletion is not a disposition here either.

## 9. The class

**A residue whose size is a function of the remedy is not a quantity you can count once.** The item
carried an exact number, took it honestly, and was overtaken by the commit that discharged its own
neighbouring section. And **a bound written as a literal on the day it was true becomes a bound the
system exceeds by 10x**, at which point the control is not weak, it is absent — while still printing
a number that reads like a pass.
