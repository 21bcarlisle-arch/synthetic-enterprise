"""The pre-registered grade of the ending-term belief must be able to grade a book, not only refuse.

THE DEFECT IT GUARDS (2026-11-22). The standing book dropped `desk_belief_log`, and its rows never
said which term a renewal ended unless the switch was on, so no published book could grade the
switch. A grader that refuses every book passes every refusal test, so the first leg here is the
one that must return a grade.

THE NAMED MUTATIONS. Drop `ending_term_type` from the run's desk_belief_log row and the source leg
fires. Read the same year's rows into the multiplier (`<=` for `<` in the ledger) and the online leg
fires: the book's first year has no earlier rows, so its beliefs must come out unconditioned.
"""
import ast
from pathlib import Path

from tools.grade_ending_term_belief_on_a_book import (
    MIN_LEAVERS,
    MIN_STATES,
    _ledger,
    grade,
    online_conditioned_beliefs,
)


def _book():
    log, events = [], []
    for year in range(2016, 2025):
        for i in range(40):
            acct = f"C{year}_{i}"
            fixed = i % 2 == 0
            leaves = fixed and i % 4 == 0  # a quarter of the fix-ends leave, no default roll does
            # the live belief is backwards: higher on default rolls than on fix-ends
            log.append({"account_id": acct, "term_start": f"{year}-03-01", "fuel": "electricity",
                        "desk_churn_belief": 0.2 if fixed else 0.4, "desk_asked": True,
                        "left": leaves, "ending_term_type": "fixed" if fixed else "default"})
            if leaves:
                events.append({"customer_id": acct, "event_date": f"{year}-03-01",
                               "event_type": "churned"})
    return {"desk_belief_log": log, "customer_events": events}


def test_a_qualifying_book_is_graded_and_the_switch_outranks_a_backwards_belief():
    out = grade(_book())
    assert "refused" not in out, out
    assert out["states"] >= MIN_STATES and out["leavers"] >= MIN_LEAVERS
    assert out["auc_live"] < 0.5 < out["auc_conditioned"]
    assert out["paired_95"][0] > 0
    assert out["multiplier_for_2019"]["default"] < 1 < out["multiplier_for_2019"]["fixed"]


def test_a_book_without_the_log_or_the_type_is_refused_by_name():
    assert "no desk_belief_log" in grade({"customer_events": []})["refused"]
    book = _book()
    for r in book["desk_belief_log"]:
        del r["ending_term_type"]
    assert "no ending_term_type" in grade(book)["refused"]


def test_the_run_writes_the_ending_term_type_on_every_desk_row():
    src = Path("simulation/run_phase2b.py").read_text()
    appends = [n for n in ast.walk(ast.parse(src))
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and n.func.attr == "append" and isinstance(n.func.value, ast.Name)
               and n.func.value.id == "desk_belief_log"]
    assert appends, "desk_belief_log is no longer appended in run_phase2b"
    for call in appends:
        keys = {k.value for k in call.args[0].keys if isinstance(k, ast.Constant)}
        assert "ending_term_type" in keys, "a desk_belief_log row no longer says which term it ended"


def test_a_row_is_conditioned_only_on_years_before_its_own():
    rows = [r for r in _book()["desk_belief_log"]]
    cond = online_conditioned_beliefs(rows, _ledger(rows))
    first = [(r["desk_churn_belief"], c) for r, c in zip(rows, cond) if r["term_start"] < "2017"]
    later = [(r["desk_churn_belief"], c) for r, c in zip(rows, cond) if r["term_start"] >= "2017"]
    assert first and all(c == live for live, c in first), "the first year read its own outcomes"
    assert any(c != live for live, c in later), "no later row was conditioned at all"
