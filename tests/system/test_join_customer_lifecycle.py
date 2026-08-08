"""JOIN 5 — the customer lifecycle: join → bill → serve → leave.

Design: `docs/design/JOIN_TEST_TIER.md`. R15 cut-proofs: `test_join_cut_mutation.py`.

Asserts arrival and departure carry their real consequences — including debt at
departure. A lifecycle whose ends are not bound by the join and leave dates
settles a customer it never had, or keeps settling one that left; a lifecycle
that drops the closing balance deletes real money at the moment it is hardest to
notice.

REPORT-ONLY first landing — see JOIN_TEST_TIER.md §3.
"""

import pytest

from tests.system import chains

pytestmark = pytest.mark.join_report_only


def test_the_customer_lifecycle_join_conducts():
    """Join and leave dates bound settlement exactly, and debt survives the exit."""
    chain = chains.run_lifecycle_chain()
    chains.assert_lifecycle_join(chain)


def test_a_customer_is_not_served_before_they_join():
    """The window's opening bound, on its own. The window deliberately opens
    before the acquisition date, so a chain that ignores the bound bills days the
    customer was never a customer for."""
    chain = chains.run_lifecycle_chain(join_offset_days=10)
    before_join = [d for d in chain["settled_dates"] if d < chain["join_date"]]
    assert before_join == [], (
        f"settled {len(before_join)} days before the customer joined: {before_join[:3]}"
    )


def test_moving_the_join_date_moves_the_bill():
    """The bound is a live function of the date, not a constant. A later join
    must produce strictly fewer served days and a strictly smaller bill."""
    early = chains.run_lifecycle_chain(join_offset_days=5, leave_offset_days=30)
    late = chains.run_lifecycle_chain(join_offset_days=20, leave_offset_days=30)
    assert len(late["settled_dates"]) < len(early["settled_dates"]), (
        "a 15-day-later join served the same number of days — the acquisition date is "
        "not reaching settlement"
    )
    assert late["closing_balance_gbp"] < early["closing_balance_gbp"], (
        f"a shorter tenure produced no smaller closing balance "
        f"(GBP{late['closing_balance_gbp']:.2f} vs GBP{early['closing_balance_gbp']:.2f})"
    )


def test_debt_at_departure_is_carried_not_deleted():
    """Change of tenancy is where debt quietly disappears in a real supplier's
    books. Assert the closing balance leaves the relationship as a live arrears
    case carrying its own amount."""
    chain = chains.run_lifecycle_chain()
    assert chain["closing_balance_gbp"] > 0
    notes = " ".join(s["note"] for s in chain["final_stages"])
    assert ("%.2f" % chain["closing_balance_gbp"]) in notes, (
        "the departing customer's balance is not stated anywhere in the arrears case "
        "raised at departure"
    )


def test_no_wall_crossing_in_the_lifecycle_participants():
    chains.assert_no_wall_crossing(
        ["company/crm/churn_model.py", "company/crm/enriched_churn_estimate.py"]
    )
