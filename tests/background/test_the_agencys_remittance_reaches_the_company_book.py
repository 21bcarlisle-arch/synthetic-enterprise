"""The agency's remittance on a written-off debt reaches the company's book as cash earmarked to it.

In-run, the per-debt sale rule's learner (`cash_forecast_provision._written_off`) reads cash after a
written-off bill's write-off, earmarked to that bill. The agency's remittance used to stop at the
post-run page as a `recovery_note`, so the learner resolved nothing and every debt was decided at the
prior. Finding: `docs/staging/SEAT_FINDING_THE_HELD_PER_DEBT_SALE_RULE_LEARNS_A_WINDOW_THE_AGENCY_
NEVER_PAYS_INTO_2026-11-20.md`, "In-run successor" (I0-I5). Knowledge:
`docs/market_research/debt_and_collections.md` s.7.7.
"""
import datetime as dt

from background.live_payment_triad import LivePaymentTriad
from company.billing.account_ledger import LedgerEvent, LedgerEventType
from company.finance.cash_forecast_provision import _written_off
from simulation.arrears_engine import (
    DCA_OUTCOME_DAYS,
    dca_placement_date,
    dca_recovered_amount,
)

T = LedgerEventType
LAST_ISSUE = dt.date(2018, 3, 1)


def _triad():
    """Account A, three unpaid bills: one aged (due 400 days before the last bill), one young (due
    30 days before it) and the final bill, so the sweep writes each off under its own ref."""
    triad = LivePaymentTriad()
    for ref, due in (("A::1", LAST_ISSUE - dt.timedelta(days=400)),
                     ("A::2", LAST_ISSUE - dt.timedelta(days=30)),
                     ("A::3", LAST_ISSUE + dt.timedelta(days=14))):
        issue = due - dt.timedelta(days=14)
        triad._ledger_book.post(LedgerEvent(f"bill:{ref}", "A", T.BILL_DEBIT, 100.0, issue,
                                            dt.datetime.combine(issue, dt.time(0)), invoice_ref=ref))
        triad._bill_due_by_ref[ref] = due
    triad._last_issue_by_account["A"] = LAST_ISSUE
    return triad


def _remitted_by_ref(triad, through):
    return {ref: (stage, on, gbp) for _a, ref, stage, on, gbp in triad.agency_remittances}


def test_each_written_off_bill_is_remitted_on_its_own_date_at_its_own_age():
    """One control over the partition: the aged bill AND the young one both cross, each at the
    world's own recovery for its age, on write-off + placement + outcome; and a remittance after the
    run's end does not cross. Defect: no remittance crosses, or every bill at one age."""
    triad = _triad()
    end = dt.date(2025, 12, 31)
    triad.write_off_closed_balances(end)
    got = _remitted_by_ref(triad, end)
    [wo_on] = {e.valid_time for e in triad._ledger_book.ledger("A").events()
               if e.event_type == T.WRITE_OFF_CREDIT}
    paid_on = dca_placement_date(wo_on) + dt.timedelta(days=DCA_OUTCOME_DAYS)
    assert got["A::1"] == ("RECOVERED", paid_on, dca_recovered_amount(100.0, 400))
    assert got["A::2"] == ("RECOVERED", paid_on, dca_recovered_amount(100.0, 30))
    assert got["A::1"][2] < got["A::2"][2]
    short = _triad()
    short.write_off_closed_balances(paid_on - dt.timedelta(days=1))
    assert short.agency_remittances == []


def test_the_company_book_carries_the_remittance_earmarked_to_the_written_off_bill():
    """The point: the learner sees it. Defect: cash that crosses but lands unearmarked, so
    `_written_off` reads no recovery."""
    triad = _triad()
    end = dt.date(2025, 12, 31)
    triad.write_off_closed_balances(end)
    seen = [cash for _wo, _gbp, _cell, cash in _written_off(triad._ledger_book.ledger("A"), end)]
    assert len(seen) == 3 and all(len(cash) == 1 for cash in seen)
    assert sorted(g for cash in seen for _d, g in cash) == sorted(
        gbp for *_x, gbp in triad.agency_remittances)


def test_a_second_sweep_places_nothing_twice():
    """Defect: the agency remitting the same debt on every sweep."""
    triad = _triad()
    end = dt.date(2025, 12, 31)
    triad.write_off_closed_balances(end)
    n = len(triad.agency_remittances)
    triad.write_off_closed_balances(end)
    assert len(triad.agency_remittances) == n == 3


def test_a_statute_barred_write_off_is_not_placed_with_the_agency():
    """A statute-barred write-off is on a live account, so no agency works it.
    Defect: every write-off placed, whatever its rule."""
    from company.billing.arrears_engine import WriteOffReason, build_write_off_event

    triad = _triad()
    barred_on = dt.date(2018, 6, 30)
    triad._ledger_book.post(build_write_off_event(
        "A", 100.0, WriteOffReason.STATUTE_BARRED, barred_on,
        dt.datetime.combine(barred_on, dt.time(23, 59)), invoice_ref="A::1"))
    triad.write_off_closed_balances(dt.date(2025, 12, 31))
    assert "A::1" not in _remitted_by_ref(triad, None)
    assert {"A::2", "A::3"} <= set(_remitted_by_ref(triad, None))


def test_the_run_end_record_publishes_refs_remittances_the_learned_cells_and_the_sale_split():
    """KNIFE3 I1-I5 need these on the book. One control over the partition: the record carries every
    write-off with its ref, every remittance as a row on a ref the company wrote off, a learned lag,
    BOTH age cells, and at an offer between the two cells' expectations the aged debt sold AND the
    young one worked. Defect: any of the four missing, or a sale split that cannot differ by cell."""
    triad = _triad()
    end = dt.date(2025, 12, 31)
    triad.write_off_closed_balances(end)
    rec = triad.debt_recovery_record(end, payment_method_of=lambda a, d: "direct_debit",
                                     offers=(0.0, 0.5))
    assert {r["invoice_ref"] for r in rec["write_offs"]} == {"A::1", "A::2", "A::3"}
    assert rec["share_of_gbp_with_invoice_ref"] == 1.0
    assert len(rec["agency_remittances"]) == 3
    assert rec["remitted_gbp"] == rec["remitted_gbp_on_a_ref_written_off"] > 0
    learned = rec["learned"]
    assert learned["remittance_lag_days"] == DCA_OUTCOME_DAYS + (
        dca_placement_date(end) - end).days
    aged, young = learned["by_cell"]["over_a_year_past_due"], learned["by_cell"]["under_a_year_past_due"]
    assert aged["expected_recovery"] < young["expected_recovery"]
    mid = (aged["expected_recovery"] + young["expected_recovery"]) / 2
    rec = triad.debt_recovery_record(end, payment_method_of=lambda a, d: "direct_debit",
                                     offers=(mid,))
    split = {d["over_a_year_past_due"]: d["sold_at"][f"{mid:.3f}"] for d in rec["sale_decisions"]}
    assert split == {True: True, False: False}
