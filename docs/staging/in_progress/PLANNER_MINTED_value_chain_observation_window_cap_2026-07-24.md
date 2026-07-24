<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- draw-visibility marker (2026-07-24): self-drawable next step, no wall — surfaced to the draw so rung-7 does not over-mint over it. Fail-closed structured token parsed by background/staging_disposition.selfdrawable_mint_in_progress. -->

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

---

## BUILD ladder step 1 — counterparty attribution on `ForwardContract` (DONE, 2026-07-24 worker tick)

Grounded by the prior-tick DISCOVER pass (`docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md`). Reversible, company-side, wall-clean.

- **`ForwardContract` gains a counterparty dimension** (`company/trading/forward_book.py`) reusing the register's OWN taxonomy so the attribution feeds `WholesaleCreditExposureRegister` directly, not a parallel enum: `counterparty_id`, `counterparty_type` (`CounterpartyType`), `clearing_status` (`ClearingStatus`), `counterparty_rating` (`CounterpartyCreditRating`), `broker_arranged: bool`. All defaulted → backward-compatible (the sole non-test constructor, `run_phase2b.py:1641`, and every existing test still build unchanged; 98 forward-book tests green).
- **`assign_default_counterparty()`** — deterministic (hashlib, NOT salted `hash()` → C-S2 reproducible replay), wall-safe (reads only company-observable contract attributes). Realises the **R10 named simplification**: ~50/50 cleared/bilateral (measured 50.8/49.2 over 3000), bilateral weighted bank≈20%/trader≈20%/generator≈10%, concentrated to an 11-name active pool. The split is inferred-best-estimate (RQ2 ungrounded-gap — no public supplier-level split exists), flagged for external cross-check, never sourced/tuned.
- **`TradingBook.exposure_by_counterparty()`** — ISDA-netted per-counterparty MtM: sums SIGNED MtM per name, then credit exposure = `max(0, netted)`. This IS the consumable feed for the register (`gross_credit_exposure_gbp` → `WholesaleCreditRecord.gross_mtm_gbp`), proven by a shape test that builds a real record from the aggregation.
- **Wall placement enforced by test:** CCP-cleared carries no per-name rating (CCP default waterfall absorbs); bilateral carries a PUBLISHED rating band (readable observable), true default-prob stays sim-internal.
- **R15 both ways:** the distribution test FAILS on a collapsed single-channel split; the exposure test FAILS if netting were removed (a hedged-both-ways counterparty would overstate) or if credit exposure went negative (fail-open). 15 new tests, full trading/market path green (727 passed).

**Next drawable step (unchanged sequencing):** the LIVE FEED — wire `assign_default_counterparty` at `open_hedge` and construct/populate the register from `exposure_by_counterparty` each run step (give the organ blood), THEN the observation-window cap on top. Step 1 delivers the per-counterparty exposure the feed needs.

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

---

## DISCOVER GROUNDING (BUILD ladder step 1 — counterparty-attribution) — 2026-07-24 third worker tick

The prior FRAME named the counterparty-attribution model as the next load-bearing prerequisite and flagged that it is *"best begun with a short DISCOVER grounding pass on real UK supplier hedge-counterparty distribution before the book change."* That pass is now **DONE** (read-only research, no code) — findings in **`docs/market_research/uk_supplier_hedge_counterparty_distribution_2026-07-24.md`** (+ 4 rows appended to `docs/market_research/ASSUMPTIONS.md`), grounded via live fetches of Ofgem (incl. the Oxera 2021-failures review), ICE, ECC/EEX, LCH. This unblocks BUILD ladder step 1 with grounded defaults rather than a guess.

### What the grounding decided (Axis-3 believability, wall-checked)
- **Counterparty-type set for `ForwardContract.counterparty` (grounded H):** `CCP_CLEARED` (ICE Clear Europe / ECC — daily+intraday variation margin, initial margin, no per-name credit limit; the CCP default waterfall absorbs it), `BILATERAL_OTC_BANK`, `BILATERAL_OTC_TRADER`, `BILATERAL_OTC_GENERATOR` (all ISDA+CSA, rating-anchored credit limit, MtM-driven calls), and `BROKER_INTERMEDIATED` as a *pass-through flag* on a bilateral type, **not** a fifth credit-bearing category (the real credit counterparty is whoever the broker matched). This defeats the single-synthetic-counterparty stub the FRAME warned was the accretion trap — the register now has real per-type structure a veteran can read.
- **Distribution default (R10 named simplification — flag on BUILD, NOT a sourced split):** no public supplier-level cleared-vs-bilateral disclosure exists (Ofgem's Financial Resilience Transparency Report checked, carries none). Use ~50% `CCP_CLEARED` / ~50% pooled bilateral (bank+trader weighted for standard tenors, generator for shaped/PPA), with a small single-digit-to-low-teens active bilateral pool per supplier-scale bracket. Register as an R10 simplification in the atom when built; follow-up DISCOVER task queued to re-attempt a trade-press (Montel/ICIS/Cornwall Insight) split (DuckDuckGo/Bing were bot-blocked this session).
- **Wall placement (RQ4, decisive for the observation-window cap):** published agency rating *bands* (S&P/Moody's/Fitch letter grades) ARE public and wall-safe for the company to read as the cap's *prior*; the counterparty's *true* default probability stays sim-internal and is inferred by the company ONLY from its own observed settle/dispute history. This is exactly the "rating-anchored prior modulated by observed settle/dispute history" the window cap (ladder step 3) needs — grounded, not asserted.
- **MC-2 death-loop — material correction to the design (RQ5, honest finding):** the Oxera review shows the *dominant* UK **domestic** 2021 supplier-failure cause was **under-hedging / naked exposure** ("the free bet"), NOT margin calls on a hedged book. The collateral/margin-call death-loop is real and strongly evidenced, but at the **generator/major-trader** level (Uniper/Fortum, ~$29bn 2022 rescue). **Consequence for the build:** MC-2 must be modelled as a **DISTINCT failure channel** — a margin/collateral-call spike on `BILATERAL_OTC_*`/`CCP_CLEARED` positions during a wholesale shock — *separate from and not a substitute for* the existing naked-exposure `MIN_HEDGE_FLOOR` mechanic. Conflating them would misattribute the UK-specific evidence. This corrects the original scope's implicit assumption that the death-loop and under-hedging are the same failure.

### Restated BUILD ladder (steps 2–5 unchanged; step 1 now grounded)
1. **Counterparty-attribution model — GROUNDED, ready to BUILD.** Add the 5-type `counterparty_type` dimension (+ broker flag) to `ForwardContract`/hedge execution; assign via the R10-flagged default distribution above with its own named seeded substream (C-S2). Reversible, no curriculum value, wall-clean (own book + public ratings only) — proceeds under standing PRODUCT-FIRST authority. Register the distribution default as an R10 simplification on the atom at BUILD.
2. **Live feed** — now has a real per-counterparty MtM stream to wire into both registers behind the typed seam.
3. **Observation-window cap** — rating-band prior modulated by observed settle/dispute history (wall placement grounded above).
4. **MC-2 collateral death-test** — a DISTINCT channel from `MIN_HEDGE_FLOOR`; benign path survives, MC-2 path dies. MC-2 *difficulty* stays R13 curriculum → escalate the value.
5. Verify: epistemic-verifier on the diff; full suite for `company/trading|finance|risk`.

**Next drawable step is now BUILD ladder step 1 (counterparty-attribution) — grounded and reversible; the next BUILD tick starts here with real defaults, not a stub.** Doc + research only this tick: no `company/` code changed, no level moved, no curriculum value chosen.

> **Tick note (2026-07-24, RUNG-7 doorbell, third worker tick):** doorbell again fired the stale "rungs 1–6 empty → MINT" read; disk again contradicts it (5 waived `PLANNER_MINTED_*` open in `in_progress/`, mint = over-production the director intervened on). Correct draw per the waiver's sequencing guard = top PRODUCT-FIRST item. Item 1 (`generator_draw_wiring`) at its director-reserved R13 activation wall (reversible half shipped, NTFY-escalated). Item 2 (this doc) advanced by running the FRAME-named DISCOVER grounding pass — BUILD ladder step 1 now grounded. No mint this tick: premise false. Also archived a stale superseded run-complete marker (git=5481b4e1d, finished 18:23Z — superseded by the already-published 18:39Z run git=8bdfb8431) that would otherwise risk a stale-data republish.

---

## BUILD ladder step 2 — the LIVE FEED transform (DONE, 2026-07-24 fourth worker tick)

Ladder step 1 (counterparty-attribution) is now COMMITTED (`37004b27b` step 1, `8d4fe46fe` step 2 — `ForwardContract` carries `counterparty_id/type/clearing_status/rating`, wired at `open_hedge`, board-visible channel mix in `trading_book.summary()`, and `TradingBook.exposure_by_counterparty(prices)` emits the ISDA-netted per-counterparty MtM stream). So step 2 — the feed into `WholesaleCreditExposureRegister` — was the next drawable step. **Built this tick:**

- **`company/trading/wholesale_credit_exposure.py::build_credit_register_from_exposure(exposure)`** — a PURE transform (no I/O, no clock, deterministic) from `exposure_by_counterparty()` output → a populated `WholesaleCreditExposureRegister`. Wall-clean (own netted MtM + public rating band only; epistemic-verifier PASS on the diff). Three R10-flagged modelling choices, documented in the docstring: (a) `gross_credit_exposure_gbp → gross_mtm_gbp` (OTM nets to zero exposure); (b) `collateral_held_gbp = 0` here — CSA/variation-margin postings are ladder step 3's job, so this feed reports an UPPER BOUND on the true net line (named simplification); (c) CCP-cleared rows get `_CCP_NO_PER_NAME_LIMIT_GBP` (no per-name limit — the default waterfall absorbs), JSON-safe finite sentinel, not a rating-band cap that would false-breach a large cleared book. `"UNATTRIBUTED"` is skipped (no counterparty identity → no phantom record; the book's `unattributed_count` self-check already surfaces the regression).
- **`tests/company/trading/test_credit_register_feed.py`** — 6 tests, proven against the REAL producer (`TradingBook.exposure_by_counterparty`), not a hand-built dict. **R15 BOTH-WAYS proven this tick:** the empty-register fail-open mutation reds 4 tests; the dropped-`_CLEARED_EXPOSURE_HAIRCUT` mutation reds the CCP test; clean restore green. + bilateral-breach-detected-through-the-feed (proves gross_mtm is fed not zeroed), OTM→zero-exposure, UNATTRIBUTED-skipped, deterministic-replay (C-S2). Full `tests/company/trading/` suite green (660).

### Decisive finding for step 3 (the run-loop WIRING) — recorded, not half-built
The feed TRANSFORM is done and tested, but wiring it live surfaces a genuine design sub-problem the earlier FRAMEs assumed away, and it is **not** a mechanical adapter: **there is no mid-run price snapshot in `run_phase2b`.** `exposure_by_counterparty(prices)` needs a `{customer_id: current_forward_price}` snapshot, and the run computes none. Critically, at END-of-run over 2016–2025 nearly all contracts have delivered, so `open_contracts()` is ~empty → an end-of-run feed would populate a near-EMPTY register (the cosmetic "organ with no blood" this doc forbids). The board-meaningful credit exposure occurs **mid-run at peak open-position during a price shock**, so the honest wiring is a **mid-run sample-point** (e.g. per-term or per-year end, at a point-in-time forward-price snapshot generated by the existing `generate_forward_price` machinery under point-in-time discipline). Choosing the sample cadence + the price basis is a reversible, wall-loaded design step (epistemic-verifier gate) — the next drawable BUILD step, now with the transform already proven so it starts on the real question, not a stub. No curriculum value, no level move, no one-way door.

> **Tick note (2026-07-24, RUNG-7 doorbell, fourth worker tick):** doorbell fired the stale "rungs 1–6 empty → MINT" read AGAIN; disk contradicts it (auto-processor daemon live on the run-complete queue holding `.tree.lock` = rung-1 in flight; 5 waived `PLANNER_MINTED_*` open in `in_progress/`). Minting a sixth batch = the over-production the director intervened on. This tick BROKE the three-prior-tick doc-only pattern by shipping the actual step-2 code + R15 tests (not another FRAME note). No mint: premise false.

---

## BUILD ladder step 3 — the OBSERVATION-WINDOW CAP mechanism (DONE, 2026-07-24 fifth worker tick)

**Stale-note correction (verified on disk this tick):** the prior four tick-notes repeatedly named *"the run-loop live feed"* as the next drawable step. **It is already COMMITTED — `5219495f9` "VALUE_CHAIN: feed the credit-exposure + margin-call registers from the live run loop"** (`simulation/run_phase2b.py:2289–2348`: an end-of-run observable forward-price mark → `build_credit_register_from_exposure` + `build_margin_calls_from_mtm`). The ladder had silently advanced past its own doc. So the genuine next step this tick was step 3 itself — **the observation-window cap** (the actual declared FAIL: replace the static `_CREDIT_LIMIT_BY_RATING` dict read).

**What shipped (the mechanism + a benign default — the doc's authorised scope, `company/trading/wholesale_credit_exposure.py`):**
- **`ObservedCounterpartyBehaviour`** — the company's OWN observed record (counts of SETTLED / DISPUTED / DEFAULTED margin calls it exchanged with a counterparty) over the window. Through-the-wall observable (own book conduct + public rating band); never the counterparty's true default probability. Wall-clean — **epistemic-verifier PASS on the diff.**
- **`observation_window_credit_limit(rating, behaviour)`** — the cap is now a rating-anchored PRIOR eroded monotonically by `adverse_score` (dispute weighted 0.5, default 1.0) toward `_WINDOW_LIMIT_FLOOR_FRACTION` (0.25) of the prior at an all-defaulted history. **One-directional named simplification (R10):** observed conduct can only ERODE, never earn a line above the rating band (a board does not lift a rating limit on clean payment alone).
- **`WholesaleCreditRecord.credit_limit_gbp`** now calls the mechanism; the new optional `observed_behaviour` field defaults to `None` → returns the exact rating prior → **100% backward-compatible** (all 37 register/feed tests + 1290 trading/finance tests green, no consumer changed).
- **R15 BOTH-WAYS proven this tick** (`tests/company/trading/test_observation_window_cap.py`, 10 tests): benign-default = prior; all-defaulted = floor; disputes erode less than defaults; monotone in default count; **teeth test** — erosion flips a within-limit 600k exposure into a LIMIT BREACH once the cap drops to 500k. Mutations that red their guard: revert-to-static (breach test reds), floor→1.0 (floor+monotone red), equal dispute/default weight (softer-signal + blend red); clean restore green.

### The declared FAIL is now closed at the mechanism level
The cap is **no longer a pure static dict** — it is a prior a deteriorating counterparty's own observed conduct tightens. The veteran's "cosmetic tell" (Axis 3) is answered: the collateral mechanics now have real credit-control physics.

### HONEST remaining work (verified-absent prerequisites — the mechanism is LIVE but DORMANT until fed)
Recording precisely per *consumed≠absorbed*: the mechanism is proven, but **nothing feeds `observed_behaviour` live yet**, so on a real run the cap still equals the prior (honest, not cosmetic — no adverse history observed). Two verified prerequisites, each the next drawable step:
1. **A margin-call settle/dispute RESOLUTION mechanic** — verified absent: `build_margin_calls_from_mtm` creates every call as `MarginCallStatus.RECEIVED`; nothing ever settles/disputes/defaults, so there is no adverse signal to observe. This is the load-bearing next BUILD.
2. **Multi-period sampling** — verified: the register/margin feed runs at a SINGLE end-of-run snapshot (`open_contracts()` ~empty by 2025 → the near-empty cosmetic case the FRAME feared). A rolling window needs the feed to accumulate across mid-run sample points (`build_margin_calls_from_mtm(book=…)` already supports accumulation; the run loop calls it once).
3. **Surfacing gap** (verified): the register/margin summaries computed at `run_phase2b:2322–2344` do NOT appear in the published run-output JSON (80 top-level keys, none of `wholesale_credit_exposure`/`margin_call_book`/`trading_book`) → the board cannot yet SEE them. Surface AFTER (1)+(2) so it shows moving numbers, not an empty organ.
4. **MC-2 collateral death-test** — unchanged; its *difficulty* stays R13 curriculum → escalate the value.

> **Tick note (2026-07-24, RUNG-7 doorbell, fifth worker tick):** doorbell fired the stale "rungs 1–6 empty → MINT" read a FIFTH time; disk contradicts it (6 self-drawable `PLANNER_MINTED_*` open, director-waived — minting a sixth batch = the over-production the director intervened on). Correct draw = top PRODUCT-FIRST item (this doc). Shipped the step-3 MECHANISM + R15 both-ways (not a FRAME note), corrected the doc's own stale "next = live feed" claim to verified disk truth (feed committed at `5219495f9`), and named the three verified-absent prerequisites so the next tick starts on the real blocker (a settle/dispute resolution mechanic), not a cosmetic layer. No mint: premise false.

---

## BUILD ladder step 3 prerequisite 1 — the RESOLUTION-observation SEAM (DONE, 2026-07-24 sixth worker tick)

The step-3 note named prerequisite 1 as *"a margin-call settle/dispute RESOLUTION mechanic — the load-bearing next BUILD"* to feed the (live-but-dormant) observation-window cap. Framing it exposed a **wall fork the stated prerequisite glossed over — caught before code (Tier-1, not a style point):**

1. **Two sides of the margin exchange are distinct.** `build_margin_calls_from_mtm` (`company/finance/margin_call_book.py`) builds the calls the **company OWES** (the liquidity leg, sign-complement). The observation-window cap needs a **COUNTERPARTY's** conduct on margin the **counterparty owes the company** (the owed-to-us / credit-exposure leg this register tracks). Naively "resolving the calls build_margin_calls_from_mtm creates" and folding them into the cap would erode a counterparty's line on the **company's own** (dis)honour — a **semantics inversion**. The stated prerequisite would have wired the wrong side.
2. **Counterparty resolution is a WORLD property, observed not invented.** *Whether* a counterparty settles/disputes/defaults reflects its true default propensity, which lives **behind the wall**. The company may only OBSERVE the outcome (cash arrived / amount contested). A company-side model that *decides* counterparty defaults would be a Tier-1 epistemic violation. So prerequisite 1 is a **COUPLED-TRIAD build** (WORLD counterparty-behaviour model → COMPANY observes settlement outcomes → the cap consumes → HARNESS measures the belief-vs-truth gap), **not** a company-side adapter.

### What shipped this tick (the wall-correct company-side CONSUMER seam)
`company/trading/wholesale_credit_exposure.py` — the typed contract the WORLD producer plugs into (typed-flow-seam preference; define the observable-consumer shape before the producer exists):
- **`MarginResolution`** (SETTLED / DISPUTED / DEFAULTED) + **`CounterpartyResolutionOutcome`** (`call_id`, `counterparty_id`, `resolution`) — an OBSERVED, **counterparty-attributed** outcome. The type **structurally forbids** feeding the company-owes liquidity leg (no counterparty-credit meaning), so the sign-inversion in (1) cannot be wired by accident.
- **`observed_behaviour_from_resolutions(outcomes) -> {cp_id: ObservedCounterpartyBehaviour}`** — a PURE fold: order-invariant (**C-S1**: single/late/out-of-order tolerated), idempotent by `call_id` (**C-S2**: duplicate delivery harmless), no clock/RNG/I/O. It **aggregates** observed outcomes; it never **decides** them (wall-clean — **epistemic-verifier PASS on the diff**). A contract, not a board-surfaced empty organ → not the "organ with no blood" DON'T-ACCRETE forbids.
- **R15 both-ways** (`tests/company/trading/test_observation_window_cap.py`, +6 tests, 17 total green; full `tests/company/trading/` 677 green): end-to-end teeth (an observed all-defaulted stream MOVES the cap to the floor); mutations proven to red — drop-dedup reds C-S2, miscount-defaults-as-settled reds the fold+teeth tests; clean settle-history must NOT erode (one-directional); empty stream benign. Clean restore green.

### Next drawable step — the WORLD half (a coupled atom, gated on its own side of the wall)
A **WORLD counterparty-resolution behaviour** model: rating-band-conditioned, its own named seeded RNG substream (C-S2), emitting the observable settle/dispute/default stream the company feeds into `observed_behaviour_from_resolutions`. Per COUPLED_TRIAD this is a SIM/world atom — it must be **authored as a coupled atom** and faces world-atom gating (no L3 until the company has been tested against it and the belief-vs-truth gap measured), so it is NOT a bare company-side worker-tick action. The consumer seam above is the stable target it plugs into. Also still open: multi-period sampling (feed accumulates across mid-run sample points) and the run-output surfacing gap (register/margin summaries absent from published JSON) — both named in the step-3 note, unchanged.

> **Tick note (2026-07-24, RUNG-7 doorbell, sixth worker tick):** doorbell fired the stale "rungs 1–6 empty → MINT" read a SIXTH time; disk contradicts it (2 self-drawable `PLANNER_MINTED_*` open with drawable next steps, 4 blocked, director-waived — a sixth mint batch = the over-production the director intervened on). SSP sibling has no worker-tick step left (part-a is network-gated / R13-baseline / director-reserved-grounding, ranked below spike-tail). Correct draw = advance THIS mint's drawable step — shipped the wall-correct consumer seam + R15 both-ways, and caught the semantics-inversion the stated prerequisite would have wired. No mint: premise false.
