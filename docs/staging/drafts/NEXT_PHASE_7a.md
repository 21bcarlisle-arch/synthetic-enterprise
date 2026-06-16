# Proposed Next Phase: 7a — The Ledger (Gap #2 MVP)

## Context

Phase 6b (event-driven lifecycle) closed hollow gap #1 at MVP level —
accounts can now churn; the roster shrinks. The remaining "five hollow gaps"
(per CLAUDE.md) are:

2. **No ledger** — P&L is a formula, not the sum of transactions. Bills
   are computed but not issued as artefacts. Wholesale costs are settled
   but not posted to any account.
3. SIM/company barrier structural not functional.
5. (Reporting — closed by Phase 5a/5b.)

Gap #2 is the clearest next priority. The simulation produces all the right
numbers but none of the right records. There is no financial history —
nothing you could audit, reconcile, or hand to a treasurer and say "here's
where the money went."

ToU tariffs (Phase 6a's HH data makes these buildable) are listed as "Later"
in the roadmap — they require a real tariff pricing decision on top of the
infrastructure Phase 7a would provide (specifically, the ledger's
settlement records would be the natural place to track ToU period costs).
So ledger first.

## Proposed scope

**1. Transaction log.** A chronological list of money-moving events
(not a P&L formula). Three event types to start:

- `billing_event` — raised when a monthly bill is issued: amount, customer,
  period, line items (energy charge, standing charge, VAT, any prior debt).
  Created by an updated `saas/bill_generator.py`.
- `settlement_event` — raised when a half-hourly settlement period is
  processed: wholesale cost paid to BSUoS/grid, volume settled, spot price.
  Created by `simulation/hedged_settlement.py` and `simulation/gas_settlement.py`.
- `hedge_event` — raised when a hedging cost is incurred: forward price paid,
  volume hedged, hedge fraction, term start/end.
  Created from existing `forward_price` + `hedge_fraction` data in
  `simulation/renewals.py`.

Each event is a plain dict with a mandatory `transaction_id` (deterministic
UUID from the content), `event_type`, `amount_gbp` (positive = cash in,
negative = cash out), `timestamp` (settlement date/period), and the relevant
foreign keys.

**2. Running cash position.** `treasury_cash_balance_gbp` is already tracked
per settlement record. Phase 7a formalises this: the cash position is the
starting treasury plus the sum of all `amount_gbp` across all events in
chronological order. The existing per-settlement `treasury_cash_balance_gbp`
field becomes a derivable, auditable quantity rather than a stateful
accumulator.

**3. P&L from ledger.** Add a `derive_pnl(events: list[dict]) -> dict`
function (pure, no simulation state) that aggregates the ledger to produce
revenue, gross margin, capital cost, and net margin — the same figures the
simulation currently computes directly. Running both derivations in parallel
for one cycle lets us verify they agree before removing the direct
computation.

**4. Persisted ledger file.** Write the full event list to
`docs/reports/ledger_latest.json` alongside `run_output_latest.json` at the
end of each full run. Not a database — just the canonical record of what
happened, in append-only event order.

**5. Report section.** Brief "Transaction Log Summary" section in
`ANNUAL_REPORT.md`: total events by type, cash-flow waterfall (revenue
collected → wholesale settled → hedge costs → capital charges → net margin),
verification that P&L-from-ledger matches the simulation's direct figure.

**6. Tests.** `derive_pnl(events)` agrees with simulation's direct P&L on
the same run; `transaction_id` is deterministic (same inputs, same IDs);
cash position from ledger matches `treasury_cash_balance_gbp` at each
settlement period; a `billing_event` is raised for every customer-month pair
in `bills`.

## Out of scope (deferred)

- **Actual payment collection.** Bills are issued but payment is still just
  `payment_behaviour.py`'s probability model — no "cash received" event for
  individual payments. Full payment lifecycle (invoice → partial payment →
  bad debt write-off) is a separate phase.
- **VAT, Ofgem levies, balancing mechanism charges.** The ledger's
  `settlement_event` records the SSP/NBP wholesale cost only — levy/charge
  accounting is a later addition once the basic ledger structure is validated.
- **Double-entry bookkeeping.** The MVP is a single-sided event log (cash
  flows only), not a full general ledger with debits/credits. Good enough to
  answer "where did the money go?" without the overhead of mapping to nominal
  accounts.

## Why now

- All the underlying data exists: bills from `build_monthly_bills()`,
  settlement records from `run_hedged_term()` / `run_gas_term()`, hedge
  details from `renewals.py`'s forward prices.
- No upstream design dependencies: the ledger reads what the simulation
  already produces, it doesn't change how any of it is computed.
- Unblocks future capabilities: ToU tariff accounting, payment lifecycle,
  debt events from Phase 6b's churn mechanic.

## Gate

Proceeding with this scope in 4 hours unless redirected via staging or NTFY.
