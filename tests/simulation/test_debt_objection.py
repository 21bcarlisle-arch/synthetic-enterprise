"""The SLC 14 domestic debt objection stops a share of an indebted credit household's departures.

Defect it names: the world's departure draw ignored arrears entirely, so a domestic credit-meter
household owing its supplier money could always switch away -- under the real objection right,
Ofgem counts about 28% of such attempts blocked (`simulation/debt_objection.py`).
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import pytest

from simulation.customer_events import roll_lifecycle_event
from simulation.debt_objection import (
    DEBT_OBJECTION_BLOCKED_SHARE,
    DEBT_OBJECTION_ENV,
    WorldDebtBook,
    unblocked_tail_roll,
)
from simulation.payment_behaviour_source import (
    CARD,
    DIRECT_DEBIT,
    PREPAYMENT,
    REPRESENTATION_DAYS_AFTER_DUE,
)
from simulation.segment_vocabulary import is_business
from simulation.settlement import CONTRACT_LENGTH_DAYS

_PROJECT = Path(__file__).resolve().parents[2]
_ACQ = "2016-01-01"
_RENEWAL = (date.fromisoformat(_ACQ) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()


def _customers(cid: str) -> list[dict]:
    return [{"customer_id": cid, "commodity": "electricity", "segment": "resi",
             "epc_rating": "D", "acquisition_date": _ACQ}]


def _records(cid: str) -> list[dict]:
    return [{"customer_id": cid, "settlement_date": f"2016-{m:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": 50.0, "unit_rate_gbp_per_mwh": 150.0,
             "revenue_gbp": 7.5, "wholesale_cost_gbp": 5.0, "margin_gbp": 2.5,
             "capital_cost_gbp": 0.1, "net_margin_gbp": 2.4}
            for m in range(1, 13) for d in range(1, 29)]


def _pair(cid: str, eligible):
    base = roll_lifecycle_event(cid, _RENEWAL, "electricity", _records(cid), _customers(cid))
    asked = roll_lifecycle_event(cid, _RENEWAL, "electricity", _records(cid), _customers(cid),
                                 debt_objection_eligible=eligible)
    return base, asked


class _Rec:
    """The triad's `PeriodRecord` shape, for the fields the book reads."""

    def __init__(self, customer_id, due_date, result, payment_method, days_late=0,
                 settled_on=None):
        self.customer_id, self.due_date, self.result = customer_id, due_date, result
        self.payment_method, self.days_late = payment_method, days_late
        self.settled_on = settled_on


def test_the_blocked_share_is_ofgems_ratio_and_the_cited_file_carries_both_counts():
    assert DEBT_OBJECTION_BLOCKED_SHARE == pytest.approx(170 / 600)
    text = (_PROJECT / "docs/market_research/domestic_debt_objection_rates_gb.md").read_text()
    assert "430,000" in text and "170,000" in text


def test_a_debtors_p_stay_rises_by_exactly_the_blocked_share_of_its_departure_probability(
        monkeypatch):
    monkeypatch.delenv(DEBT_OBJECTION_ENV, raising=False)
    base, asked = _pair("C5", True)
    p = base["effective_retention_probability"]
    assert 0.0 < p < 1.0
    assert asked["effective_retention_probability"] == pytest.approx(
        p + (1 - p) * DEBT_OBJECTION_BLOCKED_SHARE, abs=1e-4)
    assert asked["realized_churn_probability"] < base["realized_churn_probability"]
    assert asked["debt_objection_eligible"] is True


@pytest.mark.parametrize("eligible", [None, False])
def test_a_non_debtor_is_unchanged(eligible):
    base, asked = _pair("C5", eligible)
    assert asked == base
    assert asked["departure_blocked_by_debt_objection"] is False


def test_the_switch_off_removes_the_block(monkeypatch):
    monkeypatch.setenv(DEBT_OBJECTION_ENV, "0")
    base, asked = _pair("C5", True)
    assert asked == base


def test_every_branch_of_the_partition_is_taken_and_a_block_is_exactly_the_slice_it_claims(
        monkeypatch):
    monkeypatch.delenv(DEBT_OBJECTION_ENV, raising=False)
    seen = {"blocked": 0, "left_anyway": 0, "stayed_anyway": 0}
    for i in range(200):
        base, asked = _pair(f"C{i}", True)
        if base is None:
            continue
        p0, p1, roll = (base["effective_retention_probability"],
                        asked["effective_retention_probability"], asked["random_roll"])
        # One roll decides stay/leave for every reader that checks `roll <= P(stay)`.
        assert (asked["event_type"] == "renewed") == (roll <= p1)
        if asked["departure_blocked_by_debt_objection"]:
            seen["blocked"] += 1
            assert base["event_type"] == "churned" and p0 < roll <= p1
            assert asked["departure_cause"] is None
        elif asked["event_type"] == "churned":
            seen["left_anyway"] += 1
            assert base["event_type"] == "churned" and asked["departure_cause"] is not None
        else:
            seen["stayed_anyway"] += 1
            assert base["event_type"] == "renewed"
    assert all(seen.values()), seen


def test_the_tail_map_is_the_identity_without_a_block_and_covers_the_whole_tail_with_one():
    assert unblocked_tail_roll(0.9, 0.4, 0.4) == 0.9
    assert unblocked_tail_roll(1.0, 0.4, 0.57) == pytest.approx(1.0)
    assert unblocked_tail_roll(0.570000001, 0.4, 0.57) == pytest.approx(0.4, abs=1e-6)


def test_the_book_holds_a_credit_meter_debt_28_days_past_due_and_never_a_prepayment_one():
    due = date(2017, 1, 28)
    records = [_Rec("H1", due, "failed", DIRECT_DEBIT), _Rec("H2g", due, "dispute", CARD),
               _Rec("H3", due, "failed", PREPAYMENT),
               _Rec("H4", due, "success", DIRECT_DEBIT, days_late=40),
               _Rec("H5", due, "success", DIRECT_DEBIT, days_late=10)]
    book = WorldDebtBook(records)
    day_27, day_30, day_45 = (due + timedelta(days=n) for n in (27, 30, 45))
    assert not book.owes_objectionable_debt("H1", day_27)  # inside SLC 14's 28 days
    assert book.owes_objectionable_debt("H1", day_30)
    assert book.owes_objectionable_debt("H2", day_30)  # the gas leg's debt is the household's
    assert not book.owes_objectionable_debt("H3", day_45)  # prepayment: Debt Assignment Protocol
    assert book.owes_objectionable_debt("H4", day_30)
    assert not book.owes_objectionable_debt("H4", day_45)  # paid on day 40
    assert not book.owes_objectionable_debt("H5", day_30)
    # Records the triad appends later are read on the next question.
    records.append(_Rec("H6", due, "failed", DIRECT_DEBIT))
    assert book.owes_objectionable_debt("H6", day_30)


def test_a_later_settlement_ends_the_debt_on_its_date_and_an_unsettled_debt_never_ends():
    """Defect: a failed bill was never paid afterwards in the world's truth, so one missed bill
    made a household objectionable for the rest of the run (56% of renewals on a full run)."""
    due = date(2018, 3, 15)
    paid = due + timedelta(days=120)
    book = WorldDebtBook([_Rec("H1", due, "failed", DIRECT_DEBIT, settled_on=paid),
                          _Rec("H2", due, "failed", CARD)])
    assert book.owes_objectionable_debt("H1", due + timedelta(days=30))
    assert book.owes_objectionable_debt("H1", paid - timedelta(days=1))
    assert not book.owes_objectionable_debt("H1", paid)  # the cure is read
    assert book.owes_objectionable_debt("H2", due + timedelta(days=3650))  # the non-payer stays


@pytest.fixture(scope="module")
def _live_run():
    import background.live_payment_triad as lpt
    from simulation.run_phase2b import main as run_phase2b

    captured, segments = [], {}
    original, original_record = lpt.LivePaymentTriad.__init__, lpt.LivePaymentTriad.record_period

    def _capture(self, *a, **k):
        original(self, *a, **k)
        captured.append(self)

    def _record(self, **k):
        segments[(k["customer_id"], k["due_date"])] = k.get("segment", "resi")
        return original_record(self, **k)

    mp = pytest.MonkeyPatch()
    mp.setattr(lpt.LivePaymentTriad, "__init__", _capture)
    mp.setattr(lpt.LivePaymentTriad, "record_period", _record)
    try:
        result = run_phase2b(report_end="2017-06-30")
    finally:
        mp.undo()
    result["_triad_records"] = list(captured[-1].records)
    result["_triad_segments"] = segments
    return result


def test_a_live_run_holds_an_indebted_credit_household_at_a_renewal(_live_run):
    """The rare branch is takeable in the real world: the first window with a renewal by a
    household the triad's own truth says owes debt 28 days past due (8 of 15 renewals here,
    2026-10-03; 6 of 15 once a failed bill could be paid off later, 2026-10-04)."""
    rolled = [e for e in _live_run["customer_events"] if "debt_objection_eligible" in e]
    assert rolled, "no renewal was rolled, so this proves nothing"
    eligible = [e for e in rolled if e["debt_objection_eligible"]]
    assert eligible
    assert len(eligible) < len(rolled)


def test_a_live_run_cures_some_unpaid_bills_and_leaves_others_unpaid(_live_run):
    """The rare branches are takeable in the real world: on the run's own records at least one
    failed bill is collected on re-presentation, at least one is paid off later, and at least one
    never is. (Re-keyed 2026-10-09: a returned DD is now re-presented 14 days after its due date, so
    "every cure is past day 28" became "every cure is the re-presentation or past day 28".)"""
    segments = _live_run["_triad_segments"]
    failed = [r for r in _live_run["_triad_records"] if r.result == "failed"
              and not is_business(segments[(r.customer_id, r.due_date)])]
    cured = [r for r in failed if r.settled_on is not None]
    never = [r for r in failed if r.settled_on is None]
    assert cured and never, (len(cured), len(never))
    re_presented = [r for r in cured
                    if r.settled_on == r.due_date + timedelta(days=REPRESENTATION_DAYS_AFTER_DUE)]
    later = [r for r in cured if r not in re_presented]
    assert re_presented and later, (len(re_presented), len(later))
    assert all(r.payment_method == DIRECT_DEBIT for r in re_presented)
    assert all(r.settled_on > r.due_date + timedelta(days=28) for r in later)
