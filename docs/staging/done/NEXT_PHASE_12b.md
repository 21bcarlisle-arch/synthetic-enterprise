# Phase 12b: Company-Driven Retention Offers — First Company Decision Affecting Simulation Outcome

## What this phase does

**The company acts on its own churn estimate before the SIM rolls.**

In Phase 12a, the company learns of churn after the SIM has already decided. In Phase 12b, the company's `CompanyEventLog` enables a pre-roll intervention: if the company's churn estimate exceeds a threshold, it offers a retention discount before the SIM rolls the churn dice.

This is the first case of a company decision affecting simulation outcome.

## Mechanism

1. At each renewal point, before `roll_lifecycle_event()` is called:
   - If `company_churn_estimate > RETENTION_THRESHOLD` (e.g. 0.30), the company offers a retention discount
   - The discount is a unit rate reduction (e.g. 5% below the renewal offer)
   - The SIM applies a `retention_modifier` to `churn_probability`: `p_churn_modified = p_churn * (1 - RETENTION_EFFECTIVENESS)`
   
2. The company records the retention attempt as a `RetentionEvent` in `CompanyEventLog`:
   ```python
   @dataclass
   class RetentionEvent:
       customer_id: str
       event_date: str
       company_churn_estimate: float
       discount_pct: float  # e.g. 0.05
       outcome: str  # "retained" | "churned_despite_offer"
   ```

3. The cost of the retention offer (foregone margin on the discounted term) is recorded in the ledger as a `retention_cost_event`.

## What this unlocks

- Company imperfect estimates (under-estimating churn in crisis years) become consequential
- The simulation can show whether the company's retention strategy is net-positive
- Basis risk in churn estimation has a P&L consequence, not just a tracking consequence

## Deliverables

1. `company/crm/event_log.py`: add `RetentionEvent` dataclass; `CompanyEventLog.record_retention()` method
2. `company/interfaces/sim_interface.py`: `notify_retention_attempt(account_id, event_date, company_estimate, discount_pct)` method
3. `simulation/run_phase2b.py`: before `roll_lifecycle_event()`, check `company_churn_estimate`; if above threshold, apply `retention_modifier` to the churn model; notify the company of the retention attempt
4. Ledger: `make_retention_cost_event()` — records foregone margin on discounted term
5. Annual report: "Retention Strategy P&L" section — offers made vs retained vs cost

## Constants to expose

```python
RETENTION_THRESHOLD = 0.30        # company churn estimate above which to intervene
RETENTION_DISCOUNT_PCT = 0.05     # 5% unit rate reduction on renewal offer
RETENTION_EFFECTIVENESS = 0.20    # reduces churn probability by 20% if offer is made
```

## Commit message

"Phase 12b: company retention offers — first company decision affecting SIM outcome"
