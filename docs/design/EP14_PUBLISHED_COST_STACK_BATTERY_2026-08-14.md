# EP14 — The published cost stack: the disqualification battery, run

**Atom:** `EP14_adapter_published_cost_stack` · lane `W4_the_wall` · epoch 3 · level 0 → 3 · `loop_stage: idle`
**Draw:** 2026-08-14 worker tick, LANE 3 (DISCOVER/FRAME only). **No BUILD code written** — the atom is
epoch-3 BUILD-gated (`block_reason`: director-reserved curriculum sequencing, R13);
`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1 permits DISCOVER/FRAME on a parked atom and forbids BUILD.
**Level:** HELD at 0 — the adapter is the deliverable, not the document.

**Neither the map nor the note store was edited, and this is a decision, not an omission.**
`docs/design/maturity_map.yaml` carries another lane's hunks in the index right now, and
`tests/design/test_simplifications_store.py` requires each atom's map `simplifications_count` to equal
its store file's note count — so appending a note to
`docs/design/simplifications/EP14_adapter_published_cost_stack.yaml` would oblige a same-commit map edit,
and a pathspec commit on that file would carry the other lane's hunks. This document is the record
instead. Nothing under `company/`, `saas/`, `sim/`, `simulation/` or `site/` was changed.

**This is the THIRD pass on EP14.** The first (2026-08-13, in the note store) established that the
"~£4.9M reconciliation gap" in this atom's own `name:` **is the cost stack's own total** and must never
be its exit criterion. The second (2026-08-14,
`docs/design/EP14_PUBLISHED_COST_STACK_DISCOVER_2026-08-14.md`) decomposed the gas side and found the
silent-clamp defect. **Both deferred to the same thing and both stopped at the same place:** the scope
brief's **B1** cap-annex reconciliation, which the second pass correctly showed is blocked on this
atom's own unbuilt half.

But B1 is one of **seven** tests. The brief
(`docs/domain_artefact_library/scope_briefs/ADVISOR_SCOPE_BRIEF_NONCOMMODITY_COST_STACK_2026-08-07.md`)
carries a **disqualification battery B1–B7**, and six of them need no adapter, no company build-up and
no network access. Neither prior pass ran any of them. **This pass runs the battery.** Two passes
deferring to the one blocked member of a seven-member battery is the shape worth naming: the blocked
test was allowed to stand for the whole battery.

Everything here is `observed-with-evidence` unless labelled otherwise (R9). **MEASURED AT:** HEAD
5975a4e26, live `docs/reports/run_output_latest.json`, with `simulation/policy_costs.py` functions
called directly and nothing monkeypatched.

---

## The battery, scored

| | test | verdict | evidence |
|---|---|---|---|
| **B1** | build-up reconciles to cap annex | **BLOCKED** | no company build-up exists; prior pass §4 |
| **B2** | no wrong-decade signals | **PASS, and see §2** | shape-invariance proven numerically |
| **B3** | fuel purity | **PASS** | import census, both directions |
| **B4** | losses as volume, not price | **PASS on the letter, §3** | no loss physics in the world at all |
| **B5** | every constant traces to a publication | **12 of 13** | one table cites no source |
| **B6** | three clocks / true-up | **NOT RUN** | needs a settlement rerun; `D2_three_clocks` owns it |
| **B7** | mutualisation bookable | **PASS** | £157,256.46 booked across the failure years |

The stack this is scored against, summed 2016–2025 from the run's own published per-year components:

| component | £ |
|---|---:|
| RO levy | 1,722,321.54 |
| CfD levy | 262,856.80 |
| FiT levy | 466,836.80 |
| CCL (electricity, business) | 458,497.10 |
| CM levy | 336,419.95 |
| mutualisation levy | 157,256.46 |
| *electricity policy total* | *3,404,188.65* |
| electricity network (DUoS+TNUoS+BSUoS+metering, combined) | 869,332.79 |
| gas policy | 171,108.84 |
| gas network | 393,759.19 |
| **total** | **4,838,389.48** |

## 1. B3 PASSES, and it passes structurally rather than by luck

The brief disqualifies a gas bill carrying RO, CfD, CM or AAHEDC, and an electricity bill carrying GGL.
Checked by import census at the two settlement modules, which is stronger than checking output values —
a charge that cannot be imported cannot be applied:

* `simulation/gas_settlement.py` imports exactly `get_gas_ccl_per_mwh`, `get_gas_network_cost_per_mwh`,
  `get_gas_standing_charge_per_day`, `get_ggl_per_mwh`. No electricity levy is in scope.
* `simulation/hedged_settlement.py` imports exactly `get_ccl_per_mwh`, `get_cfd_levy_per_mwh`,
  `get_cm_levy_per_mwh`, `get_fit_levy_per_mwh`, `get_mutualization_levy_per_mwh`,
  `get_electricity_network_cost_per_mwh`, `get_electricity_standing_charge_per_day`,
  `get_ro_cost_per_mwh`. No gas reader, and no `get_ggl_per_mwh`.

The two fuels are separated at the import boundary. **B3 PASS.**

**Coverage note, not a B3 breach:** `AAHEDC` appears nowhere in the repo — zero matches under
`simulation/` and zero under `company/`. It is a brief line with no line in the model, which is an
absence, not an impurity. Likewise the run's per-year components carry no separately identified ECO or
WHD line; whether either is absorbed inside `fixed_cost_gbp` was **not determined here** and is left
open rather than guessed.

## 2. B2 PASSES — and the proof shows the stack has NO time-variance at all

The brief's B2: *"if shifting a customer's evening peak changes their TNUoS or BSUoS cost,
DISQUALIFIED (~post-reform both are shape-invariant for domestic)."*

Proven, not asserted. `simulation/hedged_settlement.py` applies every non-commodity charge **inside**
the half-hourly loop (`for period in range(1, 49)`, lines 166–177), on that period's own
`consumption_kwh` — so the application is genuinely half-hourly. But every rate it multiplies by is a
function of the DATE only. Holding daily volume at 24 kWh on a winter weekday (2022-01-19, resi) and
redistributing it across maximally different shapes:

| shape | non-commodity cost, £/day |
|---|---:|
| flat across all 48 periods | 2.15232 |
| 100% inside the 16 peak periods | 2.15232 |
| 100% outside them | 2.15232 |

Identical to eight decimal places. The per-period rate takes exactly **one** distinct value across all
48 periods (£89.68/MWh). **B2 PASS** — and it is a structural pass: a census of all 13 reader
signatures shows not one takes an intraday time, a period index or a half-hourly shape. Their whole
argument surface is `(date_str, segment)`, plus `aq_kwh` for GGL.

**The consequence, which is the finding.** The same brief's time-variance census says what *should*
vary: *"genuinely time-varying = wholesale shape, DUoS bands, CM window exposure, losses-weighted
volume"*, and names DUoS band structure and the CM window as **NOT simplifiable** because *"these carry
the personalisation signal and the true-up physics."* Today:

* the **CM levy** (£336,419.95, 6.95% of the stack) is a flat £/MWh on all volume, though the real
  charge lands only in the winter weekday ~16:00–19:00 window;
* **DUoS bands** do not exist — DUoS is inside a single combined resi/SME network rate
  (£869,332.79, 17.97%), and the one DUoS-only table, `_DUOS_IC_BY_YEAR`, is also a flat annual £/MWh.

So **24.92% of the stack is the portion the brief says carries genuine time-variance, and all of it is
flat.** B2 passes because the stack is shape-invariant *everywhere*, including the two places where
shape-invariance is the wrong answer. A test that can only be failed by over-modelling is passed by
modelling nothing — worth stating because the green verdict reads as fidelity and is partly the absence
of the mechanism. The brief puts this stack under "the cost side of the abatement engine — time-shifting
only creates value where the stack is time-varying"; `flexibility_revenue_gbp` is **£0.00** across the
whole run.

Filed as `docs/staging/WORKER_FINDING_THE_NON_COMMODITY_STACK_IS_EXACTLY_SHAPE_INVARIANT_2026-08-14.md`
(LATENT — queued, not fixed, per SELF_INTERRUPT discipline; grading argument in the finding).

## 3. B4 — losses are not a price line, because losses are not anything

The brief: *"settled kWh = metered × LLF × TLM; losses appearing as a p/kWh price line instead is
disqualified."* Losses do **not** appear as a price line, so B4 passes as written. But the volume
uplift is not there either: `LLF`, `TLM` and `loss_factor` return **zero matches anywhere under
`simulation/`**. Settled volume is metered volume.

The organ exists — on the wrong side of the wall. `company/market/llf_register.py` is a full LLF
register whose own docstring states the physics (*"Settlement quantity = Metered quantity x LLF"*,
*"flat 1.0 assumption is an error"*), and it is reachable only from other company modules and tests.
**This is the exact inversion of the prior pass's finding 4.** There, one table served both sides of
the wall so the company could not be wrong; here the company holds a belief about losses that the world
does not implement, so the company cannot be *right* — there is no truth for its LLF register to
approximate. Both are the same wall defect from opposite ends, and EP14's build touches both.

## 4. B5 — twelve of thirteen tables cite a publication; one does not

The brief: *"every constant traces to a published artefact (CDCM sheet version, ILR notice, cap annex
cell) — an untraceable constant is invented physics."* Censused over the 13 tables `YEAR_KEY_BASIS`
declares, reading the comment block immediately above each definition:

Twelve cite a named source — Ofgem (RO, network, CM, mutualisation, both standing charges, gas
network), HMRC (both CCLs), npower + Ofgem FiT reports (FiT), DESNZ (GGL), and a source line for CfD.
**`_DUOS_IC_BY_YEAR` cites none.** Its comment explains its *keying* and its relationship to the Triad
mechanism, but nothing says where £11.0 → £14.0/MWh came from. It is the I&C DUoS path.

Not quantified here: what share of the £869,332.79 electricity network line is I&C DUoS. Decomposing it
needs a re-run attributing by segment, which this pass did not do — stated rather than estimated.

## 5. B7 PASSES, with money on it

The brief: *"the model can book an RO mutualisation surcharge in a supplier-failure year replay; if the
mechanism cannot exist, the 2021–22 cost physics cannot be reproduced."* `_MUTUALIZATION_LEVY_BY_YEAR`
exists, `get_mutualization_levy_per_mwh` is imported and applied by `simulation/hedged_settlement.py`,
and the run books **£157,256.46** across the window. The mechanism is not merely present; it fires.
**B7 PASS.**

## 6. B6 — not run, and why that is not a second B1

B6 wants a settlement rerun that restates volumes to restate DUoS/CfD/CM through the billed/settled/
banked discipline. That is a rerun-and-restate exercise owned by `D2_three_clocks`, not a property of
the cost stack readable from a single run. It is **not** blocked on EP14's unbuilt half the way B1 is —
it is simply another atom's subject. Recorded so the next draw does not re-defer it as though it were.

## 7. What this pass did NOT do

* No adapter, parser, schema-drift or cap-annex work. Nothing in `file_scope` touched.
* **B1 still not run**, for the reason the prior pass established — the company has no build-up to
  reconcile, and running it today would measure the world against itself.
* **B6 not run** (§6). **B5's material exposure not quantified** (§4). The gas tables' *values* still
  not re-checked against source — open since the first pass.
* No external source fetched: this tick had no network. Nothing here claims any tabulated rate is
  numerically wrong.
* No level moved, no map edit, no note-store edit (see header).

## 8. Also observed, and filed separately

The silent-clamp defect the second pass filed **has already been repaired — in the working tree only.**
`simulation/policy_costs.py` carries an uncommitted 142-line addition (`table_coverage`,
`is_extrapolated`, `extrapolation_status`, `coverage_report`, `first_extrapolated_date`), its test
`tests/simulation/test_policy_cost_coverage.py` is untracked, and the consumer edits in
`simulation/run_phase4c_on_phase2b.py` and `saas/reporting/annual_report.py` are uncommitted too. The
supplier and its consumers are all on the same side of the tree, so this is **not** the
consumer/supplier split whose class closed today — checked, and it is worth checking rather than
assuming. What it is: `docs/reports/ANNUAL_REPORT.md` already carries the generated disclosure
("EXTRAPOLATED RATES — 13 of 13 rate tables", lines 510 and 537) and that file is staged in the index,
while no committed code can regenerate it. **Not adopted or landed by this pass** — it is another
lane's work in that lane's subject area, and this is a DISCOVER draw. Filed as
`docs/staging/WORKER_FINDING_THE_REPORTS_EXTRAPOLATION_DISCLOSURE_HAS_AN_UNCOMMITTED_GENERATOR_2026-08-14.md`
— titled to carry its class token deliberately: `background/finding_classes.classify_file` reads only the
FILENAME and H1 TITLE, so a `**class:**` line in the body is invisible to it and the finding would
never have reached `CLASS_UNCOMMITTED_AND_ORPHANED_WORK`.
