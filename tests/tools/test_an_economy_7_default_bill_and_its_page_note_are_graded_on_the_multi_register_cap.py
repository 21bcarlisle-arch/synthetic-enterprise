"""The N19 rows (eighth cold read, 2026-11-04), written blind: a printed Economy 7 default bill's all-in
rate at SLC 28AD.36(a)'s 58/42 sits within the multi-register cap, and a page note that the bill
"breaks a published rule" agrees with that grade.

The defects these tests name:
  * a grade at the household's own Day/Night mix, or against the single-rate cap, which read 626
    Economy 7 bills on the b3ce2a4e73 book as breaches that were at the cap;
  * a bill that runs SVT then fixed graded as if all of it were SVT: the fixed days lift its
    register rates, and the SVT part was at the cap (SYN-2016-592 Dec 2023, SYN-2016-380 Aug 2024);
  * a page note that is printed on a bill within the multi-register cap;
  * a row whose branches cannot all be reached, so it passes by never grading.
"""
from __future__ import annotations

from tests.tools.test_the_domain_invariant_runner_reads_only_the_raw_export_and_every_evaluator_can_fire import (
    _account,
)
from tools import domain_invariant_runner as runner

ROW_A = {"id": "INV_DEFAULT_TARIFF_TWO_REGISTER_INVOICE_WITHIN_MULTI_REGISTER_CAP",
         "tolerance": {"upper_relative": 0.015},
         "rows": [{"from": "2016-01-01", "to": "2018-12-31", "lower": None, "upper": None},
                  {"from": "2019-01-01", "to": "2019-03-31", "lower": None, "upper": 14.63},
                  {"from": "2019-04-01", "to": "2019-09-30", "lower": None, "upper": 16.469},
                  {"from": "2026-01-01", "to": None, "lower": None, "upper": None}]}
ROW_B = {"id": "INV_PAGE_CAP_BREACH_NOTE_AGREES_WITH_THE_MULTI_REGISTER_GRADE",
         "twin_of": ROW_A["id"], "_twin": ROW_A}


def _bill(start, end, day_p, night_p, *, note=0.0, tariff="svt", day_kwh=733.2, night_kwh=278.3,
          non_commodity_p=2.0):
    """A printed Economy 7 bill on SYN-2016-592's Feb 2019 shape: 72% day, the household's own mix."""
    kwh = day_kwh + night_kwh
    regs = [{"label": "Day", "consumption_kwh": day_kwh, "unit_rate_p_per_kwh": day_p,
             "amount_gbp": round(day_kwh * day_p / 100, 2)},
            {"label": "Night", "consumption_kwh": night_kwh, "unit_rate_p_per_kwh": night_p,
             "amount_gbp": round(night_kwh * night_p / 100, 2)}]
    return {"period_start": start, "period_end": end, "commodity": "electricity",
            "term_tariff_type": tariff, "consumption_kwh": kwh, "registers": regs,
            "commodity_amount_gbp": sum(r["amount_gbp"] for r in regs),
            "non_commodity_amount_gbp": round(kwh * non_commodity_p / 100, 2),
            "default_tariff_excess_p_per_kwh": note}


def _book(*bills, year=2019, terms=None):
    acct = _account("E7", "electricity", rate=14.0, year=year, registers=("4", "5"))
    if terms:
        for p in acct["periods"]:
            p["contracted_terms"] = terms
    acct["printed"] = {"invoices": list(bills)}
    return {"E7": acct}


def _grade(book, row=ROW_A):
    return {r["id"]: r for r in runner.run([row], book)}[row["id"]]


# 0.58 x 13.332 + 0.42 x 3.352 + 2.0 = 11.140p: SYN-2016-592's Feb 2019 energy pair, under 14.63.
AT_CAP = ("2019-02-01", "2019-02-28", 13.332, 3.352)


def test_every_outcome_of_the_invoice_grade_can_be_reached():
    acct = runner.Account("E7", _book()["E7"])
    outcomes = {runner._e7_invoice_grade(ROW_A, acct, b)[0] for b in (
        _bill(*AT_CAP),                                                     # WITHIN
        _bill(*AT_CAP, non_commodity_p=5.5),                                # 14.641: tolerance
        _bill("2019-02-01", "2019-02-28", 18.0, 8.0),                       # OVER
        _bill("2019-03-15", "2019-04-14", 18.0, 8.0),                       # straddle, flag only
        _bill("2018-02-01", "2018-02-28", 30.0, 30.0),                      # pre-cap: not graded
    )}
    assert outcomes == {"WITHIN", "WITHIN_TOLERANCE", "OVER", "STRADDLE_FLAG", "NOT_GRADED"}


def test_an_e7_bill_at_its_own_mix_over_the_single_rate_cap_is_within_the_multi_register_one():
    # SYN-2016-592, Feb 2019: 16.09p at its own 72% day mix, over the single-rate 15.723p.
    bill = _bill(*AT_CAP, non_commodity_p=5.5)
    own_mix = (bill["commodity_amount_gbp"] + bill["non_commodity_amount_gbp"]) * 100 / bill["consumption_kwh"]
    assert own_mix > 15.723 * 1.015
    assert _grade(_book(bill))["status"] == "CLEAN"
    over = _grade(_book(_bill("2019-02-01", "2019-02-28", 18.0, 8.0)))
    assert (over["status"], over["breached"]) == ("BREACHED", 1)


def test_a_bill_that_runs_svt_then_fixed_is_not_graded_as_svt():
    terms = [{"tariff_effective_from": "2019-01-01", "tariff_effective_to": "2019-02-14",
              "tariff_type": "svt", "unit_rate_p_per_kwh": 11.0},
             {"tariff_effective_from": "2019-02-14", "tariff_effective_to": "2020-02-14",
              "tariff_type": "fixed", "unit_rate_p_per_kwh": 16.0}]
    mixed = _grade(_book(_bill("2019-02-01", "2019-02-28", 18.0, 8.0), terms=terms))
    assert (mixed["status"], mixed["unbounded"]) == ("UNREACHED", 1)
    assert "1 spans a term change" in mixed["unit"]


def test_the_page_note_breaches_where_the_bill_is_within_and_agrees_where_it_is_over():
    false_note = _grade(_book(_bill(*AT_CAP, note=0.37)), ROW_B)
    assert (false_note["status"], false_note["breached"]) == ("BREACHED", 1)
    r_over = 0.58 * 18.0 + 0.42 * 8.0 + 2.0 - 14.63
    agreeing = _grade(_book(_bill("2019-02-01", "2019-02-28", 18.0, 8.0, note=round(r_over, 4))), ROW_B)
    assert (agreeing["status"], agreeing["checked"]) == ("CLEAN", 1)
    assert "agreeing note 1" in agreeing["unit"]
    silent = _grade(_book(_bill("2019-02-01", "2019-02-28", 18.0, 8.0)), ROW_B)
    assert (silent["status"], silent["flagged"]) == ("FLAGGED", 1)
    pre_cap = _grade(_book(_bill("2018-02-01", "2018-02-28", 13.3, 3.4, note=0.2), year=2018), ROW_B)
    assert (pre_cap["status"], pre_cap["breached"]) == ("BREACHED", 1)
