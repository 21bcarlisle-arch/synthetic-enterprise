# PRE-REGISTRATION — is the truncated console archive twin one day, or a class?

**Filed:** 2026-09-23, delivery seat, BEFORE the measurement.
**Severity:** INFORMATIONAL (a pre-registration carries no severity of its own).

## What is established before the measurement

`docs/staging/console/DIRECTOR_CONSOLE_2026-08-30.md` at HEAD is 32,798 bytes, header
`· 9 turn(s)`, sourced from 16 `.jsonl` transcripts. Its archive twin
`docs/staging/done/DIRECTOR_CONSOLE_2026-08-30.md` at HEAD is 2,505 bytes, header `· 1 turn(s)`,
sourced from 1 `.jsonl`. `diff` makes the room copy a strict superset: the twin is missing 296
lines, including the director's verbatim ruling of 2026-08-30T09:53:25Z on suspending I&C and his
refinement to the reservation.

The mechanism is already written down, in the docstring of
`tests/background/test_staging_rooms.py::test_no_LIVE_reference_or_console_document_exists_ONLY_in_the_root`:
the transcript writer APPENDS to `DIRECTOR_CONSOLE_<today>.md` all day, so an archival that runs
mid-conversation freezes a snapshot rather than archiving a record. That docstring cites this exact
file as the instance that motivated the carve-out.

HEAD holds **13** console transcripts in `done/`. Nothing has ever asked whether the other 12 are
whole.

## The question

Of the 13 `done/DIRECTOR_CONSOLE_*.md` at HEAD, how many are SHORT against a `console/` copy of the
same name — fewer bytes, fewer declared turns, or a strictly smaller `Source:` list?

## The prediction, written before running it

**2 of 12** further twins are short (range 0–4). The reasoning: the freeze requires the archival to
have run while that day's conversation was still growing, which is a timing coincidence, not the
normal path — most days were archived after the day rolled over. I expect the defect to be rare
rather than systemic, and I expect any further instances to cluster on the same late-August days as
the known one, because that is when the migration was being run by hand.

**What would refute me:** 5 or more short twins, which would make this a property of the archival
route rather than of one mis-timed run — and would mean the `done/` room has been quietly holding
truncated halves of the director's own record as its archive of them.

**What would also refute me, in the other direction:** 0 short twins other than 2026-08-30, with
the further 12 whole. That would make the known instance a genuine one-off and the remedy an
instance fix rather than a class fix.

## What the answer changes

If it is one day: replace that one twin and move on.
If it is a class: the archival route itself pairs a growing file with a frozen copy, and the fix is
at the route — an archival of a console transcript must refuse while that transcript can still
grow, which is the same carve-out the test above already makes, enforced at the writer instead of
asserted at the reader.

Either way the twin is never the copy that wins: the `console/` room copy is the record, and a
`done/` twin that disagrees with it is a snapshot, not an archive.

## Related

- `docs/staging/SEAT_RESULT_THE_FOUR_STAGING_DELETIONS_WERE_ONE_DISPOSITION_AND_THREE_LOSSES_2026-09-23.md`
  — the disposition pass this was filed from.
- `background/staging_rooms.py::room_shrinkage_violations` — the leg whose first live firing named
  this document.
