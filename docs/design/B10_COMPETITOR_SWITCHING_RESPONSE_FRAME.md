# B10 — Competitor switching response: DISCOVER + FRAME

**Atom:** `B10_competitor_switching_response` (`docs/design/maturity_map.yaml`)
**Lane:** `W2_customer_generator` · **value_stream:** `meter_to_cash` · **epoch:** 3 · **loop_stage:** `idle`
**Stage produced here:** DISCOVER (0→1) + FRAME (1→2). **No BUILD code written** — this atom is
epoch-gated (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1: a parked atom is parked for BUILD only;
the doorbell that assigned this pass is explicit that BUILD stays gated regardless of the epoch number
looking open). **Level HELD at `level_current: 0`** — this project does not self-bump a level for
analysis-only work (R16); saturation for a DISCOVER/FRAME-scoped atom is a FRAME doc in evidence, not a
level move (matching the house style set by `B8_discovered_price_sensitivity_holdout`, whose own FRAME
doc left `level_current: 0`).
**Date:** 2026-07-29.
**BACKLOG source:** `docs/design/BACKLOG.md` B10 (Wave C) — "other suppliers, so the company's pricing
meets opposition instead of pricing into a void." DoD quoted verbatim in §2.6 below.

Every claim is labelled `observed-with-evidence` (read off disk this tick, file:line quoted) or
`inferred` (R9). Nothing here is copied from the map's own prose without re-checking it against the
tree — the map's `simplifications` note for this atom is itself only a summary of a prior reconciliation
pass; this doc re-verifies the two claims it rests on (that `W2_3` and `B4` are real but insufficient)
against the actual code, not just against what the note says.

---

## PART 1 — DISCOVER: what exists, what's wired, and the precise gap

### 1.1 The file this atom's own `file_scope` names does not exist yet

`observed-with-evidence`. `file_scope: [sim/competitor_field.py, tests/sim/test_competitor_switching.py]`
— neither path exists anywhere in the live tree (`find . -iname "*competitor_field*"` returns only
docs: `docs/design/COMPETITOR_FIELD_FRAME.md`, `docs/design/frame/B4_competitor_field_FRAME.md`,
`docs/market_research/f5_simulated_competitor_field.md`). There is also no `sim/` package at all in
this repo — the SIM lives under `simulation/` (confirmed: `simulation/market_switching_propensity.py`
etc. all exist; `sim/` does not). This is expected and not a defect: `level_current: 0` with
`provenance: proposal` means `file_scope` is the *intended* BUILD-time location, not a claim that code
exists — noted here only so a future BUILD pass doesn't waste a cycle rediscovering it, and so the path
gets corrected to the `simulation/` package convention when BUILD opens.

### 1.2 `W2_3_competitor_field` is genuinely DONE at its own (modest) target — and its ground truth is a pure macro scalar, not a relative-price mechanism

`observed-with-evidence`. `W2_3_competitor_field` (`maturity_map.yaml:408-422`) is `level_current: 1`,
`level_target: 1`, `loop_stage: harden` — at target, correctly not reopened here (R16: levels are
proposals, not mine to move, and this one isn't even a proposal — it's already closed at its own bar).
Its real substance is `simulation/market_switching_propensity.py`:

- `MARKET_SAVINGS_BY_YEAR` (`:29-40`) — one GBP/yr figure **per calendar year**, DESNZ/Ofgem-anchored,
  "annual savings available... to the best available competitor deal."
- `market_switching_multiplier(renewal_year: int) -> float` (`:80-102`) — takes **one argument: the
  year**. No company price, no customer id, no competitor tariff object of any kind is passed in or
  read.
- Wired live: `simulation/customer_events.py:32` imports it, `:110` applies it —
  `p_churn_market = (1.0 - effective_p_retain) * market_switching_multiplier(market_year)` — described
  in the module's own comment (`:108-109`) as an "opportunity ceiling," applied uniformly **before**
  any customer-level modifier.

**The precise consequence:** this is a real, well-calibrated, honestly-wired mechanism — but it answers
"how much did the market as a whole want to switch this year," identically for every customer and every
possible company price. It structurally **cannot** produce the DoD's "switching responds to relative
price" or "a competitor price change moves the book" — there is no competitor price *object* in the
calculation to change, and no company price *input* for it to be relative *to*. Two companies charging
different prices in the same year get an identical `market_switching_multiplier`. This is the single
clearest confirmation of the gap this atom exists to close.

### 1.3 `B4_competitor_field` is genuinely unbuilt, already thoroughly FRAMEd — and is the wrong side of the coin for this atom

`observed-with-evidence`. `B4_competitor_field` (`maturity_map.yaml:163-177`) is `level_current: 0`,
`level_target: 1`, `loop_stage: idle`, five DISCOVER/FRAME passes deep (2026-07-12 through 07-16),
with two full FRAME docs already in its own `evidence:` list: `docs/design/frame/B4_competitor_field_FRAME.md`
and `docs/design/COMPETITOR_FIELD_FRAME.md`. Both read in full for this pass. They specify, in real
depth: a `CompetitorFieldObservation` typed dataclass crossing `sim_interface.py` (published ceiling +
aggregate savings-available signal, no rival internals), and wiring into (a) the company's own churn
*belief* and (b) `RenewalPricingEngine.price_renewal()`'s SVT-ceiling — i.e. **the price the company
itself sets**. Confirmed via grep: no `CompetitorFieldObservation` or `get_competitor_field` exists
anywhere in the live tree yet (`grep -rn "get_competitor_field\|CompetitorFieldObservation" --include=*.py .`
— zero hits outside worktree mirrors) — B4 is exactly as unbuilt as its own map entry says.

**Why B4 does not reach B10's DoD even once built:** B4 is the company's *pricing* decision responding
to a market signal (ceiling/undercut pressure on the price the company sets). B10's DoD is the
*population's switching* decision responding to relative price — a different actor, a different flow
direction. B4 answers "should the company nudge its own price down because a rival looks cheap?"; B10
answers "does the population actually leave when the company's price is worse than a rival's?" A
company could implement all of B4 and still have zero customers ever switch away, because nothing in
B4's own scope touches the churn/switching probability calculation directly on a *company-price-vs-
competitor-tariff* term — B4's FRAME even says so explicitly (`B4_competitor_field_FRAME.md:29`: "L1 is
belief + one live coupling... No optimiser, no game-theoretic reaction function"). The two atoms are
complementary halves of a real market, not duplicates, and not substitutes for one another — this
matches the atom's own `simplifications` note's reconciliation, now independently re-verified against
the code rather than taken on trust.

### 1.4 The one place the RIGHT SHAPE already exists in the tree — and it is dead at zero

`observed-with-evidence`. `saas/home_move_win_rate.py::home_move_win_probability()` (`:61-79`) is a real,
already-built, relative-price-gap function:

```python
win_probability = base - price_differential_pct * sensitivity_by_EPC
```

This is structurally the *shape* B10 needs — a switching outcome as a function of `price_differential_pct`
("our price relative to the market average," `:69-71`), scaled by a segment attribute (EPC band). But
three things stop it from being B10's mechanism:

1. **Scope.** It fires only on the **home-move** channel (new occupant moving into a property decides
   whether to stay with the incumbent or switch) — never on an existing customer's ongoing
   renewal/churn decision, which is where the great majority of real switching volume sits.
2. **The feed is hardcoded dead at zero, everywhere it is called.** `PRICE_DIFFERENTIAL_PCT = 0.0` is
   declared independently in three places — `simulation/customer_events.py:36`,
   `simulation/run_phase4b_on_phase2b.py:28`, `simulation/run_phase4c_on_phase2b.py:86` — each commented
   "matches run_phase4c_on_phase2b.py"/"price parity with the market average," and none of the three
   call sites ever passes a non-zero value. `observed-with-evidence`: `grep -rn
   "PRICE_DIFFERENTIAL_PCT" simulation/` shows only these three declarations plus their pass-throughs
   into `build_home_move_win_rates()` — never a computation from an actual company price or a published
   competitor tariff. So even the one live relative-price term in this codebase has never, in any run,
   taken a non-zero value.
3. **"Market average" is ungrounded.** The docstring (`home_move_win_rate.py:69-71`) never defines what
   `price_differential_pct` is measured *against* — there is no reference tariff object it is a
   difference from. It is a parameter shape without a populated numerator or denominator.

**Conclusion, stated plainly:** no file, anywhere in this tree, makes an *existing* customer's
switching/churn probability depend on the company's own price relative to a live competitor tariff.
`market_switching_propensity.py` is exogenous-year-only (§1.2). `switching_propensity.py`
(`STRESS_SWITCHING_MULTIPLIER`, `TENURE_SWITCHING_MULTIPLIER`, `:17-56`) is customer-attribute-only —
stress and tenure, no price term at all. `satisfaction_churn.py` (imported in `customer_events.py:34`)
is a satisfaction-score modifier, not a price-relative one. The one price-relative shape that exists
(`home_move_win_rate.py`) is scope-limited to home-moves and permanently fed zero. This is the gap, and
it is exactly what the atom's own name promises to close.

### 1.5 Adjacent work that must not be duplicated or silently absorbed

`observed-with-evidence`. `docs/design/ENGAGEMENT_MARKET_STATE_RESPONSIVENESS_PROPOSAL_2026-07-22.md`
(a `provenance: proposal`, DISCOVER/FRAME-workable, **not yet a registered map atom** — its own text
says "NOT built, NOT registered to `maturity_map.yaml`") proposes making the ACTIVE/PASSIVE/DISENGAGED
*disposition mix* (`simulation/household_segments.py`) responsive to market state ("offer availability"
+ "fixed-vs-SVT spread"). This is genuinely adjacent but **not the same mechanism**: that proposal
modulates whether a household is *in the market at all* (opportunity, aggregate disposition), sourced
from the company's own SVT-vs-fixed spread, not a specific rival's tariff. B10 is about whether a
customer actually **moves to a specific rival tariff** because of the gap between the company's own
price and that tariff — a company-vs-rival relative-price mechanism, not a market-wide opportunity
gate. The FRAME below is written so the eventual BUILD can consume that proposal's "opportunity" signal
as one *input* (a customer with zero opportunity cannot switch regardless of price gap) without
absorbing its scope or duplicating its registration.

### 1.6 R13 baseline benchmarks already in this repo (no new external research needed for the FRAME; one gap flagged for BUILD-time)

`observed-with-evidence`. Two calibration anchors already exist and are real, sourced, and currently
used only at the aggregate level:

- **Annual population-level switching rate by year**, `docs/market_research/churn_price_elasticity.md`
  §1: 2015–2025 switching rate 3%–23% of the book, cross-tabulated against savings-available (DESNZ
  Quarterly Energy Prices Table 2.1 / Energy UK switching stats / Ofgem State of the Market Jan 2026).
  This is the aggregate the eventual mechanism's population-level output must reconcile against (R13:
  the DEFAULT field's aggregate switching rate is a fidelity target, checked blind to company P&L).
- **Active/passive/disengaged stock split**, `docs/market_research/ASSUMPTIONS.md:120`: Ofgem RMI
  Oct-2025 45.1%/54.9% actively-chosen-vs-default split, R13-ruled 2026-07-22 into
  `household_segments.py`'s 45/35/20 shares. This anchors what *fraction* of the book is even
  disposed to respond to a price gap at all — a DISENGAGED household should show near-zero sensitivity
  to `price_differential_pct` regardless of the gap's size, matching real "sticky SVT" behaviour.

**What is NOT yet in the repo, and should be a named BUILD-time discovery task, not fabricated here:**
a calibrated elasticity of *individual switching probability* to a *specific* relative-price-gap
percentage (e.g. "a 5% company-vs-cheapest-rival gap moves an ACTIVE household's annual switch
probability by X pp"). `churn_price_elasticity.md` calibrates the *market-wide* multiplier to
*aggregate* savings-available; it does not give a per-customer, per-percentage-point curve. `inferred`:
this is very likely derivable by combining the existing aggregate rate curve (§4 of that doc) with the
existing ACTIVE/PASSIVE/DISENGAGED disposition split as a weighting, rather than requiring wholly new
primary research — flagged as BUILD-decomposition item (b) in §2.7, not invented here (R13: a baseline
parameter must be calibrated to real structure, never asserted to make the FRAME doc look complete).

---

## PART 2 — FRAME: the design (nothing built)

### 2.1 Purpose, one sentence

Give the population an actual competitor tariff to switch to and a switching probability that responds
to the **live gap** between the company's own price and that tariff — so that overpricing costs
customers and underpricing wins them, replacing today's year-keyed macro opportunity ceiling
(§1.2) and the dead, home-move-only relative-price stub (§1.4) with a mechanism that fires for the whole
book, on an ongoing basis, symmetrically wall-clean.

### 2.2 The mechanism shape — a competitor tariff feed and a switching-propensity function of relative price

**World side (extends `W2_3_competitor_field`'s existing ground truth, does not replace it):**
a per-period **competitor reference tariff** — reusing `W2_3`'s already-real, already-anchored
`MARKET_SAVINGS_BY_YEAR` (§1.2) as the *savings-available* half, combined with the company's own
period price to derive `relative_price_gap_pct = (company_price − competitor_reference_price) /
competitor_reference_price`. This is deliberately the **minimal extension** of what already exists,
per the Simplicity Guard (C-S1–C-S5 doctrine): `W2_3` already generates a real, calibrated annual
reference figure; B10's own world-side addition is to also expose it as a **price level** (not only a
"savings available" delta), so a per-customer relative-gap term can be computed, rather than inventing
a wholly new multi-rival price-setting engine (that richer per-rival model is explicitly `W2_3`'s own
named L2+ gap, `docs/design/COMPETITOR_FIELD_FRAME.md:56-59`, and stays out of this atom's scope for the
same epistemic-wall reason `B4`'s FRAME already found: there is no ground truth today for a per-rival
snapshot, so a per-rival OBSERVABLE would be fabricating precision the world doesn't generate).

**Switching-propensity function:** `p_switch = disposition_weight(active/passive/disengaged) ×
opportunity(offer_availability) × f(relative_price_gap_pct)`, where:
- `disposition_weight` reuses the existing, R13-anchored `household_segments.py` split (§1.6) — a
  DISENGAGED household's weight should be near-zero regardless of the gap, matching real "sticky SVT"
  non-response and directly explaining why a large gap in 2022 (`MARKET_SAVINGS_BY_YEAR[2022] = -200.0`)
  produced almost no switching even among the nominally ACTIVE cohort (there was nothing to switch to).
- `opportunity` is the natural consumer of §1.5's adjacent proposal, if/when it is separately opened —
  named as an input seam here, not built or absorbed.
- `f(relative_price_gap_pct)` is the genuinely new piece: a monotonic function (company more expensive
  than the reference → higher switch probability; company cheaper → lower), calibrated so that the
  **population-level aggregate**, summed across the whole book in a given year, reconciles against
  `churn_price_elasticity.md`'s existing 3%–23% real switching-rate series (§1.6) — the calibration
  target is the AGGREGATE, exactly as `market_switching_multiplier` is calibrated today; the
  per-customer function is the new resolution the aggregate is decomposed into, not a new aggregate
  invented independently of it.

### 2.3 The WALL — what may and may not cross `sim_interface.py`

The company may observe, exactly as a real supplier's customer-facing team would from a comparison site
or its own switching-in/out flow:
- A **published competitor reference tariff level**, dated (`as_of_date`, `data_regime`), same style as
  `B4`'s already-designed `CompetitorFieldObservation` (§1.3) — reused, not reinvented, since the two
  atoms should share one observable type rather than mint two competing wall-crossing schemas for the
  same underlying "what does the market look like" question. Portability constraint (§2.7) applies
  identically: `market_id`/`segment` keyed, never hardcoded.
- Its **own realised acquisition and churn flows** — win/loss counts, reasons coded from its own billing
  system events (e.g. `gaining_supplier` / `erroneous_transfer` flags on an exit event), matching the
  `real_world_twin`'s own framing: "the incumbent learns it lost only when the erroneous-transfer/
  gaining-supplier flows arrive — never by being told what the competitor was thinking."

The company may **never** observe, read, or have any code path that touches:
- the competitor's true cost basis, margin target, intent, or price-setting RNG substream;
- the **`f(relative_price_gap_pct)` switching-propensity function's parameters or its evaluated
  probability** for any individual customer, before that customer's own decision is realised as an
  actual churn/acquisition event — the company only ever sees the *outcome* (the customer left, or a
  new one arrived), never the *mechanism* that produced it. This is the sharpest and most B10-specific
  wall statement: it would be trivial, and wrong, to let a "company churn-risk estimator" import the
  same switching-probability function the world uses to *decide* switching — that is not an estimate,
  it is reading the answer key. The company's OWN churn model (`company/crm/churn_model.py`,
  `enriched_churn_estimate.py`) remains free to build its own belief from observed flows, exactly as it
  does today; it must never import, call, or numerically reconstruct the world-side `f(...)` directly.

### 2.4 R15-failable controls, each with a named killer mutation

A control that cannot fail is worse than none (R15). Two controls, two independent killer mutations:

**Control A — wall integrity: no company-side code path can reach the world's true switching-propensity
parameters or evaluated probability.**
*Killer mutation:* patch a test double of the company's churn estimator to import and call the
world-side `f(relative_price_gap_pct, ...)` (or read its internal parameter table) directly instead of
reconstructing its own belief from observed acquisition/churn events. A correctly-built wall test must
turn **RED** the moment that import/call exists — mirroring the existing precedent
`epistemic-wall-company.md`'s own test ("could a real supplier know this without simulation internals?")
and the C9/F1b precedent already proven in this codebase (`company/comms/susceptibility_estimator.py`
importing nothing from `simulation.*`, per `B8_DISCOVERED_PRICE_SENSITIVITY_FRAME.md:§1.1`). If the
mutation does NOT turn the test red, the control is theatre (a TAUTOLOGY-class failure per R15 — it
would be checking the company's declared imports rather than the actual value path, the exact
class of miss the `B8` FRAME already found and fixed at `simulation/run_phase2b.py:1163-1172`).

**Control B — the DoD's own acceptance test: "a competitor price change moves the book."**
*Killer mutation:* hardcode `f(relative_price_gap_pct)` to return a constant (decoupling the switching
probability from the relative-price-gap input entirely, e.g. always return the disposition-weighted
baseline regardless of `relative_price_gap_pct`'s value) while leaving every other input (disposition
mix, opportunity, calibration constants) untouched. A correctly-built test that asserts "the modelled
switch-away rate materially differs between a run where the company prices 10% above the reference and
a run where it prices 10% below" must turn **RED** under this mutation — proving the test actually
checks *responsiveness to the gap*, not merely "some non-zero churn number exists" (a FAIL-OPEN
pattern R15 explicitly names: passing on a hardcoded/constant value is exactly the shape of defect a
non-mutation-tested control would miss). This is also the direct DoD acceptance test named in
`BACKLOG.md:169-171` — building this control IS building the DoD's own gate, not a proxy for it.

A third, cheaper sanity control worth naming for BUILD (not a substitute for A/B): the population-level
aggregate switch rate produced by summing `p_switch` over a full year's book must fall inside
`churn_price_elasticity.md`'s real 3%–23% band for that year's calibration point — a fail-open version
of this (accepting any output because "some number came out") would defeat the entire R13 discipline
below.

### 2.5 R12 — switching rate is a diagnostic, never a target

The realised switch-away rate (and the resulting win/loss count) is measured and reported, but is
**never** tuned toward looking like a particular company outcome — the population's `f(...)` calibration
target is the external DESNZ/Ofgem aggregate series (§1.6/§2.2), decided **blind to company margin or
churn results**, exactly as R12/R13 require. If a build pass ever produces a switch rate that looks
"too high" or "too low" relative to how the company's P&L would prefer it, the correct response is R4
diagnosis of the mechanism (is the calibration wrong, is a wall leak inflating/suppressing it, is the
disposition weighting mis-specified) — never a parameter nudge aimed at the P&L number. **Competitor
aggressiveness itself (whether a rival runs an unusually cheap loss-leader tariff, an entry/exit wave,
or a price war) is director-authored CURRICULUM (R13, `MARGIN_REALISM.md`'s own worked example) — never
agent-tuned in response to how the company is doing.** The DEFAULT/baseline reference-tariff generator
described in §2.2 may only be changed for fidelity-to-reality reasons.

### 2.6 DoD, restated against BACKLOG's own acceptance criteria (`BACKLOG.md:169-171`)

> "≥1 competitor prices tariffs the population can switch to; switching responds to relative price; the
> company's win/loss is observable only through acquisition/churn (wall held); a test asserts a
> competitor price change moves the book."

Mapped directly onto this FRAME:
1. **"≥1 competitor prices tariffs the population can switch to"** → §2.2's competitor reference tariff,
   extending `W2_3`'s existing real, calibrated `MARKET_SAVINGS_BY_YEAR` into a price level the
   population can be compared against (not a wholly new price-setting engine — reuses real prior art).
2. **"switching responds to relative price"** → §2.2's `f(relative_price_gap_pct)`, the piece confirmed
   in §1.4 to not exist anywhere live today (the one shape that resembles it is dead at zero).
3. **"the company's win/loss is observable only through acquisition/churn (wall held)"** → §2.3's wall
   statement + Control A (§2.4).
4. **"a test asserts a competitor price change moves the book"** → Control B (§2.4), which is this exact
   sentence made mutation-testable.

### 2.7 Scale-readiness, portability, and BUILD decomposition (epoch-gated, NOT opened by this FRAME)

- **C-S1/C-S2/C-S3/C-S5:** identical discipline to `B4`'s own FRAME (§7 of
  `COMPETITOR_FIELD_FRAME.md`) — the competitor reference observation is an event arriving over time
  (no batch-completeness assumption), the world-side price-setting/noise draws from B10's **own** named
  seeded substream (never sharing `W2_3`'s or any sibling's, per the 01:09Z-incident precedent, C-S2),
  and the wall crossing is asynchronous (fetch ≠ same-step as the switching decision it feeds).
- **Portability:** the reference tariff and switching-propensity function are keyed by `market_id`/
  `segment`, reusing the same convention `B4`'s FRAME already specified — no second schema invented for
  the same underlying "what does the market look like" question.
- **Simplicity guard:** one new world-side price-level exposure on top of `W2_3`'s existing calibration,
  one new company-observable field (reusing `B4`'s already-designed `CompetitorFieldObservation` shape
  rather than minting a second one), one new switching-propensity function, one wall test, one
  responsiveness test. No new competitor-entity engine, no game-theoretic reaction function — that is
  explicitly `W2_3`'s own named L2+ gap and stays out of scope here, matching `B4`'s FRAME's identical
  restraint.

**BUILD decomposition, for the eventual BUILD pass (not opened here):**
(a) extend `W2_3`'s ground truth to expose a comparable price *level* (not only a savings-delta) —
    `file_scope: [simulation/market_switching_propensity.py]`, small.
(b) the per-customer/per-percentage-point elasticity calibration named as an open gap in §1.6 —
    reconciling the existing aggregate rate series against the disposition-mix weighting; a discovery
    task, not fabricated in this FRAME.
(c) the switching-propensity function + its own named RNG substream —
    `file_scope: [simulation/competitor_switching_propensity.py]` (new module, naming TBD at BUILD
    time; corrects this atom's own registered `file_scope` path from `sim/` to the real `simulation/`
    package, per §1.1).
(d) the observable crossing `sim_interface.py`, reusing `B4`'s already-FRAMEd
    `CompetitorFieldObservation` rather than a new type.
(e) Control A (wall) and Control B (responsiveness) as R15-mutation-tested tests —
    `file_scope: [tests/simulation/test_competitor_switching.py]` (path corrected from this atom's
    registered `tests/sim/...` for the same reason as (c)).

None of (a)–(e) are opened by this document — BUILD-open remains DIRECTOR_TWIN's call per
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` §3a, within epoch 3 once sequencing allows it.

---

## AMENDMENT, 2026-08-28 — the gap §1.2 names was closed on 2026-08-27

**Read this before building from Part 2.** This FRAME is dated 2026-07-29. On 2026-08-27 the
churn decision gained a per-customer relative-price term
(`simulation/customer_events.py::_price_differential_vs_market` +
`price_elasticity_for_customer`), which is §2.1's stated purpose — *"a switching probability that
responds to the live gap between the company's own price and that tariff"* — and which makes
§1.2's "single clearest confirmation of the gap" no longer true.

**The half that remains is the half the director's C2 is about**, and it is a different
deliverable: *nothing in the world responds to what the company does.* The reference the
differential is measured against (`simulation/svt_rates.py`, and this FRAME's own proposed
`MARKET_SAVINGS_BY_YEAR`) is a table keyed on the calendar. It cannot move.

**B10's amended deliverable: a competitor reference price that is a function of the company's own
observed position, with a lag, bounded below by a cost floor built from the same wholesale stack
the company faces.** Control B's killer mutation becomes *"freeze the reference at its calendar
value and the responsiveness test must go red"* — a strictly better mutation than the original,
because that mutation reproduces the world as it stands today.

Full evidence and reasoning:
`docs/staging/WORKER_FINDING_B10S_FRAME_TARGETS_THE_HALF_THAT_ALREADY_LANDED_2026-08-28.md`.
Part 1's DISCOVER survey and Part 2's wall statement (§2.3), controls (§2.4) and portability
constraints are otherwise unaffected and stand.
