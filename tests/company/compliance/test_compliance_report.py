"""Tests for company/compliance/compliance_report.py -- DOMAIN_SENSE_AND_COMPLIANCE.md Phase 4."""
from company.compliance.compliance_report import build_compliance_report
from company.compliance.obligations_register import REGISTER


def test_report_shape():
    report = build_compliance_report(held_bill_count=0)
    assert report["obligation_count"] == len(REGISTER)
    assert set(report["by_tier"].keys()) == {"tier_1", "tier_2", "tier_3"}
    assert sum(len(v) for v in report["by_tier"].values()) == len(REGISTER)


def test_zero_held_bills_is_green_overall():
    report = build_compliance_report(held_bill_count=0)
    assert report["overall_rag"] == "GREEN"


def test_held_bills_makes_overall_red():
    report = build_compliance_report(held_bill_count=3)
    assert report["overall_rag"] == "RED"
    assert report["held_bill_count"] == 3


def test_gate_covered_obligations_reflect_live_held_count():
    report = build_compliance_report(held_bill_count=5)
    all_entries = [e for tier in report["by_tier"].values() for e in tier]
    billing = next(e for e in all_entries if e["id"] == "slc_6_7_billing_accuracy")
    vat = next(e for e in all_entries if e["id"] == "vat_by_segment")
    assert billing["status"] == "RED"
    assert vat["status"] == "RED"
    assert "5" in billing["basis"]


def test_gate_covered_obligations_green_when_clean():
    report = build_compliance_report(held_bill_count=0)
    all_entries = [e for tier in report["by_tier"].values() for e in tier]
    billing = next(e for e in all_entries if e["id"] == "slc_6_7_billing_accuracy")
    assert billing["status"] == "GREEN"


def test_non_gate_obligations_are_manual_not_fabricated_green():
    report = build_compliance_report(held_bill_count=0)
    all_entries = [e for tier in report["by_tier"].values() for e in tier]
    psr = next(e for e in all_entries if e["id"] == "psr_vulnerability_duties")
    assert psr["status"] == "MANUAL"
    assert "vulnerability_register" in psr["basis"]


def test_every_entry_carries_full_register_metadata():
    report = build_compliance_report()
    all_entries = [e for tier in report["by_tier"].values() for e in tier]
    for e in all_entries:
        for key in (
            "id", "name", "source", "impact", "likelihood", "control_type",
            "testing_depth", "testing_frequency", "reporting_visibility",
            "status", "basis", "rationale",
        ):
            assert key in e


def test_tier_1_obligations_land_in_tier_1_bucket():
    report = build_compliance_report()
    tier_1_ids = {e["id"] for e in report["by_tier"]["tier_1"]}
    assert "slc_6_7_billing_accuracy" in tier_1_ids
    assert "vat_by_segment" in tier_1_ids
    assert "psr_vulnerability_duties" in tier_1_ids
