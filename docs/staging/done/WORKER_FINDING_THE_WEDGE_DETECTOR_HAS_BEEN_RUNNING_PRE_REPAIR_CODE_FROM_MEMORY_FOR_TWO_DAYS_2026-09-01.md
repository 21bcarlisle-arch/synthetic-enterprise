# The wedge detector has been running pre-repair code from memory for two days

*Filed 2026-09-01 by the autonomous worker, in the course of clearing the 14-failure publish-gate
wedge. Class: `publish_gate_and_wedge` (instance 56) — born archived, not staged live.*

---

## What the wedge actually was

Not a red test. Not a refusing pre-commit gate. **The push.**

Local `main` and `origin/main` forked at `5f34dfe9c`: 6 local-only commits against 23
upstream-only. Every publish cycle since regenerated the site, committed it **successfully** to
local `main`, and was then rejected by origin as non-fast-forward. The publisher reports that
correctly and in detail — `push_did_not_reach_origin`, with `origin=` and `head=` printed, and the
raw `git push` stderr quoted underneath.

The episode has two phases, and the split matters:

| Window (UTC) | Recorded outcome | What it was |
|---|---|---|
| 08-31 17:32 → 22:23 | `commit_refused` | the commit itself was refused |
| 08-31 23:51 → 09-01 02:39 | `push_did_not_reach_origin` | the fork |

Six of the fourteen failures were the fork. The other eight were something else, and nothing in
the record the drawn worker reads distinguishes them.

## The defect

`docs/observability/.publish_gate_state.json` — the artefact the RUNG-1 doorbell is generated
from — recorded every one of those fourteen failures as:

```
"kind": "commit_did_not_land",
"reason": "... the publisher's own scoped suite was GREEN and the commit was
           refused/timed out/never reached origin"
```

That sentence **does not exist in the code at HEAD**. It was removed on 2026-08-30 by
`c03455cdb` and replaced with `background/publish_cause.py`, a module written for precisely this
failure — its own docstring opens by quoting the disjunction and calling nine consecutive
unattributed episodes "not a diagnosis". The current call site writes `... was GREEN. Cause: {}
({})` with an observed cause and its evidence.

The string survives at HEAD in exactly two places: that module's docstring, quoting it as the
thing it abolished, and
`tests/background/test_a_publish_failure_names_which_of_the_three_it_was.py:161`, which asserts
it is **not** in `entry["reason"]`. That test is green.

And the live artefact written at **02:39 today** carries it.

## Why

`background/sim_runner.py` (PID 495) has been running since **Mon 2026-08-24 15:16**. The repair
landed **2026-08-30 20:05**. The daemon reaches the wedge detector through:

```python
def _record_publish_gate_outcome(marker, rc, *, kind=None):
    ...
    from background import process_run_complete as prc     # background/sim_runner.py:479
    return prc.record_publish_gate_outcome(marker, rc, kind=kind)
```

A lazy import is still a one-time import. The module object has been resident in that process
since before the repair existed, so for two days the wedge detector has been writing pre-repair
records while the repaired code sat at HEAD, on origin, and under a green test.

**The confirming observation is that one daemon runs two vintages of the same module at once.**
The publishing itself is a *subprocess* — `sim_runner.py:348` spawns
`[sys.executable, 'process_run_complete.py', marker]`, which loads from disk every cycle and
therefore runs **current** code. The outcome *recording* is the in-process lazy import above.
So the two halves disagree in the record, and the disagreement is visible in the artefacts:

- the log tail, written by the subprocess, names the cause precisely —
  `PUSH did NOT advance origin (rc=1, origin=64bea0ba0, head=d95c659e3)`, then
  `Commit/push failed (push_did_not_reach_origin)`;
- the state file, written in-process, records the same event as the abolished three-way
  disjunction.

Same daemon, same failure, same second — one half two days newer than the other. That is not an
inference from the process start time; it is the start time *and* two artefacts that can only
have been produced by different code.

This file already carries three documented "sibling half" defects, each a class closed on one
caller and left open on another: the wrapper deadline (2026-08-10, "the wedge continued for
another 3 hours after the 'fix' landed"), the stderr capture (2026-08-21, which made the
publisher's own advice to "read the log tail" structurally false), and the cached deadline
constant (2026-08-22). This is the fourth, in the same file, by the same mechanism.

**This exact class was diagnosed in this same file, eight days ago, one function above.**
`_publisher_deadline_seconds` carries a fourteen-line docstring about it: the daemon cached
`GATE_SUITE_TIMEOUT_SECONDS = 1200` during a 78-minute window when the constant was transiently
wrong, then killed every publish at 1200s for ten hours after it was corrected — *"The old body
was a lazy `from background import process_run_complete` under a docstring claiming a call-time
import kept the number current. A lazy import is still a one-time import."*

That was repaired by reading the number from disk. The repair was applied **to the instance**.
The sibling function twelve lines below it, doing the same lazy import for the same reason, was
left alone — and is the one that feeds the RUNG-1 draw. CLAUDE.md's own rule: *an absurdity is
fixed as a class, not an instance.*

## What it cost

The doorbell for this episode told the drawn worker, in bold, that there was no red test to find
and that the cause was "refused by a non-test pre-commit gate, or no verdict was reached before a
clock expired" — a two-way OR faithfully derived from the stale three-way OR in the state file.
Both arms are wrong. The third arm, dropped in the retelling, was the true one, and it is the one
the publisher had observed and named in its own log fourteen times.

The doorbell was right that running the gate's pytest argv would waste ten minutes and come back
green. It was right for the wrong reason, and it sent the worker to read the pre-commit hook
chain's refusal banner — which for the last six failures does not exist, because no hook refused.

**A stale reader turned a precisely-attributed failure into an unattributed one, and the
attribution machinery built to prevent exactly that was bypassed by a `sys.modules` entry.**

## Control status

The control is green and cannot fail on this. `test_a_publish_failure_names_which_of_the_three_it_was`
imports the module fresh and asserts on a value it computes in-process. It is a control over the
**code**; the defect is in the **process**. No test in this repository reads
`.publish_gate_state.json` and asks whether the record actually on disk was written by code that
still exists.

That is the missing leg, and it is a one-liner in shape: the live record's `reason` must satisfy
the same assertion the unit test makes. Keyed to the property (does the record match what current
code would write?), not to today's answer.

## Disposition

- **Done in this pass:** the fork itself, merged and pushed. See the merge commit's receipt.
- **Owed, and the reason it is not done here:** restarting PID 495 reloads the module and stops
  the bleeding, but it is a fix that expires the next time a daemon outlives a repair — which is
  the instance-not-class error a second time. The durable repair is a control that reads the live
  artefact, plus a route that makes a long-lived daemon pick up a changed reporting module. Both
  are more than this bounded tick should start; filed here so the next seat draws them with the
  evidence attached rather than rediscovering them from a green test.
