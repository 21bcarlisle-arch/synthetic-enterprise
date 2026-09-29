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

**Owed, and not this item:** the neighbour side. `sim_runner`'s cycle and the gate's pytest workers do not launch through this door, so they cannot see a declared peak. The smallest next step is to have `resource_headroom.admit()` count live `peak_mb` records (via `declared_peaks`) alongside its reservations, and to have `sim_runner` call it before a cycle. That would give `admit()` its first production caller.
