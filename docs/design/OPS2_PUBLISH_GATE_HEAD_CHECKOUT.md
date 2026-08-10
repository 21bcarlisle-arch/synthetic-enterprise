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
| In-tree baseline (`PROJECT_DIR`) | *owed* | the pre-ruling subject — the denominator |
| Reused checkout, first cycle (cold `__pycache__`) | **1291.9s** | measured, HEAD `3ee4541a7`, 23,249 passed / 7 failed, box quiet |
| Reused checkout, second cycle (warm) | **1167.5s** | measured, HEAD `54141b559`, box quiet, 13.2G→4.4G available |

> **STATUS 2026-08-10 21:00Z — the ninth launch DEFERRED, and waiting was the defect.**
> Observed, from the unit's own journal: `20:40:05Z [measure] ! publisher still live after 2700s
> — DEFERRING`. It resumed both banked phases correctly (*"phase 1/3 COLD — banked by an earlier
> launch at 1291.9s, not re-run"*, and the same for warm) — the resume fix holding — and then
> lost the box for the **fourth** time on the same phase.
>
> **Nine launches, `deferral_count` rising, `in_tree_baseline` never once timed. That is not bad
> luck, it is a control that cannot fire.** `docs/staging/` holds **112 pending
> `run_complete_*.md` markers**; `background_worker.py::process_leftover_run_markers` re-globs
> them every cycle; one publish cycle is now bounded at `GATE_SUITE_TIMEOUT_SECONDS` = 2600s of
> gate plus the publish path after it. The publisher therefore runs very nearly back-to-back, and
> a guard that **waits for a gap** in a queue that refills faster than it drains starves — quietly,
> one deferral at a time, with every banked phase looking healthy in the record. The phase that
> keeps losing is the ratio's **denominator**, so the criterion stays unmeasurable rather than
> wrong, which is the better of the two failures but still a failure.
>
> **Closed by taking the gap instead of waiting for one.** The primitive was already in the repo
> and this harness was not using it: `process_run_complete.py::_run_lock` is a non-blocking
> `flock` on `.process_run_complete.lock` wrapping the *whole* cycle (`_process`), and a publisher
> that cannot take it exits `EXIT_LOCK_SKIPPED` (75) with its marker still pending — a path
> `background_worker.py` already handles as *"still pending, will retry next cycle"*, not as a
> failure. `_publisher_exclusion` now **holds that lock for the duration of a phase**:
>
> * it converges — the acquire waits out at most **one** live publisher, then no further one can
>   start, where the poll had to win a race against a queue that never empties;
> * `box_was_quiet` becomes true **by construction**, not by luck. The seventh launch's invariant
>   (`test_a_banked_phase_was_always_admitted_quiet`) previously rested on nothing having started
>   in the gap between the last poll and the first test;
> * the acquire deadline is **derived** from `PUBLISH_PATH_TIMEOUT_SECONDS` — the longest a
>   publisher may legally hold the lock — not restated as a round `45 * 60`. A wait shorter than
>   the work it waits on does not bound the wait; it guarantees a deferral. That is the same
>   defect §2 closed one layer down, where a 900s caller cap sat under a 2600s gate.
>
> Cost: **one deferred publish cycle per phase**, on a queue that is already deferred, and nothing
> to the marker. R15 both ways in `tests/tools/test_measure_publish_gate_subject_cost.py` — the
> lock is interrogated through `prc._run_lock` itself (so a test cannot pass against a lock the
> real publisher would not respect), and the four mutations are named in the tests' own
> docstrings: drop the exclusion, drop the release, fall through instead of deferring, hand-type
> the deadline.
>
> **And the exclusion would have wedged publishing from inside the gate — caught before commit,
> by running the module rather than reading it.** The publisher holds `_run_lock` for the whole
> of `_process`, and the gate's suite runs *inside* that hold; this harness's test module is in
> the gate's own argv. So the tests that drive `_run_measurement` — which enters the exclusion in
> the COLD and WARM phases itself, past the stubbed `_time_suite` — blocked on the **live**
> publisher's lock for `QUIET_WAIT_SECONDS` = 3800s (observed: killed at 900s in
> `test_a_banked_phase_is_resumed_rather_than_re_run`, lock confirmed HELD). Inside the gate that
> is a 2600s timeout and a **fail-CLOSED** verdict — every cycle, deterministically, on this
> atom's own wedge class. The free-lock branch is the mirror: a unit test takes the real
> publisher's lock and live cycles skip.
>
> Closed with an **autouse** redirect of `prc.RUN_LOCK_FILE` into each test's `tmp_path` — autouse
> because two of the three entry points are not nameable at any test's call site — plus two
> controls, both mutation-proven 2026-08-10: `test_no_test_in_this_module_can_reach_the_live_
> publishers_lock` (mutation `autouse=False` → reds, naming the live path) and
> `test_any_test_module_that_enters_the_exclusion_redirects_the_lock`, whose population is
> **derived from the tree** with a vacuity guard rather than listed (mutation: a probe module
> driving the harness without the redirect → reds naming it). One older test was also un-stubbed:
> under the new ordering its `_wait_for_quiet` stub let the run reach the **real**
> `prc._head_checkout()`, so its verdict turned on whether a publisher held the reuse lock; it now
> defers at the guard that actually fires first. Module: **900s+ hang → 54 passed in 5.3s**. Full
> finding: `docs/staging/done/WORKER_FINDING_THE_EXCLUSION_DEADLOCKED_AGAINST_THE_LOCK_IT_TAKES_2026-08-10.md`.

**Ratio warm / in-tree: STILL OWED** against the exit criterion of ≤ 1.3×. Cold and warm are
both banked and load-bearing (§2's bound is derived from the worst of them), but the *exit
criterion itself* is a ratio, and its denominator has now lost the race for the box three times.

> **STATUS 2026-08-10 (seventh launch, OOM-killed in phase 3 — R9: observed, from the unit's own
> journal).** `Active: failed (Result: oom-kill)`, 19:25:11 BST, 11.1G peak, after 1h36m41s. It
> entered BASELINE's quiet-wait at 18:25:58Z, timed out at ~19:11, and — per the then-current
> fall-through — **started the suite anyway, beside a live publisher.** Two full suites do not
> fit in 15.9G.
>
> **This is now fixed at the cause, and the cause was not the OOM.** The fall-through to
> "measure anyway, flagged contended" was FAIL-OPEN in the R15 sense: the phase that keeps
> losing the box is `in_tree_baseline`, which is the ratio's **denominator**, so a contended
> baseline runs slow → ratio smaller → criterion likelier to read **MEETS**. The kill was the
> cheap failure; the survivable version would have certified this atom's own exit criterion with
> a number wrong in the passing direction, with only `box_was_quiet: false` buried in a phase
> record to say so.
>
> Both guards now **defer**: bank the measured phases, record `deferred{reason, at_phase}`,
> exit 0, and let the next launch resume. Every banked phase is therefore admitted-quiet by
> construction — an invariant the record is checked against
> (`test_a_banked_phase_was_always_admitted_quiet`,
> `test_the_live_record_carries_no_contended_phase`) rather than a caveat. The convergence risk
> this takes on is visible as a rising `deferral_count`, not silent.
>
> Full finding, with the four mutations run both ways:
> `docs/staging/done/WORKER_FINDING_MEASURE_ANYWAY_BIASED_THE_EXIT_CRITERION_TOWARD_PASS_2026-08-10.md`

> **STATUS 2026-08-10 (fifth launch, OOM-killed in phase 2 — R9: observed, from the unit's own
> journal, not inferred).** The systemd form HELD: the unit ran 1h33m, banked the cold phase,
> and was not reaped. It died of memory:
>
>     publish-gate-subject-cost.service: The kernel OOM killer killed some processes in this unit
>     Active: failed (Result: oom-kill) since 13:55:30 BST ... Mem peak: 6.5G
>
> **Measured cause, not inferred.** The box has **15G of RAM** (WSL2 hands the VM half of 32),
> 4G swap with 3G already used, and `/tmp` is a **7.8G tmpfs — RAM, not disk**. A suite leaves
> its pytest temp roots there: `/tmp/pytest-of-rich` held **2.0G** across roots of 775M, 676M
> and 570M, all from that day. Phase 1 left its gigabytes resident and phase 2 started a full
> suite on top of them, 6m20s before the kernel intervened.
>
> `_sweep_stale_pytest_temp_roots` could not have helped and was never meant to: its bound is
> 3h-old, keep-newest-3, and this debris was minutes old and three roots deep. That sweep is a
> *between-cycles* reclaim; the OOM is what *within-run* accumulation looks like. The two are
> different controls and only one of them existed.
>
> **Two defects closed in response, both mutation-proven** (`tests/tools/`):
>
> 1. **The measurement now gets its own `--basetemp`,** which pytest clears at the start of every
>    run — so at most one phase's temps are resident, and the three phases start from the same
>    tmpfs state, which also makes them more comparable than they were. It stays under `/tmp`
>    (same filesystem as the real gate's, because the runtime *is* the measurement and §2's bound
>    comes off it) and is named under `HEAD_CHECKOUT_PREFIX` so the existing sweep already owns
>    the leak `finally:` cannot clean after a SIGKILL.
> 2. **The resume is now code.** The comment above `PHASE_ORDER` has claimed since it was written
>    that "a partial record tells the next tick precisely which phases to resume rather than
>    restart". It did not: `_run_measurement` opened with `"phases": {}` every time. Five launches
>    have now been killed and none has survived three phases in a row, so a harness that restarts
>    from the top never converges — and launch six would have deleted the reused checkout and
>    re-paid 21 minutes for a cold number already banked on disk. A checkpoint nothing reads is a
>    log line.
>
> The record can now span commits, so it says so: `phases_from_an_earlier_head` names any phase
> timed at a different SHA, and `warm_cache_established_by` records that a resumed warm phase was
> warmed by an earlier launch or the live publisher rather than by this run's own cold phase.
> The ratio the exit criterion reads is warm/in-tree and those two are re-run together whenever
> either is owed, so a stale cold can move §2's floor but never the ratio.

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

**1800s → 2600s, and the test constant 613s → 1291.9s, in the same commit.** Derived from the
one phase that is measured, and re-derivable when the other two land.

The bound is ≥ 2× the *worst legitimate* run (`implied_timeout_floor_2x` in the JSON), not 2× the
usual one, because a cold cycle is a real outcome — a fallback throwaway when another publisher
holds the reuse lock, or a rebuilt corrupt checkout. The worst legitimate run measured so far is
the **1291.9s cold**, so the floor is 2583.8s and the bound is **2600s**.

**1800s was already undersized against the subject the gate had been running since the ruling.**
It was 1.39× a runtime the gate really pays, and `test_the_gate_timeout_exceeds_the_suites_own_
runtime` did not notice because its constant was 613 — the *in-tree* suite, the pre-ruling
subject. A control calibrated to a subject its target had stopped running is the fail-open shape
R15 names: it could pass while the thing it guards sat one contended box away from wedging. The
constant now reads 1291.9 with the record and SHA it came from named in the docstring.

The direction of danger has flipped since the constant was first set. A timeout used to return
`True` (publish unverified); since 2026-08-09 it **fail-CLOSES**, so an undersized bound no longer
publishes garbage — it wedges publishing, which is the same defect as the original 600s bound, in
the same direction, against a subject nobody had re-measured.

**INTERIM, and labelled as such:** 1291.9s is the worst runtime measured *so far*. The warm phase
has since banked at **1167.5s** (slower than nothing, faster than cold, so it does not move the
floor); `in_tree_baseline` is the one still owed.

### The re-derivation is now checked against its evidence, not against a copy of itself

Until 2026-08-10 the only control on this constant was
`test_the_gate_timeout_exceeds_the_suites_own_runtime`, which compares it against
`MEASURED_SUITE_SECONDS = 1291.9` — **a second hand-copied transcription of the same phase of the
same record.** Two copies of one number cannot disagree unless a human re-copies one of them, so
that control could fail on a typo and on nothing else — least of all on the failure this bound has
actually suffered twice: the measured runtime moving out from under it. And the harness was
already computing `implied_timeout_floor_2x` into the record, where **nothing read it** — a
derived value with no consumer, this project's no-caller class exactly.

`prc.measured_gate_timeout_floor()` is that consumer and
`test_the_timeout_clears_the_floor_the_measurement_implies` is the control. It reads the committed
record, takes the worst banked phase × `GATE_TIMEOUT_SAFETY_FACTOR` (never below the harness's own
stated floor), and reds when the bound stops clearing it. Live now: floor **2583s**, bound 2600s.

Two properties it needed, both of them the reason the earlier control was inert:

* **It works on a PARTIAL record.** Eight launches have been killed or deferred and `complete` has
  never once been true; a floor that waits for completeness is a control that never fires. Every
  banked phase is admitted-quiet by construction (the harness defers rather than timing beside a
  live publisher), so the worst banked phase is a real runtime whether its siblings exist or not.
* **A record that cannot answer FAILS the check** rather than yielding a small floor the constant
  happens to clear — absent, malformed, wrong shape, `seconds: None/True/"1291.9"`, or a
  checkpoint written before phase one.

R15 both ways, run 2026-08-10: dropping the bound back to the pre-OPS2 1800s reds it (*"the
measured runtimes imply a floor of 2583s"*), and pointing it at a missing record reds it (*"the
bound's evidence is gone, which is a FAILED check, not a pass"*). Plus a mutation on the
**evidence** — a 1500s phase puts the floor at 3000s, above the constant — so the live green is
demonstrably falsifiable rather than merely never-yet-observed-red.

When `in_tree_baseline` lands, this control decides whether 2600s survives; nobody has to remember
to re-derive it.

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
