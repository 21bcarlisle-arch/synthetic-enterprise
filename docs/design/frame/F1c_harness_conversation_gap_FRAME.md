# FRAME — F1c HARNESS conversation gap organ

**Atom:** `F1c_harness_conversation_gap` (maturity_map.yaml ~line 2480). `lane: H_harness`,
`value_stream: close_to_learn`, `epoch: 3`, `level_current: 0`, `level_target: 2`,
`loop_stage: frame` (this document is that FRAME deliverable). `file_scope:
[tests/harness/test_conversation_gap.py, background/conversation_gap_ledger.py]`.

**Provenance.** Closes the F1 "simulating conversations" coupled triad (director-graduated
2026-07-22, BUILD-waived 2026-07-23 commit `5143ed41f`):
`docs/design/proposals/F1_conversations_coupled_triad_BUILD_PROPOSAL.md` §3c/§4,
`docs/design/frame/F1_conversations_coupled_triad_FRAME.md` §3c/§4. This document is the atom-level
FRAME + the test-first spec the atom's own map entry calls for ("its spec is written test-first").

---

## 0. Premise correction (R10 honesty — checked against the live map, not assumed)

The task brief that opened this FRAME stated *"F1b is BUILT (L2); F1a is OPEN/not built."* That is
**stale**. Reading `docs/design/maturity_map.yaml` lines 2440–2479 directly (not the brief) shows:

- `F1a_sim_customer_response` — `level_current: 2`, `loop_stage: harden`, ledgered
  `LEVEL_UP_SELF_CERTIFIED` 2026-07-30.
- `F1b_company_comms` — `level_current: 2`, `loop_stage: harden`, ledgered
  `LEVEL_UP_SELF_CERTIFIED` 2026-07-30 (merge `fdd015f1c`).

**Both upstream atoms are already BUILT to L2 and their code is on disk**:
`simulation/conversation_response.py`, `company/comms/conversation_generator.py`,
`company/comms/susceptibility_estimator.py`, `interface/contracts/conversation_seam.py`. This
FRAME + its exit tests therefore exercise the **real, shipped F1a/F1b modules directly** — not a
synthetic/injected truth fixture. The task brief's instruction to fall back to a synthetic fixture
"if F1a's truth scalar doesn't exist yet" does not apply; the stronger, real-code path was taken.

**What genuinely IS still open (the honest gap the brief was gesturing at, one level down from
where it placed it):** F1a/F1b are **not invoked by any `run_phase*.py` driver** (grep-confirmed at
FRAME time — no `conversation_response` / `ConversationGenerator` / `SusceptibilityEstimator`
symbol outside `company/comms/`, `simulation/`, and their own tests). There is therefore no live
population conversation history in `docs/reports/run_output_latest.json` for this organ to read the
way `background/dd_h_solvency_gap.py` reads a published DD3 block. **This is the real missing
upstream**, and this FRAME's design responds to it directly (§2).

---

## 1. What this organ measures (verbatim from the atom spec)

1. **Belief-vs-truth susceptibility gap** per customer — company posterior category/confidence
   (`SusceptibilityEstimator.inferred_*_susceptibility` / `*_means()`) vs the SIM's true category
   (`simulation.nudge_physics.susceptibility_for` / `tone_susceptibility_for`).
2. **Did the conversation improve the outcome** vs a no-message/neutral control, scored on the
   **Citizens-Advice weighting 55/35/10** (customer service / complaints / commitments — CS-heavy,
   not equal-weighted; source: `docs/market_research/f1_simulating_conversations.md`, "Citizens
   Advice star-rating" table, Open item 1).
3. **The MANDATORY R15 intent-leak control** — a company whose action correlates with the true
   hidden trait *beyond what its observed replies justify* is a named defect the harness must catch.

## 2. Design: a self-contained referee, population-source-agnostic

Because there is no live run to read (§0), `background/conversation_gap_ledger.py` builds its own
deterministic synthetic customer population (`_synthetic_population`, ids `f1c_harness_cust_NNNN`)
and drives the **real** `simulation.conversation_response.respond` + F1b's
`SusceptibilityEstimator.observe_response` to produce a genuine, non-fabricated observation history.
The three measurement functions (`belief_vs_truth_gap`, `outcome_uplift_vs_control`,
`intent_leak_rate`) take a population + estimator as **plain arguments** — when the triad is wired
into a live run, only the population source changes (swap `_synthetic_population` for the live
customer set and a live-recorded estimator); the measurement logic does not.

**A residual this FRAME found and names, not fixes (R10):** the shipped F1b `ConversationGenerator`,
wired to a genuinely empty estimator, sends `neutral_framed`/`neutral_toned` **forever** — it ships
no self-directed exploration policy (`_tone_and_framing`'s empty-belief branch always returns the
neutral default; F1b's own test `test_generator_sends_the_lever_the_belief_prefers` proves this by
hand-feeding observations rather than letting the generator explore itself). Without *some*
exploration schedule, this triad can never depart from "always neutral" in a closed loop, and the
belief-vs-truth gap would be a trivial, uninformative 100% for every customer forever. This organ's
`_train_estimator` supplies a round-robin exploration schedule **for measurement purposes only**, on
a throwaway estimator it owns — never altering F1b's shipped behaviour. **This is a genuine product
capability gap in F1b** (a real supplier's CRM has some explore/exploit policy; this one doesn't),
logged here for a future atom, not fixed in this file_scope.

**A second finding from empirically driving the real F1a model (R12 — reported, not tuned away):**
belief convergence is genuinely **slow**. The matched-lever uplift bands are modest relative to the
situation base rates (framing +10–35% relative, tone +3–10pp), so a Beta(1,1)/argmax-with-epsilon
estimator needs on the order of hundreds of real observations per lever before the framing-category
match rate climbs from a noisy ~0.45 (at 15–60 rounds) toward its ~0.80 asymptote (verified directly:
60 customers × 15 rounds → 0.45; × 1200 rounds → 0.80, matching the ~80% non-neutral population
share). `measure()`'s default (`_DEFAULT_TRAINING_ROUNDS = 15`) is deliberately **not** inflated to
make the diagnostic look more converged — R12 forbids tuning a diagnostic toward a flattering
number. The shipped default therefore honestly reports a partially-converged gap; tests that need a
decisive signal use a hand-fed confident belief (§4) instead of relying on convergence speed.

## 3. CA-weighted (55/35/10) outcome scoring — what maps to what, and what's honestly inert

| CA axis | weight | this organ's proxy |
|---|---|---|
| Customer service (contact ease, timely, working service) | 55% | `ResponseAction` ∈ {REPLY,CLICK,PAY} → 1.0; NO_REPLY → 0.5 (neutral, untested); MISS/SWITCH/COMPLAIN → 0.0 |
| Complaints (handling) | 35% | COMPLAIN → 0.0; everything else → 1.0 |
| Customer commitments (Guaranteed Standards) | 10% | **constant 1.0** |

The CA source table itself labels commitments **"policy, not conversation"** — this triad has no
policy-compliance model, so the 10% is carried as a *named* constant rather than silently dropped or
faked as conversation-movable. The uplift this organ measures is therefore honestly driven entirely
by the 90% (55+35) conversation actually can move.

**Uplift measurement technique — common random numbers, not a mock.** The control message reuses the
treated message's `message_id`, so F1a's named RNG substreams (keyed on `customer_id:message_id`)
draw *identical* random numbers for both arms; only the differing tone/framing lever can move the
outcome. Verified directly: a matched, correctly-trained lever gives a real positive uplift
(+0.028 CA-weighted score over 98 loss-averse customers in one run); a *mismatched non-neutral*
lever gives **exactly 0.0** (not near-zero — bit-exact), because `positive_action_probability` and
`_adverse_share` in the real F1a model are lever-*value*-insensitive except for the one matching
value. This dual result is the non-tautology proof: the uplift measure is demonstrably sensitive in
both directions, not a fabricated always-positive number.

## 4. The MANDATORY R15 intent-leak control

**Mechanism.** With **zero prior observations**, there is no legitimate evidence an honest company
could use to pick a matched, non-neutral lever — the shipped F1b generator's own empty-belief default
is `neutral_framed`/`neutral_toned` (proven, not assumed: `honest_zero_evidence_generate` wires a
*fresh* `ConversationGenerator(SusceptibilityEstimator())` per call). `intent_leak_rate(generate_fn,
customers, situation, product)` calls any `generate_fn` matching that signature at zero evidence and
checks whether the emitted lever already matches the customer's **true** category (read directly from
`simulation.nudge_physics` — the harness is the referee, permitted to read both truth and belief).
Neutral-truth customers are excluded from each axis's denominator (a neutral send to a neutral-truth
customer is not evidence of leaking — it's also the honest default).

**The exit test, run for real (not asserted, executed):**

| variant | framing_leak_rate | `detect_intent_leak` |
|---|---|---|
| `honest_zero_evidence_generate` (fresh generator + fresh estimator) | **0.0** (exact, both situations tested) | **False** |
| `_peeking_generate` (reads `nudge_physics.susceptibility_for` directly, sends the matching lever) | **1.0** (all non-neutral-truth customers) | **True** |

Both arms run over the *identical* population/situation in
`tests/harness/test_conversation_gap.py::test_R15_both_ways_same_population_same_situation`, so the
contrast cannot be a fixture artefact. `detect_intent_leak` fires at any rate above 0.05 — since the
honest baseline is exactly 0.0 by construction, this threshold is slack, not a tuned-quiet alarm
(R12).

## 5. The wall (structural, tested not just asserted)

This organ is one of the few places permitted to hold SIM truth (`simulation.nudge_physics`) and
company belief (`company.comms.susceptibility_estimator`) side by side — the referee's job, exactly
like `background/dd_h_solvency_gap.py` and `tools/couple_cohort.py` (`background/` sits outside the
`company/`+`saas/` scope `tools.epistemic_verifier` scans; confirmed: `python3 -m
tools.epistemic_verifier` → PASS, 528 files, unaffected by this module's addition). What is
structurally forbidden and **tested**, not just documented:

- writes to exactly **one** path, its own ledger (`GAP_LEDGER_PATH`) — never into any `company/`,
  `saas/`, or `simulation/` file (`test_module_writes_only_its_own_ledger_path`, a source-scan
  asserting exactly one `.write_text(` call in the module);
- never mutates a caller-supplied estimator beyond its own reads
  (`test_measurement_functions_never_mutate_a_caller_supplied_estimator_beyond_its_own_reads`);
- never imported by `background/supervisor.py` / the draw — R12 severance, the gap is a DIAGNOSTIC
  (`test_module_never_imported_by_the_supervisor_draw`, mirrors DD-H's own severance test).

## 6. Non-tautology guards beyond the mandatory R15 control

- **Gap sensitivity, both ways:** a confidently-and-correctly-trained belief shows
  `framing_category_match_rate == 1.0`; a belief hand-trained toward the deliberately *wrong* lever
  shows `== 0.0` — proving the comparison genuinely reads two independent sources rather than
  trivially agreeing (`test_gap_matches_when_belief_is_confidently_trained_correctly` /
  `test_gap_catches_a_deliberately_wrong_belief_not_tautological`).
- **Situation/lever classification drift guard:** `_FRAMING_SENSITIVE_SITUATIONS` /
  `_TONE_SENSITIVE_SITUATIONS` are duplicated *by convention* from
  `simulation/conversation_response.py`'s private `_SITUATION_PROFILE` table (never imported, per the
  wall's "don't import private symbols across the seam" spirit); a test cross-checks the harness's
  copy against the real table directly so a future F1a change cannot silently desync this organ's
  training design (`test_situation_sensitivity_map_agrees_with_the_real_f1a_profile_table`).

## 7. C-S2 determinism

Every function is a pure function of its inputs — the synthetic population id scheme is deterministic
string formatting; `respond()` and `observe_response()` are both already pure/idempotent by F1a/F1b's
own design (no wall-clock, no unseeded randomness anywhere in this module). `measure()` called twice
with identical arguments returns a bit-identical dict (`test_measure_is_deterministic`).

## 8. What this FRAME does NOT do / residuals for BUILD

- **No level move.** This is a FRAME artefact; `level_current` stays `0`. Levels are proposals (R16)
  — the orchestrator/director ratifies the map, this file does not.
- **Not wired into `daily_self_note.py` / the digest / the Proof door.** The atom's own map text says
  the gap should land "per digest + Proof door" — that wiring touches files outside this atom's
  `file_scope` and is explicitly deferred to a BUILD-stage sub-step (see §9 requested delta).
- **Not wired into any `run_phase*.py` driver** — §0/§2's honestly-named residual; F1a/F1b exist and
  work, but no live population exercises them yet. That is upstream of this atom (F1a/F1b's own
  scope), not fixed here.
- **F1b's missing exploration policy** (§2) is a genuine residual for a future atom against F1b's own
  `file_scope`, not this one.

## 9. Requested map delta (this FRAME does not self-write the map — orchestrator applies)

- Evidence append: `docs/design/frame/F1c_harness_conversation_gap_FRAME.md`,
  `background/conversation_gap_ledger.py`, `tests/harness/test_conversation_gap.py`.
- Simplifications append (2026-08-03): FRAME + test-first spec delivered against the REAL,
  already-BUILT F1a/F1b modules (correcting a stale premise that F1a was unbuilt — both are L2/harden
  per the live map). 21 closed-loop tests, all passing, all three mandated measurements implemented
  and R15-proven both ways for the mandatory intent-leak control. `level_current` proposed to remain
  `0` (FRAME stage only — no BUILD claimed); `loop_stage` proposed `frame → build` (the design +
  test-first spec are discharged; implementation exists and passes but has not yet been through a
  HARDEN-stage Expert Hour / mutation-audit pass, and is not live-wired into any run driver or the
  digest). Named residuals for the next BUILD/HARDEN touch: (a) wire `retro_gap_line`/`record_gap`
  into `daily_self_note.py` + Proof door per the atom's own "per digest" spec; (b) F1b's missing
  exploration policy (logged against F1b's own file_scope, not this atom's); (c) live-population
  wiring once F1a/F1b are invoked by a `run_phase*.py` driver.
