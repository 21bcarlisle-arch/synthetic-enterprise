Phase 301 -- Erroneous Transfer Register

Status: PROPOSED (2026-06-26T21:30Z)
4h opt-out window: expires 2026-06-27T01:30Z

Context:
Phase 300 (Regulatory Compliance Dashboard) closed the milestone for the regulatory layer.
The next authentic gap is the Erroneous Transfer (ET) register. Under Ofgem SLC P14 /
Retail Energy Code (REC) Schedule 19, every UK supplier must track switches where the
wrong customer supply point was transferred. ET claims must be resolved within 20 working
days; failure triggers mandatory 30 GBP compensation. Ofgem benchmarks ET rate < 0.1% of
switches -- suppliers above this trigger compliance review.

ET resolution connects directly to:
- cos_process.py (Ph298): the switching process that can go wrong
- supply_point_register.py (Ph299): the MPAN/MPRN register identifies correct supply point
- regulatory_dashboard.py (Ph300): ET rate is a consumer protection compliance metric

Goal:
Add company/market/erroneous_transfer.py -- a register that tracks ET claims from
identification through investigation to resolution or compensation.

Design:
- company/market/erroneous_transfer.py (new):
  ETStatus (OPEN/INVESTIGATING/RESOLVED_CORRECTED/RESOLVED_ACCEPTED/COMPENSATION_DUE/CLOSED)
  ETResolutionType (RETURNED_TO_ORIGINAL/CUSTOMER_ACCEPTED_GAIN/WITHDRAWN)
  frozen ETClaim (claim_id/mpan/affected_account_id/claim_date/original_supplier/
    gaining_supplier/status/resolution_date/resolution_type;
    working_days_open/is_overdue [>20 working days]/compensation_gbp [30 GBP if overdue])
  ErroneousTransferRegister (raise_claim/update_status/resolve_claim/open_claims/
    overdue_claims/et_rate_pct/compensation_outstanding_gbp/claims_by_status/et_summary)

- tests/company/market/test_erroneous_transfer.py (~12 tests):
  - ETClaim is frozen
  - working_days_open counts Mon-Fri only (skips weekends)
  - is_overdue True when working_days_open > 20
  - compensation_gbp = 30.0 when overdue and unresolved, 0.0 when closed on time
  - raise_claim adds to register, appears in open_claims
  - update_status transitions correctly
  - overdue_claims filters to unresolved claims past 20 working days
  - et_rate_pct = claims / total_switches * 100
  - compensation_outstanding_gbp sums all overdue unresolved claims
  - ET rate above 0.1% is flagged in summary
  - RESOLVED_CORRECTED vs RESOLVED_ACCEPTED distinction tracked
  - et_summary has all required keys

Estimated: ~12 tests, ~140 lines Python

Fidelity delta:
UK energy suppliers must report ET rates quarterly to Ofgem via the SFR data collection.
An ET rate above 0.1% triggers a compliance conversation. In 2022/23, several challenger
suppliers had elevated ET rates due to onboarding system failures. The 30 GBP automatic
compensation obligation means every overdue ET has a direct financial consequence.
Closes the switching-governance gap between switch_governance.py and the new
supply_point_register (Ph299) / cos_process (Ph298) layer.
