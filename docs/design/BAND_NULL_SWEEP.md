# H33 — Does this statistic have a null, and is the threshold above it?

**Atom:** `H33_does_this_statistic_have_a_null` (lane H_harness, epoch 3, L0 -> L2)
**Mechanism:** `background/band_null_sweep.py` | **Runner:** `tools/band_null_sweep.py`
**R15:** `tests/harness/test_band_null_sweep.py` (25 tests, both directions)
**Artefact:** `docs/observability/band_null_sweep.json`
**Minted from:** the CLASS half of `WORKER_FINDING_AN_ANCHOR_IS_A_NUMBER_AND_A_WINDOW_2026-08-09`

## The question

Not "is the anchor real" — L1.4's anchor *was* real, correctly quoted from a
published source, and the band was still fail-open, because a total-variation
distance between two subsets of one home's own data is bounded away from zero by
sampling noise alone. A population with no weekday/weekend structure whatsoever
cleared it. Re-reading the source could never have caught that.

The question is: **what does each statistic read on a population from which the
structure its band certifies has been REMOVED, at the window the band is APPLIED
at — and is the threshold above that?**

## (1) The enumeration

Derived by iterating the live `fabric_gap_ledger.BANDS` table
(`anchored_bands()`), never from a hand-copied list. **9 of 14 bands** carry a
numeric threshold and an external anchor (`published` / `domain`). The other 5
are reported as an explicit complement with reasons (`excluded_bands()`), so a
band that changes anchor class leaves the sweep's scope visibly rather than
evaporating from a list:

| excluded band | reason |
|---|---|
| `L1.1u_half_hourly_texture_unregistered_regime` | no numeric threshold (anchor=need) |
| `L1.2h_heating_shape_repeatability` | no numeric threshold (anchor=need) |
| `L1.4_weekday_weekend_separation` | no numeric threshold (anchor=need) — the instance this atom was minted from |
| `L1.4n_weekday_weekend_null_ratio` | structural: its bound is an argument, not an external figure |
| `L1.5_max_multiplicity_share` | structural, as above |

`unswept_band_sources()` re-scans `background/` and `tools/` by AST for any
*other* module constructing a `Band`/`RateBand`. Currently empty — the
enumeration's source is complete. A mention in prose does not count (see
`lcl_household_anchors.py`, which discusses `AnchorStatus.NEED` and declares
nothing); an always-red detector would be as ignored as a blind one.

## (2) The measurement

**Applied window: 10 homes x 120 days**, read off `tools/couple_fabric.py`
(`WINDOW_START` 2022-01-01 -> `WINDOW_END` 2022-04-30) rather than restated, so
the tool's window cannot desync from the sweep's claim.

Each band's null removes exactly the structure that band certifies and leaves
everything else intact. The verdict rule was fixed **before** any number was
looked at: `INSIDE_NULL` when the structureless population clears the band in at
least 1 draw in 20; `SAME_ORDER` when it fails by less than the null's own p5-p95
spread; `SEPARATED` otherwise.

| band | dir | n | threshold | null (best) | null spread | margin | verdict |
|---|---|---|---|---|---|---|---|
| L1.1_half_hourly_texture | at_least | 9 | 0.15 | 0.0818 | 0.0432 | +0.0682 | separated |
| L1.1e_..._electric_heat | at_least | 1 | 0.0705 | 0.0542 | — | +0.0163 | separated \*\* |
| L1.1r_..._resistive_heat | at_least | 0 | 0.0363 | — | — | — | **unmeasurable** |
| L1.2_day_to_day_shape_correlation | at_most | 10 | 0.85 | 1.0 | 0 | +0.15 | separated |
| L1.3_away_days_per_year | at_least | 10 | 1.0 | 0.0 | 0 | +1.0 | separated |
| L2.1_smoothing_ratio | at_most | 10 | 0.85 | 1.0 | ~0 | +0.15 | separated |
| L2.2_between_home_correlation | at_most | 10 | 0.6 | 1.0 | 0 | +0.40 | separated |
| L2.3_timing_diversity_periods | at_least | 10 | 0.5 | 0.4899 | 0.2677 | **+0.0101** | **same_order** |
| L2.4_scale_spread_p90_p10 | at_least | 10 | 4.881 | 1.0 | 0 | +3.881 | separated \*\* |

\*\* the null rests on a single reading, so it has no estimable spread: the
`SEPARATED` verdict is a point estimate and `SAME_ORDER` was not reachable for
that band at this window. Carried as an explicit `caveat`, not folded into the
verdict.

### Two failed nulls, recorded because they are the same mistake this sweep exists to catch

The first two versions of the flat-day null **added** the movement the band
measures, and each produced defects that were not there:

1. Resampling each day's *total* injected level jumps across the midnight
   boundary: texture rose ~0.05 -> ~0.35 and L1.3 gained 120 spurious away days
   per home. Three bands falsely reported fail-open.
2. Bootstrapping the mean profile was defended as "the estimation noise a
   120-day mean genuinely carries" — but sampling noise in a mean profile *is*
   half-hourly movement, which is exactly what L1.1 measures. It inflated the
   texture null ~30% and flipped L1.1e into a defect on the strength of noise
   the null itself had added.

The shipped null is **deterministic** and is the *most favourable* structureless
generator available — it keeps each home's own mean profile and its own daily
totals, where a real smooth-by-construction generator (the shipped rescaled-PC1
path) has one national profile for everybody. So a band this null clears is
unambiguously fail-open, and a band it fails is separated against the friendliest
structureless population that could be built.

## (3) Dispositions

**Never lower the floor until something fails (R12).** Two repairs are allowed.

### L2.3_timing_diversity_periods — REPAIR THE STATISTIC

The band (0.5 half-hours, `at_least`) clears its null by **3.8% of the null's own
spread**. Its window sensitivity, measured on the live panel:

| window | null p95 | null median | observed | margin | verdict |
|---|---|---|---|---|---|
| 40 d | 0.8107 | 0.5887 | 1.3847 | **-0.3107** | inside_null |
| 60 d | 0.7026 | 0.4845 | 1.2620 | **-0.2026** | inside_null |
| 90 d | 0.5333 | 0.3840 | 1.1263 | **-0.0333** | inside_null |
| 120 d | 0.4899 | 0.3444 | 1.0129 | +0.0101 | same_order |

The band sits **inside its own null at 40, 60 and 90 days** and clears it at 120
only marginally — while the number in the table never moves. A population of
homes with no timing identity at all would pass L2.3 on any shorter run.

The observed value falls *with* the null (1.38 -> 1.01 as the null goes 0.59 ->
0.34), which is the diagnostic that decides the repair: `timing_diversity` is a
spread-of-means and carries the same sampling term as its own null, so **no fixed
half-hour floor can be correct at every window**. The repair is the L1.4 -> L1.4n
pattern: score the observed spread against its own permutation null (observed /
null, ~2.9x at 120 d and ~2.35x at 40 d — far more stable than the raw statistic
against a constant) rather than against a constant. Repairing the window instead
would only move the problem to whichever window is run next.

### L1.1r_half_hourly_texture_resistive_heat — UNMEASURABLE, widen the panel

No home at the applied window is judged by this band: `tools/couple_fabric.py`'s
PANEL is 9 gas boilers and 1 air-source heat pump, and there is no resistive
(`electric_storage` / `electric_direct`) home at all. The band is carried and
never exercised — notable given it was derived *because* a storage-heater home
breached L1.1. Its null cannot be measured on the load set it governs, and
measuring it on the gas panel would be the wrong-load-set defect. Disposition:
add a resistive-heat home to the panel, then re-run; not a threshold change.

### L1.1e_half_hourly_texture_electric_heat — one home, no estimable spread

Margin +0.0163 against a null of 0.0542, both from the single heat-pump home. The
verdict is a point estimate: `SAME_ORDER` was not reachable for this band at this
window, so `SEPARATED` here means "not obviously inside its null", not "clear of
it". Same disposition as L1.1r — widen the panel, then re-measure.

None of the three is dispositioned as a threshold move.

## The sweep's own fail-open shapes, and what closes each

| shape | guard | test |
|---|---|---|
| enumerates nothing, reports clean | `sweep()` raises on empty | `test_an_empty_enumeration_RAISES` |
| a band silently skipped | `sweep()` raises on missing null spec | `test_a_band_with_no_null_spec_RAISES` |
| a band table in another module | AST scan of `background/` + `tools/` | `test_a_band_table_outside_the_swept_set_is_FOUND` |
| the guard reds on prose | AST call nodes only, not text | `test_a_MENTION_of_a_band_is_not_a_declaration` |
| the null invents structure | daily totals preserved, null deterministic | `test_the_null_does_not_INVENT_structure` |
| a null read on the wrong load set | sub-populations routed through `texture_band_for` | `test_a_bands_null_is_read_only_on_the_homes_it_JUDGES` |
| an unexercised band reads as clean | `UNMEASURABLE` is its own state and counts as a hit | `test_a_band_with_NO_home_to_judge_is_unmeasurable_not_clean` |
| the verdict cannot move | threshold moved into the null flips it | `test_a_threshold_moved_INTO_its_null_flips_the_verdict` |
| the middle verdict is unreachable | threshold inside the spread yields SAME_ORDER | `test_a_band_separated_by_LESS_than_its_nulls_spread_is_a_finding` |
| the sweep re-implements a statistic | source asserted to call `fgl.*` and define none | `test_the_sweep_reads_the_SHIPPED_statistics_not_its_own_copies` |

`tools/band_null_sweep.py` exits 1 on any `INSIDE_NULL`, so a scheduled run is an
alarm and not a report.

## Appendix — the atom as minted

Moved here verbatim from `maturity_map.yaml` when the map hit its size ratchet.
The record is not lost, it is in the place the ratchet exists to push it:

> MINTED FROM the CLASS half of WORKER_FINDING_AN_ANCHOR_IS_A_NUMBER_AND_A_WINDOW_2026-08-09 (the instance half closed the same day; the sweep it proposes has never been run). THE QUESTION, per band: not 'is the source real' but 'does this statistic have a NULL, and is the threshold above it?' -- a distance between two SUBSETS of one subject's data is bounded away from zero by sampling noise alone, and a band derived over a full year can sit UNDER the null of the same statistic at a 120-day window, so a randomised population clears it. Sibling shapes already on the register: worst-of-N not scale-invariant, band applied to the wrong load set, mutation must dominate the natural spread. EXIT: (1) an ENUMERATION of every band in background/ and tools/ carrying a numeric threshold and an external AnchorStatus, derived from the band tables rather than by inspection; (2) per band, the statistic's null MEASURED by randomising the structure it is meant to detect at the window the band is APPLIED at (not the window it was derived at), with the margin recorded -- a band inside its own null is a defect, a band the same order as it is a finding; (3) each hit dispositioned repair-the-statistic (the L1.4->L1.4n permutation-null pattern) or repair-the-window, NEVER lower-the-floor-until-something-fails (R12 goal-seek); (4) R15 both ways incl. a vacuity guard proving the enumeration is non-empty on the live tree, since a sweep that finds no bands is the fail-open shape here.
