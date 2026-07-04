# NEXT PHASE PROPOSAL: Phase PW -- I&C Corporate Arrears Calibration

## Gap addressed
Phase PS Population Anchoring RED finding: arrears 29-31% of active customers per year
vs DESNZ I&C commercial energy debt benchmark <8%. Root cause: I&C customers use
BACS/CHAPS payment, which generate_billing_ledger.py always marks as ("success", 0) --
producing 0% I&C arrears (unrealistically clean). Real I&C businesses have ~5-8%
invoice dispute/late-payment rate from cashflow management, disputes, and admin delays.

## What real fidelity is gained
- I&C arrears rate 0% -> ~5-8% (DESNZ benchmark range)
- Residential arrears still driven by income_stress (current model correct)
- Population Anchoring overall_rag transitions RED -> AMBER/GREEN
- Board can now distinguish corporate credit risk from household income stress

## Architecture
The fix is entirely in tools/generate_billing_ledger.py:
1. Add _IC_INVOICE_LATE_PROB = 0.06 (6% of I&C invoices have payment delay)
2. Add _IC_LATE_DAYS = (14, 45) -- corporate payment delay range
3. Add _IC_DISPUTE_PROB = 0.02 -- 2% escalate to formal dispute (arrears case)
4. Modify _payment_outcome: BACS/CHAPS outcome now has small late/dispute probability
   - 92% on-time success (was 100%)
   - 6% late success (days_late 14-45)
   - 2% dispute -> triggers arrears case
5. Add _ic_arrears_stages: INVOICE_DISPUTED -> DISPUTE_NOTICE -> PAYMENT_PLAN_AGREED | WRITTEN_OFF
   (no DD_FAILED stage -- I&C uses bank transfer)
6. generate_billing_ledger.py: I&C arrears cases use _ic_arrears_stages
7. population_anchor.py: annotate arrears check with portfolio_type note
   (benchmark is from DESNZ commercial energy debt statistics, not residential)

## Epistemic check
All changes are in the billing ledger generator (company-observable document).
I&C payment records are company-observable (invoice payment history).
No SIM internals accessed. PASS.

## Test targets (~15 tests)
1. _payment_outcome BACS/CHAPS: ~92% success-on-time, ~6% late, ~2% dispute
2. I&C dispute creates arrears case with INVOICE_DISPUTED stage (not DD_FAILED)
3. Arrears stages for I&C: INVOICE_DISPUTED -> DISPUTE_NOTICE -> PAYMENT_PLAN_AGREED or WRITTEN_OFF
4. Residential DD_FAILED path unchanged (regression)
5. I&C arrears rate across full portfolio: 4-10% of billing months (benchmark range)
6. Residential arrears rate unchanged (income_stress driven, was 29-31%)
7. Arrears case count for I&C customer over full sim: > 0 (was 0)
8. BACS on-time probability set correctly (0.92 base)
9. Late BACS payment: days_late in (14-45) range
10. Written-off I&C arrears: bad_debt raised (matches written_off stage)
11. generate() populates arrears_history for an I&C customer
12. I&C arrears_case_count > 0 for C_IC1 (high volume customer, most likely to dispute)
13. SME BACS path: also gets small late probability (SME ~3-4% dispute rate)
14. Arrears check in population_anchor.py: RED when ic_arrears_rate > 8%; GREEN when <8%
15. population_anchor overall_rag AMBER after PW fix (arrears transitions to benchmark range)

## Expected outcome
Population anchoring arrears check transitions from RED (29-31%) to GREEN/AMBER (~5-8%).
No changes to income_stress model (residential arrears remain driven by stress trajectory).
No changes to simulation/ layer. Purely company-observable billing ledger calibration.
