"""The world's churn ceiling is the WORLD's, and the control proves it can fail.

Guards the cut recorded as `docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`
§3g: `simulation.satisfaction_churn -> saas.churn_model` — the world clamping
its own ground-truth churn probability at the company's constant, so the
company's belief about the ceiling WAS the ceiling.

WHAT IS ASSERTED, AND WHAT DELIBERATELY IS NOT
----------------------------------------------
NOT asserted: that `WORLD_MAX_CHURN_PROBABILITY == saas.churn_model.
MAX_CHURN_PROBABILITY`. Pinning them equal would restore in the suite exactly
the coupling the cut removes from the code — the refusal recorded for `B3` (the
cap schedule) and `B7` (the hedge floor). The readings may drift; that is a
finding to report, never a gate (R12).

Asserted instead — INDEPENDENCE, by mutation, which is the property the cut
actually bought:

  * mutating the COMPANY's ceiling does not move the WORLD's clamp, and
  * the same mutation demonstrably DOES move the company's own answer.

The second is the vacuity guard, and it is not decoration. Without it this file
would pass just as happily against a company constant nothing reads — the
`donated residual is not a control` shape. The mutation has to be shown to bite
somewhere before "it did not bite here" means anything.

R15 note on where this runs. `tools/pre_commit_test_gate.py` maps a changed
`simulation/churn_ceiling.py` to `tests/**/test_churn_ceiling*.py`, so this file
is selected whenever the ceiling itself is touched. The case it cannot see —
someone re-adding `from saas.churn_model import ...` to a sim module without
touching the ceiling — is the WALL RATCHET's job, and that is why the ratchet
was added to that gate's always-run control set in the same commit rather than
left to per-file selection.
"""
import importlib

import pytest

import saas.churn_model
import simulation.satisfaction_churn as satisfaction_churn
import simulation.switching_propensity as switching_propensity
from simulation.churn_ceiling import WORLD_MAX_CHURN_PROBABILITY
from simulation.household import IncomeStress


def test_the_world_ceiling_is_a_probability():
    assert 0.0 < WORLD_MAX_CHURN_PROBABILITY <= 1.0


def test_the_world_clamp_actually_binds():
    """Vacuity guard for every test below: the ceiling has to be reachable.

    A clamp that no input can reach makes every independence claim about it
    vacuously true.
    """
    adjusted = satisfaction_churn.adjust_churn_for_satisfaction(0.99, 0.10)
    assert adjusted == pytest.approx(WORLD_MAX_CHURN_PROBABILITY), (
        "a base probability of 0.99 with the low-satisfaction multiplier should "
        "hit the world ceiling; if it does not, the tests below prove nothing"
    )


def test_mutating_the_companys_ceiling_does_not_move_the_worlds(monkeypatch):
    """THE CUT. Fails if any sim module reads the company's constant again."""
    before = satisfaction_churn.adjust_churn_for_satisfaction(0.99, 0.10)

    monkeypatch.setattr(saas.churn_model, "MAX_CHURN_PROBABILITY", 0.10)
    importlib.reload(satisfaction_churn)
    try:
        after = satisfaction_churn.adjust_churn_for_satisfaction(0.99, 0.10)
    finally:
        monkeypatch.undo()
        importlib.reload(satisfaction_churn)

    assert after == pytest.approx(before), (
        "the world's churn ceiling moved when the COMPANY's constant was "
        "mutated -- the company's belief is constituting the world's physics "
        "again (register §3g, B2's shape)"
    )
    assert after == pytest.approx(WORLD_MAX_CHURN_PROBABILITY)


def test_the_same_mutation_does_move_the_companys_own_answer(monkeypatch):
    """VACUITY GUARD for the test above: prove the mutation bites somewhere.

    If mutating `MAX_CHURN_PROBABILITY` changed nothing anywhere, "it did not
    change the world" would be a statement about a dead constant, not about
    independence.
    """
    monkeypatch.setattr(saas.churn_model, "MAX_CHURN_PROBABILITY", 0.10)
    # 100 bill shocks: far past the company's real cap, so the clamp decides
    # the answer and the mutation is visible in it.
    assert saas.churn_model.churn_probability(100) == pytest.approx(0.10), (
        "mutating the company's ceiling did not move the company's own capped "
        "estimate -- this control is measuring nothing"
    )


def test_the_world_ceiling_has_one_home_across_the_sim():
    """`one name, two numbers` guard: the sim's copies are the same object.

    The world expressed this ceiling three ways before the cut. Two of them are
    now aliases of the third; this fails if a private copy is reintroduced and
    silently drifts.
    """
    assert switching_propensity._MAX_CHURN_PROBABILITY == WORLD_MAX_CHURN_PROBABILITY

    capped = switching_propensity.adjust_churn_probability(
        0.99, IncomeStress.LOW, tenure="owner_occupier"
    )
    assert capped <= WORLD_MAX_CHURN_PROBABILITY


def test_no_sim_module_names_the_companys_churn_constant():
    """The named-edge control, asked of the WALKER rather than of a substring.

    A substring scan fails on its own subject here: the docstrings recording
    *why* the import went away contain both `saas.churn_model` and
    `MAX_CHURN_PROBABILITY` (the `REVIEW_GATE must match idleness, not prose
    mentioning the string` class, which bit this programme once already at §3a).
    So this asks `tools.epistemic_wall.live_crossings()` — the one definition of
    "a crossing" this pass extracted as its first step.
    """
    from tools.epistemic_wall import live_crossings

    assert ("simulation.satisfaction_churn", "saas.churn_model") not in live_crossings()
