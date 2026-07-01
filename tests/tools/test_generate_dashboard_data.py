"""Tests for tools/generate_dashboard_data.py pure extraction helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_dashboard_data import _fmt, extract_portfolio, extract_financial


def test_fmt_rounds_float():
    assert _fmt(3.14159) == 3.14


def test_fmt_none_returns_zero():
    assert _fmt(None) == 0.0


def test_fmt_integer():
    assert _fmt(100) == 100.0


def _portfolio_data(**overrides):
    base = {
        "_ledger_headline": {"net_margin_gbp": 500_000.0, "gross_margin_gbp": 600_000.0},
        "total_net_gbp": 480_000.0,
        "total_gross_gbp": 590_000.0,
        "enterprise_value_gbp": 1_000_000.0,
        "starting_treasury_gbp": 200_000.0,
        "final_treasury_gbp": 300_000.0,
        "bills_total": 1500,
        "committee_wake_ups_total": 5,
        "retention_log": [{"outcome": "retained"}, {"outcome": "churned"}],
        "churned_billing_accounts": ["C5", "C6"],
    }
    base.update(overrides)
    return base


def test_extract_portfolio_keys():
    r = extract_portfolio(_portfolio_data())
    for key in ("net_margin_gbp", "gross_margin_gbp", "enterprise_value_gbp",
                "treasury_start_gbp", "treasury_end_gbp", "bills_total",
                "committee_interventions_total", "retention_offers", "retention_retained",
                "churn_count"):
        assert key in r


def test_extract_portfolio_uses_total_net_over_ledger():
    r = extract_portfolio(_portfolio_data())
    assert r["net_margin_gbp"] == 480_000.0


def test_extract_portfolio_retention_retained():
    r = extract_portfolio(_portfolio_data())
    assert r["retention_retained"] == 1


def test_extract_portfolio_churn_count():
    r = extract_portfolio(_portfolio_data())
    assert r["churn_count"] == 2


def _financial_data():
    return {
        "years": {
            "2022": {
                "revenue_gbp": 1_000_000.0,
                "gross_gbp": 200_000.0,
                "capital_gbp": 50_000.0,
                "net_gbp": 150_000.0,
                "treasury_end_gbp": 300_000.0,
                "policy_cost_gbp": 30_000.0,
                "bad_debt_gbp": 5_000.0,
                "bills_count": 100,
                "avg_bill_shock_pct": 5.2,
                "commodity_split": {
                    "electricity": {"gross_gbp": 120_000.0, "net_gbp": 90_000.0},
                    "gas": {"gross_gbp": 80_000.0, "net_gbp": 60_000.0},
                },
                "segment_split": {},
            }
        },
        "ledger_pnl": {},
    }


def test_extract_financial_annual_length():
    r = extract_financial(_financial_data())
    assert len(r["annual"]) == 1


def test_extract_financial_year_value():
    r = extract_financial(_financial_data())
    assert r["annual"][0]["year"] == 2022


def test_extract_financial_annual_keys():
    r = extract_financial(_financial_data())
    row = r["annual"][0]
    for key in ("year", "revenue_gbp", "gross_gbp", "net_gbp", "treasury_end_gbp",
                "bills_count", "elec_gross_gbp", "gas_net_gbp"):
        assert key in row


def test_extract_financial_empty_years():
    r = extract_financial({"years": {}, "ledger_pnl": {}})
    assert r["annual"] == []
