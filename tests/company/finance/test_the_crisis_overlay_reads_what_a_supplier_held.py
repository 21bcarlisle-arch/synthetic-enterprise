"""The forward-looking overlay sized from what a supplier held at each date
(`company/finance/bad_debt_provision.with_crisis_overlay`; bad_debt_provisioning.md, "Sizing the
forward-looking overlay from what a supplier held in 2022", 2026-10-24).

Each test names the defect it fires on.
"""
from __future__ import annotations

import ast
import datetime as dt
import inspect

import pytest

from company.billing.account_ledger import LedgerBook, LedgerEvent, LedgerEventType
from company.billing.payment_observation_consumer import PaymentObservationConsumer
from company.finance import bad_debt_provision as bdp
from company.policy.decision_policy import CURRENT_POLICY

TT = dt.datetime(2020, 1, 1)


def _year_ends():
    return {y: bdp.crisis_overlay_share(dt.date(y, 12, 31)) for y in range(2017, 2026)}


def test_the_overlay_fires_in_2022_and_is_zero_in_a_calm_year():
    """Defect: an overlay that never fires (a guard that refuses everything passes every refusal test)
    or one that is always on (a fixed share by another name). One control over the whole partition:
    the crisis year end carries the published high, a year end whose cap fell carries nothing, a
    year end with a smaller rise carries less, and a pre-cap date carries a reason."""
    by_year = _year_ends()
    high = dict(bdp.OVERLAY_SHARE_ENDS)["published_high"]
    fired = {y for y, (share, _, _) in by_year.items() if share > 0}
    calm = {y for y, (share, ratio, _) in by_year.items() if ratio is not None and share == 0}
    unread = {y for y, (_, ratio, reason) in by_year.items() if ratio is None and reason}
    assert 2022 in fired and calm and unread, (fired, calm, unread)
    assert by_year[2022][0] == pytest.approx(high)
    assert {2020, 2023, 2024} <= calm, by_year
    assert 0 < by_year[2021][0] < by_year[2022][0], by_year
    assert unread == {2017, 2018, 2019}, by_year  # Dec 2018 had no cap


def test_the_share_moves_with_the_signal_and_never_past_the_published_high():
    """Defect: a share that falls as the cap rises, or that passes the published high (B5.5.52's
    directional consistency, and the one size the record supports)."""
    pairs = sorted((ratio, share) for share, ratio, _ in _year_ends().values() if ratio is not None)
    shares = [s for _, s in pairs]
    assert shares == sorted(shares), pairs
    assert max(shares) <= dict(bdp.OVERLAY_SHARE_ENDS)["published_high"] + 1e-12


def test_the_signal_reads_only_the_cap_in_force_on_the_date():
    """Defect: look-ahead. The crisis year end's signal must not move if every cap window after it
    were different -- it is the window in force on 31 Dec 2022 against the one a year earlier."""
    on = dt.date(2022, 12, 31)
    assert bdp.cap_ratio(on) == pytest.approx(bdp.cap_level(on) / bdp.cap_level(dt.date(2021, 12, 31)))
    src = inspect.getsource(bdp.cap_level)
    assert "get_cap_unit_rate_for_date(fuel, on)" in src


def _book():
    book = LedgerBook()
    book.post(LedgerEvent("A-b", "A", LedgerEventType.BILL_DEBIT, 300.0, dt.date(2022, 11, 1), TT))
    return book


def test_the_switch_off_publishes_the_matrix_unchanged_and_on_grosses_the_overlay():
    """Defect: a switch that does nothing when on, or that moves the published stock when off."""
    consumer = PaymentObservationConsumer(ledger_book=_book())
    on = dt.date(2022, 12, 31)
    method = lambda a, d: "direct_debit"  # noqa: E731
    off = consumer.provision_stock(on, payment_method_of=method)
    lit = consumer.provision_stock(on, payment_method_of=method, crisis_overlay=True)
    assert "crisis_overlay" not in off and off["provision_gbp"] > 0
    assert lit["matrix_provision_gbp"] == off["provision_gbp"]
    share = lit["crisis_overlay"]["share"]
    assert share > 0
    assert lit["provision_gbp"] == pytest.approx(off["provision_gbp"] / (1 - share), abs=0.01)
    assert lit["buckets"] == off["buckets"]


def test_the_policy_switch_is_off_by_default_and_reaches_the_runs_read():
    """Defect: a switch the run never passes, so turning it on changes nothing that is published."""
    assert CURRENT_POLICY.provision_crisis_overlay is False
    import simulation.run_phase2b as rp
    tree = ast.parse(inspect.getsource(rp))
    calls = [c for c in ast.walk(tree) if isinstance(c, ast.Call)
             and getattr(c.func, "id", None) == "_company_provision_by_year_end"]
    assert calls and all(any(k.arg == "crisis_overlay" and ast.unparse(k.value)
                             == "policy.provision_crisis_overlay" for k in c.keywords)
                         for c in calls)
