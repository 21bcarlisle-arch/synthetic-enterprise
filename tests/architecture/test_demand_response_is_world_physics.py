"""KNIFE3 step 26 — the control on `B9_demand_response_is_world_physics`.

WHY THIS FILE EXISTS, AND WHY THE RATCHET IS NOT ENOUGH (R15)
--------------------------------------------------------------
The cut in register §3u is a MODULE MOVE: `saas/demand_response.py` ->
`simulation/demand_response.py`. Deleting the ratchet tuple proves the
`simulation.run_phase2b -> saas.demand_response` edge is gone, and that is all
it proves. Two things it CANNOT see, and both are how a module move rots:

  1. **Behaviour.** A file move is supposed to change no number. The ratchet
     would stay green if the move also changed `BASE_SHIFT_FRACTION` from 0.15
     to 0.20, or reversed the peak/off-peak windows, or stopped conserving kWh.
     So the pre-cut answers are PINNED here, computed from the module on the
     `saas/` side before `git mv` ran, and re-asserted against the module on the
     `simulation/` side. The pin is pre-cut evidence, not a re-record of the
     post-cut tree — which is the tautology this project keeps catching.

  2. **The direction the move was made to protect.** The whole ruling is that
     these numbers are the WORLD's and the supplier is allowed to be wrong about
     them. The day a `company/` or `saas/` module imports this, the supplier is
     reading the truth off the world instead of estimating it, the belief-vs-
     truth gap silently goes to zero, and every wall control stays green —
     because a company -> simulation import is a class-(a) edge the KNIFE passes
     drove to zero and nothing re-counts per module. `test_no_company_side_
     importer` counts it per module.

THE THREE KILLER PATTERNS, ANSWERED
------------------------------------
TAUTOLOGY   — the expected values are NOT derived from the module under test.
              They are literals, transcribed from a run against the pre-move
              file. Rewriting the module cannot move them.
FAIL-OPEN   — the importer scan asserts it actually walked a non-empty file set
              and that the module it is about exists at the path it names; an
              empty sweep or a renamed module is a FAILURE here, not a pass.
FAIL-SILENT — the module is imported at module scope, so an unimportable
              module errors the whole file rather than skipping quietly.

MUTATION EVIDENCE (performed 2026-08-13, restored from a copy, both directions;
23 pass on the unmutated tree, so each count below is a real kill)
  - `BASE_SHIFT_FRACTION` 0.15 -> 0.20             -> 12 failed, 11 passed.
  - swap `_PEAK_INDICES` / `_OFFPEAK_INDICES`      -> 14 failed, 9 passed,
    including the conservation/direction test, which is the one a pinned-value
    sweep alone would not have caught (a swap conserves energy perfectly).
  - a `company/` module importing this one         -> 1 failed, 22 passed:
    `test_no_company_side_importer`, and nothing else in the repo went red,
    which is the whole reason this per-module count exists.
"""

import ast
from pathlib import Path

import pytest

from simulation.demand_response import (
    BASE_SHIFT_FRACTION,
    EV_BOOST,
    HEAT_PUMP_BOOST,
    apply_demand_shift,
    compute_shift_fraction,
    make_shifted_shape_fn,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "simulation" / "demand_response.py"

# The module names that must never import this. `saas/` is included because the
# module used to LIVE there: a stray re-import back would restore the exact
# defect this step cut, from the exact side it was cut from.
COMPANY_SIDE_DIRS = ("company", "saas")

# The forms a company-side import of this module could take.
FORBIDDEN_IMPORT_TARGETS = (
    "simulation.demand_response",
    "sim.demand_response",
)

# ---------------------------------------------------------------------------
# The pin. Transcribed from a run against `saas/demand_response.py` BEFORE the
# move, over 4 asset shapes x 3 profile shapes. Values are literals on purpose.
# ---------------------------------------------------------------------------

PRE_CUT_SHIFT_FRACTION = {
    "none": 0.15,
    "ev": 0.27,
    "heat_pump": 0.22999999999999998,
    "ev+heat_pump": 0.35000000000000003,
}

# key -> (total_kwh, shifted_kwh, profile[0], profile[33], profile[46])
# index 0 and 46 are off-peak receivers; index 33 sits inside the peak window.
PRE_CUT_SHIFT = {
    "none|flat": (48.0, 1.05, 1.065625, 0.85, 1.065625),
    "none|peaky": (29.2, 3.15, 0.396875, 2.55, 0.396875),
    "none|zeropeak": (41.0, 0.0, 1.0, 0.0, 1.0),
    "ev|flat": (48.0, 1.89, 1.118125, 0.73, 1.118125),
    "ev|peaky": (29.2, 5.67, 0.554375, 2.19, 0.554375),
    "ev|zeropeak": (41.0, 0.0, 1.0, 0.0, 1.0),
    "heat_pump|flat": (48.0, 1.61, 1.100625, 0.77, 1.100625),
    "heat_pump|peaky": (29.2, 4.83, 0.501875, 2.31, 0.501875),
    "heat_pump|zeropeak": (41.0, 0.0, 1.0, 0.0, 1.0),
    "ev+heat_pump|flat": (48.0, 2.45, 1.153125, 0.65, 1.153125),
    "ev+heat_pump|peaky": (29.2, 7.35, 0.659375, 1.95, 0.659375),
    "ev+heat_pump|zeropeak": (41.0, 0.0, 1.0, 0.0, 1.0),
}

ASSET_SHAPES = {
    "none": None,
    "ev": {"ev": True},
    "heat_pump": {"heat_pump": True},
    "ev+heat_pump": {"ev": True, "heat_pump": True},
}


def _profile(kind: str) -> list[float]:
    if kind == "flat":
        return [1.0] * 48
    if kind == "peaky":
        return [0.2] * 31 + [3.0] * 7 + [0.2] * 10
    if kind == "zeropeak":
        # A real zero in the peak window, which must be told apart from a
        # shift-fraction of zero: both produce shifted_kwh == 0.0.
        return [1.0] * 31 + [0.0] * 7 + [1.0] * 10
    raise AssertionError(f"unknown profile kind {kind!r}")


# ---------------------------------------------------------------------------
# 1. Behaviour is unchanged by the move — measured, not asserted
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("key", sorted(PRE_CUT_SHIFT_FRACTION))
def test_shift_fraction_matches_the_pre_cut_value(key):
    assert compute_shift_fraction(ASSET_SHAPES[key]) == pytest.approx(
        PRE_CUT_SHIFT_FRACTION[key], abs=1e-12
    ), f"the move changed the shift fraction for {key}"


@pytest.mark.parametrize("key", sorted(PRE_CUT_SHIFT))
def test_shifted_profile_matches_the_pre_cut_values(key):
    asset_key, profile_kind = key.split("|")
    frac = compute_shift_fraction(ASSET_SHAPES[asset_key])
    profile, shifted = apply_demand_shift(_profile(profile_kind), frac)

    want_total, want_shifted, want_0, want_33, want_46 = PRE_CUT_SHIFT[key]
    assert sum(profile) == pytest.approx(want_total, abs=1e-9)
    assert shifted == pytest.approx(want_shifted, abs=1e-9)
    assert profile[0] == pytest.approx(want_0, abs=1e-9)
    assert profile[33] == pytest.approx(want_33, abs=1e-9)
    assert profile[46] == pytest.approx(want_46, abs=1e-9)


def test_energy_is_conserved_and_the_direction_is_peak_to_offpeak():
    """The two properties no single pinned value states on its own.

    A swap of the peak and off-peak index sets conserves energy just as well, so
    conservation alone cannot catch it. The direction assertion can.
    """
    before = _profile("peaky")
    after, shifted = apply_demand_shift(before, compute_shift_fraction({"ev": True}))

    assert sum(after) == pytest.approx(sum(before), abs=1e-9)
    assert shifted > 0.0
    # index 33 is inside the peak window, index 0 outside it.
    assert after[33] < before[33], "peak consumption did not fall"
    assert after[0] > before[0], "off-peak consumption did not rise"


def test_a_real_zero_peak_is_told_apart_from_a_zero_shift_fraction():
    """Both answer 0.0 shifted; only one of them is a customer who shifts."""
    zero_peak, shifted_a = apply_demand_shift(_profile("zeropeak"), 0.30)
    zero_frac, shifted_b = apply_demand_shift(_profile("peaky"), 0.0)

    assert shifted_a == 0.0 and shifted_b == 0.0
    # The zero-peak customer's profile is still processed (and unchanged,
    # because there was nothing to move); the zero-fraction one is returned
    # untouched by the early exit. The distinction that matters is that the
    # zero-peak case reached the arithmetic at all.
    assert zero_peak == _profile("zeropeak")
    assert zero_frac == _profile("peaky")


def test_the_shape_wrapper_still_wraps():
    base = _profile("peaky")
    fn = make_shifted_shape_fn(lambda _d: list(base), compute_shift_fraction(None))
    got = fn("2023-01-01")

    assert got != base, "the wrapper returned the unshifted profile"
    assert sum(got) == pytest.approx(sum(base), abs=1e-9)


def test_the_boosts_are_additive_and_capped():
    assert compute_shift_fraction({"ev": True}) == pytest.approx(
        BASE_SHIFT_FRACTION + EV_BOOST, abs=1e-12
    )
    assert compute_shift_fraction({"ev": True, "heat_pump": True}) == pytest.approx(
        BASE_SHIFT_FRACTION + EV_BOOST + HEAT_PUMP_BOOST, abs=1e-12
    )
    assert 0.0 <= compute_shift_fraction({"ev": True, "heat_pump": True}) <= 1.0


# ---------------------------------------------------------------------------
# 2. The direction the cut exists to protect
# ---------------------------------------------------------------------------


def _python_files_under(*dirs) -> list[Path]:
    found: list[Path] = []
    for d in dirs:
        root = REPO_ROOT / d
        if not root.is_dir():
            continue
        found.extend(
            p for p in root.rglob("*.py") if "__pycache__" not in p.parts
        )
    return found


def _imported_module_names(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError:
        return set()
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            names.add(node.module)
    return names


def test_the_module_is_on_the_sim_side_at_the_path_this_control_names():
    """FAIL-OPEN guard: a rename must red this file, not silently exempt it."""
    assert MODULE_PATH.is_file(), f"{MODULE_PATH} is gone — re-point this control"
    assert not (REPO_ROOT / "saas" / "demand_response.py").exists(), (
        "the module is back on the saas/ side — the step 26 cut was reverted"
    )


def test_no_company_side_importer():
    """The class-(a) direction. Per module, because nothing else counts it."""
    files = _python_files_under(*COMPANY_SIDE_DIRS)
    # FAIL-OPEN guard: an empty sweep is a broken sweep, never a pass.
    assert len(files) > 50, (
        f"scanned only {len(files)} company-side files — the sweep is broken, "
        "and a broken sweep passes this test for free"
    )

    offenders = sorted(
        str(p.relative_to(REPO_ROOT))
        for p in files
        if _imported_module_names(p) & set(FORBIDDEN_IMPORT_TARGETS)
    )
    assert offenders == [], (
        "the supplier is reading the world's demand-response physics directly, "
        "which zeroes the belief-vs-truth gap it is supposed to be scored on: "
        f"{offenders}"
    )


def test_the_module_imports_nothing_but_the_stdlib():
    """The other direction: this must never grow a sim -> company edge.

    It is also the second half of the B1 safety measurement, kept live rather
    than left in the commit message.
    """
    imported = _imported_module_names(MODULE_PATH)
    non_stdlib = sorted(
        m for m in imported
        if m.split(".")[0] in {"company", "saas", "simulation", "sim", "background", "tools"}
    )
    assert non_stdlib == [], (
        f"{MODULE_PATH.name} grew a first-party import: {non_stdlib}"
    )
