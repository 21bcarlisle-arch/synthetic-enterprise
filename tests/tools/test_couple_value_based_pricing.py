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


# --------------------------------------------------------------------------- #
# The coupled-triad measurement: belief against truth, at the chosen price     #
# --------------------------------------------------------------------------- #

def test_the_gap_is_measured_at_the_price_the_ARM_ACTUALLY_CHOOSES():
    """The whole point of measuring it here rather than at a renewal that happened. The thesis is
    that advantage comes from prediction, so the number that matters is how wrong the company is
    AT THE PRICE ITS OWN DECISION PICKS -- not at the price it happened to charge last year."""
    scored = cvp.belief_versus_truth(offered_rate=200.0, current_rate=150.0, tenure_years=4.0,
                                     eac_kwh=3100, segment="resi", term_start="2025-01-01")

    assert scored is not None
    assert set(scored) >= {"price_differential_vs_svt", "company_believes_p_leave",
                           "world_would_p_leave", "belief_error_pp"}


def test_an_UNKNOWN_market_position_is_NOT_scored_as_a_perfect_prediction():
    """R15 fail-silent, in the direction that would flatter the company most: an unscoreable
    account returning a zero error would report perfect foresight, and the summary averages it."""
    assert cvp.belief_versus_truth(offered_rate=200.0, current_rate=150.0, tenure_years=4.0,
                                   eac_kwh=3100, segment="resi", term_start="1990-01-01") is None


def test_the_SIGN_of_the_error_is_reported_and_not_just_its_size():
    """A company that expects FEWER departures than it will get is a company that will over-price
    and be punished; one that expects more will leave money on the table. A mean absolute error
    hides which failure this is, and they are not the same failure.

    MUTATION (must fire): summarise with abs() and drop `underestimating_departures`."""
    rows = [{"belief_vs_truth": {"belief_error_pp": -12.0}},
            {"belief_vs_truth": {"belief_error_pp": -4.0}},
            {"belief_vs_truth": {"belief_error_pp": 9.0}}]

    summary = cvp._belief_summary(rows)

    assert summary["underestimating_departures"] == 2
    assert summary["median_belief_error_pp"] == -4.0


def test_a_book_that_cannot_be_scored_says_so_rather_than_reporting_no_gap():
    summary = cvp._belief_summary([{"belief_vs_truth": None}])

    assert summary["available"] is False and "no account" in summary["why"]


# ---------------------------------------------------------------------------
# Is the control a credible average player? (2026-08-25)
# ---------------------------------------------------------------------------

def test_the_average_player_comparator_reads_the_PUBLISHED_allowance():
    """The director's frame makes the baseline the entire meaning of "it performed well", and
    until now nothing in the tree could say whether this company's flat GBP 2.00/MWh was anywhere
    near average behaviour. Ofgem's Default Tariff Cap publishes the regulator's own answer.

    MUTATION (must fire): invent an average-player margin here instead of reading the company's
    reading of the published allowance.
    """
    from tools import couple_value_based_pricing as cvp

    row = cvp._average_player(annual_revenue_gbp=1000.0, eac_kwh=3100.0)

    assert row["available"] is True
    assert row["low"] < row["high"], (
        "a single-fuel answer must stay a RANGE -- no single-fuel split of the fixed component "
        "is published, and collapsing it to a point invents one"
    )


def test_an_account_with_no_bill_reports_UNAVAILABLE_not_zero():
    """A silent zero would make an average supplier look like one earning nothing, which makes
    the control trivially easy to beat -- the exact misreading the comparator exists to end."""
    from tools import couple_value_based_pricing as cvp

    assert cvp._average_player(annual_revenue_gbp=0.0, eac_kwh=3100.0)["available"] is False
    assert cvp._average_player(annual_revenue_gbp=1000.0, eac_kwh=0.0)["available"] is False


def test_the_verdict_ANSWERS_the_control_question_instead_of_leaving_it_open():
    """WHAT THIS CHANGED, and it went against the convenient answer.

    The verdict used to end "what that leaves open is whether the flat control is a credible
    average player", which is a question a reader cannot answer either -- and it is the answer a
    value arm would most like to be true, because "the control was a straw man" excuses the arm.
    Measured, the control IS under-priced and NOWHERE NEAR enough to be the cause.

    MUTATION (must fire): drop `_control_clause` from the verdict and the open question returns.
    """
    from tools import couple_value_based_pricing as cvp

    average = {"available": True, "median_gbp_per_mwh_low": 3.73,
               "median_gbp_per_mwh_high": 8.54, "this_companys_flat_rule_gbp_per_mwh": 2.0}
    rows = [{"value_margin_gbp_per_mwh": 130.0}] * 3

    clause = cvp._control_clause(average, rows)

    assert "under-priced" in clause
    assert "not nearly enough to be the cause" in clause
    assert "straw man" in clause


def test_the_control_clause_says_so_when_the_control_IS_the_cause():
    """The clause has to be able to reach the other verdict, or it is a sentence rather than a
    reading. If the arm's own choice sat inside the regulated range, repricing the control WOULD
    be the whole story."""
    from tools import couple_value_based_pricing as cvp

    average = {"available": True, "median_gbp_per_mwh_low": 3.73,
               "median_gbp_per_mwh_high": 8.54, "this_companys_flat_rule_gbp_per_mwh": 2.0}
    near = cvp._control_clause(average, [{"value_margin_gbp_per_mwh": 6.0}])
    far = cvp._control_clause(average, [{"value_margin_gbp_per_mwh": 130.0}])

    assert "1x the TOP" in near or "0x the TOP" in near, near
    assert "15x the TOP" in far, far


def test_an_UNSCORABLE_average_leaves_the_cause_open_rather_than_asserting_one():
    from tools import couple_value_based_pricing as cvp

    clause = cvp._control_clause({"available": False}, [])

    assert "could not be scored" in clause and "stays open" in clause


def test_the_price_belief_gap_is_scored_against_NO_SKILL_not_against_zero():
    """THE GAP IS THE SCORE, and this is the one that speaks in the thesis's own terms.

    The belief-vs-truth summary reports a median error in percentage points, which says how
    BIASED the company is and nothing about whether its belief carries any INFORMATION. The
    no-skill baseline here is a supplier predicting the same departure probability for every
    account -- the population mean -- which is precisely the director's "flat rules with no
    per-customer view". A gap at or above 1.0 means the per-customer belief is no better than
    that, and no inference advantage can be claimed from it.

    MUTATION (must fire): normalise against zero error, or against the company's own mean, which
    would make the gap unbeatable-by-construction (R15 tautology).
    """
    from tools import couple_value_based_pricing as cvp

    # A company whose belief is EXACTLY the population mean scores 1.0 by construction: it has
    # reproduced the flat rule and nothing more.
    flat = [{"belief_vs_truth": {"company_believes_p_leave": 0.2, "world_would_p_leave": w}}
            for w in (0.1, 0.2, 0.3)]

    assert cvp.price_belief_gap(flat).gap == pytest.approx(1.0)

    # A company that knows each account exactly beats it.
    perfect = [{"belief_vs_truth": {"company_believes_p_leave": w, "world_would_p_leave": w}}
               for w in (0.1, 0.2, 0.3)]

    assert cvp.price_belief_gap(perfect).gap == pytest.approx(0.0)

    # And one that is anti-informative loses to it, which must be expressible.
    inverted = [{"belief_vs_truth": {"company_believes_p_leave": 1.0 - w, "world_would_p_leave": w}}
                for w in (0.05, 0.2, 0.6)]

    assert cvp.price_belief_gap(inverted).gap > 1.0


def test_a_gap_needs_TWO_accounts_before_it_means_anything():
    """One account has no population to be a mean of, so the no-skill baseline is zero error by
    construction and the gap would be undefined or infinite. Reported as not-measurable rather
    than as a number."""
    from tools import couple_value_based_pricing as cvp

    assert cvp.price_belief_gap([]) is None
    assert cvp.price_belief_gap(
        [{"belief_vs_truth": {"company_believes_p_leave": 0.2, "world_would_p_leave": 0.1}}]) is None


def test_the_ledger_write_is_OPT_IN_so_a_read_only_run_cannot_move_the_record():
    """`--write-ledger`, exactly as its sibling `tools/couple_pb3_book_growth.py` has it. A
    measurement tool that writes the public record on every run makes the record a function of
    how often someone ran it."""
    from pathlib import Path

    source = Path(
        __file__).resolve().parents[2].joinpath("tools/couple_value_based_pricing.py").read_text()

    assert "--write-ledger" in source
    assert "if _args.write_ledger:" in source


def test_the_ledger_write_REFUSES_a_pair_the_map_does_not_declare():
    """MIS-SUBJECTION, ONE STEP EARLIER. `tools/couple_clv.py` records what happens when a ledger
    row's key and its actual subject come apart: a row keyed `EP1_clv_three_horizon` graded a
    different module's belief entirely and stayed bit-identical when its named subject's whole
    published output was deleted. It named that shape MIS-SUBJECTED.

    A row keyed on a pair the MAP does not declare is the same defect one step earlier: the pair
    would be this tool's invention, published where a reader takes it for the map's own record.
    `B10_competitor_switching_response` has no twin declared today, so the write refuses and says
    what would make it legal.

    MUTATION (must fire): write the row regardless of what the map says.
    """
    from tools import couple_value_based_pricing as cvp

    declared, why = cvp.coupling_is_declared()

    assert isinstance(declared, bool) and why
    if not declared:
        assert "does not declare" in why or "unverified" in why
        assert "Declare the twin on the map first" in why or "unverified" in why


def test_the_refusal_is_reachable_from_the_write_path():
    """A refusal nobody consults is a comment. The `--write-ledger` branch must ASK before it
    writes, not after."""
    from pathlib import Path

    source = Path(
        __file__).resolve().parents[2].joinpath("tools/couple_value_based_pricing.py").read_text()
    tail = source[source.index("if __name__ ==") :]

    assert "coupling_is_declared()" in tail
    assert tail.index("coupling_is_declared()") < tail.index("write_gap_entry(")
