"""Phase 47b — the acquisition no-offer rule.

The supplier does not go to market for a domestic prospect when its price is above the published
default on the prospect's day: both fuels, ex-VAT, net of the EPG (2026-10-02). Every bound below
is read from `cap_ceiling_ex_vat`, never typed, so a cap-table correction moves the rule and its
controls together.
"""

from datetime import date

import pytest

from company.pricing.renewal_rate_chain import cap_ceiling_ex_vat
from saas.growth_mandate import should_attempt_acquisition


def _default(commodity, day):
    return cap_ceiling_ex_vat(
        commodity, date.fromisoformat(day), multi_register=False, net_of_epg=True)


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
@pytest.mark.parametrize("day", ["2019-06-01", "2021-10-17", "2022-06-01", "2024-08-25"])
def test_both_legs_of_the_rule_are_reachable_on_both_fuels(commodity, day):
    """The partition: just above the default refuses, at it proceeds, on either fuel. A rule that
    refused everything, or nothing, or only electricity (the rule this replaced), reds here."""
    ref = _default(commodity, day)
    above = should_attempt_acquisition("resi", commodity, ref * 1.01, day)
    at = should_attempt_acquisition("resi", commodity, ref, day)
    assert above[0] is False and at == (True, None)


def test_the_default_is_ex_vat():
    """A price under the published inc-VAT figure but over its ex-VAT reading is refused: both
    sides of the comparison are ex-VAT."""
    day = "2021-10-17"
    ref = _default("electricity", day)
    ok, _ = should_attempt_acquisition("resi", "electricity", ref * 1.03, day)
    assert ok is False


def test_the_default_is_net_of_the_epg():
    """Under the EPG the prospect paid the guarantee, not the cap, so the guarantee is the default."""
    day = "2022-10-01"
    epg = _default("electricity", day)
    cap = cap_ceiling_ex_vat(
        "electricity", date.fromisoformat(day), multi_register=False, net_of_epg=False)
    assert epg < cap
    ok, _ = should_attempt_acquisition("resi", "electricity", (epg + cap) / 2, day)
    assert ok is False


def test_the_quote_decides_when_the_supplier_has_one():
    """The forward is only a floor on the strike. Supplied, the quote replaces it in both
    directions."""
    day = "2021-06-21"
    ref = _default("gas", day)
    low_fwd_high_quote = should_attempt_acquisition(
        "resi", "gas", ref * 0.5, day, quoted_unit_rate_per_mwh=ref * 1.06)
    high_fwd_low_quote = should_attempt_acquisition(
        "resi", "gas", ref * 2.0, day, quoted_unit_rate_per_mwh=ref * 0.9)
    assert low_fwd_high_quote[0] is False and "quote=" in low_fwd_high_quote[1]
    assert high_fwd_low_quote == (True, None)


def test_the_reason_names_the_fuel_both_figures_and_the_basis():
    day = "2022-06-01"
    ok, reason = should_attempt_acquisition("resi", "gas", 400.0, day)
    assert ok is False
    assert reason == (f"cap_constrained (gas default={_default('gas', day):.1f} < fwd=400.0 "
                      f"GBP/MWh ex-VAT)")


@pytest.mark.parametrize("segment", ["SME", "I&C"])
def test_non_domestic_always_proceeds(segment):
    assert should_attempt_acquisition(segment, "electricity", 9999.0, "2022-06-01") == (True, None)


@pytest.mark.parametrize("day", ["2016-06-01", "2018-04-01"])
def test_no_published_default_means_nothing_to_price_against(day):
    assert should_attempt_acquisition("resi", "gas", 9999.0, day) == (True, None)
