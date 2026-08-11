> **ACTIONED 2026-08-10 10:42Z, OPS2 tick.** The recommendation was taken verbatim: `--detach`
> now lives in `tools/measure_publish_gate_subject_cost.py` (`_detached_popen`,
> `start_new_session=True`), R15 both ways in `tests/tools/test_measure_publish_gate_subject_cost.py`
> (undetached arm dies under the group kill, detached arm survives; production mutation
> `start_new_session=False` reds it), and the third measurement was launched THROUGH that path:
> pid 2640105, `is_session_leader: true` in `docs/observability/publish_gate_subject_cost.json`.
> The record now heartbeats inside the wait, so a fourth death of this shape is distinguishable
> from a live wait. OPS2 exit criteria 1 and 2 remain open pending that run; the atom stays at
> level 0. See `docs/design/OPS2_PUBLISH_GATE_HEAD_CHECKOUT.md` STATUS 10:42Z.

# WORKER FINDING — OPS2's measurement died a second time, and its `setsid` fix exists nowhere in the repo

**Found:** 2026-08-10 08:43-08:47Z, during the `H_GAP_fabric_belief_truth_gap` tick (incidental — not that atom's scope).
**Disposition:** QUEUED against `OPS2_publish_gate_head_worktree`. NOT fixed on sight, NOT re-launched blind.
**Rank:** top of the OPS queue — OPS2 exit criterion 2 is the last of its five still open and this is what blocks it.

## Observed, with evidence

`3cc60f133` ("OPS2: the 50-minute measurement died leaving nothing — checkpoint it, detach it")
closed on a re-launch it recorded in its own message:

> Measurement re-launched 08:35Z, pid 2473243, HEAD af38e506c; its first checkpoint is on disk.
> The next tick READS `docs/observability/publish_gate_subject_cost.json` and fills in the design
> doc's table and section 2 — it does not start another run unless `complete` is false and no
> process is live.

I am that next tick. Both conditions for a re-launch hold, because **the run is dead and produced
nothing**:

```
$ date -u +%FT%TZ
2026-08-10T08:46:57Z
$ cat docs/observability/publish_gate_subject_cost.json
  "pid": 2473243, "started_at": "2026-08-10T08:35:15Z",
  "phases": {},  "complete": false,
  "phases_missing": ["cold_checkout", "warm_checkout", "in_tree_baseline"]
$ ps -p 2473243            # (no output)
$ ps -eo cmd | grep -i measure_publish_gate | grep -v grep   # (no output)
$ tail -2 /tmp/ops2_measure.log
[measure] HEAD=af38e506c... -- three timed runs, expect ~45-60 min total
[measure]   . waiting for the live publisher to finish before timing
```

Dead ~11.7 minutes after launch, still inside `_wait_for_quiet`, before its first phase — **the
same symptom, at the same point, as the 05:28 run OPS2 was built to fix.**

The wait did not time out and is not the cause. `QUIET_WAIT_SECONDS = 45 * 60`, and the timeout
path *logs* `! publisher still live after 2700s -- measuring anyway, flagged contended` and then
**falls through to measure anyway**. That line is absent, so the process was still polling when it
stopped existing.

## The part that is worth the finding

`3cc60f133` states the second of its two fixes as done:

> it is launched under `setsid` (session leader, reparented to init) so it outlives the tick
> that starts it.

**`setsid` appears nowhere in the repository.**

```
$ grep -rn "setsid" --include=*.py --include=*.sh --include=*.service --include=*.timer . | grep -v ./.git
   (no output)
$ grep -rn "measure_publish_gate_subject_cost" --include=*.py --include=*.sh . | grep -v ./.git
tools/measure_publish_gate_subject_cost.py:26:  Usage:  python3 -m tools.measure_publish_gate_subject_cost [--out PATH]
tools/measure_publish_gate_subject_cost.py:60:  (its own self-exclusion in the liveness scan)
   # ...and nothing else. No caller.
```

So the detach was a one-off shell invocation typed by a tick that has since exited. It is
**behaviour-determining state living outside the readable repo**, which is the thing
`OPERATIONAL_COHERENCE_DESIGN_PASS` / OPS1 names as the core IaC constraint —
*reconstruct-from-repo-alone is the test*, and this does not survive it. The harness has a
committed body and an uncommitted launch.

Two consequences, both already realised rather than hypothetical:

* **The claimed fix cannot be verified, only re-typed.** Whether the 08:35Z run actually went
  through `setsid` is not checkable from the repo — the only evidence either way is that it died
  like the run that definitely did not.
* **It is a member of the no-caller class this project has censused twice**
  (`WORKER_REPORT_NO_CALLER_CLASS_CENSUS_2026-08-09`, and the same shape found in
  `write_fabric_gap_entries`). A harness with a green test and no committed caller reads as done.

## The half that DID work, said plainly

The checkpoint fix is real and it is why this finding exists at all. The 05:28 death left two lines
in `/tmp` and nothing in the repo, and that tick could not distinguish *died in the wait* from
*never launched* from *ran and found nothing*. This time the repo itself said `complete: false`
with all three phases named — I could tell which of the three had happened without leaving the
repo. **One of OPS2's two fixes held; the other was never in the repo to hold.**

## What I did, and did not do

**Did not re-launch.** The design doc's re-launch condition is met, but re-launching it the same
way — a plain background job from a bounded invocation — reproduces the defect a third time, and
this tick would end before its first phase exactly as the last two did. Starting a ~50-minute job
I know will be killed at my own edge is not progress, it is a third identical data point.

**Recommendation, and it is one line of scope, not a design question:** give the harness a
committed launch — a `--detach` flag in `tools/measure_publish_gate_subject_cost.py` that
re-execs itself under `os.setsid()` (or a unit beside `reconcile-watch.timer`, which is already
the committed-IaC pattern in this repo) — then launch it through that. R15 both ways: a test that
the detached child's parent can exit without the child dying, and a test that the flag's absence
still runs inline. Until the launch is in the repo, "detached" is an exhortation, and
`MAKE_IT_STICK` says which of those two survives.

**Second-order, worth one line:** the dead run stamped `head_sha_at_launch: af38e506c`, which is
now two commits behind HEAD (`317a7b62f`). `_time_suite` already re-stamps `head_sha_at_run` per
phase for exactly this reason, so the harness is correct here — noting it only so the next reader
does not treat the launch stamp as the subject.
