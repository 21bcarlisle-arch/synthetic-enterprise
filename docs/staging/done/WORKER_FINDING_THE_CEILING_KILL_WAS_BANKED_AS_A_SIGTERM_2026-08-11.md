# WORKER FINDING — the ceiling kill was banked as a plain SIGTERM, and bought three relaunches

**Date:** 2026-08-11 · **Atom:** `OPS2_publish_gate_head_worktree` (owed item 1) · **Lane:** H_harness
**Class:** R15 — a control keyed to ONE syntactic form, blind to the shape the event actually takes.
**Status:** control repaired and tested; the underlying sizing question is queued, not fixed here.

## What the record said

`docs/observability/publish_gate_subject_cost.json`, phase `in_tree_baseline`, launch 14:

```
"returncode": -15, "seconds": 1425.1,
"hit_memory_ceiling": false,
"hit_memory_ceiling_basis": "observed: returncode -15 is not a SIGKILL, and this
                             inference is only ever consulted on one"
```

## What the kernel said, the same second (observed-with-evidence)

`journalctl -k`, 2026-08-11 22:57:36Z — the phase's own logged end time:

```
oom-kill:constraint=CONSTRAINT_MEMCG, ...
  oom_memcg=/user.slice/.../publish-gate-phase-318057-56440.scope,
  task_memcg=<the same scope>, task=python3, pid=412539
Memory cgroup out of memory: Killed process 412539 (python3) anon-rss:6134368kB
```

Corroboration, so this is not a coincidence of timing: `318057` in the scope name is the `pid`
this record already carries for its own launch, and that scope is the **only** cgroup-constrained
OOM on the box in the whole window (`journalctl -k --since 20:00 | grep -o 'oom_memcg=[^ ,]*' |
sort | uniq -c` → one entry).

## Why the verdict was wrong

`_looks_like_the_bound` recognised "died against its own ceiling" as `returncode == -9`. Under
`systemd-run --scope` the cgroup OOM killer takes the **fattest task in the cgroup** — here a
child at 6.1 GB, not the top-level pytest the harness waits on — and systemd then tears the scope
down, so the parent exits **-15**. The shape the discriminator was keyed to only occurs when the
kernel happens to pick the one process being timed. The ordinary shape was the one it missed.

The function's own docstring had already conceded the point — *"the exact discriminator lives in
the scope's `memory.events`, which is torn down with the scope before we can read it"* — and then
inferred anyway, from a returncode this same harness produces. **Tautology: the checked value came
from the checker's own side.**

## Why it is not cosmetic — it bought an unbounded retry loop

This field is what says *why* the phase is still owed. Labelled "not a memory kill, just a
SIGTERM", the honest next move is to relaunch. So it was relaunched, and truncated, three times:
**1302.4s, 1867.6s, 1425.1s**. Each launch costs ~40 minutes and each re-read the one cause that
would have stopped it as absent. A verdict that cannot name its own failure mode does not merely
mislabel — it funds the repeat.

## The repair (landed)

The oracle is now the **kernel**, which is independent of this harness (R15): it names the cgroup,
it outlives the scope, and neither this tool nor the suite writes it.

- `_scope_oom_killed(unit, since)` matches on the `oom_memcg=` **field**, not on the unit
  appearing anywhere in the line — a global OOM prints the whole process table, so "this scope is
  mentioned" is not evidence about this scope, and collapsing those two is the exact distinction
  the field exists to draw.
- **Fail-closed:** no unit, no `journalctl`, a non-zero exit, or a raise → `None`, never `False`.
  `None` falls back to the old returncode inference *and says so* — an unavailable check is a
  failed check, and must not render as "no OOM happened".
- The phase now banks `scope_unit` and `scope_oom_killed`, so the verdict beside them can be
  **re-derived** by a reader and by the population control instead of taken on trust. That absence
  is how the false verdict survived two launches.
- The live record's `in_tree_baseline` verdict was **re-derived, not re-measured** (`seconds` and
  `returncode` are the original run's) and carries a `verdict_corrected` note saying so.

R15 both ways, `tests/tools/test_measure_publish_gate_subject_cost.py` (104 passed):
`test_the_returncode_fallback_alone_misses_the_shape_that_actually_happened` (mutation: delete the
`kernel_oom is True` branch → reds — the state that banked three truncated baselines),
`test_the_kernel_oracle_names_this_scope_rather_than_any_oom` (mutation: match `unit in line` →
the global-OOM case reds), `test_the_phase_the_kernel_answered_says_observed_not_inferred`.

## What is still owed, and the recommendation

**The baseline is not unlucky, it is unrunnable at 8192 MB.** Corroborated independently by
`docs/observability/gate_x_premium_rss.json`: the `-x`-less run — which is exactly what this
harness times — peaked at **5.34 GB in a single process** against the `-x` run's 3.15 GB. The
phase reached the 8 GB cgroup limit with one child already at 6.1 GB. A fourth launch at this
ceiling produces a fourth truncation.

Two levers, and **I recommend the second**:

1. Raise `PHASE_MEMORY_MAX_MB` above 8192. Cheap, but this is the lever whose absence
   global-OOM-killed this box three times; the box has ~15 GB total and the publisher must survive
   alongside. The same window shows unrelated `worker-tick` processes hitting 12.9 GB and 11.1 GB
   under `CONSTRAINT_NONE`, so headroom is already thin.
2. **Size the peak first, then derive the ceiling from it** — the tool's own comment already says
   the 8192 is "a ceiling, not a derived figure … when `sample_gate_rss_premium.py` reports, this
   should be re-derived from real peaks rather than left at a round number". The sampler has since
   reported (5.34 GB, contended, truncated observation). Finish that measurement to an uncontended
   peak and set the ceiling from it.

Not taken in this tick: raising a memory ceiling on a shared box, under four live lanes, is a
blast-radius decision that deserves the measurement it is waiting on rather than a round number
chosen to make one phase finish.

Unchanged by this finding, checked: `implied_timeout_floor_2x` is still 3747 against a shipped
`GATE_SUITE_TIMEOUT_SECONDS` of 4500 (criterion 2 holds), and the phase remains ratio-ineligible
and still owed, which was already correct — a truncated run may raise a floor and may never be a
denominator.
