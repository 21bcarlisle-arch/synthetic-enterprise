"""The price match reads the published default on the basis of the re-fix and floor it is compared with.

The defect each test names: the run handing the save and the renewal cut the INC-VAT default
(`simulation.svt_rates`) against an ex-VAT re-fix and floor, so the market's best deal reads 5% dear
and both desks under-offer -- on 2024-Q3, where the published gap (3.7%) is smaller than VAT, a re-fix
sitting at the cap got no offer at all.
"""
from __future__ import annotations

from datetime import date

import pytest

from company.interfaces.growth_desk import retention_cut_share_at_price_match
from company.pricing.renewal_rate_chain import cap_ceiling_ex_vat
from simulation.run_phase2b import _price_match_inputs

_TERM = {"locked_policy_cost_gbp_per_mwh": 0.0, "locked_network_cost_gbp_per_mwh": 0.0}
_DAYS = ("2019-07-15", "2021-01-15", "2024-01-15", "2024-07-15", "2025-04-15", "2025-07-15")


@pytest.mark.parametrize("day", _DAYS)
@pytest.mark.parametrize("fuel", ["electricity", "gas"])
def test_a_refix_at_the_default_is_cut_by_exactly_the_published_gap(fuel, day):
    """Property, not a value: a re-fix sitting AT the household's ex-VAT default, with a floor that
    does not bind, meets the best published deal by a cut of exactly the published gap. Off-basis
    by VAT, the cut is the gap less ~5 points (and None where the gap is under 5%)."""
    refix = cap_ceiling_ex_vat(fuel, date.fromisoformat(day), multi_register=False)
    inputs = _price_match_inputs(_TERM, fuel, day, company_fwd=refix * 0.5)
    assert inputs["published_best_deal_gap_share"] > 0.0          # the branch can be taken
    cut = retention_cut_share_at_price_match(refix, **inputs)
    assert cut == pytest.approx(inputs["published_best_deal_gap_share"])


def test_the_default_through_the_epg_is_what_the_household_was_charged():
    """The match's default through the EPG is the EPG-net rate, not the gross cap: one reading with
    the churn belief, which compares the offer against the same figure."""
    day = "2023-01-15"
    assert _price_match_inputs(_TERM, "electricity", day, 100.0)["published_default_rate"] == (
        pytest.approx(cap_ceiling_ex_vat("electricity", date(2023, 1, 15), multi_register=False)))


def test_a_fuel_with_no_cap_has_no_default():
    assert _price_match_inputs(_TERM, "heat", "2025-04-15", 100.0)["published_default_rate"] is None
