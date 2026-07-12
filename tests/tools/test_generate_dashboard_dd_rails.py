"""Tests for tools/generate_dashboard_data.py::extract_dd_rails() --
W5_1_banking_payment_rails (2026-07-12, L2->L3 attempt): the wiring + surface
that closed this atom's Expert Hour-flagged decisive gap ("zero live pipeline
callers, cannot live in time")."""
from tools.generate_dashboard_data import extract_dd_rails


def _dd_book(summary=None, mandates=None, attempts=None):
    return {
        "dd_collection_book": {
            "summary": summary or {},
            "mandates": mandates or [],
            "attempts": attempts or [],
        }
    }


def test_missing_dd_collection_book_returns_empty_shape():
    result = extract_dd_rails({})
    assert result["summary"] == {}
    assert result["example_customer"] is None


def test_summary_passed_through():
    data = _dd_book(summary={"total": 3, "active": 2, "suspended": 1, "cancelled": 0, "total_monthly_gbp": 240.0})
    result = extract_dd_rails(data)
    assert result["summary"]["total"] == 3
    assert result["summary"]["total_monthly_gbp"] == 240.0


def test_example_customer_picks_the_one_with_most_observed_attempts():
    data = _dd_book(
        mandates=[
            {"customer_id": "C1", "mandate_reference": "DD-C1", "monthly_amount_gbp": 80.0,
             "setup_confirmed_date": "2020-01-17"},
            {"customer_id": "C2", "mandate_reference": "DD-C2", "monthly_amount_gbp": 60.0,
             "setup_confirmed_date": "2020-02-17"},
        ],
        attempts=[
            {"customer_id": "C1", "mandate_reference": "DD-C1", "attempt_date": "2020-01-31",
             "amount_gbp": 80.0, "outcome": "collected"},
            {"customer_id": "C2", "mandate_reference": "DD-C2", "attempt_date": "2020-02-28",
             "amount_gbp": 60.0, "outcome": "collected"},
            {"customer_id": "C2", "mandate_reference": "DD-C2", "attempt_date": "2020-03-31",
             "amount_gbp": 60.0, "outcome": "failed", "failure_reason": "Refer to Payer"},
        ],
    )
    result = extract_dd_rails(data)
    example = result["example_customer"]
    assert example is not None
    assert example["customer_id"] == "C2"  # more observed attempts than C1
    assert example["monthly_amount_gbp"] == 60.0
    assert len(example["attempts"]) == 2
    assert example["attempts"][0]["attempt_date"] == "2020-02-28"  # sorted chronologically
    assert example["attempts"][1]["outcome"] == "failed"
    assert example["attempts"][1]["failure_reason"] == "Refer to Payer"


def test_example_customer_falls_back_to_first_mandate_when_no_attempts():
    data = _dd_book(mandates=[
        {"customer_id": "C1", "mandate_reference": "DD-C1", "monthly_amount_gbp": 80.0},
    ])
    result = extract_dd_rails(data)
    assert result["example_customer"]["customer_id"] == "C1"
    assert result["example_customer"]["attempts"] == []


def test_no_mandates_gives_none_example():
    result = extract_dd_rails(_dd_book())
    assert result["example_customer"] is None


def test_attempts_capped_at_twelve():
    attempts = [
        {"customer_id": "C1", "attempt_date": f"2020-{m:02d}-28", "amount_gbp": 80.0, "outcome": "collected"}
        for m in range(1, 13)
    ] + [
        {"customer_id": "C1", "attempt_date": "2021-01-28", "amount_gbp": 80.0, "outcome": "collected"},
    ]
    data = _dd_book(
        mandates=[{"customer_id": "C1", "mandate_reference": "DD-C1", "monthly_amount_gbp": 80.0}],
        attempts=attempts,
    )
    result = extract_dd_rails(data)
    assert len(result["example_customer"]["attempts"]) == 12
