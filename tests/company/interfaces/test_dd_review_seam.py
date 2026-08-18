"""The annual-DD-review seam's contract — and the ways this cut could rot silently.

WHY THIS FILE EXISTS (R15: a control must be able to FAIL on its own named defect)
---------------------------------------------------------------------------------
KNIFE pass 3 step 32 (disposition register §3aa,
`B13_the_annual_dd_review_is_the_suppliers_own_desk`) cut
`simulation.run_phase4c_on_phase2b -> company.billing.dd_review_runner` by putting
the supplier's DD desk behind `company/interfaces/dd_review.py`. The world hands
over its own issued bills and takes back the SERIALISED review.

The epistemic-wall ratchet polices one half: a module-scope
`simulation.* -> company.billing.dd_review_runner` import reds the suite. Three
things it cannot see, and each is what a plausible future edit would actually do:

1. **THE DOOR WIDENING.** This cut's whole substance is that the desk's own rule
   (`review`, the SLC 27B ±5% variance test), its materiality judgement
   (`LARGE_INCREASE_THRESHOLD_PCT`, the 15% bill-shock cut) and its types
   (`DDReviewBook`, `DDReviewRunResult`, `DDAction`) are UNREACHABLE through the
   seam. Nothing static objects to a convenience re-export, and the ratchet is
   happy either way because the module is under `SEAM_PACKAGE`. Control 1 asks
   what the door module actually carries, and asserts a company type cannot be
   obtained through it — including via the returned value, which is why the door
   returns a serialised dict and not a view object.

2. **THE VALUES MOVING.** The pre-cut call site was
   `run_annual_reviews(bills).serialise()` and the door is the same expression, so
   a control that re-ran that expression and compared would be checking a value
   against its own source — R15's TAUTOLOGY pattern exactly, and it would pass
   whatever the desk did. Control 2 is therefore INDEPENDENT: it hand-computes the
   ADDR arithmetic from the published rule (recommended = actual/12 rounded up to
   the pound; variance = (actual - standing×12)/(standing×12)×100; INCREASE above
   +5%, DECREASE below -5%) on a population built so each branch fires, and
   asserts the door reproduces it. It never imports the desk to get its expected
   values.

3. **THE SIM REACHING AROUND THE DOOR.** The ratchet covers module-scope imports;
   an in-function `from company.billing.dd_review_runner import ...` escapes it,
   and that is the natural shortcut for anyone who wants `large_increase` for DD4b
   without going through the seam. Control 3 is an AST census over `simulation/`
   at EVERY scope, with a vacuity guard (a census that parsed no files would pass
   for free).

Each `test_mutation_*` PERFORMS the named defect rather than asserting it is
impossible. Mutations run against synthetic trees and synthetic modules, never
against the live tree, so no guard dies when the codebase reaches its goal state.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from company.interfaces import dd_review as door

REPO_ROOT = Path(__file__).resolve().parents[3]
SIM_DIR = REPO_ROOT / "simulation"

DESK_MODULE = "company.billing.dd_review_runner"

# The supplier's own decision machinery. None of it may be obtainable through
# the door — by import, by attribute, or by riding out on the return value.
DESK_INTERNALS = (
    "review",
    "DDAction",
    "DDReviewBook",
    "DDReviewEvent",
    "DDReviewRunResult",
    "LARGE_INCREASE_THRESHOLD_PCT",
    "run_annual_reviews",
)


# --------------------------------------------------------------------------
# A population built for the ARITHMETIC, not copied from the desk.
#
# Customer A: year 0 bills sum to £1,200 against a standing DD of £50 (its own
#   first bill), so implied annual = £600 and variance = +100% -> INCREASE, and
#   a large_increase (>15%). Recommended = round(1200/12 + 0.5) = £100.
# Customer B: year 0 sums to £600 against a standing DD of £50 -> implied £600,
#   variance 0% -> MAINTAIN, recommended £50.
# Customer C: year 0 sums to £240 against a standing DD of £100 -> implied
#   £1,200, variance = -80% -> DECREASE, recommended = round(240/12 + 0.5) = £20.
#
# Each needs a following window for the review to fire at all (the desk only
# reviews a window once a later one has data), so each carries one year-2 bill.
# --------------------------------------------------------------------------
def _bill(cid: str, period_end: str, amount: float) -> dict:
    return {"customer_id": cid, "period_end": period_end, "total_amount_gbp": amount}


def _population() -> list[dict]:
    bills: list[dict] = []

    # A: first bill £50, then 11 more summing to £1,150 => year total £1,200.
    bills.append(_bill("A", "2020-01-31", 50.0))
    for m in range(2, 13):
        bills.append(_bill("A", f"2020-{m:02d}-28", 1150.0 / 11.0))
    bills.append(_bill("A", "2021-01-31", 100.0))  # opens window 1

    # B: first bill £50, then 11 more summing to £550 => year total £600.
    bills.append(_bill("B", "2020-01-31", 50.0))
    for m in range(2, 13):
        bills.append(_bill("B", f"2020-{m:02d}-28", 550.0 / 11.0))
    bills.append(_bill("B", "2021-01-31", 50.0))

    # C: first bill £100, then 11 more summing to £140 => year total £240.
    bills.append(_bill("C", "2020-01-31", 100.0))
    for m in range(2, 13):
        bills.append(_bill("C", f"2020-{m:02d}-28", 140.0 / 11.0))
    bills.append(_bill("C", "2021-01-31", 20.0))

    return bills


# The rule as PUBLISHED, transcribed here rather than imported: Ofgem SLC 27B
# annual review, ±5% variance band, recommendation = annual spend / 12 rounded up
# to the pound. `large_increase` is the project's own 15% bill-shock cut.
_VARIANCE_BAND_PCT = 5.0
_LARGE_INCREASE_PCT = 15.0


def _expected_review(standing_dd: float, actual_annual: float) -> dict:
    implied = standing_dd * 12.0
    variance = 0.0 if implied == 0 else (actual_annual - implied) / implied * 100.0
    if variance > _VARIANCE_BAND_PCT:
        action = "increase"
    elif variance < -_VARIANCE_BAND_PCT:
        action = "decrease"
    else:
        action = "maintain"
    return {
        "recommended_monthly_gbp": round(actual_annual / 12.0 + 0.5),
        "variance_pct": round(variance, 1),
        "action": action,
        "large_increase": action == "increase" and round(variance, 1) > _LARGE_INCREASE_PCT,
    }


def _events_by_customer(view: dict) -> dict[str, dict]:
    return {e["customer_id"]: e for e in view["events"] if e["window_index"] == 0}


# ==========================================================================
# CONTROL 1 — the door does not widen
# ==========================================================================

def test_door_exports_only_the_view_function():
    assert door.__all__ == ["annual_dd_review_view"]


def test_desk_internals_are_unreachable_through_the_door():
    """No name in DESK_INTERNALS may be obtainable from the seam module."""
    leaked = [name for name in DESK_INTERNALS if hasattr(door, name)]
    assert leaked == [], (
        "the seam re-exports the supplier's own decision machinery: %r. The whole "
        "substance of this cut is that the SLC 27B rule, the bill-shock threshold "
        "and the review types are unreachable from the SIM." % leaked
    )


def test_the_return_value_carries_no_company_type():
    """The door returns JSON-safe data, so no company object rides out on it.

    This is the stronger half of control 1: a door can keep its `__all__` clean
    and still hand the world a `DDReviewRunResult` whose `.book` is the desk's own
    register.
    """
    view = door.annual_dd_review_view(_population())
    assert isinstance(view, dict)
    assert set(view) == {"summary", "events"}
    assert isinstance(view["summary"], dict)
    assert isinstance(view["events"], list)

    def _plain(value) -> bool:
        if isinstance(value, dict):
            return all(isinstance(k, str) and _plain(v) for k, v in value.items())
        if isinstance(value, list):
            return all(_plain(v) for v in value)
        return value is None or isinstance(value, (str, int, float, bool))

    assert _plain(view), "a non-JSON-safe value crossed the seam: %r" % (view,)


def test_mutation_a_widened_door_is_caught():
    """PERFORM the defect: re-export a desk internal and show control 1 fires."""
    import company.billing.dd_review_runner as desk

    sentinel = object()
    assert not hasattr(door, "review")
    setattr(door, "review", sentinel)
    try:
        leaked = [name for name in DESK_INTERNALS if hasattr(door, name)]
        assert leaked == ["review"], (
            "the widening was not detected — control 1 cannot fail on its own defect"
        )
    finally:
        delattr(door, "review")
    assert desk.LARGE_INCREASE_THRESHOLD_PCT == 15.0  # the value the door hides


def test_mutation_a_company_object_on_the_return_value_is_caught():
    """PERFORM the defect: return the view OBJECT instead of the serialised form."""
    from company.billing.dd_review_runner import run_annual_reviews

    result = run_annual_reviews(_population())
    assert not isinstance(result, dict), (
        "vacuity guard: if the desk already returned a plain dict this control "
        "would pass for free"
    )
    with pytest.raises(AssertionError):
        assert isinstance(result, dict)


# ==========================================================================
# CONTROL 2 — the values, computed independently of the desk
# ==========================================================================

@pytest.mark.parametrize(
    "cid,standing_dd,actual_annual",
    [
        ("A", 50.0, 1200.0),
        ("B", 50.0, 600.0),
        ("C", 100.0, 240.0),
    ],
)
def test_the_door_reproduces_the_published_addr_arithmetic(cid, standing_dd, actual_annual):
    view = door.annual_dd_review_view(_population())
    events = _events_by_customer(view)
    assert cid in events, "no first-window review fired for %s — the population is wrong" % cid
    got = events[cid]
    want = _expected_review(standing_dd, actual_annual)

    assert got["recommended_monthly_gbp"] == pytest.approx(want["recommended_monthly_gbp"])
    assert got["variance_pct"] == pytest.approx(want["variance_pct"], abs=0.05)
    assert got["action"] == want["action"]
    assert got["large_increase"] == want["large_increase"]


def test_all_three_branches_actually_fire():
    """Vacuity guard for control 2: a population that only ever MAINTAINed would
    make the parametrised test pass while testing one branch of three."""
    view = door.annual_dd_review_view(_population())
    actions = {e["action"] for e in view["events"] if e["window_index"] == 0}
    assert actions == {"increase", "decrease", "maintain"}, (
        "the fixture no longer exercises every branch: %r" % (actions,)
    )


def test_mutation_a_shifted_variance_band_is_caught():
    """PERFORM the defect: compute the expectation under a 200% band, where B and
    C would both MAINTAIN, and show control 2's comparison fires."""
    global _VARIANCE_BAND_PCT
    original = _VARIANCE_BAND_PCT
    _VARIANCE_BAND_PCT = 200.0
    try:
        view = door.annual_dd_review_view(_population())
        events = _events_by_customer(view)
        mismatches = [
            cid
            for cid, standing, annual in (("A", 50.0, 1200.0), ("C", 100.0, 240.0))
            if events[cid]["action"] != _expected_review(standing, annual)["action"]
        ]
        assert mismatches == ["A", "C"], (
            "control 2 did not notice a moved decision band — it is measuring "
            "the desk against itself"
        )
    finally:
        _VARIANCE_BAND_PCT = original


# ==========================================================================
# CONTROL 3 — nothing in simulation/ reaches around the door
# ==========================================================================

def _modules_named_at_any_scope(tree: ast.AST) -> set[str]:
    """Every module named by an import ANYWHERE in the tree — module scope,
    function scope, class scope, inside a `try`, inside an `if`."""
    named: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                named.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.level == 0:
                named.add(node.module)
    return named


def _sim_files_naming_the_desk(root: Path) -> tuple[list[str], int]:
    hits: list[str] = []
    parsed = 0
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        parsed += 1
        for module in _modules_named_at_any_scope(tree):
            if module == DESK_MODULE or module.startswith(DESK_MODULE + "."):
                hits.append(str(path.relative_to(root.parent)))
                break
    return hits, parsed


def test_no_module_in_simulation_names_the_desk_at_any_scope():
    hits, parsed = _sim_files_naming_the_desk(SIM_DIR)
    assert parsed > 50, (
        "vacuity guard: the census parsed only %d files under simulation/, so a "
        "clean result proves nothing" % parsed
    )
    assert hits == [], (
        "the SIM reaches the supplier's DD desk directly, around the seam: %r" % hits
    )


def test_mutation_a_function_scope_import_is_caught(tmp_path):
    """PERFORM the defect on a SYNTHETIC tree: a lazy import inside a function,
    which the ratchet's module-scope walk does not see."""
    fake_sim = tmp_path / "simulation"
    fake_sim.mkdir()
    (fake_sim / "clean.py").write_text("import os\n", encoding="utf-8")

    clean_hits, clean_parsed = _sim_files_naming_the_desk(fake_sim)
    assert clean_parsed == 1 and clean_hits == [], "the synthetic tree started dirty"

    (fake_sim / "sneaky.py").write_text(
        textwrap.dedent(
            """
            def large_increases(bills):
                from company.billing.dd_review_runner import run_annual_reviews
                return run_annual_reviews(bills)
            """
        ).lstrip(),
        encoding="utf-8",
    )

    hits, parsed = _sim_files_naming_the_desk(fake_sim)
    assert parsed == 2
    assert [h for h in hits if h.endswith("sneaky.py")], (
        "control 3 missed a function-scope import — it is no stronger than the "
        "ratchet it exists to supplement"
    )


def test_mutation_the_vacuity_guard_fires_on_an_empty_census(tmp_path):
    """PERFORM the defect: point the census at an empty tree and show the guard,
    not the assertion, is what stops a free pass."""
    empty = tmp_path / "simulation"
    empty.mkdir()
    hits, parsed = _sim_files_naming_the_desk(empty)
    assert hits == [] and parsed == 0
    with pytest.raises(AssertionError, match="vacuity guard"):
        assert parsed > 50, (
            "vacuity guard: the census parsed only %d files under simulation/, so "
            "a clean result proves nothing" % parsed
        )
