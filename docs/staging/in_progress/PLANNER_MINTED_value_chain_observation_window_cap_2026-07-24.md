# [PLANNER-MINTED] VALUE_CHAIN: replace the static cap dict with real observation-window mechanics + MC-2 collateral death-test (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 2 — PRODUCT-FIRST item 3, the declared static-cap FAIL + MC-2 collateral death-test). No map atom yet (tracked in `docs/PRIORITIES.md` item 3 + steer `DIRECTOR_STEER_WHOLESALE_VALUE_CHAIN_2026-07-22.md`); register on BUILD open.
> **BLOCKING SUB-ITEM (open):** Scope 1 (FRAME the static-cap call sites + name through-the-wall observable inputs) is drawable now. Scope 2-3 BUILD (observation-window cap + MC-2 death-test) proceeds under reversible authority, **but the MC-2 scenario *difficulty* is R13 curriculum — escalate any difficulty knob, never tune** (mint the mechanism + a benign default only). **UNBLOCKS:** self for the mechanism; director for any named curriculum-difficulty value. FRAME not yet done this tick (generator FRAME drew first per sequencing guard, PRODUCT-FIRST item 2 outranks item 3).

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
