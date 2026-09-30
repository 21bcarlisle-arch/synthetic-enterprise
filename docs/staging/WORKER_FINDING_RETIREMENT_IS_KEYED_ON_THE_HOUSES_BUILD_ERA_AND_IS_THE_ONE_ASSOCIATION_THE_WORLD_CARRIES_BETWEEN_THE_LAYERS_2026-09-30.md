**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none (the path is W2_5_life_event_stream's, which is closed; found by W2_31_people_phase1_the_physical_layer_stands_alone)
**Evidence:** `tests/simulation/test_household_physical_layer.py::test_every_association_the_world_draws_between_the_layers_is_declared`

# Retirement is keyed on the house's build era, and it is the one association the world carries between the layers

**2026-09-30.** Found by a scheduled-tick worker closing W2_31's third exit criterion, "the
correlation structure stated and measured rather than assumed". Until today it was only stated.

## What was measured

Every physical attribute of the drawn `Household` against `income_stress`, at 2025-12-31, over
`draw_population(seed, acquisitions_per_year_lambda=400)`. Prediction filed before the run:
occupancy is independent of income stress (chi2 p > 0.01, V < 0.05). It held.

| physical | seed 11 (n 1954) | seed 23 (n 2040) |
|---|---|---|
| occupancy | chi2 5.6 / 6 dof, p 0.47, V 0.038 | chi2 6.9 / 6, p 0.33, V 0.041 |
| **build_era** | **chi2 73.7 / 10, p 9e-12, V 0.137** | **chi2 81.8 / 10, p 2e-13, V 0.142** |
| **boiler_age** | **chi2 30.5 / 6, p 3e-5, V 0.088** | **chi2 57.2 / 6, p 2e-10, V 0.118** |
| every other field | p > 0.04 | p > 0.1 |

V 0.04 is the null floor at this n. The draw carries exactly one cross-layer path, and nobody had
declared it.

## The path

`life_events._RETIREMENT_PROB_BY_ERA` fires `retirement_starts`, which moves income stress
LOW -> MODERATE. It fires on the dwelling's `build_era`, and the comment says why: "ERA_1945_1964
occupants: born 1945–64". That assumes a house is lived in by people born the decade it was built.
`boiler_age` is drawn from the era, so it rides the same path.

Two things follow:

1. **No source says a house's age predicts its occupants' age.** The published cross-tab that
   would settle it is the EHS age of household reference person by dwelling age. It is not in the
   commons.
2. **The world holds two answers to "is someone here retired".** `dwelling_records.
   composition_cuts_for` draws `pensioner_present` on the physical layer, independently. So a home
   can retire with no pensioner present, or keep a pensioner who never retires.

## What was done, and what was not

- **Done (W2_31):** the path is declared in `LAYER_CORRELATIONS` as `in_the_world=True,
  established=False`. A control now measures every pair and fails either way: an association the
  draw carries with nobody declaring it, or one declared absent that it carries. Five mutations
  were run, including deleting this declaration, and each goes red.
- **Not done:** cutting or re-keying the path. That belongs to the life-events lane, and the
  choice is a fidelity question, not a seam one. The candidate repair is to key retirement on the
  drawn `pensioner_present` rather than on the house. That is one source instead of two, and it
  moves the association off the fabric. When it lands, the control will red on this row's
  `in_the_world=True`, and that red is the prompt to flip the row.

## Resolution

Open. Close it by landing the re-key above, or a sourced EHS cross-tab that justifies keeping the
proxy.
