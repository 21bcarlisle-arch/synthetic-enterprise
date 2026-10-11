"""B11's held-back grade reaches the annual report, rendered from the saved run.

The defect this guards: three slices of the forward-value backtest graded the book and published
only to staging, because `forward_clv.backtest_run_output` had no production caller. The report
section is that caller. The expected figures are computed through the company module's own file
door, not through the section, so a section that renders something other than the backtest's grade
goes red.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from company.analytics.forward_clv import (
    LIMITATION_SWITCH_LEVEL_IS_THE_REGIME,
    backtest_run_output,
    book_from_run_output,
)
from saas.reporting.annual_report import (
    NOT_AVAILABLE,
    _section_held_back_grade,
    generate_annual_report,
)
from tools.run_output_store import as_plain_file, load_run_output, resolve_run_output

SAVED_RUN = Path(__file__).resolve().parents[3] / "docs" / "reports" / "run_output_latest.json"
_TITLE = "## Forward Value on Held-Back History"

pytestmark = pytest.mark.skipif(resolve_run_output(SAVED_RUN) is None,
                                reason="no saved run in this checkout")


@pytest.fixture(scope="module")
def saved_run() -> dict:
    return load_run_output(resolve_run_output(SAVED_RUN))


def _section(report: str) -> str:
    start = report.index(_TITLE)
    end = report.find("\n## ", start + 1)
    return report[start:] if end < 0 else report[start:end]


def test_the_grade_renders_in_the_annual_report_from_the_saved_run(saved_run, tmp_path):
    section = _section(generate_annual_report(saved_run))
    bt = backtest_run_output(as_plain_file(resolve_run_output(SAVED_RUN), tmp_path))
    rk = bt.departure_ranking
    assert f"{bt.accounts_graded} accounts graded" in section
    for rule in ("per_customer", "flat"):
        level, (lo, hi) = bt.departure_calibration[rule]
        assert f"{level:+.3f} [{lo:+.3f}, {hi:+.3f}]" in section
    diff, (lo, hi) = rk.difference
    assert f"| Per-customer minus flat (paired) | {diff:+.3f} [{lo:+.3f}, {hi:+.3f}] |" in section
    assert f"Verdict: {rk.verdict}." in section
    assert LIMITATION_SWITCH_LEVEL_IS_THE_REGIME in section


def test_the_level_splits_by_cause_only_where_the_run_carries_a_register(saved_run):
    """Both branches over one book: without a register the split is refused with its reason, and
    with one naming a held-back departer it renders as two terms."""
    accounts, book_end = book_from_run_output(saved_run)
    cut_end = 2020 * 12 + 11
    leaver = next(a for a in accounts if cut_end < a.last_month < book_end
                  and a.first_month <= cut_end)
    ym = leaver.last_month + 1
    register = [{"household": leaver.account_id,
                 "move_date": f"{ym // 12:04d}-{ym % 12 + 1:02d}-01"}]
    without = _section_held_back_grade({**saved_run, "home_move_outs": None})
    with_register = _section_held_back_grade({**saved_run, "home_move_outs": register})
    assert "cannot be split" in without and "| Move |" not in without
    assert "cannot be split" not in with_register
    assert "| Switch |" in with_register and "| Move |" in with_register


def test_a_run_without_a_monthly_ledger_says_so():
    section = _section_held_back_grade({"years": {"2020": {}}})
    assert NOT_AVAILABLE in section and "per-account monthly ledger" in section


def test_a_book_that_ends_before_the_cut_says_so():
    short = {"years": {"2016": {"per_customer_monthly": {"C1": {"2016-01": {"net_gbp": 1.0}}}}}}
    section = _section_held_back_grade(short)
    assert NOT_AVAILABLE in section and "nothing after the cut" in section
