# A forward hedge executes at the market's quote, not the company's own forward estimate — K8 note
**Knowledge:** hedging-forward-market

**Purpose:** K8 knowledge-before-build note for
`docs/staging/SEAT_FINDING_THE_DEFAULT_TARIFF_SEGMENT_FORMS_ITS_OWN_FORWARD_2026-10-12.md`'s
"better reading, filed and not built": should `company/trading/hedge_desk.open_term_hedge`'s
`agreed_price_gbp_per_mwh` be the market's point-in-time forward
(`sim.forward_curve.generate_forward_price`) rather than the company's own belief
(`company.pricing.tariff_engine.CompanyTariffEngine.get_forward_price`, reached via
`request_company_forward_estimate`)? Written before the code change it authorises, per K8.

**Knowledge:** none -- no dedicated hedging/trading knowledge-site topic exists yet; this note's
conclusion is recorded in the build commit that acts on it and in this file, per K8, until one is.

**Date:** 2026-10-12. **Method:** reading the two forward-price code paths plus the already-sourced
counterparty/market-structure research at
`docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md` (RQ1, RQ3 —
cleared-exchange and bilateral-OTC execution mechanics, ICE/ECC/LCH, fetched 2026-07-24). The core
fact this note turns on is basic derivatives-market structure (K4: "too obvious to anyone in the
industry to be written down anywhere" as a numbered benchmark) rather than a figure needing a fresh
live fetch: **a forward contract's price is set by whoever is on the other side of the trade — the
exchange's matched order book or the bilateral counterparty's quote — never by the buyer's own
internal valuation model.** That is what distinguishes a *quote* from an *estimate*; it is the
entire reason ICE publishes a dealable screen price rather than suppliers marking their own books at
whatever number they like.

## What the two forward numbers actually are

`sim.forward_curve.generate_forward_price` (world) and
`company.pricing.tariff_engine.CompanyTariffEngine.get_forward_price` (company, reached through
`company/interfaces/renewal_offer.request_company_forward_estimate`) are **two independent models
over the same observable input** — published settlement-price history (Elexon SSP / NBP-proxy). Not
one ground-truth number and one approximation of it: different lookback windows, different seasonal
tables, different risk/regime premia, deliberately uncoupled (the company engine "never imports
sim/forward_curve.py", per its own docstring). Both are PIT-safe — the world's model as documented in
`sim/forward_curve.py`'s own header (EWMA of spot × seasonal shape × term premium, strictly
backward-looking), the company's identically so by construction.

Because the world's model is built only from published settlement history, by the same test the
project already applies elsewhere (K2/the epistemic wall: "could a real UK supplier know this?"),
**it is not simulation-internal ground truth that must stay behind the wall — it is the thing a real
market quote would track.** A UK supplier's trading desk does not run `generate_forward_price`
itself, but it calls a broker or checks an ICE/EEX screen, and what comes back is a number built the
same way: a model over public settlement history, quoted by whoever is willing to trade at it. The
world's `sim_fwd` stands in for that quote in this simulation. It crosses already, as a plain float,
every time `run_phase2b.py`/`svt_product.py`/`renewals.py` writes a schedule term's
`forward_price_gbp_per_mwh` field and hands the dict to `company/interfaces/renewal_offer.py` as
`fallback_forward_price_gbp_per_mwh` — this is not a new crossing, only a new USE of a value that
already crosses.

## Where each number belongs, and why that is two different questions

1. **What the company believes the forward is, for pricing the customer's tariff.** This is squarely
   the company's own judgement — its risk appetite, its margin target, its own (possibly wrong) read
   of where the market is headed — and it is right that this stays `company_fwd`
   (`CompanyTariffEngine`), reached only from observables. `request_fixed_unit_rate` /
   `strike_fixed_unit_rate` / SVT's `company_forward_price_gbp_per_mwh` field are correctly scoped
   here and this note does not touch them.

2. **What the company believes the forward is, for SIZING the hedge (the VaR decision,
   `decide_term_hedge`).** Also the company's own judgement call — how much to hedge against is a
   function of the company's own view of risk, which may legitimately differ from the market's quote
   (that gap is exactly what a trading desk is paid to judge). `company_fwd` stays here too; this
   note does not touch `decide_term_hedge`'s `forward_price_gbp_per_mwh` argument, which the
   mutation-proven AST control in `tests/company/interfaces/test_hedge_desk_seam.py`
   (`test_control_3_each_call_site_passes_its_own_commodity_and_its_own_locals`) already pins to
   `company_fwd` by name, for both commodities, and should keep pinning there.

3. **What the company is actually CHARGED when it executes the hedge — `open_term_hedge`'s
   `agreed_price_gbp_per_mwh`, which feeds the bid-ask spread cost and every period's realised hedge
   P&L in `TradingBook.settle_period`.** This is not a judgement call. A counterparty does not care
   what the company's internal model says the forward is worth; the company pays the market's price
   or it does not get the hedge. Pricing this leg off `company_fwd` means the simulated hedge P&L
   measures `(company's own belief − actual spot) × hedged_MWh` instead of
   `(market's quote − actual spot) × hedged_MWh` — it silently erases the real-world risk that the
   company's own forward view can be wrong RELATIVE TO THE MARKET, not just relative to outturn spot.
   M2's "value is created and then shared… transfer is not creation" cuts the same way here: if
   `company_fwd` happens to run above or below the market's quote, charging the hedge P&L calculation
   the belief rather than the quote transfers that gap into or out of the reported trading P&L
   without it ever being a real transaction.

## Decision

**`agreed_price_gbp_per_mwh` (and therefore the `forward_price_gbp_per_mwh` argument to
`open_term_hedge`, which also prices the bid-ask spread) should be the world's PIT forward
(`forward_price`/`sim_fwd` — the value already written into every schedule term's
`forward_price_gbp_per_mwh` field) on both products, wherever a hedge is actually opened.**
`decide_term_hedge`'s sizing input and the tariff-pricing strike stay on `company_fwd`, unchanged. No
new seam file: the value already crosses as a plain float through the existing
`forward_price_gbp_per_mwh` parameters on `company.trading.hedge_desk.HedgeDesk`, called from
`simulation/run_phase2b.py` via the `company/interfaces/hedge_desk.py` door exactly as today — only
WHICH already-in-scope local variable is passed to `open_term_hedge` changes. The one thing that
does need correcting is `open_term_hedge`'s own docstring, which currently claims its inputs are
"both company-observable, neither read from the world" — after this change that is no longer true of
`agreed_price`, and the docstring must say so plainly rather than leave a stale claim next to the
code it no longer describes.

## What stays open (not built here)

Gas never calls `open_term_hedge` or `settle_period_pnl_gbp` at all — only `decide_term_hedge` (the
sizing decision). No `ForwardContract` is ever booked for gas, in any tariff type, so gas hedge P&L
is not merely priced off the wrong number — it is not computed at all. That is a materially bigger
gap than the one this note closes and should not be patched as a side effect of this change; it is
recorded here so the next reader does not mistake "both products now correctly priced" for "both
products book a hedge," which this change does not make true.

**Checked before deciding, not after:** every reader of `hedge_pnl_gbp`
(`simulation/run_phase2b.py`'s per-record field, `saas/reporting/annual_report.py`'s
`_section_trading_pnl`, `company/market/settlement_reconciler.py`'s self-consistency check) and of
the book's own `total_hedge_pnl_gbp` (`company/trading/forward_book.py::TradingBook.summary`).
`TradingBook.settle_period` increments `_total_pnl_gbp` by the exact value it returns, and
`run_phase2b.py` has exactly one call site for `settle_period_pnl_gbp` (electricity fixed/
pass-through/SVT, inside the `else` branch at the hedge-execution block), so the per-record sum in
the annual report's `_section_trading_pnl` and the book's own `total_hedge_pnl_gbp` are the same
total by construction on the current call graph — the item's "a reporting decomposition that no book
total summed" describes a risk that is live (the report computes its own sum rather than reading
`trading_book["total_hedge_pnl_gbp"]` directly, so a future second call site would silently diverge
the two) rather than a present discrepancy. Not fixed here (it is a robustness improvement, not part
of this decision), but worth a follow-up atom: have `_section_trading_pnl` read
`trading_book.get("total_hedge_pnl_gbp")` as the headline figure and compare it against its own
per-record sum as a cross-check, rather than trusting the per-record sum alone.
