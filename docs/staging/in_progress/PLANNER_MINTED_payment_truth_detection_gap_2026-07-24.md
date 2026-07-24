# [PLANNER-MINTED] Close the belief-vs-truth PAYMENT-FAILURE detection gap (W2_11) (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 4 — FRAME/DISCOVER half only, as the doc scopes). Attaches to existing atom `W2_11_payment_behaviour_source` (`maturity_map.yaml`).
> **BLOCKING SUB-ITEM (open):** ~~Scope step 1 (DISCOVER/FRAME diagnosis of the 0.63 detection gap) is drawable now (doc-only)~~ **DONE this tick (2026-07-24 worker tick) — see the "DISCOVER/FRAME diagnosis" section appended below. Mechanism named + MEASURED: the gap is the non-DD-channel no-remittance blind spot, exactly (offline harness: flagged 877 == true-DD 877, non-DD leaked 0, gap = 338/1215 = the non-DD fraction). The `regime_mixed_attributed_to_G2` tag is a SEPARATE, harness-side grid-attribution approximation, not a detection-rule collapse.** The **detection BUILD is roadmap-gated** — Billing+CRM rotate in after the three axes stabilise. **UNBLOCKS ON:** the director rotating Billing+CRM in / opening the front; the propose-half detection mechanism (expected-collection reconciliation) is named below and ready.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Minted from a fidelity-ledger row. **Propose-then-proceed.**

## Fidelity-ledger row served
`docs/observability/fidelity_evidence_ledger.json` → `live_payment_detection_gap` (atom `W2_11_payment_truth`, cell `A1_G2`):

- `true_failures`: **43**
- `believed_failures`: **16**
- `detection_gap`: **0.63** (the company sees fewer than 4 in 10 of the payment failures that actually occurred)
- simplification tagged: `live_payment_gap_regime_mixed_attributed_to_G2`.

This is a **coupled-triad gap** in exactly the form the triad law wants surfaced: WORLD produced 43 payment failures, COMPANY (through the wall) believes 16 — the GAP is the score, and it is currently wide.

## Ratified goal served
- **COUPLED_TRIAD doctrine** (CLAUDE.md): *no company capability is complete until it has faced a world that can defeat it; the gap is reported per coupled pair.* W2_11 has faced the world and is being defeated (0.63 gap) — closing/bounding it is the triad's own definition of progress.
- **DIRECTOR_AXES roadmap:** Billing + CRM rotate in after the three axes stabilise. A payment-truth detection organ is the substrate that rotation needs — building the diagnosis now (doc/FRAME) is drawable ahead of the rotation; the wiring BUILD proceeds when the roadmap turns.

## Real-world fidelity gained
A real supplier that only detects 37% of payment failures has a broken collections/arrears signal — every downstream CRM action (dunning, vulnerability flags, SoLR risk) fires on a lie. Narrowing the detection gap makes arrears and collections behave like a real book. Honesty guard: the goal is a *smaller measured gap*, never a company that *believes* it detects everything (that would be a fail-open control — a wider hidden gap).

## Scope (propose)
1. DISCOVER/FRAME (drawable now): diagnose the 0.63 gap — the `regime_mixed_attributed_to_G2` tag suggests failures from multiple regimes are being collapsed onto one cell / one detection rule. Name which real payment-failure modes the company currently cannot observe through the wall (direct-debit bounce vs card decline vs standing-order lapse vs partial payment).
2. Propose the detection mechanism (through-the-wall observables only — the company sees its own bank feed / failed-collection events, never sim internals) OR register the irreducible portion as a named simplification with its measured residual gap (R10).
3. R15: a test that the improved detector *raises* believed_failures toward true_failures on the A1_G2 cell (fires on the fix), and a mutation proving the detector can still miss (it must not fail-open to "all detected").
4. Re-measure and update the ledger row (the triad gap shrinks visibly).

## Walls untouched
Generator ground truth (the 43 true failures are sim truth — the company must *discover*, never read them); no curriculum change; no L3 self-promote. Billing/CRM BUILD-open is roadmap-gated — the FRAME/DISCOVER half is drawable now, the wiring BUILD lands when the director rotates the roadmap or opens the front.

## Propose-then-proceed window
FRAME/DISCOVER proceeds immediately. The detection BUILD proceeds under reversible authority once the roadmap rotates Billing+CRM in (or the director opens it); until then it stays a ready propose-half, not idle.

---

## DISCOVER/FRAME diagnosis (DONE — 2026-07-24 worker tick, R4: measured against the closed-loop harness, not argued)

**Method.** Read both sides of the wall — the WORLD source (`simulation/payment_behaviour_source.py`), the seam (`simulation/payment_seam_adapter.py`), the COMPANY belief (`company/billing/payment_observation_consumer.py`), the offline gap harness (`tools/couple_w2_11_d5.py`) and the LIVE ledger writer (`background/live_fidelity_evidence.py`). Then RAN the closed-loop harness (`python3 -m tools.couple_w2_11_d5 --customers 4000 --seed 0`) for a hard channel-split, rather than reasoning structurally.

### The gap has TWO distinct sources living under one ledger number — separate them or the BUILD chases the wrong thing.

**SOURCE 1 — the no-remittance CHANNEL blind spot (the real belief-vs-truth detection gap; DOMINANT and, measured, the *entire* gap).**
A failed **non-Direct-Debit** payment (standing_order / card / prepayment) emits **no `WallResponse` at all** — a real supplier's bank feed has nothing to report for a *missed customer-initiated push payment* (there is no ARUDD/Bacs failure event to receive when nobody pushed the money). `PaymentObservationConsumer`'s `recent_dd_failures` and `arrears_risk_belief` are built **only** from observed DD/rail-failure events, so every non-DD failure is a **guaranteed miss** by construction (the harness's own witness counter `n_flagged_non_dd` must stay 0 — a non-zero value would be a *leak*, not an improvement).

Measured proof (offline harness, 4000 customers × 3 periods = 12,000 cases, seed 0):

| quantity | value |
|---|---|
| true failures (all channels) | **1215** |
| true DD failures | 877 |
| true non-DD failures | 338 |
| flagged (company belief) | **877** — *exactly* the DD failures |
| non-DD "leaked" into belief | **0** (the blind spot's witness) |
| detection gap | 338 / 1215 = **0.2781** = *exactly* the non-DD-failure fraction |

`believed == true_DD` to the unit, and `gap == non_DD / total` to the digit. **The entire detection gap is the non-DD channel blindness — no other mechanism contributes.** This is CORRECT modelling per the epistemic wall (R12/R13: a near-zero gap here would be a RED FLAG / leak, never a success) — the company is not *broken*, it is genuinely blind to three of four payment channels' failures, exactly like a real supplier that only receives Bacs DD outcome reports.

Which real failure modes the company **can** vs **cannot** observe through the wall:
- **direct_debit bounce** (`INSUFFICIENT_FUNDS` vs cancelled/other) — **OBSERVABLE** (Bacs ARUDD-style outcome report → `WallResponse`). These are the 16 (live) / 877 (offline) it believes.
- **standing_order lapse** — **NOT observable** (no failure event exists for a push that never happened).
- **card decline** — **NOT observable** through the current seam.
- **prepayment / partial non-DD payment** — **NOT observable**.

**Why the live ledger reads 0.63 while the offline scaffold reads 0.28:** identical mechanism, different populations. The live 2016-25 `run_phase2b` book has a *higher non-DD share of failures* (≈63% of failures are on push channels) than the illustrative offline `_STRESS_MIX` (≈28%). The gap number tracks the payment-method mix of the failing population — not a detector defect that changed. Sub-finding worth carrying: **the live method-mix implies most failures are on channels the company structurally cannot see** — the collections/arrears signal is worse in the live world than the scaffold suggests.

**SOURCE 2 — the `regime_mixed_attributed_to_G2` tag is NOT a detection defect; it is a harness grid-ATTRIBUTION approximation.**
The original mint hypothesised "failures from multiple regimes collapsed onto one cell / one detection rule." **Half right, and the important half is wrong for the BUILD:** the collapse is real but it is *measurement-side*, not *detection-side*. Per `background/live_fidelity_evidence.py` (`LIVE_CELL_ID = "A1_G2"`, `_REGIME_MIXED_SIMP_ID`): a live run spans 2016-25 (calm years **and** the 2021-22 gas crisis), so the single measured gap is regime-MIXED, but it is filed under the **one** `A1_G2` grid cell (affordability-stressed household × crisis/sustained-spike) while the **other 14 cells stay UNMEASURED** (G1's fail-open floor scores them ≥ the worst measured cell — "one corner lit, the rest honestly dark"). This is an R10-registered coverage approximation on the *emitted evidence record*, and **no detection rule is collapsing multiple failure modes** — Source 1 is a clean single mechanism.

### Consequence for the BUILD (propose-half — keep the two sources apart)

1. **Close SOURCE 1 (the company capability, roadmap-gated on Billing+CRM):** the through-the-wall mechanism a real supplier actually uses for push channels is **expected-collection reconciliation** — the company knows its own issued bills and due dates (its own ledger) and observes its own **bank statement** (money received / not received). A missed push payment is detectable as *"billed £X due by D, no matching credit received by D+N"* — the **absence of an expected inbound credit**, without ever needing a failure event that push channels don't generate. This is genuinely through-the-wall (own ledger + own bank feed, never `PaymentEvent.result`). **R12 honesty guard:** it *narrows*, never closes — partial payment, late-but-eventual payment, and the ambiguous account-level `correlation_id` → oldest-first allocation fallback all leave residual. Register the irreducible residual as a named R10 simplification with its **measured** residual gap; the goal is a *smaller measured gap*, never `believed == true` (that is the fail-open failure mode the mint's own honesty guard names).
2. **Close SOURCE 2 separately (harness coverage, drawable now, NOT roadmap-gated):** it is closed by **measuring more of the 5×3 grid** (per-regime split the live population, lighting additional cells), NOT by any detector change. Do not let a grid-coverage improvement masquerade as a detection improvement — they are different work with different owners.

### R15 pre-registration (for the eventual BUILD, so the control can fail)
- Detector test: a reconciliation detector must **raise** believed-failures toward true-failures on the non-DD cases (fires on the fix); **and** a mutation proving it still misses partial/late payments (must not fail-open to "all detected"). The existing `n_flagged_non_dd == 0` witness flips to `> 0` only when a *legitimate* non-DD detection path lands — a fast regression anchor already in the harness.

### Walls respected this tick
Doc-only. No generator/ground-truth read (the 43/1215 truths stay sim-side; the company must *discover*). No curriculum change. No level self-promote. No BUILD started (roadmap-gated) — this is the ready propose-half. `SELF_INTERRUPT`: one bounded DISCOVER slice, then STOP.
