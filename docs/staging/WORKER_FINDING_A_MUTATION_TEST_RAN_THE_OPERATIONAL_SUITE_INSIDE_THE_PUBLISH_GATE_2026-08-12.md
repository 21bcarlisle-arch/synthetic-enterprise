# WORKER FINDING — a mutation test ran the whole operational suite *inside* the publish gate

**Date:** 2026-08-12 · **Lane:** RUNG-1 publish-gate unwedge (priority zero)
**Status:** FIXED + class guard landed. Wedge alarm was FALSE-ARMED; publishing was never frozen.

---

## The headline

The publish gate is **not red**. It passed at `7237c67a9` and published at **04:17:35Z**
(commit `72e8c2935`, net £1,526,252). The RUNG-1 alarm has been armed since 2026-08-09T14:30Z
on a pipeline that works, because a gate cycle takes **40+ minutes** against a **5–9 minute**
commit interval — and the reason it takes 40+ minutes is that one of its own tests launches the
entire operational test suite as a child process.

## Evidence (R9: observed, not inferred)

Process tree read live at 04:26Z:

```
background_worker            4042974
 └─ process_run_complete      833541  (43:56 elapsed)
     └─ pytest -m 'not operational …'   855448   ← THE PUBLISH GATE's content suite
         └─ pytest -m 'operational or join_report_only or scale_report_only'   870918
```

`/proc/870918/environ` named the culprit exactly:

```
PYTEST_CURRENT_TEST=tests/controls/test_daemon_loop_mutation.py::
                    test_stall_alarm_fires_when_commit_stale_and_work_queued (call)
```

Supporting facts, each read off disk:

| Fact | Value |
|---|---|
| `.last_tested_hash` | `7237c67a9`, written **04:17:35Z** — sole writer is the gate on rc=0 |
| `.publish_gate_state.json` | **untouched since 03:45:39Z**; still `episode_failures: 195` |
| All 5 in-window failures | `git_hash: 7237c67a9` — three commits behind HEAD |
| Named blocking test | passes alone (1 passed) and in-file (116 passed) |
| That test's race | already fixed in `bcf296936`, which landed **after** `7237c67a9` |

## Mechanism

`deadmans_switch.run_cycle()` calls six `_check_*` helpers. The `dms_isolated` fixture
neutralised **four**. `_check_operational_layer_signal` was added to `run_cycle` after that list
was written and the list did not move with it — the classic *"a test isolates the paths it
thought of"*.

The signal self-throttles on `process_run_complete.OPERATIONAL_LAYER_STATE_FILE`, an **absolute
path into the real `docs/observability/`** which the fixture's `OBSERVABILITY_DIR` patch does not
reach. So the first of this file's **12** `run_cycle()` calls after each hour boundary read the
*live* throttle, found itself due, and spawned the whole operational suite — nested inside the
content gate, writing the live `.operational_layer_signal.json` from within a unit test.

Downstream consequences, all observed: ~3 GB of concurrent pytest RSS on a 15 GB box with swap
already at 2.2 GB; gate cycles outrunning the commit interval so `record_publish_gate_success`
is reached 40+ minutes late (or not at all); and test-written lines (`git=abc1234`, `git=unknown`,
`/tmp/pytest-of-rich/...` paths) landing in the real `sim-runner-log.md` — the alarm's own
evidence channel.

## Fix

**Instance:** `_check_operational_layer_signal` added to the fixture's neutralise list.

**Class (R10 — an instance fix does not close this):** the neutralise list is a hand-maintained
enumeration of *another function's* call set, and such a list rots silently. New guard
`test_dms_isolated_accounts_for_every_check_run_cycle_calls` relates the two: it reads
`run_cycle`'s **own source** for the actual call set and asserts every check is either
neutralised or explicitly allowed-to-run-for-real *with a stated reason*.

Not a tautology (R15): the expected side comes from the daemon's source, the actual side from the
fixture's constants; neither derives from the other.

**The guard earned its keep on its first run** — it immediately caught two further unclassified
checks nobody had noticed: `_check_open_mint_escalation` and `_check_drawable_undrawn_escalation`.
Both scan real primary state and both `notify(kind="real_alarm")`, so a fire would append to
`calls` and break the `assert len(calls) == 1` these tests are built on. They were quiet only by
accident of arithmetic — they need `since_commit >= 2h` and the stall tests pin their gap at
~46 min. Latent, not isolated. Now neutralised.

## R15 mutation evidence — the guard fires in all three directions

| Mutation | Result |
|---|---|
| Check in `run_cycle`, unclassified (the real defect) | **FIRED** — named both missing checks |
| Name classified but no longer called (stale/ghost) | **FIRED** |
| `run_cycle` refactored to call nothing (lost subject) | **FIRED** — refuses to be green over nothing |
| Unmutated control | **PASSES** |

## Result

`tests/controls/test_daemon_loop_mutation.py`: **20 passed in 0.96s**.
With `tests/background/test_deadmans_switch.py`: **68 passed in 0.90s**, zero operational
suites spawned. That file previously spawned a 40-minute nested suite once an hour.

## What this finding does NOT claim

- The wedge state was **not** hand-cleared. The live publisher (PID 833541) will record its own
  outcome when it exits; clearing it by hand is precisely the fail-open
  `record_publish_gate_success` defect the code already guards against.
- The 51-marker `run_complete` queue was not flushed — a publisher already holds the run lock.
  The queue was draining slowly *because* of this defect; the fix is what lets it drain.
- Deployment is by commit: the gate materialises a clean HEAD checkout each cycle, so the next
  cycle after this lands is the first to run without the nested suite.
