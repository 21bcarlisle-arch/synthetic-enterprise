# Proposed Phase NG: Company Satisfaction Score -> Renewal Churn Estimate

## Problem
enriched_churn_estimate() has accepted satisfaction_score since Phase NB/NC,
but run_phase2b.py passes satisfaction_score=None (never wired). The company renewal churn
estimate ignores the satisfaction signal -- the same gap causing 67% blind miss rate.
SIM-side: roll_lifecycle_event gets satisfaction_score=_nf_satisfaction (Phase NF).
Company-side: estimate uses only rate model because satisfaction is absent.

## Fix
Wire CustomerSatisfactionAccumulator into run_phase2b.py using company-observable signals:
1. Import CustomerSatisfactionAccumulator from company.crm.satisfaction_accumulator.
2. Instantiate _company_sat_acc = CustomerSatisfactionAccumulator() (per-customer dict).
3. At each term where rate_increase > BILL_SHOCK_THRESHOLD: record_bill_shock(cid).
4. Apply monthly decay once per billing year: apply_monthly_decay(cid, months=12).
5. At renewal: pass satisfaction_score=_company_sat_acc.get_satisfaction(cid) to _enriched_churn_estimate.

Epistemic: company derives satisfaction from its own billing records only (no SIM internals).

## Tests (~16)
- satisfaction_score not None at renewal (smoke)
- 0 shocks: score = BASELINE 0.70
- 1 shock: score = 0.65
- 2 shocks: score = 0.60
- 12 months decay restores ~0.12 toward baseline
- score in [0.0, 1.0] always
- low satisfaction (<0.50) -> higher churn estimate vs None baseline
- high satisfaction (>=0.80) -> lower churn estimate vs None baseline
- two customers tracked independently
- shocked customer crosses RETENTION_THRESHOLD where rate model alone would not
- satisfaction not from SIM internals (no income_stress input)
- BILL_SHOCK_THRESHOLD constant accessible
- decay rate constant accessible
- baseline constant accessible
- estimate with satisfaction > estimate without (shocked customer)
- 3-term history with 1 shock produces expected final score

## File changes
- simulation/run_phase2b.py: wire CustomerSatisfactionAccumulator (5-10 line change)
- tests/simulation/test_phase_ng_satisfaction_estimate.py: 16 new tests

## Fidelity delta
Company now uses observable bill-shock history to derive satisfaction and feeds it into
renewal churn estimate -- closing the loop between enriched model capability and what the
SIM passes at decision time. Blind miss rate should fall as low-satisfaction customers get
higher company estimates -> retention offers triggered earlier.
