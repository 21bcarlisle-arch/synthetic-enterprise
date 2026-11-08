# ARCHIVED LEGS of tests/controls/test_control_mutation.py (archive increment 3b). The tests here reach a module
# under archive/unhooked_supplier/; the live legs stay at tests/controls/test_control_mutation.py.
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
    check_bill_foots,
    check_bill_line_items_non_negative,
    check_bill_period_sane,
)
from company.billing.back_billing import BackBillingAssessment, BackBillingReason
from company.billing.pre_bill_validation import validate_bill
from company.compliance import obligations_register as orr
import tools.epistemic_verifier as ev


# --------------------------------------------------------------------------
# domain_invariants.py -- the invariant library
# --------------------------------------------------------------------------









# --------------------------------------------------------------------------
# The flagship TAUTOLOGY -- vat_by_segment
# --------------------------------------------------------------------------







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








# --------------------------------------------------------------------------
# F6_bill_integrity_structural -- the three Tier-1 STRUCTURAL controls
# (arithmetic footing, non-negativity/fail-CLOSED, temporal sanity). These are
# load-bearing evidence for F6 at L2 but were absent from this central kill-list
# apparatus until the 2026-07-16 F6 HARDEN pass -- registered here so R15's "no
# control counts unless a mutation test proves it fires" holds for them too.
# --------------------------------------------------------------------------

def _foot_bill(**overrides):
    b = dict(_bill())
    b["total_amount_gbp"] = 74.03  # 44.55 + 16.65 + 9.30 + 3.53
    b.update(overrides)
    return b


















# --------------------------------------------------------------------------
# obligations_register.py -- risk tiering (classifier)
# --------------------------------------------------------------------------









# --------------------------------------------------------------------------
# epistemic_verifier.py -- SIM/company wall scanner
# --------------------------------------------------------------------------







# --------------------------------------------------------------------------
# epistemic_verifier.py -- SEAM-FILE SEGMENT-LABEL GUARD (D-SEGMENT,
# SEGMENTATION_GENERATOR_BUILD_PLAN.md step 5). R15 mutation test: the guard
# must FIRE on a deliberately-planted violation (a company module -- here,
# the seam file itself -- exposing a SIM cohort label/attitude/sensitivity)
# and PASS on the clean, real module.
# --------------------------------------------------------------------------





















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
















# --------------------------------------------------------------------------
# consumer_duty.py -- FCA Consumer Duty RAG aggregator
# --------------------------------------------------------------------------

def _duty_assessment(outcome, rag, date="2024-01-01"):
    return OutcomeAssessment(
        outcome=outcome, assessment_date=date, rag=rag,
        metric_value=1.0, metric_name="m", narrative="n",
    )






# --------------------------------------------------------------------------
# social_obligation_register.py -- mandatory social spend
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# crisis_bad_debt_validator.py -- anchored crisis step-up diagnostic
# --------------------------------------------------------------------------







# --------------------------------------------------------------------------
# green_claims_audit.py -- REGO coverage vs green marketing claims
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# tools/generate_dashboard_data.py -- page-consistency gates (R14 + population)
# --------------------------------------------------------------------------

# RETIRED 2026-08-20, and this is the record of it rather than a silent shrink.
# `_check_consistency` (dashboard totals vs run_insights.json) was deleted from the module
# in 03dd8c49e: the fold deleted every page that fetched the second surface, so the two
# things it kept consistent were both unreachable. Its two mutation tests lived HERE and
# were the one consumer that retirement missed -- they went red at import-time
# (AttributeError) and wedged the publish gate for 13 consecutive runs.
#
# The invariant they used to carry has NOT gone unheld: the control must never come back,
# and three assertions now say so -- test_publish_blockers_guard_a_reachable_page.py::
# test_the_retired_exec_summary_comparison_is_not_declared (both `not in
# PUBLISH_VERDICT_CHECKS` and `not hasattr`) and test_website_integrity_fix.py:328.
# What the publish verdict IS now is a two-check conjunction, and both are mutation-tested
# below: _check_population_consistency and _check_front_door_segment_claim.








# --------------------------------------------------------------------------
# background/health_check.py -- the stack health control
# --------------------------------------------------------------------------







# --------------------------------------------------------------------------
# background/process_run_complete.py -- the change-detection (dedup) gate
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# LLM-judge evaluators -- what is HONESTLY testable (structure, not judgement)
# --------------------------------------------------------------------------



# --------------------------------------------------------------------------
# Registry integrity -- the kill list must stay honest / in sync
# --------------------------------------------------------------------------





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










# --------------------------------------------------------------------------
# W4_2_verifier_timing_extension KL-2b: dynamic-import bypass (the AST scan
# only walked ast.Import/ast.ImportFrom nodes -- a literal-string dynamic
# import via importlib.import_module()/__import__() smuggled a forbidden
# module name straight past it, a FAIL-OPEN gap of the same class KL-2
# already fixed for literal import syntax). Same doctrine: inject the exact
# defect (a dynamic SIM import), assert it now FIRES; confirm it did NOT fire
# before this fix by asserting on the OLD ast.Import/ImportFrom-only path.
# --------------------------------------------------------------------------









# --------------------------------------------------------------------------
# segment_debt_policy.py -- the LPCDCA Tier-1 lawfulness control
# --------------------------------------------------------------------------

from datetime import date as _date
from company.compliance import segment_debt_policy as sdp










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


# ==========================================================================
# PASS 6 (B2_opex_cost_to_serve HARDEN, L3->L3, 2026-07-16): the three Tier-1
# COMMERCIAL controls of the B2 cost-to-serve taxonomy. These are load-bearing
# solvency/cross-subsidy-visibility controls (director-set real risk-appetite
# numbers, 2026-07-10) but had firing tests ONLY in their own atom test files,
# never in THIS central mutation-test apparatus -- the same R15 honesty gap the
# F6 pass (2026-07-16) closed for the structural bill controls. Registered +
# mutation-tested here so "no control counts unless a mutation test proves it
# fires on its own named defect" holds centrally for them too. Red-teaming them
# found + FIXED one real FAIL-OPEN (the empty/all-loss-making concentration
# false-green, below).
# ==========================================================================

from company.risk.concentration_risk import (
    ConcentrationSnapshot, ConcentrationDimension,
    build_gross_margin_concentration_snapshot, gross_margin_concentration_check,
)
from company.finance.segment_capital import (
    SegmentROCEHistory, segments_under_hurdle, decision_artefacts_needed,
)


# --------------------------------------------------------------------------
# concentration_risk.py -- single-customer gross-margin concentration limit
# (director risk-appetite: RED >15%, AMBER >10%)
# --------------------------------------------------------------------------









# --------------------------------------------------------------------------
# concentration_risk.py -- the Ofgem single-entity HHI cap (20%)
# --------------------------------------------------------------------------





# --------------------------------------------------------------------------
# segment_capital.py -- the ROCE-hurdle persistent-underperformance control
# (director hurdle: 12% pre-tax; cross-subsidy must be visible + decided)
# --------------------------------------------------------------------------







