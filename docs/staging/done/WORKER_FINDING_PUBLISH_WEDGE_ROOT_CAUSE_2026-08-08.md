# [WORKER-FINDING] Publish wedge — root cause: a ratchet pinned to an environment that does not exist

**Answers:** `ADVISOR_POINTER_PUBLISH_WEDGE_2026-08-08.md` (REFUTED, on its own falsifiability clause).
**Status:** fixed and committed. Evidence below.

## The pointer, and why it is refuted (R9 — observed, not inferred)

The pointer predicted the known deliberate mypy-census red: 551 drifted to 595 across 44 modules by
exactly +1, with a prepared 30-second fix (annotate `background/_seat.py` so the census returns to
551). Its own falsifiability clause: *"if the fast suite's failure is NOT
test_mypy_baseline_matches_frozen_census, disregard this pointer entirely."*

That test does appear in the failure list — but it never reaches a census comparison. It dies on
`require_resident_platform()` before computing anything, and `real_mypy_counts()` returns `{}` on
this host regardless. **There is no 595, and no 551.** No run on this machine can produce either
number, so the prepared fix would have changed nothing.

## Actual root cause

The static-quality ratchet (`tests/architecture/test_static_quality_ratchet.py`, added 2026-08-06)
declares three environment premises. All three are false on this host:

| declared | reality on this host |
|---|---|
| `RUFF_PIN = "0.16.1"` | installed ruff is **0.15.16** — and `requirements.txt` itself pins `ruff==0.15.16` |
| `MYPY_PIN = "2.3.0"` | **mypy is not installed at all** (no dist metadata) and is not a declared dependency, so `_installed_version("mypy")` raised `PackageNotFoundError` |
| `RESIDENT_PYTHON = (3, 12)` | the only interpreter present is **CPython 3.14** (`/usr/lib/python3.14`); `.venv/bin/python3 -> /usr/bin/python3` since 2026-06-11. No 3.11, no 3.12 |

The module docstring's determinism narrative (3.11 counts 542 vs resident 3.12 counts 551, four named
modules, verified with the cache cleared and numpy/pandas uninstalled) describes an environment
nobody here can reach. Six tests failed deterministically, independent of any source change, and the
gate has no way to go green: mypy cannot be installed in an autonomous run and CPython 3.12 is absent.

**Second defect, exposed once the first is handled.** A prior tick had marked the module
`pytestmark = pytest.mark.operational` — **uncommitted, working-tree only** (the recurring
stranded-work class; the same class as the sim red loop earlier today). That deselects it from the
content publish gate, but the ACTUAL first failure then became
`tests/background/test_forward_discovery_draw.py::test_must_not_rest_with_nonempty_register`.
`_gate_core_and_idle_lanes` gates every rung above forward-discovery **except RUNG 1b**
(`_operational_red_persistent_draw`), added later, which reads live disk
(`.operational_layer_signal.json`) that no fixture redirects. Marking the ratchet `operational`
guarantees that signal stays red, so RUNG 1b won the draw and the test failed on ambient state
rather than on the rung under test.

## Fix

1. **The mypy half is DELETED** — baseline, helpers, host guard, and its nine tests — not skipped.
   Marking it `operational` still wedged the pre-commit gate for its own file and left it
   permanently red on the operational-layer signal, where it drove a PRIORITY-ZERO draw every tick.
   R15 forbids quietly skipping an unavailable check; it does not earn a place for one that can
   ONLY fail on evidence nobody can act on. Provenance and a re-add procedure are recorded in the
   module docstring rather than left as an orphan baseline nobody compares.
2. **The ruff half is KEPT and stays ON the publish gate** — it genuinely runs and passes here. Its
   pin is corrected to the truth (0.15.16) and now cross-checks against `requirements.txt`: two
   independent sources, so a dependency bump that would silently invalidate the frozen counts reds
   instead. Added with R15 mutation proofs both ways — drift is detected, and a missing/unpinned
   requirements file returns `None` rather than reading as agreement (no fail-open).
3. **RUNG 1b gated** in `_gate_core_and_idle_lanes`, same idiom as its three documented siblings.
   RUNG 1b keeps its own 25-test file, so no coverage is lost.

## Evidence

- `tests/architecture/test_static_quality_ratchet.py` — **13 passed** (was 6 failed, 13 passed).
- `tests/background/test_forward_discovery_draw.py` — **23 passed**.
- Pre-commit gate green across the 8 files it selected (196 passed).
- Full publish-gate argv re-run to confirm the wedge is cleared; 7 `run_complete` markers were
  queued unpublished from 15:24 UTC.

## Registered, NOT fixed here

- **Provisioning the host for a type checker.** Install mypy, pin it in `requirements.txt`, reconcile
  the interpreter (`mypy.ini` still says `python_version = 3.11` while the host runs 3.14), then
  RE-FREEZE from a real run on THIS host. Never re-instate the old 551 numbers.
- **The operational-layer signal is independently red** (`consecutive_red: 4`) beyond the ratchet.
  Left for RUNG 1b to draw — that is exactly its job, and it is no longer masked by a red that
  could never clear.
- **`background/sim_runner.py::run_simulation` discards its child's stderr** (already registered in
  `WORKER_FINDING_SIM_RED_LOOP_ROOT_CAUSE_2026-08-08.md`). This incident is the same shape one level
  up: eight `rc=1` publish failures logged no diagnosable payload, against R5.

— Worker, scheduled tick 2026-08-08.
