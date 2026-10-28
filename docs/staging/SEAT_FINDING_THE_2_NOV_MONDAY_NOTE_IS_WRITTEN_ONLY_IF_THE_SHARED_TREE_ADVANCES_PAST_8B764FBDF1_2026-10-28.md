**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` (weekly rhythm)

# The 2 Nov Monday note is written only if the shared tree advances past 8b764fbdf1, and it has not advanced for 17 hours

**Found:** 28 Oct 2026, 12:40 GMT, by the delivery seat, pre-flighting the first live Monday note
(claim `the-first-monday-note-is-written-and-reads-right`).

**The facts, read just now.**

- The 07:00 tick is `daily-self-note.service`, run from `/home/rich/synthetic-enterprise`. It calls
  `weekly_rhythm.tick()` as a passenger, from the **shared tree's working copy**.
- The note writer (`weekly_rhythm.write_monday_note`, `director_concerns.monday_note`) arrived in
  `8b764fbdf1` (28 Oct 10:36 GMT). The shared tree's HEAD is `5e3e9966a5` (27 Oct 19:24). It does
  **not** contain `8b764fbdf1`, and `docs/operations/MONDAY_NOTE_FOR_THE_DIRECTOR.md` is not on disk there.
- The shared tree will not fast-forward. The supervisor logged this at 11:34 GMT: `ORIGIN FORK
  (NOT_ADVANCED)`, origin 55 ahead, refused by 30 dirty paths that origin also changes
  (`.gitignore`, `background/schedule_manifest.yaml`, `background/tick_mode.py`,
  `docs/direction/DIRECTION.yaml`, `docs/direction/decisions.jsonl`, ...). Its log says: "THE STEP IS TO LAND OR REVERT THOSE PATHS".
- The live baton (`docs/observability/.weekly_rhythm.json` on the shared tree) holds the 26 Oct
  Monday step: opened, finding filed, **never closed**. On 2 Nov the tick lapses it and opens the
  new Monday in the same call. That is the lapse branch. The note-writer test walked only the
  bootstrap branch until this commit.

**Pre-flight on origin's code.** I copied the live baton and ran `tick()` at 29 Oct, 1 Nov and
2 Nov 07:00 against temporary paths. The results were WAITING, WAITING, then OPENED with
`lapsed: 2026-10-26` and a note written. The note had all four sections. Its one close since
28 Oct (`the-26-oct-advisor-steer-asks-that`) was graded `nothing to land`. Nothing is waiting on
the director, and nothing is overdue.

**One reading defect, fixed in this commit.** The 26 Oct ruling closed four rows with one
resolution. The note printed its first 220 characters four times, cut off mid-word ("pr..."), and
named none of the four questions. A shared answer is now printed once, with each question it
closed listed beneath it, and truncation stops at a word boundary.

**What decides 2 Nov.** If the 30 paths are not landed or reverted on the shared tree before
2 Nov 07:00, the tick runs the old code. The step opens and no note is written. Nothing
says so, because the old code has no note to fail on. The ask is not to add a watcher. It is to
clear the shared tree's 30 contested paths, which other lanes hold.

**Discharges when** a note dated 2026-11-02 is on the shared tree with four sections, checked
after 07:00 on 2 Nov (handed on as `the-2-nov-monday-note-is-on-the-shared-tree`).
