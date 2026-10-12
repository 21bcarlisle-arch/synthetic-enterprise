"""A default-tariff segment hands the company its OWN forward, not the world's.

`simulation/svt_product.build_svt_schedule` wrote `company_forward_price_gbp_per_mwh = sim_fwd`
on every segment until 2026-10-12, and the run loop hands that field to the hedge desk (VaR sizing
and the contract's agreed price, both fuels) and to the move-with-us offer as its cost. The segment
now asks `company/interfaces/renewal_offer.request_company_forward_estimate` at its own start. See
`docs/staging/SEAT_FINDING_THE_DEFAULT_TARIFF_SEGMENT_FORMS_ITS_OWN_FORWARD_2026-10-12.md`.

R15 MUTATIONS (each must red a test here):
  M1  restore `"company_forward_price_gbp_per_mwh": sim_fwd` -> the first test reds (the two
      forwards differ on these records, so the world's number cannot pass for the company's).
  M2  ask the door with `notice_date` shifted (e.g. the segment's END) -> the first test reds.
  M3  drop the fallback (`fallback_gbp_per_mwh=0.0`) -> the second test reds.
"""
from __future__ import annotations

from datetime import date, timedelta

import simulation.svt_product as sp
from company.interfaces.renewal_offer import request_company_forward_estimate


def _records(start: date, days: int) -> list[dict]:
    """A rising daily NBP-shaped series, so the company's EWMA and the world's mean disagree."""
    return [
        {"settlementDate": (start + timedelta(days=i)).isoformat(),
         "systemSellPrice": 20.0 + 0.15 * i}
        for i in range(days)
    ]


def test_every_segment_carries_the_companys_estimate_at_its_own_start():
    """The company field is the door's answer on the segment's start date, and that answer is
    not the world's forward on at least one segment -- else this control could not tell them apart."""
    records = _records(date(2018, 6, 1), 700)
    schedule = sp.build_svt_schedule("C-OWN", "2019-01-15", "2019-12-31", records, fuel="gas")
    assert len(schedule) >= 3
    differs = 0
    for seg in schedule:
        expected = request_company_forward_estimate(
            commodity="gas", notice_date=seg["acquisition_date"],
            observable_price_records=records,
            fallback_gbp_per_mwh=seg["forward_price_gbp_per_mwh"],
        )
        assert seg["company_forward_price_gbp_per_mwh"] == expected, seg["acquisition_date"]
        differs += seg["company_forward_price_gbp_per_mwh"] != seg["forward_price_gbp_per_mwh"]
    assert differs == len(schedule), (
        f"only {differs}/{len(schedule)} segments carry a company forward distinct from the world's")


def test_a_segment_the_company_has_no_record_for_falls_back_to_the_worlds_estimate(monkeypatch):
    """The cold-start branch (register §3a's owed leak) is reachable and returns the world's number,
    rather than a zero that would hedge the segment off a free commodity."""
    monkeypatch.setattr(sp, "generate_forward_price", lambda *a, **k: 61.5)
    schedule = sp.build_svt_schedule("C-COLD", "2019-01-15", "2019-06-30", [], fuel="electricity")
    assert schedule
    assert all(seg["company_forward_price_gbp_per_mwh"] == 61.5 for seg in schedule)
