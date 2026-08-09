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
(`anchored_bands()`), never from a hand-copied list. **8 of 15 bands** carry a
numeric threshold and an external anchor (`published` / `domain`) — it was 9 of
14 until H34 executed the L2.3 disposition below. The other 7 are reported as an
explicit complement with reasons (`excluded_bands()`), so a band that changes
anchor class leaves the sweep's scope visibly rather than evaporating from a
list:

| excluded band | reason |
|---|---|
| `L1.1u_half_hourly_texture_unregistered_regime` | no numeric threshold (anchor=need) |
| `L1.2h_heating_shape_repeatability` | no numeric threshold (anchor=need) |
| `L1.4_weekday_weekend_separation` | no numeric threshold (anchor=need) — the instance this atom was minted from |
| `L1.4n_weekday_weekend_null_ratio` | structural: its bound is an argument, not an external figure |
| `L1.5_max_multiplicity_share` | structural, as above |
| `L2.3_timing_diversity_periods` | no numeric threshold (anchor=need) — **the floor came out 2026-08-10, H34**, per this document's own disposition |
| `L2.3n_timing_diversity_null_ratio` | structural, as above — and see "why the repaired cell is not swept" below |

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
| L2.3_timing_diversity_periods | at_least | 10 | 0.5 | 0.4899 | 0.2677 | **+0.0101** | **same_order** † |
| L2.4_scale_spread_p90_p10 | at_least | 10 | 4.881 | 1.0 | 0 | +3.881 | separated \*\* |

† **This row is the 2026-08-09 reading and is now history.** The floor came out on
2026-08-10 (H34) and the cell left the swept set; the live sweep has no
`inside_null` and no `same_order` row at all. The row is kept because deleting the
measurement along with the band would leave the finding resting on prose — and it
is also kept as a TEST
(`test_band_null_sweep.py::test_a_shrinking_window_GROWS_the_sampling_null`
restores the band exactly as it was and re-measures it, so the finding has to keep
reproducing).

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

### L2.3_timing_diversity_periods — REPAIR THE STATISTIC — **DONE 2026-08-10 (H34)**

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

#### What was built, and what it measures

`L2.3_timing_diversity_periods` is now **reported, not judged** (`threshold=None`,
`anchor=NEED`, with the route back to a number named on the cell: a panel of
per-home half-hourly reads from which the PANEL's own null is computable at the
same window). `L2.3n_timing_diversity_null_ratio` judges in its place:
`timing_diversity` over the 95th percentile of the same statistic under 99
re-deals of the population's own days, so **1.0 is the decision point by
construction** — a one-sided permutation test at alpha = 0.05 — and there is
nothing in it to tune. The deal is `fabric_gap_ledger.deal_preserving_counts`,
which is the same function this sweep's `_exchangeable_homes_null` now calls: one
null, not a measured one and a judged one free to drift apart.

The threshold rule was fixed before the numbers, and the numbers are the point of
the repair — **the old floor's fail-open rate is a function of the window and the
ratio's is not** (applied panel, 40 independent structureless deals per window):

| window | timing-less population clears the **0.5 floor** | ...clears the **ratio** | real panel's ratio |
|---|---|---|---|
| 40 d | 65% | 7% | 1.656 |
| 60 d | 57% | 12% | 1.841 |
| 90 d | 15% | 7% | 2.111 |
| 120 d | 2% | 2% | 2.121 |

Both R15 directions hold at **every** window in 40–120 d: the real panel passes at
all four, a timing-less population fails at all four, and the shipped defect (one
national `HEATING_PERIOD_WEIGHTS` constant) makes the null itself degenerate —
every re-deal gives the same spread — which the statistic RAISES on and the cell
scores 0.0, a definitive violation rather than a skip.

#### Why the repaired cell is not itself swept, which was the atom's fourth exit

The atom asked for "band_null_sweep shows L2.3 SEPARATED at every window". It does
not, and no honest build could make it: `SEPARATED` compares the threshold with
the 95th percentile of the band's null, and L2.3n's threshold **is** the 95th
percentile of its null. Sweeping it would ask whether p95 ≥ p95 — R15's first
killer pattern, a value checked against the source it is derived from. A one-sided
test at alpha = 0.05 is *defined* to pass a structureless population about 1 time
in 20, so it can never separate from its own null; that is its size, not a
fail-open. What was delivered instead is stronger than the verdict word: the sweep
is now **clean at every window** — no `inside_null` and no `same_order` row exists
at all — and the property the verdict was a proxy for (how often does a
structureless population clear this control, and does that depend on the window)
is measured directly at each window in the table above. The same reasoning is why
`L1.4n` was already excluded.

### L1.1r_half_hourly_texture_resistive_heat — was UNMEASURABLE; **panel widened 2026-08-09 (H35)**

No home at the applied window was judged by this band: `tools/couple_fabric.py`'s
PANEL was 9 gas boilers and 1 air-source heat pump, with no resistive
(`electric_storage` / `electric_direct`) home at all. The band was carried and
never exercised — notable given it was derived *because* a storage-heater home
breached L1.1. Its null could not be measured on the load set it governs, and
measuring it on the gas panel would have been the wrong-load-set defect.

### L1.1e_half_hourly_texture_electric_heat — was one home, no estimable spread

Margin +0.0163 against a null of 0.0542, both from the single heat-pump home. The
verdict was a point estimate: `SAME_ORDER` was not reachable for this band at that
window, so `SEPARATED` meant "not obviously inside its null", not "clear of it".
Same disposition as L1.1r — widen the panel, then re-measure.

None of the three was dispositioned as a threshold move. L2.3 closed in H34; the
other two are atom `H35_the_panel_never_exercises_two_of_its_own_bands`, executed
below.

---

# H35 — the panel widened, and what the two unexercised bands actually read

**Atom:** `H35_the_panel_never_exercises_two_of_its_own_bands` (lane H_harness, L0 -> L2)
**Changed:** `tools/couple_fabric.py` PANEL, 10 homes -> 15 (9 gas, 3 heat pump, 3 resistive)
**Guard:** `background/band_null_sweep.FATAL_VERDICTS` / `fatal()`; runner exits 1 on UNMEASURABLE
**R15:** `tests/harness/test_band_null_sweep.py` §7, both directions

## What was added, and the one deliberate deviation from the atom's wording

Three air-source heat-pump homes (H10 as before, plus H11 a partially-insulated
1965-80 detached retrofit and H12 a post-2000 terrace on a monthly meter) and
three `ELECTRIC_DIRECT` panel-heater homes (E13, E14, E15). Regime and meter
cadence are varied independently, so "electric" and "read daily" cannot be
confounded.

**The atom asked for an `electric_storage` home and it did not get one, on
purpose.** The world layer does not model a storage heater:
`simulation/fabric_physics.py::_CONTROL_MODE` gives `ELECTRIC_STORAGE` the same
deadband thermostat as a gas combi, and `simulation/premise_trace.py` has no
charge window, no thermal store and no Economy-7 calendar
(`WORKER_FINDING_THE_MODELS_STORAGE_HEATER_IS_NOT_ONE`, owner atom `W1_12`). A
home labelled `electric_storage` would have been a panel heater wearing a storage
heater's register value, and L1.1r's null would then be reported as measured on a
load set half of which is a mislabel. `ELECTRIC_DIRECT` *is* a panel heater, and
L1.1r's own anchor covers "resistive (storage or panel)" — so the band is now
measured on the sub-regime the physics genuinely represents, and the storage
sub-regime stays **openly unexercised** until the storage-heater work lands rather
than being quietly claimed.

**The panel is a SPAN, not a sample**, and the widening makes that worth restating:
6 of 15 homes are electrically heated against ~9% of the GB stock. Representativeness
lives in `build_drawn_population` (raked onto published EHS marginals); the panel
exists so that every band the ledger carries is exercised by the run that judges it.

## The re-measurement (same window: 15 homes x 120 days)

| band | n before | n now | threshold | null (best) | null spread | margin | verdict |
|---|---|---|---|---|---|---|---|
| L1.1_half_hourly_texture | 9 | 9 | 0.15 | 0.0818 | 0.0432 | +0.0682 | separated |
| L1.1e_..._electric_heat | 1 | **3** | 0.0705 | 0.0695 | 0.0302 | **+0.0010** | **same_order** |
| L1.1r_..._resistive_heat | **0** | **3** | 0.0363 | 0.1228 | 0.0763 | **-0.0865** | **inside_null** |
| L1.2_day_to_day_shape_correlation | 10 | 15 | 0.85 | 1.0 | 0 | +0.15 | separated |
| L1.3_away_days_per_year | 10 | 15 | 1.0 | **120** | 120 | **-119** | **inside_null** |
| L2.1_smoothing_ratio | 10 | 15 | 0.85 | 1.0 | ~0 | +0.15 | separated |
| L2.2_between_home_correlation | 10 | 15 | 0.6 | 1.0 | 0 | +0.40 | separated |
| L2.4_scale_spread_p90_p10 | 10 | 15 | 4.881 | 1.0 | 0 | +3.881 | separated \*\* |

Both target bands are now MEASURABLE, and both are hits. A third band — L1.3,
clean at ten gas-ish homes — went `inside_null` on the same widening. That is the
finding underneath all three: **two of this ledger's statistics were only ever
valid for a home whose heat is on the other meter**, and nothing could say so
while the panel had no electrically-heated home to say it with.

## Dispositions — repair the statistic, in both cases (R12: never lower the floor)

### L1.1r and L1.1e — one fixed floor for every home size

Both electric bands are `0.15 x behavioural share`, where the share comes from ONE
published typical home (Ofgem TDCV medium against a DESNZ/ESC median-SPFH4 heat
pump = 47.0% behavioural; resistive = 24.2%). The panel's homes are not that home.
Measured heat share of own electricity, and the floor the band's OWN arithmetic
gives at each home's own share:

| home | regime | heat share | own-share floor | texture | fixed floor | fixed verdict |
|---|---|---|---|---|---|---|
| H10 | heat pump | 0.305 | 0.1043 | 0.1261 | 0.0705 | pass |
| H11 | heat pump | **0.624** | **0.0564** | **0.0704** | 0.0705 | **FAIL by 0.2%** |
| H12 | heat pump | 0.316 | 0.1026 | 0.1664 | 0.0705 | pass |
| E13 | resistive | 0.428 | 0.0858 | 0.1031 | 0.0363 | pass |
| E14 | resistive | 0.356 | 0.0966 | 0.1213 | 0.0363 | pass |
| E15 | resistive | 0.738 | 0.0393 | 0.0567 | 0.0363 | pass |

Every home clears the floor implied by its **own** behavioural share — H11 by 25%.
The number that does not fit is the band's assumed home, not the trace. In the
`at_most` direction the same fixed floor is far too LOW for the smaller resistive
homes, which is why a structureless resistive population clears 0.0363 easily and
the band lands inside its own null.

Which repair, per this document's own rule: the resistive population reads no
higher than its null (observed median 0.1031 against a null best of 0.1228), which
is the **statistic-has-no-discriminating-power** reading, not the threshold-too-low
one. For a heat-dominated home, `half_hourly_texture` is dominated by the
thermostat's own on/off blocks rather than by appliance events, so it cannot
separate a smooth-by-construction generator from a real home in that regime.

**Disposition: REPAIR THE STATISTIC** — atom
`H36_the_texture_floor_is_one_number_for_every_home_size`. Not a threshold move in
either direction: raising the floor until it clears its null would be fitting the
threshold to the population, which is R12 read backwards.

### L1.3 — the away-day signature reads a heat pump as an empty house

`away_signature` is mean active-window consumption over mean base-load
consumption, and a day scoring below 1.30 is counted as "demonstrably empty". A
heat pump runs THROUGH the base-load window, so its base load is not a base load:

* H11 is flagged away on **104 of 120 days** and H12 on 72 — on the REAL trace,
  with the household occupied every day. `observed-with-evidence`.
* Under the flat-day null every day becomes the home's own mean profile, whose
  active/base ratio for those two homes is below 1.30, so all 120 days are flagged
  and the null reads 120 away-days-per-home against a floor of 1.0.

The band therefore cannot fail on absence of the structure it certifies, and the
statistic is already mis-reading the live panel. `inferred`: the same will hold for
any continuously-heated electric home, including a correctly-modelled storage
heater, whose overnight charge block would make it worse.

**Disposition: REPAIR THE STATISTIC** — atom
`H37_the_away_signature_reads_a_heat_pump_as_an_empty_house`. The netting L1.2h
already applies (score the behavioural stream, not the meter total) is the obvious
candidate and is named as a candidate, not as the answer.

## The guard the atom asked for: an unexercised band FAILS the run

Before H35 the runner's exit code named `INSIDE_NULL` only, so `L1.1r` judging zero
homes produced a **clean exit 0 beside a green table** — the sweep reported the
state and nothing acted on it. `UNMEASURABLE` is now fatal
(`background.band_null_sweep.FATAL_VERDICTS`, read by the runner so the exit code
and the report cannot hold two ideas of what is bad), with the R15 pair in
`tests/harness/test_band_null_sweep.py` §7: a gas-only population makes the
heat-pump band fatal, one heat-pump home stops it being fatal for that reason, and
a measured-and-separated band leaves `fatal()` empty — a guard that could only ever
fire would be worth no more than a blind one.

`SAME_ORDER` stays non-fatal on purpose: it is a finding about distance from the
null with a real disposition, not a blind control.

## What this run now exits with, and why that is correct

> **Superseded in part, 2026-08-10 (H37).** L1.3 is no longer inside its null:
> the statistic was repaired as this section dispositioned, and the sweep now
> names L1.1r alone. The paragraph below is left as the reading of the run that
> produced the disposition — see the H37 section for the current one.

`python3 tools/band_null_sweep.py` exits **1** at HEAD, naming L1.1r and L1.3. The
live coupling run (`tools/couple_fabric.py`) reports **RED** on
`L1.1_half_hourly_texture` (worst home H11) and `L2.4_scale_spread_p90_p10`. Both
are recorded rather than edited away: the floor was not moved, H11 was not taken
off the panel, and no cell was marked UNVALIDATED — each of which would have gone
green in one line while making the measurement worse.


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

---

# H37 — the away-day signature, read where it is an occupancy statistic

**Atom:** `H37_the_away_signature_reads_a_heat_pump_as_an_empty_house` (lane H_harness, L0 -> L2)
**Changed:** `fabric_gap_ledger.trough_statistics` takes `space_heat=`; the L1.3 cell and the sweep both pass it
**New null:** `band_null_sweep._flat_behavioural_day_null`
**R15:** `tests/harness/test_premise_two_level.py` (H37 block), `tests/harness/test_band_null_sweep.py` (H37 block)

## The physics, which is the whole of the argument

`away_signature` is mean active-window consumption over mean **base-load**
consumption. It is an occupancy statistic only while the denominator is a base
load. A heat pump does not stop at midnight, so on the electricity meter of an
electrically-heated home the denominator is the thermostat and the ratio falls
towards 1.0 for a household that never left. Panel heaters make the mirror-image
error: off overnight and on when the room is used, they inflate the *numerator*
and hide an absence that did happen.

So the repair is not a new statistic and not a new number. It is the same
statistic read on the load set it was always about — the meter **net of space
heat**, the netting L1.2 already applies (`meter_net_of_space_heat`), passed in
rather than re-derived so the two cells cannot come to hold two ideas of what a
home's behaviour is. Where the generator supplies no split the whole meter is
judged, exactly as before: the leniency is bought with a stated, checked fact.

## The measurement, against each trace's own `is_away` calendar

Live panel, `tools/couple_fabric.PANEL`, 15 homes x 120 days. The harness may
read the generator's own occupancy truth here — measuring belief against truth is
what this ledger is for — but the **statistic** never does, or it would be a
tautology.

| stream | true away days | detected | false positives | recall | precision |
|---|---|---|---|---|---|
| electricity meter | 177 | 176 | 217 | 0.994 | 0.448 |
| net of space heat | 177 | **177** | **23** | **1.000** | **0.885** |

Per home, where the two disagree:

| home | regime | true | meter flagged | netted flagged |
|---|---|---|---|---|
| H10 | heat pump | 14 | 57 | **14** |
| H11 | heat pump | 26 | **104** | **26** |
| H12 | heat pump | 9 | 72 | 17 |
| E13 | resistive | 4 | 4 | 4 |
| E14 | resistive | 20 | 28 | 35 |
| E15 | resistive | 4 | 28 | **4** |
| nine gas homes | gas combi | 100 | 100 | 100 |

**Recall goes UP, not down.** That is the sentence the fail-closed worry turns on:
netting could in principle have made an empty house undetectable, and instead it
found the one true absence the meter had buried (E15, 0.75 -> 1.00) — because a
panel heater running in the active window is precisely what was hiding it. The
nine gas homes are bit-for-bit unchanged; a home whose heat is on the other meter
contributes a stream of zeros, and the test asserting that runs on the live
generator, not on the synthetic fixture.

**Two residuals, named rather than smoothed.** H12 still reads 8 false positives
and E14 reads 15 — more than the 8 it had on the meter. Netting fixes the
denominator; it does not make the behavioural stream of a small resistive home
noiseless, and the 1.30 cutoff is a threshold on a ratio, not a proof. The
honest reading is that this statistic is now confounded by ordinary quiet days
rather than by plumbing, at a rate (23 in 1,800 home-days) comparable with the
gas homes it was always trusted on. Moving 1.30 to clear them would be R12 read
backwards and was not done.

## Where the null had to move, and why the two shortcuts are both wrong

Once the band is READ net of space heat, its null has to be TAKEN there. The two
available shortcuts each inject the structure the null exists to remove:

* **flatten the meter, leave the heat stream** — the netted result is
  `flat_meter - real_heat`, which carries the heating machine's entire
  day-to-day structure with a minus sign in front of it. The null invents the
  absences the band looks for.
* **flatten both streams** — the netted day is `M_d*u_meter - H_d*u_heat`, whose
  shape moves with the ratio of the two daily totals. Less structure, but not
  none, and it appears on cold days: a null that puts a weather signal into a
  band about holidays.

`_flat_behavioural_day_null` takes the null where the reading is taken. Every
day's behavioural stream becomes that home's own mean behavioural profile at
that day's own behavioural total; the heating machine survives in full; the
meter is rebuilt as `flat_behavioural + heat`, so `meter_net_of_space_heat`
recovers exactly the flattened stream and the heat stream is still a genuine
component of the meter it is subtracted from. Where there is no split it degrades
to `_flat_day_null` **exactly**, and a test asserts the grids are equal rather
than similar.

## Re-swept at four windows (`bns.truncated`, the shipped helper)

| window | threshold | null (best) | null spread | margin | verdict | observed worst | observed median |
|---|---|---|---|---|---|---|---|
| 40d | 1.0 | 0 | 0 | +1.0 | separated | 0 | 3 |
| 60d | 1.0 | 0 | 0 | +1.0 | separated | 0 | 4 |
| 90d | 1.0 | 0 | 0 | +1.0 | separated | 0 | 4 |
| 120d | 1.0 | 0 | 0 | +1.0 | separated | 4 | 13 |

L1.3 is outside its null at every window — the null reads **zero** away days per
home, which is what "no absence is representable" should read. **The residual is
in the observed column, not the null:** at 40/60/90 days at least one home has
taken no holiday yet, so the live cell would fail that home. That is a property
of applying an annualised at-least band over a third of a year, it is unchanged
by this repair, and it is why the applied window is 120 days.

## What the sweep and the coupling run say now

`python3 tools/band_null_sweep.py --persist` exits **1**, naming
**L1.1r alone** (`docs/observability/band_null_sweep.json`, `randomisation:
flat_behavioural_day`, `margin: 1.0`, `verdict: separated` for L1.3). L1.1r stays
a defect and belongs to H36 — it was not touched here. `tools/couple_fabric.py`
reports RED on `L1.1_half_hourly_texture` and `L2.4_scale_spread_p90_p10`,
exactly as it did before H37; L1.3's cell now reads 0 of 15 homes violating,
worst home S3 at 12.18 away days per year against a floor of 1.0, with the note
carrying `away signature read net of space heat; 6 of 15 homes carry heat on the
judged meter`.

## R15, both ways

| direction | test |
|---|---|
| the defect is real and reproducible | `test_H37_the_DEFECT_is_reproduced_on_the_raw_meter` — a heat pump reads occupied-as-empty, panel heaters read empty-as-occupied |
| an occupied home is not called empty | `test_H37_an_OCCUPIED_home_is_not_called_empty_in_any_regime` |
| **fail-closed:** an empty home is still detected | `test_H37_a_genuinely_EMPTY_home_is_still_detected_in_any_regime`, all three regimes |
| the band can still fail | `test_H37_a_generator_with_no_absences_at_all_still_FAILS_the_band` |
| no split is the STRICT reading | `test_H37_no_split_supplied_judges_the_WHOLE_meter_fail_closed` |
| a gas home is untouched | `test_H37_a_gas_home_is_bit_for_bit_what_it_was`, on the live generator |
| the LEDGER reads the repaired stream | `test_H37_the_L1_3_CELL_reads_the_netted_stream_not_the_meter` |
| the sweep reads the same load set | `test_H37_the_sweep_reads_L1_3_on_the_SAME_load_set_the_ledger_judges` |
| **the null's own mutation** | `test_H37_taking_the_null_on_the_METER_puts_L1_3_back_INSIDE_it` — swap the behavioural null for the meter null and the verdict flips to `inside_null` |
| the null leaves the machine alone | `test_H37_the_behavioural_null_LEAVES_THE_HEATING_MACHINE_ALONE` |
| it degrades exactly, not approximately | `test_H37_the_behavioural_null_is_the_METER_null_where_there_is_no_split` |

The synthetic homes in the fgl tests are synthetic on purpose: the defect is a
property of the arithmetic, so it is named in arithmetic a reader can check by
hand rather than left resting on whichever regimes the panel happens to carry.
The two assertions that would go vacuous if the fixture drifted (the raw meter
and the netted read agreeing; the mutation no longer being a defect) both carry
an explicit message saying so.

## What was NOT done

* **R12 held.** `AWAY_SIGNATURE_MAX` is still 1.30 and L1.3's floor is still 1.0.
  The load set was wrong, not the number.
* **The non-positive-base branch was left alone.** `away_signature` returns `inf`
  when the base-load mean is not positive, so such a day can never be counted
  away. Netting makes that branch *less* plausible, not more: what is left after
  the heating machine comes out is the fridge, measured minimum 0.034 kWh per
  half hour over the panel. Recorded rather than pre-emptively rewritten.
* **L1.1r was not touched** (H36), and the sweep still exits 1 because of it.
* **`min_half_hour_kwh` stays on the meter**, unnetted — it is a statement about
  what the meter can read, not about occupancy.
