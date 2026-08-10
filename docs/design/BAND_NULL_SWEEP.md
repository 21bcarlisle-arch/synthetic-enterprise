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

> **Superseded 2026-08-10 (H36).** L1.1r no longer exists: the fixed floor was
> the defect, the statistic is read net of space heat and the sweep exits 0. The
> paragraph below is the reading of the run H37 produced.

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
* **L1.1r was not touched** (H36), and the sweep still exited 1 because of it.
  *Superseded 2026-08-10:* H36 retired L1.1r along with the whole regime-
  conditioned floor and the sweep now exits 0 — see the H36 section.
* **`min_half_hour_kwh` stays on the meter**, unnetted — it is a statement about
  what the meter can read, not about occupancy.

---

# H36 — one floor, read where the floor's own argument holds

**Atom:** `H36_the_texture_floor_is_one_number_for_every_home_size` (lane H_harness, L0 -> L2)
**Changed:** `half_hourly_texture` takes `space_heat=`; the L1.1 cell and the sweep both pass it
**Retired:** `L1.1e`, `L1.1r`, `heating_texture_threshold` and its two callers, `HEATING_REGIMES`
**Null moved to:** `band_null_sweep._flat_behavioural_day_null` (H37's, unchanged)
**R15:** `tests/harness/test_premise_two_level.py` §8, `tests/tools/test_couple_fabric.py`, `tests/harness/test_band_null_sweep.py`

## The argument, which is one sentence and then the evidence for it

L1.1 is `median |x[t] - x[t-1]| / mean(x)` and its 0.15 floor reasons entirely
about the DENOMINATOR — "a kettle is 2.8 kW for three minutes on a ~0.7 kWh
half-hour". Where the heating machine is on the judged meter that denominator is
not the one the argument is about, and the fix this replaces compensated in the
THRESHOLD: `0.15 x behavioural share`, with the share taken from ONE published
typical home (Ofgem TDCV medium against a DESNZ/ESC median-SPFH4 heat pump =
47.0% behavioural, resistive = 24.2%). One number, every home size.

The panel's homes are not that home. Measured behavioural share and what the
band's own arithmetic gives at each home's own share (the table H35 produced):

| home | regime | heat share | own-share floor | fixed floor | verdict under the fixed floor |
|---|---|---|---|---|---|
| H10 | heat pump | 0.305 | 0.1043 | 0.0705 | pass |
| H11 | heat pump | **0.624** | **0.0564** | 0.0705 | **FAIL by 0.2%** |
| H12 | heat pump | 0.316 | 0.1026 | 0.0705 | pass |
| E13 | resistive | 0.428 | 0.0858 | 0.0363 | pass |
| E14 | resistive | 0.356 | 0.0966 | 0.0363 | pass |
| E15 | resistive | 0.738 | 0.0393 | 0.0363 | pass |

25% too strict at one end. The other end is the one that matters.

## The fail-open, measured — why this is a STRENGTHENING and not a rescaling

Replace each home's behaviour with its own mean behavioural profile, rescaled to
that day's own behavioural total — level, diurnal shape and daily totals all
preserved, every appliance event gone — and leave the heating machine untouched.
That is the smooth-by-construction generator the floor exists to catch, in a
house that still has a real heat pump in it. Read on the WHOLE meter against the
rescaled floors that used to judge these homes:

| home | regime | mutated, whole meter | its old floor | old verdict | mutated, net of space heat | new verdict |
|---|---|---|---|---|---|---|
| H10 | heat pump | 0.0730 | 0.0705 | **PASS** | 0.0869 | fail |
| H11 | heat pump | 0.0415 | 0.0705 | fail | 0.0514 | fail |
| H12 | heat pump | 0.0814 | 0.0705 | **PASS** | 0.1094 | fail |
| E13 | resistive | 0.1137 | 0.0363 | **PASS** | 0.1334 | fail |
| E14 | resistive | 0.0693 | 0.0363 | **PASS** | 0.0932 | fail |
| E15 | resistive | 0.0407 | 0.0363 | **PASS** | 0.0665 | fail |

**Five of six.** The machine's own period-to-period movement stood in for the
behaviour that had been removed, and the rescaled floor was low enough to let it
— E13 cleared its band by 3x with no appliance event anywhere in 120 days. A
control that cannot fail on its own named defect is worse than none (R15), and
that is what the previous reading was for an electrically heated home. Pinned by
`test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home`.

## The repair, and what it deletes

The floor stops moving and the LOAD SET moves instead — the netting L1.2 (and,
since H37, L1.3) already apply. `half_hourly_texture(space_heat=...)` reads the
meter net of space heat; the cell computes the behavioural stream ONCE and hands
the same one to all three L1 cells, so they cannot come to hold two ideas of what
a home's behaviour is.

What that DELETES is the point, and it is an R10 class closure rather than an
instance fix: there is no per-regime threshold, no published seasonal efficiency
for any machine, and no NEED band for a ground-source heat pump — a machine this
file has never heard of is judged like every other one, because the split takes
it out whatever its efficiency is. The heating register survives with one job
left: deciding whether a home with NO split has a meter that is already
behavioural, or a thermostat in it that cannot be taken out. The second case is
COUNTED, never judged (`L1.1u_half_hourly_texture_no_behavioural_stream`), which
is the same visible-hole treatment the unregistered-regime band had.

## The panel, re-read (15 homes x 120 days, same window)

| home | regime | whole meter | net of space heat | vs 0.15 |
|---|---|---|---|---|
| nine gas homes | gas combi | 0.1782-0.2874 | **bit-for-bit unchanged** | pass |
| H10 | heat pump | 0.1261 | 0.1766 | pass |
| H11 | heat pump | **0.0704** | **0.1537** | pass |
| H12 | heat pump | 0.1664 | 0.2452 | pass |
| E13 | resistive | 0.1031 | 0.1618 | pass |
| E14 | resistive | 0.1213 | 0.1655 | pass |
| E15 | resistive | 0.0567 | 0.1533 | pass |

Every home now reads in one comparable range (0.1533-0.2874) against one floor.
The gas homes are unchanged because their heat is on the other meter and the
netting is the identity on them — asserted on the live panel, not argued.

**H11's breach is closed and the floor did not move.** `tools/couple_fabric.py`
reports RED on `L2.4_scale_spread_p90_p10` alone; L1.1's cell reads 0 of 15
violating, worst home E15 at 0.1533, verdict INSUFFICIENT — fifteen homes cannot
rule out a 5% violation rate. The breach is gone; the power was never there.

## The sweep

`python3 tools/band_null_sweep.py` now exits **0**. L1.1r's `inside_null` and
L1.1e's `same_order` are gone with the bands; the surviving floor is measured
over all 15 homes on the load set it is read on:

| band | n | threshold | null (best) | null spread | margin | verdict |
|---|---|---|---|---|---|---|
| L1.1_half_hourly_texture | 15 | 0.15 | 0.1166 | 0.0763 | **+0.0334** | **same_order** |

`SAME_ORDER` is a FINDING, not a defect, and it is dispositioned below rather
than left as a colour in a table.

## Two findings this opened, both named and neither folded in

### 1. The behavioural stream still carries the WATER heater

On the drawn 60-home population (the one the ledger's judged verdict comes from,
not the panel) the sharper cell puts **one home in sixty** under the floor:
P0008 at 0.1423. Decomposed:

| home | regime | whole meter | net of space heat | net of BOTH machines | water heat as a share of "behaviour" |
|---|---|---|---|---|---|
| P0008 | resistive | 0.1382 | **0.1423** | 0.2048 | 0.403 |
| P0020 | resistive | 0.1228 | 0.1526 | 0.2177 | 0.357 |
| P0033 | storage | 0.0378 | 0.1653 | 0.2434 | 0.387 |

The same wrong-load-set shape one level in. Taking the space heater out leaves
the water heater, which is 36-40% of what is left, and it is a MACHINE rather
than an appliance event: a large regular draw that lifts the MEAN while the
MEDIAN step barely moves — the exact numerator/denominator argument that forced
the space-heat netting. Net of both, all three read 0.2048-0.2434.

`observed-with-evidence`, on the live generator, and the floor was NOT moved,
P0008 was NOT excluded and no cell was marked UNVALIDATED — each would go green
in one edit while making the measurement worse. **Disposition: REPAIR THE
STATISTIC** — atom `H38_the_behavioural_stream_still_carries_the_water_heater`.
Until it lands the cell reports FAIL, which is the correct reading of a control
asking a home about a machine. Held by
`test_the_L1_1_BREACH_is_the_WATER_HEATER_in_the_denominator`.

### 2. The floor sits inside the spread of its own null

The surviving band clears its null by 0.0334 against a spread of 0.0763 —
separated by the draw, not by construction. `inferred`: the flat-day null
preserves each home's mean diurnal profile, and the statistic then reads that
profile's own roughness, which is a property of the home rather than of the
generator's honesty — so the null's spread ACROSS homes is large and the p95 is
set by whichever home has the peakiest mean profile (E13 at 0.1334 against a
population median near 0.06). **Disposition: REPAIR THE STATISTIC** — atom
`H39_the_texture_floor_sits_inside_the_spread_of_its_own_null`, with the
`L1.4 -> L1.4n` / `L2.3 -> L2.3n` own-null-ratio pattern named as the candidate
and NOT as the answer. Not a threshold move in either direction: raising the
floor until it clears its null is fitting the threshold to the population, which
is R12 read backwards.

## R15, both ways

| direction | test |
|---|---|
| **the old reading was fail-open** | `test_the_OLD_WHOLE_METER_reading_was_FAIL_OPEN_on_a_BEHAVIOURALLY_FLAT_home` — 5 of 6 homes passed with every appliance event removed |
| the floor can still fail, every regime | `test_the_MUTATION_that_proves_the_floor_is_VALID_on_EVERY_regime`, five machines |
| the mutation attacks BEHAVIOUR, not the machine | `_flatten_behaviour` rebuilds the meter with the heat stream intact |
| there is only ONE judged floor | `test_the_FLOOR_is_ONE_NUMBER_and_no_regime_has_its_own`, which also asserts the retired derivations are gone |
| the floor does not move with heat share | `test_the_floor_does_not_move_with_a_homes_HEAT_SHARE` |
| a gas home is untouched | `test_the_TEXTURE_CELL_BREACH_CLOSED_when_the_LOAD_SET_WAS_REPAIRED` (d), on the live panel |
| **the closure control still fires** | `test_the_CLOSURE_CONTROL_still_fires_when_the_JUDGING_BAND_IS_MOVED` — floor raised to 0.20, real homes breach, control raises |
| ...and accepts the real cell | `test_the_CLOSURE_CONTROL_accepts_a_clearing_cell_and_REJECTS_a_sub_floor_one`, pass arm now measured rather than constructed |
| the register still fails CLOSED | `test_the_MISSING_register_fact_still_fails_CLOSED_onto_the_gas_band`, `test_an_UNKNOWN_machine_fails_CLOSED_rather_than_onto_the_floor` |
| an unjudgeable home is COUNTED | `test_a_home_with_NO_RECOVERABLE_behaviour_is_COUNTED_never_folded_in` |
| ...and a population of them is INSUFFICIENT | `test_a_population_MOSTLY_unjudgeable_is_INSUFFICIENT_not_clean`, `..._with_NO_judgeable_band_at_all_...` |
| every machine is classified (R10) | `test_EVERY_heating_system_is_registered_or_explicitly_UNANCHORED` |
| the unjudged home cannot become the worst cell | `test_the_worst_L1_1_cell_is_the_worst_MARGIN_not_the_lowest_RAW_value` |
| the sweep reads the same load set | `test_the_floor_is_read_NET_OF_SPACE_HEAT_and_so_is_its_null`, both directions |
| **the vacuity guard survives the collapse** | `test_a_band_that_judges_NO_HOME_is_FATAL_and_not_merely_reported` + `test_the_SAME_band_stops_being_fatal_once_a_home_EXERCISES_it` — re-aimed at the population that now empties the floor's load set |

The H35 guard (`UNMEASURABLE` is fatal) is kept live rather than orphaned: with
the regime bands gone, the population that empties the floor's load set is one
where every home carries its heat on the judged meter and no split is supplied,
and both the fires-on-it and stops-firing arms are asserted on that.

## What was NOT done

* **R12 held.** The floor is still 0.15 — the gas number this cell was born with.
  Nothing was raised to clear a null and nothing was lowered to clear a home.
* **The water-heater netting was not folded in.** It is a second application of
  the same repair with its own measurement to take, and doing it inside this one
  would have made both unreviewable. Atom `H38`, evidence already in hand.
* **The panel was not trimmed and P0008 was not dropped.** The one open breach is
  reported at the cell, on the wire (`homes_violating`, `worst_home`), and in the
  test that decomposes it.
* **`_smooth` was left in place.** It inverts on a heat-pump home's METER and no
  longer does on its behavioural stream; that reversal is now an assertion
  (`test_the_SMOOTH_mutation_is_VALID_AGAIN_once_the_MACHINE_IS_OUT`) rather than
  a deleted comment, because it is evidence that the statistic measures the same
  thing in both regimes now.
* **`docs/market_research/ASSUMPTIONS.md` kept its rows.** The SPFH4 and in-situ
  boiler research is real and correctly sourced; it is marked as no longer
  anchoring a live control rather than deleted, because the 53.0% derived share is
  what made the fixed-floor defect visible in the first place.

---

# H38 — the second machine, and a floor that finally asks every home the same question

**Atom:** `H38_the_behavioural_stream_still_carries_the_water_heater` (lane H_harness, L0 -> L2)
**Changed:** `machine_draw` composes space + water heat into the ONE stream the L1 cells net out
**Renamed:** `meter_net_of_space_heat` -> `meter_net_of_machines`; the `space_heat=` kwarg -> `machines=`
**Added:** `PopulationTraces.water_heat_grids`, filled from the trace's own `dhw_fuel_kwh`
**R15:** `tests/harness/test_premise_two_level.py` (four new arms), `tests/harness/test_band_null_sweep.py`, `tests/tools/test_couple_fabric.py`

## What was open, and what it turned out to be

H36 left one home in sixty under the floor — P0008 at 0.1423 against 0.15 — and
named the cause without fixing it: what is left after the space heater comes out
is the WATER heater, 36-40% of what the cell then calls behaviour.

The first thing to check was whether that was a fail-open. It is not, and saying
so matters because it changes what the repair has to prove. Replace a home's
behaviour with its own flat daily mean, leave both machines standing, and the
cell fires under BOTH readings (texture 0.0000 either way): three 12-minute
draws a day move six steps in 47, and this statistic's numerator is a MEDIAN,
which is exactly robust to that. **The water heater was never supplying texture.
It was supplying DENOMINATOR** — ~38% more mean, against a floor derived where it
was absent.

Absent where? The 0.15 anchor reasons from a gas-heated home's electricity meter,
and a gas-heated home heats its water with gas. The anchor population never
carried this load at all.

## The measurement that decides it

Raw values across regimes are not comparable, so this is measured in H36's unit:
how much of its own behaviour a home must lose before the cell fires. Drawn 60,
`base_seed=17`, real Open-Meteo 2022-01-01..2022-04-30.

| homes | net of space heat | net of BOTH machines |
|---|---|---|
| 57 gas homes (median) | 0.3066 | **0.3066 — identical** |
| P0008 electric_direct | 0.0000 | 0.2721 |
| P0020 electric_direct | 0.0168 | 0.3119 |
| P0033 electric_storage | 0.0914 | 0.3892 |

An electrically heated home was firing at **1.7% breakage where a gas home needed
31%** — an 18x gap — and P0008 at 0.0000 was already under the floor with nothing
done to it at all. Net of both machines the three land astride the gas median.

**The gas column is the control and it could not have been tuned toward.** It is
bit-for-bit identical under both readings, because a gas home's cylinder is on
the other meter. That is what makes this a load-set repair rather than a
loosening, and it is asserted both ways — an electric home that became HARDER to
fail than a gas home would trip
`test_the_WATER_HEATER_netting_is_a_LOAD_SET_repair_and_not_a_LOOSENING`.

## Honest about the direction

Netting space heat was a STRENGTHENING and could be proven as one. **This is not.**
Every affected reading moves UP (0.1423 -> 0.2048) and the affected homes get
easier to pass. The claim is not "stricter" — it is *parity with the population
whose meters derived the floor*, and it is measured rather than argued. R12
holds: the floor is still 0.15, the gas number this cell was born with.

## Why all three L1 cells and not just L1.1

H36's invariant is that the behavioural stream is computed ONCE and handed to
L1.1, L1.2 and L1.3, because two cells deriving "this home's behaviour"
separately is how they come to hold two ideas of it. Netting the water heater
from L1.1 alone would have bought exactly that defect. So the other two were
MEASURED rather than assumed:

| cell | net of space heat | net of BOTH | verdict |
|---|---|---|---|
| L1.2 shape correlation (median / worst / violating) | 0.2104 / 0.4386 / 0 | 0.2143 / 0.4386 / 0 | no material change |
| L1.3 away detection (detected / false pos / recall) | 849 / 8 / 1.000 | 849 / **0** / 1.000 | strictly better |

L1.3 was the surprise. The prior was that a hot-water draw is an EVENT on the
household's own clock, so netting it should cost recall. It does not, and the
mechanism is H37's exactly, one machine over: the away signature DIVIDES BY the
00:00-06:00 base-load window, and an early-rising household draws hot water
inside it. Day 68 on P0008 is the clean case — 1.674 kWh of water heat in the
base window, 0.000 in the active window — and the ratio falls 4.17 -> 1.15, under
the 1.30 threshold, on a day nobody left. All 8 false positives are that shape.
Recall does not move because a water heater draws nothing on an away day, so the
netting is the identity on precisely the days L1.3 exists to find.

## The panel and the population, re-read

`L1.1` on the drawn 60: **0 of 60 violating, verdict PASS**, and the worst home is
now **P0036, a GAS home, at 0.1521**. That is the tell that this was a load-set
repair: after it, the marginal home in the population is one the netting is the
identity on. The panel says the same — worst home D7 (gas) at 0.1782, where H36
left E15 (resistive) at 0.1533.

**A prediction H36 wrote down was paid off on a row it deliberately left red.**
H36 recorded ED1, the panel heater, at 0.1313 — not clearing 0.15 — and said its
whole deficit was the water heater. ED1 now reads 0.2050. The diagnosis was made
before the repair and it held.

## The sweep

`python3 tools/band_null_sweep.py` still exits **0**, and L1.1 improved without
being touched:

| band | n | threshold | null (best) | null spread | margin | verdict |
|---|---|---|---|---|---|---|
| L1.1 (H36) | 15 | 0.15 | 0.1166 | 0.0763 | +0.0334 | same_order |
| L1.1 (H38) | 15 | 0.15 | 0.0950 | 0.0558 | **+0.0550** | same_order |

Margin-to-spread goes 0.44 -> 0.99. **H39 is NOT closed** — the band still sits
inside its own null's spread, which is a separate defect with a separate repair,
and this is a note that its numbers moved, not that it went away.

## A stale docstring that mattered

`PremiseDayTrace.behavioural_electricity_kwh` claimed to be "appliances +
lighting + electronics + base load + **electric DHW**". It is not and never was:
on P0008, meter 17.8475 = behavioural 9.8144 + dhw 6.2700 + space heat 1.7630,
exactly. Corrected, because a reader checking this atom's netting against that
line would have concluded it double-counts.

## What was NOT done

* **The floor did not move.** Still 0.15.
* **Nobody was excluded.** All 60 homes judged on every anchored cell.
* **H39 was not folded in.** The band still clears its null by less than the
  null's own spread; that is its own atom and its own measurement.
* **The netting is not claimed to be complete.** EV charging is also on the judged
  meter of some homes and is also not an appliance event. Nothing here measured
  it, so nothing here says anything about it — the drawn 60 has no EV home under
  the floor, which is an absence of evidence and not a clearance.
* **`_flatten_blend` was kept** even though `_smooth` is a valid mutation again
  once both machines are out. It attacks the defect this cell is really about;
  the reversal is recorded as an assertion rather than used as a reason to delete.


# H39 — the floor's null is a property of the HOME, and this takes it out

**Atom:** `H39_the_texture_floor_sits_inside_the_spread_of_its_own_null` (lane H_harness, L0 -> L2)
**Added:** `fabric_gap_ledger.flatten_to_mean_profile`, `half_hourly_texture_vs_own_null`, band + rate band `L1.1n_half_hourly_texture_null_ratio`, an L1.1n cell in `evaluate_two_level`
**Moved, not copied:** the sweep's `_flatten_home` is now a call into the ledger's kernel — one flattening, since it became the denominator of a JUDGED band
**Unchanged:** the 0.15 floor, its anchor, its load set, and every home it judges
**R15:** `tests/harness/test_premise_two_level.py` §9b, four mutations, each shown firing

## The argument, which is one sentence and then the evidence for it

`half_hourly_texture` is `median |x[t] - x[t-1]| / mean(x)`, and a home's own mean
diurnal profile *already moves between adjacent half-hours* — the morning ramp and
the evening fall are period-to-period steps that are there whether or not the
generator ever fired an appliance. So the reading a structureless generator gets
is not zero, and it is not the same number for every home. Measured on the live
panel with every appliance event removed and the heating machines left intact:

| home | regime | observed | its own flat reading | ratio |
|---|---|---|---|---|
| F1 | gas combi | 0.2437 | 0.0606 | 4.02 |
| T2 | gas combi | 0.2187 | 0.0432 | 5.06 |
| S3 | gas combi | 0.2141 | **0.0365** | **5.87** |
| D4 | gas combi | 0.2002 | 0.0437 | 4.58 |
| T5 | gas combi | 0.2390 | 0.0925 | **2.59** |
| S6 | gas combi | 0.2102 | 0.0552 | 3.81 |
| D7 | gas combi | 0.1782 | 0.0659 | 2.70 |
| F8 | gas combi | 0.2874 | 0.0553 | 5.20 |
| S9 | gas combi | 0.1859 | 0.0419 | 4.44 |
| H10 | heat pump | 0.2155 | 0.0474 | 4.55 |
| H11 | heat pump | 0.1959 | 0.0403 | 4.86 |
| H12 | heat pump | 0.2674 | **0.1009** | 2.65 |
| E13 | resistive | 0.2438 | 0.0546 | 4.46 |
| E14 | resistive | 0.2407 | 0.0658 | 3.66 |
| E15 | resistive | 0.2205 | 0.0496 | 4.45 |

**2.8x across the panel, 3.5x across the drawn 60** (0.0292–0.1035, which is 19%
to 69% of the floor). One floor is therefore asking S3 to manufacture 0.113 out of
appliance events and H12 to manufacture 0.049 — and neither number is about how
honest the generator was.

## The mint's stated mechanism was WRONG, and the correction is the first result

H39 was minted with an explicitly `inferred`-labelled cause: *"the p95 is set by
whichever home has the peakiest mean profile"*. It is not, and the label was doing
its job — measured across the panel, the flat reading is essentially uncorrelated
with the mean profile's peak-to-mean (**r = −0.052**), and the two extremes are
the wrong way round: H12 has the panel's *second-lowest* peak-to-mean (2.264,
against a 2.203–2.731 range) and the *highest* flat reading, while H11 has the
highest peak-to-mean and the second-lowest reading.

Sharpening a profile's peak does not raise the statistic — it lowers it. Taking
the panel's own mean behavioural shape and raising it to a power to sharpen the
peak, applied to every home as one national profile:

| peak-to-mean | 2.24 | 2.90 | 3.53 | 4.09 | 4.59 | 5.02 | 5.42 |
|---|---|---|---|---|---|---|---|
| median flat reading | 0.0402 | 0.0401 | 0.0352 | 0.0312 | 0.0271 | 0.0219 | 0.0163 |

A tall peak is still smooth *between adjacent half-hours*, which is the only thing
this statistic reads. The driver is the mean profile's period-to-period
**roughness**, and what makes one home's mean rough is not settled here: it
correlates weakly and negatively with the home's behavioural level (r = −0.377,
n = 15 — reported as weak, not as a finding). **The defect is real and the repair
is unchanged; the stated cause was wrong**, and a wrong cause left standing is how
the next repair gets aimed at the wrong thing. Pinned by
`test_the_MINTS_INFERRED_MECHANISM_was_REFUTED_by_measurement`.

## The fail-open, measured — a generator the floor cannot see

The floor's own rationale says what it is for: *"a rescaled national average has
the texture of a national average, which is the texture of a hundred thousand
homes already summed"* — i.e. it assumes the fake shape is **smooth**. A more
convincing fake is not. Take **one real day from one real home** and use it as
every home's base shape, rescaled to each home-day's own real total: zero
day-to-day behaviour anywhere in the population, which is exactly what L1.1
certifies.

| band | reading on that generator | verdict |
|---|---|---|
| `L1.1` (at_least 0.15) | 0.1890 – 0.1923, all 15 homes | **PASS, 15 of 15** |
| `L1.1n` (at_least 1.0) | 1.0 to within 4e-16, all 15 homes | FAIL, 15 of 15 |

**Said out loud, because overselling this would be the easy mistake:** `L1.2`
(day-to-day shape correlation reads exactly 1.0) and `L1.5` (multiplicity share
2.0 against a 0.10 band) also fail this generator, so the CELL was never blind to
it. The claim is about **L1.1's own null**, which is the quantity this sweep
measures band by band and the quantity H39 is about. Pinned by
`test_L1_1n_FIRES_on_the_RESCALED_REAL_DAY_that_the_FLOOR_CANNOT_SEE`.

The defect cuts the other way too. On the drawn 60 the home closest to the floor
is P0036 at **0.1521 — 1.4% clear of firing** — while reading **4.26x** its own
flat counterfactual; the home closest to its *own* null (P0031, 2.14x) reads
0.1750 and is nowhere near the floor. The floor's ranking of those two homes and
the evidence's ranking disagree.

## The window evidence, which is what decides "repair the statistic"

This module's disposition rule has two branches. Neither describes L1.1, and that
is itself the diagnosis:

| window | null (best) | null spread | observed median | margin | verdict |
|---|---|---|---|---|---|
| 40 d | 0.1138 | 0.0517 | 0.2155 | +0.0362 | same_order |
| 60 d | 0.1124 | 0.0720 | 0.2090 | +0.0376 | same_order |
| 90 d | 0.0846 | 0.0443 | 0.2120 | +0.0654 | **separated** |
| 120 d | 0.0950 | 0.0558 | 0.2187 | +0.0550 | same_order |

The null does **not shrink with the window** — it wanders, and the verdict wanders
with it, flipping to `separated` at 90 days and back at 120 while the observed
value never moves. A *sampling* null shrinks with n (that is L2.3's shape, and it
is why L2.3 was repaired to a ratio). This one does not, because it is not a
sampling term at all: it is a **per-home constant**, estimated on whichever days
the window happens to contain. Repairing the WINDOW is therefore not available —
there is no window at which this null is small — and the statistic is what has to
change.

## The repair, and why it is not a threshold move in either direction

`L1.1n_half_hourly_texture_null_ratio` = `half_hourly_texture` on the home,
divided by `half_hourly_texture` on the **same home flattened**: every day's
behavioural stream replaced by that home's own mean behavioural profile, rescaled
to that day's own behavioural total. Level, diurnal shape and daily totals all
survive; appliance events do not. **1.0 is the decision point by construction** —
the flattening is idempotent, so a structureless population reads exactly 1.0 —
and there is nothing in it to tune. The number reads as *"this home's meter is N
times rougher than its own smooth counterfactual"*.

**The null is a POINT MASS, and that is the difference from `L1.4n` and `L2.3n`.**
Those are 99-sample permutation nulls, so their 1.0 is a 95th percentile and a
structureless subject clears them 1 time in 20 — their size, not a fail-open,
which is why `L1.4n` needed a 0.50 population tolerance. Here the counterfactual
is deterministic, a structureless home reads 1.0 with no spread at all, and no
sampling puts a home with any behaviour under it. So the rate band is the
**impossibility bound, 0.0**.

### The 1e-9 is float error, and it is load-bearing

The two readings are the same arithmetic in a different order, so a structureless
home lands at 1.0 ± a few units in the last place. On the panel's own flat null,
**5 of 15 homes land ABOVE 1.0**, by up to 2.4e-15. A band written `at_least 1.0`
would therefore have passed a third of a smooth-by-construction population — the
exact defect it exists to fail. `TEXTURE_NULL_RATIO_TOLERANCE = 1e-9` is sized
against float error, never against where the population sits: the smallest real
margin measured anywhere is 1.14 (P0031, ratio 2.14), nine orders clear of it.
Zeroing the constant makes two tests fail; that is the mutation, and it is run.

### The floor did not move, and it is still judged

R12 in both directions. `L1.1` keeps 0.15, keeps its domain anchor, and keeps
every home it judges — it answers the **magnitude** question ("is this as textured
as a real household?"), which has an external argument behind it. `L1.1n` answers
the **significance** question ("is any of this texture behaviour rather than
shape?"), which has a construction behind it. They are separate cells for the
reason `L1.4`/`L1.4n` already are: collapsing them into one name would be one name
carrying two numbers. Raising 0.15 until it cleared its null, or retiring it
because the sweep flagged it, would each have been fitting the number to the
population.

### Why the L1.1 row is still `same_order`, and why no honest build could change that

`SEPARATED` compares the threshold with the 95th percentile of the band's null
**across homes**, and L1.1's null across homes is irreducibly wide because it is a
property of the homes. Nothing that leaves 0.15 in place can turn that row green,
and `L1.1n` is not swept either — its threshold **is** its null, so sweeping it
would ask whether 1.0 ≥ 1.0, R15's first killer pattern (`anchored_bands()`
excludes it automatically as `STRUCTURAL`, the same door `L1.4n` and `L2.3n` go
through). What is delivered instead of a colour change is the property the verdict
was a proxy for, measured directly: **a population with no day-to-day behaviour in
it now fails a judged band of this cell, at every home, whatever its profile looks
like.**

## R15, both ways

| direction | test |
|---|---|
| **the floor is fail-open on a rescaled real day** | `test_L1_1n_FIRES_on_the_RESCALED_REAL_DAY_that_the_FLOOR_CANNOT_SEE` — floor passes 15/15, L1.1n fails 15/15 |
| the band can PASS, on the real drawn 60 | `test_L1_1n_CAN_PASS_and_is_not_a_control_that_can_only_fail` — 0 violations, worst home 2.14x |
| the null is ONE number where the floor's is not | `test_the_NULL_is_ONE_NUMBER_for_every_home_where_the_FLOORs_is_NOT` |
| the tolerance is load-bearing | `test_the_TOLERANCE_is_LOAD_BEARING_and_at_least_1_0_would_be_FAIL_OPEN` |
| the decision point is exact | `test_the_FLAT_COUNTERFACTUAL_is_IDEMPOTENT_which_is_what_makes_1_0_EXACT` |
| one flattening, not two | `test_the_FLATTENING_is_the_LEDGERS_and_the_SWEEP_keeps_no_second_copy` — AST, not substring: this module's docstring names the function, so a text match would have passed an inlined copy |
| a degenerate null RAISES | `test_L1_1n_FAILS_CLOSED_rather_than_returning_a_spectacular_pass` |
| ...and the cell scores it a VIOLATION | `test_L1_1n_scores_a_DEGENERATE_home_as_a_VIOLATION_not_as_a_pass` |
| the machine is netted BEFORE the flattening | `test_L1_1n_NETS_THE_MACHINE_BEFORE_it_flattens` — the wrong order reads a null of 0.2092 against the right one's 0.0724 |
| the mint's stated cause was refuted | `test_the_MINTS_INFERRED_MECHANISM_was_REFUTED_by_measurement` |
| the floor is still ONE number and no regime has its own | `test_the_FLOOR_is_ONE_NUMBER_and_no_regime_has_its_own` — widened to assert `texture_band_for` can never route a home to `L1.1n` |

**The four mutations, each run and each shown firing:** tolerance → 0.0 (2 tests
fail); flattening keeps 1% of the real day, so it is no longer a null (3 fail);
flatten-the-meter-then-net, which is H36's defect coming back in through the null
(1 fail); the sweep inlines its own copy of the flattening (1 fail).

## What was NOT done

* **The floor did not move.** Still 0.15, still judged, still every home.
* **Nobody was excluded**, and no cell was marked UNVALIDATED.
* **The MAGNITUDE question is still open** and is still where it was: the
  SERL/LCL published per-home half-hourly band is not in the artefact library, so
  nothing here says whether a real household reads 2x or 5x its own flat
  counterfactual. The route back is named on the band — a panel of real per-home
  half-hourly reads, from which the ratio's real-home distribution is computable
  **at the window it is applied at**.
* **What makes one home's mean profile rough is not diagnosed.** The correlation
  with behavioural level (−0.377, n=15) is reported as weak and is not a finding.
* **EV charging is still unmeasured**, as H38 recorded — carried forward, not
  closed.
* **`docs/observability/band_null_sweep.json` was stale** (it carried H38's
  pre-repair 0.0334/0.0763) and was regenerated here. Noted rather than folded in:
  a derived artefact that lags its generator is its own class, already on the
  register.
