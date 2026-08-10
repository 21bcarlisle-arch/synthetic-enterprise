# [WORKER-REPORT] — The headroom governor is built and mutation-proven; its callers wait for the census (2026-08-10)

Against `ADVISOR_FLAG_RESOURCE_HEADROOM_GOVERNOR_2026-08-09`, sequenced by
`DIRECTOR_PRIORITY_MEMORY_CLEANSE_2026-08-10` step 2 ("next draw after BUILD_THE_BREATHING").
BUILD_THE_BREATHING is in `docs/staging/done/`, so the sequence was satisfied before drawing.

## What the tick found first (verify, don't redo)

**The ENUMERATE_THE_STACK draw was already in flight** — `tools/enumerate_publish_gate_reds.py`
(pid 3249292, `--deadline-seconds 5400`) with its no-`-x` pytest child, started by a prior tick.
It was NOT restarted or duplicated: a second census would have doubled the heaviest job on the
box while the first was still running, which is the exact defect this atom exists to prevent.

**Memory-cleanse step 1 was already delivered** with an R2 receipt
(`WORKER_RECEIPT_MEMORY_CLEANSE_STEP_1`, 5,126 MB freed, qwen unloaded). Not redone — the doc's
own delivery record warns that double *re-pointing* of organs is not harmless. Its one open
half remains operator-only (`sudo systemctl disable --now ollama.service`); `sudo` is banned by
`.claude/hooks/block_sudo.py` and hook-bypass is a WALL, so it was not attempted.

## The evidence that sized this build (measured, not inferred — R9)

| quantity | value | source |
|---|---|---|
| lifetime oom-kills | **64** | `/proc/vmstat oom_kill` — monotonic, privilege-free |
| largest victim | 9,648,484 kB anon-rss (`publish-gate-subject-cost.service`) | dmesg |
| heavy residents seen live in ONE window | 5,548 MB + 854 MB + 577 MB + 316 MB | `ps` |
| real MemTotal | **15,912 MB** — the 32 GB constant is fiction | `/proc/meminfo` |

The cost is not the crash. An oom-kill is **indistinguishable downstream from a test
regression**: the gate dies mid-suite with no summary line and the publisher records
`kind: "test_regression"`, so the next cycle hunts a bug that never existed.

## What landed

`background/resource_headroom.py` + `tests/background/test_resource_headroom.py` (18 tests):

1. **Watchdog** (`observe`) — samples `MemAvailable`, `Shmem` (/tmp is tmpfs, so those pages are
   RAM and never appear as RSS), PSI, and the oom-kill counter. Episode memory carries
   since-when, **worst** availability, and **victims** as a delta of the monotonic counter.
2. **Concurrency budget** (`admit` / `reservation`) — heavy jobs declare a class with a
   *measured* weight and are admitted or **deferred**. Every deferral writes a receipt.

**Two independent conditions, deliberately** (R15 tautology guard): the DECLARED ledger is what
this project intended to run; `MemAvailable` is what the kernel says IS running. Ledger-only is
blind to whatever never declared (a human's pytest, the agent seat); measurement-only is blind
to the job that declared 9.7 GB and has so far allocated 200 MB — the collision that has not
happened yet.

**It is a governor, not a gate.** It never reds a suite and never decides whether anything
publishes. Its only verdict is "start now" or "start later", and deferral is reversible by
waiting — which is why fail-closed does not wedge here
(`feedback_control_that_can_only_fail_wedges`).

## R15 — six mutations run for real, not asserted

| mutation | killed by |
|---|---|
| drop the declared-budget condition | `test_denies_when_the_budget_is_exhausted_though_memory_looks_free` |
| drop the measured-memory condition | `test_denies_when_memory_is_tight_though_the_ledger_is_empty` |
| undeclared class defaults to weight 0 | `test_an_undeclared_job_class_is_denied_not_treated_as_weightless` |
| unmeasurable `/proc` → assume room | `test_unreadable_meminfo_defers_rather_than_assuming_room` |
| liveness ignores `starttime` (PID reuse) | `test_pid_reuse_does_not_resurrect_a_dead_reservation` |
| naive `find(")")` stat parse | `test_liveness_survives_a_comm_containing_spaces_and_parens` |

**The sixth mutation SURVIVED on the first attempt, and the test was the defect.** The fixture's
comm was `(py test (x)` — one `)`, so `find` and `rfind` agreed and the test could not
discriminate what its own name promised. Fixture sharpened to `(py) test (x)` (the kernel
truncates comm to 15 chars but does not escape `)`), after which the mutation dies. Filed as a
lesson: a mutation that survives is as often a hole in the test as a hole in the code, and the
test name is not evidence that the fixture exercises the shape.

## What is NOT done, and what unblocks it

**Requirement (2)'s callers are not wired.** `process_run_complete`, `sim_runner` and the
census tool do not yet call `admit`/`reservation`. This is a deliberate deferral, not an
oversight:

* those are **publish-path files**, and a census enumerating every red at HEAD is running right
  now — committing into the publish path would move HEAD under it and make the census a moving
  target, which `DIRECTOR_PRIORITY_ENUMERATE_THE_STACK` forbids by name ("no instance-fixes on
  moving targets");
* a new write in the publish path enlists every publisher test in the pre-commit gate, on a box
  that is currently running the census as its heaviest job.

Confirmed safe to land now: `resource_headroom` is **not** among `publish_scope`'s six
`PUBLISH_PATH_SOURCES`, so this commit cannot perturb the in-flight subject.

**Unblocks when:** the census lands its red list. The wiring then goes in with that batch —
one publish-path touch, not two. Also still open from the cleanse doc's step 3: the tmpfs-aware
preflight (measure RAM, not filesystem) and OOM-as-OOM classification, both already filed as
findings; this module is the substrate they need
(`WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10`).

The flag doc is therefore parked in `docs/staging/in_progress/`, not archived — the mechanism is
live, the absorption is not complete, and CLAUDE.md's rule is that a genuinely-open sub-item is
parked with its blocker named rather than left to re-ring the doorbell.
