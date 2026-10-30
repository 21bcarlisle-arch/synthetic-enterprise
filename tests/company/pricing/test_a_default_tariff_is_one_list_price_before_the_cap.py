"""A default tariff is one list price: the renewal chain's per-account writers do not move an SVT segment.

Before the cap nothing clamps an SVT segment, so writers 1 (the portfolio premium, read at the
account's own term start) and 2 (the margin surcharge, read off the account's own last term) priced
each account apart: 2,489 of 4,366 pre-cap SVT terms on the 9553d403b7 book, 16 electricity rates on
2017-06-01 against one list price (`docs/staging/SEAT_FINDING_LEG_ONE_GRADES_FOUR_OF_THE_FIVE_
UNCHECKABLE_ROWS_AND_FINDS_SVT_PRICED_PER_ACCOUNT_BEFORE_THE_CAP_2026-10-30.md`). Knowledge:
`docs/market_research/default_tariff_cap_and_epg_on_the_bill.md`, choice 7.

Each test names the defect it catches.
"""

from __future__ import annotations

import pytest

from company.pricing import renewal_rate_chain as chain

PRE_CAP = "2017-06-01"
STRUCK = 133.33
# A book running under its target and an account its supplier lost money on: both writers fire.
LOSING_BOOK = [-0.05, -0.04, -0.06, -0.03]


def _contracted(*, tariff_type: str, prior_margin: float | None, commodity: str = "electricity",
                ) -> float:
    return chain.decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity=commodity, term_start=PRE_CAP,
        tariff_type=tariff_type, term_index=3, struck_unit_rate_gbp_per_mwh=STRUCK,
        portfolio_margin_rates=LOSING_BOOK, prior_term_margin_gbp=prior_margin,
        prior_term_revenue_gbp=100.0, is_domestic=True, segment="resi", settled_records=[],
        customer={"metering": "NHH", "smart_meter": False},
    ).unit_rate_gbp_per_mwh


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_a_pre_cap_svt_segment_contracts_at_its_list_price_whatever_the_accounts_history(commodity):
    """Catches writers 1-2 reaching `svt`: two accounts on the same default tariff on the same day,
    one the supplier lost money on and one it did not, contract at different rates. The fixed leg
    with the same inputs must move, so a chain that moves nothing cannot pass."""
    lost = _contracted(tariff_type="svt", prior_margin=-20.0, commodity=commodity)
    kept = _contracted(tariff_type="svt", prior_margin=None, commodity=commodity)
    fixed = _contracted(tariff_type="fixed", prior_margin=-20.0, commodity=commodity)
    assert fixed > STRUCK * 1.01, "writers 1-2 no longer fire on a fixed renewal: this control proves nothing"
    assert lost == pytest.approx(STRUCK, rel=1e-12) and kept == pytest.approx(STRUCK, rel=1e-12), (
        f"{commodity} SVT on {PRE_CAP}: {lost:.2f} for the account it lost money on, {kept:.2f} for "
        f"the other, against one list price {STRUCK:.2f}")
