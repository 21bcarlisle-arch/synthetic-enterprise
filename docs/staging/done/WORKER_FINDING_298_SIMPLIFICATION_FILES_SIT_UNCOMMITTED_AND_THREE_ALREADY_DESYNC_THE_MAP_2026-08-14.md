# [WORKER-FINDING] 298 files under docs/design/simplifications/ sit uncommitted, and three already desync the map's own published counts (2026-08-14)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** measured, not repaired — filed per
`SELF_INTERRUPT_DISCIPLINE` (queue, do not fix on sight; this tick's draw was the surgical-land
leak, `WORKER_FINDING_THE_ONLY_LEGAL_LANDING_MOVE_LEAKS_150MB_A_KILL_2026-08-14`, now closed).

Found while landing an UNRELATED piece of orphaned work (`tools/migrate_atom_names.py` +
`tests/tools/test_pre_commit_gate_store_surface.py`, themselves discovered uncommitted while
closing the leak finding above) through `tools.surgical_land`. That landing was refused —
correctly — because the resulting-tree gate, in a checkout containing only HEAD plus those two
named paths, ran `tests/design/test_simplifications_store.py::test_counts_match_file_contents`
(pulled in by `tests/tools/test_pre_commit_gate_store_surface.py`'s own name-stem selection) and
it failed:

    D31_the_recon_grid_saturates_beyond_this_books_window: map simplifications_count=2 != store file count=1
    H27_payment_belief_gap: map simplifications_count=35 != store file count=34
    D28_the_detection_gap_is_quantised_by_this_books_placement: map declares simplifications_count=2 but has no store file

All three pass on the REAL working tree (`python3 -m pytest tests/design/test_simplifications_
store.py::test_counts_match_file_contents -q` → 1 passed) because the working tree already
carries the edits that reconcile them. None of those edits are committed.

## Scale, `observed-with-evidence`

    $ git status --short docs/design/simplifications/ | wc -l
    298
    $ git status --short docs/design/simplifications/ | awk '{print $1}' | sort | uniq -c
        286 M
         12 ??
    $ git diff --stat docs/design/simplifications/ | tail -1
     286 files changed, 681 insertions(+), 3520 deletions(-)
    $ git log -1 --format="%h %ad %s" --date=short -- docs/design/simplifications/
    30e27aebb 2026-08-14 EP13 DISCOVER/FRAME: there is no factor table, there are three, and they disagree by half

The net shape (−3520/+681, mostly deletions) reads as the `map_records`/note-tenant drain
`tools/migrate_atom_names.py`'s own docstring describes ("the fourth of the same move") — real,
coherent work from this box's own recent ticks, not noise. The last commit that DID touch this
directory was made TODAY. This is not a stale multi-week backlog; it accumulated across however
many ticks ran today without anyone committing this directory specifically.

## Why BLOCKING, not housekeeping

Two independent things are true at once, and each alone would be enough:

1. **A published figure is wrong right now.** The map (`docs/design/maturity_map.yaml`, itself
   committed and clean at HEAD) declares `simplifications_count` values for at least 3 atoms that
   do not match what is actually committed in the store — `D28`'s declared count-2 has ZERO
   committed store files. Any consumer reading the committed tree (a fresh clone, a CI checkout,
   `tools.surgical_land`'s own gate) sees a map that lies about its own store.
2. **The repo's sole legal landing path is unreliable in a way that depends on which test-name
   stems a commit happens to select.** This tick's first landing (`tools/surgical_land.py` +
   its own test, commit `5bf1efd52`) never triggered this check — nothing in that pathspec
   matched `store_surface`/`simplifications_store` by name, so the gate's own selection
   mechanism (`WORKER_FINDING_GATE_SELECTS_TESTS_BY_NAME_STEM...`, prior finding) never ran it.
   The SECOND landing attempt, touching a file with `pre_commit_gate_store_surface` in its name,
   did. So `surgical_land` currently works for some pathspecs and refuses others, for a reason
   that has nothing to do with what either commit changes — this is the same class of defect as
   the leak finding just closed (the one legal landing tool intermittently unusable), reached by
   a different mechanism.

## What is owed, and what is explicitly NOT being done here

This is 298 files of accumulated work from (apparently) several ticks today, net −2839 lines. It
is NOT reviewed here, and committing it blind is exactly the treadmill `SELF_INTERRUPT_DISCIPLINE`
exists to prevent — so nothing in `docs/design/simplifications/` was touched by this finding.
Owed, in order:

1. Whoever holds this lane next reviews and commits the backlog in reviewable chunks (the
   `migrate_atom_names` drain looks like one coherent chunk; the `??` dozen new atom files look
   like several unrelated FRAME/DISCOVER outputs and should not be bundled with it).
2. Once committed, `test_counts_match_file_contents` should pass at HEAD unconditionally, and the
   two orphaned files this tick found (`tools/migrate_atom_names.py`,
   `tests/tools/test_pre_commit_gate_store_surface.py`, still uncommitted, unblocked once this
   lands) can land cleanly.
3. Worth asking, not answering here: WHY did 298 files accumulate in one day without a single
   `docs/design/simplifications/`-scoped commit — is something in the map-write path
   (`H9_map_write_serialisation`, sole map writer) not actually flushing to git, or is this
   ticks-not-committing-their-own-output, the same shape as the leak finding's own lesson
   ("moving a leak out of the audited surface is not removing it")?

**Not taken here:** `tools/migrate_atom_names.py` and `tests/tools/test_pre_commit_gate_store_
surface.py` remain uncommitted in the working tree, verified green in isolation (26 tests
passing: `python3 -m pytest tests/tools/test_pre_commit_gate_store_surface.py tests/design/
test_atom_notes_store.py -q`) and ready to land the moment (1) is resolved.

## Addendum, same tick: HEAD ITSELF already fails the check this finding is filed under

Re-checked directly against a clean `git archive HEAD` extract (not the working tree, not a
surgical-land checkout carrying any of this tick's own paths):

    $ git archive HEAD | tar -x -C /tmp/head-check
    $ python3 -c "from background import finding_classes as fc; print(fc.check().ok, fc.check().failures)"
    False ['STALE SEVERITY CLASS_NO_CALLER_AND_NEVER_RUNS_2026-08-12.md: prints LATENT, instances
    derive BLOCKING ...']

**`check()` is already red at committed HEAD, before any change this tick makes.** It has been
since whichever commit archived `WORKER_FINDING_THE_MAPS_TWO_CONTROLS_ARE_UNREACHABLE_FROM_THE_
MAP_2026-08-14.md` citing `tools/migrate_atom_names.py` as discharge evidence without committing
that file in the same commit — this defect PREDATES today's tick entirely. It did not surface
before now only because `tools/pre_commit_test_gate.py::main` gates the class-consolidation
check behind `any(p.startswith("docs/staging/") for p in staged)` — nothing had committed
through `docs/staging/` since it broke. **The practical effect: every lane's landing path
through `tools.surgical_land` is refused the instant it touches `docs/staging/` at all**, which
is every archival, every new finding, every class re-render — the exact mechanism, reached a
different way, as the leak finding this report closes.

Attempted repair, abandoned as out of scope for one tick, recorded so the next attempt does not
repeat it: committing just the 3 reconciling files above PLUS `tools/migrate_atom_names.py` +
its test clears the `CLASS_NO_CALLER` staleness but the resulting checkout then reds on 4
DIFFERENT tests — `test_atom_notes_store.py::test_declarations_match_the_store`,
`test_atom_notes_store.py::test_stored_notes_are_nonempty_strings`,
`test_simplifications_store.py::test_counts_match_file_contents` (still, on OTHER atoms than the
3 picked), and the store-surface suite's own consistency check. **The 298-file backlog is not
reducible to a small hand-picked subset**; the map/store/notes stores are cross-referential
enough that a partial commit trades one inconsistency for another. This needs a full,
reviewed pass over the backlog, not a spot fix.

## Second addendum, same tick: it blocks `docs/design/maturity_map.yaml` too, not just `docs/staging/`

This tick's LANE 3 DISCOVER/FRAME draw (`PB3_book_growth_as_earned_outcome`, a legitimate,
tested, correct note-only change — `set_note_for_atom(..., "discover_note", ...)` plus the
matching `notes_rehomed` declaration, 19/19 green in `tests/design/test_atom_notes_store.py`
on the real tree) could not land either, for the same underlying reason reached a THIRD way:
touching `docs/design/maturity_map.yaml` at all pulls in `tests/design/test_maturity_map_
facets.py` and `tests/design/test_simplifications_store.py` by name-stem, and inside the
checkout (HEAD + only PB3's own 2 files) both the already-known D31/H27/D28 count mismatches
AND a previously-unseen `test_live_map_value_stream_hygiene` failure (`D41`/`D42`/`D43`/`D45`
declare `value_stream: close_to_learn` but are not in the reviewed list — a DIFFERENT
pre-existing defect, same shape) fire. Confirmed the PB3 change itself is clean in isolation
(`pytest tests/design/test_atom_notes_store.py::test_declarations_match_the_store
tests/design/test_atom_notes_store.py::test_stored_notes_are_nonempty_strings` → 2 passed).

**Practical scope, now measured three ways in one tick: the map/store surface is currently
unlandable by ANY lane, for ANY reason, the moment a commit touches `docs/staging/` OR
`docs/design/maturity_map.yaml`.** `docs/design/simplifications/PB3_book_growth_as_earned_
outcome.yaml` and the matching one-line `maturity_map.yaml` declaration sit correctly in the
working tree, uncommitted, ready to land the moment this backlog clears — same disposition as
the migration tool above.
