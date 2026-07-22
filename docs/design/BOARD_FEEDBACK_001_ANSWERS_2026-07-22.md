# Answers to the Board's four MATERIAL CHALLENGES on Reconciliation 001 (for Movement 3)

**Source:** `docs/staging/BOARD_FEEDBACK_001_MATERIAL_CHALLENGES_2026-07-22.md` (board verdict VERBATIM +
advisor instruction). **Answers to:** `docs/design/WHOLESALE_TRADING_BOARD_RECONCILIATION_2026-07-22.md`
(the 001 reconciliation the board worked cold). **Status:** analysis, **reversible** (the board's own tag).
Each challenge is answered **accept-with-action** or **reject-with-reasons**, with code anchors. Any
*mechanism replacement or loop build* named below is **contract-touching** and routes through the
WHOLESALE_VALUE_CHAIN propose-then-proceed gate (2h veto) — **this doc authorises nothing to build.**
Written to be carried to the board.

---

## Standing note the board demanded (recorded first, so it can't be lost)

**"MET-in-plan" warmth in §§4–6 of the 001 reconciliation is NOT achievement.** The §7 tally is the true
state and the baseline the next sitting measures against. **And under MC-1's re-grade that baseline moves
DOWN, honestly:**

- 001 reconciliation as written: **4 PASS / 6 PARTIAL / 2 FAIL.**
- After MC-1's mechanism-or-script re-grade (below): **3 PASS / 6 PARTIAL / 3 FAIL**, of which **item 5's
  PASS is provisional** (magnitude unproven, MC-3). So: **2 firm PASS + 1 provisional / 6 PARTIAL / 3 FAIL.**

The tally fell because two "credible" verdicts rested on scripted calendar years. That is the mechanism-or-
script discipline working as intended — honest reds credited, per the advisor's own framing ("MC-1's
re-grade may lower the tally — that is the point").

---

## MC-1 — mechanism-or-script classification + re-grade — **ACCEPT-WITH-ACTION**

**Accepted as a CLASS discipline, not an instance fix** (confirming the advisor's read; it is R10-shaped and
epoch-4-critical — the evolutionary tournament reruns lives against *generated* worlds where a scripted
calendar year cannot fire).

### (a) Every §7 battery behaviour classified `mechanism | script | calibrated-parameter`

Definitions used: **mechanism** = behaviour derived from live market/world state, fires on novel inputs the
author never enumerated. **script** = behaviour keyed to a hardcoded enumerated case (a calendar year, a
hand-supplied flag) — cannot fire on an un-listed input. **calibrated-parameter** = a legitimately-fixed
magnitude sourced from a published/real series (allowed as scaffolding; can never *ground* a credibility
verdict on its own).

| # | Disqualifier | 001 verdict | Classification | Re-graded verdict | Anchor |
|---|---|---|---|---|---|
| 1 | Gas missing/subordinate | PARTIAL | **mechanism** (curve/OTC/cash-out constructs) + calibrated (`hedge_fraction=0` retail) | **PARTIAL** (unchanged; see MC-4 — mechanism present but *unconsumed*) | `gas_forward_curve.py:29-119`, `gas_otc_book.py:80-148` |
| 2 | No shape residual | PARTIAL | **mechanism** (`ShapeBand` DA/intraday) | **PARTIAL** (unchanged) | `shape_risk_book.py` |
| 3 | Look-ahead in hedging | PASS | **mechanism** (adversarial mutation test + enforcement hook) | **PASS** (unchanged — R15-solid) | `tests/interfaces/test_observable_trace.py:51`, `.claude/hooks/block_point_in_time_read.py` |
| 4 | No collateral physics | PARTIAL | **mechanism** (cash ledgers) but **script trigger** (`record_call` takes a hand-supplied loss) | **PARTIAL** (unchanged; the missing trigger is MC-2) | `otc_margin_book.py:65-78`, `wholesale_credit_exposure.py:70-75` |
| 5 | Demand/price independent | PASS | **mechanism** (joint tail from a shared weather draw) | **PASS — PROVISIONAL** (magnitude unproven, MC-3) | `sim/weather_price_chain.py`, `sim/weather_tail_demonstration.py` |
| 6 | Churn uncorrelated w/ market | PARTIAL | **SCRIPT** (`CRISIS_PASSIVE_YEARS={"2022"}`) + **calibrated-by-year** (`MARKET_SWITCHING_MULTIPLIER_BY_YEAR` dict, calendar-keyed) | **FAIL** (re-graded down — see below) | `churn_model.py:101,137`, `market_conditions.py:22-45` |
| 7 | Benign imbalance always | PASS | **SCRIPT trigger** (caller-supplied `stress: bool`) + **calibrated** (`_NIV_PREMIUM_STRESS=1.2`) | **PARTIAL** (re-graded down — see below) | `company/market/imbalance.py:28,47,55` |
| 8 | Cap mechanics absent | FAIL | **script/calibrated** (static per-year dict, no mechanism) | **FAIL** (unchanged) | `ofgem_price_cap.py:25-52` |
| 9 | Infinite liquidity | PARTIAL | **mechanism** (tenor-widening spread, bought at ask) | **PARTIAL** (unchanged) | `hedge_decision.py:24-28,87-94` |
| 10 | Profitable desk (no alarm) | FAIL | **absent** (doc-only, no code) | **FAIL** (unchanged) | this spec + reconciliation only |
| 11 | No losses/UIG/estimate error | PASS | **mechanism** (registers compute from inputs) + calibrated (LLF 1.12 = published regulatory value, legitimate) | **PASS** (unchanged) | `llf_register.py:41-62`, `uig_allocation_register.py:19-43`, `eac_drift_assessor.py:44-62` |
| 12 | Everything 100% hedged | PARTIAL | **mechanism** (bounded evolution in [0.85,1.0]) + calibrated (gas 0%) | **PARTIAL** (unchanged) | `sim/hedging_strategy.py:64` |

**Two script-based verdicts re-graded (the substance of MC-1):**

- **Item 6 → FAIL.** The board's exact test — *"if the sim generates a novel spike in a year not on the
  list, does the book swell?"* — the honest answer is **NO**. Both surviving pieces are calendar-keyed:
  `CRISIS_PASSIVE_YEARS = frozenset({"2022"})` (`churn_model.py:101`) is a hardcoded year, and
  `MARKET_SWITCHING_MULTIPLIER_BY_YEAR` (`market_conditions.py:22`) is a `{2016: 2.17 … 2022: 0.44 …}`
  lookup that returns a **calm-year value for any un-listed year** (`.get(renewal_year, 1.0)`). A generated
  2019 spike gets multiplier `1.43` — no swell. The genuine market-responsive mechanism the board wants
  ("fixed customers leave when the market falls below their fix; SVT book swells when the market gaps up")
  is **ABSENT** (already noted ABSENT in the 001 reconciliation). With its surviving half now classified
  script, item 6 has **no credible mechanism** → **FAIL**.

- **Item 7 → PARTIAL.** Two corrections, both owed under R9:
  1. **The "£9,999" is a docstring citation of real history, not a live parameter.** `grep -rn "9999"` over
     `company/`, `sim/`, `saas/`, `simulation/` finds it **only** in the `imbalance.py` module docstring
     ("In the 2021-22 crisis, SSP reached £9,999/MWh") — nowhere in executable code. The 001 reconciliation's
     anchor "SSP → £9,999/MWh in crisis (`imbalance.py:27-55`)" overstates: lines 27-55 contain only
     `_NIV_PREMIUM_STRESS = 1.2`.
  2. **The live crisis behaviour is script-triggered.** `compute_imbalance(..., stress: bool = False)`
     flips the premium from 18% to 120% **only when a caller passes `stress=True`** (`imbalance.py:47,55`).
     Nothing derives `stress` from world state (NIV volume, system tightness, a price gap). So imbalance
     *can* be non-benign, but only when a script says so — not when the generated world produces a tight
     system. The premium's direction is a real mechanism; its *crisis trigger* is script → **PARTIAL**.

### (b) Register mechanism-or-script as a standing fidelity rule — **ACCEPT**

Proposed for canon (director's to ratify): **a script or a calendar-keyed / hand-flag-keyed value may exist
as calibration scaffolding, but can NEVER ground a credibility (PASS/PARTIAL-credit) verdict.** A battery
item whose only passing evidence is script is graded on the mechanism it lacks, not the script it has. This
is R15-adjacent (a control that cannot fire on a novel input is theatre) and R10-adjacent (class fix, not
instance). Mechanised follow-on (queued, not built here): the fidelity-oracle harness tags each battery
verdict with its classification and refuses PASS on a script-only anchor.

### (c) Item 6 replacement — derive book-swell from market state — **ACCEPT, propose via gate**

Replace the calendar keys with a mechanism: churn/rollover pressure derived from **the live wholesale-vs-
locked-rate gap** (fixed customer in-the-money when market < their fix → sticky; out-of-the-money → leaves)
and **SVT-vs-cap headroom** (crisis passivity emerges when wholesale > cap so no fix undercuts the default —
computed, not the string "2022"). This is **contract-touching** → a `WVC_3` sub-mechanism proposal through
propose-then-proceed, **not built on sight of this doc.** `CRISIS_PASSIVE_YEARS` / the year-dict may remain
as a *calibration cross-check* only, never as the verdict's ground.

---

## MC-2 — collateral loop as a falsifiable R15 test — **ACCEPT (ready-made spec)**

Accepted exactly as the board framed it. The loop counts as **wired** only when a **test** (built first,
per propose-then-proceed) demonstrates both:

1. **A price move ALONE produces a cash call** — no hand-supplied loss. Concretely: `mark_to_market(price)`
   on the OTC/hedge book must *drive* `record_call(...)`; today `record_call` takes a hand-supplied loss
   (`wholesale_credit_exposure.py`, `otc_margin_book.py:65-78`) — the causal edge price→margin→cash is the
   gap (finding F2). The R15 mutation: perturb only the forward price by ±30%, assert a non-zero cash call
   appears with no other input touched.
2. **A 2021–22 replay shows ≥1 death-by-collateral path with P&L still positive** — i.e. facility headroom
   (`finance/margin_call_book.py:34-39`) exhausts and the supplier is insolvent-on-cash while cumulative
   mark-to-market P&L is ≥0. This is the board's "died of collateral before they died of P&L."

**Sequence:** test first (falsifiable, fails on today's un-wired loop = R15 proof it can fire), then the
loop, both via the gate. Until the test exists and fails-then-passes, item 4 stays PARTIAL.

---

## MC-3 — the £9,999 / 10× spike-tail coexistence — **ANSWERED (with two R9 corrections)**

The advisor's hypothesis was "two different organs." **Confirmed — but with the advisor's own gloss
corrected, which is the honest part:**

**Two organs, distinct:**

- **Organ A — the company's imbalance cost model** (`company/market/imbalance.py`). Company-side, behind the
  wall. The "£9,999" here is a **docstring citation of real 2021-22 history**, not a parameter (MC-1 item 7).
  The live magnitude is a calibrated `1.2×` stress premium, script-triggered. This organ is the *company's
  belief about imbalance cost*, and it is fine as far as it goes.

- **Organ B — the SIM/WORLD generated merit-order price engine** (`W1_6`, `sim/`;
  `docs/calibration/price-engine.md`). The declared **~10× defect lives HERE**, and the 001 reconciliation
  never mentioned it — **R9 owed and hereby paid.**

**R9 correction #1 — the direction is inverted in the advisor's gloss.** The advisor wrote "the generated
price engine's *under-drawn* tail." The evidence says the opposite: the merit-order ratio form
**OVER-estimates real SSP by ~10× even at the lowest γ** (`EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_
DISCOVER.md:105,375`; `WHOLESALE_VALUE_CHAIN_FRAME.md:30,335`). It is an **over-drawn** raw tail, which
**production runs sidestep by using real historical SSP** (`WVC_FRAME.md:30`). So the two figures do not even
point the same way: Organ A cites a real £9,999 spike that *did* happen; Organ B's raw generator would
manufacture spikes ~10× too *large* if used un-recalibrated, so it is held out of the production price path.

**R9 correction #2 — why the reconciliation omitted the defect.** It scoped item 7 to the *company's*
imbalance module (Organ A) and read "£9,999" as a live crisis parameter there. It never crossed to Organ B's
generated-engine calibration, so the declared ~10× blocker — which is a WORLD/SIM defect, not a company one —
fell outside the frame it drew. That is a real scoping miss; recorded.

**Item 5 sizing (the board's "proven to exist, not to be the right size"):** the joint demand-price tail is a
**mechanism** (shared weather draw), so it exists structurally — but its *magnitude* is measured, not yet
validated against reality. The coupled-gap ledger already quantifies it per cell
(`docs/observability/coupled_gap_ledger.json`: `cold_still_spike` n_tail=58, `tail_bias_mw` etc.), which is
where sizing gets adjudicated. **Item 5 stays PASS-PROVISIONAL until the 002/004 reconciliations' tail-sizing
verdicts stand.** Note: the 002/003/004 line-by-line reconciliations **have now landed** (commit `e2683a922`)
and their consistent finding is exactly the board's predicted defect — *mechanisms present, correlations and
tails under-sized*. So MC-3's fold-in is satisfied by cross-referencing those, not by re-deriving here.

---

## MC-4 — consumers-first audit of the deep gas plumbing — **ANSWERED (honest "nothing", tied to F1)**

**The honest answer is: today, essentially NOTHING consumes the deep gas trading plumbing. It is deep
capability without a consumer.** Audit (import-graph, excluding tests and worktrees):

- `company/trading/gas_forward_curve.py` (7-tenor curve w/ bands + crisis flag) — imported **only by
  `tests/company/trading/test_gas_forward_curve.py`**. **Zero production consumers.**
- `company/market/gas_otc_book.py` (OTC book) — imported **only by `tests/company/market/test_gas_otc_
  book.py`**. **Zero production consumers.**
- `company/market/gas_imbalance_ledger.py` (SBP/SSP cash-out) — the one apparent reference,
  `uig_allocation_register.py:7`, is a **docstring disambiguation** ("Distinct from gas_imbalance_ledger.py"),
  **not a consumer.** Zero production consumers.

What *is* wired is retail **gas consumption/billing** physics (spot pass-through in `bill_generator.py`,
`portfolio_position.py`) — i.e. gas is billed but **not traded/hedged through the plumbing**. This is the
concrete face of F1: `hedge_fraction=0` for retail gas means the forward curve, OTC book, and cash-out
ledgers have no decision that reads them.

**The fix is F1, and it closes MC-4 in one move:** make the **retail gas book actively hedged INTO the
existing plumbing** (a hedge program that reads `gas_forward_curve`, transacts on `gas_otc_book`, and settles
residual through `gas_imbalance_ledger`). That gives the plumbing its consumer and answers the challenge
simultaneously. Until then, per R15/the cost-centre discipline, the unconsumed gas plumbing must not be
counted as a credibility asset — a capability nothing consumes cannot pass a fidelity test. Build routes via
the gate (F1 is the largest re-prioritisation in the 001 reconciliation).

---

## Sequencing & disposition

- **items 5/6 provisional** until 002/004 reconciliations stand — those **have landed** (`e2683a922`);
  item 5 remains PASS-PROVISIONAL on tail-*sizing*, item 6 is re-graded FAIL on mechanism-or-script here.
- **Nothing builds on sight of this doc.** MC-1(c) item-6 replacement, MC-2 collateral test+loop, and MC-4/F1
  gas hedging are all **contract-touching** → proposals through WHOLESALE_VALUE_CHAIN propose-then-proceed.
- **Reversibility tag:** narrow/reversible for these answers; contract-touching for any mechanism replacement.

— Executive, answering the board's four material challenges, 2026-07-22.
