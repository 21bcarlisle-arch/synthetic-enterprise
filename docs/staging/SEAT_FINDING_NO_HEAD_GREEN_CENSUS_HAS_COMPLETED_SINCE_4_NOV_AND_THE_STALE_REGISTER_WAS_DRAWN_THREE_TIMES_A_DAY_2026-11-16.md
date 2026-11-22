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

## 8. Grading §7's Q1-Q3 against the 18 Nov 03:30 census (18 Nov 08:45 GMT, claim `grade-18-nov-census-q1-q3`)

**What ran.** Nothing. The census started at 03:34:44, and `resource_headroom` **DEFERRED** it 4 seconds
later. The budget was already exhausted: 16180 MB declared (4380 MB reserved, plus
`longjob-value-test-step-6-flag1` at 11800 MB, 450 min into its 3200 declared). Adding the 11981 MB
request would have gone over the 23010 MB budget. The shared tree carried a0f591668 at the time, so
the instrument was in place. The suite never started.

| | prediction | outcome |
|---|---|---|
| Q1 | does not complete (≥ 75%) | **Held**, by deferral. That is the route §4's P1 named and §7 did not see. |
| Q2 | an early exit or kill leaves a PARTIAL row dated 18 Nov and an `rc=` line | **Not graded.** Its condition (ending without a summary for any reason other than deferral) did not occur. `runs[-1]` is still 4 Nov, and with no suite that is correct. |
| Q3 | if ≥ 1000 tests are reached, all 17 owed are reached | **Not graded.** No test ran. |

The STALE property from §3 held again. `attempts[-1]` is 03:34:48, `stale_attempts` = 2, `drawable` = 0,
and `HEAD_RED_REGISTER.md` is absent from `staging_rooms.work_queue`.

**Both GAPs stay open:** why the 17 Nov suite exited at 1h21m, and why the suite doubled (§2). Nothing
in this night's evidence bears on either one. The scheduling conflict in §5 has now taken 6 of the
last 10 nights.

**For the 19 Nov 03:31 census.** `longjob-value-test-step-6-flag1` no longer exists as a unit at
08:45, so the budget that deferred tonight's run has been freed, unless another long job declares
memory before 03:31. The same Q1-Q3 carry over unchanged to that run, together with the grader's
read list in §6. The earliest verdict is about 08:25 on 19 Nov if the run is killed at its bound,
and about 03:31 plus its runtime if it exits early.

## 9. Grading §7's Q1-Q3 against the 19 Nov 03:30 census (19 Nov 08:50 GMT, claim `grade-19-nov-census-q1-q3`)

**What ran.** Nothing. The census started at 03:30:10, and `resource_headroom` **DEFERRED** it 4 seconds
later. 13990 MB was already declared: 2190 MB reserved, plus `longjob-value-test-threshold-skip` at
11800 MB, which had run 862 min of its 1400 declared and started 18 Nov 13:08. Adding the 11981 MB
request would have gone over the 23010 MB budget. §8 expected the memory to be free once
`step-6-flag1` ended. It was not: **a different value-test job took the same 11.8 GB.** That job is
still active at 08:50.

| | prediction | outcome |
|---|---|---|
| Q1 | does not complete (≥ 75%) | **Held, by deferral again.** |
| Q2 | an early exit or kill leaves a PARTIAL row and an `rc=` line | **Not graded.** No suite ran. |
| Q3 | if ≥ 1000 tests are reached, all 17 owed are reached | **Not graded.** No test ran. |

The STALE property held a third time. `attempts[-1]` is 19 Nov 03:30:14 at `b585a3bb`, and
`runs[-1]` is unchanged.

**Both GAPs stay open:** why the 17 Nov suite exited at 1h21m, and why the suite doubled (§2). The
a0f591668 instrument has still not fired, because nothing has run since it landed.

**The record, 8-19 Nov (12 nights, from `journalctl --user -u head-green-census`).** 7 runs were
deferred (8, 9, 13, 14, 15, 18 and 19 Nov). 4 were killed at the 17400 s bound (10, 11, 12 and
16 Nov). 1 exited early (17 Nov). **None completed.** In each budget deferral, one value-test long job
held 11.8 GB.

**Stopping here, as the item said.** Waiting on the 20 Nov run will not help: the conflict is
structural. The last two value-test jobs declared 1400 and 3200 minutes and started at 13:08 and about 20:00, so on most nights one of
them overlaps 03:30.

**§5 turns into a pace proposal (seat's recommendation).** The census defers once and then gives up
for 24 hours. The minimal fix is for the census to **wait for admission rather than defer**. It would
re-ask `resource_headroom` every 30 minutes until a deadline (03:30 + 20 h, say) and run once the
long job releases its memory. That changes the census's own retry policy and nothing else. It holds
back no value-test work, it is reversible by reverting one unit, and it adds nothing on the
director's path. It is a scheduling call inside the seat's delegation, not a question for him, so
it is handed on as seat work rather than raised in `for_the_director`.

## 10. The census now waits for admission (19 Nov, claim `census-waits-for-admission-rather-than-deferring`)

**Done.** `tools/head_green_census.run_suite` no longer asks `resource_headroom.admitted` once. It
goes through `resource_headroom.queued`, the queue the commit gate and the sim runs already use. It
re-asks every `ADMISSION_POLL_SECONDS` (1800 s) until `ADMISSION_DEADLINE_SECONDS` (66 300 s, about
18.4 h after it fires). It builds its HEAD subject only *after* admission, so the commit it measures is
HEAD when the suite starts. A timeout, or a governor that raises, is still a deferral: the result
is UNPROVEN, the reason is on `--json`, and nothing pages. Nothing else is paused or rescheduled.

The deadline is derived, not chosen. The whole unit must end before the next 03:30 firing:
86 400 − 600 (timer delay) − 1800 (one poll can overshoot the deadline) − 17 400 (suite bound) − 300
(report) = 66 300. The unit's `TimeoutStartSec` went from 17 700 to 85 800 to hold the wait plus the
suite. It is installed: `systemctl --user show` gives `23h 50min`. To reverse it, copy back
`/var/tmp/head-green-census.service.before-2026-11-19`, run `daemon-reload` and revert the commit.
Controls: `test_a_refused_census_asks_again_and_runs_when_the_box_has_room` and
`test_a_census_that_waits_for_room_still_ends_before_the_next_firing`. Three mutations fire:
a one-shot ask, a raising governor that propagates, and the old 17 700 s unit.

**What it cannot fix, said before it is tried.** The census holds no reservation while it waits. So a
value-test job launched into a gap can take the gap first, and the queue does nothing about that.
The last two value-test jobs declared 1400 and 3200 *minutes*. If they run back to back, there may
be no ~12 GB gap inside 18.4 h at all.

**Pre-registration for the 20 Nov 03:30 firing (written 19 Nov, before it runs).** I predict the
journal shows one `QUEUED head_green_census` line, then one of two outcomes:
(a) admitted within the window, the suite runs, and the run ends COMPLETE or PARTIAL with a row in
the register. This is likely only if the running value-test job ends before about 22:00 on 20 Nov.
(b) `waited 66300s for room and never fitted`, naming the long job.
I give (a) about 50%. The value-test schedule is not something I can see from here. If it is (b) on
two nights running, the conflict is with launch order, not with the census's patience. The next
lever is then a `wait_as` place in the landings-style register for long-job launches, and that is
a design question to raise, not a retry to lengthen.

## 11. Grading §10 against the 20 Nov census (20 Nov 22:40 GMT, claim `grade-20-nov-census-queueing`)

**The new code ran.** The shared tree's HEAD at 03:30 was `3d75dfd74e` (reflog, 19 Nov 23:05).
`a28508648` is an ancestor of it, and the journal's first line is the new code's `QUEUED` line, not
the old `DEFERRED`. So the night tests the change.

**Outcome (a), and the 50% call went the right way.** At 03:39:06 the census logged
`QUEUED head_green_census`, naming `longjob-value-test-cut012.service` (11 800 MB declared, 417 min
in against 800). That job ended at 07:59:08. The census was admitted at its next poll. The log does
not record the admission time, so it can only be bounded at 07:59 or later. The suite ran and the
unit finished at 11:31:47 (7h52m wall clock, 8G peak). It wrote a **PARTIAL** row to the register:
6 033 tests reached, 13 owed, HEAD `19e317f44`. The longest red, `test_internal_seam_verifier::
test_current_tree_passes`, is now at 21 runs. Queueing was enough on this night. The launch-order
lever §10 held in reserve is not needed yet: §10 makes it a design question only after (b) on two
nights running, and this was not one.

**But the suite did not end at its bound. The census itself killed it.** The tail shows
`OSError: no fd` raised from `_boom` in
`tests/background/test_the_reconciler_manufactured_the_fork_it_existed_to_close.py:170`, a test that
monkeypatches `builtins.open` to prove the reconciler fails closed. The census's progress plugin
(`tools/head_census_progress.py`, 16 Nov) writes its line in `pytest_runtest_logreport`. For the call
phase, that hook fires **before** the test's teardown undoes the patch, so the plugin's `open()` was
the patched one. An exception inside a hook is an INTERNALERROR, which ends the session with the
patch still in place. `conftest.pytest_sessionfinish` then failed on the same `open`, so no summary
line was printed. Reproduced here: that module alone under `-p tools.head_census_progress` with
`HEAD_CENSUS_PROGRESS` set gives the identical INTERNALERROR, and without the plugin all 13 tests
pass. **So every census since 16 Nov that got as far as this module stopped there.** 6 033 is the
position of this module in the census's order, not a measure of the box or the bound.

**Fixed here.** The plugin binds the real `open` when it is imported (`_OPEN = open`), before any test
can patch the name. Control:
`test_a_test_that_patches_open_does_not_end_the_census` (in
`tests/background/test_a_stale_head_red_register_is_not_drawn.py`) runs a real pytest in which a
test patches `open`, then asserts there is no INTERNALERROR and that the test after it is reached.
The mutation back to the builtin `open` fails the control. After the fix, the reconciler module
passes 13/13 under the plugin.

**What this suggests about 17 Nov, not established.** §7 recorded an exit with no summary line after
1h21m, on the first night the plugin was live, and it listed INTERNALERROR as one candidate. This
defect fits that, but the 17 Nov output was discarded, so it remains a likely cause, not a shown one.
§2 (why the suite doubled) is still a GAP. A run that stops at a fixed test cannot measure it.

**Pre-registration for the 21 Nov 03:30 census (written 20 Nov 22:40, before it runs).** It depends
on the fix being on the shared tree's HEAD by 03:30, so check that first. If it is not there, the
night tests nothing about the fix.
`longjob-value-test-cut012-rep.service` is running now, so I expect `QUEUED` again (≈ 70%).
Q1: once the suite runs, the journal carries no `OSError: no fd` and no INTERNALERROR from
`head_census_progress`. Q2: the run reaches **more than 6 033** tests. Refutation of the fix is Q2
failing while the tail names the same module. Q2 failing at some *other* test that patches a builtin
the plugin uses would be the same class of defect, found at a new place. Q3 (≈ 40%): it COMPLETES with
a summary line inside the 17 400 s bound. I give this a low weight because §2's doubling is still
unexplained.

## 12. Grading §11 at 21 Nov 13:20 GMT: the night cannot test the fix (claim `grade-21-nov-census-after-plugin-fix`)

**The premise check fails, so Q1-Q3 are UNGRADED, not passed.** The shared tree's HEAD at 03:30
was `270bf6a178`. The reflog shows the last fast-forward at 20 Nov 18:03:27, and it is still at
that commit at 13:20, 60 commits behind origin/main (`bcb243e3db`). `89f5e98d3` reached origin at
22:48 on 20 Nov, so it is **not** an ancestor of the shared HEAD. The census builds its subject from
the shared HEAD (`head_subject_checkout` → `prc._head_sha()`) after admission, and it loads the
progress plugin from that subject with `-p`. So if it runs today it runs the **pre-fix** plugin.
What holds the fast-forward is `origin_reconcile.paths_blocking_fast_forward` on the shared tree:
21 paths, 16 "modified here, and origin changes it too" and 5 "untracked here, and origin adds its
own copy" (first three: `background/fork_salvage.py`, `background/live_payment_triad.py`,
`company/billing/payment_observation_consumer.py`). That is the same class as
`SEAT_FINDING_ONE_STRANDED_STAGED_EDIT_HELD_THE_SHARED_CHECKOUT_BEHIND_ORIGIN_2026-11-20.md`, but a
new episode, now 19h long. It is handed on separately (§12 hand-off), not fixed here. Those are
other lanes' edits, and this turn runs in an isolated worktree.

**The ≈70% QUEUED call was right.** The unit has been `activating` since 03:39:30, with 3.3s of CPU.
**But its one journal line names the wrong blocker.** `queued()` logs the refusal reason only at
the first poll: `landings come before experiments: 1 pending (commit gate ... pid 2062723)`. That
pid is dead and the landings register no longer holds it. At 13:17 the live refusal from
`admit('head_green_census')` is memory: `longjob-value-test-cut012-rep.service` has declared
11 800 MB and has run 1 288 of its 1 400 declared minutes, and 11 800 + 11 981 is more than the
23 010 MB budget. Anyone reading the journal alone would blame a landing. LATENT, and a one-line
fix: log the reason again whenever it changes. Not done here.

**Pre-registration for today's run, if the shared tree has not advanced before admission (written
13:20, before it runs).** Admission is expected at the first 1800s poll after the long job ends,
about 15:10-15:40. The 20 Nov run took 3h32m from admission. Prediction (≈ 85%): the suite stops
again at the reconciler module, with `OSError: no fd` and an INTERNALERROR from
`head_census_progress`, a PARTIAL row near 6 033 reached, and the register's HEAD equal to
`270bf6a178`. That would be a **positive control for §11's diagnosis** (the unfixed plugin still
fails at the same place), not a test of the fix. If it gets past 6 033 on the pre-fix plugin,
§11's diagnosis is wrong, or the test order changed, and the next grader must say which. If the
shared tree advances before admission, read the register's HEAD. If it contains `89f5e98d3`, grade
§11's Q1-Q3 as originally written.

**The first night that can test the fix is the 22 Nov 03:30 firing, and only if the shared tree has
rejoined origin by then.**

## 13. Grading §11 against the 21 and 22 Nov censuses (22 Nov 12:40 GMT, claim `grade-22-nov-census-after-plugin-fix`)

**Both nights tested the fix, so §12's positive control was never run.** §12's ≈85% prediction
(stop near 6 033 on the unfixed plugin) was conditional on the shared tree not advancing before
admission. It did advance: the reflog shows fast-forwards from 16:45:55 on 21 Nov
(`9e57aee83d`). Both runs ended exactly at the 17 400 s bound, so each was admitted 17 400 s before
it finished: 21 Nov at about 19:09:49, HEAD `6bdfe9c851` (18:23:05); 22 Nov at about 05:01:59, HEAD
`20a58061f`, which matches the register's own HEAD. `89f5e98d3` is an ancestor of both, as it is
of `cc1edf3776`, the HEAD at 03:30 on 22 Nov. The `_OPEN = open` binding is present at
`20a58061f`. The prediction is UNGRADED: its condition did not hold. It is not refuted and not
confirmed, and the unfixed plugin was never re-run as a control.

| | 21 Nov | 22 Nov |
|---|---|---|
| Queued from → admitted | 03:39 → ~19:10 (memory, per §12) | 03:31 → ~05:02 (two landings) |
| Reached / red | **29 083** / 12 | **26 456** / 10 |
| Ended | at the bound, no summary line | at the bound, no summary line |
| Peak | 12.1 G, 358 M swap | 12.6 G, 586 M swap |

- **Q1 PASS (indirect).** Neither night's journal has `OSError: no fd` or INTERNALERROR (0 of 14
  lines). Only an early exit prints the tail, so the journal alone is weak evidence. Q2 is the strong
  evidence: an INTERNALERROR ends the session, and both sessions ran until the bound killed them.
- **Q2 PASS.** Both runs got 20 000+ tests past 6 033, the reconciler module's position. §11's
  diagnosis and fix hold: that module was where the census stopped, and it no longer stops there.
- **Q3 FAIL on both nights (I gave it ≈40%).** Neither run completed. With the plugin defect gone,
  the 17 400 s bound is now the only thing stopping the census. The rate was 1.67 tests/s on 21 Nov
  and 1.52 on 22 Nov. §2's open question, why the suite doubled in duration, is now the whole
  problem.

**Where the rest goes: the speed track, not here.** `docs/operations/EFFICIENCY_BACKLOG.md` E-p4
(the suite is serial on 16 cores) and E-p5 (the progress plugin writes `report.duration`, so every
partial census ranks the suite by file) cover exactly what is left. Adding a third route would
duplicate them. E-p5 is the cheap next step: it turns tonight's partial run into the per-file
ranking §2 needs. This finding's own ask is spent. The register is fresh nightly (PARTIAL rows
dated 20, 21 and 22 Nov), and the plugin no longer cuts the run short. The item is parked to
E-p4/E-p5, not closed, because a completed census is still owed.

**Correction beside a claim, made in this commit.** `PROFILE_THREE_WORKLOADS_2026-11-22.md` said
every full attempt since 4 Nov "was cut at the bound". That is wrong for 17–20 Nov. From the 16 Nov
plugin until `89f5e98d3`, any run that reached the reconciler module died at test 6 033 on the
plugin defect (§11). 21 Nov is the first night cut at the bound. So comparing per-test rates
against early October is valid only for the 21 and 22 Nov runs.

**§12's LATENT finding still stands.** `queued()` logs its reason only once. The 21 Nov line names a
landing; the actual blocker for most of the 15.5 h wait was memory. Not fixed here.
