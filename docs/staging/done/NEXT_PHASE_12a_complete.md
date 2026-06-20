# Phase 12a: Event-Driven Customer Lifecycle — Customers Actually Leave

## What this phase closes

**Hollow Gap 1: No customer events actually firing.**

Currently `roll_lifecycle_event()` returns an event dict and sets a flag in
`churned_billing_accounts`, but the customer remains in the simulation in a
weird limbo: their electricity settlement continues to be skipped via the
`billing_account in churned_billing_accounts` guard, but:
- No churn date is recorded anywhere permanent
- The customer's record in the system is unchanged
- There is no observable "customer left on this date" artefact
- No acquisition event fires for the incoming customer
- The company has no CRM record of the churn event

This is the difference between a risk score and an event.

## Epistemic contract

After this phase, when a customer churns:
1. A `ChurnEvent` is recorded with `customer_id`, `churn_date`, `reason: "non-renewal"`,
   `sim_churn_probability`, and `company_churn_estimate`.
2. The company's CRM updates the account status to `inactive` via
   `sim_interface.notify_churn()` — which already exists but does nothing in the live interface.
3. An `AcquisitionEvent` fires for any home-mover win (also currently a flag, not an event).
4. The company's CRM records the new acquisition with an `acquisition_date`.

## Deliverables

### 1. `company/crm/event_log.py`

Simple append-only event log for the company layer:
```python
@dataclass
class ChurnEvent:
    customer_id: str
    event_date: str
    reason: str  # "non-renewal", "home-move", "debt" (future)
    sim_churn_probability: float
    company_churn_estimate: float | None

@dataclass
class AcquisitionEvent:
    customer_id: str
    event_date: str
    channel: str  # "home-move-win", "market-acquisition"
    predecessor_id: str | None

class CompanyEventLog:
    def record_churn(self, event: ChurnEvent) -> None: ...
    def record_acquisition(self, event: AcquisitionEvent) -> None: ...
    def all_events(self) -> list[ChurnEvent | AcquisitionEvent]: ...
    def active_accounts(self, as_of_date: str) -> set[str]: ...
```

### 2. Wire `notify_churn` / `notify_acquisition` in `LiveSimInterface`

These methods already exist but are `pass` stubs. Wire them to a
`CompanyEventLog` instance so churn events are recorded when `run_phase2b`
calls `notify_churn` (it doesn't yet — that's step 3).

### 3. Emit `notify_churn` from `simulation/run_phase2b.py`

When a churn event fires (`event["event_type"] == "churned"`), call:
```python
sim_interface.notify_churn(billing_account, term_start_str)
```
Similarly emit `notify_acquisition` when a home-move win or fresh acquisition activates.

### 4. `run_phase2b` output: `company_event_log`

Add the company's event log to the simulation output JSON so the annual
report can inspect it. Key insight to surface: does the company's record
of who churned match the SIM's ground truth? (It should — but later, when
the company has its own churn estimator deciding whether to attempt
retention, the records will diverge.)

### 5. Annual report section: "Company CRM vs SIM Ground Truth"

Table comparing:
- SIM churned billing accounts (ground truth)
- Company CRM active accounts on each year-end date
- Any discrepancy (should be zero in Phase 12a — the company learns the
  same outcome the SIM produced; divergence becomes possible in Phase 12b
  when the company acts on its own churn estimate to attempt retention)

## Test scope

- `tests/company/crm/test_event_log.py` — unit tests for CompanyEventLog
- `tests/company/interfaces/test_notify_churn_live.py` — verify notify_churn
  populates the event log
- `tests/simulation/test_run_phase2b_event_log.py` — integration test confirming
  churn events in SIM output match company event log

## What this unlocks

- Customers actually leave on a specific date. That date is an artefact.
- The company CRM knows which customers are active at any point in time.
- Foundation for Phase 12b: if the company's churn estimate exceeds a threshold,
  it can attempt a retention offer BEFORE the churn roll — and the SIM can
  reduce churn probability based on the offer. The company acts on its imperfect
  estimate; the outcome depends on the SIM's ground truth.
- Foundation for a real ledger: final settlement on the last bill of a churned
  account is a distinct transaction type.

## Commit message

"Phase 12a: event-driven customer lifecycle — customers actually leave"
