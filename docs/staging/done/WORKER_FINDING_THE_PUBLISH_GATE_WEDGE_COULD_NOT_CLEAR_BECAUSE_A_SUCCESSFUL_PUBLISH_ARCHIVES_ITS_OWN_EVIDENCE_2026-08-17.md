# WORKER FINDING — the publish-gate wedge could not clear, because a successful publish archives the evidence the clear path reads

**Severity:** BLOCKING · **Lane:** H_harness · **Disposition:** FIXED IN THIS TICK (RUNG 1, publish-gate wedge)

**Discharged:** `tests/background/test_sim_runner_publish_gate_outcome.py::test_router_reads_a_marker_the_successful_publish_already_archived` and `tests/background/test_sim_runner_publish_gate_outcome.py::test_router_marker_that_is_genuinely_nowhere_still_clears_nothing`

The severity states what this tick FOUND — the wedge alarm's only clear path was unreachable in
the steady state, so it had been armed since 2026-08-09 against a pipeline that was publishing.
The discharge above is the named falsifier, mutation-proven both ways in the table below.

**Found:** 2026-08-17 scheduled worker tick, drawn as `OPS3_first_post_ruling_publish` (exit
criterion 4: "the episode counter for the publish-gate wedge returns to zero through a real pass,
never by hand").
**Subject:** `background/process_run_complete.py::record_publish_gate_outcome`.
**Class:** publish-gate/wedge — the control that stops publishing, and what it stops on.
**Measured at:** HEAD `4d490c27b` plus this tick's tree. Everything below is
`observed-with-evidence` (R9); no claim here is inferred.

## The measurement

`record_publish_gate_outcome` is the shared router every publish path feeds. On `rc=0` it refuses
to call a wedge recovered until the suite's own stamp proves a pass **for that marker's commit**:

```python
git_hash = parse_marker(Path(marker)).get("git_hash", "unknown")   # the defect
...
if rc == 0:
    if not _green_is_on_record_for(git_hash):   # False for "unknown", by design
        return "unproven"
```

That independence check is correct and stays. What was wrong is **where the hash was read from**.
A publish that SUCCEEDS archives its marker to `docs/staging/done/` as its last act, and only then
does the caller route the return code — so on the success path the handed path is *always already
gone*. `parse_marker` raised `FileNotFoundError`, the bare `except Exception: pass` left
`git_hash = "unknown"`, and `_green_is_on_record_for("unknown")` returns False by design.

**The clear path was therefore unreachable for every genuinely green publish.** Observed in
`docs/observability/sim-runner-log.md`:

```
- [2026-08-17 13:01 UTC] [process_run] Publish gate: run_complete_20260817T122429Z.md exited 0
  but no suite PASS is recorded for git=unknown -- publishing nothing is not evidence the gate
  is healthy, so the wedge streak is left exactly as it was found.
```

The three facts that make this a false negative, each read off real disk:

| fact | evidence |
|---|---|
| that marker names a real commit | `docs/staging/done/run_complete_20260817T122429Z.md` → `Git: 6a132fa61` |
| the suite really passed for it | `docs/observability/.last_tested_hash` → `6a132fa61`, mtime 12:55:12Z |
| the gate's own state never moved | `.publish_gate_state.json` mtime **10:44:21Z** — untouched by the 12:55Z pass |

So the gate passed at 12:55Z for exactly the commit the marker names, and six minutes later the
router recorded that pass as evidence of nothing.

**The cost, measured.** `episode_failures: 257` and `wedge_since: 1786285809` (2026-08-09) at a
moment when `publish_provenance.json` on the live surface reads `verification_state: "verified"`
with `showing_run == last_verified` at `6a132fa61`. The supervisor's RUNG-1 unwedge draw reads
`wedge_since` to decide ">60 min", so a **priority-zero doorbell fired every tick for eight days**
against a working pipeline — the same false-armed failure mode this router was written in
2026-08-03 to prevent, arriving through the neighbouring door.

## Why it survived the tests that exist

The four existing router tests all build their marker with `_marker(tmp_path)` — which **leaves
the file where it was handed**. Every one of them tests the failure and skip paths against a
marker that still exists, i.e. the one state the success path never has. The population the
control was measured on excluded the only case that matters (R15, wrong population).

## The fix

`_marker_git_hash()` asks the archive policy where the marker is *now* — `done/` or an exhaust
partition — exactly as `_process()` in the same module already does for the same reason. The
fail-safe direction is preserved: a marker that is genuinely nowhere, or unreadable, still yields
`"unknown"` and still clears nothing, because an unavailable check is a FAILED check (R15).

Independence is untouched: the hash still comes from the marker (written by the sim runner before
the gate ran) and the pass still comes from `.last_tested_hash` (written only by the gate's own
`rc=0`). Two sources, neither derived from the other — the fix changes which *directory* one of
them is read from, not who wrote it.

## R15 — mutation-proven both ways

| # | mutation | expected | observed |
|---|---|---|---|
| M1 | revert `_marker_git_hash` to reading the handed path only | the archived-marker test reds | **RED** — `assert 'unproven' == 'success'`, reproducing the live log line `git=unknown` verbatim; the other 11 pass |
| M2 | on "marker is nowhere", fall back to `.last_tested_hash` (fail-open) | the nowhere test reds | **RED** — `assert 'success' == 'unproven'`; the other 11 pass |

Each mutation reds **only** its own test, so neither is a tautology of the other.
Restored: **12 passed**. Neighbouring publish-path suites green — `test_publish_gate_alert` ·
`test_pw4_episode_guards` · `test_episode_monotonic_guard` ·
`test_a_duplicate_marker_is_not_a_publish` (**88 passed**); `test_process_run_complete` ·
`test_background_worker` · `test_staging_archive_policy` · `test_publish_gate_scope`
(**144 passed**).

## A second defect, found by the first and fixed with it

The archived-marker test passed its `"success"` assertion and failed its `episode_failures == 0`
assertion — for a reason that had nothing to do with the code under test. `record_publish_gate_
success` decides whether the EPISODE closes from `pending_run_complete_markers()`, which globs
`STAGING_DIR`; the module's `_isolate` fixture patched the state file, the log and
`.last_tested_hash` but **not** the staging directory. So whether that unit assertion held was
decided by how many real markers happened to be queued on the box at that second — one was
mid-publish. `STAGING_DIR` now joins the fixture, with the reason recorded there.

## What this does NOT close

The counter cannot be zeroed by hand — that is the criterion's own wording and a wall. This fix
makes the clear path *reachable*; it returns to zero when the next publish cycle routes its own
green through the repaired router (R2: committed is not running — the cycle live during this tick
had already loaded the old code). That is the observation OPS3 criterion 4 still needs.
