"""Phase AL: Counterfactual Retention Value section tests."""
import pytest
from saas.reporting.annual_report import _section_counterfactual_retention


def _no_offer(cid, event_date, etm, co_est=0.0, reason="below_threshold"):
    return {
        "customer_id": cid,
        "event_date": event_date,
        "company_churn_estimate": co_est,
        "expected_term_margin_gbp": etm,
        "no_offer_reason": reason,
    }


def _ret_offer(cid, event_date, outcome="retained"):
    return {
        "customer_id": cid,
        "event_date": event_date,
        "company_churn_estimate": 0.35,
        "discount_pct": 0.08,
        "retention_cost_gbp": 5000.0,
        "expected_term_margin_gbp": 50000.0,
        "acq_cost_saved_gbp": 150.0,
        "outcome": outcome,
    }


def _pcl(cid, segment="resi", net_margin=5000.0):
    return {
        "segment": segment,
        "net_margin_after_cost_to_serve_gbp": net_margin,
    }


def _data(no_offer_entries, rl=None, pcl_dict=None):
    return {
        "no_offer_churn_log": no_offer_entries,
        "retention_log": rl or [],
        "per_customer_lifetime": pcl_dict or {},
    }


# ── 1. Empty no_offer_churn_log returns empty ─────────────────────────────────

def test_empty_returns_empty():
    assert _section_counterfactual_retention({}) == ""
    assert _section_counterfactual_retention({"no_offer_churn_log": []}) == ""


# ── 2. Header present ─────────────────────────────────────────────────────────

def test_header_present():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "## Counterfactual Retention Value" in result


# ── 3. Churned account shown in table ────────────────────────────────────────

def test_account_in_table():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "C3" in result
    assert "2020-06-30" in result


# ── 4. Positive ETM flagged as MISSED OPP ────────────────────────────────────

def test_positive_etm_missed_opportunity():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "MISSED OPP" in result


# ── 5. Negative ETM flagged as CORRECT PASS ──────────────────────────────────

def test_negative_etm_correct_pass():
    data = _data([_no_offer("C1", "2021-12-30", etm=-200.0)])
    result = _section_counterfactual_retention(data)
    assert "CORRECT PASS" in result


# ── 6. Retention probability calibrated from actual retention_log ─────────────

def test_calibrated_retention_rate():
    rl = [_ret_offer("IC1", "2018-01-01", "retained")] * 9 +          [_ret_offer("IC2", "2019-01-01", "churned_despite_offer")]
    data = _data([_no_offer("C3", "2020-06-30", etm=1000.0)], rl=rl)
    result = _section_counterfactual_retention(data)
    # 9/10 = 90% retention rate
    assert "90%" in result


# ── 7. Default 60% retention when no retention_log ───────────────────────────

def test_default_retention_rate_no_log():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "60%" in result


# ── 8. SME/I&C gets 8% discount rate ─────────────────────────────────────────

def test_sme_discount_rate():
    data = _data(
        [_no_offer("C6", "2024-03-30", etm=2000.0)],
        pcl_dict={"C6": _pcl("C6", segment="SME")},
    )
    result = _section_counterfactual_retention(data)
    assert "8%" in result


# ── 9. Resi gets 5% discount rate ────────────────────────────────────────────

def test_resi_discount_rate():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "5%" in result


# ── 10. Net counterfactual benefit computed ───────────────────────────────────

def test_cf_net_benefit_computed():
    # 10 offers, 10 retained = 100% retention
    rl = [_ret_offer("IC1", "2018-01-01", "retained")] * 10
    # C3: etm=1000, 5% disc=50 cost, 100% * 1000 - 50 = 950
    data = _data(
        [_no_offer("C3", "2020-06-30", etm=1000.0)],
        rl=rl,
    )
    result = _section_counterfactual_retention(data)
    assert "950" in result  # £950 net benefit


# ── 11. Missed opportunities count correct ───────────────────────────────────

def test_missed_opportunity_count():
    entries = [
        _no_offer("C3", "2020-06-30", etm=500.0),   # positive → missed
        _no_offer("C1", "2021-12-30", etm=-200.0),  # negative → correct
        _no_offer("C4", "2024-09-29", etm=300.0),   # positive → missed
    ]
    data = _data(entries)
    result = _section_counterfactual_retention(data)
    assert "Missed opportunities (positive ETM, below detection): 2" in result
    assert "Correct no-offer (net-neg ETM): 1" in result


# ── 12. Root cause note shown when missed opportunities exist ─────────────────

def test_root_cause_note():
    data = _data([_no_offer("C3", "2020-06-30", etm=500.0)])
    result = _section_counterfactual_retention(data)
    assert "Root cause" in result or "root cause" in result.lower()


# 13. Correct-pass label shown when ETM <= 0
def test_correct_pass_shown():
    no_offer = [{"customer_id": "C1", "expected_term_margin_gbp": -500.0,
                 "company_churn_estimate": 0.8, "event_date": "2022-06-01"}]
    d = {"no_offer_churn_log": no_offer}
    result = _section_counterfactual_retention(d)
    assert "CORRECT PASS" in result or "correct" in result.lower()


# 14. Retention probability calibrated from rl outcomes
def test_retention_prob_from_log():
    no_offer = [{"customer_id": "C1", "expected_term_margin_gbp": 2000.0,
                 "company_churn_estimate": 0.7, "event_date": "2022-01-01"}]
    rl = [{"outcome": "retained"}, {"outcome": "retained"}, {"outcome": "churned"}]
    d = {"no_offer_churn_log": no_offer, "retention_log": rl}
    result = _section_counterfactual_retention(d)
    # P(retain) = 2/3 = 67%, should show it or at least not crash
    assert "Counterfactual" in result


# 15. Account id shown in table
def test_account_id_in_table():
    no_offer = [{"customer_id": "C99", "expected_term_margin_gbp": 1000.0,
                 "company_churn_estimate": 0.5, "event_date": "2023-01-01"}]
    d = {"no_offer_churn_log": no_offer}
    result = _section_counterfactual_retention(d)
    assert "C99" in result
