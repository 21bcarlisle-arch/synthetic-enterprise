"""A storage-heated home's winter estimate, at what its own meter is registered to use, is not held as
a business.

Defect this guards: SYN-2016-175, a listed, storage-heated dwelling registered at an EAC of 18,721.5
kWh, had its four winter estimates (Nov 2016 to Feb 2017, 1,964 to 2,152 kWh a month) held on
`vat_by_segment` and `slc_6_7_billing_accuracy` against a flat 2,100 kWh/month population screen
(fd91027799 book, exception queue). With a read already taken in April, no release could reach them.
They are 16 bills on three such homes, and the cause of INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL's
whole exception.

The rule: BSCP504's data collector fails an advance over twice the meter's expected advance (EAC times
the profile). The meter's figure lifts the screen to that and never lowers it, and lifts the VAT half
only on a listed dwelling (HMRC 701/19 s.3.2.1). Knowledge:
docs/market_research/how_far_a_settled_eac_sits_from_next_years_use.md section 5.
"""

from __future__ import annotations

import datetime as dt

from company.billing.pre_bill_validation import validate_bill
from company.billing.unread_month_estimate import split_on_register_shape

EAC = 18721.5  # SYN-2016-175's registry figure on the fd91027799 book

HELD_ON_THE_BOOK = [  # (start, end, kWh) of SYN-2016-175's four held estimates
    ("2016-11-01", "2016-11-30", 2081.6),
    ("2016-12-01", "2016-12-31", 2152.0),
    ("2017-01-01", "2017-01-31", 2151.8),
    ("2017-02-01", "2017-02-28", 1963.9),
]


def _bill(start, end, kwh, *, listed=True, registry=EAC, fuel="electricity", cid="SYN-2016-175"):
    days = (dt.date.fromisoformat(end) - dt.date.fromisoformat(start)).days + 1
    money = round(kwh * 0.15, 2)
    standing = round(days * 0.30, 2)
    vat = round((money + standing) * 0.05, 2)
    bill = {
        "customer_id": cid, "segment": "resi", "commodity": fuel,
        "period_start": start, "period_end": end, "total_consumption_kwh": kwh,
        "commodity_amount_gbp": money, "non_commodity_amount_gbp": 0.0,
        "standing_charge_gbp": standing, "vat_gbp": vat,
        "total_amount_gbp": round(money + standing + vat, 2),
        "billing_basis": "estimated", "premise_council_tax_listed": listed,
    }
    if registry is not None:
        bill["registry_annual_kwh"] = registry
    return bill


def _expected(start, end):
    return sum(split_on_register_shape(
        EAC, dt.date.fromisoformat(start), dt.date.fromisoformat(end)).values())


def test_syn_2016_175s_four_winter_estimates_are_not_held():
    held = {end: validate_bill(_bill(start, end, kwh)).reasons for start, end, kwh in HELD_ON_THE_BOOK}
    assert not any(held.values()), held


def test_the_partition_lifts_and_still_holds():
    """Both sides of the ceiling must be reachable, or a gate that passes everything would pass the
    test above. Pinned to the property, twice the expected advance, not to today's bills."""
    dec = ("2016-12-01", "2016-12-31")
    twice = 2 * _expected(*dec)
    assert not validate_bill(_bill(*dec, 0.95 * twice)).held          # under 2x: the meter's own scale
    over = validate_bill(_bill(*dec, 1.05 * twice))
    assert over.held and over.consumption_scale_only                    # over 2x: wrong in scale
    # The same volume with no registry figure behind it: the screen alone, and it holds.
    assert validate_bill(_bill(*dec, 2152.0, registry=None)).held
    # Off the council tax list the volume half passes, but the VAT half still asks the screen,
    # so a business premise on a domestic label is still caught (the C6 class).
    unlisted = validate_bill(_bill(*dec, 2152.0, listed=None))
    assert unlisted.held and all(r.startswith("vat_by_segment") for r in unlisted.reasons)


def test_the_meters_figure_never_lowers_the_screen():
    """A home registered light whose use has grown since (SYN-2016-050 doubled) is not held below the
    screen: the company holds the EAC it was handed, not the data collector's current one."""
    light = _bill("2016-12-01", "2016-12-31", 1500.0, registry=1000.0, cid="SYN-2016-050")
    assert not validate_bill(light).held


def test_gas_keeps_the_screen():
    """No gas tolerance is published to us (UNC Validation Rules, a GAP): a large AQ does not lift it."""
    jan = validate_bill(_bill("2017-01-01", "2017-01-31", 8500.0, registry=50000.0, fuel="gas"))
    assert jan.held
