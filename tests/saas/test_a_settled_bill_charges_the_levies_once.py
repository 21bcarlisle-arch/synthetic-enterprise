"""A settled bill charges the non-commodity levies once: its pre-VAT total is the revenue booked.

Every settlement writer already carries policy and network cost inside `revenue_gbp` (explicitly on
a pass-through tariff, inside the all-in unit rate on a fixed or capped one), and its net margin
deducts them from that revenue. `generate_bill` used to add the blended levy line on top, so every
household was billed the levies twice -- the defect that made a direct-debit household's first
review rise ~33% in calm years. Found 2026-10-10 from the DD book's year-one reviews.
"""
import pytest

from company.billing.dual_fuel_bill import vat_rate_for_supply
from saas.bill_generator import generate_bill


def _settled(commodity: str, sc_field: str | None) -> list[dict]:
    rows = []
    for day in range(1, 31):
        row = {"customer_id": "C1", "settlement_date": f"2024-06-{day:02d}",
               "consumption_kwh": 8.0, "revenue_gbp": 8.0 / 1000 * 221.7 + 0.57}
        if sc_field:
            row[sc_field] = 0.57
        rows.append(row)
    return rows


@pytest.mark.parametrize("commodity, sc_field",
                         [("electricity", "standing_charge_gbp"), ("gas", "gas_standing_charge_gbp")])
def test_a_settled_bill_is_the_booked_revenue_plus_vat(commodity, sc_field):
    rows = _settled(commodity, sc_field)
    bill = generate_bill("C1", rows, "fixed_1yr", segment="resi", commodity=commodity)
    revenue = sum(r["revenue_gbp"] for r in rows)
    vat = vat_rate_for_supply("resi", commodity, bill["total_consumption_kwh"], 30)

    assert bill["non_commodity_amount_gbp"] > 0, "the levy line is still shown on the bill"
    assert bill["total_amount_gbp"] == pytest.approx(revenue * (1 + vat))
    # The unit rate printed is the all-in rate the account was sold at.
    assert bill["average_unit_rate_gbp_per_mwh"] == pytest.approx(221.7)


def test_both_branches_of_the_carve_out_are_reachable():
    """A legacy fixture with no standing-charge field folds nothing into revenue, so its levy line is
    still added. One control over the partition, so a branch cannot quietly become unreachable."""
    settled = generate_bill("C1", _settled("electricity", "standing_charge_gbp"), "fixed_1yr")
    legacy = generate_bill("C1", _settled("electricity", None), "fixed_1yr")
    settled_pre_vat = settled["commodity_amount_gbp"] + settled["non_commodity_amount_gbp"]
    legacy_pre_vat = legacy["commodity_amount_gbp"] + legacy["non_commodity_amount_gbp"]
    revenue = sum(r["revenue_gbp"] for r in _settled("electricity", None))

    assert settled_pre_vat + settled["standing_charge_gbp"] == pytest.approx(revenue)
    assert legacy_pre_vat == pytest.approx(revenue + legacy["non_commodity_amount_gbp"])
