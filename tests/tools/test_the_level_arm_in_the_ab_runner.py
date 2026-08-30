"""R15 proofs for the THIRD ARM inside the A/B runner — the level-vs-selection split.

WHY THIS FILE EXISTS. `flat_at_level` landed on 2026-08-27 as an arm with 17 tests, and the
finding it produced closed by calling the level-vs-selection gap *"a standing instrument rather
than a one-off"*. It was not one. The arm existed; the RUNNER did not know about it, so the
published 119.7% came from an ad-hoc invocation that no committed code could reproduce. Wiring it
into `run_value_cycle_ab` is what makes that sentence true, and this file is what stops the wiring
being trusted rather than proven.

THE THREE THINGS THAT COULD GO WRONG HERE, each with a proof that fires on it:

  FAIL-OPEN   — a run without the third arm publishing a level-vs-selection block that READS like
                an answer (zeros, or a silently absent key). A reader who sees `selection_gbp: 0`
                concludes the choosing was worth nothing, when in fact nothing was measured. The
                block must say `available: False` AND say why.

  TAUTOLOGY   — the level taken from a CONSTANT (the remembered 44.50) rather than from the value
                arm's own realised median in the same run. The whole point of re-running this
                after the world widens is that the arm's median is free to move; a pinned level
                would measure the pin and still produce a confident percentage.

  DIVIDE-BY-NOISE — a share reported when the value arm's advantage is at or near zero, where the
                percentage is a rounding error dressed as a result.

THE REPRODUCTION CHECK. `test_the_split_reproduces_the_published_figures` feeds the three
published nets back through the function and asserts it returns the published 119.7% and a
negative selection. That is the one assertion here that ties this code to the artefact it claims
to reproduce, rather than to its own arithmetic.
"""

import os

import pytest

from company.pricing.value_based_renewal import FLAT_AT_LEVEL
from tools import run_value_cycle_ab as rvca

#: The published full-decade figures from
#: `WORKER_FINDING_THE_VALUE_ARMS_ADVANTAGE_IS_THE_LEVEL_NOT_THE_SELECTION_2026-08-27`.
PUBLISHED_CONTROL_NET = 111_269.70
PUBLISHED_VALUE_NET = 118_335.56
PUBLISHED_LEVEL_NET = 119_724.66


def _m(net):
    return {"total_net_gbp": net}


# ---- the pure split ---------------------------------------------------------------------


def test_the_split_reproduces_the_published_figures():
    """The arithmetic ties to the artefact, not merely to itself."""
    out = rvca.level_vs_selection(
        _m(PUBLISHED_CONTROL_NET), _m(PUBLISHED_VALUE_NET), _m(PUBLISHED_LEVEL_NET), 44.5)

    assert out["available"] is True
    # 119.7% as published, to the tenth of a percent it was published at.
    assert round(out["level_share_of_advantage"] * 100, 1) == 119.7
    # The selection is worth LESS THAN NOTHING, which is the finding's actual claim.
    assert out["selection_gbp"] < 0
    assert out["selection_gbp"] == pytest.approx(-1_389.10, abs=0.01)
    assert out["value_advantage_gbp"] == pytest.approx(7_065.86, abs=0.01)
    assert out["level_advantage_gbp"] == pytest.approx(8_454.96, abs=0.01)


def test_a_run_WITHOUT_the_level_arm_says_so_instead_of_publishing_zeros():
    """FAIL-OPEN. The most reassuring wrong answer available is `selection_gbp: 0`."""
    out = rvca.level_vs_selection(_m(100.0), _m(110.0), None, None)

    assert out["available"] is False
    assert "--level-arm" in out["why_not"]
    # Not merely falsy — the figures must be ABSENT, so nothing can be read off them.
    for key in ("selection_gbp", "level_share_of_advantage", "level_arm_net_gbp"):
        assert key not in out


def test_a_near_zero_advantage_yields_NO_share_and_names_the_reason():
    """DIVIDE-BY-NOISE. A share of GBP 0.20 of advantage is not a result."""
    out = rvca.level_vs_selection(_m(100.0), _m(100.20), _m(105.0), 44.5)

    assert out["level_share_of_advantage"] is None
    assert "noise" in out["share_undefined_reason"]
    # The selection figure stays readable — it does not need the denominator.
    assert out["selection_gbp"] == pytest.approx(-4.80, abs=0.01)


def test_the_share_IS_reported_once_the_advantage_is_real():
    """The other half of the mutation: the guard must not swallow a genuine result."""
    out = rvca.level_vs_selection(_m(100.0), _m(1_100.0), _m(1_600.0), 44.5)

    assert out["level_share_of_advantage"] == pytest.approx(1.5)
    assert out["share_undefined_reason"] is None


def test_the_enterprise_value_reading_is_WITHHELD_and_not_published_beside_the_net():
    """It is a TAUTOLOGY, not a second clock — EV re-scores the book under the arm's own model.

    A future edit that "completes" this block by adding the EV delta beside the realised one is
    the exact error the finding named as the more dangerous of the two available.
    """
    out = rvca.level_vs_selection(
        _m(PUBLISHED_CONTROL_NET), _m(PUBLISHED_VALUE_NET), _m(PUBLISHED_LEVEL_NET), 44.5)

    assert not any("enterprise_value" in k for k in out)
    assert "settled net margin" in out["basis"]


# ---- the wiring, which is where a typo would cost a 40-minute run -----------------------


@pytest.fixture()
def wired(monkeypatch):
    """Replace every heavy reporter so the test observes the ORCHESTRATION and nothing else.

    Deliberately NOT a real run: the fault this guards against is a wrong policy field or a level
    read from the wrong place, and both are visible in the calls without settling a decade.
    """
    calls = []

    def fake_run_phase4c(report_end=None, policy=None):
        calls.append(policy)
        return {"phase2b": {}, "_name": policy.name}

    nets = {"current": 111_269.70, "value_arm": 118_335.56, "level_arm": 119_724.66}

    def fake_metrics(result):
        m = dict.fromkeys(
            ("enterprise_value_gbp", "account_count", "churned_accounts",
             "total_gross_margin_gbp", "total_bad_debt_gbp"), 0.0)
        m["total_net_gbp"] = nets[result["_name"]]
        return m

    monkeypatch.setattr(rvca, "run_phase4c", fake_run_phase4c)
    monkeypatch.setattr(rvca, "realised_metrics", fake_metrics)
    # DELIBERATELY NOT 44.50. A fixture whose median equals the published constant cannot
    # see a level that was pinned to that constant — the mutation would survive and the
    # tautology proof below would be theatre (the fallback-value fixture pattern).
    monkeypatch.setattr(
        rvca, "arm_decision_shape",
        lambda r: {"priced": 25, "median_margin_gbp_per_mwh": 61.25})
    for name in ("book_identity", "gross_to_net_bridge", "churn_volume_attribution",
                 "bound_attribution", "belief_vs_outcome", "churn_roster_diff",
                 "margin_movers"):
        monkeypatch.setattr(rvca, name, lambda *a, **k: {})
    monkeypatch.setattr(rvca, "cross_section_reconciliation", lambda *a, **k: {})
    monkeypatch.setattr(rvca, "control_credibility", lambda *a, **k: {})
    return calls


def test_the_level_arm_is_NOT_run_unless_asked_for(wired):
    """A third full pass is a third of the cost — it must be opt-in."""
    result = rvca.run_value_cycle_ab(level_arm=False)

    assert [p.name for p in wired] == ["current", "value_arm"]
    assert result["level_arm"] is None
    assert result["level_vs_selection"]["available"] is False


def test_the_level_arm_runs_THIRD_at_the_value_arms_OWN_median(wired):
    """TAUTOLOGY guard. The level must come from this run, not from a remembered constant."""
    result = rvca.run_value_cycle_ab(level_arm=True)

    assert [p.name for p in wired] == ["current", "value_arm", "level_arm"]
    level_policy = wired[2]
    assert level_policy.renewal_margin_arm == FLAT_AT_LEVEL
    # THE ASSERTION THAT FIRES ON A PINNED CONSTANT: it is the median the value arm just
    # published, and it reaches the policy field the chain actually resolves.
    assert level_policy.renewal_margin_flat_level_gbp_per_mwh == 61.25
    assert result["level_vs_selection"]["level_gbp_per_mwh"] == 61.25
    assert round(result["level_vs_selection"]["level_share_of_advantage"] * 100, 1) == 119.7


def test_the_level_arm_differs_from_the_CONTROL_in_exactly_the_two_arm_fields(wired):
    """Any third differing field means the residual carries an uncontrolled variable."""
    rvca.run_value_cycle_ab(level_arm=True)
    level_policy = wired[2]
    control_policy = wired[0]

    differing = sorted(
        f for f in control_policy.__dataclass_fields__
        if getattr(control_policy, f) != getattr(level_policy, f))
    assert differing == ["name", "renewal_margin_arm",
                         "renewal_margin_flat_level_gbp_per_mwh"]


def test_a_value_arm_that_published_NO_median_refuses_rather_than_assuming_a_level(
        wired, monkeypatch):
    """FAIL-OPEN. Running the third arm at an assumed level answers a question nobody asked."""
    monkeypatch.setattr(rvca, "arm_decision_shape",
                        lambda r: {"priced": 0, "median_margin_gbp_per_mwh": None})

    with pytest.raises(AssertionError, match="no median margin"):
        rvca.run_value_cycle_ab(level_arm=True)

    # And it refused BEFORE spending the pass, which is the point of raising here.
    assert [p.name for p in wired] == ["current", "value_arm"]


# ---- the population axis of the same wiring --------------------------------------------
#
# `arm_identity` refuses a third differing POLICY field (above). Nothing refused a second
# BOOK until `same_book_across_arms` landed, and the two are the same class of defect:
# a delta across two populations is a delta with an uncontrolled variable in it. The finding
# is WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26.


def test_the_run_publishes_a_same_book_verdict_a_reader_can_check(wired):
    """The check is IN the artefact, not only in the run. A reader of a downloaded file has
    no way to know a refusal path existed unless its verdict is on the page with the books."""
    result = rvca.run_value_cycle_ab(level_arm=True)

    agreement = result["book_identity"]["same_book_across_arms"]
    assert agreement["same_book"] is True
    assert agreement["arms_compared"] == ["control_arm", "level_arm", "value_arm"]
    assert len(agreement["distinct_books"]) == 1


def test_two_arms_on_two_books_are_REFUSED_rather_than_reported(wired, monkeypatch):
    """The reachable failure, end to end. An arm is a full phase-4c pass — minutes — and the
    served segments resolve from a file on EVERY call, so a curriculum edit or an override
    change between the control arm and the value arm genuinely puts the two arms on two
    books. Reading the resolver once at the end reports the second book for both of them and
    the delta reads clean; this is the mutation that proves it no longer can."""
    def flip_the_book_after_the_first_arm(report_end=None, policy=None):
        wired.append(policy)
        os.environ["SE_SERVED_SEGMENTS"] = "resi" if len(wired) == 1 else "resi,SME"
        return {"phase2b": {}, "_name": policy.name}

    monkeypatch.setattr(rvca, "run_phase4c", flip_the_book_after_the_first_arm)
    monkeypatch.setenv("SE_SERVED_SEGMENTS", "resi")

    with pytest.raises(AssertionError, match="did not serve one book"):
        rvca.run_value_cycle_ab()

    # Both arms ran — the refusal is on the comparison, not on the second pass.
    assert [p.name for p in wired] == ["current", "value_arm"]
