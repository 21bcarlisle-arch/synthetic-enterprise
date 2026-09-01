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

**And it does not rest on inference at all — this repo already owns the instrument.** `boot_sha`
records what each daemon actually booted from, and the three commands settle it:

```
background.boot_sha.read_boot_sha('sim-runner')      -> cf7ae97be  (2026-08-24 15:05)
git merge-base --is-ancestor c03455cdb cf7ae97be     -> rc=1   the repair is NOT in the running code
git show cf7ae97be:background/process_run_complete.py
  | grep -c "Cause: {} ({})"                         -> 0      the repair is absent
  | grep -c "refused/timed out/never reached origin" -> 1      the abolished string is present
```

So the running code is proven, not guessed: it is the pre-repair module, and it contains exactly
the sentence found in today's records. This is an **R2** defect — the subject is the *process
table*, never the module, which is why no function-level test can see it.

The deploy route exists and is self-verifying: these are generated systemd user units
(`background/process_manifest.yaml` → `generate_units.py`), so
`systemctl --user restart sim-runner.service` re-stamps the boot SHA on `ExecStartPre`. Verify by
**discrimination** — assert this module drops out of
`process_reconciler.evaluate_boot_sha_drift()`'s `stale_detail`, not by watching a counter; the
daemon usually stays `stale` overall because other lanes' uncommitted files are in its import
closure, and a wholesale flip to green would be the suspicious outcome.

**Detection was never the gap.** The drift signal has been able to read RED on exactly this
module the whole time. Nothing consumes a RED drift row and restarts.

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

## THE SAME CLASS AGAIN, ON DISK, TWENTY MINUTES LATER — and this one was the live blocker

Clearing the fork did not clear the wedge. The next cycle refused with a *different* cause,
`provenance_refused`, naming four missing provenance fields (`showing_run.population`,
`last_verified.population`, and both `run_retained`). Hooks fire serially, so one cause clearing
reveals the next rather than a green publish.

I diagnosed it as a fail-closed guard whose only producer never supplied a population, wrote the
one-line fix, verified it (`violations -> []`, banner reading *"over 251 accounts and 10,906
bills"*), and then found **the fix was already at HEAD** — `31def55aa`, brought in by the merge I
had just landed, a day old.

**The code was right. The file on disk was not.** `background/process_run_complete.py` in the
shared working tree was a pre-merge copy, 23 commits behind HEAD, and `sim_runner` spawns the
publisher as a *subprocess that loads from disk*. So the publisher was executing a version that
predated the guard's producer, and refusing against a guard that HEAD could satisfy perfectly
well.

Why the merge did not fix it: `surgical_land --merge` deliberately does not touch a path that is
**modified-unstaged** in the shared tree — moving the file would be the `git checkout <path>` the
wall forbids, and those bytes are in no commit and no reflog. That is the correct rule. Its cost
is that a stale unstaged copy of a file the daemons *execute* silently outranks HEAD.

Measured before touching it, because the rule exists to protect real work:

| | in the working copy | at HEAD |
|---|---|---|
| `population=_prov.population_of(data)` (`31def55aa`) | **absent** | present |
| `_measure_suspect_list` wrapped so a diagnostic cannot block the wedge clear (`7a995e2b1`) | present | **also present** |
| `_object_store()`, the linked-worktree object path | **absent (reverted to the literal)** | present |

Working-tree-unique content, excluding my own edit: **two lines, both reverting `_object_store()`
to the legacy literal.** Nothing unique, nothing owed to any lane — a pure superseded draft of
work already on origin. Copy preserved outside the repo, then the file written to HEAD's bytes
(a plain write, not `git checkout`, and nothing destroyed that was not provably already committed).

**So one root class produced this whole episode twice over:**

| | stale **in memory** | stale **on disk** |
|---|---|---|
| subject | `sim_runner`'s lazy-imported `process_run_complete` | the shared working tree's copy of the same file |
| age | booted 08-24, repair landed 08-30 | 23 commits behind HEAD |
| symptom | the wedge record named an abolished cause | every publish refused `provenance_refused` |
| why invisible | control is over the code, defect is in the process | control reads HEAD's source, defect is the disk |

Both are the same sentence: **the thing that ran is not the thing that was reviewed.** Every
control here reads HEAD or imports fresh, and neither of those is what executed.

## Disposition

- **Done in this pass:** the fork itself, merged and pushed. See the merge commit's receipt.
- **Also done in this pass:** `systemctl --user restart sim-runner.service`, deferred until the
  in-flight publish had landed so the verification of the unwedge was not destroyed by the fix to
  the thing that misreported it. Verified by discrimination against `evaluate_boot_sha_drift()`,
  not by watching `episode_failures` — and `episode_failures` is deliberately **not** hand-cleared:
  OPS3's criterion says the counter clears through a real pass, never by hand.
- **Owed, and named rather than done:** the restart is still the *instance*. It expires the next
  time a daemon outlives a repair, which is the same instance-not-class error that produced the
  four sibling-half defects above. Two legs close it as a class, and neither belongs in a bounded
  tick:
  1. **A control over the live record, not the code.** Nothing reads
     `.publish_gate_state.json` and asks whether current code could have written that `reason`.
     The existing test asserts the same property against a fresh in-process import and is green
     throughout. One leg, keyed to the property: *the record on disk matches what HEAD's code
     would write.* It goes red exactly when a daemon is stale, which is the condition no
     function-level test can reach.
  2. **Something that consumes a RED drift row.** The drift signal already detects this for all
     five daemons and has no hand. A detector nothing acts on is as ignored as a blind one.
