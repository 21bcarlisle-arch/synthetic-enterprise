**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted

# FINDING — the alarm family files eight distinct names a week and clears one

The other half of the sediment alarm's own advice. Attributing its seven-day window by producer
family (full table in
`docs/staging/records/SEAT_RESULT_THE_WORK_CHANNEL_WAS_THREE_QUARTERS_WRITE_UPS_OF_FINISHED_TURNS_AND_TWO_OF_MY_FOUR_PREDICTIONS_WERE_REFUTED_2026-09-23.md`):

    WORKER_FINDING_REPEATING_ALARM_    8 filed    1 dispositioned    net +7

**This refutes a prediction I filed before running it.** I predicted the alarm family's net would
be ≤ +2, reasoning that a regenerated document re-files under the *same* name and so scores on both
sides of `root_flow`. The eight are eight **distinct names**, so `alarm_repetition`'s
one-document-per-firing holds *within* a signature and not *across* signatures — a new condition
mints a new document and nothing ever merges them.

Nine sit in the root right now. They are the only family left in the work channel that is
**regenerated rather than authored**, and for a regenerated document the sediment control's *other*
remedy is the right one: fewer channels that file, not a disposition route. A route would archive a
document whose producer will simply write it again next cycle.

## What is already built and not run

`tools/staging_migrate_rooms.collapse_alarms()` exists, is idempotent, is additive by construction
(the survivor gains one `- \`instance\` (first seen ...)` line per document folded in, and the
folded documents move to `done/` with their text intact), and groups by the declared `Signature:`
line via `alarm_repetition.family()` — the same rule that will file the next one, deliberately, so
the collapse cannot come apart on the next firing. It was written for a one-time migration and has
not been run against the current nine.

**It is not run here on purpose.** This turn's change is a classification and a relocation; folding
nine alarm documents into their families is a merge that changes document *contents*, and landing
both in one commit would make an attribution impossible if anything downstream moved. `--dry-run`
first, then apply, then land — one variable.

## Why the ratio is the finding and not the nine

Eight in and one out is a **rate**, and it is the same shape as the one the seat was handed: a
backlog whose size is a function of what other lanes are doing cannot be drained by drawing it.
Collapsing today's nine leaves the producer untouched, so the honest exit test is not "the root has
fewer alarm documents" — it is **"a second firing of a condition already in the queue adds an
instance line and not a document"**, keyed to the property and not to today's count.

## Recommended, not asked

Run `collapse_alarms` as its own commit, then decide whether `escalate()` should fold on write
rather than leaving a migration tool to do it afterwards. I am not doing either in this turn; the
RESULT route was 74% of the filings and this is the remaining 3%.
