"""R15 contract for the two-arm pricing comparison.

WHAT IS GUARDED is not the arithmetic — `tests/company/pricing/test_value_based_renewal.py` owns
that — but the two ways a comparison like this lies: by reporting a verdict its own numbers do
not support, and by quietly covering fewer accounts than it appears to.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from saas.tariff_pricing import TARGET_MARGIN_GBP_PER_MWH
from tools import couple_value_based_pricing as cvp

REPO = Path(__file__).resolve().parents[2]

RUN = {"per_customer_lifetime": {
    "C1": {"segment": "resi", "cost_to_serve_gbp": 330.0},
    "C2": {"segment": "resi", "cost_to_serve_gbp": 120.0},
    "C3": {"segment": "resi", "cost_to_serve_gbp": 90.0},
}}
BOOK = {"customers": [
    {"legs": {"e": {"cid": "C1", "total_kwh": 30000, "avg_rate_gbp_per_mwh": 150.0, "bill_count": 60}}},
    {"legs": {"e": {"cid": "C2", "total_kwh": 9000, "avg_rate_gbp_per_mwh": 140.0, "bill_count": 36}}},
    {"legs": {"e": {"cid": "C3"}}},          # no consumption on record at all
]}


def test_an_account_the_company_cannot_price_is_NAMED_not_dropped():
    """A comparison silently covering two of three accounts is a different claim from one
    covering all three, and the difference is invisible unless it is stated."""
    out = cvp.compare(RUN, BOOK)

    assert out["accounts_priced"] == 2
    assert sum(out["accounts_skipped"].values()) == 1
    assert "no consumption or rate" in " ".join(out["accounts_skipped"])


def test_the_control_is_the_IMPORTED_constant_and_says_what_it_is():
    out = cvp.compare(RUN, BOOK)

    assert out["control"]["margin_gbp_per_mwh"] == TARGET_MARGIN_GBP_PER_MWH
    assert "what this company does today" in out["control"]["what_it_is"]


def test_the_VERDICT_is_derived_from_the_rows_and_not_written_beside_them():
    """A verdict a reader has to check against the table is a verdict that will be quoted without
    checking. The invariant: if the arm's choice sat at the edge of what it was allowed on ANY
    account, the comparison is not fit to run — because on that account the ceiling decided, not
    the customer.

    MUTATION (must fire): return `fit_to_run: True` unconditionally.
    """
    out = cvp.compare(RUN, BOOK)
    at_edge = sum(1 for r in out["accounts"] if r["endpoint_bound"])

    if at_edge:
        assert out["verdict"]["fit_to_run"] is False
        assert "not a decision, it is a ceiling" in out["verdict"]["why"]
    else:
        assert isinstance(out["verdict"]["fit_to_run"], bool)


def test_a_book_the_arm_can_actually_decide_on_reports_FIT(monkeypatch):
    """THE NULL, and without it "not fit to run" is also satisfied by a verdict hard-coded to
    refuse. Blind the search to an interior winner and the verdict must turn."""
    from company.pricing import value_based_renewal as vbr

    interior = {2.0: 5.0, 3.0: 50.0, 5.0: 5.0}

    def _fake(*, arm, customer_id, **kw):
        best = max(interior, key=interior.get)
        margin = TARGET_MARGIN_GBP_PER_MWH if arm == vbr.FLAT_RULES else best
        return vbr.MarginDecision(
            customer_id=customer_id, arm=arm, margin_gbp_per_mwh=margin,
            expected_value_gbp=interior[margin], p_retain=0.9, expected_periods=3.0,
            cost_to_serve_gbp_per_year=50.0, eac_mwh=3.1,
            considered=tuple(interior.items()), endpoint_bound=False,
        )

    monkeypatch.setattr(cvp, "decide_margin", _fake)
    out = cvp.compare(RUN, BOOK)

    assert out["verdict"]["fit_to_run"] is True
    assert "interior optima" in out["verdict"]["why"]


def test_an_EMPTY_book_is_a_comparison_that_did_not_run_not_one_that_found_nothing():
    out = cvp.compare({"per_customer_lifetime": {}}, {"customers": []})

    assert out["verdict"]["fit_to_run"] is False
    assert "nothing was compared" in out["verdict"]["why"]


@pytest.mark.skipif(not (REPO / "site" / "data" / "customers.json").is_file(),
                    reason="no published book in this tree")
def test_the_LIVE_book_reports_a_verdict_consistent_with_its_own_rows(tmp_path):
    """R11 to the value that will be quoted. Deliberately does NOT pin `fit_to_run: False` — a
    future fix to the churn model should turn it True and must not have to edit a test to do so.
    What is pinned is that the verdict follows the rows, so it cannot be made True by writing
    True."""
    # Written to tmp_path, not to the real artefact: a test that regenerates a published
    # diagnostic makes the suite a producer, and the next reader cannot tell a measurement from
    # a test run.
    data = cvp.generate(tmp_path / "arms.json")
    at_edge = sum(1 for r in data["accounts"] if r["endpoint_bound"])

    assert data["accounts_priced"] > 0
    assert data["verdict"]["fit_to_run"] == (at_edge == 0
                                             and data["median_implied_bill_change_pct"] < 25.0)
