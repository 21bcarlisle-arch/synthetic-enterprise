**Severity:** RECORDED · **Lane:** C_customer_ops · **Atom:** `C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv`

# Pre-registration: why the median renewing household contributes −£3.91 a month

Written 20 Oct 2026 at 19:28 BST, before the probe run was launched. The run is the C34 on-arm
policy from `b8c665948`, on `origin/main` at `768f41ed1`, with full window and default seed. It
wraps `term_contribution_per_month` and the desk's two `observe_*` methods to record every leg's
inputs, and it changes no code. The finding that grades this note follows.

## What each number counts

- **`term_contribution_per_year`** (`company/crm/renewal_advice_desk.py`) is one leg over one
  year of the coming term. It is (renewal unit rate − `pre_margin_unit_rate`) × the company's
  EAC, less `FIXED_OVERHEAD_GBP_PER_YEAR["resi"]` (£55) for that leg.
  - `pre_margin_unit_rate` is the same number as `term_cost_floor`: forward + capital + locked
    policy + locked network.
  - The standing charge is not credited. It is a stated GAP, §6.1 of
    `next_best_action_and_cross_sell.md`.
  - Bad debt is not netted.
- **The book's provisioned net margin** (`cd1f976c7`) covers every leg over the whole window.
  It counts unit revenue **plus the standing charge** that every settled record bills
  (`hedged_settlement.py`, `gas_settlement.py`), less wholesale, pass-through, cost to serve and
  provisioned bad debt.

## Predictions

- **P1.** On a fixed leg struck by `strike_fixed_unit_rate`, rate − `term_cost_floor` is exactly
  +£2.00/MWh (`TARGET_MARGIN_GBP_PER_MWH`) unless the competitive ceiling clamped it. It is never
  above £2.00.
- **P2.** The term that makes the median negative is cost to serve: £55 a year per leg, against
  a median leg margin of about 2 × EAC/1000, or £6–25 a year. A fixed leg breaks even at an EAC
  of 27.5 MWh.
- **P3.** Fewer than 10% of legs sit below `term_cost_floor`. Where one does, the competitive
  ceiling put it there (2021–22, 2025).
- **P4.** The positive households sit where the rate passed in is not a fresh strike (2023 shows
  higher spreads), not only at large EACs.
- **P5.** Bad debt is not in the quantity. Adding the year's resi provision makes it more
  negative.
