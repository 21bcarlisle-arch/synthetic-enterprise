"""The company's ledger is billed each month's settled revenue, to the pound.

Defect it names: the run posted the FIRST settlement record of each customer-month as that month's
bill -- one half-hour, a median of GBP 0.023 across a decade -- so every absolute amount the company
reads from its own receivable (the renewal price's stock term on money owed) was near zero.
"""
from __future__ import annotations

import pytest

import background.live_payment_triad as triad_module
from simulation.run_phase2b import main as run_phase2b

#: Past the first renewals, so some months ARE split between two terms of one leg (19 of 850 at
#: this end, 2026-10-03). Before any renewal the split leg below would pass on an empty case.
REPORT_END = "2017-02-28"


@pytest.fixture(scope="module")
def _billed():
    posted: list[tuple[str, str, float]] = []
    real = triad_module.LivePaymentTriad.record_period

    def spy(self, **kw):
        posted.append((kw["customer_id"], kw["due_date"].isoformat()[:7], float(kw["amount_gbp"])))
        return real(self, **kw)

    mp = pytest.MonkeyPatch()
    mp.setattr(triad_module.LivePaymentTriad, "record_period", spy)
    try:
        result = run_phase2b(report_end=REPORT_END)
    finally:
        mp.undo()
    return result, posted


def test_the_ledger_is_billed_the_runs_own_revenue_to_the_pound(_billed):
    result, posted = _billed
    revenue = sum(float(r.get("revenue_gbp") or 0.0) for r in result["all_records"]
                  if isinstance(r, dict))
    assert posted and revenue > 100.0, "the window billed nothing, so this control proves nothing"
    assert sum(a for _, _, a in posted) == pytest.approx(revenue, abs=1.0)


def test_a_customer_is_billed_once_a_month_even_when_a_renewal_splits_it(_billed):
    result, posted = _billed
    terms: dict[tuple, set] = {}
    for r in result["all_records"]:
        if isinstance(r, dict):
            terms.setdefault((r["customer_id"], r["settlement_date"][:7]), set()).add(
                r.get("term_start"))
    assert any(len(t) > 1 for t in terms.values()), "no month in the window is split by a renewal"
    keys = [(c, m) for c, m, _ in posted]
    assert len(keys) == len(set(keys))
