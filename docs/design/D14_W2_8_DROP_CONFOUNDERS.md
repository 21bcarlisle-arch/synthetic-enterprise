# D14 — the world had no way to be wrong, so the detector had no way to be wrong either

**Atom:** `D14_w2_8_needs_negative_drops` · **Lane:** D_billing_metering · **Level:** 0 → 2
**Built:** 2026-08-09 · **Minted by:** `D13_self_rationing_negative_population_discover`
**Pair:** `W2_8_self_rationing` ↔ `C10_self_rationing_detection`
**Files:** `simulation/self_rationing.py` (WORLD), `tools/couple_w2_8_c10.py` (HARNESS),
`tools/couple_w2_11_d5.py::DETECTION_DIRECTION_CONTRACT` (the register entry this pays)

---

## The finding this pays

The D13 DISCOVER measured the W2_8↔C10 pair's false-flag rate as **0.0000 — for any
drop-based detector whatsoever**. Not because the detector was precise: because
`generate_self_rationing_state` returned `observed == healthy` **exactly** on the not-onset
branch, so of 3752 non-rationers, **0 had any consumption drop at all** and 0 were flaggable
under any of the five weather factors the coupler can draw.

A rate of zero that no company behaviour can move is a property of the **world**. Publishing it
beside a recall figure would have read as detector precision (R12). So the second direction was
held back, the register entry stayed recall-only, and the debt was booked here.

**The blocker was world depth, not metric design** — which is why this took a WORLD change and
not a denominator edit.

## What was added to the world

`simulation.self_rationing.DropConfounder` — a **non-budget cause of a consumption drop**, drawn
**independently of the rationing label** from this module's own new named substreams
(`confounder_onset`, `confounder_magnitude`, APPENDED to `_SUBSTREAMS`, so every pre-existing
onset and severity draw is byte-identical).

| cause | incidence/yr | drop band | anchor (R10) |
|---|---|---|---|
| `HOUSE_MOVE` | 0.100 | 0.20–0.70 | ~10% of GB households move each year — advisor scope brief `ADVISOR_SCOPE_BRIEF_CHANGE_OF_TENANCY_2026-08-07.md` (itself marked verify-current). The outgoing account reads part of a year against a full-year baseline. |
| `VOLUNTARY_CUT` | 0.060 | 0.15–0.35 | GB domestic demand fell materially through the 2022-23 price shock (DESNZ/NESO; gas ~10-15%, electricity mid-single-digit) and much of it came from households under **no** budget stress. The phenomenon is anchored; the per-household incidence is a curriculum shape [L]. |
| `VACANCY` | 0.020 | 0.50–0.90 | Vacant dwellings run ~2-3% of the English stock (council-tax-base dwelling statistics), long-term empties ~1% [L]. |
| `EFFICIENCY_RETROFIT` | 0.010 | 0.10–0.30 | ECO/GBIS-scale installs in the low hundreds of thousands a year against a ~28m stock, i.e. ~1%/yr, at a typical 10-30% saving [L]. |

Compounding: a rationer who *also* moves out cuts further — the two cuts multiply on the same
home — but `rationing_severity` keeps naming **only** the budget-driven part, so the answer key
never absorbs the confounder's share and the harm attributed to hardship is not inflated by a
house move.

**R13 discipline.** This is a BASELINE fidelity change: made because the world lacked a real
phenomenon, decided blind to what it does to the measured gap. The four incidences and bands were
fixed from the anchors above and committed **before** the resulting false-flag rate was measured.
The change RAISES that rate off zero. That is the point, and it is never a number to tune back
down (R12).

## What it measures now

Reference population, `n = 4000`, no seed (deterministic):

```
                                     BEFORE (confounders off)   AFTER
must-flag   (is_silent_hardship)              192                205
NEITHER     (rationing, above floor)           56                 43
must-not-flag (label == NOT_RATIONING)       3752               3752
  ... of which really DID drop                  0                695   <- the point
recall (caught/truth)                      0.6927             0.6878
false-flag rate, settled negative           0.0000             0.0560
false-flag rate, naive denominator          0.0000             0.0553
```

The confounder mix at that population is `house_move 380 · voluntary_cut 262 · vacancy 84 ·
efficiency_retrofit 32` (19% of households, matching the incidences).

Two consequences that must not be glossed:

* **The truth set MOVED (192 → 205).** Confounders push some above-floor rationers below the
  floor, so they cross from NEITHER into `is_silent_hardship`. The change is not truth-preserving
  and is not claimed to be.
* **Recall barely moved (0.6927 → 0.6878).** The miss direction is still the smart-meter coverage
  blind spot; this change did not buy the company anything on the direction it was already scored
  on.

## The denominator defect, fixed in the same change

The DISCOVER found `false_positive_rate` dividing by `n_customers - len(truth_set)` — sweeping
the households that **are** self-rationing but sit above the floor into the negatives. A C10 flag
on one of them is **correct**; counting it as a false flag scores the company down for being
right (the D11 rule). It cost 0.0000 when found, because everything did.

It costs something now: **0.0560 (settled) vs 0.0553 (naive)** — the numerators are identical (43
NEITHER households, none of them flagged, because the detector requires below-floor) and the
denominators differ, 3752 vs 3795. Small, and published anyway: `NEGATIVE_BASES` scores **both**
every run, so the defect cannot come back quietly. Unlike the sibling D15 pair's three-way R13
call, this is **not** a curriculum choice — the naive basis is simply wrong, and travels only so a
reader can see what it is worth.

The 43 excluded households are published, not silent (the D10 rule): `n_excluded` and the
`exclusion_reason` travel in the ledger components.

## The register entry this pays

`couple_w2_8_c10.detection` moves from `counts_both_error_directions: False` (debt, owner D14) to
`True`, scorer `background.gap_metric.detection_measures`. The published pair gap changes meaning:
harm-weighted miss only (0.3094) → **mean of both directions (0.1787)**, `g0 = 0.5`. The old
ledger entry's number is not restated as if it were the same measurement.

**A control that could only pass while debt existed.** Flipping the last recall-only entry broke
`test_every_published_detection_dimension_declares_its_error_directions`: its vacuity guard
asserted that *some* register entry was still recall-only, and its lying-declaration sibling
picked that entry at runtime. Both would have failed on the day the register got clean — the one
day they most need to work. The recall-only side of the differential is now scored from
`detection_gap` **directly** (`_reference_recall_only_score`), so the control no longer depends on
an unpaid liability existing.

## R15 — the controls fire on their own named defect

* `test_the_world_emits_hard_negatives_a_drop_with_no_hardship` — non-rationers who genuinely drop
  exist, at a material rate, each with a named cause, and all four mechanisms are reachable.
* `test_mutation_disabling_confounders_restores_the_vacuous_world` — the MUST-FIRE half: with
  `confounders_enabled=False` the world returns to 0 hard negatives and `observed == healthy` for
  every household, exactly as D13 measured it.
* `test_mutation_the_published_measure_never_runs_with_confounders_off` — the off-switch is a test
  instrument only; the published entry point cannot reach it, and if it could, the false-flag rate
  would read exactly 0.0000 again.
* `test_no_drop_is_ever_unexplained` — every drop traces to severity, a confounder, or both; the
  confounder cannot mask a generator bug as noise.
* `test_confounders_are_drawn_independently_of_the_rationing_label` — a confounder that only ever
  landed on non-rationers would let the label be recovered from the drop cause.
* The flag-EVERYTHING degenerate is scored through this pair's own `false_flag_measures` in the
  register control, so a regression to recall-only fails it rather than passing a re-implementation.

## Registered simplifications (R10 — never hidden)

* **At most one confounder per household per period.** Real homes can move *and* be retrofitted.
* **The cause is ANSWER KEY: the company cannot see it.** In reality a supplier learns of some of
  these directly — a change-of-tenancy registration, an ECO install on its own scheme, a void
  notification. Hiding them makes detection strictly **harder** than reality, so the published
  false-flag rate is an **upper bound**, never flattering. Minted as the follow-on atom
  `D18_confounder_observable_channel` — a company that can explain away a known house move should
  false-flag less, and the gap between the two is itself worth measuring.
* **Magnitudes are annual-consumption fractions, not within-year profiles.** This world has no
  intra-year shape to cut.
* **Harm on a rationer who also drew a confounder** is computed from the compounded observed
  figure, so part of it is attributable to the move/void rather than to hardship. The household
  really does consume that little; the attribution split is not modelled.

## Reproduction

```bash
python3 -m tools.couple_w2_8_c10 --customers 4000          # both directions, both bases
python3 -m pytest tests/sim/test_w2_8_self_rationing.py \
                  tests/test_c10_self_rationing_detection.py \
                  tests/tools/test_couple_w2_11_d5.py -q
```

The BEFORE column is reproduced by `couple.build_populations(4000, confounders_enabled=False)`.
