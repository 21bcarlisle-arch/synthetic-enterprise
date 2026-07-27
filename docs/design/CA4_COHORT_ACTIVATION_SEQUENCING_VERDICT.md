# CA4 — Cohort-activation sequencing verdict (go/no-go before the live flip)

**Atom:** `CA4_cohort_activation_sequencing_verdict` (lane `W2_customer_generator`, front `SIM_ACTORS` open).
**Deliverable:** the director-invited answer to *"activate cohorts now, or counter-propose the sequencing?"* (ruling §3, `DIRECTOR_RULING_COHORT_ASSIGNMENT_ACTIVATED_2026-07-27.md`). A written go/no-go **before** CA1 flips the live seam, so the flip is a decision on record, not a reflex.
**Verdict clock:** 2026-07-27, worker tick. Evidence gathered from disk/git state (R7/R9), not narrative.

---

## VERDICT: **PROCEED** (matches the ruling's own tag `proceed`; no evidenced counter-proposal found)

The director invited disagreement *if* activating now would (a) corrupt a baseline, (b) invalidate a comparison, or (c) collide with in-flight work. I checked each against real state. None holds. Below is the evidence for PROCEED and the honest caveat that scopes what the flip actually does today.

### (a) Baseline corruption — NO

The byte-identical default-off control is the baseline, and it survives untouched:

- `simulation/population_draw.py:251-256` — `assign_cohort()` draws from its **own named substream** keyed on `customer_id`, never from the acquisition `rng`. It cannot perturb the segment/commodity/band/payment/eac draw sequence. Proven both directions by `test_cohort_substream_isolation_does_not_perturb_acquisition_draw` and `test_cohort_draw_default_off_is_byte_identical` (`tests/simulation/test_population_draw.py:376-387, 448-456`).
- `SyntheticCustomer.to_customer_dict()` (`population_draw.py:216-230`) **omits `cohort` by construction**. Flipping `assign_cohorts=True` therefore leaves the saas-shaped OBSERVABLE dict byte-identical to the no-cohort dict — the cohort rides only on the hidden SIM-truth object.

Consequence: no published run figure moves when CA1 flips. The activation attaches ground truth for coverage/manifest legibility without changing a single observable the company or a report reads.

### (b) Comparison invalidation — NO

The one comparison that could break is the default-off regression control, and the ruling §4 explicitly keeps it (`test_cohort_draw_default_off_is_byte_identical` stays as the control for callers that do not opt in). CA1's flip is scoped to the **live seam's own opt-in call** (`simulation/live_population.py`), not the default. Callers that never opt in still get the byte-identical stream. No margin/P&L comparison is anchored to the drawn book today (see caveat), so nothing re-baselines that wasn't already gated by the coverage report.

### (c) Collision with in-flight work — NO

- **`PLANNER_MINTED_generator_draw_wiring` (in_progress)** — the population-EXISTENCE wiring (`SE_DRAW_POPULATION`, whether SYN-* households exist at all). CA1 is the cohort-VARIETY flag *layered on top* of that population; it is additive, not a competing edit. Disjoint concern: existence (that ruling) vs variety (this one). No file-scope conflict — CA1 touches only the `assign_cohorts=` argument inside the already-activated branch.
- **CA2 (`coverage_report_realised_cohort`, committed 84b4614bb)** — already draws with `assign_cohorts=True` independently, so realised-cohort legibility does not depend on CA1 and does not conflict with it.
- **CA3 (untestable ledger)** — records that segmentation stays untestable at the current book; consistent with, not contradicted by, activating pool variety (§2 world-side vs company-side distinction).

### Elicitation wall — HOLDS post-activation (ruling requirement, re-proven under CA1)

The ruling requires the closed-symbol/elicitation scan to be *confirmed still firing after activation*. CA1 strengthens `tests/simulation/test_live_population_seam.py` so the wall test asserts, post-flip, that the underlying `SyntheticCustomer`s **do** carry cohorts while **no** returned dict exposes `cohort` — the wall test now genuinely exercises the activated state instead of the trivial no-cohort case. See CA1.

---

## HONEST CAVEAT — what the flip does today (scopes, does not weaken, PROCEED)

`simulation/live_population.py` sits behind the **still director-reserved, default-OFF** `SE_DRAW_POPULATION` flag, and is **not yet wired into any run entrypoint** (its own module docstring, lines 16-25; population-activation core remains the held/escalated release rung). So CA1's flip is presently **latent**: it makes the live seam draw cohort-tilted households *when population draw is activated*, but no published run consumes that seam yet.

This is consistent with the ruling, not a gap in it: the ruling is a **curriculum act on a mechanism** (§3 "not an instruction about how or when to wire it"). Activating `assign_cohorts` now means the release rung, when the director flips it, yields a genuinely varied pool with zero further code change. The world-side variety is armed; the company-side book stays untestable (CA3). Proceeding now is strictly better than deferring: it removes cohort-variety from the critical path of the held population release, and it costs nothing observable today.

## Sequencing recommendation

1. **CA4 (this doc)** — verdict on record. ✅ PROCEED.
2. **CA1** — flip `assign_cohorts=True` at the live seam; re-prove the wall scan fires post-activation.
3. **CA3** — register the volume-dependent segmentation capabilities as untestable-at-current-book with the named unlock, gated so the class cannot be silently scored "working".

CA2 (coverage legibility) already landed and does not gate this sequence.

*Filed by the worker tick, 2026-07-27. Verdict is a decision record, not authorization to move any level (levels stay `blocked_on: director_level_up`, R16) or to flip `SE_DRAW_POPULATION` (director-reserved release rung, untouched).*
