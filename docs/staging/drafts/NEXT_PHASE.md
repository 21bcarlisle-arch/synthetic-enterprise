Phase 147 -- Guaranteed Standards of Performance (GSOPs)

Status: PROPOSED (2026-06-26)

Ofgem's GSOP scheme requires UK licensed electricity and gas suppliers to make
automatic payments to domestic customers when specific service standards are not met.
These are statutory, not contractual. Failure to auto-pay is itself a breach.

Standards and payment amounts (2016-2025 approximate; updated by Ofgem periodically):
- Missed appointment: £30 per occurrence
- Reconnection after wrongful disconnection: £30 per day up to 10 days
- Erroneous transfer (wrong MPAN switch): £30 compensation within 20 working days
- Failure to issue final bill within 6 weeks of switch: £30
- Failure to make refund within 10 working days: £30

Annual reporting obligation: suppliers must file GSOP compliance returns to Ofgem.
Non-automatic payments = additional Ofgem penalty (per SLC 2.7 etc.).

Design: company/regulatory/gsop.py

GSOPType enum: MISSED_APPOINTMENT / ERRONEOUS_TRANSFER / WRONGFUL_DISCONNECT /
               FINAL_BILL_DELAY / REFUND_DELAY

GSOPPayment(customer_id, gsop_type, trigger_date, payment_due_date, amount_gbp,
            paid_date=None)

GSOPBook:
- record_trigger(customer_id, gsop_type, trigger_date) -> GSOPPayment
  (auto-calculates due_date and amount from type)
- pay(payment_id, paid_date) -> marks as paid
- overdue(as_of_date) -> list of unpaid payments past due
- annual_report(year) -> payments by type, total liability, auto-pay rate pct
- total_liability_gbp(year=None) -> sum of unpaid + all if no year

2022 dynamic: high switching activity -> more erroneous transfers and missed
appointments as call centres overwhelmed; total GSOP liability rises.

~11 tests. Adds a mandatory financial liability line and regulatory compliance
obligation that every UK licensed supplier must track.
