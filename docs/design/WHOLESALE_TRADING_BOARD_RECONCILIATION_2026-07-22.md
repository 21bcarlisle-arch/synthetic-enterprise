# Wholesale & trading function — reconciliation against BOARD_SPEC_001 (for Movement 3)

**Source:** `docs/staging/BOARD_SPEC_001_WHOLESALE_TRADING_2026-07-22.md` (blind practitioner spec, VERBATIM)
+ its reconciliation instruction. **Status:** doc-and-analysis, **reversible** (the board's own tag);
findings drive **proposals** through the WHOLESALE_VALUE_CHAIN propose-then-proceed gate, **not** silent
scope change or immediate builds. Written to be read by practitioners, not the harness.

**The triangulation (the steer set this up):** three independent anchors for the same function —
1. **Board expectation** — `BOARD_SPEC_001_WHOLESALE_TRADING_2026-07-22.md` (practitioner, blind).
2. **Advisor documentary evidence** — `ADVISOR_DISCOVERY_WHOLESALE_ANCHORS_2026-07-22.md` (sourced).
3. **Primary-source DISCOVER + build audit** — this pass + `WHOLESALE_VALUE_CHAIN_FRAME.md`,
   `EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md`, `W1_6_PHYSICS_PRICE_SIGNAL_DISCOVER.md`.

**Where the three disagree, that is a finding, recorded — not a nuisance.** Each board expectation is
marked **MET / PARTIAL / ABSENT / N/A**, against the **current build** and against the **planned
VALUE_CHAIN scope** (the FRAME's WVC_1–WVC_5), with reasons and anchors. Build-state verdicts cite code;
where a verdict rests on an unverified claim it says so (R9).

---

## 0. The headline findings (the disagreements worth carrying to the board)

**F1 — GAS-FIRST is the largest single re-prioritisation, and my own FRAME got it wrong.** The board's
§1 opens: a GB *domestic* supplier is *predominantly a gas business* by energy delivered (~4× kWh gas vs
electricity; the board's typical dual-fuel figures: ~2,700 kWh elec, ~11,500 kWh gas). The entire build,
the director's own steer, and my `WHOLESALE_VALUE_CHAIN_FRAME.md` are **power-led** — the FRAME names gas
a "second commodity — product-as-first-class check" (a footnote). The board is right and this is a
material correction: **the WVC atoms must be gas-AND-power with gas as at least a co-equal primary book**,
not power-with-gas-appended. This does not invalidate the FRAME's constructs (shaped benchmark, ladder,
cover fan, value-add ledger, tariffs-from-stack all apply per-fuel) — it **re-weights** them and adds
gas-specific physics (NBP p/therm, gas day 05:00–05:00, winter-skewed seasonal, unidentified gas). It is
a scope re-prioritisation → a **proposal** via the steer's propose-then-proceed, logged here, not built
on sight. *(Advisor pre-flagged this as "the largest single re-prioritisation" — confirmed, but
narrowed:* the verification pass shows gas *market* plumbing is actually **deep** — a 7-tenor forward
curve, OTC book, SBP/SSP cash-out, storage/nominations, HDD daily shape. The real gap is two-fold: **(a)
retail gas is modelled as spot pass-through (`hedge_fraction=0`), not an actively-hedged retail book like
power**, and **(b) the FRAME/steer *framing* is power-led.** So gas-first is not "build a gas market from
scratch" — it is "make the retail gas book actively hedged and lead the value-chain constructs with the
larger fuel.")

**F2 — Collateral is a CAUSE OF DEATH, not a layer to add.** Board §3.6 puts collateral/credit *inside*
the trading desk pack (not a finance annex) and §7.4 makes "no collateral physics" disqualifying:
*"2021–22 was a liquidity event wearing a price event's clothes… suppliers died of collateral before
they died of P&L."* This **raises the priority** of the cash/working-capital/collateral-call layer from
"on the Epoch-2 horizon" to a modelled cause of insolvency: a ±30% price move must produce a **cash**
collateral call, not just a mark. Candidate: a `WVC_6_collateral_physics` atom (or fold into the
value-add loop's residual leg), proposed via the gate.

**F3 — "A profitable desk is an alarm" (§7.10) arrives independently from the practitioner side and
CONVERGES with our own degenerate-emergent-behaviour law.** Two independent derivations of the same law
strengthen both — record the convergence. It also aligns with **R12 (anti-goal-seek: margin is a
diagnostic, never a target)** and §4/§6's "cost centre not profit centre; cost flows forward into price,
price never backward into cost." The FRAME's **value-add ledger (WVC_4) measured vs a mechanical
benchmark** is exactly the board's §4 discipline ("discretion must prove itself against the robot").

**F4 — The board's §5 cost stack construction IS the FRAME's shaped-cost benchmark, independently
specified** — and it adds three lines the FRAME under-weighted: **losses/UIG grossing-up**, an explicit
**shape/imbalance premium over baseload** (the board: "if the model prices a domestic shape at the
baseload price, everything downstream is flattered"), and the **wholesale-riding obligations (RO, CfD,
CM)**. Fold into WVC_1/WVC_5's stack decomposition.

---

## 1. Products & conventions (board §1) — vs planned scope + build

| Board expectation | vs FRAME scope | vs build | Reason / anchor |
|---|---|---|---|
| Two commodities, **gas first** (~4× kWh) | **PARTIAL (finding F1)** | POWER-LED | FRAME treats gas as second commodity; build's gas is thin (see §7.1). Re-prioritise. |
| Gas NBP p/therm, gas day 05:00–05:00, seasons S(Apr–Sep)/W(Oct–Mar) | PARTIAL | see §7.1 | `company/trading/gas_forward_curve.py` `GasTenorBand` has the tenors; day-convention/depth TBC by scout. |
| Power baseload (all hrs) + peak (wd 07:00–19:00), seasons/qtrs/months → DA → within-day → imbalance | **MET-in-plan** | PARTIAL | FRAME §3.2 unifies exactly this ladder; build has the silos (`ShapeBand`, DA/intraday books). |
| **Shape residual** bought progressively to delivery; shape+imbalance premium over baseload = a real cost line | **MET-in-plan (WVC_1/3)** | see §7.2 | FRAME §3.1/§3.4 makes shape premium explicit; board warns near-zero premium = broken. |
| Adjacent obligations (REGO/RO/CfD/CM, **loss factors**) in the stack | PARTIAL | see §7.7 | FRAME §3.4 names policy/network lines; losses/UIG under-weighted (F4). |

## 2. Hedge policy by tariff type (board §2) — the fixed vs SVT split

- **Fixed book back-to-back at acquisition; manage residuals (churn/volume/weather); ±5% tolerance
  band.** vs FRAME: **PARTIAL** — the FRAME's cover fan (WVC_3) and hedge program cover this in spirit,
  but the FRAME does **not** yet split hedge *logic by tariff type*, and the **churn-leaves-the-book-long
  correlation** (the fixed book's "poison") is a specific mechanism to add (see §7.6). **Finding:** add
  the fixed/SVT hedge-logic split to WVC_3 explicitly.
- **SVT book replicates the cap: buy in tranches mirroring the cap's observation window; deviation = a
  speculative position against the regulator's index, sized/authorised/stop-lossed.** vs FRAME:
  **PARTIAL** — FRAME §3.1/§8.1 already frames scoring achieved cost vs the cap allowance and keeps the
  published cap as an observable, and the advisor evidence gave the 3-1.5-12 window; but the **mechanical
  cap-tracking hedge ladder** is not yet an atom. **Finding:** the SVT-replicates-the-cap ladder is a
  concrete WVC_3 sub-mechanism; cap observation-window mechanics are a build dependency (see §7.8).
- **Written ladder: target ratio by horizon, tolerance bands, delegated authority, stop-loss, no naked
  shorts; desk shows actual-vs-policy any morning.** vs build: the desk-pack surfaces (FRAME §5) render
  actual-vs-policy; delegated-authority/stop-loss governance is absent (a real supplier control, propose).

## 3. The weekly desk pack (board §3) — vs the FRAME's desk-pack surfaces

The board's 7-item Monday pack and the FRAME's §5 desk-pack surfaces are the **same artefact seen from
two sides**. Mapping (P = position-vs-policy, etc.):
1. Position vs policy (hedge ratio by month/fuel vs ladder + band; NOP) → FRAME "cover fan" + "fixed/var
   split". **MET-in-plan.**
2. Cost vs market **and vs allowance** (WACOG vs curve MtM; SVT vs accruing cap allowance = the default
   book's gross margin) → FRAME "value-add ledger". **MET-in-plan**, and item-2's cap line sharpens
   WVC_4: the achieved-vs-allowance line *is* SVT gross margin.
3. Demand (weather-normalised forecast, actual-vs-forecast error, churn/acquisition vs plan, EAC moves)
   → forecasting leg of the loop. **PARTIAL** (forecast-error attribution to be built, WVC_4).
4. Risk (VaR + named weekly stress: 2021 rally, 1-in-20 cold, demand-price joint) → **PARTIAL**; VaR
   exists (`hedge_decision.py`), the weekly named-stress-with-cash-consequence pack is absent.
5. Imbalance & shape (imbalance % of demand, cost/MWh vs DA ref; shape achieved vs assumption) →
   **PARTIAL**; imbalance exists (see §7.7), shape-achieved-vs-assumption is a WVC_1 output.
6. **Collateral & credit** (margin posted, Elexon cover, facility headroom, projected call under ±30%)
   → **finding F2**; see §7.4.
7. Market backdrop (curve moves, gas storage/LNG, vol) → one-page context. **PARTIAL/ABSENT.**

**Finding:** adopt the board's 7-item pack ordering as the desk-pack surface spec (the director's
believability axes, FRAME §5) — it is a more complete and practitioner-legible list than the FRAME's
five.

## 4. Where value is created (board §4) — the cost-centre discipline

**MET-in-principle, strongly.** The board's "risk-management **cost centre**, not a profit centre" and
its four value loci (execution-vs-ladder, forecast accuracy, shape/imbalance, avoiding distressed trades)
map directly onto the FRAME's **value-add ledger vs a mechanical benchmark (WVC_4)** and onto R12. The
board's **P&L attribution into price/volume/shape/timing/imbalance** is a sharper decomposition than the
FRAME's timing/shape/volume/roll — **adopt the board's five-way split**. See F3 (profitable-desk alarm)
and §7.10.

## 5. The annual cost stack (board §5) — the shaped benchmark, independently specified

**MET-in-plan (WVC_1) — this is the FRAME's spine, arrived at independently by the board.** The board's
6-step construction (shape → shape-weighted curve incl. peak/shape premium & winter-gas → gross up for
losses/UIG → shaping/imbalance allowance → RO/CfD/CM → the wholesale line above networks/policy/opex/
margin) *is* the shaped-cost benchmark, and it **adds losses/UIG and the wholesale-riding obligations**
the FRAME under-weighted (F4). Its watched ratios (achieved-vs-cap-allowance; **shape premium as % of
baseload — single digits when sane, near-zero = broken**; winter/summer spreads; forward premium over
realised spot mid-single-to-low-double-digit %; imbalance cost/MWh vs DA; forecast error by horizon)
become **WVC-1/WVC-4 sanity bands** (R12: diagnostics, not targets). **Adopt the board's ratio set.**

## 6. Stack → retail price (board §6) — tariffs from the stack

**MET-in-plan (WVC_5).** The board's fixed = cost-plus off a **live curve** (+ explicit risk premia
incl. the **customer's free churn option** — "they leave if the market falls, stay if it rises; that
asymmetry has a price") and SVT = cap-constrained (hedge-tracks-allowance is the real question) map onto
FRAME §3.4. The board's governance law — **"cost flows forward into price; price never flows backward
into cost; margin is an output not a target"** — is R12 + the FRAME's §3.4 pricing-committee separation.
Two additions to fold: (a) the **stale-quote free-option** hazard ("re-price at least daily in volatile
markets") → a WVC_5 control; (b) the **churn-option risk premium** as an explicit stack line.

---

## 7. The credibility battery (board §7) — the standing practitioner fidelity oracle

**Recommendation (advisor-flagged, endorsed):** register these 12 as a **standing practitioner fidelity
oracle**, peer to the regulatory-rules oracle — every test exists because the failure it names actually
kills suppliers (the R15 spirit: a control that cannot fail is worthless; each of these names a concrete
defect). Verdicts below are against the **current build** (anchors from the verification pass); "claim
MET only with proof cited."

Each item is a *disqualifier* (a failure mode); verdict = **does the build avoid it?** PASS (credible) /
PARTIAL / FAIL. Anchors from the verification pass.

| # | Disqualifier (board §7) | Verdict | Proof / anchor |
|---|---|---|---|
| 1 | Gas missing or subordinate | **PARTIAL** | Gas *market* plumbing is deep, not "a thin series": 7-tenor curve w/ bands + crisis flag (`gas_forward_curve.py:29-119`), OTC book (`gas_otc_book.py:80-148`), SBP/SSP cash-out (`gas_imbalance_ledger.py:51-56`), storage/nominations/interruption, HDD daily shape (`sim/weather_hdd.py`). **But retail gas is modelled as spot pass-through, `hedge_fraction=0`** (`tests/simulation/test_gas_pass_through_hedge.py`), while power carries an evolving hedge (`sim/hedging_strategy.py:26-34`) — gas is a deep market book but **not an actively-hedged retail book**, and the whole framing is power-led → **finding F1**. |
| 2 | No shape residual | **PARTIAL** | Baseload/peak distinction exists (`shape_risk_book.py` `ShapeBand`) with DA/intraday books; but the **shape/imbalance premium over baseload as an explicit cost line** is FRAME-planned (WVC_1), not confirmed built. Board: near-zero shape premium = broken. |
| 3 | Any look-ahead in hedging inputs | **PASS** | Genuine adversarial mutation test (`tests/interfaces/test_observable_trace.py:51` future record → `None`), PreToolUse enforcement hook (`.claude/hooks/block_point_in_time_read.py`, tested), traces to a real caught foresight bug. |
| 4 | No collateral physics | **PARTIAL** | Rich cash-consequence *ledgers* — variation-margin `cash_impact_gbp` (`otc_margin_book.py:65-78`), additional calls (`initial_margin_register.py:106`), MtM-vs-collateral netting (`wholesale_credit_exposure.py:70-75`), finite facility + stress flag (`finance/margin_call_book.py:34-39`). **But the price-move→margin-call causal loop is NOT wired** — `mark_to_market(price)` never drives a call; `record_call` takes a hand-supplied loss → **finding F2**. |
| 5 | Demand and price independent | **PASS** | Joint tail proven from a *shared weather draw*: cold→price (`weather_price_triad.py`, `sim/weather_price_chain.py`) + cold→demand (`weather_demand_triad.py`), joint severity demonstrated (`sim/weather_tail_demonstration.py` "a joint tail, never two marginals"). Caveat: structural proof, no replayed named-2018 event. |
| 6 | Churn uncorrelated with market | **PARTIAL** | SVT-swell-on-spike PASSES (`churn_model.py:100-140` `CRISIS_PASSIVE_YEARS={"2022"}`; market multiplier `market_conditions.py:24`). **But "fixed customers leave when the market falls below their fix" is ABSENT** — no in/out-of-money logic; churn keys off the customer's own `rate_increase_pct`, not live wholesale-vs-locked-rate → **risk-correlation finding**. |
| 7 | Benign imbalance, always | **PASS** | Imbalance spikes: NIV stress premium 1.2, SSP → £9,999/MWh in crisis (`company/market/imbalance.py:27-55`). |
| 8 | Cap mechanics absent/hand-waved | **FAIL** | `company/pricing/ofgem_price_cap.py:25-52` is a **static per-year dict** — no observation window, quarterly reset, or achieved-cost-vs-allowance tension. Build dependency for the SVT-replicates-the-cap ladder (§2). |
| 9 | Infinite liquidity | **PARTIAL** | Bid-offer modelled (tenor-widening spread, bought at ask not mid — `hedge_decision.py:24-28,87-94`); **no clip size / market depth / liquidity limit anywhere** (grep clean). Spread yes, depth no. |
| 10 | A profitable desk (no alarm) | **FAIL (spec-only)** | The "cost-centre-not-profit-centre / beating-the-market is leakage" law exists **only as documentation** (this spec + reconciliation) — no code enforces it → **finding F3**: build the desk-profit alarm as an R15-failable check. |
| 11 | No losses / UIG / estimate error | **PASS** | All three: line-loss factors to 1.12 (`llf_register.py:41-62`), monthly UIG allocation (`uig_allocation_register.py:19-43`), EAC drift (`eac_drift_assessor.py:44-62`), billed-vs-metered reconciliation (`back_billing.py`, `settlement_reconciler.py`). |
| 12 | Everything exactly 100% hedged | **PARTIAL** | Power book breathes: floor 0.85 + bounded evolution in [0.85,1.0] (`sim/hedging_strategy.py:64`), population 0.80–0.90 — not pinned at 100%. But it's a hedge-*fraction* floor, not an explicit ±% **volume tolerance band** (board §2), and gas retail is 0% pass-through. |

**Tally: 4 PASS (3,5,7,11) · 6 PARTIAL (1,2,4,9,12,6) · 2 FAIL (8,10).** The two hardest gaps are the
**unclosed price-move→cash-call loop (item 4 / F2)** and **churn lacking a live wholesale-vs-fix trigger
(item 6)** — precisely the *risk correlations* the board's Chair says are where the excitement should
live. Recommend registering the battery as a standing R15-failable practitioner fidelity oracle so each
verdict is re-measured, not asserted once.

---

## 8. What goes to Movement 3 (the net)

The board's closing is the headline: **competence here looks _boring_** — mechanical ladders, cap
replication, attribution tables, collateral headroom — **and the excitement lives in the risk
correlations, not trading brilliance.** The reconciliation's net:
- The FRAME's spine (shaped benchmark, ladder, cover fan, value-add-vs-benchmark, tariffs-from-stack) is
  **independently corroborated** by the board — build it.
- **Four findings re-shape scope (proposals, not silent change):** F1 gas-first (largest), F2 collateral
  as cause-of-death, F3 profitable-desk-alarm convergence (a law confirmed), F4 losses/UIG + shape
  premium + obligations in the stack. Plus the fixed/SVT hedge-logic split (§2) and the churn-market
  coupling (§7.6) as the risk correlations the board says the excitement lives in.
- **Battery → standing fidelity oracle** (§7), R15-failable, peer to the regulatory oracle.

*All scope changes route through the WHOLESALE_VALUE_CHAIN steer's propose-then-proceed (2h veto); this
reconciliation is analysis, and authorises nothing to build.*
