# SEAT PRE-REGISTRATION — what the three undispositioned carriers do across the partition

**Date:** 2026-09-04
**Class:** R10 (an absurdity is fixed as a class, not an instance)
**Lane:** H_harness
**Written BEFORE running anything.** The measurement follows in the finding of the same subject.

---

## Why this is being asked at all

`9810e2bdd` swept the ABSENT-vs-PRESENT-BUT-UNREADABLE conflation across the eight carriers the
self-clearing-alarm census calls `real`, and built `tests/background/test_episode_prior_partition.py`
to hold it. That control's subject is **derived from the census's own `real` rows** — deliberately,
so a sixth carrier of the class fails there rather than joining it quietly.

A derived subject has a blind spot exactly where the derivation reads nothing: **a carrier with no
disposition row at all is not in the `real` set, so it is outside that control by construction.**
`background/self_clearing_alarm_census.py --check` exits 1 at HEAD (`23c63e296`) naming three:

    .seat_continuation.json      background/seat_continuation.py
    .sim_next_run_not_before.json  background/sim_runner.py
    .weekly_rhythm.json          background/weekly_rhythm.py

They are the only three carriers in the tree that neither the census's disposition check nor the
partition control has ever looked at. That is the residue, and it is what this turn measures.

## What I predict, before running it

Stated so the run can refute me. The partition is: **missing file / missing key / null / non-positive
/ corrupt (truncated, unparseable) / not-even-a-mapping (`[1, 2, 3]`)**.

1. **`weekly_rhythm.read_baton` returns `None` to every one of them**, and `tick()` answers `None`
   with **BOOTSTRAP** — which *overwrites the baton* with a blank step armed for the next Monday. So
   I predict: an unreadable baton **destroys an open, overdue step**, `due_on` is re-stamped
   forward, `days_late` resets to 0, and the FINDING that was owed is never filed. That is the
   2026-08-09 shape verbatim — the failure shortening its own episode — and the write makes it
   unrecoverable.

2. **`seat_continuation._load` returns `[]` to both absent and unreadable**, and `hand_off` is
   `_load()` → append → `_save()`. So I predict a present-but-unreadable store is **truncated to the
   single new entry**: every live continuation destroyed, silently, by the next hand-off. Absent and
   unreadable deserve opposite acts here — writing one entry over nothing is correct, writing one
   entry over an unreadable store is data loss.

3. **`sim_runner.pause_owed_from_a_previous_process` crashes on `[1, 2, 3]`.** Its docstring claims
   it fails toward running "in every direction: no file, unreadable file, corrupt JSON, a
   non-instant". But the code is `(raw or {}).get("next_run_not_before")`, and a JSON list is
   truthy, so `.get` is reached on a list → **`AttributeError`**. This is the identical
   `json.loads`-accepts-a-list crash `9810e2bdd` fixed in three carriers, still live in a fourth —
   and invisible to its control for exactly the reason above.

4. **Also `sim_runner`: the OSError branch mislabels present-but-unreadable as absent.** The
   docstring says "A MISSING file and a CORRUPT one are the same decision and DIFFERENT news …
   Same answer, separate reasons." A file that exists but cannot be read (permissions, a directory,
   an I/O error) takes `except OSError` and is reported as *"no deadline was recorded by a previous
   process"*. Same answer is right; that reason is false, and it is the one line an operator reads.

## What would refute each

1 is refuted if `tick()` preserves `due_on`/`opened_at` across an unreadable baton, or if BOOTSTRAP
does not write. 2 is refuted if `hand_off` re-reads or refuses on an unreadable store. 3 is refuted
if `[1, 2, 3]` returns `(0.0, reason)` rather than raising, or if the caller catches it such that no
behaviour changes. 4 is refuted if the OSError branch already names the file's existence.

## What done means for the turn

Every one of the three carries a disposition row stating a verdict on the **episode** question and,
separately, an answer on the **loader** question — because `benign` is scoped to the question the
census asks ("can a write shorten an episode?") and has been read as clearing rows for a question it
never asked. Each real conflation repaired. `census --check` green at HEAD. A control that asserts
absent and unreadable **DIFFER** for these three, with a reachability leg, mutation-proved.
