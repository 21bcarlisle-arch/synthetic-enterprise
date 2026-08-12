# WORKER FINDING — the wedge episode closes only on an empty queue, and the queue cannot empty

**Severity:** LATENT · **Lane:** H_harness

**Filed:** 2026-08-12 · **Lane:** H_harness · **Class:** R15 — a control that cannot fire (R10:
the CLASS of an already-"closed" finding) · **Status:** DIAGNOSED, mechanism QUEUED not built
(SELF_INTERRUPT_DISCIPLINE) · **Rank proposal:** RUNG-1 successor — it is what keeps the
RUNG-1 doorbell armed.

## The headline

`observed-with-evidence` — **publishing is not stopped.** A clean publish landed at
**2026-08-12T04:17:35Z** and was pushed. The RUNG-1 PRIORITY-ZERO doorbell that funded this
tick ("wedged ~3726 min, 195 consecutive failures, BLOCKING ALL PUBLISHING") describes a
*record*, not the pipeline. The record cannot clear, because the only thing that clears it is a
condition the pipeline makes unreachable.

## Evidence, in the order it was gathered (R9)

**1. The named blocking red is already dead at HEAD.** `.publish_gate_state.json` names one
blocking test:

```
FAILED tests/tools/test_measure_publish_gate_subject_cost.py::test_the_sampler_reads_this_scopes_own_high_water_mark_from_the_kernel
```

Run in a clean `git archive HEAD` checkout of **b0120f28c** (`/var/tmp/unwedge-head-bNNOgf`),
together with the four other tests that were blocking reds earlier in this episode:

```
4 passed, 1 deselected in 3.71s
```

The sampler test collects under the gate's own marker expression (verified by `--collect-only`
with `-m 'not operational and not join_report_only and not scale_report_only'`) and passes. It
was narrowed by **bcf296936** (`git merge-base --is-ancestor bcf296936 HEAD` → true), committed
**04:52:40 BST**, i.e. *before this tick's doorbell was written*. The doorbell sent this worker
at a red that no longer existed.

**2. Every in-window failure is stamped to a commit 37 behind HEAD.** All five entries in
`failures[]` carry `git_hash: 7237c67a9`, recorded 02:48Z–03:45Z.
`git rev-list --count 7237c67a9..HEAD` → **37**, of which six are `unwedge(publish)` fixes.
The `git_hash` recorded is the *queued marker's sim-run hash* (`record_publish_gate_outcome`:
`git_hash = parse_marker(marker).get("git_hash")`), not the tree the gate tested — and the
marker queue is hours deep, so the attribution is stale by construction.

**3. A clean publish landed and the wedge state did not move.** From `sim-runner-log.md`:

```
- [2026-08-12 04:17 UTC] [process_run] Moved run_complete_20260811T235415Z.md to done/
- [2026-08-12 04:17 UTC] [process_run] Provenance: Verified 2026-08-12T04:17:35Z · showing run run_output_7237c67a9_20260811T235415Z.json
- [2026-08-12 04:17 UTC] [process_run] Committing and pushing (net=£1,526,252)
```

→ commit `72e8c2935 Auto-process run complete: report + LATEST.md + site/ (git=7237c67a9, net=£1,526,252)`.

Read at 04:42Z, *after* that publish, the state file still said:

```
wedge_since       2026-08-09T14:30:09Z
episode_failures  195
alerted_at        2026-08-12T03:45:35Z
failures          [5 entries]
```

No `Publish gate recovered -- cleared wedge state, re-armed alarm.` line appears anywhere after
04:17Z.

## The mechanism

`process_run_complete.py::record_publish_gate_success` (≈3915):

```python
pending = (pending_run_complete_markers() if markers_pending is None else markers_pending)
episode_closed = (pending == 0)
```

Only `pending == 0` closes the episode and zeroes `wedge_since` / `episode_failures`.

Measured against the real queue:

| | measured |
|---|---|
| markers pending in `docs/staging/` | **54** |
| span of the backlog | `20260811T225910Z` → `20260812T043511Z` |
| arrival rate (sim_runner, one per cycle) | **~10 / hour** (~5–6 min per run) |
| markers drained in the 4h35m of 2026-08-12 UTC so far | **2** (01:57Z, 04:17Z) → **~0.44 / hour** |

The drain is one gate cycle per marker, and a gate cycle is 28 min scoped (measured:
`1668.48s` at 03:44Z) up to `GATE_SUITE_TIMEOUT_SECONDS` = 2600s on the full-suite fallback.
The queue therefore grows monotonically and **`pending == 0` is unreachable**. `wedge_since` and
`episode_failures` have no reachable clearing path: the alarm half re-arms, the episode half
never does, and the RUNG-1 PRIORITY-ZERO doorbell fires on every tick for ever — as it has, at
increasing `episode_failures`, across at least six landed fixes today.

## Why this is R10, not a new instance

This is the *same construct* as
`WORKER_FINDING_A_GUARD_THAT_WAITS_FOR_A_GAP_STARVES_ON_A_FULL_QUEUE_2026-08-10.md`, which is
marked **"closed at the cause, R15 both ways."** That finding named the class exactly — *"a
control that waits for the publisher's absence has to win a race against a queue that refills
faster than it drains"* — and fixed **one** site (`_publisher_exclusion`, by taking the lock
instead of waiting for a gap). The identical wait-for-an-empty-queue construct in
`record_publish_gate_success` was left standing. R10: an absurdity-class defect may not be
closed with an instance fix; the sibling site was never swept.

It is also the second occurrence of the alarm class already recorded in
`record_publish_gate_outcome`'s own docstring — *"the alarm stayed armed for ~5960 min against a
pipeline that was working, firing a PRIORITY-ZERO doorbell each tick for a wedge that no longer
existed"* (2026-08-03). Same outcome, different unreachable predicate. **R3 two-strike: this
mechanism has now produced a false PRIORITY-ZERO doorbell twice and should be redesigned, not
patched again.**

## Recommendation (QUEUED, not built this tick — and why)

**Close the episode on a DRAINED-TO-CURRENT criterion, not on an empty queue.** The honest
question is not "is the backlog zero" — a pipeline that publishes every cycle can never answer
yes — but *"has this pipeline published cleanly at a tree no older than the one the gate
tested?"* Concretely: close the episode when a marker has been published cleanly **and** no
pending marker is older than the gate's own subject commit. That is still evidence-bearing (it
cannot be manufactured by a run that publishes nothing, which is the fail-open PW2 closed), and
it is reachable in steady state.

**Not built in this tick, deliberately.** `record_publish_gate_success` is in the publish path,
where a new write enlists every publisher test, and the guard being changed was added on purpose
to close a fail-open (PW2, 2026-08-09: a path that published nothing could zero the episode).
Getting the replacement predicate wrong disarms a real wedge alarm — strictly worse than a
noisy one. It wants its own atom with R15 mutation proof in both directions (fires on a genuine
wedge; clears on a genuinely-draining pipeline), not a rushed edit mid-episode.

## What was disposed of in this tick

Three of the eight findings the doorbell cited as "holding the suspects" self-declared FIXED and
had never been archived, so `linked_findings` — which correctly scans only the staging ROOT
(*"a finding in done/ has been dispositioned"*) — kept re-citing them at every worker. Moved to
`docs/staging/done/`:

- `WORKER_FINDING_A_GUARD_THAT_WAITS_FOR_A_GAP_STARVES_ON_A_FULL_QUEUE_2026-08-10.md`
  — its instance is closed; **its class is re-filed as this document.**
- `WORKER_FINDING_THE_CONTROL_LANDED_WITHOUT_THE_MECHANISM_2026-08-10.md`
- `WORKER_FINDING_THE_SCOPE_IS_RESOLVED_AGAINST_A_DIFFERENT_TREE_THAN_THE_GATE_RUNS_IN_2026-08-10.md`

Left in the root, each with a genuinely unbuilt half (not archived, per the standing rule
against bulk-archiving to silence a doorbell):

- `..._A_DUPLICATE_MARKER_DISARMS_THE_WEDGE_ALARM_...` — "Proposed atom (queued, not built)"
- `..._A_MEASUREMENT_TOOL_NEVER_LANDS_THE_EVIDENCE_ITS_CONTROL_READS_...` — "instance FIXED, class OPEN"
- `..._A_PHASE_WAS_STAMPED_WITH_A_COMMIT_MADE_AFTER_IT_STARTED_...` — "Pinning the pair — QUEUED, not built"
- `..._THE_DURATION_SERIES_RECORDS_ABORTED_RUNS_...` — "Disposition: QUEUED"
- `..._THE_WEDGE_ALARM_NAMED_TESTS_THE_GATE_NEVER_RAN_...` — "the free scope cross-check is NOT built"
