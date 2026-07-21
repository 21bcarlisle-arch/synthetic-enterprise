# Segmentation reconciliation FRAME — one taxonomy, arbitrated by the learning-value knee

**Status:** FRAME (director console 2026-07-21: "Proceed with the reconciliation FRAME — one taxonomy. Fold the tenure×adoption recoupling through the fusion assumptions register … keep the learning-value frontier as the arbiter"). Supersedes the parallel-taxonomy framing in `docs/design/SEGMENTATION_WIRING_PLAN.md` §Step-2. No generator change (that is the convergent director-reserved BUILD).

## 1. One taxonomy — D-SEGMENT folds INTO population-coverage
The D-SEGMENT trait axis (DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20 Part 2) and the POPULATION_COVERAGE track (DIRECTOR_STEER_POPULATION_COVERAGE_DESIGN_2026-07-20) are the **same object**: data-derived combination cohorts across factor axes, worst-cell scored, generator change director-reserved. There is **one** cohort taxonomy — the committed population-coverage schema — not two:
- **The permutation space:** `docs/market_research/population_coverage/cohort_schema.json` — 12 factor axes (tenure, accommodation, cars, nssec, heating_fuel, region, green_stance, price_sensitivity, channel_pref, solar_PV, EV, home_battery), each carrying `observed`/`fused`/`assumed` provenance.
- **The joint-structure gate:** `docs/market_research/population_fusion_assumptions_register.json` — every dimension pair is a testable hypothesis with an explicit refutation condition; conservative crossing by default, fusion only on positive evidence.
- **The coverage design:** `nested_design.json` — 1000 nested worst-cell cohorts.
- **The arbiter:** `learning_value_frontier.json` + `build_learning_frontier.py` — the learning-value knee.

D-SEGMENT does not add a taxonomy; it adds three things to this one (§3).

## 2. The tenure×adoption recoupling — the first refuted assumption (the loop working)
The register's `['green_stance','solar_PV']` entry (and the general "attitudes/adoption are crossed from the structural axes" assumption) carried an explicit refutation condition: *"a source showing [attitude] predicts [tech] after conditioning on income+tenure."* The **DESNZ Public Attitudes Tracker, Spring 2026** (live fetch, `segmentation_joint_structure.md`) **fires it**: 42% of renters say a heat-pump decision "isn't theirs to make" vs 7% of owner-occupiers — a **structural** (dwelling-control), not merely attitudinal, coupling of tenure to low-carbon adoption.

Folded through the register (this pass):
- New `['tenure','low_carbon_adoption']` entry, provenance **observed**, status `REFUTED_ASSUMPTION_RECOUPLED`, with the sourced gap/lift recorded and the exact Cramér's V flagged pending the full cross-tab (R9 — lift recorded, V not fabricated).
- The `['green_stance','solar_PV']` crossing annotated `partially_superseded_by_tenure_recoupling` (the tenure leg is refuted; green_stance's own residual coupling stays crossed pending its own consented residual measurement — the recoupling is tenure-structural, not a green_stance promotion).
- `_meta.refutation_events` records it as the **first refutation to fire on this register** — assumption → refutation-condition → new evidence → reclassification, exactly the mechanism the register was built to run. This is the learning loop working as designed, not a schema patch.

## 3. What D-SEGMENT genuinely adds to the one taxonomy
1. **The recoupling above** — tenure→adoption, now `observed`.
2. **The coupled-triad half.** Population-coverage designs the *true* cohort space. D-SEGMENT adds that the **company discovers cohorts through the wall from observables and is scored on the belief-vs-truth gap** (worst cell), not read from SIM ground truth. That harness half is a company-layer BUILD, coupled to the true schema.
3. **Observable-proxy constraints.** Some axes (green_stance, framing/tone susceptibility, CO₂ salience) have **no** real observable a company could cluster on — bounding which axes can ever be part of a *company-discoverable* cohort, distinct from the true generative cohort.

## 4. The learning-value knee is the arbiter (not schema completeness)
Director 2026-07-21: "every segment earns its place by measured learning value, not schema completeness." Re-derived `build_learning_frontier.py` on the merged schema (deterministic, `PYTHONHASHSEED` 0):
- **The knee is unchanged by the recoupling alone** — dimension-knee at 5 dims, segment-knee at 4070, byte-identical to the committed frontier. This is correct and honest: the frontier ranks dimensions by **outcome-variance reduction**, which a coupling in the *coverage* register does not by itself move. A coupling earns learning value only once it produces *differential outcomes*.
- **Tenure already clears the knee** (#2 by learning value overall, 0.22; **#1 under `net_zero_tilt`**: `[tenure, heating_fuel, price_sensitivity, accommodation]`). So the tenure-gated adoption recoupling earns its place **exactly where it matters** — the carbon/net-zero objective, the mission's unit of account.
- **Binding rule for the merged schema:** a segment/dimension is included iff it clears the re-derived knee. The recoupling does not buy inclusion by existing in the register; its full learning value (the tenure-gated adoption cell's marginal variance-reduction) is **measured at the generator BUILD**, when tenure actually gates adoption in the outcomes, and re-tested against the knee then. Completeness never justifies a segment; measured learning value does.

## 5. The convergent BUILD (director-reserved) — what remains
Both tracks defer to the **generator change**: wire the one cohort schema into the population draw so households carry their joint cohort, tenure gates low-carbon adoption in the outcomes, and the company-discovery harness measures the worst-cell belief-vs-truth gap. This is director-reserved (per both tracks) and needs:
- a **code-read verification** pass (FRAME-lane agent with code permission — the discovery-agent correctly could not cross the SIM wall; verify the trait inventory / RNG-substream identifiers against live source before the generator change);
- the **worst-cell company-scoring** decision (a company-scoring value, not market research);
- any residual `assumed` pair whose recoupling has no external cross-tab → an R13 director-curriculum [ACT], batched.

No generator code changed in this FRAME.
