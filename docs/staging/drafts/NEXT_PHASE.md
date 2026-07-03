# NEXT PHASE PROPOSAL: Phase PV -- I&C Corporate Payment Behavior + Arrears Calibration

## Gap addressed
Population Anchoring RED finding (Phase PS): arrears 29-31% of active customers per year
vs DESNZ I&C benchmark <8%. Root cause: (1) the I&C benchmark is applied to a MIXED
portfolio including residential customers whose DD failure rate is correctly higher; and
(2) I&C customers show 0% arrears (unrealistically clean -- bacs/chaps always success),
when real I&C businesses have ~5-8% from late BACS transfers and disputed invoices.

## What real fidelity is gained
A real UK energy supplier operates two distinct credit risk regimes:
  Residential: income-stress -> DD failure -> arrears dunning (Ofgem domestic benchmarks)
  I&C: corporate treasury -> late BACS / invoice dispute -> credit controller (DESNZ benchmarks)
Currently the SIM applies the I&C benchmark to the whole mixed portfolio.
Phase PV separates the two regimes, giving each segment correct payment mechanics and the
correct benchmark. The Population Anchoring dashboard transitions from RED to AMBER/GREEN.

## What this phase builds

### Part A: I&C corporate payment behavior (tools/generate_billing_ledger.py)
Current: bacs/chaps -> always (success, 0). No arrears ever.
New: _ic_payment_outcome(amount_gbp, year, rng) -> (outcome, days_late, dispute_flag)
  Base: 5% late BACS normal years; 10% crisis years (2021-22)
  Invoice dispute rate: 3% of invoices (BACS held pending resolution)
  Late days: 7-21 normal; 14-45 crisis
  Arrears trigger: >45 days overdue after dispute
  Resolution: 90% within 30 days via credit controller
  Write-off: only on customer churn (insolvency-proxied)
  Target: ~5-8% I&C arrears rate per year; <12% crisis years

  _ic_arrears_stages(arrears_gbp, due_date, is_dispute, eventually_resolved) -> stages
  INVOICE_DISPUTE / BACS_HOLD -> CREDIT_CONTROLLER -> RESOLVED | WRITTEN_OFF
  (not DD_FAILED dunning language -- I&C gets different stage labels)

### Part B: Segmented arrears benchmarks (tools/population_anchor.py)
_arrears_check_by_year: add segment_filter param (ic | resi | None=all)
Separate outputs:
  ic_arrears_vs_benchmark: filter to C_IC* customers; benchmark <8%/<12%
  resi_arrears_vs_benchmark: filter to non-IC; benchmark <15%/<25% (Ofgem domestic)
population_anchoring.json: replace arrears_vs_benchmark with ic_arrears + resi_arrears keys
overall_rag: arrears component uses IC rag only (company is I&C specialist)

### Part C: Annual report update (saas/reporting/annual_report.py)
_section_population_anchoring: render two arrears rows (I&C / Residential) instead of one
Column: segment | arrears_rate | benchmark | RAG

## Architecture decision (no one-way door)
Split is fully reversible -- two code paths additive, residential path unchanged.

## Epistemic check
Payment terms and dispute rates are company-observable (invoice ledger, BACS remittances).
DESNZ benchmarks are public (published business energy debt statistics). PASS.

## Test targets (~20 tests)
1. I&C invoice generates late BACS payment at ~5% rate in normal year
2. I&C crisis year late rate ~10%
3. I&C dispute rate ~3% of invoices
4. I&C arrears stage labels use BACS_HOLD / CREDIT_CONTROLLER (not DD_FAILED)
5. I&C arrears resolved within 30 days in 90% of cases
6. I&C write-off only on churned customers
7. I&C arrears rate per year: 5-8% normal, <12% crisis
8. Residential path unchanged (DD failure still income_stress driven)
9. _arrears_check_by_year segment_filter ic returns only C_IC* customers
10. _arrears_check_by_year segment_filter resi returns only non-IC customers
11. population_anchoring.json has ic_arrears_vs_benchmark key
12. population_anchoring.json has resi_arrears_vs_benchmark key
13. IC arrears RAG GREEN most years (5-8% < 8% benchmark)
14. IC arrears RAG AMBER in crisis years (9-11% < 12% benchmark)
15. overall_rag uses IC arrears RAG (not mixed)
16. Annual report renders two-row arrears table (I&C / Residential)
17. Annual report I&C row shows GREEN most years
18. Regression: existing churn/billing tests still pass
19. generate_billing_ledger with IC customers produces 5-8% arrears rate
20. population_anchor generate() runs end-to-end on live billing ledger

## Expected key finding
I&C arrears: 5-8% (GREEN, consistent with DESNZ business debt benchmarks). Residential
arrears: 20-30% (benchmarked against Ofgem domestic, AMBER most years). Population Anchoring
overall_rag transitions from RED to AMBER. Root cause of prior RED confirmed: mixed-benchmark
error, not a real simulation flaw. I&C corporate credit discipline correctly distinct from
residential income-stress-driven arrears.
