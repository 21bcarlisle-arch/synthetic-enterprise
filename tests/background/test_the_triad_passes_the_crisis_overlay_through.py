"""The run's provision read reaches the company's crisis overlay through the triad's door.

DEFECT LINE: E6 (2410634ae) had `_company_provision_by_year_end` pass `crisis_overlay=` to
`LivePaymentTriad.provision_stock`, whose signature did not take it. The TypeError was caught as "a
reporting read must not kill a completed run", so every run published `company_provision` as
unavailable and only a WARNING line said so (seen on a 2016-12-31 run, 24 Oct).
"""
from __future__ import annotations

from datetime import date

from background.live_payment_triad import LivePaymentTriad


def test_the_overlay_switch_reaches_the_consumer_and_its_absence_leaves_none():
    triad = LivePaymentTriad()
    method = lambda account, on: "direct_debit"  # noqa: E731
    on = date(2016, 12, 31)
    assert "crisis_overlay" in triad.provision_stock(on, payment_method_of=method, crisis_overlay=True)
    assert "crisis_overlay" not in triad.provision_stock(on, payment_method_of=method)
