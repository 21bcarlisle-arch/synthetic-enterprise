**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

**Discharged:** `tests/tools/test_console_capture_lapse.py` -- eleven controls, each named for a
defect in this document; the capture now runs from a hook and `check()` raises when it lapses.

# The console capture read a folder that went cold, and six days of director input left no trace

**Found 2026-09-07** by the director: *"The console capture is dead. docs/staging/console/ ends at
DIRECTOR_CONSOLE_2026-09-01.md — six days stale... it stopped without anything noticing."*
**Reproduce:** `python3 tools/console_instruction_record.py --check`.

---

## The cause, and it is one line

The harness names a session's transcript folder by slugging its **working directory**. A seat
launched from `/` writes to `~/.claude/projects/-`; one launched from the project writes to
`~/.claude/projects/-home-rich-synthetic-enterprise`. `console_instruction_record.py` had the first
of those **hardcoded**.

On **2026-09-03 the seat moved under systemd** — this session's own first turn is *"Worker seat
(re)started under systemd"* — its launch directory became the project, and every transcript from
that moment landed in the other folder.

| | folder read | transcripts | newest |
|---|---|---:|---|
| what the capture read | `~/.claude/projects/-` | 16 | **2026-09-03 10:03** |
| where the sessions went | `~/.claude/projects/-home-rich-synthetic-enterprise` | 2,143 | live |

## Why nothing noticed, which is the part that matters

The module was **explicitly designed to fail closed**. Its own docstring says: *"An unreadable
transcript RAISES. It must never write an empty record, because an empty record is
indistinguishable from a director who said nothing."*

That guard was correct and it guarded the wrong state. It fires when there is **no** transcript. The
state that occurred was a folder that still existed and still held sixteen real transcripts, and had
simply stopped receiving new ones. **Blindness was guarded; staleness was not**, and to every reader
the two render identically. `observe()` returned `{'changed': False}` — cheerfully, every cycle.

**And nothing ran it anyway.** `observe()` has zero callers. Its own comment says it *"runs in the
worker loop"*; no hook, no timer and no daemon invokes it. The capture only ever ran when a session
remembered to type `--write`, which is an exhortation wearing a mechanism's clothes.

## The naive fix would have been worse than the gap

Pointing the scanner at the live folder sweeps in every daemon-injected prompt. Measured after doing
exactly that:

| day | turns captured | not the director |
|---|---:|---:|
| 2026-09-04 | 39 | **26 (67%)** |
| 2026-09-06 | 87 | **73 (84%)** |

The intruders are `"You are the autonomous worker, woken by a scheduled tick..."` — the machine's own
words, quoted as the director's, in a file `pull_forward_proposal.release_verdict` reads as his
authority. The records ballooned to 485 KB, 992 KB and 1.56 MB against 22–54 KB for a genuine day.

**There is no structural discriminator to fall back on.** An interactive seat, an autonomous worker
tick and a delivery-seat dispatch all record `userType: "external"`, the same `cwd` and the same
`version`. Only the text differs — and matching text is the enumeration this module already warns
about in another context (*"enumerating a family one member at a time is how the next member gets
through"*).

**So the capture had to move to where the answer is known.** At `UserPromptSubmit` the turn arrives
on its own, in a session whose identity is available, and the classification problem does not arise.

## Two defects committed inside the repair, both kept here

**The control read a different room from the writer.** `_newest_captured_day` globbed the staging
root and `done/` and never `console/`, so it reported a four-day lapse over records sitting on disk
— the original bug, reproduced inside its own guard, within the hour.

**The backstop deleted evidence.** `write()` reads only transcripts modified inside a three-day
window, so re-running it regenerates an older day from nothing. It cut the 2026-09-03 record from
**22,907 bytes to 10,592**, silently dropping turns it could no longer see, while being repaired for
losing six days. I overwrote an untracked file without backing it up first. It is now recovered to
34,218 bytes — larger than the original, because the merge unions both folders.

## What changed

1. **The transcript folder is derived from the launch directory**, never hardcoded, and the legacy
   folder is still read so its history is not orphaned.
2. **Capture is a `UserPromptSubmit` hook** (`.claude/hooks/capture_director_console.py`),
   resident-seat guarded, verbatim, never blocking. The scan stays as a backstop, not the mechanism.
3. **One judgement, shared.** `is_director_prompt()` is used by both the hook and the scanner, so
   they cannot drift.
4. **`write()` merges, never regenerates.** A turn can leave the record only by a human deleting it.
5. **`--check` raises a finding** by comparing the record against `.human_last_input` — two
   independent signals, because one cannot tell silence from blindness. Wired into
   `process_run_complete` beside the stretch-log check.
6. **`--backfill DAYS --from-dir PATH`** recovers days that have aged out of the window.

**THE RULE, the director's words:** *a session that takes director input without capturing it is a
finding.* Raised, never a refusal — blocking a commit would not write the missing turns and would
stop the work those turns were asking for.

## What is recovered and what is not

2026-09-04 to 2026-09-07 are now captured, filtered to his turns only. The six days were recoverable
because the transcripts still exist; had they rotated, they would not have been.

**Not fixed here, named instead:** six days (2026-08-28 to 2026-09-02) exist in **both**
`docs/staging/console/` and `docs/staging/done/`. That duplication predates this work — it is at
HEAD — and `record_path` now prefers an existing copy so it does not worsen it. Deciding which room
owns an archived console record is a separate piece of work.
