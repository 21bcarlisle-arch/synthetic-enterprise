# OPS2 — the HEAD-checkout publish gate gets a real lifecycle (2026-08-10)

**Atom:** `OPS2_publish_gate_head_worktree` · lane `H_harness` · level 0 → 2
**Spec (not re-derived here):** `docs/staging/done/PLANNER_MINTED_publish_gate_head_checkout_polish_2026-08-09.md`
**Ruling it serves:** `DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` — *"publishing tests
committed truth only; the working tree belongs to the lanes."*

The minimal version (landed 2026-08-09) moved the gate's SUBJECT to a clean `git archive HEAD`
checkout. It was correct on day one and had no lifecycle: a fresh directory every cycle, cleanup
only in a `finally:` that a SIGKILL skips, a timeout bound justified against the old subject, and
— the part that mattered — **no test asserted the property the ruling bought**. This atom is the
lifecycle and that test.

---

## 1. The checkout is REUSED between cycles

One directory, `<tmp>/publish-gate-head-reused`, refreshed in place rather than recreated:

    .git/HEAD <- new SHA
    git read-tree -u --reset <sha>     # index + working tree to the new commit, deletions included
    git clean -xdfq -e __pycache__ -e sim/cache -e node_modules

`git worktree add` is still deliberately NOT used: it registers state in the real repo that
survives this process being SIGKILLed, which is exactly what the archive form avoids. Deleting
the directory still deletes every trace.

**Why reuse at all — the cost is bytecode, not extraction.** Extraction is 0.46s. What a fresh
directory costs is a cold `__pycache__`: ~3,000 modules plus every test module's
pytest-rewritten bytecode recompiled on every publish cycle, permanently.

### Measured, both sides, `-x` removed from the gate argv on both

`-x` is removed for the measurement only: with it a red run stops at the first failure, so the
"duration" would be time-to-first-failure and the two sides would not be comparable.

| Run | Wall clock | Notes |
|---|---|---|
| In-tree baseline (`PROJECT_DIR`) | *pending* | the pre-ruling subject |
| Reused checkout, first cycle (cold `__pycache__`) | *pending* | what every cycle used to pay |
| Reused checkout, second cycle (warm) | *pending* | the steady state |

**Ratio warm / in-tree: PENDING** against the exit criterion of ≤ 1.3×.

> **STATUS 2026-08-10 11:22Z — FOURTH launch, and the first one init owns:
> `python3 -m tools.measure_publish_gate_subject_cost --systemd` → transient unit
> `publish-gate-subject-cost.service`, MainPID 2674636, HEAD `49863e9c6`, record says
> `launched_by: "systemd"` (computed from `INVOCATION_ID`, not claimed).**
>
> **Verified from the kernel rather than from the launch line:** `ps -o ppid= -p 2674636` → 409,
> which is `/usr/lib/systemd/systemd --user`. The measurement is not a descendant of the tick
> that started it, so the reaper shape inferred below cannot reach it.
>
> **Why the third launch still died, and why "detach harder" was the wrong next move.** The
> 10:42:36Z run went through `--detach` and its own record said `is_session_leader: true` — the
> detach HELD — and it died anyway at 10:46:06Z, 3.5 minutes in, still inside `_wait_for_quiet`.
> `dmesg` has no OOM after 08:28 (observed), and this repo has no reaper — `worker_seat.py`
> states the reaping path is DELETED and `pkill`/`killpg` appear nowhere outside comments
> (observed, by grep). **Inferred** (R9 — the killer was not caught in the act): `start_new_session`
> changes the session and process group but NOT the child's `ppid`, so a cleanup that walks a
> launcher's descendants still finds it. Session detachment and descendant-walk invisibility are
> two different protections, and `--detach`'s control only ever tested the first. That gap is now
> a control of its own —
> `test_session_detach_does_not_hide_a_child_from_a_descendant_walk` asserts a `--detach` child
> IS still a descendant, which is what stops the systemd assertion from passing vacuously.
>
> **This also corrects a diagnostic rule written into this doc on the previous pass.** It said a
> heartbeat that stops *in the wait* means "the detach did not hold". It does not: the fourth
> record stopped in the wait with the detach demonstrably holding. What a stalled in-wait
> heartbeat means is only "killed while waiting"; WHICH protection failed is what `launched_by`
> now answers.
>
> ---
>
> **Superseded status (third launch, 2026-08-10 10:42Z — kept because its lesson stands):**
>
> The two previous attempts died at the same point — inside `_wait_for_quiet`, ~12 minutes in,
> before phase one — because each was started from a bounded worker tick as an ad-hoc background
> job. `3cc60f133` reported the second of these as fixed by "launched under `setsid`", and
> `WORKER_FINDING_THE_DETACH_THAT_FIXED_THE_DEATH_IS_NOT_IN_THE_REPO_2026-08-10` established by
> grep that **`setsid` appeared nowhere in the repository**: the harness had a committed body and
> a typed launch, which is behaviour-determining state outside the readable repo (the IaC
> constraint OPS1 names as the core one) and a member of this project's no-caller class.
>
> What changed, and it is code rather than a note:
>   * **`--detach`** re-execs the harness through `_detached_popen` (`start_new_session=True`), so
>     the child is a session and process-group leader and a kill directed at the tick's group
>     cannot reach it. Its argv deliberately omits `--detach` — a child that carried it would
>     fork launchers forever without timing anything.
>   * **The record says whether it was really detached, computed not claimed.** `is_session_leader`
>     is `os.getpid() == os.getsid(0)` asked by the running process. The 08:35Z run's detachment
>     could only be re-typed, never checked; this one is checkable from the artefact alone.
>   * **A heartbeat inside the wait.** `last_heartbeat` advances every poll, so a fourth death is
>     diagnosable: a record that stops advancing *in the wait* means the detach did not hold and
>     the next escalation is a systemd unit beside `reconcile-watch.timer`, not a fourth identical
>     launch.
>   * **A second concurrent launch is refused** (`_measurement_is_running`), because two runs
>     would delete the reused checkout under each other's suite and both would report a wrong
>     ratio without saying so. The guard skips its own ancestor chain — counting the launch's own
>     command line would make it refuse every launch.
>
> R15 both ways, `tests/tools/test_measure_publish_gate_subject_cost.py`:
> `test_a_detached_child_survives_the_death_of_its_launchers_process_group` runs BOTH arms — the
> undetached child must die under the group kill (else the survival assertion is vacuous) and the
> detached one must live. **Mutation on the production file: `start_new_session=False` reds it**
> (verified 2026-08-10, file restored). Plus: no flag means no spawn, a live measurement refuses a
> second launch, and the `is_session_leader` stamp is read from source to prove it is computed.
>
> Harness: `python3 -m tools.measure_publish_gate_subject_cost --detach` (in the repo precisely so
> this claim can be re-run rather than believed). It writes
> `docs/observability/publish_gate_subject_cost.json` with all three phases, the ratio, and
> `implied_timeout_floor_2x`. A ~50-minute run that must not overlap the live publisher's own
> suite — it waits for the box to go quiet, and deletes the reused checkout only AFTER that wait
> so it can never pull the directory out from under a real cycle. **The next worker tick should
> READ that JSON and fill in this table and §2 — not start another run.**
>
> **The half that DID hold, from the 05:28 attempt.** The harness **checkpoints from before the
> first wait** and after every phase, carrying `complete: false` and `phases_missing` until the
> derived figures exist, plus `pid` and `started_at`. That is why the 08:35Z death was
> diagnosable from the repo at all — it said which of the three phases it still owed, where the
> 05:28 death had left only two lines in `/tmp`. **Readers must therefore test `complete`, not
> the file's existence** — a checkpoint is not a result. One of OPS2's two fixes held; the other
> was never in the repo to hold, which is the whole lesson and is now closed above.
>
> Re-launch — **always through `--systemd`** (`--detach` is now known to be insufficient from a
> bounded tick; see the 11:22Z status above) — only if `complete`
> is false AND no `measure_publish_gate_subject_cost` process is running (`pgrep -af`; the flag
> refuses on its own if one is live); resume-worthy phases are listed in `phases_missing`. If a
> record shows `is_session_leader: false`, whoever launched it went around the committed path and
> the run is expected to die at that tick's edge. Do **not** re-launch
> merely because the recorded SHA is behind HEAD: HEAD moves under a ~50-minute measurement as
> ordinary commits land, each phase stamps the SHA it actually ran against (`head_sha_at_run`),
> and the runtime being measured does not turn over commit by commit. Treating "behind HEAD" as
> death costs another 50 minutes for no information.
>
> A live `aborted` field means the run ended for a *named* reason (usually another publisher
> holding the reuse lock, which makes the warm phase not warm) — that one is worth re-launching
> promptly, because it costs minutes rather than the full 50 and only needs a quieter window.

Both sides ran on the live box while the publisher's own cycles were running, so the absolute
numbers carry that load; the ratio is what the criterion is about and both sides carry it alike.
Per R12 the number is a DIAGNOSTIC — it is recorded here, and the test module asserts the
MECHANISM (bytecode survives a refresh, debris does not) rather than a wall-clock threshold,
which on a shared box would be a flake generator.

## 2. `GATE_SUITE_TIMEOUT_SECONDS`, re-derived

**PENDING the §1 measurement — still 1800s, which is the constant justified against the OLD
in-tree subject.** This is the one exit criterion of the five that is not yet met, and it is
named here rather than quietly left: the bound moves to ≥ 2× the *worst legitimate* run
(`implied_timeout_floor_2x` in the JSON), not 2× the usual one, because a cold cycle is a real
outcome — a fallback throwaway when another publisher holds the reuse lock, or a rebuilt corrupt
checkout. `test_the_gate_timeout_exceeds_the_suites_own_runtime`'s `MEASURED_SUITE_SECONDS = 613`
moves with it in the same commit; that constant currently describes the in-tree subject and so
under-states what the gate now actually runs.

The direction of danger has flipped since the constant was first set. A timeout used to return
`True` (publish unverified); since 2026-08-09 it **fail-CLOSES**, so an undersized bound no longer
publishes garbage — it wedges publishing. The bound is therefore derived from the measured
runtime of the subject the gate actually runs, and
`test_the_gate_timeout_exceeds_the_suites_own_runtime` carries the measured constant with it.

## 3. Crash-safe lifecycle

`finally:` does not run under SIGKILL, and `rc=-9` is a known gate outcome (the OOM killer is the
known cause). Leaked 130MB directories are therefore expected, not hypothetical — 4.4GB of them
exhausted the tmpfs on 2026-08-09 and wedged publishing with a message about git.

* The reused directory is safe by construction: there is one, and the next cycle reuses it.
* Every cycle **sweeps** `publish-gate-head-*` directories older than 3h (well clear of the suite
  timeout, so a live fallback checkout can never be swept out from under its own suite). The
  sweep runs BEFORE the disk pre-flight, which makes the exhausted-tmpfs wedge self-healing.
  It fired on its first real run and reclaimed two abandoned checkouts.

## 4. The three hazards a reused directory introduces, each closed as a control

| Hazard | Closure | Control |
|---|---|---|
| Two publishers refreshing one tree | non-blocking `flock`; the loser gets a correct, cold throwaway | `test_a_second_publisher_never_shares_the_reused_checkout` |
| A suite's debris judging the next cycle | `git clean -xdf` at refresh, keeping only bytecode and the DATA overlay | `test_the_checkout_is_reused_and_keeps_its_bytecode` |
| Crash leakage | age-bounded sweep, throwaways removed in `finally:` including on a raising run | `test_stale_checkouts_are_swept_and_live_ones_are_not`, `test_the_throwaway_checkout_is_removed_even_when_the_run_raises` |

A fourth, found while building: the directory is state that outlives the process, so it can be
found in any condition — truncated, from an older layout, borrowing an object store that has
moved. `_checkout_is_usable` checks the alternates line, and **unusable means rebuild**, never
"run the gate in it and see" (`test_a_corrupt_reused_checkout_is_rebuilt_rather_than_trusted`).

## 5. R15 both ways — `tests/background/test_publish_gate_subject_is_head.py`

The property the ruling bought had no test: *a lane's uncommitted work cannot change the publish
verdict*. It does now, and by mutation rather than by assertion. Every behavioural test builds a
REAL git repo in `tmp_path` and points `prc.PROJECT_DIR` at it — writing a syntax error into a
tracked file of the live shared tree, the honest way to make a tree dirty, would break every
daemon that imports it for as long as the test ran.

Mutations run against the production file, each reverted immediately (2026-08-10):

| Mutation | Reds |
|---|---|
| `_run_gate_in(PROJECT_DIR, …)` — subject back to the shared tree | `test_a_dirty_working_tree_does_not_change_the_verdict`, `test_the_gate_runs_with_its_cwd_inside_the_checkout` |
| `_checkout_unavailable_verdict` returns `(True, False)` | `test_an_unavailable_checkout_blocks_the_publish` |
| wipe the checkout every cycle | `test_the_checkout_is_reused_and_keeps_its_bytecode` |
| `git clean` spares a previous suite's debris | `test_the_checkout_is_reused_and_keeps_its_bytecode` |
| sweep loses its age bound | `test_stale_checkouts_are_swept_and_live_ones_are_not` |
| stamp `.last_tested_hash` regardless of rc | `test_a_red_suite_does_not_stamp_the_tested_hash`, `test_mutation_pointing_the_gate_back_at_the_tree_reds` |

Six mutations, six reds, file restored byte-identical.

**One test in the older module was CHANGED, not deleted, and the change is a real weakening that
belongs on the record.** `test_the_checkout_is_removed_afterwards` asserted removal after every
run; removal is no longer the property that keeps /tmp bounded, BOUNDEDNESS is. It is now
`test_the_checkout_is_either_reused_or_removed_never_leaked`, which asserts the disjunction
because which branch a caller gets depends on whether a live publisher holds the reuse lock. The
branch-specific behaviour is pinned deterministically in the new module instead — the weaker
assertion is in the module that cannot control the condition, the strong ones where it can.

## 6. The `.last_tested_hash` contract, stated once

It had two readers inferring the semantics from each other's call sites, which is how a
cross-check quietly stops being independent. The contract now lives in exactly one place,
`process_run_complete.LAST_TESTED_HASH_CONTRACT`: **one writer** (`_run_gate_in`, only on rc=0);
**two readers** (`run_fast_tests` skips a SHA already green; `supervisor::_publish_gate_wedge_draw`
uses it as the INDEPENDENT cross-check that says recorded failures are stale). Anything that
stamps the file without a green suite collapses that independence into a tautology and blinds the
wedge draw — `test_a_red_suite_does_not_stamp_the_tested_hash` and the timeout test pin both
directions, and `test_the_hash_contract_is_stated_in_one_place` fails if the two modules' declared
paths ever diverge (read from source, because this suite's conftest monkeypatches the attribute).

---

## What this atom did NOT do

* **No `git worktree`.** Rejected for the reason above (state in the real repo surviving a
  SIGKILL); the exit criterion allowed either.
* **The gate's own suite is still red at HEAD for unrelated reasons.** This atom changes the
  gate's LIFECYCLE, not what the suite finds; the wedge-clearing work is `OPS3`.
* **No change to what runs.** Same argv, same marker expression, same heavy ignores, same
  live-box tests observing the live box.
