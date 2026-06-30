# Phase HK: BSC Performance Assurance Register

**Proposed:** 2026-06-30
**Target file:** company/market/bsc_performance_assurance_register.py
**Estimated tests:** 28-34
**Connects to:** dadc_contract_register (CV), mop_appointment_register (HJ), bsc_settlement_run_register (DH), mpas_standing_data_correction_register (HB)

## What it models

BSC Section M Performance Assurance (PA) framework. Every market participant
(supplier, DA, DC, MOP) submits quarterly PA assessments to Elexon, which scores
them against six data quality metrics and assigns a tier: Standard, Watch, or
Formal Action. Watch/Formal Action triggers a Remedial Action Plan (RAP) within 20WD.
Formal Action can result in agent suspension -- settlement risk for all MPANs under that agent.

Phase CV (DA/DC appointment) and Phase HJ (MOP appointment) model who the agents are.
Phase HK adds how well they're performing -- the quarterly compliance loop Elexon enforces.

## Enums

PAAgentType: SUPPLIER / DATA_AGGREGATOR / DATA_COLLECTOR / METER_OPERATOR
PAMetric: MISSING_READS / LATE_DATA_FLOWS / ERRONEOUS_READS / UNRECONCILED_VOLUMES / DATA_SUBSTITUTION_RATE / FLOW_REJECTION_RATE
PAAssessmentTier: STANDARD / WATCH / FORMAL_ACTION
PAStatus: OPEN / SUBMITTED / ACCEPTED / RAP_REQUIRED / RAP_IN_PROGRESS / RAP_CLOSED

## Dataclasses

PAMetricScore (frozen): metric; score_pct; threshold_pct; is_breached (score<threshold);
  severity HIGH (<50% of threshold) / MEDIUM (50-90%) / LOW (90-100%)

PAAssessmentRecord (frozen): assessment_id (auto PA-00001...); agent_type; agent_name;
  quarter_year; quarter_number (1-4); quarter_label property "Q{n}/{year}";
  assessment_date; metric_scores tuple; tier (0 breaches=STANDARD, 1-2=WATCH, 3+=FORMAL_ACTION);
  status; rap_required (tier != STANDARD); rap_due_date (+20WD if rap_required else None);
  is_rap_overdue(as_of) False when not required or RAP_CLOSED;
  breached_metrics property; overall_pass_rate_pct property; assessment_summary property

## Register: BSCPerformanceAssuranceRegister

Mutations (invalid transitions raise ValueError):
  record_assessment(agent_type, agent_name, quarter_year, quarter_number, assessment_date, metric_scores)
  submit_assessment(assessment_id)  OPEN -> SUBMITTED
  accept_assessment(assessment_id)  SUBMITTED -> ACCEPTED or RAP_REQUIRED
  raise_rap(assessment_id)          RAP_REQUIRED -> RAP_IN_PROGRESS
  close_rap(assessment_id)          RAP_IN_PROGRESS -> RAP_CLOSED

Queries:
  assessments_for_agent(agent_name)
  current_tier_for_agent(agent_name, as_of) -- latest accepted assessment
  agents_on_watch  -> list[str]
  agents_on_formal_action -> list[str]
  overdue_raps(as_of)
  quarterly_summary(year, quarter) -> dict with tier counts
  pa_register_summary

## Domain facts / calibration

- BSC Section M: Performance Assurance (Elexon SA subsidiary document)
- Quarterly: assessments due within 30 calendar days of quarter end
- Thresholds: MISSING_READS>=97%; LATE_DATA_FLOWS>=95%; ERRONEOUS_READS>=99%;
  UNRECONCILED_VOLUMES>=98%; DATA_SUBSTITUTION_RATE<=5% (score=100-subst_pct, threshold=95);
  FLOW_REJECTION_RATE>=97%
- Tier: 0 breaches=STANDARD; 1-2=WATCH; 3+=FORMAL_ACTION
- RAP: 20WD from assessment acceptance
- Formal Action: Elexon can suspend agent -> settlement risk for all MPANs under that agent
- Epistemic: company observes own agents' PA scores; Elexon public PA reports for market intelligence
- Distinct from: dadc_contract_register.py (appointment), bsc_settlement_dispute_register.py (disputes),
  mpas_standing_data_correction_register.py (standing data quality)
