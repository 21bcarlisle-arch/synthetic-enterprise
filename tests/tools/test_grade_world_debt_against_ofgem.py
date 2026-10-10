"""The arrears like-for-like counts what Ofgem counts, over the denominator Ofgem uses, and can grade
either way.

Each test names the defect it reds on. The run-scale reproduction (50/1153 = 4.3% on the
400-founder capture) is recorded in docs/market_research/debt_and_collections.md §7; the capture
itself is not tracked.
"""
from datetime import date, timedelta
from types import SimpleNamespace

from tools.grade_world_debt_against_ofgem import (
    OFGEM_ARREARS_PLUS_DEBT_2019,
    grade,
    quarter_reading,
    spells_from_records,
)

Q4 = date(2019, 12, 31)
ALL_2019 = ["2019-03", "2019-06", "2019-09", "2019-12"]


def _rec(account, due, result, days_late=0, settled_on=None, method="direct_debit"):
    return SimpleNamespace(account_id=account, due_date=due, result=result, days_late=days_late,
                           settled_on=settled_on, payment_method=method)


def _book(n_accounts, n_behind, method="direct_debit"):
    """n_accounts electricity accounts billed every quarter-end month of 2019; the first n_behind
    hold a bill from 2018 that is never settled."""
    raw = {}
    for i in range(n_accounts):
        spells = [["2018-06-01", None]] if i < n_behind else []
        raw[f"ACC-{i}"] = {"months": list(ALL_2019), "method": method, "spells": spells}
    return raw


def test_a_bill_paid_inside_91_days_is_never_counted_and_one_paid_after_is():
    """Reds if the capture admits a bill paid inside 91 days into the unpaid spells."""
    due = Q4 - timedelta(days=200)
    recs = [_rec("ACC-early", due, "success", days_late=90),
            _rec("ACC-late", due, "success", days_late=250),
            _rec("ACC-early", Q4, "success"), _rec("ACC-late", Q4, "success")]
    raw = spells_from_records(recs)
    assert raw["ACC-early"]["spells"] == []
    behind, active = quarter_reading(raw, Q4)
    assert behind == ["ACC-late"] and sorted(active) == ["ACC-early", "ACC-late"]


def test_the_91_day_line_is_at_due_plus_91_and_a_settled_bill_leaves_the_stock():
    """Reds if the age line or the settled-on exit moves."""
    at = Q4 - timedelta(days=91)
    raw = {"ACC-at": {"months": ["2019-12"], "method": "card", "spells": [[at.isoformat(), None]]},
           "ACC-in": {"months": ["2019-12"], "method": "card",
                      "spells": [[(at + timedelta(days=1)).isoformat(), None]]},
           "ACC-cured": {"months": ["2019-12"], "method": "card",
                         "spells": [["2019-01-01", "2019-12-01"]]}}
    behind, _ = quarter_reading(raw, Q4)
    assert behind == ["ACC-at"]


def test_the_denominator_is_every_billed_account_not_only_the_ones_that_ever_failed():
    """Reds if the matched denominator is dropped: 5 behind of 100 is 5%, not 5 of 5."""
    g = grade([_book(100, 5)])
    assert (g["behind"], g["accounts"]) == (20, 400)
    assert g["share"] == 0.05


def test_gas_accounts_are_split_off_on_the_g_suffix():
    raw = _book(10, 0)
    raw["ACC-0g"] = {"months": list(ALL_2019), "method": "prepayment", "spells": [["2018-01-01", None]]}
    assert grade([raw])["behind"] == 0
    assert grade([raw], fuel="gas")["behind"] == 4


def test_met_high_and_low_are_each_reachable_and_seeds_pool():
    """The partition: a grader that always says MET (or never does) reds here."""
    verdicts = {grade([_book(1000, k)])["verdict"] for k in (10, 51, 150)}
    assert verdicts == {"NOT MET, LOW", "MET", "NOT MET, HIGH"}
    # two seeds pool counts, not shares: 51/1000 and 151/1000 is 202/2000, not the mean of verdicts.
    pooled = grade([_book(1000, 51), _book(1000, 151)])
    assert (pooled["behind"], pooled["accounts"]) == (808, 8000)
    assert pooled["verdict"] == "NOT MET, HIGH"
    assert grade([_book(1000, 51)])["wilson"][0] <= OFGEM_ARREARS_PLUS_DEBT_2019


def test_the_prepayment_share_of_the_accounts_behind_is_reported():
    raw = _book(100, 4)
    raw["ACC-0"]["method"] = "prepayment"
    g = grade([raw])
    assert g["prepayment_behind"] == 4 and g["prepayment_share_of_behind"] == 0.25
