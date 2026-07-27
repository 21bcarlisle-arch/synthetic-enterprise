# Response — DIRECTOR_RULING_HARNESS_EXIT_CRITERION_RATIFIED_2026-07-27 (MINT + question answered)

Ruling actioned as a **MINT source** (§2+§4 DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE). One atom minted per named deliverable in the WORK THIS CREATES block; the one-line question answered inline. Committed to `docs/design/maturity_map.yaml`.

## Coverage check (no re-mints)
Grep of `maturity_map.yaml` before minting: NO atom existed for the exit criterion — it lived only as `HARNESS_EXIT_CRITERION_PROPOSAL_2026-07-27.md` (prose) + this ratification. None of the four deliverables was already covered by a map atom or a `PLANNER_MINTED_*` doc. All three build-deliverables are therefore NEW mints; nothing re-minted.

## Deliverables 1–3 → drawable atoms (lane H_harness, close_to_learn, level 0→3, blocked_on: null — director-opened H-lane per decision 2a, drawable NOW)

- **HX1_exit_criterion_counter_mechanise** (deliverable 1) — the ratified N=3 consecutive-content-advance / zero-stall-class counter computed from PRIMARY STATE ONLY (git, map, gate ledger, fidelity register, backlog), never the tick's own enumeration (LAW C). R15 PAIR is the exit criterion, both-ways mandatory: a synthetic stall RESETS the counter; three clean content advances SATISFY it; pure function of primary state (TAUTOLOGY guard); non-finite/missing inputs REJECT (FAIL-OPEN guard). R12: gate on a decision, never a quality score. depends_on HX2.
- **HX2_stall_set_coverage_verdict** (deliverable 2) — written verdict on each of the four named events (console rescue / publish-wedge >1h / origin-freeze >30min / advisor-restart-ruling): detected, detector-added (R15-proven, must NOT trip on a legitimate DECISION-class touch), or argued-not-stall-class with evidence. Feeds HX1's stall-class input as the enumerated UNION (FAIL-SILENT guard). Leaf atom — drawable first.
- **HX3_counter_published_and_derivable** (deliverable 3) — daily self-note (SM1, reuse not accrete) publishes current count + last-reset cause; the coherence-by-derivation gate (`tools/moap_coherence_gate.py`) extended so ANY surface claiming "harness done for now" must DERIVE it from the HX1 counter — a hand-written claim is a publish-gate failure. R11 to the rendered value + R15 both-ways mutation. depends_on HX1, HX2.

Dependency chain: HX2 → HX1 → HX3. Level moves stay `blocked_on: director_level_up` (R16 — no self-bump). YAML validated, 141 atoms, no duplicate ids.

## Deliverable 4 — one-line answer on the merit_order date (answered inline, not an atom)

**`merit_order` (`W1_6b_merit_order_reconstruction`) is drawable only from 2026-07-28 because of a SELF-IMPOSED R13 propose-then-proceed BUILD window — a scheduling artifact, NOT an epoch/front gate and NOT a dependency block. It needs NO director act to open: a tick on or after 2026-07-28 draws it automatically.**

Honest follow (per your "a date is not a reason" challenge): the window is the machine's own caution, not a real gate. The reconstruction touches the R13 baseline, so a 1-day window was held to let you revise before the build proceeds with *no interim tuning*. It expires tomorrow on its own; if you'd rather not wait, say the word and I close it and draw merit_order now. It is not hiding a decision — the reason is exactly this R13 baseline-discipline hold, stated in the atom's `blocked_on`.

— autonomous worker, 2026-07-27
