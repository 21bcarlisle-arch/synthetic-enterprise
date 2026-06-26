Phase 302 -- Guaranteed Standards of Performance (GSoP) Payments Tracker

Status: PROPOSED (2026-06-26T23:45Z)
4h opt-out window: expires 2026-06-27T03:45Z

Context:
Phase 301 (Erroneous Transfer Register) introduced automatic compensation for ET
resolution breaches (£30 per overdue claim). The other major statutory compensation
scheme is the Guaranteed Standards of Performance (GSoP), defined under the Electricity
(Standards of Performance) Regulations 2015 and Gas Standards equivalent. These mandate
automatic compensation payments to customers when suppliers breach minimum service
standards -- no complaint required, payments triggered by breach event.

Key GSoP obligations (supplier-side):
  - Failure to provide a bill within 12 weeks of meter read: £30/customer
  - Failure to resolve a billing complaint within 8 weeks: £30/customer
  - Failure to reconnect supply within 24 hours of emergency disconnection: £30/customer
  - Failure to acknowledge a complaint within 5 working days: £30/customer
  - Missing engineer appointment without 24h notice: £30/customer
  - Failure to provide final bill within 6 weeks of switch: £30/customer

Ofgem collects GSoP breach data through the SFR (Supplier Financial Resilience) and
annual SLC returns. Repeated breaches signal systemic failure and trigger investigations.

GSoP connects directly to:
  - cos_process.py (Ph298): final bill after switch is a GSoP obligation (6 weeks)
  - erroneous_transfer.py (Ph301): ET compensation is parallel scheme (£30 per breach)
  - consumer_duty.py (Ph283): Consumer Support outcome -- response time obligations
  - regulatory_dashboard.py (Ph300): GSoP compliance rate is a consumer protection metric
  - ofgem_supply_return.py (Ph190): annual SLC return includes GSoP breach counts

Design:
- company/regulatory/gsop_tracker.py (new):
  GSoPStandard enum (10 breach types):
    BILLING_DELAY / COMPLAINT_NO_RESPONSE / COMPLAINT_UNRESOLVED /
    RECONNECTION_DELAY / APPOINTMENT_MISSED / FINAL_BILL_DELAY /
    METER_READ_DISPUTE / DIRECT_DEBIT_ERROR / SWITCHING_DELAY / DEBT_QUERY_DELAY

  GSoPBreachStatus enum: OPEN / COMPENSATED / WAIVED / DISPUTED

  frozen GSoPBreach dataclass:
    breach_id / account_id / standard / breach_date / resolution_date (optional)
    compensation_gbp (fixed 30 GBP per breach) / status / notes
    Properties: is_open / is_compensated / working_days_open (Mon-Fri count)

  GSoPTracker class:
    record_breach(account_id, standard, breach_date, notes) -> GSoPBreach
    compensate_breach(breach_id, resolution_date) -> GSoPBreach
    waive_breach(breach_id) -> GSoPBreach
    open_breaches() -> list[GSoPBreach]
    breaches_for_standard(standard) -> list[GSoPBreach]
    total_compensation_paid_gbp() -> float
    total_compensation_outstanding_gbp() -> float
    breach_rate_per_100_customers(total_customers) -> float
    breaches_by_standard() -> dict[str, int]
    is_systemic(standard) -> bool  (>5 breaches of same type)
    gsop_summary() -> dict

- tests/company/regulatory/test_gsop_tracker.py (~14 tests):
  - GSoPBreach is frozen (immutable)
  - working_days_open counts Mon-Fri only
  - compensation_gbp is always 30.0 (statutory fixed amount)
  - record_breach returns OPEN breach, appears in open_breaches()
  - compensate_breach transitions to COMPENSATED with resolution_date
  - waive_breach transitions to WAIVED
  - total_compensation_outstanding_gbp sums only OPEN breaches
  - total_compensation_paid_gbp sums only COMPENSATED breaches
  - breach_rate_per_100_customers correct calculation
  - breaches_for_standard filters correctly
  - is_systemic True when >5 same-standard breaches
  - gsop_summary has all required keys
  - BILLING_DELAY and FINAL_BILL_DELAY most common in real UK data
  - Empty tracker produces clean summary (no division errors)

Estimated: ~14 tests, ~150 lines Python

Fidelity delta:
UK energy suppliers paid 21.3M GBP in GSoP compensation in 2022-23 (Ofgem data).
BILLING_DELAY and COMPLAINT_UNRESOLVED are the two most common breach types -- 2022 crisis
saw complaint volumes 10x normal, causing widespread GSoP breaches. The 30 GBP fixed amount
matches ET compensation (Ph301) by regulatory design. Ofgem uses breach-per-100-customers as
a red flag: >3 triggers supervisory action. Phase 301 closed the ET gap. Phase 302 closes the
GSoP gap. Both feed regulatory_dashboard.py (Ph300) and the annual SFR return.
