# WORKER FINDING — the ageing headline scores a perfect 0.000000 for a company that wrongfully ages its entire current book

**Date:** 2026-08-10 · **Found by:** worker tick running Expert Hour #6 on `H27_payment_belief_gap` (2→3)
**Advances:** `D22_ageing_ordinal_is_one_directional` (minted here, **not** built here) · `H41_the_map_ratchet_has_no_ongoing_drain` (recurrence measured)
**Verdict:** **HELD AT L2.** Sixth Hour, sixth defect, and the third sighting of one class.
**R12:** nothing was tuned. Every published figure is byte-identical before and after — the headline,
both direction rates and the mean displacement. Only witnesses were added.

## Why the Hour ran here

Hour #5's release named the criterion and the start point in advance: *two consecutive clean Hours*,
starting on the two leads it handed over about the ageing dimension's **population**. This Hour took
the second of them. It is not clean.

## The finding (observed, R9)

`background/gap_metric.py::_ageing_counts` builds the ordinal term over the truly-overdue only:

```python
displacements = [abs(rank[b] - rank[t]) for t, b in scored if t != current]
```

`GapResult.gap` — the number the ledger and the Proof door carry — is the mean of that list. So no
amount of **over**-ageing can move it.

### Measured, through the shipped scorer, n=4000

Each strategy scored through `ageing_gap` with the live D16 exclusion mask, at seeds 7 / 11 / 23:

| company | headline | `understated` | `overstated` | `max_disp` |
|---|---|---|---|---|
| dates every invoice right | **0.000000** | 0.0 | 0.0 | 0 |
| perfect on the overdue book, **every** truly-current invoice dated `90+` | **0.000000** | 0.0 | **1.0** | 0 |
| perfect on the overdue book, every truly-current invoice dated `30-60` | **0.000000** | 0.0 | **1.0** | 0 |

10,758 cases changed between row 1 and row 2 and the headline did not move — identical to machine
precision, at all three seeds. Rows 2 and 3 are the point the dimension exists to make: its docstring
says the ordinal term *"distinguishes off-by-one from stone-blind, which an error rate cannot"*. In
the over-ageing direction it distinguishes neither, and `overstated_arrears_rate` — the plain rate the
ordinal term was built to improve on — is all that is left.

The direction is **not** invisible to the *dimension*; it is invisible to the *ordinal term*, which is
the whole of what this dimension adds over a rate. A 30-60 wrongful ageing and a 90+ one send a real
supplier's account down different collections paths.

## Why the sweep, not the instance, is the defect

`DETECTION_DIRECTION_CONTRACT` already states this class in the same file:

> a one-directional detection score cannot distinguish a precise company from an indiscriminate one,
> so it MUST either measure both directions or name the atom that will make it

D11/D12/D14/D15 fixed it in four detection dimensions. D19 then found it had **escaped into `belief`**,
and named why: *"it is keyed to detection scorers, so the BELIEF dimension … was never swept."* It has
now escaped the same way a second time, into the one dimension that is neither a detection scorer nor
a rate. Three sightings, one keying.

The existing sweeps could not have caught it. `AGGREGATE_SCORING_CONTRACT` passes on `ageing`
legitimately — a permutation *does* move it (0.1232 → 1.2246) — so the direction blindness sat
underneath a green probe.

## What landed (closed at the class, R10)

**`HEADLINE_DIRECTION_COVERAGE`** — the sweep with the keying removed.

- **Keyset DERIVED from what `score_triad` publishes**, not listed. A published dimension with no
  entry raises; so does a registered dimension nobody publishes. A dimension cannot escape by not
  being a detection scorer, by being ordinal, or by being added later.
- **Per entry, the dimension's own indiscriminate degenerate**, scored through the dimension's **own
  shipped scorer** (`_rescore_dimension`, no second copy of any formula), beside a perfect company:

  | dimension | perfect → degenerate | verdict |
  |---|---|---|
  | `detection` | 0.0 → 0.5 | distinguishes |
  | `belief` | 0.0 → 0.5 | distinguishes |
  | `belief_population_mix` | 0.0 → ~0.96 | distinguishes |
  | `ageing` | 0.0 → **0.0** | **named debt, atom D22** |

- **A third state, checked rather than trusted.** `detection_latency` is honestly truth-conditioned —
  its population is cases the company *did* detect, so an indiscriminate flagger's extra flags never
  enter it and there is no belief-side degenerate. Its entry therefore **names the sibling** that
  counts the direction it cannot, and the control asserts (a) that sibling really does distinguish and
  (b) no truly-current case reached the latency population. `latency_inputs` is published for that
  probe: a dimension a control cannot reach drops silently out of the sweep, and an unreachable entry
  reads exactly like a clean one.
- **Ageing may not claim that cover**, and the reason was already measured: D16 established that
  detection's `false_flag_rate` is a *different quantity over a different population* from this
  dimension's overstatement. Nothing in this instrument sees over-ageing **severity**.
- **Printed every run** in the CLI beside the permutation control, verdict line included — a limit a
  reader has to go looking for is one they read past.

**Stamped at source**, so it reaches the scorer's other caller (`tools/d6_ageing_metric_oracle.py`)
and not only the pair whose Hour found it (the D19 pattern): `mean_overstatement_displacement`,
`max_overstatement_displacement`, `n_overaged_beyond_one_bucket`, and an `ordinal_direction_caveat`
whose witnesses are interpolated from the measurement rather than typed in once and left to rot.
`format_ageing_summary` prints the mirrored term, so the headline cannot be published bare.

### R15, both ways

| mutation | what fires |
|---|---|
| declare the one-directional `ageing` headline as counting both | "declared to count BOTH error directions, but its degenerate scores…" |
| declare the two-directional `detection` headline as debt | "…it DOES tell its degenerate apart. The entry has rotted" |
| strip `ageing`'s `debt_atom` | "one-directional with neither a `debt_atom` nor a `covered_by` — an unowned hole" |
| point latency's `covered_by` at the one-directional `ageing` | "a cover claim covering nothing" |
| point `covered_by` at a dimension that does not exist | raises |
| declare a degenerate strategy nobody wrote | raises |
| make the ageing degenerate inert | vacuity guard: "the probe is VACUOUS" |
| leak a truly-current case into the latency population | "no longer truth-conditioned" |

## The lead that was checked and NOT taken

Hour #5's **lead 1** — the truly-overdue side reaching 2 of 4 buckets on a three-age book. Real,
already pinned by `test_the_ageing_headline_is_entirely_miss_driven_here`, and it turns out to be the
same weakness from the other side: of the 4-bucket ordinal vocabulary the headline is published in,
one side of the book exercises two buckets and the other contributes nothing at all. Widening the
scenario's age spread moves published numbers on every dimension, so it stays registered.

## Two things this tick caught about its own record-keeping

1. **The Hour #5 entry was missing from the atom's simplification record.** Hour #5 caught exactly this
   omission in the map's `expert_hour.findings` and recorded it late; its own entry in the *other*
   register was then left behind. Two consecutive Hours, two registers, the same divergence. Written
   late above and marked as late. Two append-only registers with nothing tying them together will keep
   diverging — that is a mechanism gap, not a memory gap.
2. **The map's per-atom byte budget went red on the attempt to record this Hour faithfully** — H27 at
   12,685 B against the 12,288 B cap. That is `H41_the_map_ratchet_has_no_ongoing_drain` recurring in
   the field its own exit criterion (2) anticipates: `expert_hour.findings` is the map's next unbounded
   narrative flow after the two H41 named. `expert_hour` cannot be rehomed on sight —
   `store.is_record_field` is a class guard, so adding it fires `check_no_inline_records` on every atom
   carrying the field, and both production readers (`generate_proof_data::_verification_stack`,
   `generate_maturity_map_data`) load the map with a bare `yaml.safe_load` and would silently drop a
   field that publishes to the Proof door. **Interim, recorded as interim:** the map entry is a pointer
   and the full text lives in the store record and in this document, which is where the control's own
   violation message says growing prose belongs. No record was shortened away. The flow is still
   running and the next faithful Hour will red this again.

## Why H27 is still at L2, and the criterion for Hour #7

Hour #4 set the release criterion as **two consecutive clean Hours**. Six Hours, six defects, none
predicted by its predecessor, and this is again the tick that changed the instrument — the worst-placed
tick there is to certify it. The count is still zero.

**Hour #7's criterion, stated in advance:** two consecutive clean Hours, and the first place to look is
`detection_latency` — the one dimension no Hour has taken on its own terms, and now the only entry in
the new register whose honesty rests on a division of labour with a sibling rather than on its own
arithmetic.

## Tests

13 new in `tests/tools/test_couple_w2_11_d5.py` (235 in that file). **516 green** across every suite
touching `gap_metric` and the coupled pairs: `test_gap_metric`, `test_gap_metric_misapplication_class`,
`test_d7_ageing_measures`, `test_d6_ageing_metric_shape`, `test_couple_w2_11_d5`, `test_couple_cohort`,
`test_couple_supply_start`, `test_couple_w2_4_c6`, `test_couple_w2_5_c7`, `test_couple_fabric`,
`test_couple_w2_7_c9`, `test_couple_w2_9_c11`, `test_live_payment_triad`, `test_coupled_triad_gate`,
`test_generate_proof_coupled_gaps`, `test_c10_self_rationing_detection`, `test_c7_life_event_detection`.
94 green in `tests/design` + `tests/controls/test_map_reconciliation.py`.
