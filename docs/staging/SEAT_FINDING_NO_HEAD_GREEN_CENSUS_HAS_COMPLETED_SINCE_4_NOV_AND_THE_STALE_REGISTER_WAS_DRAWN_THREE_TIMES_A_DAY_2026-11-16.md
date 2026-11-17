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

## 6. Grading §4: not yet possible (16 Nov 22:50 GMT)

The grade was drawn about five hours before the census it grades. `head-green-census.timer` next
fires at 17 Nov 03:30:33. Its bound is 17400s, and the 16 Nov run used 4h50m wall clock, so the
earliest a verdict exists is about 08:25 on 17 Nov. Nothing here grades P1-P3.

What was checked before the run, so the grader starts from it:
- **The precondition holds.** The shared tree carries 7743cde68 (its HEAD is a60de79cda, 22:38),
  including `tools/head_census_progress.py`, and `head_green_census.pytest_argv` loads it with `-p`.
- **The register baseline at 22:50.** `docs/observability/.head_red_observed.json` has 30 runs.
  The newest is 4 Nov (b3ce2a4e, 17 red). `stale_attempts` is `[]` and `drawable` is 17. The 16 Nov
  UNPROVEN ran before the landing, so it recorded no attempt.
- **The grader reads:** `journalctl --user -u head-green-census --since '2026-11-17 03:00'`. P1 needs
  DEFERRED or a timeout line. P2 needs a `runs[-1]` dated 17 Nov that is marked partial or reached,
  with all 17 owed modules reached. P3 needs `stale_attempts` to be non-empty and
  `HEAD_RED_REGISTER.md` to be absent from `staging_rooms.work_queue`.

## 7. Grading §4 against the 17 Nov 03:30 census (17 Nov 09:20 GMT, claim `grade-17-nov-census-after-it-runs`)

**What ran.** `head-green-census` started at 03:30:33. Admission passed, so the memory governor did
not defer it. It ended at **04:52:11 after 1h21m37s of wall clock** (8.2G peak, 5.7M swap) with
`UNPROVEN: no pytest summary line`, and **no timeout line**. Pytest exited by itself, about 3.5 hours
inside its bound. The kernel log shows no OOM kill in the window. The only segfaults are weston's
rdp-backend, every few minutes, and are unrelated. Subject HEAD `67ba0b694`.

| | prediction | outcome |
|---|---|---|
| P1 | does not complete (≥ 80%), by DEFERRED (≥ 40%) or kill at bound | **Half right.** It did not complete, but by **neither named route**. A third outcome, exit without a summary, was not on my list. The part about the mechanism is refuted. |
| P2 | if killed: a PARTIAL row dated 17 Nov, all 17 owed reached | **Not graded.** Its condition did not occur. No PARTIAL row was written (`runs[-1]` is still 4 Nov), because only the timeout path read the progress stream. |
| P3 | if deferred: STALE, and not in `work_queue` | **Its condition did not occur, but its property held for this UNPROVEN.** `attempts[-1]` is 04:52:11 at `67ba0b694`, `stale_attempts` = 1, `drawable` = 0, and `HEAD_RED_REGISTER.md` is absent from `staging_rooms.work_queue`. The last "17 owed" draw was 04:46, before the attempt. 0 of the 109 worker draws since 04:53 offered it. |

**The defect this exposed.** When pytest returned on its own without a summary, `_run_admitted_suite`
returned its output to `evaluate` (UNPROVEN) and unlinked the progress stream unread. It wrote
neither the returncode nor any of the output to the journal. So the night's evidence was destroyed
three ways: the cause of the exit, the reds the run had re-observed, and how far it got (which
would have answered §2). **Fixed here.** A suite that exits with no `N passed` summary is now handled
as a kill by another route. The progress stream becomes a PARTIAL row, `observed["exited_early"]`
carries the rc into the verdict's reason, and the last 40 lines of output go to the journal.
Control: the `exits_early` leg of
`test_a_killed_suite_reports_what_it_reached_and_a_finished_one_does_not`. The mutation that drops
the branch fires on that leg only. The one-line wire in `main()` from `exited_early` to
`result["reason"]` has no test of its own.

**§2 (why the suite doubled) is still a GAP.** This run's progress was deleted, so it cannot say. The
next census that does not complete will now leave a PARTIAL row, a reached count and the output tail.

**Why pytest exited at 1h21m is unknown, and is not guessed here.** The candidates the evidence
allows: a test or fixture calling `os._exit`/`sys.exit` outside pytest's catch; an INTERNALERROR
(rc 3); a signal from another lane's process reaper (rc < 0); a crash of the interpreter. The next
journal entry tells them apart by rc and tail.

**Pre-registration for the 18 Nov 03:30 census (written before it runs).** Q1: it does not complete
(≥ 75%). Q2: if it ends without a summary for any reason other than deferral, `runs[-1]` is a PARTIAL
dated 18 Nov and the journal carries an `rc=` line. Q3: the 17 owed modules run first, so if it
reaches ≥ 1000 tests, all 17 are reached. Refutation: an early exit or kill with no PARTIAL row, or
a PARTIAL row with fewer than 17 of the owed modules in it once ≥ 1000 tests are reached.
