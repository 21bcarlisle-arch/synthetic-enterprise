# G1/G2/G3 live company consumer — DISCOVER/design start (2026-07-19)

**Why:** G1/G2/G3 (the fidelity machinery) are `blocked_on: coupled_triad_l3_needs_live_company_
consumer`. L2→L3 for a company-lane/measurement atom requires (COUPLED_TRIAD_DESIGN §3.1) that it
"has faced a world that can defeat it": evaluated against a coupled world atom ≥L2 whose hidden
truth it acted on **through the wall**, with the pair's `gap` measured and **non-degenerate
(gap>0 — gap=0 is an epistemic-wall leak, not a pass)**. Today the machinery scores the *price
engine's* fidelity (SIM-vs-real, `fidelity_emitter.py`) — that is not a COMPANY belief-vs-SIM-truth
pair. The missing piece is a **live company consumer**: a company atom that forms a belief through
the wall, whose gap vs SIM truth the fidelity machinery scores.

## The seam (what the consumer must and must NOT do)

- **Company belief — observables only.** The consumer reads its inputs through
  `company/interfaces/sim_interface.py` (meter reads, market feeds, payments, contacts) — never SIM
  internals. This is the wall: *could a real UK supplier know this, at that moment?* `epistemic_
  verifier` must stay PASS over the consumer's company-side code.
- **SIM truth — harness side only.** The answer-key (the hidden θ the belief is scored against) is
  read on the **harness** side, never handed to the company. The gap is computed where both are
  visible (the harness), not inside the company (which would be a leak → gap→0).
- **Gap flow.** company belief `b` + SIM truth `θ` → the coupled gap metric (COUPLED_TRIAD §1,
  `gap = raw_gap/g0`, normalised to a no-skill baseline) → scored by **G1** (`fidelity_grid_scorer`,
  per-cell severity), emitted by **G2** (`fidelity_evidence_ledger.append_record`), chained by **G3**
  (`fidelity_inspection_chain`, belief/truth wall enforced in-schema). A non-degenerate `gap>0`
  block recorded on the pair closes the loop and lets G1/G2/G3 draw to L3.

## Candidate live pair (build the smallest closed loop first — R4)

Pick an **existing company twin already ≥L2** whose world partner is ≥L2, so no new world/company
capability is required — only the wiring + the gap measurement. Strong candidate from the declared
topology (`test_maturity_map_facets.EXPECTED_PAIRS`):

- **`C6_affordability_inference` ⇄ `W2_4_household_budget`** — the archetypal gap (COUPLED_TRIAD §1
  lead example): the company infers affordability/arrears risk from observable payment+meter
  behaviour; SIM truth is the household's hidden budget state. Metric: classification (can't-pay vs
  won't-pay / at-risk). Both sides are mature. *Alternate:* `C9_cantpay_wontpay_classifier ⇄
  W2_7_willingness_classification`.

The consumer is a **harness organ** that: runs the chosen company twin against the chosen world
atom over a real run, reads `b` (company output) and `θ` (SIM answer-key) on their correct sides of
the wall, computes the gap, and drives G1→G2→G3. It is the *first live instance* of the coupled
triad, not a new company capability.

## Build shape (fresh pass — NOT built here)

1. A harness-side `live_coupled_gap.py` (sits beside `fidelity_emitter.py`): given (company_twin_id,
   world_atom_id), assemble `b` via the company's observable-only path and `θ` via the harness
   answer-key, compute the normalised gap, and emit through G1/G2/G3.
2. Write the `gap` block onto **both** atoms of the pair (COUPLED_TRIAD §3.3) — symmetric.
3. R15: mutation — if the company path can see `θ` (a wall leak), gap→0 and the control must FIRE
   (gap=0 is a leak, never a pass). If the answer-key is unavailable, the check FAILS (fail-silent
   guard), never scores green.
4. Verify `epistemic_verifier` PASS + the full publish gate; then G1/G2/G3 draw to L3 (the gap block
   satisfies their `blocked_on`).

## Status
DISCOVER/design start only — doc-only, wall intact. The BUILD is a fresh, careful pass (the
epistemic wall is physics-grade; a rushed consumer that leaks θ is the one defect that most
discredits the whole project). Front is otherwise full: A/D at L1, W1_2..W1_10 cascade BUILD-open.
