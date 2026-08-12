# WORKER FINDING — the wedge clears on publisher process EXIT, not on the gate's recorded pass

**Severity:** LATENT · **Lane:** H_harness

**Found:** 2026-08-12, worker tick drawn on the RUNG-1 publish-gate wedge doorbell (~4508 min).
**Class:** a state record whose clearing is coupled to a PROCESS LIFECYCLE rather than to the
evidence it claims to summarise. Sibling of
`WORKER_FINDING_THE_WEDGE_RECORD_CITED_A_TEST_THAT_NO_LONGER_EXISTS_2026-08-12.md` — that one is
about the record being STALE IN CONTENT; this one is about it being STRUCTURALLY UNABLE TO CLEAR
while the healthy path is mid-flight.
**Disposition:** QUEUED (SELF_INTERRUPT_DISCIPLINE). **Not blocking** — publishing is working;
this costs a priority-zero doorbell per tick, not the publish. **Rank requested:** backlog.

## Observed-with-evidence

At 17:56 UTC, with HEAD `999517203`:

| record | value | written |
|---|---|---|
| `.last_tested_hash` | `62818325d` | **17:34:52 UTC** |
| `.publish_gate_state.json` | 4 failures, `alerted_at` set, `episode_failures: 201` | **17:05:01 UTC** |
| `pending_run_complete_markers()` | `0` | live |
| `docs/status/LATEST.md` | `Last updated: 2026-08-12T17:34:53Z` | 17:34 |
| HEAD commit | `999517203` *"Auto-process run complete … net=£1,526,252"* | 17:34:53 |

`.last_tested_hash` has exactly one writer — the gate's own rc=0 (`LAST_TESTED_HASH_CONTRACT`).
So **the gate passed at `62818325d` at 17:34:52**, published one second later, and drained the
queue to zero. For the **22 minutes since**, the wedge record has continued to read RED and the
RUNG-1 doorbell has continued to fire priority-zero.

## Why it cannot clear

`record_publish_gate_success()` is never called directly. Its sole live caller is
`record_publish_gate_outcome(marker, rc)`, and that is invoked from
`sim_runner.py:242` / `background_worker.py:445` — both **after the publisher subprocess returns**:

```python
result = subprocess.run(...)          # the whole publish cycle
_record_publish_gate_outcome(marker, result.returncode)
```

The publisher for `run_complete_20260812T170601Z.md` (PID 458301) has been alive **46 minutes**
and is still running — its child PID 484054 is executing a *further* content gate. It committed
and pushed at 17:34; it simply has not exited.

So the clearing evidence (`.last_tested_hash` matching the marker's hash) has been on disk and
correct since 17:34, and the function that reads it — `_green_is_on_record_for()` — will return
True the moment it is asked. **Nothing asks it until the process exits.**

The asymmetry: `record_publish_gate_failure` is reached per-cycle from inside the publisher, but
success is only ever routed from outside it, at exit. A publisher that fails fast reports
promptly; a publisher that succeeds and then keeps working stays silent for as long as it works.

## Why this is not the same finding as the stale-test one

The sibling finding shows the record's `blocking_tests` field naming a test that no longer exists.
That is repairable by guarding the field at read time. This one survives that fix: even with a
perfectly fresh `blocking_tests`, the record would still read RED for the whole duration of a
long, *successful*, multi-marker publish cycle, because no code path updates it during one.

## What it cost, measured

201 consecutive recorded failures in the episode, and the doorbell text served to this tick
asserted "no pass at HEAD `999517203`" and "BLOCKING ALL publishing" — both false at the moment
they were rendered. A tick drawn priority-zero on this spends its budget re-deriving that the
pipeline is healthy. This tick did exactly that, twice (once on a mis-built checkout of my own).

## Candidate repair (NOT applied — queued)

Call the outcome router **at the end of each marker's publish inside `process_run_complete`**,
where the pass is already known, rather than only from the parent at exit. The evidence check
(`_green_is_on_record_for`) is unchanged and stays anti-tautological, so the R15 property that
made the router trustworthy — a publish that published nothing cannot clear the alarm — is
preserved. Requires care that a mid-cycle clear cannot be reached by the lock-skip and
duplicate-marker branches, which are the two paths that legitimately exit 0 having published
nothing.

## Method note (R9)

My first reproduction of the gate was **wrong and is recorded as wrong**: I built the HEAD
checkout with `git archive | tar -x` plus a bare `git init`, which has no history, so
`git blame --line-porcelain` inside it failed and `blocked_atom_visibility --check` returned
rc=2 `PROBE UNAVAILABLE`. `stale_in()` counts any non-zero as stale, so this surfaced a phantom
`docs/design/BLOCKED_ATOM_VISIBILITY.md` red. The real gate lends its checkout the object store
via `.git/objects/info/alternates` + `git read-tree` (`_make_checkout_a_repo`), where the same
check is **rc=0**. Verified directly in the real repo: `python3 -m background.blocked_atom_visibility --check` → rc=0.
No repair was written to the tree (`repair_from` returned `repaired: []`).
