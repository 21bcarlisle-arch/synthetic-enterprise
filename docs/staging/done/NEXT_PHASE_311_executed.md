Phase 311 -- Debt Collection Process Book

Status: PROPOSED (2026-06-27T11:15 UTC)
4h opt-out window: expires 2026-06-27T15:15 UTC

Context:
The company has bad_debt_provision.py (aging buckets, provision rates) but no
formal debt collection process tracker. In a real UK energy supplier, arrears
go through defined stages with escalating actions, each governed by Ofgem
Standards of Performance and vulnerable customer rules.

UK regulatory framework:
- SLC P14 / SoP Regulations: suppliers must follow a debt collection process
  before disconnecting or adding a debt to a prepayment meter
- Ofgem Smart Meter Prepayment Meter (PPM) Rules: debt can be loaded onto PPM,
  max £250 (domestic), recovery rate 5% of total spend
- Debt Assignment Protocol (DAP): debt follows the customer on switch
- Statute of limitations: 6 years (England/Wales), 5 years (Scotland)

Stages modelled:
1. INITIAL_REMINDER: 7-day payment reminder letter (automated)
2. WARNING_LETTER: 14 days, advises potential referral
3. PRE_LEGAL: 28 days, final notice before external agency
4. DEBT_AGENCY: assigned to external collection agency at ~70p/£ recovery rate
5. LEGAL_ACTION: county court judgment (CCJ) or small claims
6. WRITE_OFF: statute-barred or unrecoverable

Design:
  company/finance/debt_collection.py (new)

  DebtStage (enum): INITIAL_REMINDER / WARNING_LETTER / PRE_LEGAL / DEBT_AGENCY /
    LEGAL_ACTION / WRITE_OFF

  DebtRecord (frozen dataclass):
    account_id / amount_gbp / stage / stage_date / is_vulnerable_customer
    Computed:
      days_in_stage(as_of_date) -- calendar days since stage_date
      is_statute_barred(as_of_date) -- >6 years from initial
      recovery_probability -- 0.85 (pre-legal), 0.70 (agency), 0.40 (legal), 0.0 (write-off)
      expected_recovery_gbp -- amount * recovery_probability

  DebtCollectionBook:
    record_debt(record) -> DebtRecord
    escalate(account_id, new_stage, stage_date) -> DebtRecord
    write_off(account_id, write_off_date) -> DebtRecord
    active_debts() -> list (not WRITE_OFF)
    debts_by_stage(stage) -> list
    total_outstanding_gbp() -> float (all active)
    expected_recovery_gbp() -> float (sum of expected_recovery_gbp)
    vulnerable_accounts() -> list (is_vulnerable_customer)
    statute_barred_check(as_of_date) -> list of barred records
    debt_summary() -> dict

Real data calibration:
- Bad debt 2022: UK average £380/customer in arrears (Ofgem Retail State of Market)
- Write-off rate: ~1.5-2.5% of revenue in crisis years (2022-23)
- Agency recovery rate: 60-75p in the £ for energy debts
- Average days-to-legal: 90-120 days from first reminder
- Vulnerable customers: must not be referred to debt agency without prior welfare checks

Connects to: bad_debt_provision (Ph?? -- aging buckets), billing (invoices),
  warm_home_discount (Ph281 -- vulnerable customers), consumer_duty (Ph283),
  stress_test (Ph303 -- credit default scenario).

Estimated: ~18 tests, ~150 lines
