"""The world's run holds no `DecisionPolicy` — KNIFE3 step 39, register §3ah.

WHAT THIS GUARDS
----------------
`simulation/run_phase2b.py` was the last module with a live wall crossing into
`company.policy.decision_policy`, and it was the last owed row of
`A_composition_lift`. Its `main()` took the supplier's own decision object as a
parameter and read four fields off it inline:

  * `policy.retention_discount_for_risk(...)`   — how big a retention discount
  * `policy.include_acq_cost_saved_in_guard`    — the Phase-15b offer guard term
  * `framing_type_for(policy, ...)`             — the comms-framing cohort split
  * `policy.use_var_hedge_decision`             — the Phase-43b VaR hedge switch

All four now resolve on the company side of a door, from the run's ACTIVE
policy. A counterfactual arm enters `policy_scope(...)`; the world never holds,
names, defaults or type-annotates a policy.

THREE NAMED DEFECTS, each with a control that fires on it
---------------------------------------------------------
1. THE CROSSING COMES BACK — an `ast` walk for any `company.policy` import in
   the world's run modules, with a FAIL-OPEN guard proving the walker descends
   into function bodies. A function-scope import is the realistic regression
   (it is the shape `decide_term_hedge` itself uses), and `build_edges` sees
   those too, so a control that only checked module scope would be weaker than
   the ratchet it is meant to back up.

2. THE PARAMETER COMES BACK — the signature itself. A `policy=` parameter is
   how the crossing returns without an import: a caller passes an object the
   world then reads fields off. Checked on the real signatures, not on a
   docstring claim.

3. THE DOOR IS NOMINAL — each of the four fields is driven through its REAL
   call path under both arms and required to differ. This is the half that
   catches a door which resolves a pinned constant instead of the run's policy,
   which is `WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE`'s defect one
   layer along. Each has a vacuity guard showing the two policies actually
   disagree on the field, so a probe cannot pass by measuring nothing.

WHAT THIS FILE DELIBERATELY DOES NOT DO
---------------------------------------
It does not re-run the decade and compare outputs. Two arms of a full replay
differ for many reasons, and a before/after comparison of the SAME expression
is R15's TAUTOLOGY pattern — it would pass whatever the doors did. The
behavioural claims here are made against the doors' own values under a scope,
which is the quantity that actually changed.
"""

from __future__ import annotations

import ast
import inspect
import warnings
from pathlib import Path

import pytest

from company.interfaces.growth_desk import (
    offer_framing_for,
    replacement_cost_avoided_gbp,
    retention_discount_for_risk,
)
from company.interfaces.hedge_desk import build_hedge_desk
from company.policy.decision_policy import (
    CURRENT_POLICY,
    NAIVE_POLICY,
    policy_scope,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

# The world's run modules — the composition roots this design spent 39 steps
# unwinding. `run_phase2b` is the one the edge was on; `run_phase4c_on_phase2b`
# is included because it FORWARDED the parameter, so it is the other half of the
# same regression.
RUN_MODULES = (
    REPO_ROOT / "simulation" / "run_phase2b.py",
    REPO_ROOT / "simulation" / "run_phase4c_on_phase2b.py",
)


def _policy_imports(source: str) -> list[str]:
    """Every import of `company.policy.*` anywhere in a module, function bodies
    included.

    `ast.walk` rather than a scan of `tree.body`, for the reason recorded in
    §3aa: a function-scope import is invisible to a module-scope-only walker and
    is exactly how a cut edge comes back. `tools/epistemic_wall.py::build_edges`
    walks the same way, so this control and the ratchet agree about what an
    import is.
    """
    hits: list[str] = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and (node.module or "").startswith(
            "company.policy"
        ):
            names = ", ".join(a.name for a in node.names)
            hits.append(f"line {node.lineno}: from {node.module} import {names}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith("company.policy"):
                    hits.append(f"line {node.lineno}: import {alias.name}")
    return hits


# ---------------------------------------------------------------------------
# 1. The crossing comes back
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("path", RUN_MODULES, ids=lambda p: p.name)
def test_the_run_does_not_import_the_companys_policy(path):
    hits = _policy_imports(path.read_text(encoding="utf-8"))
    assert not hits, (
        f"{path.name} imports the supplier's decision policy again — this was "
        f"A_composition_lift's last wall crossing (register §3ah). The fields "
        f"belong behind company/interfaces/growth_desk.py and the hedge desk:\n  "
        + "\n  ".join(hits)
    )


def test_the_import_walker_sees_function_scope_imports():
    """FAIL-OPEN GUARD. A module-scope-only walker would pass the test above
    while the realistic regression sat inside `main()`. Prove the walker
    descends — and use the exact shape the desk itself uses, so this is not a
    synthetic case that no one would write."""
    source = (
        "def main(report_end=None):\n"
        "    from company.policy.decision_policy import active_policy\n"
        "    return active_policy()\n"
    )
    hits = _policy_imports(source)
    assert hits, "the walker does not descend into function bodies — it is fail-open"
    assert "active_policy" in hits[0]


def test_the_walker_has_a_population_to_walk():
    """VACUITY GUARD. The parametrized test passes trivially if the paths are
    wrong — a moved module, a renamed tree. Assert both files exist and are the
    real thing."""
    for path in RUN_MODULES:
        assert path.is_file(), f"{path} is missing — this control is scanning nothing"
        assert "def main(" in path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 2. The parameter comes back
# ---------------------------------------------------------------------------

def test_neither_run_entry_point_accepts_a_policy():
    """The import is one way back; the PARAMETER is the other, and it needs no
    import at all in the callee — a caller hands over the object and the world
    reads fields off it. Both entry points are checked because
    `run_phase4c_on_phase2b.main` forwarded the argument down."""
    from simulation.run_phase2b import main as run_phase2b
    from simulation.run_phase4c_on_phase2b import main as run_phase4c

    for fn, name in ((run_phase2b, "run_phase2b"), (run_phase4c, "run_phase4c_on_phase2b")):
        params = set(inspect.signature(fn).parameters)
        assert "policy" not in params, (
            f"{name}.main regained a `policy` parameter. A counterfactual arm sets "
            f"company.policy.decision_policy.policy_scope(...) — the world is not "
            f"handed the supplier's decision object (register §3ah)."
        )


def test_the_signature_check_can_fail():
    """MUTATION. Perform the defect on a stand-in with the same shape and prove
    the assertion above fires, rather than trusting that `not in` works."""
    def main_with_policy(report_end=None, sim_interface=None, policy=None):
        return policy

    assert "policy" in set(inspect.signature(main_with_policy).parameters), (
        "the signature check cannot fail: a function that plainly takes `policy` "
        "did not report it"
    )


# ---------------------------------------------------------------------------
# 3. The doors are not nominal — every field switches with the run
# ---------------------------------------------------------------------------

def _both_arms(probe):
    with policy_scope(CURRENT_POLICY):
        current = probe()
    with policy_scope(NAIVE_POLICY):
        naive = probe()
    return current, naive


def test_the_retention_discount_switches_with_the_run():
    """CURRENT is tiered (8% at high risk); NAIVE is a flat 5%. 0.80 is chosen
    because it is above CURRENT's top tier — at 0.55 both policies pay 5% and
    the probe would witness nothing."""
    assert CURRENT_POLICY.retention_discount_mode != NAIVE_POLICY.retention_discount_mode
    current, naive = _both_arms(lambda: retention_discount_for_risk(0.80))
    assert current == 0.08, f"CURRENT arm's high-risk discount is {current}, not the 8% tier"
    assert naive == 0.05, f"NAIVE arm's discount is {naive}, not its flat 5%"


def test_the_offer_guard_credit_switches_with_the_run():
    """The whole effect of `include_acq_cost_saved_in_guard`: CURRENT credits the
    segment's replacement cost, NAIVE credits nothing. Asserted as ZERO rather
    than "smaller", because a door that merely scaled the credit would pass a
    less-than check and still be the wrong policy."""
    assert (
        CURRENT_POLICY.include_acq_cost_saved_in_guard
        != NAIVE_POLICY.include_acq_cost_saved_in_guard
    )
    current, naive = _both_arms(lambda: replacement_cost_avoided_gbp(segment="resi"))
    assert current == 150.0
    assert naive == 0.0


def test_the_offer_framing_switches_with_the_run():
    """CURRENT splits offers across two framings; NAIVE fixes one. Measured over
    a sample rather than a single call: `("C0001", "2023-01-31")` alone returns
    'gain_framed' under BOTH policies — the pair lands on the gain side of
    CURRENT's sha256 split, and 'gain_framed' is NAIVE's fixed value — so a
    one-call probe reports a pin that is not there."""
    sample = [
        ("C0001", "2023-01-31"), ("C0042", "2023-06-30"), ("C0777", "2024-11-30"),
        ("C1234", "2022-03-31"), ("C9999", "2025-09-30"), ("C0003", "2021-07-31"),
    ]
    current, naive = _both_arms(
        lambda: frozenset(offer_framing_for(c, d) for c, d in sample)
    )
    assert current == frozenset({"loss_framed", "gain_framed"}), (
        f"the sample stopped covering both CURRENT cohorts ({sorted(current)}), so "
        f"this assertion proves less than it appears to"
    )
    assert naive == frozenset({"gain_framed"}), (
        f"the naive arm split its retention offers: {sorted(naive)}"
    )


def _decide(current_fraction: float = 0.5):
    price_records = [
        {"date": f"2023-{m:02d}-01", "price_gbp_per_mwh": 80.0 + m} for m in range(1, 13)
    ]
    return build_hedge_desk().decide_term_hedge(
        customer_id="C0001",
        term_start="2023-01-01",
        term_end="2023-12-31",
        commodity="electricity",
        volume_kwh=3000.0,
        forward_price_gbp_per_mwh=85.0,
        unit_rate_gbp_per_mwh=110.0,
        price_records=price_records,
        term_days=364,
        current_fraction=current_fraction,
        accept_decision=True,
    )


def test_the_var_hedge_layer_switches_with_the_run():
    """CURRENT runs the Phase-43b VaR layer; NAIVE leaves the backward-looking
    evolved fraction alone. The desk answers `None` in the naive arm, which is
    what the world's `if _elec_hedge is not None` reads."""
    assert CURRENT_POLICY.use_var_hedge_decision != NAIVE_POLICY.use_var_hedge_decision
    current, naive = _both_arms(_decide)
    assert current is not None, "the CURRENT arm's desk declined to take a VaR decision"
    assert naive is None, (
        "the NAIVE arm's desk took a VaR decision — its policy switches that layer "
        "off, and the world can no longer gate the call itself"
    )


def test_a_declined_decision_is_distinguishable_from_a_committee_override():
    """The design's own stated reason for `None` rather than
    `decision_accepted=False`. A committee-overridden term STILL carries a
    `var_log_entry` reporting the risk actually run; a term where the layer is
    off carries none, because no decision was taken. Collapsing the two would
    put a decade of undecided rows into `hedge_var_log` in the naive arm."""
    with policy_scope(CURRENT_POLICY):
        overridden = build_hedge_desk().decide_term_hedge(
            customer_id="C0001",
            term_start="2023-01-01",
            term_end="2023-12-31",
            commodity="electricity",
            volume_kwh=3000.0,
            forward_price_gbp_per_mwh=85.0,
            unit_rate_gbp_per_mwh=110.0,
            price_records=[
                {"date": f"2023-{m:02d}-01", "price_gbp_per_mwh": 80.0 + m}
                for m in range(1, 13)
            ],
            term_days=364,
            current_fraction=0.5,
            accept_decision=False,
        )
    assert overridden is not None, "a committee override must still report its risk"
    assert overridden.decision_accepted is False
    assert overridden.var_log_entry, "an overridden term lost its VaR log entry"
    assert overridden.hedge_fraction == 0.5, (
        "the committee's fraction did not survive the model's decision"
    )

    with policy_scope(NAIVE_POLICY):
        assert _decide() is None


def test_outside_any_scope_every_door_gives_the_live_answer():
    """The cut must not move an ordinary run. Every caller except the frozen
    baseline enters no scope, so each door must return exactly what the live
    policy says — this is the byte-for-byte identity claim §3ah rests on."""
    assert retention_discount_for_risk(0.80) == 0.08
    assert replacement_cost_avoided_gbp(segment="resi") == 150.0
    assert _decide() is not None
