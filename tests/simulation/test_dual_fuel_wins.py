"""R15 proofs for the gas half of a won home — the dual-fuel leg.

THE DIRECTOR, 2026-08-26: *"The funnel only ever wins electricity, never dual fuel. Real
suppliers win both together far more often than not, and dual fuel changes cost-to-serve,
churn and lifetime value — so a single-fuel-only book quietly distorts every per-customer
number we've been arguing about."*

`net_new_acquisition.ELECTRICITY_ONLY` had named the blocker precisely and declined to guess
past it: a gas account's record carries `aq_kwh`, the drawn dict does not, `TOTAL_GAS_AQ`
raises on the first won gas prospect, and *"deriving an `aq_kwh` for a won gas account means
inventing an annual quantity for a home whose gas consumption nothing has yet modelled"*.

That reasoning was right and its premise expired. Two things exist now that did not:

  * `population_draw.TDCV_BANDS_KWH["gas"]` — Ofgem's Typical Domestic Consumption Values
    per band, already duplicated SIM-side under the regulation-commons convention. The
    prospect already draws a `consumption_band`, so the quantity comes from the published
    table by the same uniform draw the electricity EAC uses.
  * `DrawnPremise.commodity` — *"the fuel whose register the supplier reads for heat"*,
    derived from the dwelling's own drawn `heating_system`. So WHETHER a home takes gas is a
    property of the housing stock, not a share anybody tuned.

WHAT THESE TESTS PIN, in the order that matters:

  1. both directions — a gas-heated home gets a leg, an electric one does not;
  2. the quantity is the PUBLISHED band's, not a default;
  3. the two legs are ONE billing account, which is what makes this reach cost-to-serve,
     churn and lifetime value rather than merely adding rows;
  4. every blank is NAMED and fails closed — an invented AQ arriving silently from a
     fallback would be worse than the one that never arrived at all;
  5. and C-S2: adding this draw leaves the electricity dict untouched.
"""

import pytest

from saas.customer_reaction import _billing_account_id
from simulation import live_population as lp
from simulation.population_draw import TDCV_BANDS_KWH


class _Premise:
    def __init__(self, commodity):
        self.commodity = commodity


class _Prospect:
    """The two things `_gas_leg_for` reads off a prospect, and nothing else."""

    def __init__(self, commodity="gas"):
        self.premise = _Premise(commodity) if commodity else None


def _elec(customer_id="PROS-2024-0001", band="MEDIUM", **extra):
    return {"customer_id": customer_id, "commodity": "electricity",
            "consumption_band": band, "eac_kwh": 2500.0, "segment": "resi",
            "acquisition_date": "2024-03-01", "acquisition_type": "net_new_won",
            "tariff_type": "fixed", "smart_meter": True,
            "location": {"lat": None, "lon": None, "region": "London"}, **extra}


# ---------------------------------------------------------------------------
# 1. both directions
# ---------------------------------------------------------------------------

def test_a_gas_heated_home_gets_a_gas_leg():
    leg = lp._gas_leg_for(_Prospect("gas"), _elec())
    assert leg is not None
    assert leg["commodity"] == "gas"
    assert leg["customer_id"] == "PROS-2024-0001g"


def test_an_electrically_heated_home_gets_NO_gas_leg():
    """The partner, and the honest reason: a heat-pump home has no gas meter. A dual-fuel
    rate that came out at 100% would be a bug wearing a feature's clothes."""
    assert lp._gas_leg_for(_Prospect("electricity"), _elec()) is None


def test_the_dual_fuel_rate_follows_the_REAL_STOCK_rather_than_a_constant():
    """Measured on the actual premise draw, not on a fixture.

    An earlier draft of this test built its own 90%-gas prospect list and then asserted the
    share was 80-95%, which measures the fixture and nothing else. The claim worth making is
    that the dual-fuel rate is a property of the HOUSING STOCK this supplier sells into, so
    the stock is what gets measured: `DrawnPremise.commodity` over the real drawn pool.

    Bounds rather than equality, and wide ones. The stock is drawn, and pinning a count
    would make this a change-detector for the population draw. What it must catch is the
    rate collapsing to nothing (the pre-2026-08-26 state) or pinning at 100% (a rule that
    gives every home a gas meter, heat pumps included).

    NOTE, and it is a fidelity observation rather than a failure: the drawn stock is ~91%
    gas-heated against a GB mains-gas share nearer 85%. That belongs to
    `premise_population`'s own calibration, and under R13 it is recorded here rather than
    tuned by a seat that has just watched it move the company's book.
    """
    from simulation.net_new_acquisition import year_premise_stock

    commodities = [p.commodity
                   for year in (2021, 2022, 2023, 2024)
                   for p in year_premise_stock(year, base_seed=20260101, n=200)]
    share = sum(1 for c in commodities if c == "gas") / len(commodities)
    assert 0.70 <= share <= 0.97, (
        f"gas-heated share of the drawn stock is {share:.1%}; at 0 the book is "
        "single-fuel again, at 1.0 every home including heat pumps has a gas meter")


# ---------------------------------------------------------------------------
# 2. the quantity is the published band's
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("band", ["LOW", "MEDIUM", "HIGH"])
def test_the_gas_quantity_comes_from_the_published_band_for_that_home(band):
    low, high = TDCV_BANDS_KWH["gas"][band]
    leg = lp._gas_leg_for(_Prospect("gas"), _elec(band=band))
    assert low <= leg["aq_kwh"] <= high, (
        f"{band} gas AQ {leg['aq_kwh']} outside the published TDCV band {low}-{high}")


def test_the_bands_are_ordered_so_a_bigger_home_really_does_use_more_gas():
    """If the bands did not separate, `consumption_band` would be decorative and the AQ
    would be a random number in a wide range wearing a band's name."""
    legs = {b: lp._gas_leg_for(_Prospect("gas"), _elec(band=b))["aq_kwh"]
            for b in ("LOW", "MEDIUM", "HIGH")}
    assert legs["LOW"] < legs["MEDIUM"] < legs["HIGH"]


def test_the_gas_quantity_is_deterministic_for_a_given_home():
    """Same home, same answer — a run that re-drew this on every call would move the total
    gas position between two reads of the same book."""
    first = lp._gas_leg_for(_Prospect("gas"), _elec())["aq_kwh"]
    second = lp._gas_leg_for(_Prospect("gas"), _elec())["aq_kwh"]
    assert first == second


def test_two_different_homes_get_different_quantities():
    """The partner. A deterministic draw that returned the SAME number for every home would
    pass the test above and make the band draw pointless."""
    a = lp._gas_leg_for(_Prospect("gas"), _elec("PROS-2024-0001"))["aq_kwh"]
    b = lp._gas_leg_for(_Prospect("gas"), _elec("PROS-2024-0002"))["aq_kwh"]
    assert a != b


def test_the_leg_carries_the_metering_constants_the_seed_book_uses():
    """`cv_factor` and `cf` are constant across every domestic gas customer in
    `saas/customers.py`. A drawn leg using anything else would be a different kind of meter
    for no stated reason."""
    leg = lp._gas_leg_for(_Prospect("gas"), _elec())
    assert leg["cv_factor"] == lp.GAS_CV_FACTOR == 39.5
    assert leg["cf"] == lp.GAS_CORRECTION_FACTOR == 1.02264


# ---------------------------------------------------------------------------
# 3. one household, one billing account
# ---------------------------------------------------------------------------

def test_the_two_legs_are_one_billing_account():
    """THE PROPERTY THE WHOLE CHANGE RESTS ON. A dual-fuel household bills once, so
    cost-to-serve, churn and lifetime value see ONE customer with two supply points. If the
    legs billed separately this would just be more rows, and every per-customer figure would
    be distorted in a new direction instead of an old one."""
    elec = _elec()
    leg = lp._gas_leg_for(_Prospect("gas"), elec)
    assert _billing_account_id(leg["customer_id"]) == elec["customer_id"]


def test_the_gas_leg_inherits_the_household_facts_and_not_the_electricity_ones():
    """Same home, same region, same acquisition — but the electricity EAC and the
    electricity tariff must NOT ride along, or the gas account reports a quantity and a
    product it does not have."""
    elec = _elec()
    leg = lp._gas_leg_for(_Prospect("gas"), elec)
    assert leg["segment"] == elec["segment"]
    assert leg["location"] == elec["location"]
    assert leg["acquisition_date"] == elec["acquisition_date"]
    assert "eac_kwh" not in leg
    assert "tariff_type" not in leg


# ---------------------------------------------------------------------------
# 4. every blank is named and fails closed
# ---------------------------------------------------------------------------

def test_a_prospect_with_no_premise_gets_no_leg_rather_than_a_default_quantity():
    """FAIL-CLOSED. The pre-PB2 draw path produces prospects with no dwelling, and nothing
    has said what kind of home they are. An invented AQ feeding the run's total gas position
    is the exact outcome `ELECTRICITY_ONLY` refused, and it would be worse arriving silently
    from a fallback than it was arriving not at all."""
    assert lp._gas_leg_for(_Prospect(None), _elec()) is None


@pytest.mark.parametrize("band", ["", "UNKNOWN", None, "medium"])
def test_a_band_the_published_table_has_no_row_for_gets_no_leg(band):
    """FAIL-CLOSED again, and case-sensitively: the table is keyed LOW/MEDIUM/HIGH, so
    `"medium"` is not a row and must not quietly become one."""
    assert lp._gas_leg_for(_Prospect("gas"), _elec(band=band)) is None


# ---------------------------------------------------------------------------
# 5. C-S2 — the new draw perturbs nothing
# ---------------------------------------------------------------------------

def test_building_the_gas_leg_does_not_mutate_the_electricity_dict():
    """The electricity account must be byte-identical whether or not this home took gas."""
    elec = _elec()
    before = dict(elec)
    lp._gas_leg_for(_Prospect("gas"), elec)
    assert elec == before


def test_the_won_list_puts_each_gas_leg_directly_after_its_own_electricity_account():
    """Ordering is not cosmetic: `live_population` hands this list to
    `register_drawn_points`, and a reader of the book should be able to see a household as a
    household."""
    class _P:
        def __init__(self, cid, commodity):
            self.premise = _Premise(commodity)
            self._cid = cid

        def to_customer_dict(self):
            return _elec(self._cid)

    import datetime as dt
    outcome = {"winners": [(_P("PROS-2024-0001", "gas"), dt.date(2024, 3, 1)),
                           (_P("PROS-2024-0002", "electricity"), dt.date(2024, 4, 1)),
                           (_P("PROS-2024-0003", "gas"), dt.date(2024, 5, 1))]}
    ids = [c["customer_id"] for c in lp._won_customer_dicts(outcome)]
    assert ids == ["PROS-2024-0001", "PROS-2024-0001g",
                   "PROS-2024-0002",
                   "PROS-2024-0003", "PROS-2024-0003g"]
