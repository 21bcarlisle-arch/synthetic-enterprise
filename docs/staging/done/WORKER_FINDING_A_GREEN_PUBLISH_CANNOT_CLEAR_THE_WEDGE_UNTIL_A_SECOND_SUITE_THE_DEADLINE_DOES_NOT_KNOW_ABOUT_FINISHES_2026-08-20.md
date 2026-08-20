**Severity:** BLOCKING · **Lane:** H_harness
**Discharged:** `tests/background/test_publish_path_step_budgets.py::test_only_the_gate_itself_may_carry_the_gates_own_bound`,
`tests/background/test_publish_path_step_budgets.py::test_no_publish_path_step_carries_a_static_bound_over_the_allowance`,
`tests/background/test_publish_path_step_budgets.py::test_deleting_the_step_cannot_pass_as_a_repair`,
`tests/background/test_publish_path_step_budgets.py::test_the_call_graph_reaches_the_steps_it_claims_to_bound`,
`tests/background/test_publish_path_step_budgets.py::test_the_walk_excludes_what_is_not_on_the_publish_path`,
`tests/background/test_publish_path_step_budgets.py::test_the_scan_finds_the_timed_subprocesses`,
`tests/background/test_publish_path_step_budgets.py::test_the_remainder_budget_never_outlives_the_publisher_itself`,
`tests/background/test_publish_path_step_budgets.py::test_an_exhausted_budget_skips_the_suite_rather_than_running_it_unbounded`,
`tests/background/test_publish_path_step_budgets.py::test_the_exhausted_skip_never_publishes_a_false_all_clear`,
`tests/background/test_publish_path_step_budgets.py::test_the_census_and_the_remainder_share_one_definition` — 2026-08-20 worker tick, commit 6444f2778. Section 3's falsifiable prediction RESOLVED to branch b and is now observed rather than inferred: the log gained its first ever TIMED OUT processing line at 16:37Z against the green, published cycle this document names, then twice more at 18:07Z and 19:39Z. Closure items 2 and 3 are landed — the annotation derives its bound from what the publish path has LEFT, through the one primitive the census already used correctly, and the deadline control now derives its population by walking the call graph from main instead of from a hand-written enumeration that did not contain the largest post-gate step. Mutations run both ways before this record was written. See the LIMITATION section below for closure item 1, which is NOT landed.

# FINDING — the publish gate went green and published 34 minutes ago; the wedge alarm cannot be told so, because the clear is routed through a process that is still running a SECOND full suite the caller's deadline does not know exists

**Found by:** the RUNG-1 priority-zero wedge draw, 2026-08-20 16:02–16:12Z. This is the fourth
consecutive tick that doorbell has consumed (`7d5494610`, `159172f5e`, `51f710b49`, this one).
**Rank requested:** top, above the wedge doorbell itself — this IS the wedge doorbell's cause.
**Relationship to `51f710b49`:** that commit filed the READ side (the state file has no ts and no
age bound, so a stale answer launders into a confident one). This is the WRITE side: *why* the
state is stale for tens of minutes at a time, and why it may never be updated at all.

---

## 1. The publish gate is GREEN and the site is live — observed, not inferred

| claim | evidence | class |
|---|---|---|
| the gate passed for `43766e01e` | `docs/observability/.last_tested_hash` = `43766e01e`, mtime **2026-08-20 15:34:03Z**. Its sole writer is `_run_gate_in`, and only on rc=0 from the suite (`LAST_TESTED_HASH_CONTRACT`). | observed |
| the marker published | `sim-runner-log.md` 15:34Z: `Moved run_complete_20260820T090542Z.md to done/` · `Provenance: Verified 2026-08-20T15:34:03Z` · `Committing and pushing (net=£1,529,289)` | observed |
| the commit landed | `cd4da3219 Auto-process run complete: report + LATEST.md + site/ (git=43766e01e, net=£1,529,289)` | observed |
| the marker's own commit matches | `docs/staging/done/run_complete_20260820T090542Z.md` reads `Git: 43766e01e` — so `_green_is_on_record_for("43766e01e")` is **True** | observed |
| **R11, the live surface** | `curl https://poesys.net/data/dashboard.json` → **HTTP 200**, `meta.generated_at = 2026-08-20T15:07:26Z`, `meta.source_file = run_output_43766e01e_20260820T090542Z.json`, `portfolio.net_margin_gbp = 1529288.58` — byte-identical to the local artefact `cd4da3219` published | observed |

Publishing is **not** blocked. The doorbell that says it has been blocked for 483 minutes is
wrong about the present tense.

And yet, at 16:12Z, `docs/observability/.publish_gate_state.json` still reads
`wedge_since: 1787212714.6` (09:18Z), `episode_failures: 14`, three in-window failures — mtime
**15:07:13Z**, i.e. written before the gate that passed ever started.

## 2. Why the clear cannot be recorded

`record_publish_gate_success()` is reachable from exactly one place: `record_publish_gate_outcome`,
on the `rc == 0` branch. That router is deliberately owned by the CALLER (R10, one router for
every publish path) and is called by `background_worker.py:489/504` and `sim_runner.py:414` —
in both cases from `result.returncode`, i.e. **only after the publisher subprocess exits**.

The publisher has not exited. `process_run_complete.py` PID 3066953 started **15:07:14Z** and at
16:12Z is still inside `run_remainder_annotation_step` (`process_run_complete.py:5308`), whose
child pytest is PID 3132509, started **15:39:46Z**:

```
tests/ -q --tb=short -m "not operational and not join_report_only and not scale_report_only" --ignore=...
```

No `-x`, no `--maxfail` — that argv is `publish_scope.remainder_pytest_argv(publish_gate_pytest_argv())`,
and by its own contract it runs **only when the scoped gate was GREEN**. Its presence is itself
proof the gate passed.

So the sequence is: gate green → publish lands → **a second full suite runs for up to
`GATE_SUITE_TIMEOUT_SECONDS` (4500s)** → process exits → *only now* may the alarm be told the
wedge is over. The step doing the delaying is the one whose docstring says *"this observes the
publish it follows and must never be able to affect it."* It cannot affect the publish. It can,
and does, hold the alarm about the publish.

Cost as observed today: 38 minutes and counting of false priority-zero, four ticks deep.

## 3. The worse half — the publisher's declared budget cannot contain its own path (inferred, with arithmetic)

```
PUBLISH_PATH_TIMEOUT_SECONDS = GATE_SUITE_TIMEOUT_SECONDS + PUBLISH_PATH_ALLOWANCE_SECONDS
                             = 4500 + 900 = 5400s      # and background_worker._publisher_deadline_seconds() reads exactly this
```

Inside that 5400s the path runs **two** bounded suites, not one:

| step | bound |
|---|---|
| the blocking gate | `GATE_SUITE_TIMEOUT_SECONDS` = 4500s |
| the red census, if the gate is red | ≤1200s, correctly DERIVED from what is left (`red_census_budget_seconds`) |
| `run_remainder_annotation_step`, if the gate is green | `_default_remainder_runner(timeout=GATE_SUITE_TIMEOUT_SECONDS)` = **4500s**, *not* derived from anything |

The annotation's own bound is **5× the entire post-gate allowance** it lives in. For the live run:
publisher deadline = 15:07:14 + 5400s = **16:37:14Z**; the annotation believes it may run until
15:39:46 + 4500s = **16:54:46Z**. There is a **17m32s window in which the annotation still holds
budget and the caller has already killed the process.**

A kill there routes to `_record_publish_gate_outcome(marker, None, kind="deadline_kill")` →
`record_publish_gate_failure(...)`. A cycle whose gate PASSED and whose commit LANDED would be
recorded as the episode's **failure #15**, and `record_publish_gate_success` would never run for it.

**Falsifiable prediction, for the next tick to check rather than assume:** at **16:37:14Z** either
(a) the annotation finished first and `.publish_gate_state.json` shows `wedge_since: null` with
`Publish gate recovered` in `sim-runner-log.md`, or (b) `background-worker-log.md` gains its first
ever `TIMED OUT processing run_complete_20260820T090542Z.md after 5400s` and the state gains a
`deadline_kill` failure against a green, published cycle.

## 4. The control that should have caught this knows about one of the two suites

`tests/background/test_publisher_deadline_exceeds_its_gate.py` exists precisely for this — it is
the R15 file written after the 900s-vs-2600s wedge of 2026-08-10, and it pins two inequalities:

* `bw._publisher_deadline_seconds() > prc.GATE_SUITE_TIMEOUT_SECONDS` → 5400 > 4500 ✓
* `slack >= prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS` → 900 ≥ 600 ✓

Both pass. Its docstring enumerates what follows the gate — *"site regeneration, the report, the
mirror, the hook-chain commit and the push"* — and the enumeration is **hand-written and
incomplete**: the largest post-gate step is missing from it. The word `annotation` occurs exactly
once in that file, at line 48, as `from __future__ import annotations`.

This is the project's own filed shape: a control whose subject set is an author's list rather
than the population, passing because the thing it does not know about is the thing that breaks it.
The 2026-08-10 retro already generalised it once ("a THIRD caller added later reds on arrival")
— over call SITES. The gap here is over bounded STEPS inside one call site.

## 5. Proposed closure — the class, not the instance (R10), withheld this tick

1. **Record the outcome when the publish LANDS, not when the process EXITS.** The publisher calls
   the same shared router (R10 preserved — one router, not a copy) immediately after
   `git_commit_push` succeeds. The router is already idempotent and already evidence-keyed on
   `.last_tested_hash` × the marker's own hash, so nothing about what counts as proof changes;
   only *when* the question is asked. The caller's post-exit call stays and becomes a confirmation.
2. **Bound every post-gate step out of the remaining allowance, the way the census already does.**
   `_default_remainder_runner` takes a derived budget (`red_census_budget_seconds` is the existing,
   correct primitive), never `GATE_SUITE_TIMEOUT_SECONDS`.
3. **Make the deadline control read the population.** Replace the hand-list with an AST walk of
   `process_run_complete.py` for every `timeout=` on a subprocess reachable after the gate, and
   assert the sum fits the slack — so a fourth bounded step added later reds on arrival.

**R15 mutations, each on its own named defect:**

* **M1 (the latency):** re-inline the outcome recording behind the annotation step → the test that
  the wedge clears within one publish cycle must go RED.
* **M2, the null control (the one that matters):** make the new early call clear the wedge on rc=0
  *without* `.last_tested_hash` matching the marker's hash → must go RED. This is the 41h
  fail-open of 2026-08-11 and the repair must not be able to reintroduce it; a repair that clears
  faster by clearing on weaker evidence is worse than the defect.
* **M3 (the arithmetic):** raise any post-gate step's bound above the remaining slack → the
  population control must go RED. Null control for M3: *removing* a bounded step must NOT red it
  (a control that only counts is satisfied by deletion — the shape filed as *a mutation can delete
  the subject instead of moving it*).

**Why no mechanism change in this tick.** Identical to `51f710b49`'s reason and still true: PID
3132509 is a live full suite with `cwd = /home/rich/synthetic-enterprise`, i.e. **this working
tree**, and `process_run_complete.py` is the file the repair touches. Editing a shared module
under a live suite is a filed rule here, and this particular suite writes its reds onto the public
page banner — so the edit would publish its own breakage. The repair is safe on the next tick,
after PID 3066953 exits.

## LIMITATION explicitly recorded and accepted (clause 2), 2026-08-20

**Closure item 1 — "record the outcome when the publish LANDS, not when the process EXITS" — is
NOT built.** The title of this document is therefore still literally true: a green publish is
recorded only when the publisher process exits, so the annotation still sits between the publish
and the clear. What changed is that the latency is now BOUNDED BY THE PATH'S OWN DEADLINE
instead of by a bound five times larger than the allowance it lives in — the process can no
longer be killed while it still believes it has budget, so the outcome is now always recorded,
where before it could be recorded as the opposite of what happened, or never.

That is the difference between a delay and a lie, and it is why the observed harm is gone while
the shape is not. The self-sustaining half is broken with it: a killed publisher left its marker
pending, and `record_publish_gate_success` deliberately preserves `wedge_since` while any marker
is pending (correctly — a resumed wedge must be measured from where it really began), so every
kill re-armed the very episode it belonged to. 11 markers were pending when this was written.

**Why item 1 is not attempted in the same tick, stated rather than quietly skipped.** Its own M2
null control is the sharpest constraint in this document: a repair that clears the wedge FASTER
by clearing it on WEAKER evidence is worse than the defect, and that is the 41h fail-open of
2026-08-11. Moving the clear earlier means touching the one path whose evidence keying —
last-tested-hash against the marker's own hash — is what makes the clear honest. That deserves
its own draw with its own mutation pass, not the tail end of a tick whose repair is already
landed and whose subject file was carrying a live publisher at the time.

## 6. Second-order, filed here rather than fixed (SELF_INTERRUPT_DISCIPLINE — queue, don't fix on sight)

`sim-runner-log.md` contains **159** `Publish-gate failure #N (deadline_kill, rc=None)` lines. None
of them is a real deadline kill: `docs/observability/` contains **zero** occurrences of
`TIMED OUT processing`, which `background_worker.log()` writes to `background-worker-log.md`
before it ever routes the outcome. All 159 were written by the test suite through the unguarded
`prc.log()` sink — they sit among `/tmp/pytest-of-rich/...` paths, `git=abc1234`, and
`could not make the HEAD checkout a git repo: git is not installed`. Every one reads `failure #1`,
which is what a per-test temp state file produces: the STATE is isolated, the LOG is not.

Same class as `294447ccf` (a fixture wrote 65% of the live suite-headroom series) and
`WORKER_FINDING_A_TEST_ISOLATES_THE_PATHS_IT_THOUGHT_OF_2026-08-10.md`. That class was closed at
one sink, under `PYTEST_CURRENT_TEST`; `prc.log()` is another sink of the same class and was not
covered. **This materially damages the log as evidence** — it is the log the wedge diagnosis reads
first — and it is the reason §3's prediction is stated as inferred rather than claimed as observed.
