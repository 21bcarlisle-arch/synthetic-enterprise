<!-- SUPERVISOR_DRAW: blocked -->
<!--
STATUS 2026-07-25 (parked in_progress — one sub-item LANDED, remainder belongs to the value_chain atom):
- §3 FACILITY-SIZING DEFECT: **LANDED.** `company/finance/margin_call_book.py` now derives the
  committed facility from the book's own gross marked exposure (`book_scaled_credit_facility_gbp`,
  FACILITY_COVERAGE_MULTIPLE=1.5, floored FACILITY_MIN_GBP=£250k), wired live via
  `build_margin_calls_from_mtm` (default credit_facility_gbp=None -> book-derived). The fixed £5m is
  gone from the live path. R15 both-ways: a fixed-facility mutant trips 7 controls; epistemic PASS.
  Coverage multiple + floor declared R10 named simplification, NOT tuned to outcome (MC-2 §4/R12).
- OPEN, blocking sub-item -> tracked by `in_progress/PLANNER_MINTED_value_chain_observation_window_cap_2026-07-24.md`:
  §2 breaking-strain sweep (0.8/1.0/1.2/1.5×) + run-ledger fields (liquidity_minimum, cover_minimum,
  outcome+cause); §1 acceptance-bar wiring (price-move-alone cash call; death-by-collateral while P&L
  survives). Do NOT run the sweep to back-tune the facility (R12).
- FOLLOW-ON (DISCOVER, non-blocking): calibrate FACILITY_COVERAGE_MULTIPLE / FACILITY_MIN_GBP to
  published UK-supplier RCF-to-book ratios (external anchor; fidelity-to-reality, blind to P&L, R13).
- §6 growth/leverage: REGISTERED for its own director session, not built here.
-->
# [DIRECTOR-RULING] — MC-2: no difficulty knob. Real 2021–22 history is the test; breaking-strain sweep around it. Facility sizing is a defect, not a dial. (2026-07-25)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers the R13 curriculum wall on `PLANNER_MINTED_value_chain_observation_window_cap` (MC-2 death-test difficulty).

## 1. No difficulty knob is set — and none is created

**The MC-2 test is the 2021–22 replay**, exactly as the board specified it: *"the collateral loop counts as wired only when a price move alone produces a cash call, and a 2021–22 replay shows at least one path to death-by-collateral while the P&L still survives."* Real history is the honest severity. An invented multiplier is a tuning surface, and a difficulty dial will eventually be turned until the test returns the wanted answer.

**Acceptance bar, verbatim and unrelaxed:**
- a **price move alone** produces a cash call — no hand-supplied loss, no injected shock at the cash line;
- at least one path shows **death-by-collateral while the P&L still survives.**

The second clause is the load-bearing one. It reproduces the actual 2021–22 failure shape: companies solvent on paper and dead on cash. If the test cannot produce that shape, the loop is not wired, however many margin calls it fires.

## 2. Breaking-strain sweep around the real world

Around the 1.0× replay, sweep severity **0.8× / 1.0× / 1.2× / 1.5×** and record **the dose at which death arrives**. This is the continuous survival signal ruled this morning — it converts a binary verdict into a comparable number, and it writes directly into the run-ledger fields already specified (`liquidity_minimum`, `cover_minimum`, outcome + cause). One mechanism, two uses. The sweep is a *measurement*, not a curriculum world: sweep points are not ratified scenarios and their results are reported as breaking strain, never as EV.

## 3. Facility sizing is a DEFECT to fix, not a difficulty to choose

`MarginCallBook.__init__(credit_facility_gbp=5_000_000.0)` is a hardcoded £5m liquidity facility standing against a book that, at the activated N=200, is orders of magnitude smaller. Nothing can kill that; the death test would be theatre. **The facility must scale with the book** — a real supplier's facility relates to its volume, credit standing and posted collateral. Fix it as a mechanism (observable, book-derived, through the wall) under the existing reversible authority. **It must not be smuggled in as a difficulty setting**, in either direction: shrinking the facility to force a death is the same R12 breach as inflating a multiplier.

Same discipline applies to `_CREDIT_LIMIT_BY_RATING` — the observation-window mechanic replaces it because the cap should be *earned and eroded* from observed exposure, not because a smaller number kills more convincingly.

## 4. R12 guard — what to do if it survives everything

If the company survives the replay and the whole sweep, **do not raise severity until it dies.** Investigate the mechanism (R4): facility oversized relative to book, MtM understated, margin calls too slow or too small, hedge cover masking the exposure. A company that cannot die to collateral is a **fail-open believability control** — the defect is real and must be found, but the fix is mechanism, never difficulty inflation. Report the diagnosis; escalate if the honest answer is that the loop needs a design change.

## 5. WVC_R world-half

The coupled-triad world half proceeds under the standing twin authorization at L1/L2, ledger-backed, on the mechanism only. Any **scenario value** that would become a named curriculum world returns to the director (R13), as ratified.

## 6. REGISTERED, not ruled — growth, leverage and the risk/opportunity balance

The director has flagged the next strategic question and it is **not to be built ahead of its own session**: *a company can hoard profit but will not grow; growth may be the one unavoidable cost.* Recorded framing for that session, plus its acute relevance here — **growth financed by leverage was the proximate cause of death for ~30 UK suppliers in 2021–22**: the obligations of a fast-grown book and the collateral calls of a price spike arrive together, because they are driven by the same event. MC-2 is therefore the *first half* of the growth question, not a separate one.

To carry into that session (register only): acquisition cost and channel (including change-of-tenancy as the near-zero-CAC prime moment, already a DISCOVER atom); the negative working-capital cycle of each new customer (hedge collateral, bill-to-cash lag, bad-debt provisioning); growth *quality* — which households are worth acquiring on cost-to-serve, payment reliability, shape-fit to the hedge and abatement potential; retention as capital-free growth; and the central question the tournament is uniquely able to answer — **what is the maximum growth rate sustainable under the survival constraint, across the sampled worlds?** Do not build a growth or capital organ before that session.

**Risk & proportionality:** removes a proposed tuning surface, sets a historical acceptance bar, fixes a hardcoded facility as a mechanism, and registers a horizon question. No curriculum value is set by this ruling. Tag: **proceed; no difficulty knob may be created.**

— Advisor bridge, carrying the director's ruling, 2026-07-25.
