"""R15 both-ways proof for PAYMENT_CHANNEL_DD_CONSISTENCY (atom
W2_payment_channel_dd_consistency_invariant).

The named defect: a customer paying by STANDARD CREDIT carries a "Direct debit
returned" arrears stage. An unpaid-DD return is raised against an active Direct
Debit Instruction -- a customer with no DDI has nothing that could be returned,
so the event cannot exist for them.

Both directions are tested, and the SECOND is the one that matters:
  (a) the control FIRES on its own named defect, on every artefact shape and
      every surface that can carry it;
  (b) a genuine Direct Debit customer with a genuine Direct Debit failure
      PASSES -- no fail-open, and equally no OVER-BLOCK, which would quietly
      delete real bad-debt signal from the book to make the count look better.

Plus the fail-open family this project keeps re-finding: an unreadable method
must never be silently treated as Direct Debit, a NaN counter must not pass a
`> 0` comparison that is blind to it, and a population scan that finds no
fields to check must not report a clean book.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    PAYMENT_CHANNEL_DD_CONSISTENCY,
    check_payment_channel_dd_consistency,
    dd_artefact_fields_present,
    scan_payment_channel_dd_consistency,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
BILLING_LEDGER = REPO_ROOT / "docs" / "state" / "billing_ledger.json"


# --------------------------------------------------------------------------
# Registration
# --------------------------------------------------------------------------

def test_the_invariant_is_registered_in_the_library():
    """R10: the closure is the LIBRARY entry, not an instance patch. If the
    invariant is not in ALL_INVARIANTS it is not part of the class closure."""
    assert PAYMENT_CHANNEL_DD_CONSISTENCY in ALL_INVARIANTS
    assert PAYMENT_CHANNEL_DD_CONSISTENCY.id == "payment_channel_dd_consistency"
    assert PAYMENT_CHANNEL_DD_CONSISTENCY.source  # a rule with no anchor is a guess


# --------------------------------------------------------------------------
# (a) FIRES -- the control catches its own named defect, per artefact shape
# --------------------------------------------------------------------------

def test_fires_on_standard_credit_with_dd_failed_stage():
    """The exact C1g defect: a standard-credit arrears case opened with a
    DD_FAILED stage."""
    record = {
        "customer_id": "C1g", "case_id": "ARR-C1g-2016-08-31",
        "method": "standard_credit",
        "stages": [
            {"stage": "DD_FAILED", "date": "2016-08-31", "note": "Direct debit returned"},
            {"stage": "FIRST_NOTICE", "date": "2016-09-07", "note": "First overdue notice"},
        ],
    }
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_the_direct_debit_returned_note_even_without_the_stage_name():
    """The note is a second, independent carrier of the same claim. A rename of
    the stage label alone must not launder the record clean."""
    record = {
        "customer_id": "C4", "method": "standard_credit",
        "stages": [{"stage": "PAYMENT_MISSED", "date": "2018-03-31",
                     "note": "Direct debit returned"}],
    }
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_dd_failure_reason_on_a_non_dd_method():
    """`insufficient_funds` is a Bacs return reason -- it cannot be stamped on
    a customer with no mandate."""
    record = {"customer_id": "C8", "method": "standard_credit",
              "result": "failed", "dd_failure_reason": "insufficient_funds"}
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_dd_failed_result_label():
    record = {"customer_id": "C8", "payment_channel": "standard_credit",
              "result": "DD_FAILED"}
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_dd_failed_counter_on_the_sample_surface():
    record = {"customer_id": "C4", "payment_channel": "standard_credit", "dd_failed": 4}
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_non_zero_dd_fail_rate_on_the_sample_surface():
    record = {"customer_id": "C1g", "payment_channel": "standard_credit",
              "dd_fail_rate": 0.0277}
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_on_a_dd_failure_buried_in_the_payment_miss_trajectory():
    """The sample surface carries per-year buckets. A control reading only the
    scalar would miss a defect visible in the yearly detail."""
    record = {
        "customer_id": "C4", "payment_channel": "standard_credit",
        "dd_fail_rate": 0.0,
        "payment_miss_trajectory": [
            {"year": 2018, "late": 1, "dd_failed": 0, "total": 12},
            {"year": 2021, "late": 0, "dd_failed": 3, "total": 12},
        ],
    }
    assert check_payment_channel_dd_consistency(record) is False


def test_fires_for_a_corporate_customer_whose_channel_is_null():
    """I&C/SME customers carry `payment_channel: null` -- the residential
    channel model does not apply to them. They pay by bacs/chaps, so non-DD is
    the CORRECT answer for them, not merely the safe one, and a DD failure on
    their record is exactly as impossible."""
    record = {"customer_id": "C_IC1", "payment_channel": None, "dd_failed": 1}
    assert check_payment_channel_dd_consistency(record) is False


# --------------------------------------------------------------------------
# (b) PASSES -- no fail-open, and equally no OVER-BLOCK
# --------------------------------------------------------------------------

def test_passes_a_genuine_direct_debit_failure():
    """THE test that matters. A real DD customer with a real DD failure is
    legitimate bad-debt signal. A control that blocks this would shrink the
    violation count by deleting the book's real arrears -- the R12 goal-seek
    failure mode in its most damaging form."""
    record = {
        "customer_id": "C7", "method": "direct_debit",
        "result": "failed", "dd_failure_reason": "insufficient_funds",
        "dd_failed": 8, "dd_fail_rate": 0.07,
        "stages": [{"stage": "DD_FAILED", "date": "2022-01-31",
                     "note": "Direct debit returned"}],
    }
    assert check_payment_channel_dd_consistency(record) is True


def test_passes_a_non_dd_customer_whose_arrears_opened_as_payment_missed():
    """The remediated shape: same collections cascade, method-correct opening
    stage. This is what the fixed generator emits."""
    record = {
        "customer_id": "C1g", "method": "standard_credit",
        "stages": [
            {"stage": "PAYMENT_MISSED", "date": "2016-08-31",
             "note": "Standard credit payment not received"},
            {"stage": "FIRST_NOTICE", "date": "2016-09-07", "note": "First overdue notice"},
            {"stage": "WRITTEN_OFF", "date": "2016-11-29", "note": "Debt written off"},
        ],
    }
    assert check_payment_channel_dd_consistency(record) is True


def test_passes_a_corporate_invoice_dispute():
    record = {
        "customer_id": "C_IC1", "method": "chaps",
        "stages": [{"stage": "INVOICE_DISPUTED", "date": "2024-03-31",
                     "note": "Invoice disputed by customer"}],
    }
    assert check_payment_channel_dd_consistency(record) is True


def test_passes_a_non_dd_customer_who_simply_paid():
    record = {"customer_id": "C1g", "method": "standard_credit",
              "result": "success", "dd_failed": 0, "dd_fail_rate": 0.0}
    assert check_payment_channel_dd_consistency(record) is True


def test_passes_a_direct_debit_customer_with_no_failures_at_all():
    record = {"customer_id": "C1", "payment_channel": "direct_debit",
              "dd_failed": 0, "dd_fail_rate": 0.0}
    assert check_payment_channel_dd_consistency(record) is True


# --------------------------------------------------------------------------
# Fail-open family
# --------------------------------------------------------------------------

def test_a_missing_method_is_not_silently_treated_as_direct_debit():
    """The fail-open trap named in the atom's own R15 obligation: if an absent
    method defaulted to `direct_debit`, every unlabelled record would license
    any DD artefact and the control would be decorative."""
    assert check_payment_channel_dd_consistency({"dd_failed": 3}) is False


def test_an_unreadable_method_type_is_not_treated_as_direct_debit():
    for bad_method in (0, 1, [], {}, True):
        record = {"method": bad_method, "dd_failure_reason": "insufficient_funds"}
        assert check_payment_channel_dd_consistency(record) is False, bad_method


def test_an_unrecognised_method_label_cannot_license_a_dd_artefact():
    record = {"method": "carrier_pigeon", "dd_failed": 2}
    assert check_payment_channel_dd_consistency(record) is False


def test_a_nan_dd_fail_rate_fails_closed_rather_than_passing_a_blind_comparison():
    """`float('nan') > 0` is False, so a naive `> 0` test reports a corrupt
    counter as 'no DD failures here'. An unverifiable value is a FAILED check."""
    assert (float("nan") > 0) is False  # the blindness this guards against
    for bad in (float("nan"), float("inf"), float("-inf"), "not-a-number"):
        record = {"method": "standard_credit", "dd_fail_rate": bad}
        assert check_payment_channel_dd_consistency(record) is False, bad


def test_a_nan_counter_inside_the_trajectory_also_fails_closed():
    record = {"method": "standard_credit",
              "payment_miss_trajectory": [{"year": 2021, "dd_failed": float("nan")}]}
    assert check_payment_channel_dd_consistency(record) is False


def test_an_unreadable_record_or_stage_fails_closed():
    assert check_payment_channel_dd_consistency(None) is False
    assert check_payment_channel_dd_consistency("not a record") is False
    assert check_payment_channel_dd_consistency(
        {"method": "standard_credit", "stages": ["not a stage dict", 7]}
    ) is False


def test_a_direct_debit_record_is_not_rescued_by_an_unreadable_artefact():
    """Symmetry check on the short-circuit: DD passes because DD artefacts are
    legal for it, which must not depend on the artefacts being readable."""
    assert check_payment_channel_dd_consistency(
        {"method": "direct_debit", "dd_fail_rate": float("nan")}
    ) is True


# --------------------------------------------------------------------------
# Vacuity -- the guard that catches a control checking nothing
# --------------------------------------------------------------------------

def test_the_vacuity_helper_distinguishes_checked_from_unchecked_records():
    """A per-record predicate that finds no fields to inspect returns True. A
    whole population of those reports 100% clean while checking literally
    nothing -- the fail-open that let a printed-bill control pass 1557/1557 on
    a book where the checked field was absent."""
    assert dd_artefact_fields_present({"method": "standard_credit", "dd_failed": 0}) is True
    assert dd_artefact_fields_present({"method": "standard_credit"}) is False
    assert dd_artefact_fields_present({"stages": []}) is False
    assert dd_artefact_fields_present({"stages": [{"stage": "DD_FAILED"}]}) is True
    assert dd_artefact_fields_present(None) is False


def test_scan_names_the_violating_customer_rather_than_returning_a_bare_count():
    records = [
        {"customer_id": "C1", "method": "direct_debit", "dd_failed": 2},
        {"customer_id": "C4", "method": "standard_credit", "dd_failed": 4},
    ]
    findings = scan_payment_channel_dd_consistency(records)
    assert len(findings) == 1
    assert findings[0]["customer_id"] == "C4"
    assert findings[0]["method"] == "standard_credit"
    assert findings[0]["check"] == "payment_channel_dd_consistency"


def test_scan_of_an_empty_population_is_empty_and_provably_vacuous():
    """'Zero violations' on an empty population must never read as evidence."""
    assert scan_payment_channel_dd_consistency([]) == []
    assert scan_payment_channel_dd_consistency(None) == []


# --------------------------------------------------------------------------
# Population -- the real book, with its own vacuity guard
# --------------------------------------------------------------------------

def _ledger_arrears_records():
    """Every arrears case in the real ledger, joined to the method of the
    payment that opened it."""
    if not BILLING_LEDGER.exists():
        pytest.skip("billing_ledger.json not generated in this tree")
    ledger = json.loads(BILLING_LEDGER.read_text())
    records = []
    for cid, customer in (ledger.get("customers") or {}).items():
        by_invoice = {p["invoice_number"]: p for p in (customer.get("payments") or [])}
        for case in customer.get("arrears_history") or []:
            payment = by_invoice.get(case.get("invoice_number")) or {}
            records.append({
                "customer_id": cid,
                "case_id": case.get("case_id"),
                "method": payment.get("method"),
                "stages": case.get("stages"),
            })
    return records


def test_the_population_control_is_not_vacuous_on_the_real_ledger():
    """Proves the population assertion below is actually inspecting the fields
    it claims to. Without this, a schema change that renamed `stages` would
    turn the population test permanently green while checking nothing."""
    records = _ledger_arrears_records()
    assert records, "the real ledger carries no arrears cases to check"
    checked = [r for r in records if dd_artefact_fields_present(r)]
    assert checked, "no arrears case exposed a field this control inspects"
    methods = {r["method"] for r in records}
    assert "direct_debit" in methods, "no DD case present: direction (b) untested here"
    assert methods - {"direct_debit"}, "no non-DD case present: direction (a) untested here"


def test_the_real_ledger_has_no_non_dd_customer_carrying_a_dd_failure():
    """The class closure, asserted on the real book rather than on fixtures.

    This test is EXPECTED TO FAIL against a ledger generated before the
    arrears_engine fix and to pass once it is regenerated -- the ledger on disk
    is a build artefact, not source. Its measured pre-fix state was 5 customers
    / 12 arrears cases (C1g, C4, C5, C6, C8).
    """
    findings = scan_payment_channel_dd_consistency(_ledger_arrears_records())
    assert findings == [], (
        "%d arrears case(s) pair a non-DD method with a DD-only artefact: %s"
        % (len(findings), sorted({f["customer_id"] for f in findings}))
    )
