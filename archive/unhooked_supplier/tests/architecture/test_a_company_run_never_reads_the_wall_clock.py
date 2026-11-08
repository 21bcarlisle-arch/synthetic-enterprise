# ARCHIVED LEGS of tests/architecture/test_a_company_run_never_reads_the_wall_clock.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/architecture/test_a_company_run_never_reads_the_wall_clock.py.
"""A company module inside a simulated run must not read the machine's calendar.

The company lives through 2016-2025. A `date.today()` inside it answers "2026" (or whatever day
the run was launched), so a deadline, an age or an "is it overdue" measured against it is wrong
by years and changes with the launch date -- the run stops being a pure function of its inputs.

THREE LEGS.
  1. THE INSTANCE THAT OPENED THIS (2026-10-03): `gsop_tracker.GSoPBreach.working_days_open`
     fell back to `date.today()` for an unresolved breach. It now takes the run's as-of date and
     refuses a missing one. The control replays a 2019 run through every public surface of the
     tracker with the module's `date.today` POISONED, so any read of the wall clock raises rather
     than quietly answering.
  2. THE CLASS, AS A RATCHET. Wall-clock reads in company/ are counted by AST, per file, below.
     A read that is about the MACHINE rather than the simulated world (a file's age, a live portal
     request) is named in HONEST_READS by (file, function) with its reason and is not counted, so
     the ratchet counts only the defect. A new read, or a file's count rising, reds; an entry
     naming more reads than the file now has reds too ("delete or lower it").
  3. THE ONES A RUN REACHES (sorted 2026-10-03). `payment_observation_consumer.snapshot` (reached
     by tools/couple_w2_11_d5.py), `retention_risk_feature_vector` (reached by
     tools/generate_shadow_html.py after every run) and `decision_rights.log_decision_event` /
     `submit_decision_request` (reached by saas/ledger.py's replay, which stamped 2016-2025
     write-off decisions as recorded in 2026) each now refuse a missing date. Each is replayed
     below with its module's clock POISONED.
"""
from __future__ import annotations

import ast
import collections
import datetime as _real_dt
import types
from datetime import date, datetime
from pathlib import Path

import pytest

import company.regulatory.gsop_tracker as gsop_tracker
from company.interfaces.bitemporal_event_log import BitemporalEventLog
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


# ---------------------------------------------------------------------------------------------
# Leg 3 -- the reads a run reaches, each replayed with its module's clock poisoned
# ---------------------------------------------------------------------------------------------


class _ClockPoisonMeta(type):
    # a real date/datetime still passes isinstance against the stand-in, so only the clock changes
    def __instancecheck__(cls, obj):
        return isinstance(obj, cls.__mro__[1])


class _PoisonedDateAll(date, metaclass=_ClockPoisonMeta):
    @classmethod
    def today(cls):  # noqa: D401
        raise AssertionError("a simulated run read the wall clock (date.today())")


class _PoisonedDatetime(datetime, metaclass=_ClockPoisonMeta):
    @classmethod
    def now(cls, tz=None):  # noqa: D401
        raise AssertionError("a simulated run read the wall clock (datetime.now())")

    @classmethod
    def utcnow(cls):  # noqa: D401
        raise AssertionError("a simulated run read the wall clock (datetime.utcnow())")

    today = utcnow


def _poisoned_datetime_module():
    """A stand-in for `import datetime as dt` whose date/datetime cannot read the clock."""
    mod = types.ModuleType("datetime")
    mod.__dict__.update(vars(_real_dt))
    mod.date, mod.datetime = _PoisonedDateAll, _PoisonedDatetime
    return mod








class _StubPaymentBehaviour:
    DEFAULT_CREDIT_RISK = "high"
    CREDIT_RISK_BY_CUSTOMER: dict = {}

    def bad_debt_provision_gbp(self, credit_risk, total_amount_gbp):
        return round(total_amount_gbp * 0.10, 2)

    def expected_payment_date(self, period_end, credit_risk):
        return "2019-03-01"




# ---------------------------------------------------------------------------------------------
# Leg 2 -- the ratchet
# ---------------------------------------------------------------------------------------------


def _clock_read_sites(path: Path) -> list:
    """The innermost enclosing function name of every wall-clock read in `path`."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    funcs = [f for f in ast.walk(tree) if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))]
    sites = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and node.func.attr in CLOCK_ATTRS:
            owner = node.func.value
            name = owner.id if isinstance(owner, ast.Name) else getattr(owner, "attr", None)
            if name in CLOCK_OWNERS:
                inside = [f for f in funcs if f.lineno <= node.lineno <= f.end_lineno]
                sites.append(min(inside, key=lambda f: f.end_lineno - f.lineno).name
                             if inside else "<module>")
    return sites


def _clock_reads(path: Path) -> int:
    rel = path.relative_to(REPO).as_posix()
    return sum(1 for fn in _clock_read_sites(path) if (rel, fn) not in HONEST_READS)


def census() -> dict:
    out = collections.Counter()
    for path in sorted((REPO / "company").rglob("*.py")):
        k = _clock_reads(path)
        if k:
            out[path.relative_to(REPO).as_posix()] = k
    return dict(out)


#: Reads about the MACHINE, not the simulated world -- not counted. Keyed by (file, function) so a
#: new read elsewhere in the same file is still counted. Every entry must name a live read.
HONEST_READS = {
    ("company/compliance/sanity_adjudication.py", "adjudicate"):
        "audit stamp: when the sanity daemon, a machine process, adjudicated a finding",
    ("company/interfaces/market_feed_publication.py", "publish_feed"):
        "when the feed FILE was written; read back only by PriceFeed.is_stale",
    ("company/market/price_feed.py", "is_stale"):
        "the age of the feed file on this machine, against that file's own write stamp",
    ("company/portal/app.py", "switch_tariff"):
        "live portal request (the portal serves in real time, outside any run): a reference seed",
    ("company/portal/app.py", "submit_contact"):
        "live portal request: the day the visitor submitted the contact form",
    ("company/portal/app.py", "smart_meter_post"):
        "live portal request: the day the visitor submitted the smart-meter form",
}

#: Wall-clock DEFECT reads per company file -- a simulated-world date that falls back to today.
#: MAY ONLY SHRINK. Lowered 2026-10-03 when the run-reached ones were fixed (leg 3) and the honest
#: ones moved to HONEST_READS. Every one left is reached by no run (no production importer) or
#: only by the portal, which has no run date to pass (retention_risk.retention_risk's fallback).
#: Five entries left 2026-11-08 with their modules for archive/unhooked_supplier/ (increment 2),
#: and contract_exposure_register's the same day (increment 3a).
WALL_CLOCK_READS_2026_10_03 = {
    "company/billing/account_closure.py": 1,
    "company/billing/collections.py": 2,
    "company/billing/contract.py": 2,
    "company/billing/direct_debit.py": 1,
    "company/billing/invoice.py": 1,
    "company/compliance/consumer_duty_board_report.py": 1,
    "company/crm/home_registry.py": 4,
    "company/crm/retention_risk.py": 1,
    "company/crm/service_log.py": 1,
    "company/pricing/switching_recommendation.py": 1,
}










