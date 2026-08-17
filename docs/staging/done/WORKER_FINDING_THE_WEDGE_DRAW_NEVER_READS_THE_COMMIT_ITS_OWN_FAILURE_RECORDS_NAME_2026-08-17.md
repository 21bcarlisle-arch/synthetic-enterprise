# WORKER FINDING — the wedge draw never reads the commit its own failure records name

**Severity:** LATENT · **Lane:** H_harness · **Disposition:** QUEUED (not fixed on sight)

**Found:** 2026-08-17 11:08 UTC worker tick, by taking the RUNG-1 doorbell at face value and
then checking it against disk (R7).
**Subject:** `background/supervisor.py::_publish_gate_wedge_active`, lines 3069–3102.
**Class:** an instrument that cannot see that the world moved after it took its reading.
**Measured at:** HEAD `01b283845`. Everything below is `observed-with-evidence` (R9); the one
inference is labelled as such.

## The measurement

The doorbell that woke this tick said, at priority zero:

> the publish gate has been FAILING for ~11318 min (4 failures in-window, **no pass at HEAD
> 01b283845**) and is BLOCKING ALL publishing

Every clause is literally true. What it describes is not what was on disk.

**The four in-window failures were all recorded at a commit that is no longer HEAD.**
`docs/observability/.publish_gate_state.json` this tick:

```json
{"git_hash": "1ffe5e219", "kind": "test_regression", "rc": 1, "reason": "process_run_complete rc=1 on run_complete_20260817T102732Z.md", "ts": 1786962760.5}
{"git_hash": "1ffe5e219", ... "run_complete_20260817T102732Z.md", "ts": 1786963006.7}
{"git_hash": "1ffe5e219", ... "run_complete_20260817T103340Z.md", "ts": 1786963118.3}
{"git_hash": "1ffe5e219", ... "run_complete_20260817T103942Z.md", "ts": 1786963461.2}
```

`git log --oneline 1ffe5e219..HEAD`:

```
01b283845 unwedge(publish RUNG1) the gate never ran -- a top-level import in a module both
          daemons launch AS A SCRIPT PATH killed every publish at line 16 ...
0a3b39ee9 close(H_harness BLOCKING) the publish path swallowed 199 crashes ...
```

So the cause of all four failures had been diagnosed, fixed and committed **before the draw
fired** — and the first gate run at the fixed HEAD was **in flight at draw time**: PID 126285
(`process_run_complete.py run_complete_20260817T104521Z.md`) with child PID 130446
(`pytest -x -q ...`), started 10:54 UTC per `docs/observability/sim-runner-log.md`, still
running at 11:11 UTC. The publish path reached ~40 generator steps and the suite — for the
first time in the episode, because until `01b283845` it died at line 16 before `main()`.

**The field that would have said so is written and never read.** `process_run_complete.py:4400`
stamps every failure record with the commit it happened at:

```python
failures.append({"ts": now, "reason": str(reason), "rc": rc, "kind": kind, "git_hash": git_hash})
```

`_publish_gate_wedge_active` reads that same list three times — `len()` at :3069, `ts` at
:3088, `reason` at :3102 — and never touches `git_hash`. The only hash it reads is
`.last_tested_hash` (:3080), which answers a *different* question: "has a green been stamped
that supersedes these failures?" It has not (`1f7fafc02` is an ancestor of `1ffe5e219`,
verified with `git merge-base --is-ancestor`), so the draw fires. **That is correct.** The
defect is not that it fires.

## Why it matters, at its real size and no larger

This is not a false positive and must not be repaired as one. There is genuinely no green at
HEAD, and both R15 and Rule 0 point the same way: fail safe *toward* drawing. A repair that
suppressed the draw when the failures name an old commit would blind RUNG 1 to any wedge that
survives a commit — strictly worse than the present state.

The defect is in what the draw **says**, and it costs two concrete things:

1. **A priority-zero tick spent re-diagnosing a fixed bug.** "No pass at HEAD" reads as
   "failing at HEAD". A worker who acts on it — as instructed, at priority zero, ahead of
   every product and HARDEN lane — starts from "find the red" when the true state is "the fix
   landed 20 minutes ago and its verification is running now". This tick recovered only
   because it read the state file's `git_hash` field before starting work.

2. **The doorbell's own prescribed remedy is actively harmful in this state.** It says to run
   the gate's argv without `-x`. Doing that here would have launched a second full suite
   alongside the live one on a **15 GB** cgroup with **8 GB** available (`free -g`, this tick
   — note 15 GB, not the 32 GB of physical RAM; cf.
   `WORKER_FINDING_THE_CEILING_WAS_SIZED_FROM_A_PROCESS_AND_APPLIED_TO_A_CGROUP_2026-08-11`).
   An OOM kill of PID 126285 would have been recorded as failure #258 — a *manufactured* red,
   at the hands of the instruction meant to diagnose it. That this class of kill is
   mis-recorded as a test regression is already filed
   (`WORKER_FINDING_AN_OOM_KILL_IS_RECORDED_AS_A_TEST_REGRESSION_2026-08-10.md`), which is
   what makes the loop closeable.

*Inferred, not observed:* that some share of the 257-failure episode count reflects this
read — a worker re-entering diagnosis on already-superseded failures. Not measured here; the
per-tick record needed to attribute it was not checked, and the episode counter is not
decomposable by cause.

## The repair, stated so it cannot become a suppression

Add a clause to the returned message, in the same shape as the existing `depth_clause` and
`episode_clause` (`supervisor.py:3121–3140`) — text only, never a `return None`:

* When **every** in-window failure carries a `git_hash` that is not HEAD: say so, and name
  `git log --oneline <that hash>..HEAD` so the drawn worker sees whether a fix already landed.
  Defensive on the same rule as `cited`/`depth_clause`: a record with no `git_hash`, a mixed
  set, or an unreadable git reads as **unknown**, which prints nothing and changes nothing.
* When a `process_run_complete.py` process is **live**: say that a gate run is in flight, with
  its start time, so the remedy paragraph does not send a second suite in beside it.

Exit test (both directions, R15):

* Fires — state file with 4 failures all at `<old>`, HEAD one commit ahead: message contains
  the superseded-hash clause AND the draw is still returned (not `None`).
* Silent — same failures at a `git_hash` equal to HEAD: no clause, draw unchanged. This is the
  direction that catches the suppression regression, and it is the one that matters.

## What this tick did with it

Nothing but file it — SELF-INTERRUPT DISCIPLINE: QUEUE by default. The wedge lane's real work
this tick was the in-flight gate at HEAD, which was left alone deliberately.
