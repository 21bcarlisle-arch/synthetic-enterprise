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


def test_the_poisoned_module_bites_and_is_otherwise_datetime():
    """Vacuity guard for leg 3: the stand-in must raise on a clock read and change nothing else."""
    pdt = _poisoned_datetime_module()
    with pytest.raises(AssertionError, match="wall clock"):
        pdt.date.today()
    with pytest.raises(AssertionError, match="wall clock"):
        pdt.datetime.now(pdt.timezone.utc)
    assert isinstance(date(2019, 1, 1), pdt.date) and isinstance(pdt.date(2019, 1, 1), date)
    assert pdt.timedelta is _real_dt.timedelta


def test_a_2024_payment_snapshot_never_reads_today(monkeypatch):
    import company.billing.payment_observation_consumer as pobs
    from interface.contracts.payment_observable_seam import PaymentRail, RemittanceAdvice
    from interface.contracts.wall_envelope import WallResponse, WallStatus

    monkeypatch.setattr(pobs, "dt", _poisoned_datetime_module())
    value_date = date(2024, 3, 11)
    advice = RemittanceAdvice(bank_reference="INV-9001", account_id="ACC-9001", amount_gbp=142.75,
                              rail=PaymentRail.BACS_DIRECT_DEBIT, value_date=value_date)
    consumer = pobs.PaymentObservationConsumer()
    assert consumer.observe(WallResponse(
        correlation_id="INV-9001", status=WallStatus.OK, schema_version=1,
        observed_at=datetime(2024, 3, 11, 6, 0), valid_time=value_date, payload=advice,
    )) is True
    assert consumer.snapshot("ACC-9001", as_of=date(2024, 3, 31)) \
        .allocation.unallocated_credit_gbp > 0.0
    assert consumer.snapshot("ACC-9001", as_of=date(2024, 3, 1)) \
        .allocation.unallocated_credit_gbp == 0.0, "a payment after the run's date is invisible"
    with pytest.raises(ValueError, match="as_of"):
        consumer.snapshot("ACC-9001", as_of=None)


def test_a_2019_retention_feature_vector_never_reads_today(monkeypatch):
    import company.crm.retention_risk as rr

    monkeypatch.setattr(rr, "date", _PoisonedDateAll)
    inv = {"customer_id": "C1", "payment_status": "unpaid", "due_date": "2019-05-15"}
    complaint = {"customer_id": "C1", "complaint_flag": True, "event_date": "2019-05-20"}
    vec = rr.retention_risk_feature_vector({"customer_id": "C1"}, [inv], [complaint],
                                           as_of=date(2019, 6, 1))
    assert (vec["overdue_invoice"], vec["recent_complaint_90d"]) == (1.0, 1.0)
    with pytest.raises(ValueError, match="as_of"):
        rr.retention_risk_feature_vector({"customer_id": "C1"}, [inv], [], as_of=None)


class _StubPaymentBehaviour:
    DEFAULT_CREDIT_RISK = "high"
    CREDIT_RISK_BY_CUSTOMER: dict = {}

    def bad_debt_provision_gbp(self, credit_risk, total_amount_gbp):
        return round(total_amount_gbp * 0.10, 2)

    def expected_payment_date(self, period_end, credit_risk):
        return "2019-03-01"


def test_a_2019_ledger_replay_records_its_decisions_on_the_runs_clock(monkeypatch):
    import company.governance.decision_rights as dr
    from saas.ledger import build_ledger

    monkeypatch.setattr(dr, "dt", _poisoned_datetime_module())
    own = BitemporalEventLog()
    monkeypatch.setattr(dr, "_DECISION_LOG", own)
    bill = {"customer_id": "C1", "period_start": "2019-01-01", "period_end": "2019-01-31",
            "total_amount_gbp": 1_000.0, "total_consumption_kwh": 2_000.0}
    build_ledger([], [bill], _StubPaymentBehaviour())
    stamps = [r.transaction_time for r in own.all_records()]
    assert stamps, "the replay logged no decision -- this control has no subject"
    assert all(t.date() == date(2019, 3, 1) for t in stamps), stamps
    with pytest.raises(ValueError, match="transaction_time"):
        dr.log_decision_event(dr.DecisionClass.PRICING_MOVE, entity_id="C1", request={},
                              context={}, decision={}, rationale="",
                              valid_time=date(2019, 1, 1), log=own)
    with pytest.raises(ValueError, match="submitted_at"):
        dr.submit_decision_request(dr.DecisionClass.PRICING_MOVE, entity_id="C1", request={},
                                   context={}, valid_time=date(2019, 1, 1), log=own)


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
WALL_CLOCK_READS_2026_10_03 = {
    "company/billing/account_closure.py": 1,
    "company/billing/collections.py": 2,
    "company/billing/contract.py": 2,
    "company/billing/direct_debit.py": 1,
    "company/billing/invoice.py": 1,
    "company/billing/meter_assets.py": 1,
    "company/billing/ppm_warrant_register.py": 1,
    "company/billing/switching.py": 1,
    "company/compliance/consumer_duty_board_report.py": 1,
    "company/crm/contract_exposure_register.py": 1,
    "company/crm/home_registry.py": 4,
    "company/crm/retention_risk.py": 1,
    "company/crm/service_log.py": 1,
    "company/finance/customer_lifetime_revenue.py": 1,
    "company/pricing/switching_recommendation.py": 1,
    "company/regulatory/ico_breach_register.py": 1,
    "company/regulatory/ofgem_redress_register.py": 1,
    "company/regulatory/statutory_accounts_register.py": 1,
}


def test_every_honest_read_names_a_live_read():
    """An entry whose read was deleted would silently excuse the next one written there."""
    dead = {k: v for k, v in HONEST_READS.items() if k[1] not in _clock_read_sites(REPO / k[0])}
    assert not dead, f"HONEST_READS entries naming no wall-clock read -- delete them: {dead}"


def test_an_honest_read_excuses_its_function_not_its_file(tmp_path, monkeypatch):
    """A new read in an allowlisted file, outside the named function, is still counted."""
    probe = REPO / "company/portal/app.py"
    assert _clock_reads(probe) == 0 < len(_clock_read_sites(probe))
    fake = tmp_path / "company/portal/app.py"
    fake.parent.mkdir(parents=True)
    fake.write_text(probe.read_text(encoding="utf-8")
                    + "\n\ndef some_new_handler():\n    return date.today()\n", encoding="utf-8")
    monkeypatch.setitem(globals(), "REPO", tmp_path)
    assert _clock_reads(fake) == 1


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
