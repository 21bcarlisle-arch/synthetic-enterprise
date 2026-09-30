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
