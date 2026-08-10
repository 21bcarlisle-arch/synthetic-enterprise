> **[IN PROGRESS — 2026-08-10] Mechanism LIVE, callers NOT wired.**
> Requirement (1) the headroom watchdog with episode memory (since-when / worst / victims from
> `/proc/vmstat oom_kill`) and requirement (2)'s admission primitive are built and
> mutation-proven in `background/resource_headroom.py` + `tests/background/test_resource_headroom.py`
> (18 tests, 6 mutations run for real). Requirement (3), the qwen/llama retirement, was
> delivered separately with an R2 receipt (5,126 MB freed).
>
> **STILL OPEN — the blocking sub-item:** `process_run_complete`, `sim_runner` and the census
> tool do not yet CALL `admit`/`reservation`, so nothing defers yet. "Consumed" is not
> "absorbed" (R17).
>
> **What unblocks it:** the in-flight `enumerate_publish_gate_reds` census landing its red list.
> Those callers are publish-path files; committing into them now would move HEAD under a running
> census (forbidden by name in DIRECTOR_PRIORITY_ENUMERATE_THE_STACK) and enlist every publisher
> test in the pre-commit gate. The wiring goes in WITH that batch — one publish-path touch.
>
> Full disposition: `WORKER_REPORT_THE_GOVERNOR_LANDED_BUT_ITS_CALLERS_WAIT_FOR_THE_CENSUS_2026-08-10.md`

# [ADVISOR-FLAG] — Resource headroom needs a governor (2026-08-09)

**Type:** [REQUIREMENT — problem, not mechanism]. Director-prompted after tonight's OOM. Evidence, measured not inferred: dmesg oom-kill of sim-runner's python3 at 5.4GB RSS while llama-server held ~5.8GB of 16GB and a full pre-commit pytest ran concurrently — the kernel executed an innocent (the landing commit's gate died at ~80%, no summary line), costing a landing cycle during an outage.

**Requirements:** (1) a memory-headroom watchdog — free/pressure sampled, alarmed below threshold with the standard episode memory (since-when, worst, victims if any), so the next contention window is seen before the kernel arbitrates it; (2) a heavy-job concurrency budget — sim runs, publish gates, and any future large residents declare their class, and the machine defers rather than collides (tonight's manual sim-runner stop/restart, mechanised with R2 notes); (3) the already-ruled Qwen/llama retirement is hereby priced: ~5.8GB reclaimed and most of this class deleted — worth its draw sooner for that reason alone. Falsifiable exit: a synthetic contention window produces a deferral and an alarm, never an oom-kill.

— Advisor, on the director's "do we need to monitor memory?"; the answer is yes, with teeth and a budget, not a graph.
