"""Guard tests for the tenure→adoption per-asset SENSITIVITY diagnostic
(tools/tenure_adoption_sensitivity.py, FROM_AGENT_SEGMENTATION_INTEGRATION_
FOLLOWON item 3). Fast (small population); locks the invariants that make the
diagnostic trustworthy so a silent regression fails the suite."""
import pytest

from tools import tenure_adoption_sensitivity as S

_ASSETS = ("solar_pv", "ev", "heat_pump")


@pytest.fixture(scope="module")
def pop():
    # Small but enough to have a non-trivial eligible base for each asset.
    return S._population(2000)


@pytest.mark.parametrize("asset", _ASSETS)
def test_eligible_base_is_nonempty(pop, asset):
    assert len(S._structurally_eligible(pop, asset)) > 0


@pytest.mark.parametrize("asset", _ASSETS)
def test_rate_is_zero_at_zero_and_one_at_one(pop, asset):
    eligible = S._structurally_eligible(pop, asset)
    assert S._adoption_rate(eligible, asset, 0.0) == 0.0
    # every eligible household adopts in its ungated realization -> rate 1.0
    assert S._adoption_rate(eligible, asset, 1.0) == 1.0


@pytest.mark.parametrize("asset", _ASSETS)
def test_rate_is_monotone_nondecreasing_in_m(pop, asset):
    eligible = S._structurally_eligible(pop, asset)
    grid = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
    rates = [S._adoption_rate(eligible, asset, m) for m in grid]
    for lo, hi in zip(rates, rates[1:]):
        assert hi >= lo, f"{asset} adoption rate not monotone in m: {rates}"


def test_a_lower_factor_strictly_reduces_adoption_vs_ungated(pop):
    # The whole point of the dial: a materially lower factor must reduce the
    # renter adoption rate below the ungated base for at least one asset.
    eligible = S._structurally_eligible(pop, "heat_pump")
    assert S._adoption_rate(eligible, "heat_pump", 0.14) < 1.0


def test_report_renders_all_three_assets():
    report = S.build_report(n=1500)
    for asset in _ASSETS:
        assert asset in report
    assert "DIAGNOSTIC" in report
    # honesty: the downstream-deferral caveat must be present
    assert "item 5" in report
