"""Mutation-test apparatus for the company's controls -- CONTROLS_THAT_CANNOT_FAIL.md.

Doctrine: a control that CANNOT FAIL is worse than no control -- it manufactures
confidence. For every inventoried control, construct the minimal CORRECT input,
then MUTATE it to inject the exact defect the control exists to catch, and assert
the control FIRES (rejects / flags / holds). A control that does not fire on its
own named defect is THEATRE.

Also encodes the three killer-pattern audits as executable assertions:
  - TAUTOLOGY  -- check_vat cannot catch the mislabel it is named for (documented,
                  xfail); its independent replacement DOES fire.
  - FAIL-OPEN  -- the pre-bill gate's subtotal<=0 skip (FIXED: now fails closed).
  - FAIL-SILENT-- the Qwen backstop returning clean when Ollama is down (FIXED:
                  now alarms on checker-unavailability).

Registry: docs/design/control_registry.json. Kill list: docs/design/CONTROL_KILL_LIST.md.
"""
import json
import os
import tempfile
from datetime import date

import pytest

from company.compliance import domain_invariants as di
from company.compliance.domain_invariants import (
    ALL_INVARIANTS,
    RateInvariant,
    RangeInvariant,
    YearlyRangeInvariant,
    check_vat,
    check_vat_consistent_with_consumption,
    check_resi_bill_consumption_plausible,
    check_back_billing_cap_respected,
    check_billed_clock_reconciles,
)
from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from company.billing.pre_bill_validation import validate_bill
from company.compliance import obligations_register as orr
from company.compliance.internal_audit import (
    parse_audit_response,
    run_internal_audit,
    run_phase_close_audit,
    CHECKER_UNAVAILABLE,
)
import tools.epistemic_verifier as ev


# --------------------------------------------------------------------------
# domain_invariants.py -- the invariant library
# --------------------------------------------------------------------------

def test_rate_invariant_fires_on_wrong_rate():
    # CORRECT: resi VAT at 5% passes. MUTATE: 20% on a resi bill must fire.
    assert di.VAT_RESIDENTIAL.check(0.05) is True
    assert di.VAT_RESIDENTIAL.check(0.20) is False
    assert di.VAT_SME.check(0.20) is True
    assert di.VAT_SME.check(0.05) is False


def test_every_range_invariant_fires_outside_its_band():
    """Sweep: EVERY RangeInvariant in the library must reject a value just below
    its low bound and just above its high bound. A range control that accepts an
    out-of-band value is theatre."""
    range_invs = [i for i in ALL_INVARIANTS if isinstance(i, RangeInvariant)]
    assert range_invs, "no RangeInvariants found -- inventory drift"
    for inv in range_invs:
        span = max(inv.high - inv.low, 1.0)
        mid = (inv.low + inv.high) / 2
        assert inv.check(mid) is True, f"{inv.id} rejects a mid-band value"
        assert inv.check(inv.low - 0.01 * span) is False, f"{inv.id} FAILS to fire below low"
        assert inv.check(inv.high + 0.01 * span) is False, f"{inv.id} FAILS to fire above high"


def test_yearly_range_invariant_fires_on_order_of_magnitude_error():
    inv = di.UNIT_RATE_ELEC_RESI_BY_YEAR
    year = min(inv.by_year)
    anchor = inv.by_year[year]
    assert inv.check(anchor, year) is True
    assert inv.check(anchor * 10, year) is False  # 10x the cap -- absurd


def test_yearly_range_invariant_precap_year_is_documented_fail_open():
    """DOCUMENTED limitation (not an accidental fail-open): no valid anchor
    pre-dates the Ofgem cap, so any pre-min-year value passes. Asserted here so
    the kill list can honestly cite it as a KNOWN, sourced gap, not a surprise."""
    inv = di.UNIT_RATE_ELEC_RESI_BY_YEAR
    precap_year = min(inv.by_year) - 5
    assert inv.check(9_999_999.0, precap_year) is True  # cannot check -- by design


# --------------------------------------------------------------------------
# The flagship TAUTOLOGY -- vat_by_segment
# --------------------------------------------------------------------------

@pytest.mark.xfail(
    reason="TAUTOLOGY (theatre): check_vat derives the expected rate from `segment` "
    "and checks it against a VAT figure the generator also derives from `segment`, "
    "so it structurally CANNOT catch the SME-as-Household MISLABEL it is named for. "
    "Its independent replacement (see next test) is the real control.",
    strict=True,
)
def test_check_vat_arithmetic_catches_the_mislabel_it_is_named_for():
    # An SME mislabelled resi, with VAT self-consistently computed at 5%.
    # check_vat("resi", 0.05) == True -> does NOT fire. This assert therefore
    # fails, and xfail(strict) records the tautology honestly in the suite.
    assert check_vat("resi", 0.05) is False


def test_independent_vat_consumption_crosscheck_fires_on_the_mislabel():
    # The real fix: an I&C-scale metered load billed at the domestic 5% rate.
    big_load_kwh = 5000.0  # well above the resi monthly ceiling
    fires = not check_vat_consistent_with_consumption("resi", "electricity", 0.05, big_load_kwh, 30)
    assert fires is True
    # One-directional by honest design: a business rate on domestic-scale
    # consumption is NEVER flagged (a microbusiness looks identical there).
    assert check_vat_consistent_with_consumption("sme", "electricity", 0.20, 300.0, 30) is True


def test_resi_consumption_plausibility_fires_on_sme_scale_load():
    assert check_resi_bill_consumption_plausible("electricity", 300.0, 30) is True
    assert check_resi_bill_consumption_plausible("electricity", 50_000.0, 30) is False


# --------------------------------------------------------------------------
# check_back_billing_cap_respected -- fail-CLOSED (already hardened)
# --------------------------------------------------------------------------

def _breaching_catchup_bill(written_off):
    return {
        "catchup_applied": True,
        "catchup_direction": "undercharge",
        "catchup_period_start": "2020-01-01",
        "catchup_period_end": "2024-01-01",
        "period_end": "2024-02-01",
        "catchup_raw_delta_gbp": 5000.0,
        "catchup_written_off_gbp": written_off,
        "segment": "resi",
        "customer_id": "X",
    }


def test_back_billing_cap_fires_when_breach_not_written_off():
    assert check_back_billing_cap_respected(_breaching_catchup_bill(0.0)) is False


def test_back_billing_cap_passes_with_correct_write_off():
    a = BackBillingAssessment(
        account_id="X", billing_date=date(2024, 2, 1),
        consumption_period_start=date(2020, 1, 1), consumption_period_end=date(2024, 1, 1),
        billed_amount_gbp=5000.0, reason=BackBillingReason.ESTIMATED_READ_CORRECTED,
        is_domestic=True,
    )
    assert check_back_billing_cap_respected(_breaching_catchup_bill(a.written_off_gbp)) is True


def test_back_billing_cap_fails_closed_on_missing_or_malformed_data():
    # Killer-pattern audit: must NOT fail-open on missing/malformed inputs.
    assert check_back_billing_cap_respected({"catchup_applied": True}) is False  # no direction
    bad_date = _breaching_catchup_bill(0.0)
    bad_date["catchup_period_start"] = "not-a-date"
    assert check_back_billing_cap_respected(bad_date) is False  # malformed date, fail closed


def test_billed_clock_reconcile_fires_on_divergence():
    issued = [{"total_amount_gbp": 60.0}, {"total_amount_gbp": 40.0}]
    assert check_billed_clock_reconciles(100.0, issued) is True
    assert check_billed_clock_reconciles(100.0, issued[:1]) is False  # divergence


# --------------------------------------------------------------------------
# pre_bill_validation.py -- the Tier-1 gate (integration + FAIL-OPEN fix)
# --------------------------------------------------------------------------

def _bill(**overrides):
    b = {
        "customer_id": "C", "period_start": "2024-01-01", "period_end": "2024-01-31",
        "segment": "resi", "commodity": "electricity", "total_consumption_kwh": 300.0,
        "commodity_amount_gbp": 44.55, "non_commodity_amount_gbp": 16.65,
        "standing_charge_gbp": 9.30, "vat_gbp": 3.53,
    }
    b.update(overrides)
    return b


def test_gate_passes_a_clean_bill():
    assert validate_bill(_bill()).outcome.value == "pass"


def test_gate_holds_the_sme_as_household_mislabel():
    sub = 44.55 + 16.65 + 9.30
    mis = _bill(total_consumption_kwh=5000.0, vat_gbp=round(sub * 0.05, 2))
    assert validate_bill(mis).held is True


def test_gate_fail_open_on_nonpositive_subtotal_is_fixed():
    """FAIL-OPEN FIX: a bill with a zero/negative subtotal PREVIOUSLY skipped all
    VAT validation silently. Now VAT charged on a non-positive subtotal, and any
    negative subtotal, fail CLOSED (HELD)."""
    zero_sub_with_vat = _bill(
        commodity_amount_gbp=0.0, non_commodity_amount_gbp=0.0,
        standing_charge_gbp=0.0, vat_gbp=5.0,
    )
    assert validate_bill(zero_sub_with_vat).held is True

    negative_sub = _bill(commodity_amount_gbp=-100.0)
    assert validate_bill(negative_sub).held is True


# --------------------------------------------------------------------------
# internal_audit.py -- the Qwen backstop (FAIL-SILENT fix)
# --------------------------------------------------------------------------

def test_parse_response_empty_is_unavailable_not_clean():
    # FAIL-SILENT killer pattern: an unavailable checker must NOT read as clean.
    assert parse_audit_response("")["verdict"] == CHECKER_UNAVAILABLE
    assert parse_audit_response("garbage, no verdict")["verdict"] == CHECKER_UNAVAILABLE
    # A real verdict still parses normally.
    assert parse_audit_response("VERDICT: flagged\nNOTE: x")["verdict"] == "flagged"
    assert parse_audit_response("VERDICT: clean\nNOTE: x")["verdict"] == "clean"


def test_internal_audit_alarms_when_checker_unavailable():
    bills = [{"customer_id": "C1", "segment": "resi", "period_end": "2024-01-31"},
             {"customer_id": "C2", "segment": "resi", "period_end": "2024-01-31"}]
    findings = run_internal_audit(bills, n_samples=2, seed=1, call_qwen_fn=lambda p: "")
    assert any(f.get("kind") == "checker_unavailable" for f in findings), \
        "FAIL-SILENT: audit returned clean/empty when the checker was down"


def test_phase_close_audit_alarms_when_checker_unavailable():
    artefacts = {"page_a": "content a", "page_b": "content b"}
    findings = run_phase_close_audit(artefacts, n_samples=2, seed=1, call_qwen_fn=lambda p: "")
    assert any(f.get("kind") == "checker_unavailable" for f in findings)


def test_internal_audit_clean_run_does_not_false_alarm():
    # The fix must not create false positives: a reachable, clean checker -> [].
    bills = [{"customer_id": "C1", "segment": "resi", "period_end": "2024-01-31"}]
    findings = run_internal_audit(
        bills, n_samples=1, seed=1, call_qwen_fn=lambda p: "VERDICT: clean\nNOTE: ok"
    )
    assert findings == []


# --------------------------------------------------------------------------
# obligations_register.py -- risk tiering (classifier)
# --------------------------------------------------------------------------

def test_customer_financial_high_reaches_tier_1():
    assert orr.derive_risk_tier(orr.ImpactTier.CUSTOMER_FINANCIAL, orr.Likelihood.HIGH) == orr.RiskTier.TIER_1


def test_physical_harm_is_tier_1_even_at_low_likelihood():
    assert orr.derive_risk_tier(orr.ImpactTier.PHYSICAL_HARM, orr.Likelihood.LOW) == orr.RiskTier.TIER_1


def test_vat_by_segment_obligation_is_tier_1():
    assert any(o.id == "vat_by_segment" and o.risk_tier == orr.RiskTier.TIER_1 for o in orr.REGISTER)


def test_uncovered_obligations_are_surfaced_not_hidden():
    gaps = {o.id for o in orr.obligations_without_a_tracker()}
    # vat_by_segment and slc_6_7_billing_accuracy are honestly flagged as
    # having no dedicated existing_tracker (the gap this programme fills).
    assert "vat_by_segment" in gaps


# --------------------------------------------------------------------------
# epistemic_verifier.py -- SIM/company wall scanner
# --------------------------------------------------------------------------

def test_epistemic_verifier_fires_on_forbidden_sim_import():
    with tempfile.TemporaryDirectory() as d:
        bad = os.path.join(d, "bad.py")
        with open(bad, "w") as fh:
            fh.write("from simulation.weather_engine import temperature\n")
        assert len(ev._scan_file(bad)) == 1  # FIRES


def test_epistemic_verifier_clean_on_approved_seam_import():
    with tempfile.TemporaryDirectory() as d:
        good = os.path.join(d, "good.py")
        with open(good, "w") as fh:
            fh.write("from company.interfaces.sim_interface import get_market_price\n")
        assert ev._scan_file(good) == []


# --------------------------------------------------------------------------
# Registry integrity -- the kill list must stay honest / in sync
# --------------------------------------------------------------------------

def test_control_registry_is_wellformed_and_in_sync():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, "docs/design/control_registry.json")) as fh:
        reg = json.load(fh)
    controls = reg["controls"]
    assert controls, "empty registry"
    valid = {"FIRED", "THEATRE", "DID-NOT-FIRE"}
    for c in controls:
        assert c["result"] in valid, f"{c['id']} has invalid result {c['result']}"
        assert c["location"] and c["catches"] and c["mutation"]
    # The flagship tautology must remain recorded as THEATRE -- if a future
    # refactor 'fixes' check_vat into looking like it fires, this guards against
    # quietly relabelling a known tautology as a real control.
    vat = next(c for c in controls if c["id"] == "check_vat_arithmetic")
    assert vat["result"] == "THEATRE"
    assert vat["killer_pattern_audit"] == "TAUTOLOGY"
