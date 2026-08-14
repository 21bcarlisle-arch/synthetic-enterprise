# EP14 — The published cost stack: DISCOVER, continued

**Atom:** `EP14_adapter_published_cost_stack` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-14 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-3 BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13);
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0. This is an adapter atom — the adapter is the deliverable, not the document — so the
EP10 precedent applies rather than EP19's. `docs/design/maturity_map.yaml` deliberately NOT edited: nothing
in the map moves, and another lane holds staged hunks in that file (R16 — no map edit from this tick).

**This is a CONTINUATION, not a second FRAME.** EP14 already had a full DISCOVER/FRAME on 2026-08-13,
recorded in `docs/design/simplifications/EP14_adapter_published_cost_stack.yaml` (four findings; finding 1
established that the "~£4.9M reconciliation gap" in this atom's own `name:` **is the cost stack's own
total**, 99.05% of it, and must never be its exit criterion). Repeating that pass would have produced a
second copy of it. This draw takes two of the three threads that pass explicitly named as **not done**:

> "the gas side of the stack (£564,868 combined) was not decomposed; the scope brief's B1 cap-annex
> reconciliation was read but not run against the company's build-up."

The gas decomposition is below. The B1 cap-annex reconciliation is still not run, and §4 says why.

Everything here is `observed-with-evidence` unless labelled otherwise (R9). **MEASURED AT:** HEAD
071a60ec7, live `docs/reports/run_output_latest.json`, with `simulation/policy_costs.py` functions called
directly and nothing monkeypatched.

---

## 1. The stack, decomposed — and the gas side is 11.67% of it

Summed over 2016–2025 from the run's own published per-year components:

| component | £ | share |
|---|---:|---:|
| electricity policy | 3,404,188.65 | 70.36% |
| electricity network | 869,332.79 | 17.97% |
| **gas policy** | **171,108.84** | **3.54%** |
| **gas network** | **393,759.19** | **8.14%** |
| **total** | **4,838,389.48** | |

The prior pass quoted £564,868 combined for gas against a different run; it is £564,868.03 here, unchanged
to the penny. Electricity network reads £869,332.79 against that pass's £876,028.87. **No claim is made
that the difference is the year-key repair landing** — these are two different runs, and a before/after
attribution across two refs is the mixed-join shape that manufactures the defect it counts. One ref would
be needed to say it, and this pass did not produce one.

## 2. Gas policy is £0.00 for three years, and that is CORRECT

| year | gas policy £ | gas network £ |
|---|---:|---:|
| 2016 | 0.00 | 479.08 |
| 2017 | 0.00 | 898.18 |
| 2018 | 0.00 | 904.80 |
| 2019 | 15,154.74 | 50,388.00 |
| 2020 | 19,467.75 | 47,215.03 |
| 2021 | 22,472.01 | 50,461.67 |
| 2022 | 27,046.36 | 54,623.29 |
| 2023 | 32,229.97 | 80,063.31 |
| 2024 | 37,494.84 | 76,774.12 |
| 2025 | 17,243.17 | 31,951.72 |

A zero holding for three years then jumping to £15k reads as a defect. It is not one. Gas policy cost in
this window is gas CCL only (the Green Gas Levy did not exist until 30 Nov 2021), and
`get_gas_ccl_per_mwh` returns `0.0` for `segment == "resi"` because **domestic gas is CCL-exempt in
reality**. The run's gas accounts, by first bill:

    C1g       2016-01-01  resi
    C2g       2016-04-01  resi
    C3g       2016-07-01  resi
    C4g       2016-10-01  resi
    C_IC3g    2019-01-01  I&C     <- the only non-domestic gas account in the run

The single I&C gas account arrives on 1 January 2019, which is exactly where gas policy cost becomes
non-zero. The exemption is modelled, and the £0 is the exemption showing through a portfolio that had no
non-domestic gas before 2019 — **a fidelity point in the stack's favour, recorded because the obvious
reading of that column is the opposite one.** The £564,868 gas total is therefore dominated by network
charges that every segment pays, not by levies.

## 3. FINDING — every one of the 13 year-keyed tables ends at 2024, and all of them clamp SILENTLY inside the run's own window

`simulation/policy_costs.py` declares 13 year-keyed tables via `YEAR_KEY_BASIS`. Every one has
`max(key) == 2024`. The run bills to **2025-06-07**. Derived from each table's own declared basis:

| basis | tables | clamps from |
|---|---|---|
| `apr_mar` | RO, CCL elec, network resi/SME, DUoS IC, CM, FiT, gas CCL, gas network, GGL (9) | **2025-04-01** |
| `calendar` | CfD, mutualization, elec standing charge, gas standing charge (4) | **2025-01-01** |

Out-of-range is not refused. Each reader ends the same way — *"Falls back to nearest known year"*, seven
times over — returning `table[max(table)]` for any later date. **The returned number is indistinguishable
from a published one.** There is no `is_extrapolated` companion, no flag on the return, nothing in the run
output marking the period as extrapolated.

Exposure, measured: the 2025 published stack is **£391,531.72, 8.09%** of the £4,838,389.48 total. All of
it is priced on at least one clamped table (the four calendar-keyed ones clamp from 1 January). Of 2025's
7,010,275 kWh — apportioned evenly across each bill's period days and bucketed by day — **47.2% falls on
or after 1 April**, where the nine Apr-Mar tables clamp as well.

**Why this matters to EP14 specifically, and not just generally.** This atom's own `origin_note` states
the requirement it is being built to meet:

> "Fail-LOUD on an unparseable publication (R15: an unavailable input is a failed input, never a zero)."

The layer EP14's adapters would feed does the exact opposite today: an unavailable period is silently
served the last available one. A parser that fails loud, wired to a reader that clamps quietly, still
produces a confidently-wrong cost stack — the failure just moves one module downstream. **The fail-loud
requirement is a property of the READER, not only of the parser**, and EP14's exit criteria should say so.
The sibling shape already exists in this repo and can be copied rather than invented:
`company/regulatory/carbon_emissions.py` carries `GRID_INTENSITY_FIRST_YEAR` / `GRID_INTENSITY_LAST_YEAR`
and a `grid_intensity_is_extrapolated` companion for precisely this reason, and its comment names the
fail-open family it was written against.

Filed as `docs/staging/WORKER_FINDING_THE_COST_STACK_CLAMPS_SILENTLY_INSIDE_ITS_OWN_RUN_WINDOW_2026-08-14.md`
(LATENT — queued, not fixed, per SELF_INTERRUPT discipline; the grading argument is in the finding).

## 4. What this pass did NOT do, so the next draw is not misled

* **The B1 cap-annex reconciliation is still not run.** It compares the company's own build-up against the
  Ofgem cap annex allowance per period — and per the prior pass's finding 4, *the company has no build-up*:
  `simulation/policy_costs.py` serves both sides of the wall, so the company's forecast error on this stack
  is zero by construction and there is nothing on the company side to reconcile. Running B1 today would
  measure the world against itself. It becomes available when the adapter → `ncc_forecast_register` →
  pricing path exists, which is BUILD and is gated. This is a **sequencing** answer, not a deferral: the
  prior pass listed B1 as owed without noticing its precondition is the atom's own unbuilt half.
* No adapter, parser, schema-drift or cap-annex work of any kind. Nothing in `file_scope` touched.
* The gas tables' **values** were not re-checked against source (the prior pass flagged this too, and it
  remains open). What was checked here is the CCL exemption behaviour and the coverage window, not whether
  £9.9/MWh was the right 2016 GDN+NTS figure.
* No level moved, no map edit, and nothing under `company/`, `saas/`, `sim/` or `simulation/` was changed.
