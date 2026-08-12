# [WORKER-FINDING] The tmpfs drain was pointed at the wrong filesystem — and a right-for-its-own-subject move is what pointed it there

**Found:** 2026-08-12 04:0xZ, working the RUNG-1 publish wedge (19th).
**Disposition:** defect 1 **FIXED**, R15-proven both ways. Defect 2 **QUEUED** (see below) —
it cannot be closed by the same edit and one half of it collides with a safety invariant.
**Lane:** H_harness · **Class:** R15 control-set hole / relocation moved a sibling's subject

## The claim

`observed-with-evidence` — `_sweep_stale_pytest_temp_roots`, the drain that exists to keep the
gate's tmpfs from exhausting, has been globbing `/var/tmp/pytest-of-*` since 2026-08-11 09:26Z.
That path cannot ever match: pytest builds its numbered roots under `tempfile.gettempdir()`,
which is `/tmp` here (measured: `TMPDIR` unset, `tempfile.gettempdir()` → `/tmp`).

Measured at the moment of the finding, with the gate wedged and publishing blocked ~3690 min:

```
$ ls -d /var/tmp/pytest-of-*      →  rc=2, no match
$ du -sh /tmp/pytest-of-rich      →  3.3G  (nine numbered roots)
$ df -h /tmp                      →  tmpfs 7.8G, 5.4G used, 69%
```

After the fix, from the module's own constants:

```
sweep root : /tmp
glob matches: ['/tmp/pytest-of-rich']
 reachable roots: 8      (was 0)
```

## The mechanism — a move that was correct for its own subject

Two commits, one day apart, neither wrong on its own terms:

- `21467f98d` (2026-08-10 14:13) added this sweep, rooted at `HEAD_CHECKOUT_ROOT`. **Correct on
  arrival** — that constant was `/tmp`, and the checkouts and the pytest roots were genuinely
  the same filesystem.
- `53e82b105` (2026-08-11 09:26) *"Move the gate's HEAD checkouts off tmpfs onto disk"* changed
  `HEAD_CHECKOUT_ROOT` to `/var/tmp`. Right for checkouts — it took 139M/cycle out of the OOM
  budget and made the `_free_mb` pre-flight measure a real disk. And because **one constant was
  answering two questions**, it silently carried the tmpfs drain off the tmpfs.

The two subjects had been coincident, so nothing in the code marked them as separable. This is
`feedback_control_set_hole_not_control_defect` seen one level up: not a broken control, and not
a missing one — a control whose *subject* was relocated by a change about something else.

**Why nothing caught it for 19 hours:**

1. **Its tests supply the subject.** All three existing tests plant their population under
   `prc.HEAD_CHECKOUT_ROOT`, which `sandbox` redirects into a `tmp_path`. They therefore stay
   green for *any* value of that constant, including one on a filesystem where a pytest temp
   root can never appear. Same shape as
   `feedback_a_render_harness_that_hand_types_its_call_list_supplies_the_defect`.
   The R15 test `test_the_checkout_sweep_alone_could_not_reclaim_what_wedged_it` reconstructs
   the real 2026-08-10 population faithfully by *name* (`pytest-of-rich/pytest-{0,31,36,…}`) and
   plants it in the *wrong place* — location was the one property that decided the outcome.
2. **A silent zero looks like a clean filesystem.** The log line fires only under `if removed:`.
   A drain that reclaims nothing because it is misrouted, and a drain that reclaims nothing
   because there is nothing to reclaim, produced byte-identical silence.

## The fix (landed)

- `PYTEST_TEMP_ROOT_PARENT` — derived from **pytest's own rule** (`tempfile.gettempdir()`,
  `SE_GATE_PYTEST_TEMP_ROOT`-overridable), not borrowed from a neighbour. The two sweeps' roots
  are now independently movable, which is the property whose absence caused this.
- The `elif not parents:` branch: an empty root now *says* it is empty, so "misrouted" and
  "clean" stop being the same silence.
- `sandbox` redirects the new constant explicitly. **This was mandatory, not tidiness:** with
  the sweep correctly rooted at the real `/tmp`, a test that planted roots and swept without the
  redirect would delete the temp directories of every other suite on the box, including its own.

**R15, both arms, on the real machine:**

- `test_the_pytest_sweep_is_rooted_where_pytest_actually_builds_its_roots` — oracle is
  `tmp_path`, i.e. pytest reporting where it *really* put a basetemp in that run; nothing the
  test typed or created. On the pre-fix root: `AssertionError: the sweep globs /var/tmp/
  pytest-of-* but pytest is building its roots in /tmp`. On the fix: passes.
- `test_the_two_sweeps_do_not_share_one_root_constant` — behavioural, so the *pre-fix code
  shape* (no second constant at all) fails it rather than merely being unrepresentable.
  Mutation run against the reconstructed pre-fix function: `checkout-root roots survived: False`
  → the assertion fails. On the fix: passes.
- Whole module at the production default: **43 passed**.

## Defect 2 — FIXED 2026-08-12 04:2xZ. Liveness is proved from pytest's own lock, not from a clock

> **The design question this finding held open is answered, and the answer it PROPOSED was
> wrong.** Recorded in full because the proposed design would have been fail-open in the one
> direction that matters.
>
> **The proposal — `/proc`-verified holder by reference scan — is REFUTED BY MEASUREMENT.** At
> 05:12Z, with the gate suite demonstrably running inside `pytest-128`, no live process on the
> box referenced any pytest root through its `cwd`, its open fds, or its memory maps — pid
> 836345 included. pytest closes the lock fd the instant it has written it. A reference scan
> would have read the live suite's own root as unheld and deleted it: exactly the outcome the
> age bound exists to prevent, arrived at through a different inference.
>
> **What IS provable:** pytest's `create_cleanup_lock` writes the session PID into
> `<root>/.lock` and unlinks it from an atexit hook. Three states, and the ambiguous one is gone:
> lock+live pid = HELD (at any age); lock+dead pid = a SIGKILLed session, debris; no lock = the
> atexit ran, the session finished, debris. Verified against `/proc`, with a pid-reuse guard
> (a process that started after its lock was written cannot be the process that wrote it).
>
> **The keep-newest-3 window was backwards, measured.** `pytest-128`, the one LIVE root on the
> box, sat FOURTH by mtime — outside the window. The window was instead protecting
> `pytest-139/140/141`, three finished sessions holding 12M. Rank was never liveness. It now
> applies only on the UNPROVEN path.
>
> **`STALE_HEAD_CHECKOUT_AGE_SECONDS` is untouched, so the collision this finding named never
> happens:** `test_the_age_bound_cannot_delete_a_running_suites_checkout` still holds, and the
> 3h bound survives as the fallback for a root whose holder cannot be established. R15
> fail-silent: an unavailable check is a FAILED check, never permission to delete.
>
> **R15, four mutations, all KILLED:** no liveness proof → the live-holder tests fire; pre-fix
> age-only shape → the dead-lock-PID test fires; unproven treated as debris (fail-open) → the
> fallback test fires; pid-reuse guard removed → the recycled-pid test fires. Module: 47 passed.
>
> **Measured effect on the real filesystem**, running the landed mechanism at 04:22Z:
> `/tmp` 57% → 32% (3.4G → 5.4G available, ~1.9G reclaimed), `free available` 7G → 8G because
> the tmpfs is RAM. Four roots swept, all with dead lock PIDs; **every one of them was INSIDE
> the 3h bound** (68, 50, 43 and 24 minutes old), so the pre-fix drain would have reclaimed
> **nothing**. Both live suites' roots (`pytest-143`, `pytest-144`) proved HELD and untouched.
>
> **Caught while doing this, and fixed in the same commit:**
> `test_the_two_sweeps_do_not_share_one_root_constant` takes `tmp_path`, not `sandbox`, so
> `prc.LOG_FILE` was never redirected and the sweep's success line was landing in the LIVE
> `docs/observability/sim-runner-log.md` — a test manufacturing the evidence an operator reads
> to judge the live system. Same class as
> `WORKER_REPORT_THE_GATES_OWN_TESTS_WERE_WRITING_THE_ALARMS_EVIDENCE_2026-08-10`. The ~33
> already-written lines are LEFT IN PLACE deliberately: a live publisher was appending to that
> file at the time and rewriting it under a concurrent writer trades a cosmetic defect for a
> real one. **The wider class is NOT closed** — other tests in this module take `tmp_path`
> without `sandbox` (`git=abc1234` / `git=unknown` lines in the same log are the same shape,
> and are the already-filed
> `WORKER_FINDING_TEST_FIXTURE_VALUES_REACHED_THE_LIVE_PUBLISH_STATE_2026-08-11`). Queued, per
> SELF_INTERRUPT_DISCIPLINE.

### The original entry, as filed



`observed-with-evidence`, and **the fix above does not touch it**. Restoring reach is not the
same as reclaiming: at the moment of the fix, 8 roots were reachable and **0** were older than
the sweep's `STALE_HEAD_CHECKOUT_AGE_SECONDS` = 3h bound, so a live sweep still frees nothing.

Measured fill rate over the wedge: `/tmp` went 52% → 69% in ~80 minutes (3.3G of pytest roots,
oldest 48 min). A 3h drain cannot hold a filesystem that exhausts in under two hours. The
self-worsening loop in `WORKER_FINDING_THE_GATES_SCRATCH_SPACE_IS_RAM_AND_NOTHING_DRAINS_IT`
therefore still closes — exhaustion → failed checkout → collapsed scope → vacuity guard → full
suite → more temps.

Not fixed on sight, deliberately, and not merely under SELF_INTERRUPT_DISCIPLINE: **the obvious
edit collides with a live invariant.** `test_the_age_bound_cannot_delete_a_running_suites_
checkout` pins `STALE_HEAD_CHECKOUT_AGE_SECONDS > GATE_SUITE_TIMEOUT_SECONDS * 1.5` (= 1.875h),
because a shorter bound lets the sweep delete a *running* suite's directory — worse than the
leak. `PYTEST_TEMP_KEEP_NEWEST = 3` is not sufficient protection on its own: nine roots were
live-ish here and more than three suites can be running at once (two were, during this tick).

The design question to answer before editing, not during: **liveness must be established by
something other than age.** A root held by a live pid is safe at any age; a root whose pid is
gone is debris at one minute. Candidate: sweep on `/proc`-verified holder rather than mtime,
which decouples the drain's time constant from the suite timeout entirely and would let the
bound drop to minutes. That is a real design pass, and it is the same "prove liveness, don't
infer it from a clock" shape as `feedback_a_lock_is_not_occupancy_when_the_worker_is_a_grandchild`.

**Rank:** above backlog, below the wedge itself. It recurs on a clock and degrades silently.

## Related, already recorded

- `WORKER_FINDING_THE_GATES_SCRATCH_SPACE_IS_RAM_AND_NOTHING_DRAINS_IT_2026-08-12` — the parent.
  Its defect 1 said the sweeper's subject was "too narrow". It is narrower than that: for the
  pytest half the subject was **empty**, and had been for 19h.
- `feedback_an_elimination_must_move_the_controls_that_pin_it` — the mirror image. There, a
  removal stranded its controls; here, a relocation took a control's subject with it.
- `feedback_a_ratchet_with_no_drain_is_a_cleanup_not_a_control` — why the reachable-but-never-
  firing drain is still not a control until defect 2 closes.
- `feedback_control_set_hole_not_control_defect`, `feedback_a_test_isolates_the_paths_it_thought_of`.
