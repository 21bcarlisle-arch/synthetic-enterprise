"""PB8 L2, the seam half: `get_payment_method(..., as_of=)` reports pay-on-receipt once the supplier
has stopped the household's DD and told it, and not before.

The money side has followed the stop since dd7bbce0f. The seam answered the fixed-for-life draw, and
the seam is what the renewal price and the engagement antecedent read in `run_phase2b`. So a stopped
household was priced and engagement-weighted as direct debit at every later renewal.

The bills a stop is decided on are assembled after `run_phase2b` (in `run_phase4c_on_phase2b`), so
the run cannot ask the money side's register. `StopNoticeBoard` asks the same question of the
records the run has settled so far, by the same route, cut at the date.
"""
import pytest

import simulation.dd_collection_book as dcb
import simulation.run_phase4c_on_phase2b as p4c
from company.interfaces.sim_interface import LiveSimInterface
from tests.simulation.test_a_stopped_dd_is_paid_on_receipt_by_the_money_side import _book, _is_dd

MONTH_STARTS = ["2022-%02d-01" % m for m in range(1, 13)] + ["2023-01-01", "2023-03-15"]


def test_a_households_notices_come_from_its_own_bills_alone():
    """What the board relies on: a household's stop and its notice date do not depend on any other
    household's bills. One rails-lag stream walked in customer order broke this, because a notice
    date then hung on how many failures sorted before it."""
    bills, behavioral = _book()
    full = dcb.supplier_dd_stop_notices(bills, behavioral, 42)
    assert len(full) >= 3, full
    for cid, notice in full.items():
        own = [b for b in bills if b["customer_id"] == cid]
        assert dcb.supplier_dd_stop_notices(own, behavioral, 42) == {cid: notice}


def test_a_notice_comes_after_the_last_bill_presented_by_dd():
    bills, behavioral = _book()
    stops = dcb.supplier_dd_stops(bills, behavioral, 42)
    notices = dcb.supplier_dd_stop_notices(bills, behavioral, 42)
    assert set(stops) == set(notices)
    assert all(notices[c] > stops[c] for c in stops), (stops, notices)


def _board_over_the_book(monkeypatch):
    """A board whose bill assembly is the identity on bill-shaped records, so the cut is all that
    is under test. Each bill becomes one record dated on its period end."""
    bills, behavioral = _book()
    monkeypatch.setattr(p4c, "build_monthly_bills", lambda records, churned: list(records))
    monkeypatch.setattr("company.interfaces.bill_assembly.issued_bills", lambda b: b)
    board = dcb.StopNoticeBoard(lambda cid: behavioral[cid]["income_stress_trajectory"])
    board.observe([{**b, "settlement_date": b["period_end"]} for b in bills])
    return board, dcb.supplier_dd_stop_notices(bills, behavioral, 42)


def test_the_board_equals_the_money_sides_register_cut_at_every_date(monkeypatch):
    """Asked in date order, as the run asks it, every (household, date) answer is the full register's
    notice when that notice is on or before the date, and nothing otherwise. Both answers occur."""
    board, full = _board_over_the_book(monkeypatch)
    answers = []
    for cid in sorted(full) + ["PB8L2-%02d" % i for i in range(40)]:
        for d in MONTH_STARTS:
            want = full[cid] if cid in full and full[cid] <= d else None
            got = board.notice_as_of(cid, d)
            assert got == want, (cid, d, got, want)
            answers.append(got)
    assert any(a is None for a in answers) and any(a is not None for a in answers)


def test_a_known_stop_is_not_reported_on_a_date_before_its_notice(monkeypatch):
    """Asked late first, then early: the stop the board has found must not leak backwards."""
    board, full = _board_over_the_book(monkeypatch)
    cid, notice = min(full.items(), key=lambda kv: kv[1])
    assert board.notice_as_of(cid, "2023-03-15") == notice
    assert board.notice_as_of(cid, "2022-01-01") is None


class _FixedBoard:
    def __init__(self, notice):
        self.notice = notice

    def notice_as_of(self, supply_point, as_of):
        return self.notice if self.notice <= as_of else None


def _households():
    dd = next(f"PB8L2-{i:02d}" for i in range(40) if _is_dd(f"PB8L2-{i:02d}"))
    other = next(f"PB8L2-{i:02d}" for i in range(40) if not _is_dd(f"PB8L2-{i:02d}"))
    return dd, other


def test_the_seam_reports_pay_on_receipt_after_the_notice_and_dd_before_it():
    dd, other = _households()
    seam = LiveSimInterface()
    dcb.install_stop_notice_board(_FixedBoard("2022-06-10"))
    try:
        before = seam.get_payment_method(dd, "electricity", as_of="2022-06-09")
        after = seam.get_payment_method(dd, "electricity", as_of="2022-06-10")
        untouched = seam.get_payment_method(other, "electricity", as_of="2022-06-10")
        undated = seam.get_payment_method(dd, "electricity")
    finally:
        dcb.install_stop_notice_board(None)
    assert (before, after, undated) == ("direct_debit", "standard_credit", "direct_debit")
    assert untouched == seam.get_payment_method(other, "electricity") != "direct_debit"


def test_a_dated_question_with_no_board_is_refused_by_name():
    dd, _ = _households()
    dcb.install_stop_notice_board(None)
    with pytest.raises(ValueError, match="stop-notice board"):
        LiveSimInterface().get_payment_method(dd, "electricity", as_of="2022-06-10")


def test_the_gas_question_asks_the_gas_supply_point():
    asked = []

    class _Recording:
        def supply_point_billed(self, household, fuel):
            return household + "g"

        def notice_as_of(self, supply_point, as_of):
            asked.append(supply_point)
            return None

    from simulation.household_segments import PaymentChannel, payment_channel_for_customer
    dd = next(f"PB8L2-{i:02d}" for i in range(40) if _is_dd(f"PB8L2-{i:02d}") and
              payment_channel_for_customer(f"PB8L2-{i:02d}", "gas") is PaymentChannel.DIRECT_DEBIT)
    dcb.install_stop_notice_board(_Recording())
    try:
        LiveSimInterface().get_payment_method(dd, "gas", as_of="2022-06-10")
        LiveSimInterface().get_payment_method(dd, "electricity", as_of="2022-06-10")
    finally:
        dcb.install_stop_notice_board(None)
    assert asked == [dd + "g", dd]


@pytest.mark.parametrize("leg", ["", "g"], ids=["gas_only_no_suffix", "dual_fuel_gas_leg"])
def test_the_gas_question_finds_the_stop_on_the_leg_the_run_billed(monkeypatch, leg):
    """The gas question used to spell the leg `household + "g"`. A gas-only household's one leg has
    no suffix (`SYN-2016-021`), so its stop was never found and it read direct debit at every later
    renewal while the money side paid it on receipt. The same book billed as gas, under each id
    shape: both must find the stop after its notice, and not before it."""
    book, stress = _book()
    bills = [{**b, "customer_id": b["customer_id"] + leg, "commodity": "gas"} for b in book]
    behavioral = {cid + leg: v for cid, v in stress.items()}
    monkeypatch.setattr(p4c, "build_monthly_bills", lambda records, churned: list(records))
    monkeypatch.setattr("company.interfaces.bill_assembly.issued_bills", lambda b: b)
    full = dcb.supplier_dd_stop_notices(bills, behavioral, 42)
    from simulation.household import household_of
    from simulation.household_segments import PaymentChannel, payment_channel_for_customer
    cid, notice = next((household_of(sp), n) for sp, n in sorted(full.items())
                       if payment_channel_for_customer(sp, "gas") is PaymentChannel.DIRECT_DEBIT)
    board = dcb.StopNoticeBoard(lambda sp: behavioral[sp]["income_stress_trajectory"])
    board.observe([{**b, "settlement_date": b["period_end"]} for b in bills])
    seam = LiveSimInterface()
    day_before = (dcb.date.fromisoformat(notice) - dcb.timedelta(days=1)).isoformat()
    dcb.install_stop_notice_board(board)
    try:
        after = seam.get_payment_method(cid, "gas", as_of=notice)
        before = seam.get_payment_method(cid, "gas", as_of=day_before)
    finally:
        dcb.install_stop_notice_board(None)
    assert (before, after) == ("direct_debit", "standard_credit"), (cid + leg, notice)
