# [PLANNER-MINTED] Close the belief-vs-truth PAYMENT-FAILURE detection gap (W2_11) (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 4 — FRAME/DISCOVER half only, as the doc scopes). Attaches to existing atom `W2_11_payment_behaviour_source` (`maturity_map.yaml`).
> **BLOCKING SUB-ITEM (open):** Scope step 1 (DISCOVER/FRAME diagnosis of the 0.63 detection gap) is drawable now (doc-only); the **detection BUILD is roadmap-gated** — Billing+CRM rotate in after the three axes stabilise. **UNBLOCKS ON:** the director rotating Billing+CRM in / opening the front. FRAME half not yet done this tick (product-first lane drew the generator FRAME first per the ruling's sequencing guard) — next drawable DISCOVER item.

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
