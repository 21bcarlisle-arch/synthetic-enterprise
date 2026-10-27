"""The run sends the SLC 22C end-of-fixed-term statement (22C.4(a): 42-49 days before the end).

The defect: `company/crm/renewal_notice_register.py` implemented the window and nothing in the run
called it, so all 1,338 fixed terms on the 2eeb3f0b3 book breached
`INV_RENEWAL_NOTICE_42_TO_49_DAYS`. Red on that code: the run returned no `renewal_notice_log`.
Text: `docs/domain_artefact_library/regulatory/slc_22c_end_of_fixed_term_statement.md`.

Graded here against the run's own term rows, the company's contract register: every statement is
dated in the window, on a day its term was supplied, once per term.
"""
from __future__ import annotations

from datetime import date

import pytest

from simulation.run_phase2b import main as run_phase2b

WINDOW_END = "2017-12-31"


@pytest.fixture(scope="module")
def run():
    return run_phase2b(report_end=WINDOW_END)


def _fixed_terms(run):
    """(customer_id, fixed_term_end) -> (term_start, supplied_until) for every fixed term row."""
    return {(r["customer_id"], r["fixed_term_end"]): (r["term_start"][:10], r["term_end"][:10])
            for r in run["account_state_log"] if r.get("fixed_term_end")}


def test_both_sides_of_the_owed_partition_are_reached(run):
    """A statement rule that sent nothing, or sent for every term, would pass a one-sided check."""
    terms = _fixed_terms(run)
    sent = {(n["customer_id"], n["fixed_term_end"]) for n in run["renewal_notice_log"]}
    assert sent, "the run sent no SLC 22C statement"
    assert set(terms) - sent, "every fixed term got a statement: none was cut short or ran past the window"


def test_every_statement_is_in_the_window_and_on_a_supplied_day(run):
    terms = _fixed_terms(run)
    for n in run["renewal_notice_log"]:
        start, supplied_until = terms[(n["customer_id"], n["fixed_term_end"])]
        days = (date.fromisoformat(n["fixed_term_end"]) - date.fromisoformat(n["notice_date"])).days
        assert 42 <= days <= 49, n
        assert start <= n["notice_date"] < supplied_until, n


def test_no_term_is_sent_two_statements(run):
    sent = [(n["customer_id"], n["fixed_term_end"]) for n in run["renewal_notice_log"]]
    assert len(sent) == len(set(sent))


# Completeness (every owed term HAS one) is not graded here: a term row is written before the
# household's departure roll at the term's start, so a row can stand for a term never supplied, and
# only the billed book tells the two apart. `INV_RENEWAL_NOTICE_42_TO_49_DAYS` grades it on the
# raw export of a full run (tools/domain_invariant_runner.ev_renewal_notice).
