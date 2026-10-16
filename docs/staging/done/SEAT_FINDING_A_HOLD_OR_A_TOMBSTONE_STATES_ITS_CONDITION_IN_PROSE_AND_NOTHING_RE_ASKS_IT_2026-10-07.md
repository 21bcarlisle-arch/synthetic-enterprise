**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A hold or a tombstone states its condition in prose, and nothing re-asks it

**Fate (2026-10-16, hold leg):** DONE for atoms -- 56d7cf77b's control (`tests/background/test_a_hold_is_re_asked_when_the_atom_it_names_is_done.py`) holds a moved-premise fixture and fails when the hold goes unlisted. The commit-reachability leg is NOT built; measured at origin a5f02f869, all 7 shas named in the 32 held rows are already on origin and cited as evidence, so it has no live instance. A hold that awaits an unlanded commit would go unre-asked. `wrong_triage.yaml` row set already_fixed.
**Fate (2026-10-16):** DONE, tombstone leg tightened -- the 2026-10-15 evidence was a LEDGER landing, which `--landed` writes for a worktree commit before promotion, so a row could still be retired on work origin never received. `delivery_lane.focus_tombstone_refusal` now needs a commit on origin/main that `_binds_item` credits to the id (or a spent premise); a refused row stays live, its ledger row carries `tombstone_refused`, and the brief lists it as "retired without a landing". Control: `test_a_focus_row_is_tombstoned_only_when_a_commit_on_origin_binds_it`. `wrong_triage.yaml` row `a-tombstone-retires-a-row-without-checking-its-done` set already_fixed.
**Fate (2026-10-15):** DONE -- both defects closed 2026-10-15: holds are re-asked in the seat's brief (background/stale_holds.py) and a focus-row tombstone needs DONE evidence (delivery_lane.focus_tombstone_refusal).
**Fate (2026-10-12, clear-the-decks):** ATOM -- no mechanism found re-grading block_reason on premise change or checking tombstone DONE before retiring a row (P3)

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Two carried items share one cause, so they share this home.*

## The cause

A held change says what it waits for ("until the retake lands", "sequenced behind B10"). A focus
row says what done means. Both are written as prose. When the premise moves, nothing re-reads the
condition, so a hold outlives its reason and a row can be retired with its DONE unmet.

## The two defects

1. **A hold is not re-asked when its premise moves.** `a15532730` and `1ff7b68b3` held "until the
   retake lands" after `57d15843d` had recorded that the retake could not be admitted. C29's
   `block_reason` said "sequenced behind B10" for five weeks after B10 reached its target
   (`15a9703ae`, 2026-08-30). That stale hold kept PB4 off L3. The instance was fixed by hand in
   `59c53d8a7`. Carried as `a-hold-condition-is-not-reasked-when-its-premise-moves`, 41 listings.

2. **A tombstone retires a focus row without checking its DONE.**
   `this-mondays-publish-reaches-origin` was retired at 09:31 on 2026-10-05 while its DONE (a
   publisher-written `site/data/dashboard.json` on origin) was unmet. The DONE was met later, by
   `a88fb2436`. The same shape recurred with `the-publish-collides-only-on-what-it-changed`. In
   four later tombstonings the DONE happened to be met already. Carried as
   `a-tombstone-retires-a-row-without-checking-its-done`, 16 listings.

## What done means

- A map `block_reason` that names another atom or commit is re-graded whenever that atom's level
  or that commit's reachability changes. The brief lists every hold whose named premise has
  already been met.
- A focus-row tombstone records whether the row's DONE was met on origin, and an unmet DONE is
  carried as a continuation by name rather than retired.

Both legs need a fixture whose premise has moved, and a control that fails when the hold or the
retirement survives it.
