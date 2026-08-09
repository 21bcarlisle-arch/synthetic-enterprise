# [ADVISOR-FLAG] — Resource headroom needs a governor (2026-08-09)

**Type:** [REQUIREMENT — problem, not mechanism]. Director-prompted after tonight's OOM. Evidence, measured not inferred: dmesg oom-kill of sim-runner's python3 at 5.4GB RSS while llama-server held ~5.8GB of 16GB and a full pre-commit pytest ran concurrently — the kernel executed an innocent (the landing commit's gate died at ~80%, no summary line), costing a landing cycle during an outage.

**Requirements:** (1) a memory-headroom watchdog — free/pressure sampled, alarmed below threshold with the standard episode memory (since-when, worst, victims if any), so the next contention window is seen before the kernel arbitrates it; (2) a heavy-job concurrency budget — sim runs, publish gates, and any future large residents declare their class, and the machine defers rather than collides (tonight's manual sim-runner stop/restart, mechanised with R2 notes); (3) the already-ruled Qwen/llama retirement is hereby priced: ~5.8GB reclaimed and most of this class deleted — worth its draw sooner for that reason alone. Falsifiable exit: a synthetic contention window produces a deferral and an alarm, never an oom-kill.

— Advisor, on the director's "do we need to monitor memory?"; the answer is yes, with teeth and a budget, not a graph.
