# [WORKER-FINDING] The gas industry-systems layer is eleven modules and no callers, and the world it is supposed to be wrong about produces nothing to be wrong about (2026-08-13)

**Severity:** LATENT · **Lane:** W4_the_wall · **Status:** measured and reported, not fixed — EP10 is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13) and this tick drew LANE 3
DISCOVER/FRAME only, so no BUILD code was written. Full analysis:
`docs/design/EP10_UK_LINK_XOSERVE_DISCOVER_FRAME.md`.

Nothing published rests on these modules — that is the point of the finding, and it is why this is
LATENT rather than BLOCKING. No control's verdict and no board figure reads any of them.

## The measurement

`observed-with-evidence`, at HEAD, by strict import check — a file that actually `import`s the module,
excluding `tests/`:

| module | non-test importers |
|---|---|
| `company/market/uig_allocation_register.py` | none |
| `company/market/gas_network_ledger.py` | none |
| `company/market/shipper_code_register.py` | none |
| `company/market/gas_nomination_register.py` | none |
| `company/market/gas_nominations.py` | none |
| `company/market/gas_imbalance_ledger.py` | none |
| `company/market/gas_interruption.py` | none |
| `company/market/gas_otc_book.py` | none |
| `company/market/gas_storage.py` | none |
| `company/crm/supply_point_register.py` | none |
| `company/billing/meter_points.py` | none |

**Eleven modules, 1,393 lines, zero non-test importers.** Each is reachable only from its own test file.
`uig_allocation_register` carries 35 named tests across `tests/company/market/test_uig_allocation_register.py`
(10) and `tests/company/market/test_phase_gn_uig_allocation.py` (25), and has never been constructed by
production code.

## The part that is not just "unwired"

Wiring is cheap. What is not cheap is that **the world half does not exist**, so wiring these modules up
today would produce a number the company invented about itself:

* `grep -i uig` over `simulation/` and `sim/` returns **nothing**.
* `simulation/gas_settlement.py` settles per gas day and carries `gas_ccl_gbp` / `gas_policy_cost_gbp` /
  `gas_network_cost_gbp` / `gas_standing_charge_gbp` — **no unallocated-gas term**. Total gas in equals
  total gas metered by construction, because only the second is computed.
* There is no zone or LDZ concept anywhere in `simulation/` or `sim/`. The only `Zone` hits are TNUoS
  Triad zone 14 in `simulation/triad.py`, an electricity concept.
* `UIGAllocationRegister.record_allocation(settlement_month, total_throughput_mwh, uig_allocated_mwh, …)`
  takes the residue **as an argument**. It stores what it is handed and computes percentages off it.

That is the *world's-X-is-the-company's-estimate* class, already filed against this project in other
lanes. Until the world generates a residue whose composition the company cannot see, EP10's advertised
belief-vs-truth gap is structurally impossible — and the COUPLED TRIAD rule ("no world/SIM atom reaches
L3 until the company has been tested against it and the gap measured") means EP10 cannot reach its L3
target on an adapter alone.

## Three fidelity mismatches inside the built register

Against EP10's own `origin_note` spec — "an unallocated-gas residue **per LDZ per gas day**":

1. **Granularity is the calendar month.** `record_allocation` coerces `settlement_month` to day 1. No
   gas-day dimension exists. (Faithful to the monthly Xoserve *allocation statement*; but a monthly
   scalar has already destroyed the attribution question before the company sees it.)
2. **No LDZ field.** `UIGMonthlyRecord` is `record_id / settlement_month / total_throughput_mwh /
   uig_allocated_mwh / xoserve_ref / notes`. Two unconnected zone vocabularies exist elsewhere in the
   same package — `gas_network_ledger.GasTransporterZone` (8 GDN zones) and `shipper_code_register.LDZ` —
   and the UIG register references `gas_network_ledger` **only in its docstring**, never in an import.
3. **Meter read classes 1–4 do not exist** — `read_class` / `ReadClass` returns nothing across
   `company/`, `simulation/`, `sim/`. Read cadence is what *creates* unallocated gas in reality
   (annual-read supply points are estimated between reads), so this is the causal story behind the
   missing residue, not a decoration.

Related and already parked, not re-filed here: `tools/build_battery_register.py` GAS-7 records that no
gas-day 05:00 boundary exists anywhere in the tree, so any per-gas-day UIG would land on a bare `date`.

## What would discharge this

Not a Xoserve adapter. The residue is physics; the Data Services Contract gates only the transport.
The smallest closed loop — world residue per LDZ per gas day → company reads only its monthly allocated
scalar → wire the existing register → measure the attribution gap — needs no gated API access and no EP6
typed wall protocol. It is set out in full in §5 of
`docs/design/EP10_UK_LINK_XOSERVE_DISCOVER_FRAME.md`.

**Discharged:** no.
