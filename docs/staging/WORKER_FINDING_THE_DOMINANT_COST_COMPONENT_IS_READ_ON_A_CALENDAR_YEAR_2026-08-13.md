# FINDING — the dominant non-commodity component is read on a calendar year against its own table's Apr-Mar keying, and the error is forward-looking

**Severity:** BLOCKING · **Lane:** W4_the_wall · **Disposition:** QUEUED (not fixed on sight)

**Atom:** `EP14_adapter_published_cost_stack` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-13)
**Class:** a lookup table documents one year boundary and its reader uses another, so every
January–March date is charged the following charging year's rate

Full derivation and every number:
`docs/design/simplifications/EP14_adapter_published_cost_stack.yaml` (finding 2).

## The defect

`simulation/policy_costs.py::_NETWORK_COST_RESI_SME_BY_YEAR` states its own key in the comment
directly above it:

> `# Apr-Mar years mapped to calendar year of Q1 (the year the obligation year starts).`
> `2021: 49.0,   # 2021/22: £49.42/MWh`
> `2022: 66.0,   # 2022/23: £66.24/MWh — BSUoS moved 100% to demand side Apr 2022`

Key `2022` is the charging year running Apr-2022..Mar-2023. Its reader does not use the
Apr-start helper that all four of its siblings use:

| function | key derived by |
|---|---|
| `get_ro_cost_per_mwh` | `_ro_oy_start_year(date_str)` (Apr–Mar) |
| `get_ccl_per_mwh` | `_ro_oy_start_year(date_str)` (Apr–Mar) |
| `get_cm_levy_per_mwh` | `_ro_oy_start_year(date_str)` (Apr–Mar) |
| `get_fit_levy_per_mwh` | `_ro_oy_start_year(date_str)` (Apr–Mar) |
| **`get_electricity_network_cost_per_mwh`** | **`int(date_str[:4])` — calendar** |

`_DUOS_IC_BY_YEAR` is read by the same function and carries the same error.

## Observed, with evidence

Measured 2026-08-13 at HEAD `f232c3480`, shipped functions called directly, nothing
monkeypatched:

```
get_electricity_network_cost_per_mwh("2021-12-01") -> 49.0
get_electricity_network_cost_per_mwh("2022-01-05") -> 66.0
```

A £17/MWh step landing on 1 January for a change the table's own comment attributes to April.

Quantified against the live run (`docs/reports/run_output_latest.json`), Q1 electricity kWh
summed from `per_customer_monthly` with gas accounts (id suffix `g`) excluded; error =
Q1_MWh × (table[Y] − table[Y−1]):

| year | Q1 elec MWh | calendar key | Apr-start key | delta | Q1 error £ | year network £ |
|---|---|---|---|---|---|---|
| 2016 | 11.8 | 43.0 | 43.0 | 0.0 | 0.00 | 2,899.57 |
| 2017 | 519.1 | 44.0 | 43.0 | +1.0 | 519.13 | 25,686.85 |
| 2018 | 765.1 | 42.0 | 44.0 | −2.0 | −1,530.12 | 38,090.77 |
| 2019 | 1,766.8 | 45.0 | 42.0 | +3.0 | 5,300.47 | 87,884.24 |
| 2020 | 2,524.0 | 46.0 | 45.0 | +1.0 | 2,524.03 | 124,165.80 |
| 2021 | 2,462.4 | 49.0 | 46.0 | +3.0 | 7,387.35 | 122,274.54 |
| 2022 | 2,424.4 | 66.0 | 49.0 | +17.0 | **41,214.65** | 132,835.36 |
| 2023 | 2,433.5 | 75.0 | 66.0 | +9.0 | 21,901.12 | 138,631.02 |
| 2024 | 2,477.8 | 69.0 | 75.0 | −6.0 | −14,867.08 | 142,680.11 |
| 2025 | 2,416.7 | 69.0 | 69.0 | 0.0 | 0.00 | 60,880.62 |
| **TOTAL** | | | | | **62,449.57** | **876,028.87** |

7.13% of the run's whole electricity network-charge line; 31.0% of 2022's alone. It is
**bidirectional** — 2018 and 2024 are *understated* — so this is a mis-keying, not a one-way
inflation. Stated because "it always overstates" would have been the convenient finding.

## Why BLOCKING

`finding_severity` clause 2, by construction: a published figure in this area is wrong.

The live published `site/data/margin_bridge.json` (front door, Reconciliation Bridge card)
carries `total_gap_gbp = 4,892,209.16`, of which the item
`noncommodity_cost_no_revenue_recognition = 4,845,911.07` is — verified against the run's own
component totals, delta £825.51 (0.017%) — the whole absorbed policy + network cost. The
£62,449.57 above sits inside that published number.

## Why it is worse than an accounting error

Jan–Mar 2022 is charged the post-BSUoS-reform rate that the table's own comment dates to
April 2022. Three winter months of the crisis are settled against a charge that had not
commenced. That is a Point-in-Time Blindfold breach **inside the world layer** — the same
class as the hedge-volatility lookback leak, not a rounding choice.

## Disposition

QUEUED, not fixed. `SELF_INTERRUPT_DISCIPLINE` queues a worker's own finding by default; the
repair is a baseline-world fidelity change (R13 — legitimate, and to be decided blind to
company P&L, which the bidirectional sign here makes easy to honour), and a fidelity change
is BUILD, which a LANE 3 DISCOVER/FRAME draw does not carry. `EP14` itself is epoch-3
BUILD-gated, so this does not wait on `EP14` opening — it is a `simulation/policy_costs.py`
repair that any BUILD draw can take.

**Recommended repair, and I am recommending rather than asking (NEVER_ASK_WITHOUT_RECOMMENDING):**
switch `get_electricity_network_cost_per_mwh` to `_ro_oy_start_year(date_str)`, matching its
four siblings and its own table comment, and add the R15 falsifier the class needs — a test
asserting that **every** year-keyed reader in `policy_costs.py` derives its key by the same
helper, so a fifth table added later cannot reintroduce this silently (R10: the class fails
automatically, not the instance). Expect the published `total_gap_gbp` to fall by ~£62.4k on
the next run; that movement is the repair landing, not a regression, and per finding 1 of the
atom record `total_gap_gbp` is the cost stack's own total and is not a fidelity score.

## Not claimed

That the table's *values* are right — they are calibrated from Ofgem Annex 9 and were not
re-derived here. That the gas-side tables (`gas_policy_cost_gbp` £171,108.84,
`gas_network_cost_gbp` £393,759.19) are free of the same class; they were not examined.
