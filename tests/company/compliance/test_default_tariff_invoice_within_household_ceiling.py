"""A default-tariff invoice never charges the household above min(Ofgem cap, EPG).

THE DEFECT EACH ASSERT NAMES. The 19 Oct run billed 4,764 capped-period invoices above that
ceiling. Two causes: an incoming occupant struck above the cap itself, and an SVT bill during the
EPG charging the household the Ofgem level -- the Treasury's half. The first control is the
partition: a rule that refuses everything passes every "does it refuse" test, so the pass leg
(a fixed term the household chose, priced above the cap) is asserted beside the fail legs.

MUTATIONS, each applied in place and reverted:
  * `net_of_epg=True` -> `False` in the invariant: the EPG leg passes, `test_the_partition` reds.
  * `DEFAULT_TARIFF_TYPES` gains "fixed": the fixed leg fails, `test_the_partition` reds.
  * the `(1.0 + vat_rate)` factor dropped: the at-the-ceiling SVT bill stays within, but the bill
    priced 4% over it ex-VAT passes too, and `test_vat_is_on_the_household_side` reds.
  * the multi-register branch dropped (every bill graded at the single-rate cap and its own mix):
    the at-cap Economy 7 bill reads as a breach, `test_an_economy_7_bill_is_graded_at_28ad_36` reds.
  * the 58/42 split replaced by the bill's own mix: same red. The leg over the multi-register cap
    keeps the branch able to refuse.
  * the multi-register ceiling taken `net_of_epg=True` (the EPG scaled by the cap's ratio, N19 class
    B): PROS-2021-0282's Apr 2023 bill reads 0.56p over, and
    `test_an_economy_7_bill_under_the_epg_is_graded_against_the_published_multi_register_cap` reds.
"""
from __future__ import annotations

from datetime import date

from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    DEFAULT_TARIFF_INVOICE_WITHIN_HOUSEHOLD_CEILING,
    check_default_tariff_invoice_within_household_ceiling,
    default_tariff_invoice_excess_p_per_kwh,
)
from company.pricing.ofgem_price_cap import get_multi_register_cap_unit_rate_for_date


def _invoice(period_start: str, p_per_kwh_inc_vat: float, *, fuel="electricity", kwh=300.0,
             vat_rate=0.05, **extra) -> dict:
    """An invoice whose all-in unit rate inc its own VAT is `p_per_kwh_inc_vat`."""
    unit_ex_vat = kwh * p_per_kwh_inc_vat / 100.0 / (1 + vat_rate)
    standing = 20.0
    net = unit_ex_vat + standing
    return {"date": period_start[:8] + "28", "period_start": period_start, "commodity": fuel,
            "consumption_kwh": kwh, "commodity_amount_gbp": unit_ex_vat * 0.8,
            "non_commodity_amount_gbp": unit_ex_vat * 0.2, "standing_charge_gbp": standing,
            "vat_gbp": net * vat_rate, "amount_gbp": net * (1 + vat_rate), **extra}


def test_the_partition():
    """Jan 2023: Ofgem 67.47p, EPG 34.0p (commons rows). Both verdicts must be reachable."""
    over_cap_svt = _invoice("2023-01-01", 80.0)
    at_ofgem_level_during_epg = _invoice("2023-01-01", 67.47)
    within_svt = _invoice("2023-01-01", 34.0)
    fixed_above_cap = _invoice("2023-01-01", 80.0)
    verdicts = {
        "over_cap_svt": check_default_tariff_invoice_within_household_ceiling(over_cap_svt, "svt"),
        "epg_not_passed_on": check_default_tariff_invoice_within_household_ceiling(
            at_ofgem_level_during_epg, "svt"),
        "within_svt": check_default_tariff_invoice_within_household_ceiling(within_svt, "svt"),
        "fixed_above_cap": check_default_tariff_invoice_within_household_ceiling(fixed_above_cap, "fixed"),
    }
    assert set(verdicts.values()) == {True, False}, verdicts
    assert verdicts == {"over_cap_svt": False, "epg_not_passed_on": False,
                        "within_svt": True, "fixed_above_cap": True}, verdicts
    assert DEFAULT_TARIFF_INVOICE_WITHIN_HOUSEHOLD_CEILING in ALL_INVARIANTS


def test_vat_is_on_the_household_side():
    """Outside the EPG (Jan 2021, 17.2p inc VAT) a bill 4% over the ceiling once VAT is added fails."""
    assert check_default_tariff_invoice_within_household_ceiling(_invoice("2021-01-01", 17.2), "svt")
    assert not check_default_tariff_invoice_within_household_ceiling(_invoice("2021-01-01", 17.2 * 1.04), "svt")


def test_what_cannot_be_graded_says_so():
    """Before the cap, and a catch-up spanning earlier ceilings, are None -- not a pass to count."""
    assert default_tariff_invoice_excess_p_per_kwh(_invoice("2018-06-01", 99.0), "svt") is None
    assert default_tariff_invoice_excess_p_per_kwh(
        _invoice("2023-01-01", 99.0, catchup_applied=True), "svt") is None
    assert default_tariff_invoice_excess_p_per_kwh(_invoice("2023-01-01", 99.0), "deemed") > 0


def _economy_7_invoice(period_start: str, over_multi_register_cap: float) -> dict:
    """SYN-2016-592's Feb 2019 shape (N19): 72% day, night at 3.352p, no non-commodity. The day rate
    puts the 58/42 all-in rate at `over_multi_register_cap` times the multi-register cap."""
    day_kwh, night_kwh, night_p, vat_rate = 733.2, 278.3, 3.352, 0.05
    ceiling_ex_vat = get_multi_register_cap_unit_rate_for_date(date.fromisoformat(period_start)) / 10.0 / (1 + vat_rate)
    day_p = (over_multi_register_cap * ceiling_ex_vat - 0.42 * night_p) / 0.58
    energy = (day_kwh * day_p + night_kwh * night_p) / 100.0
    net = energy + 20.0
    return {"period_start": period_start, "commodity": "electricity", "consumption_kwh": day_kwh + night_kwh,
            "commodity_amount_gbp": energy, "non_commodity_amount_gbp": 0.0,
            "vat_gbp": net * vat_rate, "amount_gbp": net * (1 + vat_rate),
            "registers": [
                {"label": "Day", "consumption_kwh": day_kwh, "commodity_amount_gbp": day_kwh * day_p / 100.0},
                {"label": "Night", "consumption_kwh": night_kwh, "commodity_amount_gbp": night_kwh * night_p / 100.0}]}


def test_an_economy_7_bill_is_graded_at_28ad_36():
    """SLC 28AD.4 and .36(a): a two-register default bill is graded against the multi-register cap at
    58/42. At the cap it passes, though its own 72%-day mix sits over the single-rate cap; 3% over it
    still fails, so the branch can refuse."""
    at_cap = _economy_7_invoice("2019-02-01", 1.0)
    own_mix_p = 100.0 * at_cap["commodity_amount_gbp"] / at_cap["consumption_kwh"] * 1.05
    single_rate_p = default_tariff_invoice_excess_p_per_kwh(
        {**at_cap, "registers": None}, "svt")
    assert single_rate_p and single_rate_p > 0, (
        f"the fixture must be one the single-rate grade calls a breach ({own_mix_p:.2f}p), or it "
        "cannot tell the two grades apart")
    assert default_tariff_invoice_excess_p_per_kwh(at_cap, "svt") == 0.0
    assert default_tariff_invoice_excess_p_per_kwh(_economy_7_invoice("2019-02-01", 1.03), "svt") > 0


def _pros_2021_0282_april_2023(day_p: float = 37.784, night_p: float = 5.872) -> dict:
    """PROS-2021-0282's Apr 2023 Economy 7 SVT bill as the run output records it (N19 class B): Day
    37.784p and Night 5.872p energy, 8.000p non-commodity on both, ex-VAT, 5% VAT. At 58/42 that is
    32.381p ex-VAT, 34.00p inc VAT: the single-rate EPG, landed on by a flat per-kWh EPG receipt."""
    day_kwh, night_kwh, vat_rate = 312.0, 226.0, 0.05
    kwh = day_kwh + night_kwh
    energy = (day_kwh * day_p + night_kwh * night_p) / 100.0
    net = energy + kwh * 0.08
    return {"period_start": "2023-04-01", "commodity": "electricity", "consumption_kwh": kwh,
            "commodity_amount_gbp": energy, "non_commodity_amount_gbp": kwh * 0.08,
            "vat_gbp": net * vat_rate, "amount_gbp": net * (1 + vat_rate),
            "registers": [
                {"label": "Day", "consumption_kwh": day_kwh, "commodity_amount_gbp": day_kwh * day_p / 100.0},
                {"label": "Night", "consumption_kwh": night_kwh, "commodity_amount_gbp": night_kwh * night_p / 100.0}]}


def test_an_economy_7_bill_under_the_epg_is_graded_against_the_published_multi_register_cap():
    """N19 class B. Under the EPG no multi-register household level was published: suppliers set the
    E7 discounts themselves (GOV.UK, R4 in a_storage_heated_homes_default_tariff_is_two_rate.md). The
    grade scaled the single-rate EPG by the cap's multi/single ratio (33.44p inc VAT) and called
    PROS-2021-0282's 34.00p bill a breach, so its page printed a false cap-breach note. Graded against
    the published multi-register cap (about 47p) it is within. A bill over that cap still fails, so
    the branch can refuse; the single-rate EPG leg is held by `test_the_partition`."""
    assert default_tariff_invoice_excess_p_per_kwh(_pros_2021_0282_april_2023(), "svt") == 0.0
    cap_p = get_multi_register_cap_unit_rate_for_date(date(2023, 4, 1), net_of_epg=False) / 10.0
    k = 1.03 * (cap_p / 1.05 - 8.0) / 24.381  # energy scaled so the all-in rate sits 3% over the cap
    over = _pros_2021_0282_april_2023(day_p=37.784 * k, night_p=5.872 * k)
    assert default_tariff_invoice_excess_p_per_kwh(over, "svt") > 0
