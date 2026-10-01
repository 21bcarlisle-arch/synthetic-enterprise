"""An SVT segment's contracted rate never sits above the published cap, and is not held at the EPG.

SLC 28AD binds the default tariff first: "Evergreen (SVT), Deemed, and default fixed-term contracts"
(`docs/domain_artefact_library/regulatory/slc_28ad_multi_register_cap_test.md`). Writer 4 bound
`fixed` only, so writers 1-3 moved 630 of 2,333 capped-year SVT segments above the cap, up to
x1.38, and settlement billed that rate
(`docs/staging/SEAT_FINDING_AN_SVT_SEGMENT_WAS_BILLED_ABOVE_THE_CAP_BY_THE_RENEWAL_CHAIN_2026-10-01.md`).

The ceiling is recomputed from the WORLD's reading of the published series (`simulation/svt_rates`),
not from the chain's helper: a helper that drifted would agree with itself.

Each test names the defect it catches.
"""

from __future__ import annotations

from datetime import date

import pytest

from company.pricing import renewal_rate_chain as chain
from simulation import svt_rates

VAT = 1.05
FLAT = {"metering": "NHH", "smart_meter": False}
TOU = {"metering": "NHH", "smart_meter": True}
NO_EPG, IN_EPG = "2021-10-01", "2022-12-17"


def _published_ex_vat(commodity: str, on: str) -> float:
    read = (svt_rates.get_svt_elec_rate_gbp_per_mwh if commodity == "electricity"
            else svt_rates.get_svt_gas_rate_gbp_per_mwh)
    return read(on) / VAT


def _contracted(*, commodity: str, on: str, tariff_type: str, struck: float,
                customer: dict = FLAT) -> float:
    return chain.decide_renewal_rate(
        customer_id="C1", billing_account="C1", commodity=commodity, term_start=on,
        tariff_type=tariff_type, term_index=0, struck_unit_rate_gbp_per_mwh=struck,
        portfolio_margin_rates=[], prior_term_margin_gbp=None, prior_term_revenue_gbp=0.0,
        is_domestic=True, segment="resi", settled_records=[], customer=customer,
    ).unit_rate_gbp_per_mwh


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
@pytest.mark.parametrize("on", [NO_EPG, IN_EPG])
def test_an_svt_rate_moved_above_the_cap_is_clamped_to_it(commodity, on):
    """Catches `svt` missing from `CAPPED_TARIFF_TYPES`: a strike at x1.38 the cap (the largest
    move the chain made in the 28AD run) passes through unclamped."""
    cap = _published_ex_vat(commodity, on)
    got = _contracted(commodity=commodity, on=on, tariff_type="svt", struck=cap * 1.38)
    assert got == pytest.approx(cap, rel=1e-9), (
        f"{commodity} SVT {on}: contracted {got:.2f} against a published cap of {cap:.2f} ex-VAT")


@pytest.mark.parametrize("commodity", ["electricity", "gas"])
def test_in_the_epg_window_svt_is_held_at_the_cap_and_fixed_at_the_epg(commodity):
    """Catches an SVT ceiling read net of the EPG. HM Treasury paid the supplier the gap between
    the EPG and the cap on a default tariff, so the world strikes SVT at the cap. A ceiling at the
    EPG would clamp every SVT segment in the window and take the Treasury's half out of revenue.
    Both legs of the partition are asserted, so a guard that clamps everything, or nothing, fails."""
    cap = _published_ex_vat(commodity, IN_EPG)
    svt = _contracted(commodity=commodity, on=IN_EPG, tariff_type="svt", struck=cap)
    fixed = _contracted(commodity=commodity, on=IN_EPG, tariff_type="fixed", struck=cap)
    assert svt == pytest.approx(cap, rel=1e-9), "an SVT segment struck at the cap was clamped"
    assert fixed < cap * 0.9, "the EPG no longer binds a fixed term, so this control proves nothing"


def test_an_svt_segment_sold_as_tou_is_graded_against_the_multi_register_cap():
    """Catches an SVT ToU segment graded single-rate: 28AD.4 grades any ToU tariff at the
    multi-register benchmark, and the chain sells a smart-metered SVT household the ToU pair."""
    cap = _published_ex_vat("electricity", NO_EPG)
    flat = _contracted(commodity="electricity", on=NO_EPG, tariff_type="svt", struck=cap)
    tou = _contracted(commodity="electricity", on=NO_EPG, tariff_type="svt", struck=cap,
                      customer=TOU)
    assert flat == pytest.approx(cap, rel=1e-9)
    assert tou == pytest.approx(chain.cap_ceiling_ex_vat(
        "electricity", date.fromisoformat(NO_EPG), multi_register=True, net_of_epg=False))
    assert tou < flat
