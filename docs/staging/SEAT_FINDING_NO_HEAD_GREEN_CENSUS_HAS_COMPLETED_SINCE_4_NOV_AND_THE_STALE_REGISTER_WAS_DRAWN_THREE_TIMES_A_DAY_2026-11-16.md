**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# No HEAD-green census has completed since 4 Nov, and the stale register was drawn three times a day (2026-11-16)

*Delivery seat, claim `the-head-red-register-is-re-rendered-or-not-drawn`.*

## 1. What the direction assumed, and what the journal shows

The direction said "find why no census since 4 Nov has rendered the register", and it asked the draw to
stop offering the register "while the register's run is older than the census's last completed run".
**That premise was wrong.** No census has completed since 4 Nov, so the register (run
`2026-11-04T07:54:02Z`, HEAD `b3ce2a4e7`, 17 red / 39152 passed) *is* the last completed run. A gate
keyed to "older than the last completed run" would never have fired. The render code was not broken.
The census had nothing to render. What `journalctl --user -u head-green-census` holds (it goes back to
8 Nov):

| night | outcome |
|---|---|
| 08, 09, 14, 15 Nov | DEFERRED by `resource_headroom`: 11981 MB requested over budget (long value-test jobs held 11.2–11.5 GB) |
| 13 Nov | DEFERRED: 10801 MB available, under the floor |
| 10, 11, 12, 16 Nov | killed at the 17400s suite bound (4h50m wall) |

Each UNPROVEN run wrote nothing, not even the fact that it had tried. So `drawable()` went on
returning 17 and the worker tick drew `HEAD_RED_REGISTER.md: 17 owed` against a count that no fix
could move.

## 2. The suite has doubled in duration, cause not established

The completed-run end stamps in the observation store climb steadily: 06:27Z (16 Oct), 07:54Z (4 Nov),
08:19Z (2 Nov). The 2 Nov run ended at about 4h49m, a few seconds inside its bound. The bound was set
on 30 Sep from a measured 8647s unscoped run, and over the same period the test count rose only about
8% (36151 → 39152 passed). **I cannot yet say why the run doubled.** The census's `SLOW` rows went to
the journal, and the journal before 8 Nov has rotated away. **GAP:** the cause of the doubling.
Candidates are a few new slow tests, contention with co-resident long jobs, or swap (the 16 Nov run
peaked at 385.8M swap). The next completed or partial run's progress stream can settle it.

## 3. What landed

- **An attempt is recorded.** `head_red_register.record_attempt` runs on every UNPROVEN census. It
  touches no test and no run.
- **A stale register is not drawn.** `stale_attempts(store)` is the set of attempts newer than the
  newest run. While it is non-empty, `drawable()` returns `[]`, the document carries a `## STALE`
  heading with each attempt's reason, and the doorbell says `STALE` instead of `N owed`.
- **A killed census keeps what it reached.** `tools/head_census_progress.py` is a pytest plugin
  loaded with `-p`. It streams one line per test. On timeout, `record(reached=...)` writes a PARTIAL
  run and clears only tests the run executed. A red the run never reached keeps its state, which is
  the same property the old discard rule protected.
- **The register's own modules run first.** `HEAD_CENSUS_FIRST` names the currently-red modules, so
  a bound that cuts the tail still re-observes them. 11 of the 17 owed are in `tests/tools/`, which
  is the last directory in tree order and the one the bound cuts.

Controls: `tests/background/test_a_stale_head_red_register_is_not_drawn.py`. Seven mutations were
applied and reverted, and all seven fire. The one that first did not fire (streaming only the call
phase) was a missing test: the end-to-end leg now carries a fixture error.

## 4. Pre-registration: the 17 Nov 03:30 census (written before it runs)

This assumes the shared tree carries this landing by 03:30.
- **P1.** It is either DEFERRED (≥ 40%, given 5 of the last 9 nights) or killed at its bound. I
  predict it does not complete (≥ 80%).
- **P2.** If it is killed, the register shows a PARTIAL run dated 17 Nov at that night's subject
  HEAD, and every one of the 17 owed modules is reached, because they run first.
- **P3.** If it is deferred, the register reads STALE and `staging_rooms.work_queue` does not carry
  `HEAD_RED_REGISTER.md`.

Refutation: a 17 Nov census that is killed but writes no PARTIAL row, or one that is deferred while
the register is still drawn.

## 5. Not done here

The memory-governor deferrals (5 of 9 nights) are a scheduling conflict between the census and the
long value-test jobs. That is a pace decision over the shared box. I have not changed it.
