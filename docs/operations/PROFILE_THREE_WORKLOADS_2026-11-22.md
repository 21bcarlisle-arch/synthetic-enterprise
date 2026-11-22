# Profile of three workloads, before any speed fix (22 Nov 2026)

*Step 1 of the director's 22 Nov speed steer
(`docs/staging/advisor/done/DIRECTOR_STEER_PROFILE_FIRST_SPEED_TRACK_FOR_RUNS_GATES_AND_TESTS_2026-11-22.md`).
No code changed. The ranked rows are E-p1 to E-p6 in `EFFICIENCY_BACKLOG.md`. Fixes come one at a time,
each with a prediction, an identical-results replay and an interleaved whole-workload timing.*

**Tools.** Standard library only: `os.wait4` rusage (wall, CPU, peak RSS of a step and its children),
pytest `--junitxml` (time per test), `cProfile` (one test), `/usr/bin/time -v`. py-spy and memray are
not installed; nothing was installed, and the sandbox was not widened. Run by Opus 5.5
(`claude-opus-5-5`), Claude Code CLI 2.1.319.

**Machine state** (`background.resource_headroom.sample()`), WSL2 guest with 16 cores:
- 11:18 UTC: 24,034 MB total, 13,930 MB available, swap free 2,567 MB, PSI some 0.03, 10 OOM kills since boot.
- 11:44 UTC: 14,716 MB available, PSI some 0.28.

**This was a contended day.** Running at the same time: a value-test cut (`/var/tmp/vtn-driver`, 3.8 GB RSS),
another lane's commit gate (control set, 1.8 GB), an operational pytest run (1.2 GB), and two Claude
sessions. Wall times are therefore upper bounds; the CPU columns are the less contended reading. Repeat
on a quiet window before predicting a fix's saving to better than ±25%.

## (b) The commit gate chain, gate by gate

Each step is the exact argv `tools/git-hooks/pre-commit` runs, taken from
`tools/time_the_commit_hook_chain.py::STEPS`. The probe script is outside the repo (`/tmp/prof3w/gate_probe.py`).

**The index was not empty.** Another lane had 135 paths staged, including `site/data/customers/*`.
So the site-lane gate took its broad trigger and ran the whole `site/` suite. That is the real cost
of any commit that touches site data. Steps whose subject is the staged set are floors for a code commit.

| Step | Wall s | CPU s | Peak RSS MB | Note |
|---|---:|---:|---:|---|
| **Always-run control set** (46 files, 913 tests; run by `test_gate` on any commit staging code) | **778.4** | 797.5 | **4,918** | red on the working tree (5 tests; shared-tree state, not HEAD) |
| `site_lane_gate`, broad trigger | **699.7** | 329.4 | 879 | red: the reading-log door, cured by this commit's feed rebuild |
| `orphan_ratchet` | 18.8 | 18.6 | 758 | |
| `test_gate` selection (floor; the control set above is extra) | 18.6 | 24.1 | 726 | |
| `company_network_isolation` | 6.5 | 6.5 | 70 | |
| `annual_report_import_ratchet` | 5.8 | 5.8 | 59 | |
| `file_scope_generated_paths` | 5.2 | 5.2 | 62 | |
| `running_total_order` | 3.7 | 3.7 | 62 | |
| 16 other steps together | 2.6 | 2.6 | ≤ 79 each | each under 1 s |

**Whole-chain share.**
- **A code commit that touches no site data: about 840 s.** The control set is 93% of it.
- **A commit that also touches site data: about 1,540 s.** The site gate is 45% of it.
- The recorded whole-chain series (`commit_hook_duration.jsonl`) read 1,206 s median across six
  chains over 60 s since 1 Nov, and 1,360–1,430 s on 18 Nov. That agrees with the second case.

**Inside the control set** (763 s of test time, from junit):

| File | s | Share of control set | Share of an 840 s code commit |
|---|---:|---:|---:|
| `tests/background/test_weekly_rhythm.py` (40 tests) | **489.4** | **64%** | **58%** |
| `tests/background/test_publish_scope.py` | 57.4 | 7.5% | 7% |
| `tests/architecture/test_a_control_reads_python_as_code.py` | 27.1 | 3.6% | 3% |
| `tests/test_isolation_guards.py` | 24.2 | 3.2% | 3% |
| `tests/tools/test_pre_commit_test_gate_censused_batch.py` | 21.1 | 2.8% | 2.5% |
| 41 other files | 144 | 19% | 17% |

**The single dearest test** is `test_weekly_rhythm::test_the_friday_step_proposes_the_weeks_balance_before_the_reset`:
152 s in the set, 178 s alone. Under cProfile, 146 s of that is
`tools/work_cost_estimate.py::render_results`, the Friday *Cost per result and rework rate* section,
run against the real repo. It spawns **14,711 `git` subprocesses**: 7,959 from `_git` (93 s),
2,554 from `results_of`, 2,745 from `_commits` and 1,453 from `rework_rate`. That is one process per
commit per question. One batched `git log` is the Python-first candidate. The other Monday and Friday
tests (52, 35, 25 and 23 s, and so on) were not profiled; the same section is the first suspect.

**What it costs per week.** 15–22 Nov: 609 commits. 167 touched `.py` and so paid the control set:
about **36 h of gate wall time**. 98 touched `site/`; the share that took the broad trigger is not
known, and 98 × 700 s ≈ 19 h is the upper bound. Lanes gate in parallel, so this is wall time spent
gating, not elapsed calendar time.

## (c) The test suite

**Size.** `pytest tests/ --collect-only` (default markers): **33,609 tests** in 33 s, 1.0 GB peak.
`site/` adds 2,072 more. By directory:
- `tests/tools`: 8,899
- `tests/company`: 8,041
- `tests/background`: 6,887
- `tests/simulation`: 4,211
- `tests/saas`: 1,960
- `tests/sim`: 1,351
- `tests/architecture`: 768
- the rest: under 400 each

Harness tests (`tools` and `background`) are 47% of the count.

**The whole suite has not finished in three weeks.** The nightly census
(`head-green-census.service`, bound 17,400 s) last completed before 4 Nov. Since then every full
attempt was cut at the bound:
- 21 Nov: 29,083 tests reached, 12.1 GB peak
- 22 Nov: 26,456 tests reached, 12.6 GB peak
- 10–16 Nov: 10.8–17.2 GB peaks

*Correction (22 Nov, seat): "every full attempt was cut at the bound" holds only for 21 and 22 Nov. From
the 16 Nov progress plugin until its fix `89f5e98d3`, any run reaching the reconciler module died
at test 6 033 on an INTERNALERROR (`SEAT_FINDING_NO_HEAD_GREEN_CENSUS_..._2026-11-16.md` §11, §13).*

**The suite is serial on a 16-core machine.** pytest-xdist is not installed. The census used 6 h 56 min
of CPU over 6 h 20 min of wall time: about one core.

**Rate per test.** The last complete run (early October, recorded in `tools/head_green_census.py`) was
8,647 s for 36,179 tests, about 0.24 s per test. On 22 Nov it was 17,400 s for 26,456 tests, about
0.66 s per test. **I cannot yet say whether tests got 2.7× slower or the comparison is unfair.** The
newer runs are contended, and the census now runs the register's subjects first. Prediction, filed
before measuring: an uncontended per-file run will show that fewer than 50 files carry more than half
the time, as the control set (64% in one file) and the site suite (50% in three tests) both do.

**The site suite by file** (`pytest site/`, 2,072 tests, 694 s, 0.9 GB peak):

| File | s | Share |
|---|---:|---:|
| `site/test_every_door_element_a_reader_meets.py` | 117.7 | 17% |
| `site/test_no_published_page_scrolls_sideways_on_a_phone.py` | 116.7 | 17% |
| `site/test_no_published_page_renders_an_empty_field.py` | 116.5 | 17% |
| `site/test_the_baseline_comparison_reaches_the_reader.py` (202 tests) | 92.5 | 13% |
| `site/test_explore_second_clock.py` | 53.6 | 8% |

The first three are single tests of about 115 s each. Each renders every published page; whether
they render the same pages three times over is the question for the fix.
The site gate's docstring still says "~6s, ~164 tests"; it is now 2,072 tests and 11.6 min.

**Not measured here:** per-file time for the whole `tests/` tree. It needs one uncontended full run
with `--junitxml`: about 6 h or more, serial, and up to 12 GB. The cheapest way to get it is an
instrument, not a run. The census's progress stream (`tools/head_census_progress.py`) writes one line
per test and could carry `report.duration`. Every night's census, partial or not, would then rank the
suite by file at no extra cost. That is a code change, so it is a backlog row (E-p5), not done here.

## (a) A standard book run: queued, pre-registered, not yet measured

**Deferred on 22 Nov for memory. Queued at 13:30Z the same day.** By then the value-test cut
(`/var/tmp/vtn-driver`) and s.12g were gone (the cut died at 09:59Z on a dunning invariant). But an
annual report (4.2 GB) and the C32 2021 probe (2.7 GB) were running, and `available_mb` read 12,124 with
10 OOM kills on the guest. So the run was not started inline. It is the declared long job
`profile-book-run-cprofile` (queued in unit `longjob-profile-book-run-cprofile-queued`). It declares
`--peak-mb 11200`, which is `FLOOR_RUN_PEAK_MB` in `tools/run_value_cycle_ab.py`, the measured peak of
a full run. The launcher therefore holds it until the box has that room. At 9,000 MB it would have been
admitted with 371 MB to spare, and 9,000 was a guess.

**What runs.** The probe is `/var/tmp/profile-book-run/probe.py`, run in a detached worktree of
origin/main `c617e07d4b` at `/var/tmp/profile-book-run/tree`. It runs one
`run_phase4c(report_end=None, policy=CURRENT_POLICY)` inside `policy_scope(CURRENT_POLICY)`. That is
the control arm exactly as `tools.run_value_cycle_ab.run_value_cycle_ab` enters it: the full window
and the default book, so today's account count is recorded from `run_phase2b.CUSTOMERS` at import.
- The child runs under `cProfile`.
- The parent records the peak RSS by `os.wait4`, user and system CPU, wall time, and
  `resource_headroom.sample()` before and after.
- Output goes to `/var/tmp/profile-book-run/out/`: `cprofile.pstats`, then `cprofile_top.txt` (top 60
  by tottime and by cumulative time), and LAST `cprofile.json`.

**The tracemalloc leg is separate, and sized from this one.** No code was changed, and the run has no
month loop to hook from outside. It is ordered by term and segment (`simulation/run_phase2b.py`
builds its day list once, at line ~2330). So "snapshots at month boundaries" becomes snapshots on a
wall-clock timer, with the simulated date read from the log. Its `--peak-mb` must be this leg's
measured peak times tracemalloc's overhead. Declaring that peak before the measurement exists would be
the guess the launcher is there to refuse. It is handed on behind `cprofile.json`.

**Pre-registration (written 22 Nov 13:35Z, before any number exists):**
- P1. The peak RSS by wait4 is between 7,000 and 11,200 MB. It is one pass, against 8,400 for a
  paired floor leg and 11,200 for a three-arm floor.
- P2. The wall time under cProfile is between 150 and 500 minutes.
- P3. The top function by tottime lives in `simulation/` or `sim/` (the world's settlement and demand),
  not in `company/`. Those two trees hold at least half of all tottime.
- P4. The import (the book build at `run_phase2b` import) is under 10% of the wall time.
- P5. No single function holds more than 25% of tottime. A larger share would make it the first fix,
  ahead of E-p1 if the run is weighted by runs per week.
A refutation is recorded here as a refutation, not re-worded.

## Ranking across the three workloads (what to fix first)

Ranked by share of a whole workload, not cost per call:
1. **The Friday/Monday step tests in the control set:** 58% of every code commit's chain, about 36 h of
   gate time a week. The first suspect is `work_cost_estimate` spawning one `git` process per commit.
   Expected saving: well over half of 489 s per code commit. The prediction is to be written per fix.
2. **The site gate's three whole-site render tests:** about 350 s, which is 23% of a site commit's chain.
3. **Serial suite on 16 cores:** the suite cannot finish inside its night. Parallelising needs an
   install (pytest-xdist) and a memory budget per worker against the 12 GB serial peak. That is a
   proposal, not a step-1 action.
4. **Book run:** unranked until (a) is measured. The cProfile leg is queued (see (a)).

Item 5 of the steer (reuse a gate's verdict when the files it read are unchanged) has its numbers here:
the control set and the site gate are 93% and 45% of the chain, so they are the only gates where reuse pays.
