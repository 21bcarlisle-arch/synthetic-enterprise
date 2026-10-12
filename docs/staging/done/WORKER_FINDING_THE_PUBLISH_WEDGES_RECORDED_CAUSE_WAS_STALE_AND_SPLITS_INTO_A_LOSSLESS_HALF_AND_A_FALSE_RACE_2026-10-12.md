**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Class:** `publish_gate_and_wedge`

# The publish wedge's recorded cause was stale, and the real collision splits into a lossless half and a false race

**2026-10-12, scheduled worker tick.** The doorbell's recorded cause for the publish-gate wedge
read "origin/main is 69 commit(s) AHEAD of HEAD (collides with 3 of ours: `docs/status/SEAT_STRETCH_LOG.md`)".
By the time this tick could act, `python3 -m background.origin_reconcile --check` read
`behind=3→4→7` across the session as other lanes landed — the recorded number was already stale,
and the named colliding path was not among the real blockers found below.

## What was found

`origin_reconcile`'s own collision census is rename-blind: `background/origin_reconcile.py`
builds its path lists from `git diff --name-only HEAD origin/main` (lines 272, 274, 306) with no
`--no-renames`/`--diff-filter`. A precise split (`git diff --no-renames --diff-filter=D/M
--name-only HEAD` crossed with `git diff --no-renames --name-status HEAD origin/main`) over the
shared tree at the time found two populations, not the one the wedge record named:

1. **32 paths, lossless.** This tree held an uncommitted DELETION of a `docs/staging/*.md` file
   that `c6542f76e` ("The staging backlog is given one fate each") only MODIFIED in place. HEAD's
   bytes exist in both histories, so nothing hangs on resolving this in any particular way.
   `tools/refresh_to_head` refuses a missing working copy (`refused_no_base` — it compares
   existing content, not absence), so `git checkout HEAD -- <paths>` was used instead. This
   surfaced a second, separate pre-existing defect: 31 of the 32 root paths restored this way
   already had an UNTRACKED, DAYS-OLD duplicate sitting in `docs/staging/done/` (mtimes 2026-10-02
   through 2026-10-09 — orphaned local triage work, never committed, unrelated to `c6542f76e`),
   which tripped `background/finding_classes`'s TWO-ROOMS check. All 32 duplicates were either
   byte-identical to the restored root copy or (one case) a strict subset of it, so they were
   removed by hand (`rm`), matching the established remedy in
   `docs/staging/done/WORKER_FINDING_THE_TWO_ROOMS_REPAIR_RECURRED_A_THIRD_TIME_WITH_ORIGIN_RESTORE_REFUTED_AGAIN_2026-10-12.md`.
   `background/staging_two_rooms_repair` and `finding_classes --check` both read clean afterward.

2. **5 paths, INITIALLY MISREAD AS A RACE — corrected below.** The `WORKER_FINDING_REPEATING_ALARM_{DEADMAN_LAUNCH_ARTEFACT_UNLANDED,DEADMAN_ORIGIN_FORK,DEADMAN_WORKTREE_UNDECLARED,SEAT_CLAIM,SEAT_CONTINUITY}*.md`
   families were live-modified locally (counts incrementing day-by-day through 2026-10-12, two of
   the five touched within 15 minutes of this tick) while `c6542f76e` retired each one's older
   dated instance out of the staging root into `docs/staging/done/`. **My first conclusion — that
   forcing the merge would race the next `alarm_repetition` firing and re-dirty the tree within
   minutes — was wrong, and I sent a corrective NTFY once I checked the mechanism instead of
   reasoning from the symptom.** `background/alarm_repetition.py`'s own `escalate()` /
   `_live_finding_for()` search only the staging root and `in_progress/`, **never** `done/` (the
   rule is stated at L1133/L1179-1182/L1598 of that module, and is deliberate — the module's own
   comment calls a post-archive re-occurrence "an R3 two-strike signal"). So once `c6542f76e`'s
   archival lands, the next firing for each of these five families will not find a live document
   at the old root path and will file a FRESH dated one instead of rewriting the archived file —
   it cannot collide with origin's disposition a second time. The 5 paths are exactly as lossless
   as the 32: preserve the local diff (the `origin_reconcile` preservation ref already does this on
   every run) and let origin's copy supersede.

## What this means for the wedge

Both halves of the real collision are safe to resolve by restoring to HEAD/origin and letting the
merge proceed; nothing here should have held up a fast-forward once correctly diagnosed. By the
time this was confirmed, another lane (an isolated-worktree delivery-seat session, drawn on the
same subject — `the-shared-checkout-reaches-origin-so-the-weekly-publish-lands`) had already
pushed several further base-advance merges to `origin/main` and that tree already carries the
five alarm families archived to `docs/staging/done/` under their 2026-09 dates — so the corrected
bucket-(b) analysis above was overtaken by a landing, not left undone. This document exists so the
next reconcile attempt does not re-derive the rename-blindness or the false-race read from
scratch.

## Still open

- `background/origin_reconcile.py`'s collision census should use `--no-renames --name-status` (or
  `--diff-filter`) so its own remedy text stops mislabelling a deletion as a modification — it
  printed "land or revert the N MODIFIED paths" for population 1 above, which was actually all
  deletions, and the correct door (`git checkout HEAD --`) is not the one the message names
  (`tools/refresh_to_head`, which refuses a missing copy).
- The 31-of-32 byte-identical `done/` duplicates removed by hand in population 1 are evidence that
  local, uncommitted staging-triage drafts can sit for days without being swept or noticed by any
  control until a `git checkout HEAD --` on the root twin exposes the TWO-ROOMS collision. Nothing
  currently scans for an untracked `done/` copy with no corresponding root deletion in the index.

## WORK THIS CREATES

1. Give `origin_reconcile`'s collision census a precise (deletion vs modification vs
   both-deleted) split instead of raw `--name-only`, and correct its printed remedy per path shape
   accordingly.
2. A periodic sweep (or a leg on `staging_two_rooms_repair`) that flags an untracked
   `docs/staging/done/<name>` with no corresponding index change at `docs/staging/<name>`, since
   that is exactly the orphaned-draft shape found in population 1 above.

NEXT: none -- the merge this finding concerns has already advanced past this tick on a
different lane; nothing here is still owed to that landing
