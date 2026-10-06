**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-triad-gate-s-three-excluded-atoms-get-their-company-twins`

# Nine more world atoms aim at L3 with no company twin registered

## What was measured

After W2_30 was coupled to D48 and W2_31 and W2_34 were lowered to target 2, the coupled-triad
gate (`background/coupled_triad.world_l3_blocked`) was run over the whole live map on origin. Nine
more rows return "targets L3 but has no coupled company twin registered", which is the PB4 shape
and the shape the three just fixed were in:

| Atom | Level | Stage |
|---|---|---|
| `W1_7_renewable_capacity_trends` | 2->3 | build |
| `W1_10_ev_heatpump_geography` | 2->3 | harden |
| `SPINE_1_scenario_world_state` | 2->3 | build |
| `W2_payment_channel_dd_consistency_invariant` | 2->3 | harden |
| `W2_sme_segment_case_normalisation` | 2->3 | harden |
| `PB3_book_growth_as_earned_outcome` | 2->3 | build |
| `W1_14_weather_cells_for_household_heat_load` | 2->3 | build |
| `W2_28_a_household_is_a_vector_and_a_claim_declares_what_it_reduces_over` | 2->3 | build |
| `W1_28_the_weather_partition_is_joint_over_a_stock_with_varying_fabric` | 2->3 | harden |

Every row in `build` is excluded from every BUILD draw on every supervisor cycle. Rows in `harden`
are only refused the step to L3.

## Why it matters

PB4 lost 2,275 draws to this exact defect before anyone noticed. W2_28 is the demand-vector claim
contract, and W1_14 is the household heat-load weather cells. Both sit under the first focus item.

## What is not established

For each row, whether any company capability is actually graded against it through observables.
Do not pair rows on a name match. The test is whether a company grade reads the mechanism's output.
D48 reads W2_30 that way. C34 does not read W2_34.

## Recommendation

Do one row at a time, the same way as the three: register a real twin in `_AUTHORITATIVE_COUPLING`
and on both rows' `couples_with`, or lower the target to 2 with the reason in the row's
simplification record. Once none remain, widen
`tests/test_coupled_triad_gate.py::test_the_three_rows_*` to the property, so that no live world
atom stepping to L3 is ever refused for a missing twin. It would red every lane today, which is
why it was not landed now.
