**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The operational verdict was a function of another lane's untracked file — and the class control found a twelfth leak on its first run

Drawn 2026-09-10 as RUNG 1b (PRIORITY ZERO), the operational-layer PERSISTENT-RED self-refill, at
`consecutive_red: 8`. The draw's first branch — re-run the signal, it may already be green — does
**not** apply: it is still red, and this is the fix.

---

## 1. The cause, in one line

`deadmans_switch.run_cycle()` asks `launch_liveness.landed_check()` whether every file a finished
run named has reached a commit. Another lane's finished `arms-rerun-20260910b` left
`docs/observability/value_cycle_ab_s1_noise_floor_20260910b.json` untracked, the check correctly
said `[LAUNCH UNLANDED]`, and that message landed in all 28 `assert calls == []` lists in
`tests/background/test_deadmans_switch.py`.

**The drift alarm was right.** The artefact really is unlanded and the director should be told. What
was wrong is that a test suite's verdict was a function of what some other lane happened to have
left in the working tree — so an unlanded artefact anywhere in this repository paged OPERATIONAL
LAYER RED, which reads as a daemon regression and is not one.

Reproduced in 0.78s before any change was made:

```
E   AssertionError: assert ['[DIGEST] 1 ...absent.jsonl'] == []
E     '[DIGEST] 1 batched item(s) since the last digest.
E      — drift (1):  #1 [LAUNCH UNLANDED] 1 file(s) a finished run wro...'
```

## 2. Why the pin that was written for exactly this did not cover it

The EIGHTH conftest pin (2026-08-14) points `notification_digest.QUEUE_FILE` at an **absent** path,
and its own guard test proves an absent queue flushes nothing. That guard was one of the 28
failures, which is the part worth keeping.

The queue is **append-only**, and `notify()` writes to whatever path the constant names. A check
firing *inside* the cycle re-fills the pinned queue microseconds before the same cycle flushes it.
**An absent queue is only empty until something in the cycle speaks.** Isolation at the digest is
isolation at the wrong end; it has to be at the live INPUT, which is that conftest's standing rule
and has been for ten instances.

## 3. What landed

**The ELEVENTH pin** — `launch_liveness.RECORDS_PATH` at an absent tmp path. `load()` returns `[]`
for an absent path, so both `check()` and `landed_check()` have nothing to grade and both go silent.
It closes a leak running the other way too: `check()` SAVES its settled verdicts, so before this
every `run_cycle` test in the directory rewrote the live `.launch_records.json`.

**The class control** — `tests/background/test_deadman_cycle_isolation.py`, the deadman analogue of
`test_rest_ladder_isolation.py`. It DERIVES the check set from the shipped source of `run_cycle`
(bare zero-argument statement calls) and asserts each is silent under this directory's fixtures,
with `notify` captured. R10: this is the *fourth* instance of one class —
`_flush_notification_digest` (2026-08-14, 27 tests), `_check_origin_fork` (2026-09-02, 28 tests,
then 28 again an hour later when the rung grew a second world-read), and this one — so a fourth
instance fix was not available.

**The TWELFTH pin, and it was not found by a red.** The class control named
`_check_worktree_reconcile` on its first run: it pages `[WORKTREE UNDECLARED]` about whatever
`git worktree list` says right now. It is silent in the aggregate tests *only because `notify()`
dedupes on transition state* — the alarm is keyed to the undeclared COUNT, so the moment a lane adds
or removes a worktree the state changes, the dedupe lets it through, and all ~30 assertions go red
at once. That is the "weather as its subject" flake this directory has now been bitten by four
times, and no red would have shown it today.

A second hazard closed with the same pin. `run_cycle` also calls `_check_worktree_reap`, whose own
docstring says *never* to run it in enforce mode against the real repo's worktrees — and the enforce
flag is armed on this machine. Every test here that drives `run_cycle` did exactly that. Nothing has
been reaped only because the live/locked/dirty refusal set kept saying no.

## 4. My own first draft was wrong, and the record is the point

The worktree pin's first version replaced `scan_worktrees`/`scan_fork_branches` with `lambda: []`.
It broke **four** tests in `test_fork_reconciler.py` whose SUBJECT is the scan: they build a fixture
repo, swap `F._git` for a scoped runner, and assert the porcelain parse. That is this conftest's
oldest recorded mistake — *redirect the destination, never replace the function* — and the
43-controls lesson in its own docstring: isolation and a live-artefact control want opposite things
from the same name. The shipped pin is on `fork_reconciler._git`, the module's one window onto the
world, returning `""` — which is the answer `_git` already returns on any failure. The four tests
set `_git` in their own body, which runs after the fixture and therefore still wins.

A second one of mine, caught before it fired. The derived set contains
`_check_operational_layer_signal`, and calling it for real from inside `pytest -m operational`
**spawns `pytest -m operational`**. The control passed in 0.10s only because that check
self-throttles on the live state file and was inside its hour — the exact "weather as its subject"
shape the file exists to refuse. An hour later it would have forked a twenty-minute suite run
inside a suite run. It is stubbed, with the reason on the file, and it keeps its place in the
enumeration so the vacuity guard stays honest.

## 4b. The gate then found two more, and only because it judges a clean extract

The first landing attempt was REFUSED — by my own control, running inside the pre-commit gate's
clean HEAD extract, naming two further leaks that are invisible in the working tree:

- `_reping_open_action_needed_items` re-pings every OPEN item in the real register, and **HEAD's
  committed copy holds an open `publish_gate_wedged`**. The working tree's copy is modified and
  has none.
- `_check_content_publishing` reads the publish clock, and a `git archive` extract **has no clock
  at all** — which is `state == "unpublished"`, the loudest branch it has, on every single run.

This is the divergence this conftest's oldest docstring warns about in terms: *the publish gate
judges a clean HEAD checkout while a developer judges the working tree, and the two disagree
exactly when the live file is dirty-but-fresh in the tree and stale at HEAD.* Green here, red
there — and the control said so by name in sixty seconds rather than through twenty-eight
unrelated assertions.

**The two pins point in opposite directions, and that is the finding.** "Pin it at an absent tmp
path" is the habit this file has used twelve times, and for the publish clock it is exactly wrong:
absent *manufactures* the alarm. The register is pinned ABSENT (empty register = silence); the
clock is pinned SEEDED with a fresh publish (the honest analogue of an isolated checkout, and what
`test_deadmans_switch.py::_isolate` has always asserted by stubbing the snapshot healthy). A test
asserts the difference directly, so a future reader normalising the second onto the first fails
rather than reinstates the defect.

Both are pinned at the PATH, not at the read function, and here that is load-bearing rather than
stylistic: `test_publish_freshness.py` and `test_action_needed.py` both live in this same
directory, so a directory-scoped stub of either module's reader would delete their subject.

## 4c. CORRECTION — the fourteenth pin was RED at HEAD for ten minutes, and it was mine

fb9f610be landed green through the gate, and the very next signal run came back RED with **eight
new failures**, all in `test_staging_watcher.py`, none of which had failed in the 1,247-pass run
forty minutes earlier. The cause was the pin I had just written.

The seeded publish clock was written to **`tmp_path` itself**. `test_staging_watcher.py` points
`watcher.STAGING_DIR` at that same `tmp_path` — so a seeded file landed inside eight *"the staging
directory is empty"* assertions and every one of them notified about it:

```
E  AssertionError: assert ['New staged instruction: .last_content_publish_isolated.json
                           — pending review'] == []
```

**The rule was already written in the file I was editing**, three fixtures higher, about
directories: *a fixture that materialises things inside another test's `tmp_path` is changing the
world it is supposed to be isolating.* A file is the worse case, because the watcher's own
`current_files` skips directories by construction and cannot skip a file. Fixed by moving the seed
into a subdirectory, and the property is now asserted directly —
`test_this_directorys_fixtures_put_no_FILE_at_the_root_of_tmp_path`, which is one `iterdir()` and
would have caught it before the land.

Kept here rather than revised into section 4b. The gate's clean extract caught pins 13 and 14 that
the working tree could not see; it could not catch this one, because the contamination is between
two *tests*, not between a test and the repository — a fourth face of the same class, and the
control for it is one line.

## 5. Evidence

| Leg | Before | After |
|---|---|---|
| `test_deadmans_switch.py` + `test_launch_liveness.py` (`-m operational`) | 28 failed | **58 passed** |
| the five affected files, whole | — | **182 passed** |
| the class control | did not exist | **7 passed**, and it fires on the shipped defect |

Both directions are asserted, per R15. `test_the_control_fires_when_a_real_check_leaks` reinstates
the 2026-09-10 defect on the shipped check — a register naming an untracked artefact — and watches
the control catch it; `test_check_enumeration_is_derived_not_declared` adds and removes calls in a
synthetic source and watches the answer move; a vacuity guard refuses a parse that returns fewer
than ten checks.

## 6. What is NOT fixed, said on the surface

1. **The artefact is still unlanded**, and deliberately so. It belongs to an in-flight lane
   (`SEAT_FINDING_THE_RIVAL_FLOOR_IS_A_DIFFERENT_SEED_FAMILY...`), and landing another lane's
   result out from under it is the move this project has been burned by repeatedly. The drift
   alarm continues to say so, correctly, which is now the *only* thing it does.
2. **The isolation covers `run_cycle`, not the whole operational suite.** Any other directory whose
   tests read live repository state can still contaminate the signal. `tests/background/` is where
   all three recorded episodes came from; a wider claim would not be measured.
3. **The class control's strictness is deliberate.** It captures at `notify`, one level above
   `send_ntfy`, so it catches a check that is currently transition-deduped into silence. That is
   how the twelfth leak was found, and it is the difference between a control and the weather.
