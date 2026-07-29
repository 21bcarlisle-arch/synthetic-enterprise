# B5 — Shaped-cost benchmark + trading value-add ledger — FRAME

Status: DISCOVER + FRAME complete on a lane-3 idle fork. No BUILD code written.
`level_current` HELD at 0 (MATURITY_MAP.md §3: L1 requires code built in some real
form; nothing is built here). This document is what stops the atom re-drawing the
idle DISCOVER/FRAME pool (`supervisor._atom_has_frame_doc` — only a `docs/design/*_FRAME.md`
path in `evidence:` saturates FRAME; an inline note does not).

All claims below are `observed-with-evidence` (R9) unless marked `inferred`; every
one was read from disk this session, not recalled.

## 1. Verified current state

**No shaped-cost benchmark exists anywhere in the tree.** A repo-wide grep for
`shaped.*benchmark|benchmark.*shaped|would have cost|bought shaped` returns zero
hits outside this atom's own map/backlog prose. The benchmark that *does* exist
today is a different, narrower thing:

- `company/risk/hedge_policy.py:29-69` (`company_evolve_hedge_fraction`) compares
  `actual_net_gbp` (the company's real booked P&L) against `naked_net_gbp`
  ("what the company computes it would have made with no hedge — revenue minus
  (volume × actual spot price)", `hedge_policy.py:36-38`) and raises/trims the
  hedge fraction on the difference (`:43-61`).
- The `naked_net` computed in `simulation/run_phase2b.py:2026-2045` confirms the
  precise shape: for electricity, `naked_gross = Σ revenue_gbp − (consumption_kwh/1000) ×
  elec_price_lookup[settlement_date, settlement_period]` — i.e. priced at **real-time
  half-hourly spot**, not at any forward/tenor price — minus a cost-of-capital term
  (`naked_capital`, sourced from `counterfactual_risk["monthly_cost_of_capital_gbp"]`,
  same pattern for gas at `:2036-2045` against `gas_spot_lookup`).
- This "naked" comparator answers *"did hedging beat doing nothing (raw spot
  exposure)?"* — a real trading desk is never judged against that, because no
  book can actually buy flat at real-time spot; it is judged against a **shaped
  forward strip**, which is what B5 is for. **B5's benchmark is a third
  comparator, distinct from both `actual_net` and `naked_net`.**
- This naked-vs-actual comparison is **already read back into a live decision**:
  `simulation/run_phase2b.py:76` imports `company_evolve_hedge_fraction as
  evolve_hedge_fraction` and calls it every settled term at `:2067`
  (`new_hf, reason = evolve_hedge_fraction(hf, naked_net, actual_net)`), feeding
  `next_hf[cid]`. `company/policy/decision_policy.py:16-19` documents this as the
  `NAIVE_POLICY` baseline ("Hedging: `company_evolve_hedge_fraction` alone") with
  the live `CURRENT_POLICY` layering a VaR-forward `decide_hedge_fraction` *on top
  of* it (`:9-11`, "the backward-looking evolution"), not replacing it — so the
  naked/actual comparison is live in both policies today, one directly, one as a
  substrate. **This is the sharpest finding**: a metric of exactly the shape B5 is
  about to build (a benchmark-vs-actual comparison) is *already* wired into a
  hedge-fraction decision, in direct tension with the atom's own stated intent
  ("the ledger is REPORTED and never READ BACK by any hedging/pricing decision
  path", `maturity_map.yaml:2727`). Whatever R12 guard B5 builds must be proven
  against this exact precedent, not a hypothetical.

## 2. Is a shaped cost computable today? Yes — a real (not toy) first cut, not blocked on B4

Two ingredients, both checked at source:

- **(a) Demand shape**: `simulation/premise_demand.py` (module docstring `:1-9`)
  gives each premise a 48-period half-hourly demand shape off its *own local*
  weather, reconciling (by construction, `reconcile_to_national`) to national
  demand — this is real, built, load-bearing (W1_5 L2), not a stub.
- **(b) Tenor-resolved price**: `sim/forward_curve.py:138-193`
  (`generate_forward_price`) already prices an **arbitrary tenor and arbitrary
  start month**: `contract_length_months` (default 12, but callable with any
  value) and `acquisition_date` together drive `_seasonal_shape(start_month,
  contract_length_months, fuel)` (`:126`) and a `term_premium` that scales with
  `sqrt(tenor_years)` (`:191-193` onward). Calling this function once per
  calendar month with `contract_length_months=1` already yields a **month-ahead
  price ladder** — not named/tradable products, but a real per-month forward
  price, calibrated to real Elexon/NBP seasonal multipliers
  (`sim/forward_curve.py:1-9`).

**A shaped annual cost = Σ over months of (monthly demand-shape MWh × that
month's `generate_forward_price` output) is therefore computable now**, without
waiting on B4. This directly revises the atom's registered `depends_on:
[B4_traded_product_ladder]` (`maturity_map.yaml:2725`) which is BLOCKING for the
full BACKLOG DoD but not for a genuine first cut.

**What B4 actually adds** (per the sibling B4 fork's DISCOVER, consumed for this
FRAME): `company/pricing/tariff_engine.py:137-182` (`_estimate_term_structure_slope`)
already computes a wall-safe contango/backwardation slope from observable spot
EWMAs that *does* invert sign — but `company/trading/forward_book.py:184-187`
(`open_hedge`/`self._total_bid_ask_cost_gbp += contract.bid_ask_cost_gbp`) books
only **one scalar price per customer term**; no named, independently-tradable
products exist yet (B4 is `level_current: 0`, `maturity_map.yaml:2707`). So B4
will later let the shaped-cost benchmark be priced against named tenor
instruments with their own liquidity/inversion — a **depth** upgrade to the same
ledger interface, not a **precondition** for building the ledger at all.

**Recommendation: B5 is NOT hard-blocked on B4.** Build the first cut against
today's single (but already tenor-parametrised) `generate_forward_price`, keep
the pricing-source call behind one seam function so B4's ladder is a drop-in
replacement later, and keep `depends_on: [B4_traded_product_ladder]` in the map
only as *"full BACKLOG DoD needs named products"*, not as a build blocker.

## 3. Friction — what exists, what's missing, and the flattering-benchmark check

Existing, reusable friction components (none invented for this FRAME — all found live):

| Component | Where | Evidence |
|---|---|---|
| Bid-ask / execution spread | `company/trading/hedge_decision.py:26-28,93` | `BID_ASK_BASE_PCT=0.5%` + `BID_ASK_TENOR_PCT=0.2%/yr`, capped `MAX_BID_ASK_PCT=1.5%`; tracked per-book at `company/trading/forward_book.py:34,61,187,224-225,505` (`total_bid_ask_cost_gbp`) |
| Cost of capital / collateral | `sim/risk_committee.py:77,158-159` (`monthly_cost_of_capital_gbp`, `active_collateral_gbp` per customer); `company/risk/capital_adequacy.py:10` (margin-call headroom); `company/trading/initial_margin_register.py:5,37,60` (posted collateral); `company/trading/otc_margin_book.py:5` | already the same `naked_capital` term subtracted in `run_phase2b.py:2028,2038` |
| Imbalance cost | `company/market/imbalance_ledger.py:62,81` and `company/market/gas_imbalance_ledger.py:95,115` (`net_imbalance_cost_gbp`) | SBP/SSP spread noted at `company/trading/imbalance_charge_register.py:9` |

**Missing**: a distinct **shaping premium** (the extra a passive shaped-strip
buyer pays over a flat-block price for delivering the actual demand shape,
because shape itself has value in a real forward market) is not modelled
anywhere — no hit for `shaping_premium` in the tree. This is the one friction
component B5 must add rather than reuse; it should be sourced the same way
`term_premium` is (external UK forward-market shaping-premium literature/Ofgem
wholesale cost allowance methodology), never invented as a round number (R13).

**The flattering-benchmark check, done**: today's `naked_net` comparator
(§1) is reported **gross** — nothing in `hedge_policy.py` or the `annual_report.py`
hedge-effectiveness sections nets bid-ask cost, collateral cost, or imbalance
cost out of `naked_net_gbp` before comparing it to `actual_net_gbp`
(`saas/reporting/segment_report.py:150,188`: `hedging_value_add_gbp = actual_net −
naked_net`, both computed as in §1, no friction term). **This confirms the classic
defect the atom's DoD warns against is already live in the sibling metric**: the
existing "value add" number is not netted of the friction the hedging desk
itself pays to sit in a position. B5 must not repeat this — its ledger figure is
defined as `trading_pnl − shaped_cost_benchmark − friction_total`, friction
non-zero and sourced, by construction of the dataclass (not by a caller
remembering to subtract it).

## 4. Benchmark definition (one sentence)

**Shaped annual cost = the sum, over the demand shape's own time buckets (at
minimum monthly; ideally each named tenor once B4 lands), of that bucket's MWh
priced at the forward price quoted for a contract of matching tenor and start
date — the cost the book would have paid buying its own real consumption shape
as a passive strip, before any trading activity — and the value-add ledger
reports realised trading P&L minus that benchmark minus modelled day-one
friction (spread + collateral/capital cost + imbalance + shaping premium),
never gross.**

## 5. Ledger seam, clock, basis

- **Seam**: a new module (recommended `company/trading/shaped_cost_benchmark.py`,
  matching the atom's registered `file_scope`) that takes (demand shape,
  tenor-price source, friction inputs) and returns a `ShapedCostValueAdd`
  dataclass — read-only, imported by reporting (`saas/reporting/annual_report.py`,
  `segment_report.py`) the same way `hedge_effectiveness_total` is today
  (`annual_report.py:532-550,666`), **never** imported by any decision surface
  (§6).
- **Clock (R14)**: this is a **settled-clock** figure — it can only be computed
  once a term's deliveries have actually settled (`actual_net`/`hedge_pnl_gbp`
  are settlement-derived, `company/market/settlement_reconciler.py:25,34,43`),
  same clock as `net_margin_gbp` today (`tools/generate_dashboard_data.py:259,270`:
  `"clock": "settled"`).
- **R14 gate today does NOT cover a new figure of this shape**:
  `tools/generate_dashboard_data.py:1691` hardcodes
  `_BASIS_REQUIRED_PORTFOLIO_KEYS = ("net_margin_gbp", "enterprise_value_gbp")` —
  a fixed tuple, not a generic "every headline GBP figure" hook. A B5 value-add
  figure published to a report/site surface would **not** automatically be
  caught by `_check_basis_labels_present` (`:1694-1716`) unless its key is added
  to that tuple at build time. This is a real gap the atom's DoD ("reported as a
  diagnostic... R12") does not by itself close — R14 needs an explicit edit,
  not an assumption of inherited coverage.

## 6. R12 structural guard — mechanism, not promise

The reusable pattern already exists and is proven both directions:
`tests/company/test_carbon_not_a_target.py` (AST-based, `_imports_company_carbon`
walks `ast.ImportFrom`/`ast.Import` nodes — a comment or string never
false-positives, `:25-40`) scans a named list of decision-surface files
(`_SURFACE_GLOBS`, `:64-74`, including `company/risk/*.py` and
`company/pricing/*.py`) and asserts none imports the carbon module; it
self-tests both that it fires on a synthetic import (`:45-49`) and stays quiet
on clean code (`:52-56`), and guards against a silently-empty scan
(`test_decision_surfaces_exist`, `:89-93`).

**B5 must clone this exact shape** (`tests/company/test_shaped_cost_benchmark_not_a_target.py`):
a decision-surface scan asserting no file under `company/risk/*.py`,
`company/pricing/*.py`, `sim/risk_committee*.py`, or `simulation/run_phase2b.py`'s
hedge-decision call sites imports `company.trading.shaped_cost_benchmark`, with
the same both-directions self-test. **This is not decorative given §1**:
`company/risk/hedge_policy.py` is already inside the `company/risk/*.py` glob,
and it is the exact file already wired to read back a sibling benchmark
(`naked_net`) into a live decision — so the guard has a real, named target to
prove itself against, not a hypothetical file.

## 7. R15 mutation test for the value-add control

- **TAUTOLOGY**: assert the shaped-cost benchmark is computed from the demand
  shape's own MWh **times an independently-sourced tenor price**, never derived
  by re-deriving `actual_net`'s own volume/price inputs — mutation: swap the
  benchmark's price source for the company's own realised average price; the
  value-add figure must change (if it doesn't move, the benchmark is a copy of
  the actual, not an independent comparator).
- **FAIL-OPEN**: run with a friction total of `0.0` — the "value add reported
  net of friction" claim must go RED (a zero-friction ledger is a config/wiring
  defect per §3, not a legitimate degenerate case, exactly the gross-not-net
  pattern already found live in `naked_net`/`hedging_value_add_gbp`).
- **FAIL-SILENT**: the decision-surface grep-guard (§6) itself is the
  mutation-testable control — add an import of
  `company.trading.shaped_cost_benchmark` to `company/risk/hedge_policy.py` (the
  named live-precedent file) and the new test must go RED; remove the import
  and it must go GREEN. An unavailable/deleted test file must not silently pass
  (same doctrine as `test_decision_surfaces_exist`).

## 8. Exit test for level 3

1. `shaped_cost_benchmark_gbp` computed per completed run from the book's own
   demand shape and a tenor-resolved price source (today: `generate_forward_price`
   called per bucket; post-B4: the named product ladder), matching §4's
   definition exactly.
2. `friction_total_gbp` is non-zero on every run with any active hedge position,
   composed of at least spread + capital/collateral cost + imbalance cost (all
   three already sourced per §3) plus a sourced shaping premium (new, externally
   anchored per R13).
3. `trading_value_add_gbp = trading_pnl − shaped_cost_benchmark_gbp − friction_total_gbp`
   reported to the site/report surface with a `"clock": "settled"` basis label
   added to `_BASIS_REQUIRED_PORTFOLIO_KEYS` (§5 gap closed as part of BUILD, not
   left implicit).
4. The R12 grep-guard (§6) is green with its own mutation test proving it can
   fail (§7 FAIL-SILENT leg), run in the same suite as
   `test_carbon_not_a_target.py`'s pattern.
5. A test asserts the figure is genuinely independent of `naked_net`/
   `hedging_value_add_gbp` (§1) — i.e. B5's number and the existing hedge-
   effectiveness number can and do diverge on the same run data, proving B5 is
   not a relabelling of what already exists.

## 9. Recommended build shape and build order vs B4 (recommendation, not a question)

Build B5's first cut **before or alongside B4**, not after:

1. `company/trading/shaped_cost_benchmark.py`: pure function taking a demand
   shape (from `simulation.premise_demand` output) + a pluggable
   `tenor_price_fn` (defaulting to a thin wrapper over
   `sim.forward_curve.generate_forward_price` called per calendar-month
   bucket) + friction inputs (reusing `hedge_decision.BID_ASK_*`, `risk_committee`
   cost-of-capital, `imbalance_ledger.net_imbalance_cost_gbp`, plus one new
   sourced `shaping_premium` constant) → `ShapedCostValueAdd` dataclass.
2. Wire the R12 grep-guard (§6) in the same PR — never ship the ledger before
   its own control exists (this is the exact ordering mistake the atom's
   registration note already flagged as the risk).
3. Add the R14 basis-label entry (§5) in the same PR.
4. When B4 lands (named tradable tenors + inversion), swap `tenor_price_fn`'s
   default implementation to price against the named product ladder instead of
   monthly `generate_forward_price` calls — the `ShapedCostValueAdd` dataclass
   and the R12/R14 wiring do not change; only the price source does. This is
   why `depends_on: [B4_traded_product_ladder]` should be read as "B4 upgrades
   B5's price-source depth" rather than "B5 cannot start."

Do not build B4 first purely to satisfy the map's `depends_on` — that would
delay a real, honest first cut of the benchmark that is buildable today, for a
dependency that only affects the *quality* of the price source, not whether
the benchmark exists at all.
