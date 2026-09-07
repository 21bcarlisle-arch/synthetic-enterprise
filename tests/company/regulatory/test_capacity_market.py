"""The supplier-side Capacity Market charge: a levy on demand, read not derived.

WHAT THIS FILE HAD TO CHANGE FOR (2026-09-07, a51-derating-callers-and-the-dsr-cmu-shape). The
module under test carried `_DERATING_FACTOR = 0.92  # Assumed average de-rated supply margin %`
applied to a SUPPLIER obligation -- an invented constant named for a concept that does not apply to
the quantity it multiplied, because de-rating is a haircut on a capacity PROVIDER's capacity and
demand is not de-rated. Beside it, `_CM_OBLIGATION_RATE_BY_YEAR` was a fourth home for the CM
clearing price, ending in a `.get(year, _RATE[2025])` fail-open.

TWO OF THE CONTROLS IN THIS FILE ASSERTED THOSE DEFECTS AS THE CONTRACT, which is why they are gone
rather than adjusted:

  * `test_derating_factor_reduces_obligation` recomputed `gross_kw * 0.92` and asserted the module
    agreed. Keyed to today's answer, so it would have gone red the moment the constant became more
    honest and stayed green for as long as 0.92 was wrong -- exactly backwards.
  * `test_cm_obligation_unknown_year_uses_2025_rate` asserted that an UNRECOGNISED year returns the
    2025 rate, i.e. it pinned the fail-open default as the intended behaviour. A control can make a
    defect permanent by describing it, and this one did.

`test_crisis_year_higher_rate` and `test_cm_obligation_2021_rate` read the deleted price table and
are replaced by legs over the published levy, which is a different series that moves differently --
2022 is the case that matters and it moves the OTHER WAY.
"""
import pytest

from company.regulatory.capacity_market import (
    _LEVY_GBP_PER_MWH,
    _PENALTY_DIVISOR,
    cm_charge_per_mwh,
    cm_levy_gbp_per_mwh,
    compute_cm_obligation,
)


def test_obligation_structure():
    result = compute_cm_obligation(2024, 10_000_000)
    assert result.year == 2024
    assert result.obligation_kw > 0
    assert result.annual_charge_gbp > 0


def test_annual_charge_scales_with_demand():
    r1 = compute_cm_obligation(2024, 1_000_000)
    r2 = compute_cm_obligation(2024, 2_000_000)
    assert r2.annual_charge_gbp > r1.annual_charge_gbp


def test_delivered_when_firm_capacity_meets_obligation():
    result = compute_cm_obligation(2024, 1_000_000, firm_capacity_kw=999_999)
    assert result.delivery_status == "DELIVERED"
    assert result.penalty_gbp == 0.0


def test_failed_when_no_firm_capacity():
    result = compute_cm_obligation(2024, 10_000_000, firm_capacity_kw=0)
    assert result.delivery_status == "FAILED"


def test_penalty_zero_when_delivered():
    result = compute_cm_obligation(2024, 1_000_000, firm_capacity_kw=999_999)
    assert result.penalty_gbp == 0.0


def test_cm_charge_per_mwh_positive():
    charge = cm_charge_per_mwh(2024, 5_000_000)
    assert charge > 0


def test_cm_charge_per_mwh_zero_demand():
    charge = cm_charge_per_mwh(2024, 0)
    assert charge == 0.0


def test_shortfall_when_partial():
    result = compute_cm_obligation(2024, 10_000_000, firm_capacity_kw=1)
    assert result.shortfall_kw > 0


def test_every_delivery_status_branch_is_reachable():
    """The defect: a rarely-taken branch that no input can actually reach.

    This replaces `test_partial_delivery_status`, which hard-coded `firm_capacity_kw=15_500`
    against an `obligation_kw` that included the removed 0.92 factor. Once the factor went, 15,500
    fell outside the PARTIAL band and the test read FAILED. RE-TUNING THAT NUMBER UNTIL IT AGREED
    would have fitted the fixture to the conclusion and left it just as brittle; the firm capacity
    is now DERIVED from the branch's own definition, so it tracks any future change to the sizing.

    Asserted as a partition over the whole space rather than one leg per branch: a status function
    that returned 'FAILED' for everything would pass a PARTIAL-only test that had been re-tuned
    until it didn't.
    """
    obligation = compute_cm_obligation(2024, 87_600).obligation_kw
    statuses = {
        compute_cm_obligation(2024, 87_600, firm_capacity_kw=firm).delivery_status
        for firm in (
            obligation,                    # no shortfall      -> DELIVERED
            obligation * 0.95,             # shortfall < 10%   -> PARTIAL
            0.0,                           # whole obligation  -> FAILED
        )
    }
    assert statuses == {"DELIVERED", "PARTIAL", "FAILED"}, (
        f"only reached {statuses}; a branch no input can take is not a branch")


def test_penalty_formula():
    result = compute_cm_obligation(2024, 87_600, firm_capacity_kw=0)
    levy = cm_levy_gbp_per_mwh(2024)
    expected = round((result.shortfall_kw / 1000.0) * (levy / _PENALTY_DIVISOR), 2)
    assert result.penalty_gbp == pytest.approx(expected)


# --- The de-rating verdict for this module, 2026-09-07 (a51). The answer was NO FACTOR, because
# --- the concept does not apply to a supplier obligation -- not because none was available.


def test_no_derating_factor_is_applied_to_a_supplier_obligation():
    """The defect: a de-rating factor applied to demand, which is never de-rated.

    Keyed to the PROPERTY -- peak-period demand is the raw peak estimate with no haircut -- rather
    than to any particular factor, so it fails for ANY multiplier a future edit reintroduces,
    including one read legitimately from the published register.
    """
    demand_mwh = 1_000_000
    result = compute_cm_obligation(2024, demand_mwh)
    undiscounted_peak_kw = round((demand_mwh / 8760.0) * 1.8 * 1000, 1)
    assert result.obligation_kw == pytest.approx(undiscounted_peak_kw, abs=1.0), (
        f"obligation_kw {result.obligation_kw} is not the raw peak estimate "
        f"{undiscounted_peak_kw} -- something is de-rating a demand quantity")


def test_the_charge_is_the_published_levy_times_volume_and_nothing_else():
    """The defect: deriving a supplier levy from an auction clearing price.

    The identity is the control. If any factor, peak estimate or price re-enters the money path
    this fails, and it cannot pass vacuously because the levy is asserted non-trivial first.
    """
    levy = cm_levy_gbp_per_mwh(2023)
    assert levy is not None and levy > 1.0, "reachability: the levy must be a real published rate"
    result = compute_cm_obligation(2023, 5_000_000)
    assert result.annual_charge_gbp == pytest.approx(5_000_000 * levy)
    assert cm_charge_per_mwh(2023, 5_000_000) == pytest.approx(levy)
    # ...and the per-MWh charge is volume-invariant, which a peak-times-price route was not.
    assert cm_charge_per_mwh(2023, 50_000) == pytest.approx(cm_charge_per_mwh(2023, 50_000_000))


def test_the_published_levy_falls_in_2022_when_the_clearing_price_hit_its_cap():
    """The defect: a levy modelled off a clearing price gets 2022 backwards.

    The T-1 for delivery year 2022/23 cleared at the GBP75/kW price CAP -- the highest number in
    the whole auction record -- and the supplier levy FELL, because the volume behind that price
    was small and the suspended T-4's replacement T-3 was cheap. This is the single year that
    proves the two series are different quantities rather than one series in different units, and
    the deleted table asserted the opposite (`test_crisis_year_higher_rate`).
    """
    assert cm_levy_gbp_per_mwh(2022) < cm_levy_gbp_per_mwh(2021)
    assert cm_levy_gbp_per_mwh(2022) < cm_levy_gbp_per_mwh(2023)


def test_an_unpublished_year_refuses_instead_of_carrying_the_last_rate_forward():
    """The defect: `.get(year, _RATE[2025])` making an unpublished year look established.

    Both legs: the refusal fires for a year outside the record AND names the record's range, and
    a year inside it still answers -- a guard that refused everything would pass a one-sided test.
    """
    assert cm_levy_gbp_per_mwh(9999) is None
    assert cm_levy_gbp_per_mwh(max(_LEVY_GBP_PER_MWH)) is not None
    with pytest.raises(ValueError) as excinfo:
        compute_cm_obligation(9999, 1_000_000)
    assert str(max(_LEVY_GBP_PER_MWH)) in str(excinfo.value), (
        "a refusal must name the record it is refusing against")


def test_the_module_no_longer_holds_its_own_copy_of_the_clearing_price():
    """The defect: a fourth home for the CM clearing price.

    The register's DY2024 T-4 cleared at GBP18.00/kW and this module used to carry 65.00 under the
    key 2024. Asserted as an ABSENCE of the symbol, because the failure mode is a well-meaning
    edit reinstating a local table 'for convenience'.
    """
    import company.regulatory.capacity_market as mod

    assert not hasattr(mod, "_CM_OBLIGATION_RATE_BY_YEAR")
    assert not hasattr(mod, "_DERATING_FACTOR")
    # ...and the levy it does hold is in GBP/MWh, an order of magnitude away from any GBP/kW
    # clearing price, so a re-introduced price could not masquerade as this series.
    assert all(0.1 < rate < 20.0 for rate in _LEVY_GBP_PER_MWH.values())


def test_a_malformed_commons_raises_rather_than_degrading_to_no_levy(tmp_path, monkeypatch):
    """The defect: a missing or empty artefact falling back to "no levy" instead of refusing.

    ADDED BECAUSE A MUTATION SURVIVED AND THE SURVIVAL WAS AN EQUIVALENCE, NOT A PASS. Replacing
    `_load_levy`'s empty-series `raise` with `return {}` killed nothing, because that branch is
    unreachable while the real artefact is well-formed -- so no test could have exercised it, and
    reading the survival as "the code is fine" would have been the flattering answer rather than
    the true one. This makes the branch reachable.

    Both malformed shapes, because they arrive by different routes: an artefact that is missing
    entirely, and one that is present but carries no series (a truncated write, a schema change).
    """
    import company.regulatory.capacity_market as mod

    absent = tmp_path / "gone.json"
    monkeypatch.setattr(mod, "_COMMONS", absent)
    with pytest.raises(FileNotFoundError, match="no invented default"):
        mod._load_levy()

    empty = tmp_path / "empty.json"
    empty.write_text('{"artefact": "capacity_market_supplier_levy", "levy_gbp_per_mwh": []}')
    monkeypatch.setattr(mod, "_COMMONS", empty)
    with pytest.raises(ValueError, match="carries no series"):
        mod._load_levy()

    # ...and the real artefact still loads, so this is not a guard that refuses everything.
    monkeypatch.undo()
    assert mod._load_levy()
