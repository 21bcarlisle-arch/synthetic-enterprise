# FROM AGENT — Segmentation integration follow-on (director-approved 2026-07-22)

**Type:** work order (director console 2026-07-22 approved reconciliation items 1–4). Authored by the cwd-fix worktree session at reap time; execute on main with verification. Rank: after the live re-ping/reconciler landing (already done, commit `0dad0b7df`).

**Context:** the `worktree-cwd-fix` tenure→adoption work COLLIDED with main's fuller parallel D-SEGMENT build under `W2_2_population_draw` (`SEGMENTATION_GENERATOR_BUILD_PLAN.md`). Main's build is CANONICAL (curriculum-driven, wall-clean, has `company/analytics/cohort_discovery.py` discovery-consumer + `tools/couple_cohort.py`). The worktree's Commit 2 (tenure gating) and Commit 4 (W2_12 atom) are SUPERSEDED — do NOT resurrect them. Only the items below remain.

## 1. Wire W1_6→C13 (director's original "wire the ledger pair")
Main did not wire it; W1_6 still reaches the Proof panel only via the defensive branch.
- `background/coupled_triad.py`: add `"W1_6": "C13"` to `_AUTHORITATIVE_COUPLING`.
- `docs/design/maturity_map.yaml`: `W1_6_physics_price_signal.couples_with: [C13_weather_normalisation]`; `C13.couples_with: [W1_5_premise_demand_shape, W1_6_physics_price_signal]`.
- `tests/design/test_maturity_map_facets.py`: add `frozenset(("W1_6_physics_price_signal","C13_weather_normalisation"))` to `EXPECTED_PAIRS`.
- main's pair_count tests already DERIVE the count (`test_empty_ledger_fails_closed_not_silent`), so wiring auto-tracks — but verify `test_reflects_real_ledger_exactly` and `site/proof/test_coupled_gaps_panel.py` still pass (total stays 10: W1_6 was already counted via the defensive branch). Low priority — a minor weather-price-belief facet; main's cohort coupled-triad is the real coupling depth.

## 2. Per-asset tenure→adoption factors (director CONFIRMED as ASSERTED provisional)
Main's curriculum uses a SINGLE renter multiplier (0.17). The director confirmed PER-ASSET × tenure. Extend `simulation.population_draw`'s `tenure_adoption_gating_strength` curriculum entry to per-asset (keep it curriculum-read, R13, never hardcoded in the fn):

| asset | owner (own_outright/own_mortgage) | private_rent | social_rent | anchor |
|---|---|---|---|---|
| solar_pv | 1.0 | 0.10 | 0.25 | ASSERTED (roof mod + split incentive) |
| ev | 1.0 | 0.55 | 0.55 | ASSERTED (weakest — has_driveway already carries the off-street barrier) |
| heat_pump | 1.0 | 0.14 | 0.35 | DESNZ Spring-2026 (42% renters vs 7% owners "not theirs to make") |

- Extend `low_carbon_adoption_eligibility_multiplier(cohort_tenure, asset)` to take the asset; extend `generate_life_events`'s `adoption_eligibility_multiplier` to per-asset (each of the three gates uses its own asset's factor). Keep default 1.0 byte-identical (the existing `test_default_multiplier_is_byte_identical` must still hold).
- These are R13 ASSERTED director-curriculum — changeable on his word, never tuned to company outcomes.

## 3. Sensitivity-test the factors (director's explicit ask)
Measure adoption + downstream-outcome sensitivity across a plausible range of each per-asset factor (e.g. ±0.1 around each asserted value), reported as a DIAGNOSTIC (R12 — never a target). Output `docs/market_research/tenure_adoption_sensitivity.md`. Purpose: know how load-bearing each asserted magnitude is before it drives the live world.

## 4. Register each factor as a testable hypothesis (director's explicit ask — condition now met)
The discovery-consumer (`cohort_discovery.py`) EXISTS, so the director's condition ("once the company discovery-consumer exists") is satisfied. Register each per-asset × tenure factor as a hypothesis in `docs/market_research/population_fusion_assumptions_register.json` (or its hypothesis surface) with a refutation condition the behavioural discovery loop can test against observed adoption — the ASSERTED magnitude is falsifiable, not fixed.

## 5. Activation (R13 curriculum — director authorized "activate")
Main deliberately deferred wiring a non-1.0 multiplier into the live run (R13 curriculum). The director authorized activation. Sequence it AFTER items 2–4, and VERIFY to the live run (R11): a real run's per-tenure adoption rates must change as designed (renter heat-pump/solar suppressed) and downstream bills/carbon must not break. Batch the level move (W2_2 already L3) / any L3 to the director.

## 6. Auto-integrator BUILD (per `docs/design/INTEGRATION_GRANTS_DESIGN.md`)
Build the auto-integrator + cross-tree registry. **Director's binding R15 condition (§4):** it does NOT go live until mutation-proven in BOTH directions — a red-gate branch must NOT merge, a director-reserved (L3/curriculum) change must NOT merge — plus every auto-merge writes `INTEGRATE_AUTO` provenance to `gate_authorizations.jsonl` so the daily self-note counts it. `tests/background/test_auto_integrator.py` green before the systemd unit is enabled.

— cwd-fix worktree session, 2026-07-22 (reaped after staging this).
