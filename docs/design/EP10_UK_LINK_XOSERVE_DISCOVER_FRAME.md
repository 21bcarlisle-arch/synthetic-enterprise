# EP10 — Gas, through UK Link: DISCOVER + FRAME

**Atom:** `EP10_adapter_uk_link_xoserve` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-13 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-gated (`block_reason`: director-reserved curriculum sequencing, R13), and EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0. DISCOVER/FRAME does not move a level, and `docs/design/maturity_map.yaml` carries
another lane's staged `level_current` hunk in the shared index (R16 — no map edit from this tick).

---

## 0. What the atom says it is, and what it turns out to be

The atom is filed as an **adapter** — "Adapter for the Xoserve/CDSP UK Link suite under the UNC. Access
class GATED via the Data Services Contract / UK Link User Agreement". Its `origin_note` then says the
thing actually worth building is **UIG**: "an unallocated-gas residue per LDZ per gas day is a cost the
company must absorb without ever being told whose it was, which is a genuine belief-vs-truth gap rather
than a plumbing detail."

Those two sentences point at different work, and **the second one is not gated by anything Xoserve
controls.** The Data Services Contract gates the *transport* — an authenticated API returning a number.
It does not gate the *physics*: a residue that exists, is charged to the shipper, and carries no
attribution. The world can generate that residue and the company can be told only its own monthly share
without a single line of UK Link client code. The access class is a reason this atom cannot reach L3 as
an *integration*; it is not a reason its coupled-triad gap cannot be built and measured.

What actually holds EP10 is the epoch-3 curriculum sequencing in its own `block_reason` — the director's
call, unchanged by this pass. This document does not ask for it to move. It records what a builder will
find on the day it does.

---

## 1. DISCOVER — the company half is already built, and nothing calls any of it

`grep` for UIG/Xoserve/UK Link/LDZ concepts across the tree finds a substantial gas industry-systems
layer in `company/`. Strict import check (a file that actually `import`s the module, excluding `tests/`):

| module | lines | non-test importers |
|---|---|---|
| `company/market/uig_allocation_register.py` | 132 | **none** |
| `company/market/gas_network_ledger.py` | 130 | **none** |
| `company/market/shipper_code_register.py` | 143 | **none** |
| `company/market/gas_nomination_register.py` | — | **none** |
| `company/market/gas_nominations.py` | — | **none** |
| `company/market/gas_imbalance_ledger.py` | — | **none** |
| `company/market/gas_interruption.py` | — | **none** |
| `company/market/gas_otc_book.py` | — | **none** |
| `company/market/gas_storage.py` | — | **none** |
| `company/crm/supply_point_register.py` | 98 | **none** |
| `company/billing/meter_points.py` | — | **none** |

**Eleven modules, 1,393 lines, zero non-test importers.** Every one is reachable only from its own test
file. `uig_allocation_register` alone carries 35 named tests across two files
(`test_uig_allocation_register.py` 10, `test_phase_gn_uig_allocation.py` 25) and has never been
constructed by production code.

This is the *remedy-exists-unwired* shape, not the greenfield the atom's `name:` describes. A builder
who reads the atom title and starts writing an adapter will write the twelfth module in a stack of
eleven that nothing calls. **The first EP10 BUILD move is a wiring decision, not a new-module decision.**

## 2. DISCOVER — the built UIG register cannot produce the gap the atom is worth

The `origin_note` specifies the residue as **"per LDZ per gas day"**. What was built is neither:

* **Granularity is the calendar month.** `UIGMonthlyRecord.settlement_month` is coerced to day 1 of the
  month by `record_allocation`. There is no gas-day dimension. (This is faithful to the *Xoserve
  allocation statement*, which is monthly — but the residue the origin_note wants the company to be
  unable to attribute arises daily, and a monthly scalar has already destroyed the attribution question
  before the company sees it.)
* **There is no LDZ field.** `UIGMonthlyRecord` has `record_id / settlement_month /
  total_throughput_mwh / uig_allocated_mwh / xoserve_ref / notes`. The zone vocabulary exists elsewhere
  in the same package — `gas_network_ledger.GasTransporterZone` enumerates the eight GDN zones, and
  `shipper_code_register.LDZ` is a separate enum with per-LDZ authorisations — and the UIG register
  references `gas_network_ledger` **only in its docstring**, never in an import. Three modules, three
  unconnected spellings of the same geography.
* **The number is a caller-supplied argument.** The signature is
  `record_allocation(settlement_month, total_throughput_mwh, uig_allocated_mwh, ...)`. The register does
  not derive the residue, observe it, or reconcile it — it stores whatever it is handed and computes
  percentages off it. Whoever calls it decides the truth. Nobody calls it.

## 3. DISCOVER — the world has no gas residue to be wrong about

This is the binding finding, and it is a **wall** finding rather than a gas finding.

`grep -i uig` over `simulation/` and `sim/` returns **nothing**. `simulation/gas_settlement.py` settles
gas per gas day and per customer, and its record carries `gas_ccl_gbp`, `gas_policy_cost_gbp`,
`gas_network_cost_gbp`, `gas_standing_charge_gbp` — **no unallocated-gas term of any kind**. There is no
zone or LDZ concept anywhere in `simulation/` or `sim/` (the only "Zone" hits are TNUoS Triad zone 14 in
`simulation/triad.py`, an electricity concept). `company/interfaces/sim_interface.py` exposes gas as a
`fuel` string for price lookups and nothing else.

So the truth side of EP10's advertised belief-vs-truth gap **does not exist**. Total gas entering the
system equals total gas metered to customers by construction, because the world only ever computes the
second one. If the company's UIG register were wired up today, the only number available to put in it
would be one the company itself invented — which is the *world's-X-is-the-company's-estimate* class this
project has filed before. **A coupled-triad gap is structurally impossible here until the world produces
a residue the company cannot see the composition of.**

That is what makes this atom worth its level target, and it is also why the COUPLED TRIAD rule bites:
EP10 cannot reach L3 on an adapter alone, because "no world/SIM atom reaches L3 until the company has
been tested against it and the gap measured" and there is nothing yet to measure.

## 4. DISCOVER — two smaller gaps, both already named elsewhere

* **The gas day has no start hour.** `tools/build_battery_register.py` GAS-7 already records this
  verbatim: *"No gas-day start hour exists anywhere in the tree — `company/market/gas_nomination_register.py`
  carries a bare `gas_day: date` with no 05:00 boundary. The check is trivial ONCE the constant exists;
  asserting it now would assert nothing."* Any per-gas-day UIG lands on a `date` that does not know a gas
  day runs 05:00→05:00. The check is parked and waiting on the constant, not on this atom.
* **Meter read classes 1–4 do not exist.** The atom's second verified fidelity nugget ("meter read
  classes 1-4 with cadences from daily to annual") has **no implementation anywhere** — `grep` for
  `read_class` / `ReadClass` across `company/`, `simulation/`, `sim/` returns nothing. Read cadence is
  the mechanism that *creates* unallocated gas in reality (annual-read supply points are estimated
  between reads; the estimation error is a large part of the residue), so this is not a separable
  decoration — it is the causal story behind §3.

## 5. FRAME — the smallest closed loop, and what it does not need

**The smallest closed loop that carries EP10's stated gain, needs no gated API access, and does not
depend on EP6:**

1. **World side.** Give `simulation/gas_settlement.py` a zone dimension and an unallocated residue: per
   LDZ per gas day, LDZ input minus the sum of metered offtakes the world knows it delivered. The world
   knows both halves; today it only computes the second.
2. **Wall side.** The company may read exactly one thing: its **monthly allocated share** — a scalar per
   settlement month, proportional to its throughput, exactly the shape `record_allocation` already
   accepts. It may never read the per-day, per-LDZ decomposition. That asymmetry *is* the wall, and it
   is the same asymmetry the real DSC creates.
3. **Company side.** Wire the existing `UIGAllocationRegister` to that observable — the module, its
   `is_high_uig` ≥2% flag, its rolling 3-month rate and its 35 tests already exist. Then let the company
   do what a real supplier does: attribute the residue back to its own supply points to price it.
4. **Harness side.** The gap is the score: what the company attributed vs what the world actually
   generated, per LDZ per month. The company is *allowed to be wrong* — with monthly scalars and no
   per-day decomposition it must be wrong — and how wrong, and whether it gets less wrong as read
   cadence improves, is the measurement.

**What this loop does not need:** a Data Services Contract, a UK Link User Agreement, a Supply Point
Enquiry client, or any authenticated Xoserve surface. It needs no EP6 typed wall protocol either — one
scalar per month crosses the existing `sim_interface` seam. The gated API work (Supply Point Switching,
Supply Point Enquiry, Meter Asset Enquiry via RECCo, Supply Point Quantities) is the *L3 integration*
half of this atom and belongs behind EP19's qualification paths; it is genuinely blocked, and it is not
where the fidelity is.

**Sequencing consequence.** If EP10 is ever pulled forward, the order is: read classes (§4) → world
residue (§5.1) → wall observable (§5.2) → wire the existing register (§5.3). Steps 1–3 are worth more
than the adapter and are cheaper than it. The adapter is the last step, not the first.

**Schema-drift tolerance** (the origin_note's other requirement, from Project Trident being mid-flight)
applies only to step 4's gated surfaces. It is a real requirement and it is not exercised by steps 1–3,
so it should not be designed for until there is a client to drift.

---

## 6. What this pass changed

* This document.
* `docs/design/simplifications/EP10_adapter_uk_link_xoserve.yaml` — the atom's own two `evidence`
  pointers repaired (both named `docs/staging/…` paths that no longer exist; see below), plus these
  findings recorded.
* Two findings staged, neither fixed:
  * `WORKER_FINDING_THE_GAS_INDUSTRY_SYSTEMS_LAYER_IS_ELEVEN_MODULES_AND_NO_CALLERS_2026-08-13.md`
    (LATENT · `W4_the_wall`) — §1–§3 above.
  * `WORKER_FINDING_EIGHTY_ATOMS_CITE_EVIDENCE_AT_A_PATH_THAT_MOVED_2026-08-13.md`
    (LATENT · `H_harness`) — the class behind EP10's own broken evidence pointers.

Nothing under `company/`, `simulation/`, `sim/` or `saas/` was touched. No level moved.
