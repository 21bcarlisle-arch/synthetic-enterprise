# Proposed Next Phase: 7b — Ledger: Payment Lifecycle

## Context

Phase 7a (The Ledger MVP) closed hollow gap #2 at MVP level. The ledger
now records three event types:

- `billing_event` — revenue raised when a bill is issued (cash in, positive)
- `settlement_event` — wholesale cost paid per HH period (cash out, negative)
- `capital_charge_event` — VaR-based capital charge per HH period (cash out, negative)

What Phase 7a explicitly deferred:

> **Actual payment collection.** Bills are issued but payment is still just
> `payment_behaviour.py`'s probability model — no "cash received" event for
> individual payments. Full payment lifecycle (invoice → partial payment →
> bad debt write-off) is a separate phase.

The `billing_event` marks when a bill is *issued*, not when it is *paid*.
For a real energy supplier — especially with SME customers — the gap between
invoice date and cash receipt is material, and bad debt write-offs are a real
P&L event. The current `payment_behaviour.py` already models credit risk,
expected payment dates, and bad debt provisions per bill. Phase 7b closes
the loop: those probability outputs become actual timestamped events.

## Why now

- `payment_behaviour.py` already produces `expected_payment_date`,
  `credit_risk`, and `bad_debt_provision_gbp` per bill — the data exists.
- The ledger infrastructure from Phase 7a gives us the natural place to
  record these events with deterministic UUIDs.
- Bad debt isn't currently reflected in the cash position. If C4 is modelled
  at "high" credit risk with a 5% provision, that cost should appear in the
  ledger and reduce `net_margin_gbp` in `derive_pnl()`.

## Proposed scope

**1. Two new event types:**

- `payment_received_event` — cash collected against a bill:
  `{"event_type": "payment_received_event", "transaction_id": ...,
    "timestamp": expected_payment_date, "customer_id": ..., "bill_period": ...,
    "amount_gbp": total_amount_gbp - bad_debt_provision_gbp}` (positive)
- `bad_debt_event` — provision written off:
  `{"event_type": "bad_debt_event", "transaction_id": ...,
    "timestamp": expected_payment_date + 30d (write-off date), "customer_id": ...,
    "amount_gbp": -bad_debt_provision_gbp}` (negative, cash out)

The pair is deterministic from the payment_behaviour record. When
`bad_debt_provision_gbp == 0`, no `bad_debt_event` is emitted.

**2. Updated `derive_pnl()` to include payment-lifecycle items:**

```
Revenue billed:       billing_events sum
Cash collected:       payment_received_events sum
Bad debt written off: bad_debt_events sum
Cash P&L:             cash_collected + bad_debt_events (= revenue - bad debt)
```

The existing `gross_margin_gbp` and `net_margin_gbp` keys are unchanged —
they remain revenue-based. A new `cash_net_margin_gbp` key reflects what
was actually collected (revenue minus bad debt).

**3. Report section update:**

Extend the "Transaction Log" section's cash-flow waterfall:
```
Revenue billed           £xxx,xxx
  Cash received          (£xxx,xxx)   ← usually slightly less
  Bad debt written off   (£xx,xxx)    ← only if any
Cash collected net       £xx,xxx
Wholesale cost           (£xx,xxx)
Gross margin (cash)      £xx,xxx
Capital charges          (£x,xxx)
Net margin (cash)        £xx,xxx
```

**4. `build_ledger()` updated:**

`build_ledger(all_records, bills, payment_behaviour)` adds the third
argument. Existing tests still pass because the parameter is optional
(defaults to `None`, skipping payment events if absent).

**5. Tests:**

- Payment event amount = bill total − bad debt provision
- Bad debt event only emitted when provision > 0
- When provision = 0, no `bad_debt_event` emitted
- `derive_pnl` with payment events: `cash_net_margin_gbp` < `net_margin_gbp`
  when bad debt exists
- Determinism: same bill → same transaction IDs for payment events
- Chronological order: payment events appear after their corresponding
  billing event

## Out of scope (deferred)

- **VAT and Ofgem levies.** The billing events' amounts already include VAT
  (since `generate_bill()` returns the gross bill amount); explicit VAT
  line items and levy accounting are a later addition.
- **Partial payments / instalment plans.** One payment per bill. A real
  payment schedule with scheduled instalments is out of scope for now.
- **Hedge cost events.** Forward contracts commit capital when signed, before
  physical delivery. The simulation uses the forward price to set tariffs
  but doesn't model the actual delivery vs hedge P&L separately. A
  `hedge_event` type (Phase 7c?) would require reworking how the forward
  price relates to settlement cash flows — non-trivial scope.
- **Double-entry bookkeeping.** Still single-sided cash flows only.

## Gate

Proceeding with this scope in 4 hours unless redirected via staging or NTFY.
