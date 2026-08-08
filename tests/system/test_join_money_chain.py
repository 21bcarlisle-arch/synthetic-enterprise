"""JOIN 3 — the money chain: meter read → bill → payment → arrear → recovery or
write-off.

Design: `docs/design/JOIN_TEST_TIER.md`. R15 cut-proofs: `test_join_cut_mutation.py`.

The number that has to survive this chain is an AMOUNT. A read error becomes a
billing error becomes an arrears balance becomes a write-off, and at every seam
the amount must be the SAME amount — that is the only thing distinguishing a
money chain that conducts from five stages that each produce a plausible figure
independently.

REPORT-ONLY first landing — see JOIN_TEST_TIER.md §3.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


def test_the_money_chain_join_conducts():
    """The read error reaches the bill; the bill's amount reaches the arrears
    case; the case resolves to a write-off that reconciles against it."""
    chain = chains.run_money_chain()
    chains.assert_money_join(chain)


def test_the_estimate_is_a_belief_not_a_read_of_the_truth():
    """The wall, stated dynamically at the seam it matters most.

    An estimated read is built from the customer's own trailing ACTUALS — the
    company-observable history — never from this period's true consumption. If
    the estimate tracked the truth, the company would be reading simulation
    internals through the billing path, and every downstream gap would vanish.
    """
    chain = chains.run_money_chain()
    estimate = chain["estimated_event"].estimated_consumption_kwh
    truth = chain["true_consumption_kwh"]
    trailing = (300.0, 320.0, 310.0)
    assert estimate != truth, (
        "the estimated read equals the true consumption — the company is billing from "
        "ground truth it cannot see"
    )
    assert min(trailing) <= estimate <= max(trailing), (
        f"the estimate ({estimate}) is not derived from the observable trailing actuals "
        f"{trailing} — it came from somewhere the company cannot see"
    )


def test_a_paid_bill_opens_no_arrears_case():
    """The opposite direction: the arrears machinery must not fire on a resolved
    account, or 'a failed payment opens a case' is unfalsifiable."""
    chain = chains.run_money_chain()
    from datetime import date, timedelta

    from simulation import arrears_engine

    resolved = arrears_engine.arrears_stages(
        chain["arrears_gbp"],
        date.fromisoformat("2023-03-14") + timedelta(days=14),
        eventually_resolved=True,
        archetype="NEUTRAL",
        method="direct_debit",
    )
    stage_names = [s["stage"] for s in resolved]
    assert "RESOLVED" in stage_names and "WRITTEN_OFF" not in stage_names, (
        f"a resolved arrears case still wrote the debt off — {stage_names}"
    )


def test_no_wall_crossing_in_the_money_chain_participants():
    chains.assert_no_wall_crossing(
        [
            "saas/bill_generator.py",
            "company/billing/invoice.py",
            "company/billing/credit_refund.py",
            "company/billing/arrears_engine.py",
        ]
    )
