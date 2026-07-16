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


# ==========================================================================
# PASS 2 (H12 L2->L3): the INVENTORIED-BUT-UNTESTED tail
# CONTROLS_THAT_CANNOT_FAIL.md -- compliance trackers, health/page-consistency
# gates, the daemon change-detection gate, and (structurally) the LLM judges.
# Same doctrine: inject each control's named defect and assert it FIRES; audit
# every one for TAUTOLOGY / FAIL-OPEN / FAIL-SILENT. Where a control has a
# genuine not-applicable/degrade-gracefully branch we ASSERT that branch
# explicitly so the kill list can cite it honestly rather than hide it, and
# where a real fail-open/fail-silent gap exists that needs caller analysis we
# pin its CURRENT behaviour in a test and register it as a kill-list entry.
# ==========================================================================

from company.compliance import population_sanity as ps
from company.compliance.consumer_duty import (
    ConsumerDutyRegister, OutcomeAssessment, DutyOutcome, OutcomeRAG,
)
from company.regulatory.social_obligation_register import (
    SocialObligationSpendRegister, SocialObligationType, ObligationStatus,
)
from company.compliance.crisis_bad_debt_validator import validate_crisis_bad_debt


# --------------------------------------------------------------------------
# population_sanity.py -- population-level statistical checks
# --------------------------------------------------------------------------

def _resi_bill(cid, year, kwh, days, gbp=None, commodity="electricity"):
    return {
        "customer_id": cid, "segment": "resi", "commodity": commodity,
        "period_end": f"{year}-12-31", "total_consumption_kwh": kwh,
        "days_in_period": days, "commodity_amount_gbp": gbp if gbp is not None else 0.0,
    }


def test_population_consumption_distribution_fires_on_sme_scale_annual_load():
    # CORRECT: ~3000 kWh/yr over a full year passes. MUTATE: 50,000 kWh/yr fires.
    clean = [_resi_bill("C_ok", 2022, 1500.0, 183), _resi_bill("C_ok", 2022, 1500.0, 183)]
    assert ps.check_consumption_distribution(clean) == []
    absurd = [_resi_bill("C_bad", 2022, 25000.0, 183), _resi_bill("C_bad", 2022, 25000.0, 183)]
    fired = ps.check_consumption_distribution(absurd)
    assert fired and fired[0]["check"] == "consumption_distribution_vs_tdcv"


def test_population_consumption_distribution_partial_year_is_documented_not_fail_open():
    # DOCUMENTED not-applicable guard (SANITY_TRIAGE_2026_07_11): a partial-year
    # joiner/leaver (< _MIN_DAYS_COVERAGE) is skipped, NOT flagged low. Asserted
    # so the kill list cites it as a KNOWN scoped guard, not a surprise fail-open.
    stub = [_resi_bill("C_stub", 2022, 128.68, 2)]  # 2-day stub, absurd as a full year
    assert ps.check_consumption_distribution(stub) == []


def test_population_unit_rate_bands_fire_on_absurd_rate():
    year = min(di.UNIT_RATE_ELEC_RESI_BY_YEAR.by_year) + 3
    anchor = di.UNIT_RATE_ELEC_RESI_BY_YEAR.by_year[year]  # GBP/MWh
    # CORRECT: 1000 kWh billed at exactly the anchor GBP/MWh -> avg == anchor, in band.
    clean = [_resi_bill("C_ok", year, 1000.0, 365, gbp=anchor)]
    assert ps.check_unit_rate_bands(clean) == []
    # MUTATE: same kWh billed at ~16x the anchor -> absurd average unit rate.
    absurd = [_resi_bill("C_bad", year, 1000.0, 365, gbp=anchor * 16)]
    fired = ps.check_unit_rate_bands(absurd)
    assert fired and fired[0]["check"] == "unit_rate_vs_cap_band"


def test_population_estimated_read_rate_fires_when_mechanism_broken():
    # CORRECT: a plausible mix passes. MUTATE: 100% estimated -> mechanism broken.
    mixed = [{"status": "estimated"}] * 3 + [{"status": "actual"}] * 7
    assert ps.check_estimated_read_rate(mixed) == []
    all_est = [{"status": "estimated"}] * 20
    fired = ps.check_estimated_read_rate(all_est)
    assert fired and fired[0]["check"] == "estimated_read_rate_vs_industry_norms"


def test_population_estimated_read_rate_empty_log_fires():
    # KL-4 FIXED (FAIL-SILENT): a TOTAL absence of reads -- the most-broken
    # read-generation state -- previously read CLEAN ([]) (theatre). Now the
    # empty log FIRES: an empty check cannot be a passing check (R15).
    # BEFORE: check_estimated_read_rate([]) == []  (passed wrongly / fail-silent)
    # AFTER : it returns a finding.
    fired = ps.check_estimated_read_rate([])
    assert fired and fired[0]["check"] == "estimated_read_rate_vs_industry_norms"
    # OUTCOME-SAFE: a plausible non-empty mix still reads clean (no false positive).
    assert ps.check_estimated_read_rate(
        [{"status": "estimated"}] * 3 + [{"status": "actual"}] * 7
    ) == []


def test_population_payment_channel_mix_fires_when_everyone_on_one_method():
    mixed = ([{"method": "direct_debit"}] * 7) + ([{"method": "standard_credit"}] * 3)
    assert ps.check_payment_channel_mix(mixed) == []
    all_dd = [{"method": "direct_debit"}] * 20
    fired = ps.check_payment_channel_mix(all_dd)
    assert fired and fired[0]["check"] == "payment_channel_mix_vs_desnz_anchor"


# --------------------------------------------------------------------------
# consumer_duty.py -- FCA Consumer Duty RAG aggregator
# --------------------------------------------------------------------------

def _duty_assessment(outcome, rag, date="2024-01-01"):
    return OutcomeAssessment(
        outcome=outcome, assessment_date=date, rag=rag,
        metric_value=1.0, metric_name="m", narrative="n",
    )


def test_consumer_duty_overall_rag_fires_on_a_red_outcome():
    reg = ConsumerDutyRegister()
    reg.record_assessment(_duty_assessment(DutyOutcome.PRICE_AND_VALUE, OutcomeRAG.GREEN))
    assert reg.overall_rag() == OutcomeRAG.GREEN
    # MUTATE: a single RED outcome must escalate the whole register to RED.
    reg.record_assessment(_duty_assessment(DutyOutcome.CONSUMER_SUPPORT, OutcomeRAG.RED, "2024-02-01"))
    assert reg.overall_rag() == OutcomeRAG.RED
    assert len(reg.red_outcomes()) == 1


def test_consumer_duty_empty_register_fires_not_green():
    # KL-5 FIXED (FAIL-SILENT): an EMPTY register -- zero outcome assessments
    # ever performed -- previously reported GREEN (theatre: absence read as
    # compliant). Under FCA Consumer Duty "no assessment done" is a governance
    # failure. Now it reports the distinct NOT_ASSESSED state (NOT green), and
    # the register flags it.
    # BEFORE: ConsumerDutyRegister().overall_rag() == OutcomeRAG.GREEN
    # AFTER : it is NOT_ASSESSED, and needs_attention() fires.
    reg = ConsumerDutyRegister()
    assert reg.overall_rag() == OutcomeRAG.NOT_ASSESSED
    assert reg.overall_rag() != OutcomeRAG.GREEN
    assert reg.is_assessed() is False
    assert reg.needs_attention() is True
    # OUTCOME-SAFE: a genuinely populated all-green register still reads GREEN
    # (no false positive on legitimate compliance).
    reg.record_assessment(_duty_assessment(DutyOutcome.PRICE_AND_VALUE, OutcomeRAG.GREEN))
    reg.record_assessment(_duty_assessment(DutyOutcome.CONSUMER_SUPPORT, OutcomeRAG.GREEN))
    reg.record_assessment(_duty_assessment(DutyOutcome.PRODUCTS_AND_SERVICES, OutcomeRAG.GREEN))
    reg.record_assessment(_duty_assessment(DutyOutcome.CONSUMER_UNDERSTANDING, OutcomeRAG.GREEN))
    assert reg.overall_rag() == OutcomeRAG.GREEN
    assert reg.needs_attention() is False


# --------------------------------------------------------------------------
# social_obligation_register.py -- mandatory social spend
# --------------------------------------------------------------------------

def test_social_obligation_underspend_surfaces_via_independent_evidence():
    reg = SocialObligationSpendRegister()
    # An obligation genuinely met (PAID, full spend) is compliant + not underspent.
    reg.record_obligation(2024, SocialObligationType.WARM_HOME_DISCOUNT,
                          target_gbp=1000.0, actual_spend_gbp=1000.0,
                          status=ObligationStatus.PAID)
    # MUTATE: an underperforming obligation must surface in non_compliant().
    reg.record_obligation(2024, SocialObligationType.ENERGY_EFFICIENCY,
                          target_gbp=1000.0, actual_spend_gbp=100.0,
                          status=ObligationStatus.UNDERPERFORMING)
    assert len(reg.non_compliant()) == 1
    # The INDEPENDENT spend-vs-target view catches underspend regardless of the
    # self-declared status label (see status-trust gap below).
    assert len(reg.underspend_records()) == 1


def test_social_obligation_status_trust_tautology_now_fires():
    # KL-6 FIXED (TAUTOLOGY): non_compliant() previously trusted the self-declared
    # `status` field ALONE -- a record mislabelled PAID while grossly underspent
    # passed it (the same "compliance from a declared label" pattern as the
    # flagship VAT tautology). non_compliant() now also folds in the INDEPENDENT
    # spend-vs-target evidence (is_underspend), so the mislabel can no longer
    # manufacture compliance.
    # BEFORE: reg.non_compliant() == []           (tautology: did NOT fire)
    # AFTER : reg.non_compliant() catches it via independent underspend evidence.
    reg = SocialObligationSpendRegister()
    reg.record_obligation(2024, SocialObligationType.WARM_HOME_DISCOUNT,
                          target_gbp=1_000_000.0, actual_spend_gbp=1.0,
                          status=ObligationStatus.PAID)  # mislabelled PAID
    assert len(reg.non_compliant()) == 1                # now FIRES on the mislabel
    assert len(reg.underspend_records()) == 1           # independent control also fires
    # OUTCOME-SAFE: a genuinely-met PAID obligation (full spend) is NOT flagged.
    ok = SocialObligationSpendRegister()
    ok.record_obligation(2024, SocialObligationType.WARM_HOME_DISCOUNT,
                         target_gbp=1000.0, actual_spend_gbp=1000.0,
                         status=ObligationStatus.PAID)
    assert ok.non_compliant() == []
    # OUTCOME-SAFE: a PROJECTED under-target obligation (not yet spent) is NOT a
    # breach -- projections legitimately show spend below target.
    proj = SocialObligationSpendRegister()
    proj.record_obligation(2024, SocialObligationType.ENERGY_EFFICIENCY,
                           target_gbp=3000.0, actual_spend_gbp=0.0,
                           status=ObligationStatus.PROJECTED)
    assert proj.non_compliant() == []


# --------------------------------------------------------------------------
# crisis_bad_debt_validator.py -- anchored crisis step-up diagnostic
# --------------------------------------------------------------------------

def test_crisis_bad_debt_validator_fires_on_flat_no_stepup_trajectory():
    # A flat ~2%-of-revenue trajectory with NO crisis step-up must FAIL (this is
    # the EXPECTED failing state the CFO cold-walk found -- the control's whole
    # value is that it fires on exactly that).
    flat_bd = {y: 200.0 for y in (2016, 2017, 2018, 2019, 2021, 2022)}
    flat_rev = {y: 10_000.0 for y in (2016, 2017, 2018, 2019, 2021, 2022)}
    res = validate_crisis_bad_debt(flat_bd, flat_rev)
    assert res.passed is False
    assert any("step-up" in f for f in res.failures)


def test_crisis_bad_debt_validator_passes_on_a_real_stepup():
    # CORRECT: a genuine crisis step-up (rate >= floor and >= 1.2x pre-crisis)
    # must PASS -- proving the control is not stuck-closed theatre.
    bd = {2016: 100.0, 2017: 100.0, 2018: 100.0, 2019: 100.0, 2021: 300.0, 2022: 300.0}
    rev = {y: 10_000.0 for y in bd}
    res = validate_crisis_bad_debt(bd, rev)
    assert res.passed is True


def test_crisis_bad_debt_validator_fails_closed_on_missing_crisis_data():
    # FAIL-CLOSED audit: no crisis-year data present must NOT read as a pass.
    only_pre = {2016: 100.0, 2017: 100.0}
    res = validate_crisis_bad_debt(only_pre, {2016: 10_000.0, 2017: 10_000.0})
    assert res.passed is False
    assert any("no crisis-year" in f for f in res.failures)


# --------------------------------------------------------------------------
# green_claims_audit.py -- REGO coverage vs green marketing claims
# --------------------------------------------------------------------------

def test_green_claims_audit_fires_on_uncovered_claim():
    from company.compliance.green_claims_audit import GreenClaimsAuditor
    from company.market.rego_portfolio import RegoPortfolio, RegoPurchase
    p = RegoPortfolio()
    p.buy(RegoPurchase(purchase_id="R1", purchase_date="2020-01-15", scheme_year=2020,
                       mwh=5.0, price_per_mwh=1.0, generator="G", technology="wind_onshore"))
    auditor = GreenClaimsAuditor(p)
    # CORRECT: 5 MWh claim fully covered by 5 MWh held -> COMPLIANT.
    ok = auditor.audit(2020, {"GREEN_FIX_1YR": 5_000.0}, date_str="2020-12-31")
    assert ok.status == "COMPLIANT"
    # MUTATE: claim 10 MWh of green supply, hold only 5 -> NON_COMPLIANT, shortfall.
    bad = auditor.audit(2020, {"GREEN_FIX_1YR": 10_000.0}, date_str="2020-12-31")
    assert bad.status == "NON_COMPLIANT"
    assert bad.shortfall_mwh > 0 and bad.penalty_estimate_gbp > 0


def test_green_claims_audit_zero_obligation_fixed(monkeypatch):
    # KL-7 FIXED (FAIL-OPEN): a zero obligation previously short-circuited to
    # COMPLIANT at 100% coverage (theatre -- broken green-product detection read
    # compliant). Now the two zero-obligation cases are distinguished:
    from company.compliance.green_claims_audit import GreenClaimsAuditor
    from company.market.rego_portfolio import RegoPortfolio
    from company.billing.tariff_products import TariffCatalogue

    # (a) OUTCOME-SAFE: no green product in use -> a genuine "no claims made" is
    #     NOT_APPLICABLE, a distinct state that is NOT "COMPLIANT".
    # BEFORE: res.status == "COMPLIANT" and res.coverage_pct == 100.0
    # AFTER : res.status == "NOT_APPLICABLE" (never a false "compliant").
    auditor = GreenClaimsAuditor(RegoPortfolio())
    na = auditor.audit(2020, {}, date_str="2020-12-31")  # no consumption
    assert na.status == "NOT_APPLICABLE"
    assert na.status != "COMPLIANT"

    # (b) FIRES: a green product IS in use (billed consumption) yet the obligation
    #     detection is broken and computes to 0 -- must fail CLOSED, not read
    #     compliant. Simulate the broken detector by forcing the REGO requirement
    #     to 0 while a real green tariff carries consumption.
    monkeypatch.setattr(TariffCatalogue, "rego_requirement_mwh",
                        staticmethod(lambda kwh, code: 0.0))
    broken = auditor.audit(2020, {"GREEN_FIX_1YR": 5000.0}, date_str="2020-12-31")
    assert broken.green_products_active > 0        # a green product WAS in use
    assert broken.obligation_mwh == 0.0            # detection produced zero obligation
    assert broken.status == "NON_COMPLIANT"        # fails closed, not compliant


# --------------------------------------------------------------------------
# tools/generate_dashboard_data.py -- page-consistency gates (R14 + population)
# --------------------------------------------------------------------------

def test_dashboard_consistency_gate_fires_on_surface_disagreement():
    import tools.generate_dashboard_data as gdd
    portfolio = {"net_margin_gbp": 100.0}
    # CORRECT: insights agree -> pass.
    assert gdd._check_consistency(portfolio, {"net_margin_gbp": 100.0}, "run.json") is True
    # MUTATE: exec-summary insights disagree with the totals -> gate fires.
    assert gdd._check_consistency(portfolio, {"net_margin_gbp": 200.0}, "run.json") is False


def test_dashboard_consistency_gate_no_insights_fixed():
    # KL-8 FIXED (FAIL-SILENT + FAIL-OPEN): the gate previously passed when its
    # comparison input was absent -- the SAME class as the R11 orphan-transition
    # incident. The pipeline guarantees run_insights.json is written immediately
    # before this gate runs, so an absent payload is a real failure.
    import tools.generate_dashboard_data as gdd
    # (a) FAIL-SILENT closed: missing/empty insights now FAILS (was True).
    # BEFORE: _check_consistency({"net_margin_gbp": 100.0}, {}, "run.json") is True
    # AFTER : it is False.
    assert gdd._check_consistency({"net_margin_gbp": 100.0}, {}, "run.json") is False
    # (b) FAIL-OPEN closed: a headline key present on one surface but missing on
    # the other is a disagreement, not a silent skip (was True).
    assert gdd._check_consistency({"net_margin_gbp": 100.0}, {"insights": []}, "run.json") is False
    # OUTCOME-SAFE: genuinely-agreeing surfaces still pass. net margin agrees on
    # both surfaces; every other headline key is absent on BOTH surfaces and is
    # legitimately not-published, so it is still skipped (not a false mismatch).
    assert gdd._check_consistency({"net_margin_gbp": 100.0}, {"net_margin_gbp": 100.0}, "run.json") is True


def test_dashboard_basis_label_gate_fires_on_unlabelled_headline_figure():
    import tools.generate_dashboard_data as gdd
    good_basis = {"clock": "settled", "provisional": True, "note": "x"}
    clean = {"net_margin_gbp": 100.0, "enterprise_value_gbp": 50.0,
             "basis": {"net_margin_gbp": good_basis, "enterprise_value_gbp": good_basis}}
    assert gdd._check_basis_labels_present(clean) is True
    # MUTATE: publish net margin with NO basis label -> R14 gate fires.
    unlabelled = {"net_margin_gbp": 100.0, "basis": {}}
    assert gdd._check_basis_labels_present(unlabelled) is False


def test_dashboard_population_consistency_gate_fires_on_book_size_divergence():
    import tools.generate_dashboard_data as gdd
    data = {"years": {"2025": {"active_customer_ids": ["Z1", "Z2"]}}}
    clean = {"customers": {"book_annual": [{"active_elec": 2, "active_gas": 0}]}, "opex_ledger": {}}
    assert gdd._check_population_consistency(data, clean) is True
    # MUTATE: the pulse-strip Book Size no longer reconciles to its source pop.
    broken = {"customers": {"book_annual": [{"active_elec": 5, "active_gas": 0}]}, "opex_ledger": {}}
    assert gdd._check_population_consistency(data, broken) is False


# --------------------------------------------------------------------------
# background/health_check.py -- the stack health control
# --------------------------------------------------------------------------

def test_health_check_fires_on_a_missing_daemon(monkeypatch):
    import background.health_check as hc
    present = {s: "python" for s in hc.EXPECTED_PANES if s != "supervisor"}
    monkeypatch.setattr(hc, "_tmux_panes", lambda: present)
    monkeypatch.setattr(hc, "_running_scripts", lambda: [])
    monkeypatch.setattr(hc, "_check_pixel_verification_capability", lambda: None)
    monkeypatch.setattr(hc, "_check_stale_running_code", lambda: None)
    monkeypatch.setattr(hc, "_check_staging_age", lambda: None)
    monkeypatch.setattr(hc, "_check_stale_dependencies", lambda: None)
    all_ok, ok, problems = hc.run_health_check()
    assert all_ok is False
    assert any("supervisor" in p and "NOT RUNNING" in p for p in problems)


def test_health_check_fails_closed_when_process_inspection_unavailable(monkeypatch):
    # FAIL-SILENT audit (the key R15 property): if tmux AND ps both fail (return
    # empty) the checker itself is effectively unavailable. It must ALARM (read
    # every daemon as NOT RUNNING -> DEGRADED), never read clean. Proven here.
    import background.health_check as hc
    monkeypatch.setattr(hc, "_tmux_panes", lambda: {})
    monkeypatch.setattr(hc, "_running_scripts", lambda: [])
    monkeypatch.setattr(hc, "_check_pixel_verification_capability", lambda: None)
    monkeypatch.setattr(hc, "_check_stale_running_code", lambda: None)
    monkeypatch.setattr(hc, "_check_staging_age", lambda: None)
    monkeypatch.setattr(hc, "_check_stale_dependencies", lambda: None)
    all_ok, ok, problems = hc.run_health_check()
    assert all_ok is False
    assert len(problems) >= len(hc.EXPECTED_PANES)  # every daemon flagged, none silently clean


def test_health_check_stale_running_code_fires_on_process_older_than_its_script(monkeypatch):
    from datetime import datetime as _dt
    import background.health_check as hc
    # MUTATE: the supervisor process 'started' in the year 2000 -- long before its
    # own (freshly-checked-out) script file was last modified -> stale, fires.
    monkeypatch.setattr(hc, "_process_start_times_by_script",
                        lambda: {"supervisor.py": _dt(2000, 1, 1)})
    assert hc._check_stale_running_code() is not None
    # CORRECT: a process started in the future is newer than its script -> clean.
    monkeypatch.setattr(hc, "_process_start_times_by_script",
                        lambda: {"supervisor.py": _dt(2100, 1, 1)})
    assert hc._check_stale_running_code() is None


# --------------------------------------------------------------------------
# background/process_run_complete.py -- the change-detection (dedup) gate
# --------------------------------------------------------------------------

def test_change_detection_fingerprint_is_sensitive_to_meaningful_change():
    # The dedup gate skips a run whose fingerprint MATCHES the last processed one.
    # For that to be safe, a meaningful business change MUST flip the fingerprint,
    # or a real change is silently withheld from the live site (the R11 incident
    # class). Prove the fingerprint moves on a net-margin change.
    import background.process_run_complete as prc
    base = {"total_net_gbp": 1000.0, "bills_total": 10}
    fp1 = prc._run_fingerprint(base)
    fp2 = prc._run_fingerprint({**base, "total_net_gbp": 2000.0})
    assert fp1 != fp2
    # An administration event is always distinguishable (never dedup-skipped).
    assert prc._run_fingerprint({**base, "administration_event": True})["administration_event"] is True


def test_change_detection_read_last_fingerprint_fails_closed_on_corruption(monkeypatch, tmp_path):
    # FAIL-CLOSED audit: if the gate's own memory (last-fingerprint file) is
    # corrupt/unreadable, it must return None so the run is PROCESSED (not
    # silently skipped by a spurious match). An unavailable dedup-memory must
    # never manufacture a skip.
    import background.process_run_complete as prc
    corrupt = tmp_path / "fp.json"
    corrupt.write_text("{not valid json")
    monkeypatch.setattr(prc, "LAST_FINGERPRINT_FILE", corrupt)
    assert prc._read_last_fingerprint() is None
    missing = tmp_path / "nope.json"
    monkeypatch.setattr(prc, "LAST_FINGERPRINT_FILE", missing)
    assert prc._read_last_fingerprint() is None


# --------------------------------------------------------------------------
# LLM-judge evaluators -- what is HONESTLY testable (structure, not judgement)
# --------------------------------------------------------------------------

def test_llm_judge_evaluators_are_structurally_read_only():
    """The phase-close-evaluator and epistemic-verifier AGENTS are LLM judges --
    their verdict quality cannot be deterministically mutation-tested here (no
    fixed prompt->NEEDS_WORK oracle). What IS testable, and matters, is the
    STRUCTURAL guarantee that a judge cannot 'fix' its way to a PASS: its agent
    definition must grant it NO Write/Edit/NotebookEdit tools. A grader that can
    mutate the thing it grades is theatre. This asserts that invariant; the
    judgement layer itself is documented as not-mutation-testable in the kill
    list, not counted as covered."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    for name in ("phase-close-evaluator", "epistemic-verifier"):
        path = os.path.join(root, ".claude", "agents", f"{name}.md")
        with open(path) as fh:
            head = fh.read()[:600].lower()
        tools_line = next((ln for ln in head.splitlines() if ln.startswith("tools:")), "")
        assert tools_line, f"{name}: no tools: frontmatter line found"
        for forbidden in ("write", "edit", "notebookedit"):
            assert forbidden not in tools_line, \
                f"{name} grants '{forbidden}' -- a judge that can mutate what it grades is theatre"


# --------------------------------------------------------------------------
# Registry integrity -- the kill list must stay honest / in sync
# --------------------------------------------------------------------------

def test_control_registry_is_wellformed_and_in_sync():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, "docs/design/control_registry.json")) as fh:
        reg = json.load(fh)
    controls = reg["controls"]
    assert controls, "empty registry"
    valid = {"FIRED", "THEATRE", "DID-NOT-FIRE", "STRUCTURAL-ONLY"}
    for c in controls:
        assert c["result"] in valid, f"{c['id']} has invalid result {c['result']}"
        assert c["location"] and c["catches"] and c["mutation"]
    # The flagship tautology must remain recorded as THEATRE -- if a future
    # refactor 'fixes' check_vat into looking like it fires, this guards against
    # quietly relabelling a known tautology as a real control.
    vat = next(c for c in controls if c["id"] == "check_vat_arithmetic")
    assert vat["result"] == "THEATRE"
    assert vat["killer_pattern_audit"] == "TAUTOLOGY"


def test_fixed_theatre_controls_are_registered_in_the_killlist():
    """The two director-named THEATRE controls fixed 2026-07-14 (the deadman
    meaningful-liveness FAIL-OPEN and the claim-evidence-hook TAUTOLOGY) MUST
    appear in the kill list as FIRED and resolve to their real source + mutation
    test -- so the kill list rendered on the Proof door stays HONEST and current.
    A FIRED result is only permitted here because a real mutation test proves each
    fires on its own named defect (asserted below by locating those tests)."""
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    with open(os.path.join(root, "docs/design/control_registry.json")) as fh:
        controls = json.load(fh)["controls"]
    by_id = {c["id"]: c for c in controls}

    expected = {
        "deadman_meaningful_liveness": {
            "src": "background/deadmans_switch.py",
            "audit_contains": "FAIL-OPEN",
            "catch_contains": "auto-process no-op commits masking executor idle",
            "test_file": "tests/background/test_deadmans_switch.py",
            "test_name": "test_flat_auto_process_commits_do_not_refresh_liveness",
        },
        "claim_evidence_hook": {
            "src": ".claude/hooks/block_unevidenced_claim.py",
            "audit_contains": "TAUTOLOGY",
            "catch_contains": "not backed by an on-origin SHA",
            "test_file": "tests/tools/test_claude_hooks.py",
            "test_name": "test_blocks_claim_citing_sha_not_on_origin",
        },
    }
    for cid, exp in expected.items():
        assert cid in by_id, f"{cid} missing from the kill list"
        c = by_id[cid]
        # A FIRED result is only honest if the source, the mutation test, and the
        # named test function all really exist -- no fabricated FIRED.
        assert c["result"] == "FIRED", f"{cid} not FIRED"
        assert exp["src"] in c["location"], f"{cid} location does not cite {exp['src']}"
        assert exp["audit_contains"] in c["killer_pattern_audit"], f"{cid} wrong killer pattern"
        assert exp["catch_contains"] in c["catches"], f"{cid} catch clause drifted"
        assert exp["test_name"] in c["mutation"], f"{cid} does not reference its mutation test"
        # The referenced mutation test must actually exist on disk (resolves).
        test_path = os.path.join(root, exp["test_file"])
        assert os.path.exists(test_path), f"{cid} references a missing test file {exp['test_file']}"
        with open(test_path) as fh:
            body = fh.read()
        assert f"def {exp['test_name']}" in body, \
            f"{cid} references {exp['test_name']} but it is not defined in {exp['test_file']}"


# ==========================================================================
# PASS 3 (H12 L2->L3): the epistemic-verifier's OWN coverage gaps (KL-2) and
# the deterministic COMPLIANCE ACCUMULATOR-REGISTER TAIL.
# CONTROLS_THAT_CANNOT_FAIL.md -- the verifier is itself a control, and it had
# two killer-pattern gaps of its own (fail-silent on a missing file it was
# asked to check; fail-open on any SIM import the line-anchored regex did not
# match: stray whitespace, a bare `import simulation`, a same-line compound
# import). The registers below are governance controls (FCA Fair Value, board
# quorum, LPCDCA statutory-interest lawfulness) not yet mutation-tested. Same
# doctrine: inject each control's named defect and assert it FIRES; audit each
# for TAUTOLOGY / FAIL-OPEN / FAIL-SILENT, asserting documented
# not-applicable/degrade branches explicitly so the kill list can cite them.
# ==========================================================================

# --------------------------------------------------------------------------
# tools/epistemic_verifier.py -- KL-2: the verifier's own killer-pattern gaps
# --------------------------------------------------------------------------

def _scan_src(src):
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "m.py")
        with open(p, "w") as fh:
            fh.write(src)
        return ev._scan_file(p)


def test_verifier_fires_on_whitespace_and_bare_sim_import_forms():
    # KL-2 FAIL-OPEN FIXED: the line-anchored regex only matched exact
    # `from simulation.` / `import simulation.` at line start. Any variant the
    # AST now catches used to read CLEAN (theatre). Each MUST fire.
    # (a) stray double-space after the keyword.
    assert len(_scan_src("from  simulation.weather_engine import temperature\n")) == 1
    # (b) bare package import with no dotted tail (`import simulation`).
    assert len(_scan_src("import simulation\n")) == 1
    assert len(_scan_src("import sim\n")) == 1
    # (c) a compound same-physical-line import -- never at a matchable line start.
    assert len(_scan_src("import os; import simulation.weather_engine\n")) == 1
    # (d) an aliased import.
    assert len(_scan_src("import simulation.weather_engine as we\n")) == 1
    # (e) an import nested inside a function body (indented, deferred).
    assert len(_scan_src("def f():\n    from simulation.var import x\n    return x\n")) == 1


def test_verifier_does_not_false_fire_on_lookalike_names():
    # OUTCOME-SAFE: the approved seam, and modules that merely START with the
    # forbidden letters but are different packages, must NOT fire.
    assert _scan_src("from company.interfaces.sim_interface import get_market_price\n") == []
    assert _scan_src("import simplejson\n") == []            # not the `sim` package
    assert _scan_src("from similarity import score\n") == []  # not `sim.`
    # The approved orchestration modules remain exempt (structural, not epistemic).
    assert _scan_src("from simulation.run_segments import run\n") == []
    assert _scan_src("import simulation.run_phase4c_on_phase2b\n") == []


def test_verifier_missing_file_alarms_not_clean():
    # KL-2 FAIL-SILENT FIXED: a file the verifier was ASKED to scan but cannot
    # read previously returned [] -- read as a clean PASS (theatre: an
    # unavailable check manufacturing confidence). It must now surface a
    # check_unavailable finding so the overall scan cannot silently pass.
    # BEFORE: ev._scan_file("/no/such/file.py") == []   (fail-silent clean)
    # AFTER : it returns a check_unavailable finding.
    findings = ev._scan_file("/no/such/directory/nope.py")
    assert findings and findings[0].get("kind") == "check_unavailable"
    # The finding carries the keys _format_report needs (no KeyError on report).
    for key in ("file", "line", "code", "description", "why"):
        assert key in findings[0]
    # An unparseable-but-readable file still gets inspected via the regex
    # fallback rather than skipped -- a broken file is not silently clean.
    assert _scan_src("def (:\n") is not None  # returns a list, not a crash


def test_verifier_syntaxerror_fallback_still_catches_the_import():
    # A file with a genuine syntax error further down must STILL have its
    # forbidden import caught by the line-regex fallback (unparseable != clean).
    src = "from simulation.weather_engine import temperature\ndef (:\n"
    assert len(_scan_src(src)) >= 1


# --------------------------------------------------------------------------
# W4_2_verifier_timing_extension KL-2b: dynamic-import bypass (the AST scan
# only walked ast.Import/ast.ImportFrom nodes -- a literal-string dynamic
# import via importlib.import_module()/__import__() smuggled a forbidden
# module name straight past it, a FAIL-OPEN gap of the same class KL-2
# already fixed for literal import syntax). Same doctrine: inject the exact
# defect (a dynamic SIM import), assert it now FIRES; confirm it did NOT fire
# before this fix by asserting on the OLD ast.Import/ImportFrom-only path.
# --------------------------------------------------------------------------

def test_verifier_fires_on_dynamic_import_of_sim_internals():
    # MUTATE: a company/ file smuggling a forbidden SIM import through
    # importlib.import_module()/__import__() instead of a literal statement.
    assert len(_scan_src('importlib.import_module("simulation.weather_engine")\n')) == 1
    assert len(_scan_src('importlib.import_module("sim.x")\n')) == 1
    assert len(_scan_src('__import__("simulation.weather_engine")\n')) == 1
    assert len(_scan_src('__import__("sim")\n')) == 1
    # The bare `from importlib import import_module` call form must fire too.
    assert len(_scan_src(
        'from importlib import import_module\n'
        'import_module("simulation.weather_engine")\n'
    )) == 1
    # Nested inside a function body (deferred/local dynamic import).
    assert len(_scan_src(
        'def f():\n    return importlib.import_module("simulation.var")\n'
    )) == 1


def test_verifier_dynamic_import_pre_fix_baseline_did_not_fire():
    # PROVES the control could fail before this pass: the OLD detection path
    # (only ast.Import/ast.ImportFrom nodes -- exactly what _scan_source did
    # prior to this fix) does not see a Call node at all, so it silently
    # cleared a real bypass. This pins the regression so the fix cannot
    # silently erode back to fail-open.
    src = 'importlib.import_module("simulation.weather_engine")\n'
    tree = ev.ast.parse(src)
    old_path_modules = []
    for node in ev.ast.walk(tree):
        if isinstance(node, ev.ast.Import):
            old_path_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ev.ast.ImportFrom) and node.level == 0:
            old_path_modules.append(node.module)
    assert old_path_modules == []  # the pre-fix scan found no import to check
    # ... while the current, fixed scan correctly fires on the same source.
    assert len(_scan_src(src)) == 1


def test_verifier_dynamic_import_does_not_false_fire_on_lookalikes_or_variables():
    # OUTCOME-SAFE: lookalike package names, the approved seam/orchestration,
    # ordinary non-SIM dynamic imports, and a non-literal (unresolvable)
    # target must NOT fire -- a control that flags everything is as useless
    # as one that flags nothing.
    assert _scan_src('importlib.import_module("simplejson")\n') == []
    assert _scan_src('importlib.import_module("similarity")\n') == []
    assert _scan_src('importlib.import_module("simulation.run_segments")\n') == []
    assert _scan_src('importlib.import_module("company.interfaces.sim_interface")\n') == []
    assert _scan_src('__import__("os")\n') == []
    # A non-literal target cannot be resolved statically -- documented
    # heuristic limit, not a claimed detection.
    assert _scan_src('importlib.import_module(some_variable)\n') == []


def test_verifier_dynamic_import_syntaxerror_fallback_still_catches_it():
    # The regex fallback (unparseable file) must ALSO catch a dynamic import,
    # not just the AST-primary path -- matching the existing literal-import
    # fallback discipline (an unparseable file must not silently read clean).
    src = 'importlib.import_module("simulation.weather_engine")\ndef (:\n'
    findings = _scan_src(src)
    assert len(findings) >= 1
    assert any("Dynamic import" in f["description"] for f in findings)


# --------------------------------------------------------------------------
# segment_debt_policy.py -- the LPCDCA Tier-1 lawfulness control
# --------------------------------------------------------------------------

from datetime import date as _date
from company.compliance import segment_debt_policy as sdp


def test_debt_terms_control_fires_on_unlawful_domestic_interest():
    as_of = _date(2022, 3, 1)
    # CORRECT: a domestic account with neither interest nor a late charge passes.
    clean = {"interest_applied": False, "late_charge_applied": False}
    assert sdp.check_debt_terms_lawful_for_segment("resi", clean, as_of) is True
    # MUTATE: LPCDCA statutory interest charged to a DOMESTIC account is unlawful.
    assert sdp.check_debt_terms_lawful_for_segment(
        "resi", {"interest_applied": True, "late_charge_applied": False}, as_of) is False
    # MUTATE: a late-payment CHARGE on a domestic account is unlawful.
    assert sdp.check_debt_terms_lawful_for_segment(
        "resi", {"interest_applied": False, "late_charge_applied": True}, as_of) is False


def test_debt_terms_control_fires_on_wrong_statutory_rate_for_business():
    as_of = _date(2022, 3, 1)  # H1 2022 -> base 0.25% -> statutory 8.25%
    expected = sdp.statutory_interest_rate(as_of)
    assert expected is not None
    # CORRECT: business interest at exactly the statutory rate is lawful.
    ok = {"interest_applied": True, "late_charge_applied": False, "interest_rate": expected}
    assert sdp.check_debt_terms_lawful_for_segment("sme", ok, as_of) is True
    # MUTATE: over-charging interest (wrong statutory rate) FIRES.
    wrong = {"interest_applied": True, "late_charge_applied": False,
             "interest_rate": expected + 0.05}
    assert sdp.check_debt_terms_lawful_for_segment("sme", wrong, as_of) is False


def test_debt_terms_control_fails_closed_on_missing_or_unrecognised_input():
    as_of = _date(2022, 3, 1)
    # FAIL-CLOSED audit: an unrecognised segment must HELD (False), not pass.
    ok_payload = {"interest_applied": False, "late_charge_applied": False}
    assert sdp.check_debt_terms_lawful_for_segment("banana", ok_payload, as_of) is False
    # FAIL-CLOSED: a malformed / missing applied payload must HELD.
    assert sdp.check_debt_terms_lawful_for_segment("resi", None, as_of) is False
    assert sdp.check_debt_terms_lawful_for_segment("resi", {"interest_applied": True}, as_of) is False
    # FAIL-CLOSED: business interest applied but the rate cannot be priced
    # (a date outside the anchored 2016-2025 statutory history) must HELD, never
    # guess -- an unverifiable control is a failed control.
    out_of_range = _date(2035, 1, 1)
    assert sdp.statutory_interest_rate(out_of_range) is None
    assert sdp.check_debt_terms_lawful_for_segment(
        "sme", {"interest_applied": True, "late_charge_applied": False, "interest_rate": 0.0825},
        out_of_range) is False


def test_canonical_segment_raises_on_the_mislabel_class():
    # INDEPENDENCE / R10: an unknown segment spelling must RAISE, never silently
    # default to domestic (the SME-as-Household mislabel class this guards).
    import pytest as _pytest
    with _pytest.raises(ValueError):
        sdp.canonical_segment("household-ish")
    with _pytest.raises(ValueError):
        sdp.canonical_segment(None)


# --------------------------------------------------------------------------
# fair_value_assessment_register.py -- FCA Consumer Duty fair-value control
# --------------------------------------------------------------------------

from company.compliance.fair_value_assessment_register import (
    FairValueAssessmentRegister, ProductCategory, FairValueOutcome,
)


def test_fair_value_register_fires_on_poor_value_and_overdue_review():
    reg = FairValueAssessmentRegister()
    fair = reg.create_assessment(
        product_id="P_fair", product_category=ProductCategory.STANDARD_VARIABLE,
        assessment_date=_date(2024, 1, 1), outcome=FairValueOutcome.FAIR_VALUE,
        cost_to_serve_gbp_pa=100.0, revenue_per_customer_gbp_pa=200.0, customer_count=10)
    poor = reg.create_assessment(
        product_id="P_poor", product_category=ProductCategory.STANDARD_VARIABLE,
        assessment_date=_date(2022, 1, 1), outcome=FairValueOutcome.POOR_VALUE,
        cost_to_serve_gbp_pa=190.0, revenue_per_customer_gbp_pa=200.0, customer_count=10)
    # MUTATE: a poor-value product must surface (the whole point of the register).
    assert [r.product_id for r in reg.poor_value_products()] == ["P_poor"]
    assert poor.is_poor_value is True and fair.is_poor_value is False
    # MUTATE: an assessment older than the 12-month review cycle is OVERDUE.
    as_of = _date(2024, 6, 1)
    overdue_ids = {r.product_id for r in reg.overdue_reviews(as_of)}
    assert "P_poor" in overdue_ids       # assessed 2022 -> long overdue, fires
    assert "P_fair" not in overdue_ids   # assessed 2024-01 -> within the cycle


def test_fair_value_register_create_rejects_impossible_economics():
    # FAIL-CLOSED audit: negative cost/revenue/customer counts are absurd inputs
    # and must RAISE, never be silently recorded (a corrupt assessment would
    # poison every downstream fair-value rate).
    import pytest as _pytest
    reg = FairValueAssessmentRegister()
    with _pytest.raises(ValueError):
        reg.create_assessment("P", ProductCategory.STANDARD_VARIABLE, _date(2024, 1, 1),
                              FairValueOutcome.FAIR_VALUE, -1.0, 200.0, 10)
    with _pytest.raises(ValueError):
        reg.create_assessment("P", ProductCategory.STANDARD_VARIABLE, _date(2024, 1, 1),
                              FairValueOutcome.FAIR_VALUE, 100.0, 200.0, -5)


def test_fair_value_compliance_rate_empty_is_none_not_false_hundred_percent():
    # FAIL-SILENT audit (same class as KL-5): an EMPTY register must NOT report
    # a compliant-looking 100%. It returns None (not-assessed), a distinct state
    # that a caller cannot mistake for compliance.
    reg = FairValueAssessmentRegister()
    assert reg.fair_value_compliance_rate_pct() is None
    # OUTCOME-SAFE: a populated all-fair register reads a genuine 100%.
    reg.create_assessment("P", ProductCategory.STANDARD_VARIABLE, _date(2024, 1, 1),
                          FairValueOutcome.FAIR_VALUE, 100.0, 200.0, 10)
    assert reg.fair_value_compliance_rate_pct() == 100.0


# --------------------------------------------------------------------------
# board_meeting_register.py -- governance quorum control
# --------------------------------------------------------------------------

from company.compliance.board_meeting_register import (
    BoardMeetingRegister, MeetingType, MeetingStatus,
)


def test_board_quorum_control_fires_when_too_few_directors_attend():
    reg = BoardMeetingRegister()
    m = reg.schedule(MeetingType.BOARD, _date(2024, 3, 1), directors_total=6)
    # CORRECT: 3 of 6 present meets the >=50% quorum -> HELD, quorum_met True.
    held = reg.record_held(m.meeting_id, directors_present=3, resolutions=[])
    assert held.status == MeetingStatus.HELD
    assert held.quorum_met is True
    # MUTATE: only 2 of 6 present -> quorum FAILS, the meeting is not validly held.
    m2 = reg.schedule(MeetingType.BOARD, _date(2024, 6, 1), directors_total=6)
    failed = reg.record_held(m2.meeting_id, directors_present=2, resolutions=[])
    assert failed.status == MeetingStatus.QUORUM_FAILED
    assert failed.quorum_met is False
    assert failed.was_held is False


def test_board_quorum_fails_closed_on_zero_directors():
    # FAIL-CLOSED audit: a meeting with zero directors on the board (or none
    # present) can never meet quorum -- quorum_met must be False, not a
    # divide-by-zero or a vacuous True.
    reg = BoardMeetingRegister()
    m = reg.schedule(MeetingType.EMERGENCY, _date(2024, 3, 1), directors_total=0)
    rec = reg.record_held(m.meeting_id, directors_present=0, resolutions=[])
    assert rec.quorum_met is False
