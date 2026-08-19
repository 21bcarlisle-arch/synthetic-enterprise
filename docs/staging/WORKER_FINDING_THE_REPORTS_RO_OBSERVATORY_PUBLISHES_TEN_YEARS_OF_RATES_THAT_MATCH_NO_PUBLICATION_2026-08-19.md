# WORKER FINDING — the report's RO observatory publishes ten years of obligation levels and buy-out prices that match no publication, and lands 26.5% below the RO cost the company actually pays

**Severity:** BLOCKING · **Lane:** W4_the_wall
**found:** 2026-08-19, source-checking the largest line in the non-commodity stack for
`EP14_adapter_published_cost_stack` (`docs/design/EP14_PUBLISHED_COST_STACK_RO_SOURCE_CHECK_2026-08-19.md` §2).
Queued rather than fixed on sight per SELF_INTERRUPT discipline.

## Why BLOCKING

The test for BLOCKING is that a control or instrument is untrustworthy, or **a published figure may be
wrong**. A published figure IS wrong, and it is committed: `docs/reports/ANNUAL_REPORT.md` lines
2064–2077 at HEAD `a275425f1` render a table headed "Renewable Obligation (RO) Cost Observatory" whose
"Obligation Level" and "Buy-out Price" columns are presented as the published regulatory values and are
not. Ten rows, both columns, every year. The section's own closing caveat — *"Buy-out price is the
regulatory ceiling"* — is the inverse of the truth: the total it publishes sits **26.5% below** the RO
cost the same run charges the company.

## The measurement

`observed-with-evidence` at HEAD `a275425f1`, reading the shipped constants from
`company/regulatory/roc_ledger.py`, the live `docs/reports/run_output_latest.json`, and the committed
`docs/reports/ANNUAL_REPORT.md`. Nothing monkeypatched. Publications fetched this pass — full URL list in
the design doc's "Sources fetched this pass".

| OY | report level | published | report buy-out | published | report cost | on published constants |
|---|---:|---:|---:|---:|---:|---:|
| 2016 | 0.317 | 0.348 | £43.30 | £44.77 | £925 | £1,050 |
| 2017 | 0.334 | 0.409 | £44.77 | £45.58 | £30,968 | £38,608 |
| 2018 | 0.342 | 0.468 | £46.43 | £47.22 | £48,828 | £67,954 |
| 2019 | 0.351 | 0.484 | £47.22 | £48.78 | £117,296 | £167,085 |
| 2020 | 0.358 | 0.471 | £48.78 | £50.05 | £176,424 | £238,154 |
| 2021 | 0.364 | 0.492 | £50.80 | £50.80 | £184,468 | £249,336 |
| 2022 | 0.370 | 0.491 | £52.88 | £52.88 | £194,408 | £257,984 |
| 2023 | 0.376 | 0.469 | £54.35 | £59.01 | £203,369 | £275,420 |
| 2024 | 0.382 | 0.491 | £56.19 | £64.73 | £214,249 | £317,236 |
| 2025 | 0.389 | 0.493 | £58.10 | £67.06 | £96,296 | £140,861 |
| **total** | | | | | **£1,267,231** | **£1,753,689** |

**Understatement £486,458.88 — 27.74%.** Substituting one column at a time on the report's own volumes:
obligation levels carry **£390,791 (80.3%)**, buy-out prices **£74,741 (15.4%)**, interaction the rest.
This is a constants-only counterfactual: the volume series and the year-keying are held fixed and only
the two constant tables move, so the delta is attributable to the constants and does not absorb the
keying question below.

Producer chain, all shipped and all committed: `company/regulatory/roc_ledger.py`
(`_ROC_OBLIGATION_LEVEL`, `_ROC_BUY_OUT_PRICE_GBP`) → `company/regulatory/statutory_obligations.py::_roc_summary`
→ `simulation/run_phase2b.py:2726` (`"roc_summary"`) → `saas/reporting/annual_report.py::_section_roc_obligations`
→ `docs/reports/ANNUAL_REPORT.md`.

## Why this is an error and not a permitted company belief

The epistemic wall lets the company be wrong about things a real supplier could not observe. It does not
let the company substitute the regulatory TEXT: the regulation-commons doctrine holds the published law
readable by every lane precisely because law is published in reality, and a supplier that got the buy-out
price wrong would be getting a number off a public Ofgem page wrong. `roc_ledger.py`'s own docstring
claims these ARE the published figures — *"Buy-out prices are published annually. Obligation levels are
published"* — and names one: *"Buy-out price: set annually by Ofgem (e.g. £54.35/ROC for 2023-24)"*. The
2023-24 buy-out price is **£59.01**. A citation is not an agreement.

## The corroboration, and the null control

The world's own settled RO line (`ro_levy_gbp` summed over `years`) is **£1,724,548.80**. Recomputing the
observatory on the published constants gives **£1,753,688.88 — 1.7% away**, the residue being
calendar-year vs Apr–Mar bucketing. As shipped it is **£1,267,231, 26.5% below**. Change only the
constants and the two organs agree to within the keying noise; leave them and they disagree by a quarter.
The mover is the constants, not the volumes.

The world-side table `simulation/policy_costs._RO_COST_BY_OY_START` was source-checked in the same pass
and is **exact on all twenty inputs**, ten obligation levels and ten buy-out prices, residual pure
rounding (worst case 0.23%). So the run holds the right rates and publishes the wrong ones.

## The shape is the tell

`_ROC_OBLIGATION_LEVEL` rises by +0.006 to +0.007 every year without exception (0.317 → 0.389). The
published series is not monotonic: it plateaus around 0.484/0.471/0.492/0.491, **falls to 0.469** in
2023/24, then returns to 0.491. A ramp cannot produce a dip. `_ROC_BUY_OUT_PRICE_GBP`'s last three years
each add ~3.4% while the real prices went 52.88 → 59.01 (+11.6%) → 64.73 (+9.7%) → 67.06. **Invented
smooth physics where the publication has a plateau, a dip and a spike** — the same class as the CCL
divergence repaired on 2026-08-17, whose old table "invented a gentle monotonic climb where the statute
has a SPIKE AND A TAPER".

## Why no existing control could catch it, which is the class

Two R10 class controls already govern exactly this defect family, and **both enumerate one module**:

* `tests/simulation/test_policy_cost_year_basis.py` discovers tables with `vars(policy_costs)`.
* `tests/simulation/test_policy_cost_values_vs_source.py` classifies every table **in `YEAR_KEY_BASIS`**
  as pinned or unverified-with-a-reason, and ratchets.

`_ROC_OBLIGATION_LEVEL` and `_ROC_BUY_OUT_PRICE_GBP` are year-keyed rate tables of exactly the governed
shape, in `company/regulatory/`. Neither control can name them — not by omission, by construction. So the
values register says of `_RO_COST_BY_OY_START` *"£1.72M, the largest line"* and **that table is right**,
while the table that is wrong by £486k is not in the register and cannot be added by mutating either
control. A register of unverified constants inherits the blindness of its own enumerator.

Second-order, stated but deliberately NOT added to the £486k: `_annual_elec_mwh` buckets by
`settlement_date[:4]` and `_roc_summary` looks both constants up on that calendar integer, while the RO
obligation year runs 1 April – 31 March. That is the identical defect repaired in
`policy_costs.get_electricity_network_cost_per_mwh` on 2026-08-13 and made a class by `YEAR_KEY_BASIS` —
**the class fix did not travel, because the class was scoped as "tables in this module" rather than
"year-keyed rate tables".**

## What the repair is, and what it is not (R10)

**NOT** twenty corrected literals. The instance edit leaves the class exactly as open as it is today and
repeats the 2026-08-13 mistake in the other direction.

1. **A repo-wide census of year-keyed rate tables**, discovered by AST walk over `simulation/`,
   `company/` and `saas/` — not `vars()` of one module — each classified verified-against-the-commons or
   unverified-with-a-reason, ratcheted downward. This is the enumerator both existing controls should
   have had. Note the shape warning: a repo-wide census is not decomposable by pathspec.
2. **The RO figures pinned in the commons in the publisher's own units** — obligation level in ROCs/MWh
   and buy-out price in £/ROC as two separate pinned series, never the £/MWh product, so the control
   performs the multiplication and the derivation is itself under test. Same reasoning that put
   `ccl_main_rates.json` in GBP/kWh rather than GBP/MWh.
3. **One source, two readers.** `_RO_COST_BY_OY_START` and `roc_ledger`'s pair are the same two published
   series duplicated with different values; the durable fix is that both load from the pinned commons.
   Note this narrows a wall gap rather than opening one — the published *law* is commons by doctrine;
   each lane keeps its own *reading* of it.
4. **Provenance carried per year**, `primary` / `secondary` / `recalled`, with `secondary` asserted and
   `recalled` excluded-and-ratcheted. Two of the twenty inputs here (2021/22 and 2022/23 obligation
   levels) are `secondary` — quoted inside another year's notice, which I fetched, rather than their own.

**R15 mutations the control must fire on, each with its own named defect:** (a) the shipped ramp restored
on either column; (b) a drifting *pin* — the commons moved instead of the table, so neither side is
privileged; (c) a year-keyed rate table added anywhere in scope with no classification; (d) a table moved
from `simulation/` to `company/` — the mutation that proves the enumerator is repo-wide and not
module-scoped, and the one this whole finding exists because nothing could fail on; (e) an emptied or
missing register — the loader must raise, because an unavailable check is a failed check.

## Population, honestly

Two unregistered tables is an **instance count, not a population**. The sweep in repair step 1 has not
been run, so the number of year-keyed rate tables outside the register is **unknown and at least two**.
Nor is it claimed that any figure in the world-side stack besides those already checked is wrong: this
pass source-checked RO, and passes 3–4 checked gas CCL, electricity CCL and GGL. Nine of the thirteen
declared tables remain unchecked, including electricity network at £869k.
