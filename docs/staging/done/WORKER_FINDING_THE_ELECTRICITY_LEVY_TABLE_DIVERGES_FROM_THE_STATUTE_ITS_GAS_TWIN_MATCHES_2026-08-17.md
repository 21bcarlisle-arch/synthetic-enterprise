# FINDING — the electricity CCL table is £43k away from the statute it cites, while its gas twin — transcribed from the same statutory rows — matches on ten years out of ten

**Severity:** BLOCKING · **Lane:** W4_the_wall · **Disposition:** QUEUED (not fixed on sight)

**Discharged:** `simulation/policy_costs.py`, `docs/domain_artefact_library/regulatory/ccl_main_rates.json`, `tests/simulation/test_policy_cost_values_vs_source.py::test_every_pinned_rate_equals_the_tabulated_constant`, `tests/simulation/test_policy_cost_values_vs_source.py::test_every_in_window_year_of_a_verified_table_has_a_pin`, `tests/simulation/test_policy_cost_values_vs_source.py::test_every_year_keyed_table_is_classified`, `tests/simulation/test_policy_cost_values_vs_source.py::test_mutation_a_drifting_constant_is_caught`, `tests/simulation/test_policy_cost_values_vs_source.py::test_mutation_a_drifting_pin_is_caught` — the nine divergent years now equal the statute, and the CLASS is closed by a values-vs-source control whose pinned figures live in the regulation commons in the statute's OWN unit (GBP/kWh), so the control performs the conversion and the checked value is not derived from the source it checks.

The severity header above states what the finding FOUND, not what it left; the discharge is the release. Disposition QUEUED was correct for the LANE 3 pass that filed it — the repair was taken by a later RUNG-1c BUILD draw, which is what this discharge records.

**Atom:** `EP14_adapter_published_cost_stack` (LANE 3 idle draw, DISCOVER/FRAME, 2026-08-17)
**Class:** a constant CITES a publication and does not EQUAL it, so a citation census scores it green

Full derivation, every number, and the fetched sources:
`docs/design/EP14_PUBLISHED_COST_STACK_SOURCE_CHECK_2026-08-17.md` (§1, §2).

---

## What was found

`simulation/policy_costs.py` carries two Climate Change Levy tables. They are two columns of one table,
in one Act, set by one section, effective on one date each year:

* `_GAS_CCL_RATE_BY_YEAR` — **exact against the published rate on 10 of 10 years**, including the
  clamped 2025.
* `_CCL_ELECTRICITY_RATE_BY_YEAR` — **diverges on 9 of 11 years**, always understating.

The model's electricity table rises smoothly (5.44 → 7.35 £/MWh) and its own comment reads
`# April 2020: step-change — electricity CCL raised as gas CCL frozen`. The statute has the step-change
in **April 2019** (5.83 → 8.47, the Budget-2016 rebalancing) and April 2020 as a **cut** (8.11), then a
taper to 7.75 flat. The comment names the wrong year *and the wrong sign*.

**OY 2018 matches exactly (5.83 = 5.83).** That is the control that makes this an error and not a
modelling choice: it fixes the intended subject as the *main* rate (as the module comment states) and
the unit convention as p/kWh × 10, and one year lands dead on it.

## Exposure

Measured on business electricity volume from the run's own `bills` (resi excluded — domestic electricity
is CCL-exempt and the shipped reader returns 0.0), kWh apportioned evenly across each bill's period days,
bucketed by Apr–Mar obligation year:

| | |
|---|---:|
| model electricity CCL line | £459,799.16 |
| **understatement, using ONLY years whose rate was fetched from the publisher/legislation** | **£43,074.89 (9.4%)** |
| understatement including three recalled years (2016, 2017, 2021) | £49,208.14 (10.7%) |

**Quote £43,074.89, not the larger figure** — 2016, 2017 and 2021 were not fetched and are excluded from
the floor. OY 2019 alone is £18,274.68 (42% of the floor), because 2019 is the year the model missed the
step.

## Why BLOCKING

Finding-severity clause 2, by construction: **a published figure in this area is wrong.** The
electricity CCL line is a component of the published non-commodity cost stack (£4.84M), and per this
atom's own first pass that stack is 99.05% of `total_gap_gbp` on the live front-door Reconciliation
Bridge. £43,074.89 of that published figure is this mis-transcription.

This is the same grading, on the same atom, as
`WORKER_FINDING_THE_DOMINANT_COST_COMPONENT_IS_READ_ON_A_CALENDAR_YEAR_2026-08-13.md` (£62,449.57,
graded BLOCKING on exactly this reasoning, since repaired) — filed the same way for consistency, not
because a second blocker on one lane is desirable.

## Why an instance fix would breach R10

The class is **"a constant cites a publication and does not equal it"**, and a nine-value edit to one
table does not close it. Two reasons the class is live and not hypothetical:

1. **11 of the 13 year-keyed tables have never been source-checked at all.** This pass checked three
   (gas CCL ✅, electricity CCL ✗, GGL ✅). The two largest lines by money — electricity network
   (£869k) and RO (£1.72M) — are untouched.
2. **The existing documentary control cannot catch this.** `tests/simulation/test_policy_cost_year_basis.py`
   verifies each table's *year basis* against its own comment, which is the right subject for the defect
   it was built for. Nothing checks a table's *values* against anything. B5 in the scope brief asks that
   "every constant traces to a published artefact", and pass 3 scored it 12/13 — but it scored
   **whether a comment names a source**, never whether the number equals it. A citation census is
   fail-open on a mis-transcribed constant by construction: it reads the same comment the author wrote,
   so the only defect available to it is a *missing* citation, never a *false* one.

**The class closure is a values-vs-source control**, not a year-basis one — a pinned expectation per
table per year, sourced from the publication and checkable against it, so that a table that drifts from
its cited source fails on sight. That is naturally EP14's own adapter work (an ingest adapter makes this
nearly free), which is why this is queued to the atom rather than patched now.

## What is NOT claimed

* **Not** that the gas tables, GGL, or any other table's values are wrong — gas CCL and GGL were checked
  and both **match**. Nine tables were not checked either way.
* **Not** that the understatement propagates unchanged to margin. The stack is passed through in the
  tariff at pricing time and deducted at settlement, so the net margin effect is partly self-cancelling;
  what is definitely wrong is the published **cost stack component** and the bridge total built on it.
* **Not** a before/after claim against any prior run's figures — those are different refs.
* No BUILD was done and no source file was touched by the pass that filed this (LANE 3, DISCOVER/FRAME).

## Reproduce

```
python3 -c "
import sys; sys.path.insert(0,'.')
from simulation.policy_costs import get_ccl_per_mwh, get_gas_ccl_per_mwh
print('elec 2019:', get_ccl_per_mwh('2019-06-01','I&C'), 'published 8.47  (FA2016 s.147: GBP0.00847/kWh)')
print('elec 2020:', get_ccl_per_mwh('2020-06-01','I&C'), 'published 8.11  (FA2020 s.92:  GBP0.00811/kWh)')
print('gas  2019:', get_gas_ccl_per_mwh('2019-06-01','I&C'), 'published 3.39  (FA2016 s.147: GBP0.00339/kWh)')
print('gas  2020:', get_gas_ccl_per_mwh('2020-06-01','I&C'), 'published 4.06  (FA2020 s.92:  GBP0.00406/kWh)')
"
```

Both statutory rates above come from the same section as the gas rate directly beneath them:
[FA2016 s.147](https://www.legislation.gov.uk/ukpga/2016/24/section/147/data.html),
[FA2020 s.92](https://www.legislation.gov.uk/ukpga/2020/14/section/92/data.html).
