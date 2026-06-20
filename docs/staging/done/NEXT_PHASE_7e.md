# Proposed Next Phase: 7e — Home-Move Win / Replacement Customer Onboarding

## Context

Phase 6b (event-driven customer lifecycle, 2026-06-16) closed hollow gap #1 at MVP
level: accounts can now actually churn at renewal, and the portfolio genuinely shrinks.
Phase 7d (currently in progress) generates the first feature-complete report with CLV
trajectory, per-year churn risk, and activity-based pricing flags.

The Portfolio shrinks but never grows. By 2024, six of the original ten billing
accounts have churned (C1, C2, C3, C4, C5, C6). C7/C8/C9 survive. This is
structurally unrealistic — real energy suppliers have continuous acquisition flow,
including home-movers taking over properties vacated by churned accounts.

The data for this already exists:
- `saas/home_move_win_rate.py` computes `win_probability` per renewal period
- `simulation/customer_events.py`'s `roll_lifecycle_event()` already retrieves this
  win probability (it feeds into `effective_retention_probability`)
- The lifecycle event dict already contains `win_probability` in its output

We are throwing away the win probability after computing it. Phase 7e uses it.

## What this means in real life

When a customer leaves (churns) at renewal:
- Their property doesn't disappear. A new occupant moves in.
- We compete to supply that new occupant.
- `win_probability` is the probability we win that competition.
- If we win, a new billing account starts at the same property from the churn date.

## Proposed scope

### 1. Extend `roll_lifecycle_event()` to return a win/loss decision on churn

When `event_type == "churned"`, add a second deterministic roll:

```python
win_roll = _random.Random(f"win_{billing_account}_{term_start_str}").random()
home_move_won = (win_roll <= renewal_data["win_probability"])

return {
    ...,
    "home_move_won": home_move_won,       # True = new occupant signed with us
    "win_probability": ...,               # already present; make explicit
}
```

This is fully deterministic and backward-compatible (existing tests still pass).

### 2. Define successor customer entries in `saas/customers.py`

For each customer that can churn, define a successor:

```python
# Successor definitions — activated if we win the home-move on original churn
{
    "customer_id": "C1_2",
    "successor_of": "C1",          # inherits property from C1
    "acquisition_date": None,       # set dynamically at activation
    "location": ...,                # same as C1
    "home_type": ...,               # same as C1
    "bedrooms": ...,                # same as C1
    "segment": "resi",
    "commodity": "electricity",
    ...
},
```

Minimal change — successors have the same property attributes but start with zero
bill-shock history (as a genuinely new customer would).

### 3. Activate successors in `run_phase2b.py`

The simulation loop is currently:
```
for term_start_str, cid, commodity, term in all_terms:
    if billing_account in churned_billing_accounts:
        continue
    ...
```

Phase 7e adds:
- A `won_successor_activations: dict[str, str]` map:
  `{successor_customer_id: activation_date}` — populated when a churn fires with
  `home_move_won == True`
- Terms for successor customers (pre-computed alongside original customers in
  `all_terms`) that are skipped until `term_start_str >= activation_date`

This keeps the main loop clean. Successor terms are pre-baked into `all_terms`
(from `CUSTOMERS + SUCCESSOR_CUSTOMERS`); they're just gated by activation date.

### 4. Report section update

`_customer_book_section()` already shows:
```
- New acquisitions this year: none
```
This was always "none" because `CUSTOMERS` has static acquisition dates in 2016.
Phase 7e fills this with actual mid-run won home-movers:
```
- New acquisitions this year: C1_2 (won home-move, property: London urban flat)
- Losses (churn): C1
```

A separate "Portfolio Churn & Acquisition" summary at the top of the report would
track gross/net portfolio change each year, showing that the business is growing,
stable, or attriting.

## Out of scope (deferred)

- **Genuinely new customers** (not home-movers — brand new properties or first-time
  switchers). That requires a separate acquisition model with market share, advertising
  spend, etc. Home-movers are the natural first step since they piggyback on the
  existing churn mechanic.
- **Gas leg for successor customers** — successors start on electricity only in this
  MVP. Dual-fuel expansion of successors is a follow-on.
- **Successor churn risk trajectory** — first-year bill-shock history is zero for a
  successor (clean slate). By the second renewal point the model runs normally. No
  special handling needed.

## Implementation complexity assessment

- `simulation/customer_events.py`: +5-8 lines (second roll, `home_move_won` field)
- `saas/customers.py`: +40-60 lines (up to 6 successor customer dicts — only for
  customers who actually churn: C1, C2, C3, C4, C5, C6)
- `simulation/run_phase2b.py`: +10-15 lines (activation gate on successor terms)
- `saas/reporting/annual_report.py`: +20-30 lines (update `_customer_book_section`
  to distinguish won home-movers from static acquisitions; add portfolio trend)
- Tests: +10-15 (determinism of win roll, activation gate, portfolio section)

Total: ~100-130 lines of new/changed code. Estimated 1.5-2 context windows.

## Financial impact

Won home-movers generate new revenue from the churn date. If C1 churns in 2021-12
and we win the home-move (typical win probability ~55% for a resi customer at
benchmark pricing), "C1_2" starts billing from 2022-01 and runs until 2025-12
(end of simulation window). That's 4 years of additional revenue from the same
property that would otherwise have been lost.

Expected portfolio size at 2025-12 with Phase 7e (rough estimate at 55% win rate):
- Original 10 → 6 churn → ~3 wins → ~7 active (vs. 3 currently)
- Revenue and net margin increase proportionally

This is a material fidelity improvement: a real supplier with ~55% home-move win
rate would NOT see its portfolio halve over 9 years, as ours currently does.

## Gate

Per CLAUDE.md opt-out pattern: will proceed in 4 hours unless Rich redirects.
