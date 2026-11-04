"""A bill in a spell off DD is paid on receipt, so the DD balance book does not hold it.

The defect: the book admitted a bill on the method the account opened with, so an account whose DD
the supplier stopped (or the household cancelled at its bank) kept a level DD running for life, and
its annual reviews went on barring a balance on a mandate that no longer existed. On 0a6391d186,
£2,475.43 of the £20,448.73 barred at reviews was barred inside a spell off DD
(`docs/staging/done/SEAT_FINDING_THE_DD_BALANCE_BOOK_KEEPS_A_LEVEL_DD_RUNNING_AFTER_THE_MANDATE_ENDED_2026-11-03.md`;
back_billing_and_liability.md s.16). The key is the ledger's: `arrears_engine.paying_method`.
"""
from __future__ import annotations

from simulation.arrears_engine import payment_method
from simulation.dd_balance_book import build_dd_balance_book


def _dd_ids(n: int) -> list[str]:
    ids = [f"C{i}" for i in range(5000)
           if payment_method("resi", 90.0, f"C{i}", "electricity") == "direct_debit"]
    assert len(ids) >= n, "too few direct-debit ids in range"
    return ids[:n]


LIVE, STOPPED, BACK = _dd_ids(3)


def _bills(cid: str, amounts: list[float]) -> list[dict]:
    y, m, out = 2020, 1, []
    for amt in amounts:
        out.append({"customer_id": cid, "segment": "resi", "commodity": "electricity",
                    "period_start": f"{y:04d}-{m:02d}-01", "period_end": f"{y:04d}-{m:02d}-28",
                    "total_amount_gbp": amt})
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


# A debit opened short (£60 against £100), then use doubles: the review has a debit to seek.
AMOUNTS = [100.0] * 12 + [200.0] * 18
BILLS = _bills(LIVE, AMOUNTS) + _bills(STOPPED, AMOUNTS) + _bills(BACK, AMOUNTS)
OPENING = {LIVE: 60.0, STOPPED: 60.0, BACK: 60.0}
# STOPPED: last bill presented by DD is Sep 2020, still off at the end. BACK: off from Oct 2020,
# re-mandated after its Mar 2021 bill.
SPELLS = {STOPPED: [("2020-09-28", None)], BACK: [("2020-09-28", "2021-03-28")]}


def _book():
    return build_dd_balance_book(BILLS, OPENING, set(), seek_balance_at_review=True, dd_spells=SPELLS)


def test_a_live_mandate_is_still_reviewed_and_a_stopped_one_leaves_the_book_at_the_stop():
    book = _book()
    reviewed = {a["customer_id"] for a in book.bar_actions if a["action"] == "review"}
    # The partition first: a bill on a live mandate is admitted, and its review can bar.
    assert len(book.trajectories[LIVE]) == len(AMOUNTS) and LIVE in reviewed, book.summary()
    # The stopped account is held up to its last DD bill, and nothing after it.
    assert [p.month for p in book.trajectories[STOPPED]][-1] == "2020-09"
    assert len(book.trajectories[STOPPED]) == 9
    after_stop = [a for a in book.bar_actions + book.review_step_ups
                  if a["customer_id"] == STOPPED and a["date"] > "2020-09-28"]
    assert after_stop == [], after_stop


def test_a_re_signed_mandate_collects_one_month_on_its_first_bill_back():
    points = _book().trajectories[BACK]
    months = [p.month for p in points]
    # Off for Oct 2020 .. Mar 2021 (six bills), back from Apr 2021.
    assert "2020-12" not in months and months[9] == "2021-04", months
    # The spell collected nothing by DD, so the first bill back is funded by one collection.
    assert points[9].n_collections == 1, points[9]


def test_no_spells_reads_every_bill_on_the_mandate_it_opened_with():
    book = build_dd_balance_book(BILLS, OPENING, set(), seek_balance_at_review=True)
    assert all(len(book.trajectories[c]) == len(AMOUNTS) for c in (LIVE, STOPPED, BACK))
