# NEXT PHASE PROPOSAL: Phase NR — Bad Debt → Capital Stress Feedback

## Problem

`company/finance/bad_debt_provision.py` exists and computes IFRS 9 ECL provisions, but it
is never imported by `company/risk/capital_adequacy.py`. The capital adequacy stress test
considers only price VaR (market risk) — credit risk from customer bad debt is completely
absent.

In a real UK energy supplier this is a material gap: post-2022 Ofgem FRA requires combined
stress testing of market risk AND credit risk. Several of the 28 supplier failures in
2021-22 were partly caused by bad debt shock (payment holidays + payment cap extension)
eroding working capital faster than price VaR alone.

Current state: `CapitalAdequacyAssessment.stress_test_passes` = `equity > price_VaR`.
Real state: should be `equity > (price_VaR + credit_stress_shock)`.

## What this phase builds

### Part A: Credit risk stress module
`company/risk/credit_risk_stress.py`: `CreditRiskStress` dataclass:
- `current_provision_gbp`: existing bad debt provision
- `stress_multiplier`: how much worse bad debt becomes in a crisis (2.5x empirical from
  Ofgem 2022 data: industry bad debt rose from ~1% to ~2.5% of revenue)
- `stress_incremental_gbp`: `max(0, provision * multiplier - provision)` = extra capital
  needed above current provision
- `is_material`: whether incremental > 0.5% of annual revenue (disclosure threshold)

### Part B: Wire into CapitalAdequacyAssessment
`company/risk/capital_adequacy.py`: add `credit_risk_stress_gbp` field to
`CapitalAdequacyAssessment`; update `stress_test_passes` to
`equity > (stress_var_gbp + credit_risk_stress_gbp)`; status scoring unchanged (still
0-4 failure count -> ADEQUATE/MARGINAL/INADEQUATE/CRITICAL).

### Part C: Board section
`saas/reporting/annual_report.py`: `_section_credit_risk_capital` -- shows current
provision rate, stress multiplier applied, incremental capital consumed, whether combined
stress (price VaR + credit) is within equity buffer. RAG: GREEN both within equity;
AMBER credit stress alone exceeds 1% equity; RED combined exceeds equity.

## Why this has real fidelity value
- Ofgem FRA post-2022 explicitly requires combined market + credit stress testing
- 2022 empirical data: bad debt rose 2.5x during crisis (Ofgem consumer vulnerability report)
- Current model would show capital as adequate even if customers stopped paying en masse
- Closing this gap means the board section gives a complete risk picture, not just commodity VaR
- Epistemic: company observes its own arrears book (bad_debt_provision) -- zero sim barrier issues

## Test targets (~12 tests)
- CreditRiskStress dataclass: multiplier, incremental, is_material threshold
- Capital assessment passes when equity covers combined stress
- Capital assessment fails when credit shock pushes combined above equity
- Stress multiplier 1.0 = current provision, no incremental capital required
- Board section renders RAG correctly at Green/Amber/Red boundaries
- No epistemic violations (company reads its own arrears book)
