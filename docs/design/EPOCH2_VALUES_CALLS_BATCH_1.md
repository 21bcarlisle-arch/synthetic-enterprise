# Epoch-2 campaign — values-calls BATCH 1 (proceed-on-default, director review)

**Provenance:** director console 2026-07-19, gate-after operating model, item 3 — *"Values-calls never stop
work: proceed on a conservative default marked 'asserted', batch them for my review. First batch: the campaign's
flagged calls, with your recommended default per item."*

**How to read this:** each row is a values/curriculum call surfaced (not invented) by the A–G DISCOVER docs. I
am **proceeding NOW** on the **asserted default** in column 3 so BUILD is unblocked; every default is **reversible**
(a constant/flag change + re-run). Column 4 is my recommendation and *why it is the conservative choice*. Override
any of these at the console and I re-run — no rebuild, just a re-parameterise. All are **category-6 values / R13
curriculum** = yours by right; the defaults below are the honest NULLs that keep *value* out of the *scoring*, not
attempts to pre-empt your call.

Governing principle across all six: **the scoring frame stays value-free; the null default can never silently
hide or drop a corner** (it errs toward over-measuring / over-investing, never under). Any harm/impact weight you
author enters as *value* on top of the frame, versioned and named (R13), never as a silent parameter.

| # | Values-call (source) | Asserted default I'm running | Why this is the conservative null / what your override changes |
|---|---|---|---|
| 1 | **Cell weighting in the worst-cell MAX** — equal vs harm-weighted (atom A §5 q4; same call re-used by atom E §5 for the settled-gap aggregation) | **Equal-cell weighting** — every in-grid cell counts equally in the MAX; no harm weight in scoring. | A harm weight is *value entering scoring*, which the frame deliberately excludes (A §1.4). Equal is the only choice that doesn't pre-decide which customers matter. Your override: author a `harm_weight(cell)` (vulnerable-edge > reference) → the "worst cell" becomes harm-shaped. Reversible: a weight vector, re-ranked in seconds. |
| 2 | **Grid completeness** — is any supplier-killing physics unrepresented by the 5-archetype × 3-regime grid? (atom A §5 q6) | **Ship the 5×3 grid as-is**, marked **provisional** via atom G's *map-of-ignorance* (unmeasured/unrepresented cells score top-severity, never hidden). | Adding a cell is cheap and reversible; the grid is domain-reasoned + your named list. The map-of-ignorance guarantees an unrepresented physics shows as a blind spot, not a silent pass — so "incomplete" fails loud rather than flattering us. Your override: name a missing archetype/regime → I add the row/column. |
| 3 | **`commercial_weight(cell)` / `κ` harm-weighting** — weight lift & exposure by "where it commercially matters"; customer-harm vs company-loss (atoms F §5.2, G §6.1) | **`commercial_weight = 1` (equal)**; **`κ` = the £ covariance `E[Δvol·spot]`** in the joint tail for *financial* cells (data-derived, blind to P&L), and a **flat/qualitative harm rank** for *collections* cells until you author a harm matrix. | Equal weight is the honest null (measure fidelity, don't pre-weight it — R12). The £ covariance is *estimated, not invented* (atom D's D3 / B-C §3), so it needs no values call — only the price-engine recal (task 1). The **customer-harm-vs-margin trade** is pure value → yours. Your override: a `commercial_weight`/harm matrix `C[q,q̂]` → exposure re-weights. |
| 4 | **`τ` investment threshold** — the £ "do-not-invest" floor on `priority = gap × exposure` (atom F §4, §5.2) | **`τ = 0`** — rank and surface the *full* gap; invest in everything; drop nothing. | τ=0 is the only value that can't silently hide a corner (an omitted item is invisible; a "priority £X < τ, deferred" item is an auditable line). Raising τ is a deliberate, logged de-scoping decision — yours. Your override: set τ>0 → cells below it render as explicit "deferred", still visible. |
| 5 | **`L_min` / `ρ_min` fidelity floors** — and whether any is a *promotion gate* (atom D §7 q5) | **Baseline-fidelity DIAGNOSTICS, not gates** — they flag a weak-fidelity link; they never gate a promotion or shorten verification. | Making a fidelity statistic a promotion gate invites goal-seeking the statistic (R12 anti-goal-seek); a floor that *gates* would pressure the estimate toward the floor. Kept diagnostic, the number stays honest. Your override: designate a specific link's floor as gating → it becomes a named gate (exit-test, not a tuning target). |
| 6 | **Atom E metric normalisation** — headline `settled_position_belief_gap` = curve-area vs single-as-of snapshot vs cohort aggregate (atom E §5 q5) | **Curve-area over `d` (t0 → RF), normalised by true settled magnitude**, aggregated **equal-cell** (per default 1). | Curve-area captures the whole belief-vs-truth *trajectory* (how long, not just how far, the company was wrong) — a single snapshot hides a company that is briefly very wrong then self-corrects, or slowly-wrong-forever. Equal-cell per call 1. Your override: prefer a peak/snapshot metric → swap the aggregator. |

## Status
- **Proceeding on all six defaults now** (gate-after item 3). These unblock the campaign's BUILD parameterisation.
- Each is logged to the decision ledger (`background/decision_log.py`) as reversible/asserted and will surface on
  the site's decision-ledger view (observability DoD, gate-after item 6).
- **None is a wall.** Calls 1–4 & 6 are value/curriculum (category-6, R13) — override at will. Call 5's *default*
  (diagnostic) is mine to set under R12; only *promoting a floor to a gate* is your call.
- **Dependency:** call 3's `κ` covariance term is blocked on **task 1 (the SSP price-engine recal)** — until the
  price engine is calibrated, `κ` for financial cells runs on the qualitative harm rank (call 3's collections path).
