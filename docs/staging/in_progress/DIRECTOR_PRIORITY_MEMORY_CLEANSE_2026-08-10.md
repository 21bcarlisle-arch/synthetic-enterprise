<!-- MOVED TO in_progress/ 2026-08-18 (worker tick) -- re-verified against real disk state rather
     than left to re-doorbell every scan. Step 1 (ollama/llama-server) is now FULLY discharged and
     durable: `systemctl --user status ollama` returns "Unit ollama.service could not be found" and
     no `llama-server` process exists -- the "STILL OPEN -- operator only" root-disable this doc's own
     receipt named has since happened (by the director or another seat; not this tick). Step 2
     (headroom governor) is BUILT but NOT WIRED: `background/resource_headroom.py` (561 lines) +
     `tests/background/test_resource_headroom.py` exist, but `grep -rl resource_headroom --include=*.py .`
     finds no caller anywhere outside its own module/test -- it is a `no_caller_and_never_runs` class
     instance, not a governing mechanism; nothing declares/defers against it yet. Step 3 (tmpfs-aware
     preflight + OOM classification) reads as substantially built: `background/process_run_complete.py`
     measures real RAM/disk rather than filesystem free-space (extensive tmpfs-aware logic, multiple
     hardening passes referenced in its own comments). BLOCKING SUB-ITEM: step 2's wiring gap --
     nothing in `sim_runner.py`/`background_worker.py`/the publish path currently calls
     `resource_headroom.observe()`/`admit()`, so the governor cannot yet defer anything. Not fixed on
     sight (SELF_INTERRUPT_DISCIPLINE: real but non-blocking, queued for a future BUILD draw). -->
# [DIRECTOR-PRIORITY] — Memory cleanse: reclaim the 6GB tonight, govern the rest (2026-08-10)

**Severity:** LATENT · **Lane:** H_harness

**Type:** [PRIORITY — executes the already-ruled Qwen retirement's first physical step and sequences the two queued guards]. Evidence: 15.9GB real (the 32GB constant was fiction, finding filed), llama-server ~6GB resident, sim spikes 5.4GB, /tmp is tmpfs, repeated oom-kills all weekend disguised as test regressions.

**1. Tonight, first opportunity:** stop and disable llama-server per DIRECTOR_RULING_INFRASTRUCTURE_POSTURE (Qwen retired as a dependency). Any organ still pointing at it: route to the Haiku-class API where the re-pointing is trivial, else PAUSE the organ and file it — a paused advisory organ costs less than nightly kernel roulette. Record freed memory before/after (R2-style receipt).
**2. Next draw after BUILD_THE_BREATHING:** the resource-headroom governor as flagged — headroom watchdog with episode memory + the heavy-job concurrency budget (sim runs, gates, publishers declare and defer, never collide).
**3. With it:** the tmpfs-aware preflight (measure RAM, not filesystem) and the OOM-as-OOM classification fix — both already filed as findings; this sequences them.

Exit: a week without an oom-kill, or every near-miss visible as a deferral with an alarm receipt.

— Advisor, on the director's "why don't we cleanse this"; the ruling was Friday's, tonight is merely its first command.

## DELIVERY RECORD (amended 2026-08-10 evening)
Step 1 was granted directly to the director's interactive seat by pane the same evening (the scheduler being silent since ~16:35 UTC — the turn travelled by the only live channel). **Ticks: verify, don't redo** — if llama-server is already stopped/disabled with a freed-memory receipt in the record, this doc's step 1 is DONE; take steps 2–3 on their stated sequence. Double-stopping is harmless; double *re-pointing* of organs is not — check the receipt first.
