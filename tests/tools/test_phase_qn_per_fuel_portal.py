"""Tests for the per-fuel customer portal depth (Phase QN, PRIORITIES.md P1
Website Integrity Part B): electricity and gas legs of a dual-fuel account
must appear as separate accounts with their own invoice/payment/arrears
history on the Customers tab, with a combined roll-up as an optional
secondary view -- never the only view."""
from tools.generate_shadow_html import build_customers, _per_fuel_case_study, PER_FUEL_CASE_STUDY_BASE


def _dash(lifetime=None, retention_deferral=None, serial_savers=None):
    return {
        "meta": {"git_commit": "abc1234"},
        "build": {"current_phase": "QN", "test_count": 1, "company_modules": 1},
        "customers": {
            "lifetime": lifetime or {},
            "events": [],
            "retention": [],
            "retention_deferral": retention_deferral or [],
            "serial_savers": serial_savers or [],
        },
    }


def _leg(commodity, segment="resi", net=10.0, gross=20.0):
    return {"segment": segment, "commodity": commodity, "acquisition_date": "2020-01-01", "net_gbp": net, "gross_gbp": gross}


def test_gas_leg_no_longer_skipped_in_all_accounts_table():
    dash = _dash(lifetime={"C1": _leg("electricity"), "C1g": _leg("gas")})
    html = build_customers(dash, {"customers": {}}, "ts")
    assert ">C1<" in html
    assert ">C1g<" in html


def test_combined_rollup_only_for_dual_fuel_customers():
    dash = _dash(lifetime={
        "C1": _leg("electricity", net=10.0), "C1g": _leg("gas", net=5.0),
        "C9": _leg("electricity", net=7.0),
    })
    html = build_customers(dash, {"customers": {}}, "ts")
    assert "Combined Roll-Up" in html
    assert "&pound;15" in html
    combined_section = html.split("Combined Roll-Up")[1].split("Retention Offers")[0]
    assert "C9" not in combined_section


def test_per_fuel_case_study_empty_without_both_legs():
    assert _per_fuel_case_study({"customers": {"C1": {}}}, "C1") == ""
    assert _per_fuel_case_study({}, "C1") == ""


def test_per_fuel_case_study_shows_both_legs_and_divergence():
    ledger = {
        "customers": {
            "C_IC3": {
                "total_billed_gbp": 6645325.4, "total_paid_gbp": 6645325.4, "balance_gbp": 0.0,
                "failed_payment_count": 0, "arrears_case_count": 0,
                "invoices": [{"period_end": "2025-12-31", "commodity": "electricity", "total_amount_gbp": 100.0, "payment_status": "paid"}],
            },
            "C_IC3g": {
                "total_billed_gbp": 2363387.93, "total_paid_gbp": 2273746.89, "balance_gbp": -89641.04,
                "failed_payment_count": 1, "arrears_case_count": 1,
                "invoices": [{"period_end": "2025-12-31", "commodity": "gas", "total_amount_gbp": 200.0, "payment_status": "arrears"}],
            },
        }
    }
    html = _per_fuel_case_study(ledger, "C_IC3")
    assert "C_IC3" in html and "C_IC3g" in html
    assert "89,641" in html
    assert "Divergence" in html


def test_build_customers_includes_per_fuel_case_study_for_default_base():
    lifetime = {
        PER_FUEL_CASE_STUDY_BASE: _leg("electricity", segment="I&C"),
        PER_FUEL_CASE_STUDY_BASE + "g": _leg("gas", segment="I&C"),
    }
    ledger = {
        "customers": {
            PER_FUEL_CASE_STUDY_BASE: {
                "total_billed_gbp": 100.0, "total_paid_gbp": 100.0, "balance_gbp": 0.0,
                "failed_payment_count": 0, "arrears_case_count": 0, "invoices": [],
            },
            PER_FUEL_CASE_STUDY_BASE + "g": {
                "total_billed_gbp": 50.0, "total_paid_gbp": 40.0, "balance_gbp": -10.0,
                "failed_payment_count": 1, "arrears_case_count": 1, "invoices": [],
            },
        }
    }
    dash = _dash(lifetime=lifetime)
    html = build_customers(dash, {"customers": {}}, "ts", ledger)
    assert "Per-Fuel Account Depth" in html
