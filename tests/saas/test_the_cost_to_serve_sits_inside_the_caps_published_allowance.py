"""A dual-fuel resi account is charged, per cap period, what the cap allows to serve it (N21 gap 2).

The book charged a flat £55 per fuel account, so £110 per dual-fuel home. Ofgem's own operating,
payment-method and smart-metering allowance for that home was £171 in 2016 and £239 in 2024.
Every per-customer CLV inherited a margin carrying about a third of the real cost of serving a home.

The band is written here from Ofgem's published cells: *Default tariff cap level* v1.28,
`ElecSingle_Other_Benchmark` / `Gas_Other_Benchmark`, direct debit, identical in every region. It
is NOT read from `saas.cost_to_serve`, so the module cannot agree with itself.
- **Lower edge:** OC + PAAC + SMNCC for both fuels, less at most £2.00 for the DD bad debt Ofgem
  puts inside OC (Appendix 6 §2.6: £0.84 + £0.46 at 2017, indexed with OC, so £1.72 by 2025).
  From July 2025 it is CO + IC + SMNCC, with nothing netted (1p allowed for rounding).
- **Upper edge:** the lower edge plus the published debt allowances the book bears on its own
  line: PAP, the debt floats, and DRC.

Knowledge: `docs/market_research/the_caps_operating_debt_and_industry_allowance_per_cap_period.md`.

Mutations:
- restore the flat £55 for resi (HEAD before this change) → all six are red;
- drop the record's date from the charge → all six are red;
- charge the nil-consumption column for April 2019 → that period is red.
"""
from __future__ import annotations

import pytest

from saas.cost_to_serve import build_cost_to_serve

# (date inside the cap period, lower edge, upper edge), £ per dual-fuel account per year.
_PUBLISHED_BAND = (
    # Apr 2016 back-cast: E OC 76.89 + PAAC 3.36; G OC 87.63 + PAAC 3.13. PAP 2.15 + 1.67.
    ("2016-06-15", 171.01 - 2.0, 171.01 + 2.15 + 1.67),
    # Apr 2019: E 82.02 + 3.59 + 13.91; G 93.48 + 3.34 + 14.64. PAP 2.94 + 2.22.
    ("2019-06-15", 210.98 - 2.0, 210.98 + 2.94 + 2.22),
    # Oct 2022: E 92.28 + 4.04 + 16.07; G 105.17 + 3.76 + 3.46. PAP 7.92 + 7.09 (this AA is wholesale).
    ("2022-11-15", 224.78 - 2.0, 224.78 + 7.92 + 7.09),
    # Apr 2024: E 99.94 + 4.37 + 16.06; G 113.90 + 4.07 + 1.02. PAP 4.25 + 3.10; debt float 15.90 + 14.67.
    ("2024-05-15", 239.36 - 2.0, 239.36 + 4.25 + 3.10 + 15.90 + 14.67),
    # Jul 2025: E CO 93.41 + IC 18.08 + SMNCC 1.67; G CO 100.22 + IC 14.58 + SMNCC -5.44. DRC 28.70 + 24.91.
    ("2025-08-15", 222.52 - 0.01, 222.52 + 28.70 + 24.91),
)

_ROSTER = [{"customer_id": "H1", "segment": "resi"}, {"customer_id": "H1g", "segment": "resi"},
           {"customer_id": "B1", "segment": "SME"}]


def _a_year_of_records(cid: str, commodity: str, on: str) -> dict:
    """One record standing for a whole year of this fuel's settlement periods, on one date."""
    return {"customer_id": cid, "commodity": commodity, "settlement_date": on, "revenue_gbp": 0.0,
            "margin_gbp": 0.0, "net_margin_gbp": 0.0,
            "settlement_periods_folded": 365 if commodity == "gas" else 17_520}


@pytest.mark.parametrize("on, lower, upper", _PUBLISHED_BAND)
def test_a_dual_fuel_home_is_charged_inside_the_caps_published_allowance(on, lower, upper):
    records = [_a_year_of_records("H1", "electricity", on), _a_year_of_records("H1g", "gas", on)]
    by_customer = build_cost_to_serve(records, _ROSTER)["by_customer"]
    dual = by_customer["H1"]["cost_to_serve_gbp"] + by_customer["H1g"]["cost_to_serve_gbp"]
    assert lower <= dual <= upper, f"{on}: £{dual:.2f} per dual-fuel home, published band £{lower:.2f}-£{upper:.2f}"


def test_the_charge_moves_with_the_cap_period_and_sme_does_not():
    """The branch can be taken both ways: resi follows the date, SME (no domestic cap) stays flat."""
    def charged(cid, on):
        return build_cost_to_serve([_a_year_of_records(cid, "electricity", on)], _ROSTER)[
            "by_customer"][cid]["cost_to_serve_gbp"]

    assert charged("H1", "2016-06-15") < charged("H1", "2024-05-15")
    assert charged("B1", "2016-06-15") == pytest.approx(charged("B1", "2024-05-15"))
