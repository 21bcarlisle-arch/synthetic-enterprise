"""The switching-GSOP door owes regs 6ZA and 6ZB on the gainer's own records, and hands back
only plain dicts. Each test names the defect it catches."""
from __future__ import annotations

import json

import company.interfaces.switching_gsop as door
from company.interfaces.switching_gsop import switching_payments_on_gains


def _gain(info, confirmed, agreed=None, contract=None):
    return {"customer_id": "C1", "information_received_on": info,
            "contract_on": contract or info, "registration_confirmed_on": confirmed,
            "erroneous_transfer_agreed_on": agreed}


def test_every_branch_can_be_taken_and_every_refusal_is_reachable():
    """Defect: a door that never owes (or always owes) passes every one-sided test."""
    late_2021 = switching_payments_on_gains([_gain("2021-03-01", "2021-04-01")])
    on_time = switching_payments_on_gains([_gain("2021-03-01", "2021-03-01")])
    et_in_force = switching_payments_on_gains([_gain("2021-03-01", "2021-03-01", "2021-03-29")])
    et_before_6zb = switching_payments_on_gains([_gain("2019-03-01", "2019-03-01", "2019-03-29")])
    late_before_6za = switching_payments_on_gains([_gain("2019-03-01", "2019-06-01")])
    assert late_2021 and et_in_force and not on_time and not et_before_6zb and not late_before_6za
    assert [a["regulation"] for a in late_2021] == ["6ZA"]
    assert [a["regulation"] for a in et_in_force] == ["6ZB"]


def test_6zb_fails_on_the_agreement_day_and_pays_within_ten_working_days():
    """Defect: the 20-day 6A agreement window used as the payment window (corrected in b70ca6797)."""
    (a,) = switching_payments_on_gains([_gain("2021-03-01", "2021-03-01", "2021-03-29")])
    assert a["failed_on"] == "2021-03-29"
    assert a["due_on"] == "2021-04-14"  # 10 working days, Good Friday and Easter Monday skipped
    assert a["paid_on"] <= a["due_on"] and a["posted_as"] == "account_credit"
    assert a["amount_gbp"] == 30.0


def test_the_2025_uplift_reaches_a_switching_failure():
    """Defect: the switching standards paid the 2015 £30 after 2 January 2025."""
    (a,) = switching_payments_on_gains([_gain("2025-02-03", "2025-03-05")])
    assert a["regulation"] == "6ZA" and a["amount_gbp"] == 40.0


def test_the_door_exports_only_finished_facts():
    """Defect: the book or its enums handed back across the wall 'for convenience'."""
    assert door.__all__ == ["switching_payments_on_gains"]
    for name in ("GSOPBook", "GSOPType", "GSOPPayment", "SWITCHING_STANDARDS"):
        assert not hasattr(door, name), name
    answers = switching_payments_on_gains([_gain("2021-03-01", "2021-04-01", "2021-03-29")])
    json.dumps(answers)
