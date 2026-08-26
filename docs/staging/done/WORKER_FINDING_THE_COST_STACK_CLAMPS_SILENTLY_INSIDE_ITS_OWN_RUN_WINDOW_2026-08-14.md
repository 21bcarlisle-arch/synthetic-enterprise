# [WORKER-FINDING] All 13 policy/network tables end at 2024, the run bills into June 2025, and every reader serves the last known rate without saying so (2026-08-14)

**Severity:** LATENT · **Lane:** W4_the_wall · **Status:** measured and queued, not fixed
— found during the `EP14_adapter_published_cost_stack` DISCOVER continuation
(`docs/design/EP14_PUBLISHED_COST_STACK_DISCOVER_2026-08-14.md` §3). Queued rather than fixed on sight
per SELF_INTERRUPT discipline.

## Why LATENT and not BLOCKING

The test for BLOCKING is "a published figure may be wrong". Clamping to the last known rate for a period
with no tabulated rate is a **modelling choice**, and this finding does not establish that any published
figure is wrong — it does not claim the 2024 rates are the wrong stand-in for 2025, and it fetched no
external source that could say. What it establishes is that **the instrument cannot tell you it is
extrapolating**. That is a fail-open shape (R15: passes on missing) and a real defect, but it is a defect
in the instrument's self-report, not a demonstrated error in a number. Graded on the definition; if a
later pass shows the 2025 rates materially differ, that pass upgrades it.

## The measurement

`observed-with-evidence`, at HEAD 071a60ec7, by executing the shipped functions and reading
`docs/reports/run_output_latest.json`. Nothing monkeypatched.

`simulation/policy_costs.py::YEAR_KEY_BASIS` declares 13 year-keyed tables. **Every one has
`max(key) == 2024`.** The run's last bill period ends **2025-06-07**. Each table's clamp date, derived
from its own declared basis via `year_key_for_basis`:

| basis | tables | clamps from |
|---|---|---|
| `apr_mar` | `_RO_COST_BY_OY_START`, `_CCL_ELECTRICITY_RATE_BY_YEAR`, `_NETWORK_COST_RESI_SME_BY_YEAR`, `_DUOS_IC_BY_YEAR`, `_CM_LEVY_BY_YEAR`, `_FIT_LEVY_BY_YEAR`, `_GAS_CCL_RATE_BY_YEAR`, `_GAS_NETWORK_COST_BY_YEAR`, `_GGL_RATE_GBP_PER_METER_YEAR` | **2025-04-01** |
| `calendar` | `_CFD_LEVY_BY_YEAR`, `_MUTUALIZATION_LEVY_BY_YEAR`, `_ELEC_SC_PENCE_PER_DAY_BY_YEAR`, `_GAS_SC_PENCE_PER_DAY_BY_YEAR` | **2025-01-01** |

Seven readers carry the same sentence — *"Falls back to nearest known year"* — and return
`table[max(table)]` for any out-of-range date. **Nothing distinguishes that return from a tabulated one.**
There is no `is_extrapolated` companion, no flag on the return value, and no marker in the run output.

**Exposure.** The 2025 published stack is **£391,531.72**, **8.09%** of the £4,838,389.48 total
(electricity policy 3,404,188.65 + electricity network 869,332.79 + gas policy 171,108.84 + gas network
393,759.19). All of 2025 is priced on at least one clamped table, since the four calendar-keyed ones clamp
from 1 January. Of 2025's 7,010,275 kWh — each bill's kWh apportioned evenly across its period days, then
bucketed by day — **47.2% falls on or after 1 April 2025**, where the nine Apr-Mar tables clamp too.

## The class, and the sibling that already solved it

This is the fail-open family: an unavailable input served as a plausible value rather than refused.
`company/regulatory/carbon_emissions.py` handles the identical problem and its comment names the family by
name — it declares `GRID_INTENSITY_FIRST_YEAR` / `GRID_INTENSITY_LAST_YEAR` and exposes
`grid_intensity_is_extrapolated(year)` so a caller can tell. The remedy therefore **already exists in this
repo, unwired to this module** — the common shape here is an orphaned control, not an absent one.

It also contradicts the requirement `EP14_adapter_published_cost_stack`'s own `origin_note` states:

> "Fail-LOUD on an unparseable publication (R15: an unavailable input is a failed input, never a zero)."

A parser that fails loud feeding a reader that clamps quietly still produces a confidently-wrong stack;
the failure just moves one module downstream. **Fail-loud is a property of the reader, not only of the
parser.**

## What discharges it

Not an instance fix — R10 forbids closing an absurdity-class defect on one table. The class is "a
year-keyed rate table read outside its own coverage window", and `YEAR_KEY_BASIS` already enumerates the
population, so the closure is available in the same shape as the year-basis control that pinned it:

1. A coverage declaration per table (first/last key) and a reader that reports extrapolation rather than
   hiding it — the `grid_intensity_is_extrapolated` shape, applied to all 13.
2. A census control that fails when a table in `YEAR_KEY_BASIS` has no coverage declaration, so table 14
   cannot be added without one — the same census leg
   `tests/simulation/test_policy_cost_year_basis.py` already runs for the basis field.
3. R15 mutation proof both ways: a reader reverted to silent clamping must go red, and the census must go
   red on an undeclared new table.

Whether extrapolation should *refuse* (raise) or merely *declare* is a live question this finding does not
settle — refusing would fail a run that currently completes, which is a curriculum-visible change and
belongs to whoever draws it, not to the finding.

## Not claimed

That the 2024 rates are wrong for 2025 (no source fetched — this tick had no network). That any published
figure is numerically wrong. That the clamp affects years before 2025: it does not, every other year in
the run window is inside every table's coverage. That the gas tables' values are right — separately open,
recorded in the EP14 record and not re-checked here.
