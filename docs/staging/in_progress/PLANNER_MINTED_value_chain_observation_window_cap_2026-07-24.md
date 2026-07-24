# [PLANNER-MINTED] VALUE_CHAIN: replace the static cap dict with real observation-window mechanics + MC-2 collateral death-test (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 2 — PRODUCT-FIRST item 3, the declared static-cap FAIL + MC-2 collateral death-test). No map atom yet (tracked in `docs/PRIORITIES.md` item 3 + steer `DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md`); register on BUILD open.
> **BLOCKING SUB-ITEM (open):** ~~Scope 1 (FRAME the static-cap call sites + name through-the-wall observable inputs)~~ **DONE this tick — see the FRAME section appended below.** Scope 2-3 BUILD (observation-window cap + MC-2 death-test) proceeds under reversible authority, **but the MC-2 scenario *difficulty* is R13 curriculum — escalate any difficulty knob, never tune** (mint the mechanism + a benign default only). **UNBLOCKS:** self for the mechanism; director for any named curriculum-difficulty value. **FRAME surfaced a prerequisite:** both target registers (`WholesaleCreditExposureRegister`, `MarginCallBook`) have **no live (non-test) constructor** — they are modelled organs not yet in the run loop, so an observation-window cap has nothing to observe until the register is first fed the company's own live MtM/margin-call stream. The next drawable BUILD step is therefore the **live feed**, then the window mechanic on top; details in the FRAME.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 empty this tick. **Propose-then-proceed.**

## Ratified goal served
- **DIRECTOR_AXES v1 — Axis 3 (Believability):** *wholesale products and prices ... does it feel like the real UK market to a 20-year veteran.* The 20-year-veteran smell test is the acceptance bar.
- **PRIORITIES.md PRODUCT-FIRST item 3 (verbatim):** *"VALUE_CHAIN first organs — replace the static cap dict with real observation-window mechanics (a declared FAIL); build the MC-2 collateral death-test (work-ordered, not built)."*
- Steer of record: `docs/staging/in_progress/DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md` (shaped-cost benchmark, cover fan, cash-collateral death-loop).

## The declared FAIL being closed
The credit/collateral cap is currently a **static dict** — a hard-coded number standing in for what a real supplier's counterparties actually grant, which moves with observed trading history and mark-to-market exposure. A veteran reads a fixed cap as a tell that the collateral mechanics are cosmetic. Replace it with **observation-window mechanics**: the cap is *earned/eroded* from the book's own observed exposure over a rolling window (through the wall — the company observes its own margin calls and counterparty behaviour, never reads sim internals).

## Real-world fidelity gained
- The cash-collateral death-loop (a real supplier's most acute failure mode: a price spike triggers margin calls that drain cash faster than the hedge protects the book) becomes a *live physics of the run*, not a static parameter. This is the front-door promise — *"the cash-collateral death-loop ... still to come. It can be wrong, and it can die."* — made real.
- **MC-2 collateral death-test:** a named death-scenario (a spike that forces margin calls exceeding available liquidity) that the company can actually fail — an R15 control that fires on its own defect (a company that *can't* die to collateral is a fail-open believability control).

## Scope (propose)
1. FRAME: read the current static-cap call sites; name the observable inputs (own margin calls, MtM exposure, posted collateral) the window may use — confirm each is a through-the-wall observable, none a sim internal.
2. BUILD observation-window cap: rolling-window cap driven by observed exposure, behind the existing typed seam; no counterparty hardcoding (portability lens).
3. BUILD the MC-2 death-test: a spike scenario draining liquidity past the cap → the company enters collateral distress / can die. R15: the test PASSES (company survives) on a benign path and FAILS (company dies) on the MC-2 path — the control can fail.
4. Verify: epistemic-verifier on the diff; full suite for company/billing|risk paths.

## Walls untouched
Curriculum values / the MC-2 scenario *difficulty* is director-owned if it becomes a named curriculum world (R13) — mint the mechanism and a benign default; flag any difficulty knob to the director rather than tuning it. No L3 self-promote. No one-way door.

## Propose-then-proceed window
Standing PRODUCT-FIRST reversible-build authority; proceed. Escalate only the irreducible core (a curriculum-difficulty value) via NTFY while continuing to draw.

---

## FRAME (Scope step 1) — 2026-07-24 worker tick

**Method:** grep for the static cap constructs across `company/trading/`, `company/risk/`, `company/finance/`; read the two organs; grep for live (non-test) constructors. Evidence is file:line below.

### 1. The static caps (the declared FAIL, located)
- **`company/trading/wholesale_credit_exposure.py:51` — `_CREDIT_LIMIT_BY_RATING`**: a hardcoded `Dict[CounterpartyCreditRating, float]` (AAA £5.0M → UNRATED £0.1M). Read via `WholesaleCreditRecord.credit_limit_gbp` (`:81`), which drives `utilisation_pct` (`:87`), `is_limit_breached` (`:93`), `headroom_gbp` (`:97`). This is the "static cap dict" of the ruling verbatim — a fixed number standing in for what a counterparty's CSA actually grants.
- **`company/finance/margin_call_book.py:39` — `MarginCallBook.__init__(credit_facility_gbp=5_000_000.0)`**: a second static cap — the liquidity facility the death-loop drains against. Drives `headroom_gbp` (`:65`), `is_liquidity_stressed` (`:68`), `stress_events` (`:71`). The MC-2 death-test lives against THIS cap (liquidity), while the credit dict is the counterparty-exposure cap — two distinct caps, don't conflate.

### 2. Prerequisite surfaced (material) — the organs are not in the live loop
Grep for non-test constructors of BOTH `WholesaleCreditExposureRegister(` and `MarginCallBook(` returns **nothing in `company/`/`saas/`/`sim/`** — only tests construct them. So the FAIL is doubly cosmetic: the cap is static **and** the register never sees a real run's exposure. **Consequence for sequencing:** an observation-window cap "earned/eroded from observed exposure over a rolling window" has no exposure stream to observe yet. The next BUILD step is the **live feed** (wire the company's own per-step MtM + margin-call events into the register from the trading path), *then* the window mechanic on top. Building the window first would be an organ with no blood in it — a fresh cosmetic layer, exactly the accretion OPS1/DON'T-ACCRETE forbids.

### 3. Through-the-wall observable inputs the window MAY use (all company-side; none a sim internal)
- **Own margin calls received** — `MarginCallEvent` (initial + variation margin, deadline, status) — the company's own cash demands; observable by definition (`margin_call_book.py:15`).
- **Own mark-to-market exposure** — `gross_mtm_gbp` per counterparty: the replacement cost the company itself computes from its own book against observed market prices (through the wall — the price feed is a public observable, the position is the company's own).
- **Own posted/held collateral** — `collateral_held_gbp`: the company's own CSA postings.
- **Counterparty credit rating** — `CounterpartyCreditRating`: **publicly observable** (agency ratings are published; a real supplier reads them). Legal to use — it is NOT a sim internal. The window would *modulate* the rating-anchored starting cap by observed behaviour (settled-on-time vs disputed/defaulted margin calls), not replace the public prior.
- **Own counterparty-behaviour history** — `MarginCallStatus` transitions (RECEIVED→SETTLED vs DISPUTED/DEFAULTED): the company's own observed record of how a counterparty honoured calls; the erosion signal.

**Wall check:** every input above is either the company's own book/cash state or a public publication (ratings, prices). None reads sim ground truth (no counterparty true default-probability, no future price). Epistemically clean — confirm with `python3 -m tools.epistemic_verifier` on the eventual BUILD diff.

### 4. Restated BUILD ladder (revised by the FRAME)
1. **Live feed FIRST** (new drawable prerequisite): wire the company's own per-step MtM + margin-call stream into `WholesaleCreditExposureRegister` / `MarginCallBook` from the trading path, behind the existing typed seam — no new engine (portability lens). *This is the load-bearing step the original scope assumed already existed.*
2. **Observation-window cap**: rolling-window cap = rating-anchored prior modulated by observed exposure + settle/dispute history; replaces the static read in `credit_limit_gbp`. R15 both ways (fires on the wire present; mutation reverts to static → cap stops moving).
3. **MC-2 collateral death-test**: a spike scenario draining liquidity past `MarginCallBook`'s facility → collateral distress / company can die. R15: PASSES (survives) on benign path, FAILS (dies) on MC-2 path. **MC-2 *difficulty* (spike magnitude/shape) is R13 curriculum — escalate the value, mint only the mechanism + a benign default.**
4. Verify: epistemic-verifier on the diff; full suite for `company/trading|finance|risk` paths.

**Walls untouched by this FRAME:** doc-only, no code changed, no level moved, no curriculum value chosen. The MC-2 difficulty escalation still stands for the director when step 3 is reached.

---

## FRAME EXTENSION (Scope step 1, deepened) — 2026-07-24 second worker tick

The first FRAME found the registers have no live constructor and named the live feed as the next BUILD step. A second read of the *source* the feed would draw from surfaces a **deeper, decisive prerequisite the first FRAME assumed away** — recording it here so the next BUILD tick does not half-build a cosmetic organ (DON'T-ACCRETE).

### The blocker: the forward book has NO counterparty dimension
- **Evidence (`company/trading/forward_book.py:31`):** `ForwardContract` is keyed by `customer_id` with fields `term_start/term_end/notional_mwh/agreed_price_gbp_per_mwh/hedge_fraction/bid_ask_cost_gbp`. **There is no `counterparty` field anywhere on `ForwardContract` or `TradingBook`** (grep confirmed: zero hits). The book models the company's hedges as abstract positions, MtM'd against observed prices (`portfolio_mtm`, `:216`), with **no attribution to who the trade is *with*.**
- **Evidence (fresh, both registers):** grep for non-test constructors of `WholesaleCreditExposureRegister(` and `MarginCallBook(` across `company/`/`saas/`/`sim/`/`simulation/` returns **nothing** — confirmed still true this tick.
- **Consequence:** `WholesaleCreditExposureRegister` and `MarginCallBook` are **counterparty-keyed** (`WholesaleCreditRecord.counterparty_id`, `_CREDIT_LIMIT_BY_RATING` by rating, per-counterparty margin calls). The only live MtM stream (`TradingBook.portfolio_mtm`) carries **no counterparty axis to key them on.** So the "live feed" is not a mechanical adapter over existing data — the data it needs (which counterparty each forward sits with) **does not exist in the book yet.**

### Why the naive fix is the accretion trap, not the fix
Attributing every forward to a single synthetic OTC counterparty *would* let the feed compile, but it collapses the register to one row — a per-counterparty exposure organ with exactly one counterparty is cosmetic, the "organ with no blood in it" DON'T-ACCRETE forbids. The believability point (Axis 3: a 20-year veteran reads the counterparty concentration and CCP/bilateral split) is **destroyed** by a single-counterparty stub. So the honest ladder gains a step *before* the live feed.

### Restated BUILD ladder (revised again by this deeper FRAME)
1. **Counterparty-attribution model (NEW load-bearing prerequisite):** give the forward book a counterparty dimension — each `ForwardContract` (or each hedge execution) is booked *with* a counterparty (bank / energy-trader / generator / CCP-cleared vs bilateral-ISDA), so a real per-counterparty MtM stream exists. **Design question for grounding (DISCOVER-workable now, read-only):** how do UK suppliers' OTC/exchange forward hedges actually distribute across counterparties and clearing venues (ICE/LCH cleared vs bilateral ISDA)? This is a *believability modelling choice* (Axis 3, reversible, NOT curriculum values and NOT a one-way door) — proceed under PROCEED_BY_DEFAULT once grounded, register any un-grounded default as an R10 named simplification. **Wall check:** the counterparty a company trades with, and public agency ratings, are the company's own book / public observables — epistemically clean; no sim internal.
2. **Live feed** (was step 1): now has a real per-counterparty stream to wire into both registers behind the typed seam. R15 both-ways as before.
3. **Observation-window cap** (unchanged): rating-anchored prior modulated by observed settle/dispute history.
4. **MC-2 collateral death-test** (unchanged): benign path survives, MC-2 path dies; MC-2 *difficulty* stays R13 curriculum → escalate the value.
5. Verify: epistemic-verifier on the diff; full suite for `company/trading|finance|risk`.

**Next drawable step is now item 1 above (counterparty-attribution), reversible-build under standing PRODUCT-FIRST authority — best begun with a short DISCOVER grounding pass on real UK supplier hedge-counterparty distribution before the book change.** No code changed, no level moved, no curriculum value chosen this tick.

> **Tick note (2026-07-24, RUNG-7 doorbell):** this tick fired on a stale "rungs 1–6 empty → MINT" read. Disk state contradicts it: five `PLANNER_MINTED_*` docs are open in `in_progress/` and the director **waived** their windows (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`) — so rungs 1–6 are NOT empty and minting a sixth batch would be the over-production the director just intervened on. Correct draw per the waiver's sequencing guard = the top PRODUCT-FIRST item. Item 1 (`generator_draw_wiring`) is at its director-reserved activation wall (reversible half already shipped). Item 2 (this doc) had a genuinely drawable next step — advanced here by deepening the FRAME so the next BUILD tick starts on the real prerequisite, not a cosmetic stub. No mint this tick: premise false.
