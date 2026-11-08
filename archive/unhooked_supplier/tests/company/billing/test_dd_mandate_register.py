import datetime as dt
import pytest
from company.billing.dd_mandate_register import (
    DDMandateRegister, DDMandateStatus,
)

DATE = dt.date(2022, 3, 1)


def _reg():
    r = DDMandateRegister()
    r.setup_mandate("ACC-001", 15, 80.0, DATE)
    return r


def test_mandate_ref_prefix():
    reg = _reg()
    assert reg._records[0].mandate_ref.startswith("DDM-")


def test_status_default_active():
    reg = _reg()
    assert reg._records[0].status == DDMandateStatus.ACTIVE


def test_day_29_raises():
    reg = DDMandateRegister()
    with pytest.raises(ValueError):
        reg.setup_mandate("ACC-X", 29, 100.0, DATE)


def test_zero_amount_raises():
    reg = DDMandateRegister()
    with pytest.raises(ValueError):
        reg.setup_mandate("ACC-X", 15, 0.0, DATE)


def test_suspend_changes_status():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.suspend(ref, DATE)
    assert updated.status == DDMandateStatus.SUSPENDED


def test_reinstate_after_suspend():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    reg.suspend(ref, DATE)
    updated = reg.reinstate(ref, DATE)
    assert updated.status == DDMandateStatus.REINSTATED


def test_cancel_sets_cancelled():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.cancel(ref, DATE)
    assert updated.status == DDMandateStatus.CANCELLED


def test_record_failure_increments_count():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    updated = reg.record_failure(ref, DATE)
    assert updated.failed_count == 1
    assert updated.status == DDMandateStatus.FAILED


def test_two_failures_auto_cancel():
    reg = _reg()
    ref = reg._records[0].mandate_ref
    reg.record_failure(ref, DATE)
    updated = reg.record_failure(ref, DATE)
    assert updated.failed_count == 2
    assert updated.status == DDMandateStatus.CANCELLED


def test_total_monthly_collection_sums_active():
    reg = _reg()
    reg.setup_mandate("ACC-002", 20, 60.0, DATE)
    assert reg.total_monthly_collection_gbp() == 140.0


def test_module_stays_caller_free_structural_guard():
    """W5_1_banking_payment_rails L3 (2026-07-12, final Expert Hour review):
    this register's own docstring documents that it has ZERO live callers
    anywhere -- DirectDebitBook (company/billing/direct_debit.py) is the
    one with a real caller (simulation/dd_collection_book.py), and this
    module was found NOT to be a clean migration target (no attempt-
    tracking concept). This structural guard mirrors bacs_rails.py's own
    no-probability-constants test: a regression here (something starting to
    import/call DDMandateRegister/setup_mandate outside this module and its
    own tests) would silently reintroduce the exact "two live writers into
    overlapping mandate state" hazard the M2 audit flagged -- catch it here,
    not by re-discovering it in a future Expert Hour."""
    import pathlib
    import re

    repo_root = pathlib.Path(__file__).resolve().parents[3]
    this_module = repo_root / "company" / "billing" / "dd_mandate_register.py"
    # An actual IMPORT statement, not just the class names appearing in
    # prose/comments (this module's own docstring, and direct_debit.py's
    # investigation comment, both legitimately NAME it without using it).
    import_pattern = re.compile(
        r"^\s*(from company\.billing\.dd_mandate_register import|"
        r"import company\.billing\.dd_mandate_register\b)",
        re.MULTILINE,
    )

    offending = []
    for py_file in repo_root.rglob("*.py"):
        if py_file == this_module:
            continue
        if "/tests/" in str(py_file.as_posix()):
            continue  # test files legitimately import what they test
        if "/.git/" in str(py_file) or "__pycache__" in str(py_file):
            continue
        text = py_file.read_text(errors="ignore")
        if import_pattern.search(text):
            offending.append(str(py_file.relative_to(repo_root)))

    assert offending == [], (
        f"dd_mandate_register.py is no longer caller-free: {offending}. "
        "If this is a deliberate, real consolidation, update the maturity-map "
        "simplifications entry and this test together -- do not just delete the guard."
    )
