## Phase PW COMPLETE -- I&C Corporate Arrears Calibration
Last updated: 2026-07-04T03:33:29Z

**Status:** COMPLETE. 15,359 tests passing. Epistemic: PASS.

**Phase PW -- I&C Corporate Arrears Calibration:**
- generate_billing_ledger.py: I&C BACS/CHAPS invoice dispute model (92% on-time, 7.3% late, 0.7% dispute)
- Dispute stages: INVOICE_DISPUTED -> DISPUTE_NOTICE -> PAYMENT_PLAN_AGREED | WRITTEN_OFF
- Segment stored in customer ledger dict
- population_anchor.py: _arrears_check_by_year separates I&C from resi
- ic_aggregate_rate_pct (10-yr) used for RAG vs DESNZ commercial benchmark (<8% normal)
- KEY FINDING: IC arrears 0% -> 5.4% aggregate; all years rag=GREEN
- Prior PS RED (29-31%) was resi income-stress arrears vs I&C benchmark (category mismatch fixed)

**Next:** Reviewing PRIORITIES.md for P2 (Network Charge Year-Indexed Actuals) or next highest gap.


**Latest simulation results (2016–2025)** — auto-processed (463s / 8 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts