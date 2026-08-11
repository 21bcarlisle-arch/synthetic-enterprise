> **IN PROGRESS (2026-08-11 OPS2 tick).** Recommendation **A is BUILT and R15-proven**; the
> measurement this finding demanded is **IN FLIGHT and self-completing**.
>
> **STILL OPEN — the one sub-item:** `PHASE_MEMORY_MAX_MB = 8192` is a stated CEILING, not a
> derived figure. `tools/sample_gate_rss_premium.py` is measuring the real peaks into
> `docs/observability/gate_x_premium_rss.json`; when that record reaches `complete: true`,
> re-derive the ceiling from the measured `-x`-less peak and move it. **What unblocks it:** the
> sampler finishing — no wait, no launch, read the file.
>
> **What the measurement already says** (partial, `with_x` exact / `without_x` a lower bound):
> the gate's own `-x` run peaked at **3.15G**; the `-x`-less run passed **5.34G still climbing**.
> Directionally the finding's `inferred` claim is holding. It is NOT yet the finished number.
>
> **What landed:** each phase's pytest now runs inside `systemd-run --user --scope` with
> `MemoryMax` **and `MemorySwapMax=0`**, so an over-large run dies alone instead of global-OOM
> killing the box (three launches died that way, the publisher a candidate each time). A missing
> `systemd-run` BLOCKS the phase and exits non-zero rather than running it bare. The `-x` premium
> is now stated in every phase record (`subject_larger_than_the_gates`), which was consequence 2.
>
> **Measured while building, and worth more than the repair:** `MemoryMax` alone does NOT kill --
> it reclaims into this box's 4G of swap. A 300MB allocation completed inside a 128MB ceiling,
> rc=0. Dropping `MemorySwapMax=0` also survived as a mutation on a box already 3G into swap, so
> the control is now pinned by reading `memory.max`/`memory.swap.max` back from the scope's own
> cgroup rather than by a behaviour that ambient swap decides.

# [WORKER-FINDING] The measurement's subject is a LARGER suite than the gate's, and that is what OOMs the box (2026-08-11)

**Rank:** after the OPS2 exit itself (P-1) — this is the standing cause of the OPS2 criterion-1
measurement never landing, but the repair needs a decision, not a patch.
**Lane:** `H_harness` · **Class:** a harness whose subject diverges from the thing it measures.
**Filed from:** the OPS2 tick of 2026-08-11, per SELF-INTERRUPT DISCIPLINE — queued, not fixed on
sight. It is the residual left after
`WORKER_FINDING_THE_MEASUREMENT_IS_OOM_KILLED_INSIDE_ITS_OWN_WAIT_2026-08-11` was refuted.

## Observed (R9 — kernel log, `journalctl -k`, 2026-08-10 23:11:10Z)

```
Out of memory: Killed process 3272589 (python3) total-vm:12949376kB, anon-rss:12928996kB
oom-kill:constraint=CONSTRAINT_NONE ... global_oom,
task_memcg=/user.slice/.../publish-gate-subject-cost.service
```

pid 3272589 is the child of the measurement unit's python (3244117) — the BASELINE phase's
pytest — at **12.9G anon RSS on a 15.9G box**. A `global_oom`, not a cgroup-limit one.

## Why the measurement OOMs where the real gate does not (`inferred`, not yet measured)

`tools/measure_publish_gate_subject_cost.py::_argv_without_x` deliberately strips `-x`:

> *"With it, a red suite stops at the first failure, so 'duration' would be time-to-first-failure
> and the sides would not be comparable."*

That reasoning is sound **for the ratio** and it is symmetric across all three phases, so it
cannot bias warm/in-tree. But it makes the measured subject a strictly LARGER run than the one
the publish gate actually performs: `prc.publish_gate_pytest_argv` keeps `-x`, and the suite is
currently red at HEAD (the banked cold phase records `7 failed, 23249 passed`). The gate stops;
the measurement runs everything to the end and accumulates the whole session's memory.

Two consequences, both `inferred` and both testable:

1. **The OOM is a property of the measurement, not of the gate.** Every launch that reaches the
   BASELINE phase is trying to do something the production path never does.
2. **`implied_timeout_floor_2x` is therefore conservative in an unstated direction.** It sizes
   `GATE_SUITE_TIMEOUT_SECONDS` from a run of a larger suite than the gate's. Erring high is the
   safe direction here (an undersized bound wedges publishing) — but the record does not SAY it
   is doing this, and a future reader re-deriving the bound "from the measured runtime" would
   not know the number carries a `-x` premium.

Neither claim is measured yet. **Measure first** — that is the lesson the refuted finding just
taught, and it applies to this one too. The cheap check is peak RSS of one `-x` run against one
`-x`-less run of the same tests.

## Suggested shape (not built — three options, with a recommendation)

* **A. Bound the child's memory** — run each phase's pytest under `systemd-run --scope
  -p MemoryMax=…` so an over-large run is killed as *that phase's* failure rather than as a
  global OOM that takes the publisher with it. Keeps the subject as-is.
* **B. Measure the gate's ACTUAL argv, and handle the red separately** — time `-x` runs and
  compare like for like, accepting that a red suite makes the number time-to-first-failure.
  Cheapest to run, but the comparability problem `_argv_without_x` was written to solve returns.
* **C. Keep `-x` off but chunk the session** so peak memory does not accumulate.

**Recommendation: A, and state the `-x` premium in the record.** It fixes the failure that has
now killed the measurement three times without touching the ratio's comparability — which is the
one property the exit criterion actually rests on — and it makes the memory ceiling an
observation the artefact carries rather than a global OOM the next reader has to reconstruct
from the kernel log. B trades a landed property for a cheaper run; C is more machinery than the
problem warrants.

## Related

* `docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md` — the atom; this blocks its criterion 1.
* `docs/staging/done/WORKER_FINDING_THE_MEASUREMENT_IS_OOM_KILLED_INSIDE_ITS_OWN_WAIT_2026-08-11.md`
  — the refuted sibling, and why the diagnosis moved here.
* `feedback_truncated_pytest_is_an_oom_not_a_failure` · `reference_the_box_has_15g_ram_and_tmp_is_a_tmpfs`.
