**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The origin-fork alarm writes into the shared tree the file that blocks the fast-forward it reports

**2026-09-30, seat lane 0, claim `shared-tree-fast-forward-blocked-by-seven-stale-working-copies`.**

The fork closed on origin at 13218de49 (ahead 0), but `origin_reconcile` logged NOT_ADVANCED. Seven
uncommitted shared-tree copies that origin also changes refused the ff-only. Here is each one, read
against both origin and the shared HEAD bc0df4b9e:

| path | shared copy | disposition |
|---|---|---|
| `docs/design/BLOCKED_ATOM_VISIBILITY.md` | generated at 06:24 over 351 atoms; origin's is over 353 | stale, refresh |
| `docs/staging/records/SEAT_PREREG_THE_AB_THAT_VARIES_THE_BOOK_NOT_THE_SEED_2026-09-30.md` | the 09:55 draft; origin is it plus one paragraph | stale, refresh |
| `tools/run_value_cycle_ab.py` | the 09:55 draft of 19ca27dbc; origin adds 47ced1cf2's run identity | stale, refresh |
| `tests/tools/test_a_book_family_redraws_…ep17.py` (untracked) | the same draft, without the seventh mutation's leg | stale, refresh |
| `docs/staging/SEAT_FINDING_THE_STRETCH_LOG_…_2026-09-30.md` (untracked) | byte-identical to origin | refresh |
| `tests/simulation/test_home_move_undeliverable_win.py` | 09-24; another fix for the same red that 48104db63 re-keyed differently. Origin's passes, 6/6 in 625s | superseded, refresh (preserved) |
| `docs/staging/WORKER_FINDING_REPEATING_ALARM_DEADMAN_ORIGIN_FORK_2026-09-15.md` | **live**. `alarm_repetition` rewrote the counts block and appended 6 instances and 6 re-asked lines. Origin appended the seat's fork disposition | 3-way merged and landed, then refresh |

**The seventh path is a mechanism, not a stale draft.** The `deadman_origin_fork` alarm fires when the
shared tree fails to advance, and each firing rewrites its own finding in the shared tree. When a
seat also records a disposition in that finding and the record reaches origin by an isolated
worktree, as it has to, the next ff-only is refused by the alarm's own write. That refusal fires the
alarm again, which rewrites the file again. It clears only because the refresh happens between a
firing and the next reconcile. A finding that an alarm owns should not be the place a seat writes
its disposition. Cheapest remedy: put the disposition in a sibling `SEAT_…` document that links to
the alarm's finding, and leave the alarm's file to the alarm.

**Also seen:** an orientation `git commit` (direction record) had been gating in the shared tree
since 15:28. When it lands on bc0df4b9e the shared tree will be 1 ahead and 20 behind, so it is a
fork again, closed by `origin_reconcile`'s merge leg rather than by the ff this item cleared. This
is the same receipt-less direction-commit shape the 13:30Z correction in the deadman finding names.

## Outcome (14:52Z)

The seven blockers are cleared, and nobody's uncommitted file other than those seven was touched.
`run_value_cycle_ab.py` went through `refresh_to_head` (it was refreshable).
`BLOCKED_ATOM_VISIBILITY.md` went through `refresh_to_head --base-wins`. Five were written by hand,
each preserved first as a blob ref under `refs/preserved/ff-block-2026-09-30/*` in the shared repo,
because the door refused them:

- **The prereg record and the deadman finding were refused with `refused_head_does_not_supersede_it`,
  and each copy was a strict line-subset of origin (0 lines only in the copy).** The stale-copy
  control reads the clock and the names, not line containment, so the one case with nothing to lose
  is the case it cannot admit. A containment leg (every line of the copy is in the base, so the copy
  is `refreshable`) would have made both enactments use the door.
- The two untracked copies were refused with `refused_no_base`, and the reason printed was "the
  fast-forward adds it; nothing needs clearing". That is wrong for `git merge --ff-only`, which
  refuses to overwrite an untracked file. Both were deleted by hand. One was byte-identical to
  origin, and the other was a line-subset apart from the call the seventh mutation's leg replaced.
- The home-move test was refused as `predates_landing_carrying_some`. The seat decided it as
  superseded, because origin's version passes 6/6 at 13218de49. Its C1b-era monkeypatch and
  `gap_ledger_path=tmp_path` are preserved in the blob ref if either one is wanted again.

As predicted above, the orientation's direction commit 876a64eeb then landed on bc0df4b9e, so the
shared tree read 21 behind and 1 ahead. Origin has not touched those three paths since bc0df4b9e.
`origin_reconcile`'s own merge was running in its isolated worktree at 14:50Z. That merge is the
route that closes it.
