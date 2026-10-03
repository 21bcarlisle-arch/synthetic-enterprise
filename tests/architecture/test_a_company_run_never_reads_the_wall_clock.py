"""A company module inside a simulated run must not read the machine's calendar.

The company lives through 2016-2025. A `date.today()` inside it answers "2026" (or whatever day
the run was launched), so a deadline, an age or an "is it overdue" measured against it is wrong
by years and changes with the launch date -- the run stops being a pure function of its inputs.

TWO LEGS.
  1. THE INSTANCE THAT OPENED THIS (2026-10-03): `gsop_tracker.GSoPBreach.working_days_open`
     fell back to `date.today()` for an unresolved breach. It now takes the run's as-of date and
     refuses a missing one. The control replays a 2019 run through every public surface of the
     tracker with the module's `date.today` POISONED, so any read of the wall clock raises rather
     than quietly answering.
  2. THE CLASS, AS A RATCHET. 33 other wall-clock reads remain in company/ (counted by AST, per
     file, below). Some are honest -- a portal request stamp, a governance transaction time -- and
     many are the same defect as leg 1. Sorting them is its own work; this leg only stops the
     count GROWING and makes every removal shrink it: a new read, or a file's count rising, reds;
     an entry naming more reads than the file now has reds too ("delete or lower it").
"""
from __future__ import annotations

import ast
import collections
from datetime import date
from pathlib import Path

import pytest

import company.regulatory.gsop_tracker as gsop_tracker
from company.regulatory.gsop_tracker import GSoPBreachStatus, GSoPStandard, GSoPTracker

REPO = Path(__file__).resolve().parents[2]
CLOCK_ATTRS = {"today", "now", "utcnow"}
CLOCK_OWNERS = {"date", "datetime", "_date", "_datetime"}


class _PoisonedDate(date):
    @classmethod
    def today(cls):  # noqa: D401
        raise AssertionError("a simulated run read the wall clock (date.today())")


def test_a_2019_run_through_the_gsop_tracker_never_reads_today(monkeypatch):
    monkeypatch.setattr(gsop_tracker, "date", _PoisonedDate)
    run_date = date(2019, 6, 28)
    t = GSoPTracker()
    a = t.record_breach("A1", GSoPStandard.APPOINTMENT_MISSED, date(2019, 6, 3))
    b = t.record_breach("A2", GSoPStandard.BILLING_DELAY, date(2019, 6, 10))
    t.compensate_breach(b.breach_id, date(2019, 6, 14))
    for _ in range(6):
        t.record_breach("A3", GSoPStandard.FINAL_BILL_DELAY, date(2019, 6, 20))
    t.waive_breach(a.breach_id)
    # every public surface, on the run's own date
    for breach in t.breaches_for_standard(GSoPStandard.FINAL_BILL_DELAY) + t.open_breaches():
        assert 0 <= breach.working_days_open(run_date) < 30
    assert t.breaches_for_standard(GSoPStandard.BILLING_DELAY)[0].working_days_open(run_date) == 4
    assert t.is_systemic(GSoPStandard.FINAL_BILL_DELAY)
    assert t.gsop_summary()["compensated_count"] == 1
    assert t.total_compensation_outstanding_gbp() == 180.0
    assert t.breach_rate_per_100_customers(100) == 8.0
    assert t.breaches_by_standard()["final_bill_delay"] == 6
    assert t.open_breaches()[0].status is GSoPBreachStatus.OPEN


def test_the_poison_bites(monkeypatch):
    """Vacuity guard: if the poison did not reach the module, leg 1 would pass on any code."""
    monkeypatch.setattr(gsop_tracker, "date", _PoisonedDate)
    with pytest.raises(AssertionError, match="wall clock"):
        gsop_tracker.date.today()


def _clock_reads(path: Path) -> int:
    n = 0
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in CLOCK_ATTRS:
            owner = node.func.value
            name = owner.id if isinstance(owner, ast.Name) else getattr(owner, "attr", None)
            if name in CLOCK_OWNERS:
                n += 1
    return n


def census() -> dict:
    out = collections.Counter()
    for path in sorted((REPO / "company").rglob("*.py")):
        k = _clock_reads(path)
        if k:
            out[path.relative_to(REPO).as_posix()] = k
    return dict(out)


#: Wall-clock reads per company file on 2026-10-03, after gsop_tracker's was removed. MAY ONLY
#: SHRINK. Not a judgement that any of these is acceptable -- an inventory of what is unsorted.
WALL_CLOCK_READS_2026_10_03 = {
    "company/billing/account_closure.py": 1,
    "company/billing/collections.py": 2,
    "company/billing/contract.py": 2,
    "company/billing/direct_debit.py": 1,
    "company/billing/invoice.py": 1,
    "company/billing/meter_assets.py": 1,
    "company/billing/payment_observation_consumer.py": 1,
    "company/billing/ppm_warrant_register.py": 1,
    "company/billing/switching.py": 1,
    "company/compliance/consumer_duty_board_report.py": 1,
    "company/compliance/sanity_adjudication.py": 1,
    "company/crm/contract_exposure_register.py": 1,
    "company/crm/home_registry.py": 4,
    "company/crm/retention_risk.py": 2,
    "company/crm/service_log.py": 1,
    "company/finance/customer_lifetime_revenue.py": 1,
    "company/governance/decision_rights.py": 2,
    "company/interfaces/market_feed_publication.py": 1,
    "company/market/price_feed.py": 1,
    "company/portal/app.py": 3,
    "company/pricing/switching_recommendation.py": 1,
    "company/regulatory/ico_breach_register.py": 1,
    "company/regulatory/ofgem_redress_register.py": 1,
    "company/regulatory/statutory_accounts_register.py": 1,
}


def test_the_census_sees_the_tree():
    """A census that counted nothing would make the ratchet below pass on any tree."""
    assert _clock_reads(REPO / "company/billing/collections.py") >= 1
    assert sum(census().values()) >= 20


def test_no_company_file_gains_a_wall_clock_read():
    live = census()
    grown = {f: (WALL_CLOCK_READS_2026_10_03.get(f, 0), n) for f, n in live.items()
             if n > WALL_CLOCK_READS_2026_10_03.get(f, 0)}
    assert not grown, (
        f"company files reading the machine's calendar MORE than on 2026-10-03 (was, now): {grown}. "
        "Take the run's as-of date as a parameter instead -- see gsop_tracker.working_days_open."
    )


def test_the_ratchet_only_shrinks():
    live = census()
    stale = {f: (n, live.get(f, 0)) for f, n in WALL_CLOCK_READS_2026_10_03.items()
             if live.get(f, 0) < n}
    assert not stale, f"reads removed -- lower or delete these entries (listed, now): {stale}"
    assert "company/regulatory/gsop_tracker.py" not in WALL_CLOCK_READS_2026_10_03
