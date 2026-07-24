# [PLANNER-MINTED] WVC: feed the credit-exposure + margin-call registers from the live run loop (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Rungs 1–6 drew empty this
tick. **Propose-then-proceed.** Lane: **BUILD** (company-side observation organs). This is the
**critical-path prerequisite that the value_chain FRAME discovered** — see provenance.

## Provenance / not-a-duplicate
`docs/staging/in_progress/PLANNER_MINTED_value_chain_observation_window_cap_2026-07-24.md` scoped an
observation-window cap on top of `WholesaleCreditExposureRegister` + `MarginCallBook`. Its FRAME
(Scope step 1, run this tick) **discovered the scope-2 assumption was false**:

> *"both target registers (`WholesaleCreditExposureRegister`, `MarginCallBook`) have **no live
> (non-test) constructor** — they are modelled organs not yet in the run loop, so an observation-window
> cap has nothing to observe until the register is first fed the company's own live MtM/margin-call
> stream. **The next drawable BUILD step is therefore the live feed**, then the window mechanic on top."*

This mint elevates that discovered prerequisite into its own drawable item so the critical path is
explicit and correctly sequenced. It is **not** a re-mint of the window-cap work (that stays in its
own doc, now correctly *downstream* of this). **File-scope note:** this touches the same organs as the
value_chain doc — the two **must serialise** (one worker, or this one first). Not a disjoint concurrent
grant.

## Ratified goal served
- **DIRECTOR_AXES v1 — Axis 3 (Believability):** *"wholesale products and prices ... does it feel like
  the real UK market to a 20-year veteran."*
- **PRIORITIES.md PRODUCT-FIRST item 3** (director-ratified 2026-07-23, waiver 2026-07-24):
  *"VALUE_CHAIN first organs."* The credit/collateral organs are inert modelled dataclasses until
  fed — a veteran reads an unfed register as cosmetic. This is item 3's true critical path.

## The gap being closed
`company/trading/wholesale_credit_exposure.py` and `company/finance/margin_call_book.py` are
constructed only in tests. The run loop never feeds them the company's own observed MtM exposure and
margin calls, so `utilisation_pct`, `is_limit_breached`, `is_liquidity_stressed`, `stress_events`
never move in a real run — the cash-collateral death-loop the front door promises ("*it can be wrong,
and it can die*") cannot occur because nothing feeds the organ that would kill it.

## Real-world fidelity gained
- The company's **own observed** wholesale exposure and margin-call stream become live run state
  (through the wall — the company observes *its own* trades/MtM/collateral, never sim internals).
- Unblocks the observation-window cap (the value_chain doc) *and* the MC-2 collateral death-test:
  both need a fed, moving register to act on.

## Scope (propose)
1. FRAME the run-loop seam: where the company books forward contracts / marks the book / posts
   collateral, and confirm each feed input is a **through-the-wall observable** (own margin calls,
   own MtM, own posted collateral) — none a sim internal. Prefer a **typed, versioned-message
   adapter** over a direct call (typed-flow-seam preference).
2. BUILD the live feed: wire the run loop to append to both registers via the append-only event-log
   abstraction (C-S4 persistence-behind-interface); idempotent + replay-deterministic (C-S2), each
   subsystem drawing from its own named seeded RNG substream; tolerant of single/late/out-of-order
   arrival (C-S1). No counterparty hardcoding (portability lens). **SIMPLICITY GUARD:** simplest
   construct — the wall already provides the seam; add discipline, not a repository cathedral.
3. Verify: epistemic-verifier on the diff (company must not read sim internals); R15 — the register
   fields *move* on a real run and the control *can* fire (a fed register that can never breach is
   fail-open). Full suite for `company/trading|finance|risk` paths + a fast-mode run showing the
   registers populated from the loop.

## Walls untouched
No curriculum-difficulty value (the MC-2 *scenario* difficulty is R13, escalate never tune — this mint
only feeds the organ). Credit-limit / facility numbers stay as the existing benign defaults here; the
window-cap doc replaces the *mechanism*. No L3 self-promote (merge L3-quality, leave level, set
`blocked_on: director_level_up` if it would bump). No one-way door.

## Propose-then-proceed window
Standing PRODUCT-FIRST reversible-build authority; proceed. Escalate only an irreducible
curriculum-difficulty value via NTFY while continuing to draw.

— RUNG-7 planner, 2026-07-24 worker tick.
