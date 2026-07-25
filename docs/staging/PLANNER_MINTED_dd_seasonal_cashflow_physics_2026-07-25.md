# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — Per-customer level-DD seasonal cash-flow physics (2026-07-25)

**Provenance:** processing of `DIRECTOR_STEER_DD_SEASONAL_CASHFLOW_2026-07-25.md` (director domain steer, advisor bridge). FRAME-first per the steer; this doc IS the "then propose" half. The steer is parked to `in_progress/`; this minted proposal is its drawable successor.

**Serves:**
- **DIRECTOR_AXES axis 3 (Believability)** — the level-DD seasonal credit cycle and the cash-rich-but-insolvent trap are precisely what a 20-year UK-supply veteran expects and would notice missing. Also pre-stages the **Billing + CRM roadmap rotation** (`DIRECTOR_AXES.md §Roadmap`).
- **MC-2 death-loop fidelity** — the steer's own words: "the SIM cannot claim to reproduce 2021–22 without it." Held customer-credit balances + the growth-funds-drawdown structure are a documented cause of UK supplier failure; this is the customer-cash-physics substrate the reserved growth/leverage session needs.
- **Fidelity ledger** — extends the live-money-flow evidence family (`live_payment_detection_gap` row) from *collection detection* into *held-credit solvency*; a new ledger row is added by sub-atom DD-H below.

**Fidelity gained (one sentence):** the company moves from a Variable-DD / pay-on-bill engine that cannot hold customer money to a level-DD engine where each customer's cash builds credit in summer and draws down in winter, that credit is booked as a **liability**, and cash-rich-but-insolvent becomes visible — the substrate of the real UK supplier solvency cycle.

---

## FRAME — what the billing organ does TODAY (established, evidence-cited)

Verdict, plainly: **the live engine is a Variable-DD / pay-on-bill engine, not level DD.** It bills the exact metered consumption each cycle and collects that exact amount, tracking only a billed-minus-collected *arrears* position per customer. Every ingredient of a genuine level-DD seasonal-credit cycle exists only as isolated, mostly-dead scaffolding.

| # | Requirement dimension | Today | Evidence |
|---|---|---|---|
| 1 | DD payment model | **Variable DD** — collects the exact bill, never a fixed amount | `simulation/dd_collection_book.py:98-101` ("always WAS Variable DD"); `saas/bill_generator.py:159`. Level-÷12 math is dead (`company/billing/dd_review.py:30-33`) or closure-only trailing-mean (`simulation/credit_refund_events.py:63`). `mandate.monthly_amount_gbp` is "an estimated reference level that never sizes or gates a collection" (`dd_collection_book.py:105-109`). |
| 2 | Staggered anniversaries | **Common calendar month** for billing/collection; entry staggered by acquisition only | `simulation/run_phase4c_on_phase2b.py:98-100,315-318` (calendar-month buckets). `payment_day` (1–28) field exists but is **dead code** — no live caller (`dd_mandate_register.py:102`; `dd_collection_book.py:118-121`). |
| 3 | Per-customer balance trajectory | **Arrears position only** (`billed − collected`), not summer-credit/winter-drawdown | `company/billing/payment_ledger.py:161-168` (`balance = paid − total_billed`). Because collection = exact bill, a paying customer sits ≈ £0. Richer rolling ledger `company/billing/account_ledger.py:249-257` is **unwired** (zero live callers). |
| 4 | Non-zero starting balance | **Absent** — customers start at zero by construction | No `initial/opening/welcome` per-customer balance anywhere; ledgers seed empty (`payment_ledger.py:106-107`; `account_ledger.py:227-229`). |
| 5 | Credit balance as a LIABILITY | **Absent** — only VAT Payable is a liability | `company/finance/double_entry.py:22,279` (`total_liabilities = vat_payable`). `sfr_book.py:53` `credit_balance_cover_pct` is a passed-in parameter, not a computed held-credit position. |
| 6 | Annual DD review event | **Absent as a live event** — full logic exists but is dead code | `company/billing/dd_review.py` complete (variance ±5%, ÷12, `overdue_for_review(months=12)`) but **zero importers**. `RefundTrigger.ANNUAL_CREDIT_REVIEW` defined, never raised (`credit_refund_events.py:113` fires closure only). |
| 7 | Three clocks + credit position | **Three clocks rendered; NO held-credit liability tile** | `saas/reporting/css_statement.py:490-492` (billed/settled/banked); `site/customers/index.html:208-211`. The shown "Balance" is the arrears position (dim 3), not held customer credit owed back. |

*(Full FRAME with quotes: derived this tick; the table above is the load-bearing summary.)*

---

## PROPOSE — the mechanism (decomposed, forward-only, typed-seam preference)

Design principle: **this is fidelity, not a difficulty knob (R12/R13).** Level (Fixed) DD is the UK domestic market *norm* — the current Variable-DD-only engine is the *simplification*; modelling level DD is a fidelity-to-reality change decided blind to company P&L. No number is tuned toward any target. Fixed and Variable DD **coexist** (real suppliers run both; payment-method stays first-class per the portability constraint). The growth-timing solvency *analysis* and the seasonal-DD *product* are RESERVED (below) — this builds only the customer-cash physics those sessions will need.

**DD1 — Level-DD mandate + staggered anniversary (seam change).** Give each customer a Fixed-DD mandate whose `monthly_amount_gbp` actually **sizes the collection** (estimated annual ÷ 12), and a `payment_day` distributed across 1–28 (wire the dead field). Collection cycles on the customer's own anniversary, not the shared calendar month. `dd_collection_book` collects the mandate figure for Fixed-DD customers; Variable-DD path unchanged. *Proposed level target: L2.*

**DD2 — Per-customer running credit/debit balance, carried tick-by-tick.** Wire a rolling per-customer balance (activate `account_ledger.py` or equivalent behind the existing seam): each cycle `balance += collected − actual_bill`, building credit through summer and drawing down through winter against that household's seasonal shape. Seed a **non-zero opening balance** at acquisition (fed by `W2_12_change_of_tenancy_debt_physics` — do NOT duplicate). Deterministic + idempotent replay (C-S2); opening-balance draws use a **named RNG substream** (C-S2 substream discipline). *Proposed level target: L3.*

**DD3 — Held customer credit as a LIABILITY.** Add a "Customer credit balances held" liability account to the double-entry chart (today only VAT Payable). Book the aggregate of positive per-customer balances as a liability; treasury cash that includes held customer credit is money **owed back**. *Proposed level target: L2.*

**DD4 — Annual DD review as a first-class event.** Wire `dd_review.py`: at each customer's anniversary + 12 months, re-estimate the level payment vs actual consumption (variance ±5%), emit an **event with consequences** — a large increase routes to the existing satisfaction/complaint/churn organ. This is "estimate meets reality." *Proposed level target: L2.*

**DD5 — Site: credit-balance liability position alongside the three clocks.** Requirement #2's surface half. Add the held-customer-credit position (labelled a **liability**, visually distinct from treasury) beside billed/settled/banked so a treasury figure never stands alone; the cash-rich-but-insolvent tell is legible. R11 render-verified on the live surface. *Proposed level target: L2.*

**DD-H — HARNESS (coupled triad).** The gap organ: the company's *belief* about its solvency (cash on hand) vs the *truth* (cash minus held customer credit owed back). A company can believe itself solvent while insolvent; that belief-vs-truth gap IS the score. New fidelity-ledger row + gap reported per digest. Per COUPLED_TRIAD, this capability is not complete until it faces a world that can defeat it — the growth-stall / wholesale-spike world (reserved to growth/leverage). *Proposed level target: L2 (sensing), gap-only, no write.*

**Sequencing:** DD1 → DD2 (needs DD1's collection) → DD3 (needs DD2's balances) → DD4 (independent, parallel-able) → DD5 (needs DD3) → DD-H (needs DD2/DD3). Each is disjoint enough for the L1 serial/worktree discipline; DD4 can run parallel.

---

## RESERVED — do NOT build now (register only)

- **Variable/seasonal DD product** (higher winter / lower summer, tracks true consumption, removes the annual-review shock — but *not* the market norm; customers do not expect it). This is a candidate **personalisation product** for the **growth/product session**; the true-need-vs-market-norm gap is itself the modellable phenomenon and arguably where the product opportunity sits. **Registered here as a candidate; not built ahead of that session.**
- **Growth-timing solvency analysis** (how acquisition seasonality interacts with solvency and the MC-2 collateral loop — the Ponzi structure). **Reserved to the registered growth/leverage session** (see `DIRECTOR_RULING_MC2_REAL_HISTORY_NOT_DIFFICULTY_2026-07-25.md`). Build the physics here; the analysis is that session's.

---

## Walls honoured

Epistemic (all seven dimensions are company-side observables — the company runs its own DD product, holds its own cash, does its own annual review; no SIM internal is read). R12 (no number tuned to a target). R13 (level DD is a fidelity change decided blind to P&L, not a curriculum/difficulty dial). Portability (payment-method first-class; Fixed/Variable coexist). C-S2 (deterministic replay + RNG substream on opening-balance draws). One-way doors: none (all reversible; git reverts). Curriculum values / growth trajectory / seasonal-DD product: director-reserved, untouched.

## Propose-then-proceed window

**48h from 2026-07-25.** If the director/advisor does not revise the requirements or reserved boundary within the window, the DD1–DD5 + DD-H build proceeds (drawn as staged RUNG-1 work; each sub-atom registered to the maturity map at build-draw with the proposed level targets above, subject to the pre-commit level gate — agent builds L3-quality code but leaves level moves as `blocked_on: director_level_up`). Growth analysis and the seasonal-DD product stay reserved regardless.

— Minted this tick from the director's DD seasonal-cashflow steer, FRAME-first.
