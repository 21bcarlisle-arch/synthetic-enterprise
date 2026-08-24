# BLOCKED ATOM VISIBILITY — the dial the ruling asked for

**Generated** by `background/blocked_atom_visibility.py` (atom `FUT3_blocked_atom_visibility`). Do not hand-edit: `--check` re-derives and fails on any disagreement.

`DIRECTOR_RULING_FUTURE_COMMITMENT_SETS_2026-08-08` §4: parked atoms are invisible to the draw and visible to the clocks and the deltas. Each line below is measured, not asserted.

## The three properties

| Property | Source | Result |
|---|---|---|
| Invisible to the BUILD draw | `supervisor._maturity_map_draw_concurrent` (the real draw) | 78/78 parked atoms not offered — 54 proven excluded BY THE PARK (lifting the park alone makes them drawable), 24 excluded for another reason |
| Visible to the staleness clocks | `tools/map_assertion_provenance.build_rows` (AO11) | 78/78 parked atoms carry a row |
| Visible to the composition dial | this module, over all 298 atoms | 78 parked (19 with a gate stated in `block_reason`) |

## The dial

At mint (2026-08-08) the ruling measured **82 harness vs 7 commercial across 206 atoms**. Today:

| Lane | All atoms | Excluding parked | Hidden by a park-filtering reader |
|---|---:|---:|---:|
| `H_harness` | 117 | 97 | 20 |
| `D_billing_metering` | 46 | 36 | 10 |
| `W2_customer_generator` | 31 | 28 | 3 |
| `W1_market_weather` | 20 | 12 | 8 |
| `C_customer_ops` | 17 | 13 | 4 |
| `G_data_learning` | 14 | 10 | 4 |
| `W4_the_wall` | 13 | 3 | 10 |
| `F_risk_compliance` | 11 | 6 | 5 |
| `B_commercial` | 9 | 5 | 4 |
| `A_strategy_governance` | 9 | 2 | 7 |
| `E_finance_treasury` | 7 | 5 | 2 |
| `W3_industry_systems` | 3 | 2 | 1 |
| `W5_banking_payment_rails` | 1 | 1 | 0 |

Harness share of the whole map: **39.3%** (117 of 298).
This is a DIAGNOSTIC (R12). `--check` never fails on it.
The same lane counts split by `loop_stage` are on the WIP-flow door (`tools/generate_wip_flow_data.py`); what is here and not there is the with/without-parked comparison and the two probes below it.

## Subject coverage — the ruling's own zero-coverage list

Matched on the atom id, as the ruling measured it; a floor, not a census.

| Subject | Atoms | Of which survive a park-filtering reader |
|---|---:|---:|
| `clv` | 2 | 2 |
| `counterparty_adapter` | 8 | 0 |
| `forecast_feed` | 1 | 0 |
| `tournament` | 1 | 0 |

**This table is the visibility property doing work.** Where the third column is 0 and the second is not, every atom covering that subject is parked — a reader that filtered parked atoms would report exactly the zero the ruling was minted to fix.

## Integrity findings

None. All probes ran and all three properties hold.
