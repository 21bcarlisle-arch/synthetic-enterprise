Phase 312 -- Account Closure Book

Status: PROPOSED (2026-06-27T03:05 UTC)
4h opt-out window: expires 2026-06-27T07:05 UTC

Context:
The company has cos_process (Ph298) tracking the switch, supply_point_register (Ph299)
for MPAN/MPRN registry, debt_collection (Ph311) for arrears, but no formal account
closure process. In a real UK energy supplier, account closure is a regulated multi-step
process with strict timelines.

UK regulatory framework:
- SLC 21B (Final bill): supplier must issue final bill within 6 weeks of supply end
- SLC 12 (Deposit return): return security deposit within 14 days of final bill
- SLC P14 (Vacant properties): vacancy-specific rules on standing charges
- Gas Safety (Installation and Use) Regulations: vacant property de-energisation
- CoS Protocol: deregistration from MPAS within 3 working days of switch completion

Stages modelled:
1. INITIATED: switch complete or vacancy confirmed
2. FINAL_READ_RECEIVED: meter read received from MOp/DC
3. FINAL_BILL_ISSUED: final invoice generated (SLC 21B: 6-week deadline)
4. DEPOSIT_RETURNED or DEBT_REFERRED: deposit applied or returned; outstanding debt flagged
5. CLOSED: account fully settled

Design:
  company/billing/account_closure.py (new)

  ClosureReason (enum):
    CUSTOMER_SWITCH / VACANT_PROPERTY / CUSTOMER_DECEASED / BUSINESS_CLOSURE

  ClosureStatus (enum):
    INITIATED / FINAL_READ_RECEIVED / FINAL_BILL_ISSUED /
    DEPOSIT_APPLIED / DEPOSIT_RETURNED / DEBT_REFERRED / CLOSED

  AccountClosure (frozen dataclass):
    account_id / supply_point_id / closure_date / reason / status
    final_read_kwh (Optional[float]) / final_bill_gbp (Optional[float])
    deposit_held_gbp / debt_balance_gbp

    Computed:
      net_balance_gbp -- final_bill + debt_balance - deposit_held
      (positive = customer owes us; negative = we owe customer)
      requires_debt_referral -- net_balance > 0 and not already referred/closed
      days_since_closure(as_of) -- int

  AccountClosureBook:
    initiate(account_id, supply_point_id, reason, closure_date, deposit_held, debt_balance)
    receive_final_read(account_id, kwh)
    issue_final_bill(account_id, bill_gbp)
    return_deposit(account_id) -- status -> DEPOSIT_RETURNED (net_balance <= 0)
    apply_deposit_to_debt(account_id) -- status -> DEPOSIT_APPLIED (net_balance > 0)
    refer_to_debt_collection(account_id) -- status -> DEBT_REFERRED
    close(account_id) -- status -> CLOSED
    active_closures() -- not CLOSED
    overdue_final_bills(as_of, days=42) -- initiated but no final bill after 42 days
    deposits_to_return() -- status DEPOSIT_RETURNED (receivable for company)
    debt_referrals() -- status DEBT_REFERRED
    closure_summary() -> dict

Real data calibration:
- Ofgem target: final bill within 6 weeks (42 days) of supply end
- 2022 complaint data: final bill delays were #1 complaint category for switches
- Deposit return: 14 days after final bill (mandatory); average deposit ~£150
- ~8-12% of closures have outstanding debt balance at final bill
- Vacant properties: standing charge continues until new supplier or de-energisation
- Business closures (SME): debt more likely (invoice terms vs DD)

Connects to: cos_process (Ph298), supply_point_register (Ph299), billing/invoice,
  debt_collection (Ph311 -- refer outstanding balances), direct_debit (deposit return),
  warm_home_discount (Ph281 -- deceased customer handling), consumer_duty (Ph283).

Estimated: ~20 tests, ~130 lines
