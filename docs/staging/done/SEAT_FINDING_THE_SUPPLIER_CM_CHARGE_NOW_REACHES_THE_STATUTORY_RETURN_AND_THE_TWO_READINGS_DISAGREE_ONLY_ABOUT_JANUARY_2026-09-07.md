**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** a53-the-supplier-cm-charge-reaches-nothing

# The supplier CM charge now reaches the statutory return, and the two readings disagree only about January

**Measured and landed:** 2026-09-07, delivery seat.
**Pre-registration:** `SEAT_PREREGISTRATION_WHERE_THE_SUPPLIER_CM_CHARGE_SHOULD_LAND_AND_WHAT_IT_WILL_DISAGREE_WITH_2026-09-07.md`, filed before any of the series below was computed.

---

## The decision a53 asked for: WIRED, not deleted

`company/regulatory/capacity_market.py` was correct and reached nothing. One importer in the whole
tree, and it was the module's own test file. a53 offered two exits — wire it to the consumer that
should have it, or delete it with the reason recorded.

**It is wired, and the consumer was already there.** `company/regulatory/statutory_obligations.py`
composes the supplier's own annual statutory return — RO, FiT levelisation, CCL — off ONE shared
electricity-volume accumulator, behind the `company/interfaces/` door, called by
`simulation/run_phase2b.py`. Its docstring already states the doctrine: *"Working out what you owe
under the Renewables Obligation, the FiT levelisation levy and the Climate Change Levy is not
physics — it is a licensed supplier doing its own statutory accounting off its own supply
volumes."* The CM supplier levy is that sentence with a fourth noun. Per-MWh on electricity
supplied, Apr–Mar obligation year exactly as RO, no segment exemption.

**CM was the missing fourth leg of a return that already had three.** No consumer was invented —
which is the move a53 forbids and the move that produced the `0.92`.

## What was found on the way in, and it reframes the module

**CM already reached production and the annual report — from the SIM side.** The `CM` column of
Policy Cost & Levy Breakdown is fed by `years[*].cm_levy_gbp`, which
`simulation/hedged_settlement.py` accumulates per settled record from
`simulation/policy_costs.get_cm_levy_per_mwh`. So a53's headline — "the supplier CM charge reaches
nothing" — was true of the *company's* reading and false of the *levy*.

That matters, because it means the shape here is not "a levy nobody charges". It is:

| Levy | SIM: pass-through in the settlement | Company: the supplier's own return |
|---|---|---|
| RO | `ro_levy_gbp` | RO Cost Observatory ← `roc_ledger` |
| FiT | `fit_levy_gbp` | FiT Levelisation ← `fit_book` |
| CCL | `ccl_gbp` | CCL Observatory ← `ccl_ledger` |
| **CM** | `cm_levy_gbp` | **nothing — until now** |

CM was the one levy of the four where only the world had a reading at all. `ro_commons.py` states
the rule the pair has to satisfy: the two lanes may hold different READINGS and may not hold
different LAW. On CM they hold the same law — `simulation/policy_costs._CM_LEVY_BY_YEAR` and
`docs/domain_artefact_library/regulatory/capacity_market_supplier_levy.json` carry identical
figures for all nine published years. That was checked, not assumed.

## The measurement: the difference is January, and nothing else

Two CM totals on one page is this project's fourth-home failure unless the delta is reconciled, so
the reconciliation is computed at render time on the run's own numbers. Basis:
`docs/reports/run_output_latest.json`.

| Year | Elec MWh | Levy £/MWh | Statutory | Settlement | Delta | Implied Jan–Mar share |
|---|---|---|---|---|---|---|
| 2016 | 169.6 | 0.50 | 84.80 | 84.81 | −0.01 | — |
| 2017 | 227.3 | 1.10 | 250.03 | 205.01 | +45.02 | 33.0% |
| 2018 | 180.2 | 3.67 | 661.33 | 505.57 | +155.76 | 33.6% |
| 2019 | 174.9 | 4.79 | 837.77 | 780.74 | +57.03 | 29.1% |
| 2020 | 191.4 | 5.86 | 1,121.60 | 1,057.42 | +64.18 | 31.3% |
| 2021 | 192.4 | 4.67 | 898.51 | 968.78 | **−70.27** | 30.7% |
| 2022 | 178.1 | 3.37 | 600.20 | 673.40 | **−73.20** | 31.6% |
| 2023 | 171.2 | 5.68 | 972.42 | 856.80 | +115.62 | 29.2% |
| 2024 | 191.0 | 7.27 | 1,388.57 | 1,303.47 | +85.10 | 28.0% |
| 2025 | 89.1 | **NOT PUBLISHED** | **NO FIGURE** | 647.59 | — | — |
| **Total (published)** | | | **6,815.23** | **6,436.00** | **+379.23** | |

**The whole difference is obligation-year keying.** If it were, then for each year

    statutory − settlement  ==  (Jan–Mar volume) × (levy(N) − levy(N−1))

because the settlement buckets each record into its Apr–Mar obligation year, so January of year N
is charged at year N−1's rate. Dividing each delta by its levy step backs out an implied Jan–Mar
volume: **28.0% to 33.6%, in all eight years with a step, clustered near 31%.** That is exactly a
winter-weighted quarter. There is no residual: no segment filter, no fuel leaking into the
electricity accumulator, no volume-basis mismatch. The two readings disagree about which year a
January MWh belongs to and about nothing else.

## The pre-registration held, including the leg that could have refuted it

1. Statutory > settlement in most years, from keying through a rising series — **held**, 7 of 9.
2. **The refutable one: 2021 and 2022 must INVERT**, being the two years whose levy fell, so the
   settlement's January carry-back charges the higher prior rate — **held**, and they are the only
   two negatives in the table. Had they not inverted, "obligation-year bucketing" would have been
   the wrong cause and must not have been published.
3. |Δ| ≈ 0.25 × levy step × volume — **held in sign and order, under-predicted by 15–35% in every
   year**, consistently. The cause is in the measurement itself: the implied share is ~31%, not
   25%, because a winter quarter carries more than a flat quarter of annual demand. The
   correction is what turns claim 3 into the reconciliation above.
4. 2025 a gap on the company side and a number on the settlement side — **held**, £647.59.
5. Total £6,000–£8,000, second-smallest of the four legs — **held**, £6,815.23; the order is RO
   £42.7k > FiT £11.2k > CM £6.8k > CCL £0.7k.

**Disclosed at pre-registration time:** 2016 and 2017 were hand-checked before filing and are not
predictions.

## The 2025 divergence is the point, not a defect

Ofgem Annex 9 ends at obligation year 2024. The company's reading returns `None` with a named
reason and refuses to compute; the world's reading carries its last known rate forward and shows
£647.59. **Both behaviours are printed side by side on the page**, because a reader comparing the
columns is owed the reason one cell is empty. An unpublished cost is reported as absent, never as
last year's — which is what `capacity_market.py` was re-founded (a51) to guarantee, and this is
its first live application.

## What was built

* `company/regulatory/statutory_obligations.py` — `_cm_summary`, the fourth leg, off the shared
  accumulator; `StatutoryObligations.cm_summary`.
* `simulation/run_phase2b.py` — emits `cm_statutory_summary`. Named at length, and not
  `cm_summary`, so it cannot sit beside the settlement figure looking like the same quantity.
* `saas/reporting/annual_report.py` — `_section_cm_supplier_levy`, with the reconciliation
  computed live. **Keyed to the property, not to today's answer:** the implied Jan–Mar share is
  checked against a 15–45% band, and a share outside it makes the page say the delta is NOT
  explained by keying and is a finding. It is not prose that can rot beside the measurement.
* Five controls, each poisoned and each killed by its own named defect: dropping the CM leg,
  carrying the levy forward past the published record, widening the reconciliation band, rendering
  the unpublished year as £0.00, and dropping the key from the report's extract whitelist.
* `docs/design/orphan_baseline.json` and `ORPHAN_DISPOSITION_REGISTER.md` — the module's
  no-caller ruling is cleared and the ratchet floor lowered by one, so **unwiring it again now
  reds the ratchet.** That is a53's exit condition made mechanical.

## What is next, and is deliberately NOT in this change

1. **`simulation/policy_costs._CM_LEVY_BY_YEAR` is a literal table holding the same nine published
   figures as the commons artefact.** They agree today — checked. Nothing makes them keep
   agreeing, and the RO version of exactly this pair is what `ro_commons.py` was built to close.
   The SIM side should read the commons too. Not done here because a53 says do not do both halves
   at once, and this is the other half.
2. **THE CAPABILITY INDEX COUNTS A PATH MENTIONED IN A COMMENT AS A CALLER, and that wedged every
   lane's commits.** Found the hard way: this change was refused by
   `tests/tools/test_capability_index.py::test_the_live_register_rules_on_every_live_orphan`, which
   demands zero stale dispositions across the whole tree. Two rows besides this one were stale —
   `company.market.capacity_market` and `company.market.portfolio_position` — so the gate was
   already red at HEAD and no lane could commit.

   Both were "wired" by a PATH MENTION IN PROSE, not by an import. `company.market.capacity_market`
   has exactly one non-test caller in the index: `company.regulatory.capacity_market (by path)` —
   which is **a52's own docstring**, the paragraph explaining why the provider-side delivery legs
   were deleted rather than moved to `company/market/capacity_market.py`. Writing down where a
   mechanism already lives reclassified that mechanism as wired.
   `company.market.portfolio_position` is the same shape, from a comment in
   `company/trading/net_open_position_register.py`.

   **I deleted both rows, because the gate demands it and the tree was wedged — and the verdict
   behind them is unsound.** Neither module has a production importer; grep says so. This is the
   R15 source-text shape the catalogue already names for `src.count()` counting a comment that
   quotes the code it guards, one level up: an index whose caller edge is satisfiable by
   documentation will read "wired" for any orphan anyone writes about. That the register's own
   exit criterion is enforced on top of it means the mis-reading is not merely cosmetic — it
   deletes true no-caller rulings and blocks commits until they are gone. **The distinction
   between an import and a mention is the whole content of the measurement, and the index does
   not draw it.** Corrects this document's earlier claim that these were other lanes' rows to
   leave alone: one is a52's, and neither could be left.
3. **Two architecture controls are RED AT HEAD and are not this change's.**
   `test_switching_rate_commons.py::test_every_discovered_switching_level_candidate_is_registered_or_classified`
   names three unregistered readings in `company.crm.enriched_churn_estimate`, and
   `test_no_tree_scan_passes_on_an_empty_population` falls with it. Proved pre-existing in a clean
   `git archive HEAD` extract, not merely "red before I looked". Nothing in this change touches
   `company/crm/`.
4. **`docs/PROJECT_OVERVIEW.md` Phase 121 described the deleted mechanism** — the 0.92, the
   clearing-price table, `firm_capacity_kw`, and a claim about 2021→2022 that is backwards.
   Corrected in place with a dated superseded note rather than rewritten, because the correction
   is the part worth keeping. **Nothing noticed for the ten weeks it was wrong**, across a51 and
   a52 which each deleted part of what it describes.
