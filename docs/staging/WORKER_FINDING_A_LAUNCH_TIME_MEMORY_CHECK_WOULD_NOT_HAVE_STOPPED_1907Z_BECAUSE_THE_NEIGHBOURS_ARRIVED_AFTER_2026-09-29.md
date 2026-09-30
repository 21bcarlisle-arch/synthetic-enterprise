**Severity:** LATENT · **Lane:** A_strategy_governance · **Class:** `no_caller_and_never_runs`

# FINDING: the long-job launcher now refuses to share the box, but a launch-time check would not have stopped 19:07Z. The neighbours arrived 1h30m after the leg, and nothing they ran through asks.

**What landed** (claim `the-exclusivity-check-for-a-long-job-is-resident-memory-not-a-flag`):
- `background/launch_long_job.py` now takes `--peak-mb`, which is required.
  - It refuses when everything resident plus the declared peak exceeds the guest's `resource_headroom.sample()["total_mb"]`, less the existing measured `RESERVE_FOR_UNDECLARED_MB`.
  - The refusal names the smallest set of largest resident pids whose exit would make the job fit.
  - `--wait-for-pid` admits instead. That pid leaves the sum, and the unit runs `tools.wait_for --pid` before the job. Exit 0 or 2 (the pid is gone) starts the job; exit 1 (deadline) or 3 (could not look) does not.
- The launch record now carries `peak_mb`, so a later launch counts a long job at its declared peak rather than at whatever it has grown to so far.
- Five controls cover it: can refuse, admits on an empty box, a declared peak counts over current RSS, a wait admits and wraps, and an undeclared peak refuses. Each was mutation-proven red.

**Two departures from the item, on the evidence:**
1. **Daemons are counted, not exempted.** The 19:07Z neighbours were two python3 workers at 6.1 and 5.2 GiB. `sim-runner.service` is a manifest daemon whose cycles peak at 5.6–6.1 GiB, and it restarted at 18:58:51Z. An exemption for daemons would have exempted the likeliest neighbour. The small daemons cost about 0.7 GB between them.
2. **A growing job is counted at its declared peak.** The live leg `longjob-ab5-runa2c` read 3.7 GiB an hour into a run that peaks at 10.2 GiB. At current RSS a second 10 GiB leg reads as room.

**The finding.** At 19:07Z the leg was alone at launch (17:35Z), and the 6.1 and 5.2 GiB pair started around 18:50–18:55Z. A check run when the leg launched sees an empty box and admits it, correctly. What would have stopped the death is the NEIGHBOUR's launch seeing the leg at its declared peak. The launcher now does that, measured below, but only for jobs launched through it:
- `resource_headroom.admit()` has **no production caller**; only `tests/background/test_resource_headroom.py` calls it.
- `sim_runner.py` does not import `resource_headroom` at all.
- The launch records' `peak_mb` is read by `launch_long_job.declared_peaks` and by nothing else.

**Numbers at real inputs** (guest 24,032 MB, budget 23,008 MB):

| case | sum | verdict |
|---|---|---|
| box now (63 procs, 6,409 MB incl. runa2c at 4.6 GB) + 10,445 peak | 16,854 | admitted |
| 19:07Z: leg declared 10,445 + 6.1 GiB neighbour launching | 18,091 | admitted |
| …then the 5.2 GiB neighbour launching | 23,416 | **refused, names pid 1033543** |
| a second 10.2 GiB leg beside a *declared* runa2c | 22,660 | admitted, with 348 MB to spare |

The last row is honest arithmetic, and it is also the case the result record calls unshareable ("10.2 GiB is not shareable on a 24 GiB box with a 6 GiB daemon cycling beside it"). It is admitted because sim-runner between cycles holds 21 MB. So the check is only as good as the neighbours' declarations.

**DONE, as the item defined it:** the refusal half is done. "Item one's relaunch went through it" cannot be: relaunch 3 (`longjob-ab5-runa2c`) was launched at 20:49Z, before this existed, and is running now. The next relaunch through the CLI must pass `--peak-mb`. `tools/run_arms_rerun.py` has no sourced peak, so it now refuses with "undeclared peak" until its own last run supplies one; no number was invented for it. `tools/measure_publish_gate_subject_cost.py` declares `CLASS_WEIGHTS_MB["subject_cost"]`, the peak measured at its OOM kill.

**Owed — SPENT for sim-runner, 2026-09-30** (claim `the-neighbour-of-a-long-job-sees-its-declared-peak`). The owed paragraph read: *have `resource_headroom.admit()` count live `peak_mb` records (via `declared_peaks`) alongside its reservations, and have `sim_runner` call it before a cycle.* That is now done:
- `admit()` counts the declared peak of every long job that still has a process (`running_long_jobs`). A record left `live` after its job has ended holds no memory, so it is not counted; otherwise the cycle would defer forever.
- `sim_runner.main()` asks `cycle_admission()` before each cycle. A refusal is logged to the journal as `DEFERRED this cycle -- <reason naming the unit and pids>`, receipted in `heavy_job_deferrals.jsonl`, and re-asked after 300 s. If the check itself raises, the cycle defers; the loop does not crash.
- `admit()` is no longer test-only: this is its first production caller.

**A defect found on the way, and fixed in the same commit.** `declared_peaks` keyed the record's unit (`longjob-x`), but the census names the cgroup leaf (`longjob-x.service`). So `co_residence`'s declared-peak uplift matched no real resident, and the launcher's own "counted at its declared peak" leg was inert for every real launch. Its control passed because the fixture typed the `.service` suffix, which the real record never carries. The fix is keyed at `declared_peaks`, with a control that goes from `launch()`'s record to `co_residence`.

**Verdicts at real inputs** (guest 24,032 MB, budget 23,008 MB, `CLASS_WEIGHTS_MB["sim_run"]` = 13,824):

| case | declared | verdict |
|---|---|---|
| 19:07Z: leg declared 10,445 MB (3.7 GiB resident), 18,000 MB free | 10,445 + 13,824 = 24,269 | **deferred**, names `longjob-ab5-runa2b.service` pid 1033543 |
| same box, leg's process gone | 0 + 13,824 | admitted |
| today 01:25Z: `longjob-ab5-lineage-unseen` declared 11,800, pids 2141363, 2295586 | 25,624 | **deferred**. sim-runner will sit out this whole run once it loads the new code. That is intended. |

**What makes it defer is the stale-high weight, and that weight is now load-bearing.** (Measured by `se-seat-executor-9a`, confirmed here.) `weight_drift('sim_run')` reports a 24 h observed peak of 6,317 MB across 9 runs against the declared 13,824; `drifted=False` because drift is checked upward only. At 6.1 GiB the 19:07Z pair (10,445 + 6,246 = 16,691) fits the budget and would be ADMITTED. The 19:07Z death also involved a second 5.2 GiB worker that neither side declares. **Do not re-derive `sim_run` downward without a mechanism for the undeclared residents:** `admit()`'s declared leg does not count them, and its measured leg only sees memory already allocated.

**Still owed:** the gate's pytest workers do not ask either. The `publish_gate` and `census` classes have weights, but no caller asks `admit()` before starting them. Left out on purpose; this landing is about the one permanent neighbour we can name.

**Still owed — SPENT for the gate and the census, 2026-09-30** (claim `the-gate-workers-ask-admit-before-starting`). What changed:
- New `resource_headroom.admitted(job_class)`. It asks `admit()` first. On a refusal it writes the receipt to `heavy_job_deferrals.jsonl`. On admission it holds a `reservation()` for the whole job. If the check itself raises, the job is deferred, not admitted.
- `reservation()` had no production caller either. sim-runner's admission was summing a ledger nobody wrote. It now counts a running gate at its declared 1,536 MB.
- `process_run_complete.run_fast_tests` asks, via `_gate_admission`, before it makes the checkout. A deferral never starts the suite. It records `scoped_gate_unjudged` with evidence "DEFERRED by resource_headroom … <reason>" and exits through the existing unjudged refusal (rc=81). That keeps the wedge streak, so a deferral that never ends pages like a wedge, and nothing tells a reader to go hunting for a red test. The in-gate red census runs inside the gate's reservation.
- `tools.enumerate_publish_gate_reds.run_census` asks as class `census`. A refusal returns `outcome: deferred` and exits 4.
- Control: `tests/background/test_the_publish_gate_asks_admission_before_its_suite_starts.py` is one partition over admitted and refused. In the admitted case the suite sees its own reservation, and it is released afterwards. In the refused case the suite never starts, the refusal is receipted, and the cause is unjudged. The census gets a deferred-outcome test. Five mutations, each red: the gate ignores the refusal; `admitted` without the reservation; the gate never asks; no receipt; the census ignores the refusal.

**Deliberately not done:**
- The gate does **not** yield to a resident long job the way a sim-runner cycle does. At 1,536 MB it fits beside a declared 11.8 GB leg, and deferring it would hold the public surface for a whole long run.
- The gate is **not** the 5.2 GiB undeclared neighbour of 19:07Z. Its observed weight is 854 MB. That resident is still unidentified.
- `head-green-census.service` (nightly, the whole unscoped suite) has no measured weight, so it still does not ask. Measuring it comes before writing any weight for it. No number was invented.
