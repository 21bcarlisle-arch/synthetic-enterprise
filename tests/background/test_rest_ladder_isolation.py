"""THE CLASS CONTROL for "a new rest-ladder rung leaks live disk into the rest proofs".

WHAT KEEPS HAPPENING. `supervisor._is_drained_and_gated()` is a ladder of refusal rungs --
`if <rung>(): return False` -- and each new rung reads some REAL file in this checkout. The
rest-proof tests in this directory (test_forward_discovery_draw.py, test_governance_refusal.py)
set up a hermetic "authorized set empty at every level" world and assert rest is PERMITTED. A rung
whose live input happens to be non-empty flips every one of those assertions, and because the
publish gate judges a clean HEAD checkout while a developer judges the working tree, the two
disagree exactly when the live file is dirty-but-fresh in the tree and stale at HEAD.

FIVE INSTANCES, EACH PATCHED ALONE:
  1. RUNG-4  declared-defect backlog   (2026-07-24) -- 16 tests red
  2. RUNG-1  publish-gate wedge        (2026-07-24) -- self-sustaining wedge, 12 tests red
  3. RUNG-7  planner axes / blocked mints
  4. RUNG-1b operational-layer red     (2026-08-08) -- red-ed the gate through two files
  5. RUNG-4b stale-gap-row             (2026-08-10) -- 11 tests red at HEAD, publish wedged

R10 forbids closing an absurdity-class defect with a sixth instance fix. This is the class fix:
rather than a hand-kept list of "rungs we remembered to isolate" (which is what decayed four
times), the control DERIVES the rung set from the shipped source of `_is_drained_and_gated` and
asserts that under the rest proofs' OWN setup every one of them is silent. A rung added tomorrow
is enumerated automatically; if it leaks, this test names IT, rather than eleven unrelated tests
failing with "rest was refused".

WHY IT IS NOT A TAUTOLOGY (R15). The rung set is parsed from the real function's source, not
declared here (proved by `test_rung_enumeration_is_derived_not_declared`, which adds and removes
rungs in a synthetic source and watches the answer move). The silence check calls the real shipped
rung functions through the real fixture (proved to FIRE by
`test_the_control_fires_when_a_real_rung_leaks`, which makes a registered rung return work).
"""
from __future__ import annotations

import ast
import inspect

import pytest

import background.supervisor as sup
from background import gap_ledger_reconciler
from tests.background.test_forward_discovery_draw import (
    _EMPTY_REGISTER,
    _gate_core_and_idle_lanes,
    _point_register_at,
)

# --------------------------------------------------------------------------- #
# PURE helpers (mutation-testable without touching disk)
# --------------------------------------------------------------------------- #

def refusal_rungs(source: str) -> list[str]:
    """Names called in `if <name>(...): return False` inside the given function source.

    That statement shape IS the definition of a refusal rung: a call whose truthiness alone
    forbids rest. Deliberately EXCLUDES the terminal `return _rule0_harden_draw() is not None`
    (which must be truthy for rest to be legitimate -- the opposite obligation) and any helper
    used in an assignment (`frozenset()`), because neither can flip a rest proof by being
    non-empty."""
    tree = ast.parse(inspect.cleandoc(source) if source.startswith(" ") else source)
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        if not (isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name)):
            continue
        body = node.body
        if len(body) != 1 or not isinstance(body[0], ast.Return):
            continue
        value = body[0].value
        if isinstance(value, ast.Constant) and value.value is False:
            name = node.test.func.id
            if name not in found:
                found.append(name)
    return found


def leaking_rungs(namespace, names) -> dict[str, str]:
    """Rungs that return something TRUTHY in the current process state -> {name: what it said}.

    A truthy rung refuses rest. Under a rest proof's setup every rung must be silent, so any
    entry here is a live-disk leak. A rung that is absent or raises is NOT reported: this control
    is about isolation, and a broken rung is a different defect with its own tests (every rung is
    fail-open by construction, so it cannot invent a hold either)."""
    leaks: dict[str, str] = {}
    for name in names:
        fn = getattr(namespace, name, None)
        if not callable(fn):
            continue
        try:
            verdict = fn()
        except Exception:
            continue
        if verdict:
            leaks[name] = repr(verdict)[:400]
    return leaks


# --------------------------------------------------------------------------- #
# R15: the enumeration is DERIVED from the shipped source, not declared here
# --------------------------------------------------------------------------- #

_SYNTHETIC = """
def f():
    if _alpha():
        return False
    if _beta(x=1):
        return False
    spare = frozenset()
    if _gamma():
        log("not a refusal")
    return _terminal() is not None
"""


def test_rung_enumeration_is_derived_not_declared():
    """MUTATE THE SOURCE, watch the answer move -- proves nothing is hard-coded."""
    assert refusal_rungs(_SYNTHETIC) == ["_alpha", "_beta"]

    added = _SYNTHETIC.replace(
        "    spare = frozenset()",
        "    if _delta():\n        return False\n    spare = frozenset()",
    )
    assert refusal_rungs(added) == ["_alpha", "_beta", "_delta"], (
        "a rung ADDED to the source was not enumerated -- this control would go blind to exactly "
        "the change it exists to catch"
    )

    removed = _SYNTHETIC.replace("    if _alpha():\n        return False\n", "")
    assert refusal_rungs(removed) == ["_beta"]


def test_terminal_harden_draw_is_not_a_refusal_rung():
    """`_rule0_harden_draw` must be TRUTHY for rest to be legitimate -- the opposite obligation.
    Enumerating it would make this control demand its silence and red the honest ladder."""
    assert "_terminal" not in refusal_rungs(_SYNTHETIC)
    assert "_rule0_harden_draw" not in refusal_rungs(inspect.getsource(sup._is_drained_and_gated))
    assert "frozenset" not in refusal_rungs(inspect.getsource(sup._is_drained_and_gated))


def test_leak_detector_separates_truthy_from_silent():
    class _Ns:
        _loud = staticmethod(lambda: "STALE-GAP-ROW self-refill (RUNG 4b): 13 measurements")
        _quiet = staticmethod(lambda: None)
        _empty = staticmethod(lambda: [])
        _explodes = staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("boom")))

    leaks = leaking_rungs(_Ns, ["_loud", "_quiet", "_empty", "_explodes", "_absent"])
    assert list(leaks) == ["_loud"]
    assert "13 measurements" in leaks["_loud"]


# --------------------------------------------------------------------------- #
# THE CONTROL ITSELF -- run against the shipped ladder under the rest proofs' setup
# --------------------------------------------------------------------------- #

def _real_refusal_rungs() -> list[str]:
    rungs = refusal_rungs(inspect.getsource(sup._is_drained_and_gated))
    # VACUITY GUARD (R15): a parse that silently returned [] would make the control below pass
    # unconditionally -- the fail-silent pattern. The ladder has had eight or more refusal rungs
    # since 2026-07-27 and only ever grows.
    assert len(rungs) >= 8, (
        f"only {len(rungs)} refusal rung(s) parsed out of _is_drained_and_gated: {rungs}. Either "
        "the ladder was rewritten into a different statement shape (update `refusal_rungs` to "
        "match it) or this control is now vacuous. Do not delete this guard to make it pass."
    )
    return rungs


def test_every_refusal_rung_is_silent_under_the_rest_proof_setup(monkeypatch, tmp_path):
    """THE CLASS CONTROL. Reproduce a rest proof's world exactly -- the core/idle lanes stubbed by
    `_gate_core_and_idle_lanes`, the live-disk rungs pinned by this directory's autouse conftest,
    the forward-discovery register empty -- then ask each rung individually whether it is silent.

    FAILS BY NAME on the rung that leaks, instead of leaving eleven tests to fail with "rest was
    refused" and no clue which level did the refusing (which is what cost the 2026-08-10 publish
    wedge its diagnosis time)."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _EMPTY_REGISTER)

    leaks = leaking_rungs(sup, _real_refusal_rungs())
    assert not leaks, (
        "REST-LADDER ISOLATION LEAK -- {} rung(s) of `_is_drained_and_gated` read LIVE state that "
        "the rest proofs in this directory do not neutralise, so every 'authorized set is empty -> "
        "rest is permitted' assertion here is now a function of this checkout's working files:\n"
        "{}\n\n"
        "This is the fifth-plus instance of one class. The fix is NOT to stub the rung in one test "
        "file: pin its live INPUT to an absent tmp path in tests/background/conftest.py's autouse "
        "fixture, beside the publish-gate / axes / staging / operational-signal / gap-ledger pins "
        "already there, so the whole directory is isolated by default and the rung's own tests "
        "(which set their state in the test body, after this fixture) still exercise it for real."
        .format(len(leaks), "\n".join(f"  {k} -> {v}" for k, v in leaks.items()))
    )


def test_the_control_fires_when_a_real_rung_leaks(monkeypatch, tmp_path):
    """R15 BOTH WAYS: reinstate the 2026-08-10 defect on the SHIPPED ladder -- a registered rung
    returning work -- and prove this control catches it. Uses the real rung name and the real
    enumeration, so it also proves the enumeration actually REACHES the shipped functions."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _EMPTY_REGISTER)

    rungs = _real_refusal_rungs()
    assert "_stale_gap_row_draw" in rungs, (
        "the rung that wedged publishing on 2026-08-10 is no longer enumerated -- if it was "
        "deliberately removed from the ladder, re-point this mutation at another live-disk rung"
    )
    monkeypatch.setattr(
        sup, "_stale_gap_row_draw",
        lambda *a, **k: "STALE-GAP-ROW self-refill (RUNG 4b): 13 published measurements",
    )

    leaks = leaking_rungs(sup, rungs)
    assert "_stale_gap_row_draw" in leaks, "the control cannot see a leaking rung -- it is theatre"
    # And the leak really does flip the rest proof it protects, which is why this matters.
    assert sup._is_drained_and_gated() is False


def test_the_gap_rung_is_silent_under_this_fixture(monkeypatch, tmp_path):
    """The INSTANCE, asserted rather than assumed: the conftest pin must actually silence RUNG 4b.

    Both directions are checked so the pin cannot rot into a no-op -- with the reconciler's ledger
    path ABSENT (this directory's default) the rung says nothing; the assertion that it CAN speak
    lives in test_the_control_fires_when_a_real_rung_leaks above."""
    assert gap_ledger_reconciler.LEDGER_PATH.name == "coupled_gap_ledger_absent.json", (
        "tests/background/conftest.py no longer pins gap_ledger_reconciler.LEDGER_PATH -- RUNG 4b "
        "is reading the real ledger again and the whole directory is one stale row from red"
    )
    assert not gap_ledger_reconciler.LEDGER_PATH.exists()
    assert sup._stale_gap_row_draw() is None


def test_rest_is_actually_permitted_in_the_isolated_world(monkeypatch, tmp_path):
    """The end-to-end consequence, stated once here so a future reader can see what the isolation
    BUYS: with every level genuinely empty, rest is legitimate. This is the assertion that eleven
    tests in this directory depend on and that the ungated rung flipped."""
    _gate_core_and_idle_lanes(monkeypatch)
    _point_register_at(monkeypatch, tmp_path, _EMPTY_REGISTER)
    assert sup._is_drained_and_gated() is True


@pytest.mark.parametrize("pinned", [
    "PUBLISH_GATE_STATE_FILE",
    "LAST_TESTED_HASH_FILE",
    "DIRECTOR_AXES_PATH",
    "STAGING_DIR",
    "OPERATIONAL_LAYER_SIGNAL_FILE",
])
def test_the_earlier_four_pins_are_still_in_force(pinned):
    """The previous instance fixes are load-bearing for this control's silence assertion -- if one
    is deleted the class control above starts failing for a reason its message would misattribute.
    Each must still point outside the real checkout."""
    value = getattr(sup, pinned)
    assert "synthetic-enterprise/docs" not in str(value), (
        f"supervisor.{pinned} is pointing at the REAL checkout inside tests/background/ -- the "
        "autouse isolation fixture in conftest.py has lost a pin"
    )


# ---------------------------------------------------------------------------
# NINTH INSTANCE -- the sim_runner sweep (2026-08-17)
# ---------------------------------------------------------------------------

def test_no_sim_runner_path_constant_points_into_the_real_checkout():
    """The ninth instance of this directory's oldest class, and the first that leaks
    OUTWARD: `sim_runner.record_run_outcome` writes `.sim_producer_state.json`, which
    supervisor RUNG 1d reads as PRIORITY-ZERO drawable work. Unisolated, the ordinary
    `run_simulation()` tests stamped `consecutive_failures: 6` onto the live machine's
    producer-health file -- i.e. a test could make the real draw ladder drop everything
    and 'go fix the producer' on a healthy box.

    The conftest pin is a SWEEP over every Path constant on the module rather than a
    ninth remembered name, so this asserts the property (nothing points into the real
    tree) rather than one path. A tenth constant added tomorrow is covered, and this
    control still fires if the sweep is deleted or narrowed."""
    from pathlib import Path

    from background import sim_runner

    repo_root = Path(__file__).resolve().parents[2]
    offenders = []
    for name in dir(sim_runner):
        if name.startswith("__"):
            continue
        value = getattr(sim_runner, name, None)
        if not isinstance(value, Path):
            continue
        try:
            value.relative_to(repo_root)
        except ValueError:
            continue
        offenders.append(f"sim_runner.{name} = {value}")

    assert not offenders, (
        "these sim_runner path constants point into the REAL checkout inside "
        "tests/background/ -- the autouse sweep in conftest.py has been lost or "
        "narrowed, and a test run will write live daemon state:\n  "
        + "\n  ".join(offenders)
    )


def test_the_sweep_leaves_paths_outside_the_checkout_alone():
    """The sweep must not be a blunt 'redirect everything': a constant already pointing
    outside the repo (a system path, an absolute temp location) is not this class's
    problem, and rewriting it would break honest tests for no reason."""
    from pathlib import Path

    from background import sim_runner

    # The pin redirects into tmp, preserving the tail -- so the ORIGINAL relative shape
    # must survive, which is what makes a redirected constant still meaningful to read.
    assert sim_runner.PRODUCER_STATE_FILE.name == ".sim_producer_state.json"
    assert isinstance(sim_runner.LOG_FILE, Path)
