"""The desk's account-level write-off of a closed account reaches the page and the statement walk.

Defect it names: the page wrote off only the engine's per-invoice cases, so on the 4dee9854a4 book
121 accounts the desk wrote off printed GBP 17,782.71 the page never wrote off
(`docs/staging/SEAT_FINDING_THE_DESKS_WRITE_OFF_OF_A_CLOSED_ACCOUNT_NEVER_REACHED_THE_PAGE_2026-11-10.md`).
"""
from company.billing.statement_export import account_events
from tools.generate_payment_ledger_data import build_account_ledger, desk_write_off_postings

AS_OF = "2021-06-30"
DAY = "2020-06-30"


def _journey(gbp):
    return [{"account_id": "ACC-X", "exit": "write_off", "stages": [
        {"stage": "missed_payment", "on": "2019-07-20", "overdue_gbp": gbp},
        {"stage": "write_off", "on": DAY, "written_off_gbp": gbp,
         "rule": "closed_account_unpaid_a_year_after_its_final_bill"}]}]


def _leg(owed, desk, engine=0.0):
    """A closed leg with one unpaid final bill of `owed`; `engine` of it written off by a case."""
    arrears = []
    if engine:
        arrears = [{"invoice_number": 1, "arrears_gbp": engine, "stages": [
            {"stage": "WRITTEN_OFF", "date": DAY, "amount_gbp": engine, "note": "case"}]}]
    return {"invoices": [{"invoice_number": 1, "issue_date": "2019-06-30", "total_amount_gbp": owed}],
            "payments": [], "arrears_history": arrears, "collections_desk_journeys": _journey(desk)}


def _post(legs):
    postings, unposted = desk_write_off_postings(legs, AS_OF)
    after = {}
    for cid, rec in legs.items():
        rec = {**rec, "desk_write_offs": postings[cid]}
        page = build_account_ledger(rec, AS_OF)["current_balance_gbp"]
        walk = account_events(rec)[-1]["balance_after_gbp"]
        assert abs(page + walk) < 0.005, (cid, page, walk)  # the walk agrees with the page
        after[cid] = page
    return postings, unposted, after


CASES = {
    # desk == page owed across two legs: both close at zero
    "closes": {"E": _leg(30.0, 100.0), "Eg": _leg(70.0, 100.0)},
    # desk below what the page shows: the rest stays owed
    "rest_owed": {"E": _leg(100.0, 60.0)},
    # desk above what the page shows: the excess is not posted, and is counted
    "excess": {"E": _leg(40.0, 55.0)},
    # the engine already wrote off part on the day: the page tops up, never doubles
    "top_up": {"E": _leg(100.0, 100.0, engine=30.0)},
}


def test_every_branch_of_the_split_can_be_taken_and_the_desk_figure_reaches_the_balance():
    out = {k: _post({cid: dict(v) for cid, v in legs.items()}) for k, legs in CASES.items()}
    # The partition: each branch is reached.
    assert out["closes"][2] == {"E": 0.0, "Eg": 0.0}
    assert out["rest_owed"][2] == {"E": 40.0}
    assert out["excess"][2] == {"E": 0.0}
    assert out["excess"][1] == [{"account_id": "ACC-X", "date": DAY, "desk_gbp": 55.0,
                                 "unposted_gbp": 15.0}]
    assert out["top_up"][0]["E"][0]["amount_gbp"] == 70.0 and out["top_up"][2] == {"E": 0.0}
    assert out["top_up"][1] == []  # the engine's 30 is the same event, not a desk excess
    # Largest debit first, each leg up to what it owes.
    assert [p["amount_gbp"] for p in out["closes"][0]["Eg"]] == [70.0]
    # No posting puts an account into credit.
    assert all(v >= 0.0 for k in out for v in out[k][2].values())


def test_a_write_off_after_the_book_is_not_posted():
    late = _leg(100.0, 100.0)
    late["collections_desk_journeys"][0]["stages"][-1]["on"] = "2022-01-01"
    postings, unposted = desk_write_off_postings({"E": late}, AS_OF)
    assert postings == {"E": []} and unposted == []


def test_the_page_does_not_post_a_share_dated_after_the_book():
    rec = {**_leg(100.0, 100.0), "desk_write_offs": [
        {"date": "2022-01-01", "amount_gbp": 100.0, "account_write_off_gbp": 100.0, "rule": "r"}]}
    assert build_account_ledger(rec, AS_OF)["current_balance_gbp"] == 100.0
