# FRAME — EP16_anchored_generators: one of the four axes is generated forward, and the curriculum wall guards a rotation set of zero

**Atom:** `EP16_anchored_generators` (lane `W1_market_weather`, epoch 4, `level_current: 0` → `level_target: 3`,
`loop_stage: idle`, `provenance: director_ruling`, `block_reason:` director-reserved curriculum sequencing R13).
**Pass:** DISCOVER/FRAME only, worker tick 2026-08-17, LANE 3 idle draw. **No BUILD code written**; `file_scope` is `[]`
and nothing outside this doc + the atom's own store record was touched. EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1 makes
DISCOVER/FRAME available on a parked atom while BUILD is not.

**Measured at HEAD `78d4f46f5`.** `docs/design/maturity_map.yaml`, the atom's store file and `docs/design/frame/` were
all clean in the shared tree at draw time, so every number below was read off the desk tree directly. Every claim is
`observed-with-evidence` unless labelled `inferred` (R9).

---

## 0. The question this pass had to answer first

The atom's own name records a duplicate-risk check at mint: *"W1_2_generate_futures (SATURATED) generates forward
CURVES; this is the whole-world generator with its anchoring discipline."* Two knobs that only ever appear as a
difference are one knob, so the first job was to test that separation rather than inherit it.

**It survives, and it is larger than the name implies.** W1_2 is not merely "curves" — it is a regime-switching
Markov price generator plus a coupled gas generator, wired end-to-end through the full replay pipeline, with an
R15-hardened six-moment fidelity check behind it. That work is real and this pass does not re-open it. What EP16 names
is genuinely absent: of the **four axes the atom lists — weather, price, demand, population — exactly one is generated
forward.** The other three are frozen, silently absent, or another atom's.

And the *discipline* half of the atom's name — "stay tethered", "director-authored curriculum" — turns out to be
mechanised over a population of **zero worlds**, while the five worlds that actually generate futures are unwalled.

---

## 1. FINDING 1 — the forward world is prices; the other three axes do not move

`simulation/run_scenario.py::run_forward_scenario` is the whole-world entry point. What it actually extends is two
feeds: `build_extended_price_feeds()` returns `(extended_elec, extended_gas)` — electricity half-hourly SSP and daily
NBP gas — and injects them into `run_phase2b.main()` by monkey-patching the two price loaders
(`_cache.get_cached_prices`, `_gas_mod.load_nbp_history`). Nothing else about the world is generated.

| axis named in the atom | forward generator | status at HEAD |
|---|---|---|
| **price** (elec + gas) | `sim/scenario/bimodal_generator.py`, `gas_scenario_generator.py` | **generated** — regime-switching, 5 presets, wired |
| **weather** | `sim/weather_engine.py` (fitted, real) | **exists but has no forward caller** — §3 |
| **demand** | — | **no generator**; follows weather, so it goes flat — §3 |
| **population** | `simulation/population_draw.py` | **pinned to one cast**; EP17's subject, not EP16's |

The weather generator is the sharp case, because it is *built and anchored*: `fit_national_macro_model` /
`simulate_national_macro` / `fit_regional_cholesky` / `simulate_regional_deviations` fit seasonal harmonics and a
season-switched innovation covariance to the real 2016-2025 panel and simulate new draws from it — precisely the
"synthetic but externally-calibrated" shape this atom asks for. Its non-test callers are
`simulation/run_phase3c_calibration.py` (a calibration study) and `sim/weather_tail_demonstration.py` (a
demonstration). **Neither writes weather for a forward scenario, and `run_scenario.py` never imports the weather
engine at all** (grep for `simulate_national_macro|fit_national_macro_model|simulate_regional_deviations` outside
`sim/weather_engine.py`).

So the mechanism EP16 would need on its second axis already exists to a high standard, one caller short of the world.

## 2. FINDING 2 — the renewable fleet is silently frozen at 2025 in every generated future

`sim/renewable_capacity_trend.py` (W1_7) is the atom's own best example of anchoring done right: the effective fleet
scalar for each calendar year τ is *mean-matched to that year's real observed outturn*, with the DUKES/DESNZ installed
capacity series ingested to separate capacity from load factor. It is honest about its residual and its limits in its
own header. Inside the fitted window it is exactly the discipline EP16 exists to generalise.

Outside that window it stops, and does not say so:

| year | `capacity_wind(y)` | `capacity_solar(y)` |
|---|---|---|
| 2016 | 97,724.18 | 13,132.41 |
| 2020 | 96,216.03 | 11,844.90 |
| 2025 | 137,740.71 | 15,417.49 |
| **2026** | **137,740.71** | **15,417.49** |
| **2029** | **137,740.71** | **15,417.49** |
| **2031** | **137,740.71** | **15,417.49** |

No raise, no flag, no `data_regime` marker — the last fitted year's value is returned for every future year, byte-
identical. The fleet grew ~41% across the fitted window and the module's own header calls that growth *"the single
biggest driver of the falling-baseload / rising-volatility regime the price engine tries to reproduce."* In a generated
2031 that driver is switched off: the world has 2025's fleet, forever, while the price generator independently asserts
a 2031 price distribution that only a *different* fleet could produce.

This is the atom's stated failure mode in its purest form — the generated 2031 is not a plausible world, because two
of its parts describe different decades. **It is also the cheapest thing on this list to fix**, and the fix is a
decision, not an algorithm: extrapolate against a published capacity trajectory (NESO FES, DESNZ), or **raise** past
the fitted window rather than silently flatten. Raising is the R15-correct default — an unavailable anchor is a failed
anchor, not a green one.

## 3. FINDING 3 — with no weather, the generated future has no winter, and that is ~95% of a cold day's demand

The per-customer demand shape is weather-driven through `_weather_adjusted_shape_fn` (`simulation/run_phase2b.py:319`),
which wraps the base profile-class shape in `build_demand_shape(base, mean_temp, commodity, property)`. Its fallback is
one line and it is silent:

```python
mean_temp = weather_means.get(date_str)
if mean_temp is None:
    shape = list(base_shape)      # unadjusted; no counter, no warning, no marker
```

**The baseline replay is clean here** — `REPORT_END = "2025-06-07"` is exactly the last row of the weather panel
(`sim/weather_data/C1..C4.csv`, 2016-01-01..2025-06-07, 3,447 rows; `weather_means_for_customer(C1)` returns n=3,446,
last key `2025-06-07`). The run window is pinned to the data. No silent gap exists in what ships today, and this pass
looked for one before asserting it.

The forward path removes that pin. `run_forward_scenario` sets `report_end = f"{year_to}-12-31"`, so a default
2026-2029 run covers **1,668 days (2025-06-08 → 2029-12-31) on which every customer's `mean_temp` is `None`** — 100% of
the generated window. What that fallback drops, measured on an 8.00 kWh base day through the real
`build_demand_shape`:

| property | commodity | 20°C | 12°C | 5°C | −2°C |
|---|---|---|---|---|---|
| `gas_boiler` | gas | 7.25 | 38.75 | 101.75 | **164.75** |
| `electric_storage` (the SME default) | elec | 7.25 | 19.06 | 42.69 | **66.31** |

The weather-free fallback returns the base **8.00 kWh** on every one of those days. On a −2°C day it therefore delivers
under 5% of the gas demand the same customer would draw with weather present. The generated world's customers do not
get cold.

**Why this is EP16's central coupling defect and not a rounding error:** the scenario presets are *weather-named*.
`stress_dunkelflaute_2027` raises `dunkelflaute_events_per_year` to 9.0 and `dunkelflaute_multiplier_mean` to 2.5 —
but "dunkelflaute" is a **price-side parameter only** (`ScenarioParams` has 15 fields, all price: mode means/stds,
negative-price frequency, dunkelflaute frequency/duration/multiplier, regime persistence). So the stress world raises
prices for a still, dark, cold spell while every customer's demand stays flat and weather-blind. The correlation that
actually kills real suppliers — demand peaking *at the same time* prices spike — is structurally absent from every
generated world, and it is absent in the one preset built to simulate it. A company that survives
`stress_dunkelflaute_2027` has survived a price shock with no volume shock attached.

That correlation is the whole point of the coupled triad here: SIM adds the depth, the company copes through the wall,
the harness measures the gap. With demand decoupled from the generated weather there is no gap to measure on this pair.

## 4. FINDING 4 — R13's curriculum wall is enforced over a rotation set of zero, and the worlds that run are a Python dict

There are **two disjoint world systems** in the tree, and the wall is on the wrong one.

**System A — walled, and empty.** `sim/scenario/spine.py` (SPINE_1) implements the R13 wall properly and says so: a
world becomes rotation-eligible only with a `ratified: true` record backed by a `ratification:` block; unratified
worlds load but `rotation_set()` excludes them and `select_for_rotation()` raises; the object is frozen and has no
setter, so no company-P&L outcome can write a scenario value back. Four curriculum artefacts exist
(`sim/scenario/curriculum/*.yaml`):

- `history_replay` — `ratified: true`, and its own comment says *"the baseline default is always available (not a
  rotation member)"*
- `crisis_2021_22`, `neso_central`, `supply_glut` — all three `ratified: false`, `true_probability: null`

Measured live: **`rotation_set()` → `[]`, n=0.** And the only non-test consumer of the spine is
`background/run_rotation.py`, which itself has **zero non-test callers** at HEAD (grep for
`run_rotation|select_next_cell|manifest_for_next_run` outside `tests/` returns one prose reference in
`sim/scenario/spine.py:278`) — re-verified this pass rather than inherited from the EP17 FRAME.

**System B — unwalled, and it is what actually generates futures.** `bimodal_generator.SCENARIOS` and
`gas_scenario_generator.GAS_SCENARIOS` are plain Python dicts holding five named difficulty worlds each —
`baseline_2025`, `central_2027`, `stress_dunkelflaute_2027`, `low_renewables_2027`, `battery_saturation_2029` — of 15
numeric parameters apiece. These are what `run_forward_scenario` runs, what `--scenario` selects from
(`choices=list(ELEC_SCENARIOS)`), and what `scenario_comparison.py` sweeps (`sorted(ELEC_SCENARIOS.keys())`). They
carry **no `ratified` field, no `provenance`, no `ratification:` block, no version, and no artefact** — and no test
asserts any of that. Any BUILD tick can edit a difficulty parameter with a one-line diff.

R13's words are *"difficulty changes are named, versioned, director-authored artefacts, never silent parameter
drift."* Mechanically, that is enforced for three worlds that can never run and waived for five that do. **The
control's population is the wrong one** — the classic R15 failure, here in its widest form: the wall is real, tested,
and pointed at an empty set.

It has already produced one false statement in live code. `sim/scenario/intraday_shape.py`'s header asserts that
per-scenario crisis severity *"is director-reserved CURRICULUM ... expressed through the daily generator's
per-scenario price level (**already director-owned via bimodal_generator SCENARIOS**)"* — and uses that as its stated
reason for adding no per-scenario dial of its own. The parenthetical is false: nothing owns those values but the file
they sit in. A later reader takes the guarantee at face value and builds on it. (`inferred`, on authorship only: the
git author of the presets' creating commit `64dc9b8c7` is *Rich Carlisle* — but that identity is shared by every
commit in this repo including agent commits, so it is evidence for neither side. What *is* evidence is the absence of
any ratification record, provenance field or curriculum artefact for these five, next to four spine worlds that carry
exactly that apparatus.)

## 5. FINDING 5 — the anchoring control covers one axis, runs only in the suite, and its live verdict is a divergence

`sim/scenario/fidelity_check.py` is the closest thing the repo has to EP16's "anchoring discipline", and it is good
work: six distributional moments (mean, std, lag-1 autocorr, tail ratio, tail skew, vol clustering) against a **block
bootstrap** of real returns, each moment added after a named red-team defeated the previous set, with R15 fail-open
handling for empty/constant/short/non-finite series and non-finite CIs. It is the template. Three limits bound what it
currently certifies:

1. **One axis, one direction.** It compares generated *price returns* to real price returns. Nothing checks generated
   weather, demand, fleet, or the cross-axis correlations of §3 — which is where the fidelity of a *world* actually
   lives, as distinct from the fidelity of a series.
2. **It can only judge the baseline.** By construction it checks the preset *expected to agree with history*. The four
   counterfactual presets have no reference series and therefore no machine-checkable tether at all. Their anchoring
   is a markdown file (`docs/market_research/price_distribution_high_renewables_2027.md`, 15,721 bytes, per-parameter
   H/M/L confidence against named sources) and **no test pins any preset value to any sourced number** — grep for
   `upper_mode_mean|lower_mode_fraction|dunkelflaute_events_per_year` in `tests/` returns only hand-built
   `ScenarioParams` fixtures. *This is EP16's actual subject: what "anchored" can mean for a world that never
   happened.* A moment-match cannot answer it; a **sourced-parameter-provenance** control can, and that is a different
   mechanism from the one already built.
3. **Its only callers are tests.** `reconcile_baseline_fidelity` (`run_scenario.py:217`) is invoked from
   `tests/simulation/test_run_scenario.py` and nowhere else; `run_forward_scenario` does not call it. So the check
   runs when the suite runs, not when a world is generated. Not "uninvoked" — but no generated world is gated on it.

And the verdict it currently records is a **divergence, still open**: the `baseline_2025` generator under-clusters
volatility versus real 2016-2025 SSP (`vol_clustering` ≈ 0.21 generated vs ≈ 0.42-0.51 real, robust across every real
window), locked in by that test and registered as a tracked simplification against W1_2. Correctly handled under R12 —
a divergence is a finding, never a cue to move the tolerance — and worth stating plainly here: **on the one axis where
this project can measure tether, the generator is measurably off, and knows it.**

---

# PASS 2 (worker tick 2026-08-17, HEAD `e015bac36`) — the recommended wiring would not deliver the property it was recommended for

Pass 1's five findings all survive unrepaired at this HEAD (`run_scenario.py` still has **zero** occurrences of the
string `weather`; the gas comment quoted in §7 is still in the tree), so this pass adds rather than re-narrates. It
takes pass 1's own item 1 — "the only one that restores a measurable gap on this coupled pair" — and tests it.

## 6. FINDING 6 — the seam is compatible, so item 1 really is small; but the spike days are drawn from an independent uniform stream, so wiring weather to demand restores no correlation

**The wiring is not blocked at the seam** (checked first, because EP17's pass 2 died exactly there). The consumer,
`simulation/weather_inputs.py::weather_means_for_customer`, resolves a customer to a location and returns
`{date_iso: temperature_mean_c}`. The generator, `sim/weather_engine.py`, returns
`simulate_national_macro -> {var: array(n_days)}` plus `simulate_regional_deviations -> {var: {location_id: array}}`,
and `location_id` is the same `C1..C4` key the CSVs carry in their own `location_id` column. National level + regional
deviation per location per day, keyed by exactly what the consumer asks for. **Item 1 stays small.**

**But it would not buy what pass 1 bought it for.** The property named was the one that kills real suppliers: volume
peaking WHEN prices spike. The price spike days do not come from weather and cannot be made to by adding a weather
caller downstream of them. In `sim/scenario/bimodal_generator.py::generate_scenario_prices`, dunkelflaute spells are
scheduled by `rng.sample(range(safe_range), ...)` on a `random.Random(seed)` stream — a **uniform draw over calendar
day index**, with no weather, temperature or wind input of any kind. Route generated weather into demand and you get
cold demand days on one independent stream and price spikes on another. The correlation stays structurally absent;
only its absence becomes harder to see, because both sides now move.

**Item 1 therefore splits, the same way EP17's did**: **1a** wire the weather generator to demand (small, seam
verified above) — **1b** make the weather draw the *upstream cause* of dunkelflaute scheduling in both price
generators, rather than a parallel process. 1b is a different mechanism, it is where the coupled-pair gap actually
lives, and pass 1 counted it inside 1.

## 7. FINDING 7 — the elec/gas dunkelflaute coupling asserted in a comment is absent, measured at chance

`sim/scenario/gas_scenario_generator.py` states the coupling twice, in prose, as its reason for needing no mechanism:

> `# Dunkelflaute scheduling (same approach as electricity generator — same event structure`
> `# means coupled dunkelflaute pressure on both commodities).`
> `# Regime state: shared with electricity via same lower_mode_fraction`
> `# (gas regime state follows electricity regime probabilistically)`

Both are false. The gas RNG is seeded `f"gas_{seed}_..."` against electricity's `f"{seed}_..."` — a deliberately
distinct sub-seed, so the two `rng.sample` calls are **independent realisations of the same distribution**. Same event
*structure* is not coupled *pressure*; an independent Bernoulli with a shared parameter does not "follow" anything.

Measured over all 5 shared presets × 3 seeds (15 draws), 2026-2029, by re-deriving each generator's day-index sets:

| scenario (seed 1 of 3) | elec dunkelflaute days | gas | shared | expected if independent |
|---|---|---|---|---|
| baseline_2025 | 34 | 35 | **0** | 0.81 |
| battery_saturation_2029 | 37 | 42 | **0** | 1.06 |
| central_2027 | 39 | 37 | **0** | 0.99 |
| low_renewables_2027 | 24 | 20 | **0** | 0.33 |
| stress_dunkelflaute_2027 | 125 | 116 | **6** | 9.92 |

Across all 15 draws: **mean shared days 2.33 against 2.59 expected under independence.** Not reduced coupling —
*no* coupling, to within the noise of the estimate. For a dual-fuel supplier the joint elec+gas spike in one cold
still spell is the event that empties the balance sheet, and it is absent by construction from every generated world,
including the preset named for it. The comment is why no one looked: it reads as a design decision already taken.

## 8. FINDING 8 — a dunkelflaute is a winter event; the generator schedules it uniformly across the calendar, and the real anchor is already in the repo

This is EP16's own subject rather than a coupling bug: a generating parameter with a **directly measurable real
counterpart that the generator does not consult**.

Generated (same 15 draws): mean Dec-Feb share of dunkelflaute days **0.184 elec / 0.259 gas**, against a **0.247**
calendar share of Dec-Feb. Uniform, as the `rng.sample(range(safe_range))` implies — roughly three quarters of every
generated "dunkelflaute" lands outside winter, and some land in July.

Real, from the observed panel already in the tree (`sim/weather_data/C1..C4.csv`, 2016-01-01..2025-06-07, n=3446 days
with all four locations present, averaged to a national daily series):

| still-and-dark definition | n days | Dec-Feb share | vs calendar 0.253 | mean temp |
|---|---|---|---|---|
| wind ≤ p25 (2.88 m/s) and cloud ≥ p75 (86.5%) | 181 | **0.359** | 1.42× | 9.04 °C (all days 10.15) |
| wind ≤ p10 and cloud ≥ p90 | 39 | **0.564** | 2.23× | 6.98 °C |

Both definitions are proxies and are stated as such — but they are proxies in the same direction, and the tighter one
is the stronger: the real thing concentrates in winter and is **3.2 °C colder** than an average day, which is exactly
the cold-still-dark conjunction the presets are named for. The anchoring failure is not that the frequency parameter
is wrong; it is that **the schedule has no seasonality at all** while a decade of the real distribution sits in the
repo, loaded by another module, unread by this one. It is also the concrete shape of §5's open question: this is what
"a sourced-parameter-provenance control" would have caught, on a parameter where the source is a local CSV.

Note the interaction with §2: the fleet is frozen at 2025 *and* the spells are aseasonal, and both are silent.

**R13 line, explicitly:** the fix here is a **baseline-fidelity** change (seasonality is a property of the real world,
measurable blind to company P&L), not a curriculum one. Event *frequency* per preset stays the director's. This pass
authored, proposed and changed no preset value.

---

## What this pass changes about EP16

**It is not W1_2 relabelled, and it is not "build a generator".** Restated from the evidence, EP16 is four items:

1. **Give the built weather generator a forward caller, and route demand through it** (§1, §3) — the mechanism exists
   and is fitted to real data; the world is one caller short. **PASS 2 SPLITS THIS (§6):** 1a the wiring, seam
   verified compatible and still small; **1b make weather the upstream cause of dunkelflaute scheduling** — without
   1b the two sides move independently and the gap this atom is scored on does not open. The claim that item 1 alone
   "restores a measurable gap on this coupled pair" is **withdrawn**; 1b is where it lives.
2. **Stop the fleet freezing silently past 2025** (§2) — smallest item here. Raise past the fitted window, or
   extrapolate against a published trajectory. Silent flattening is the fail-open.
3. **Move the curriculum wall onto the population that actually runs** (§4) — the five price presets need the same
   ratified-artefact apparatus the spine's four worlds already have, or the spine's worlds need to become the ones
   that run. Two world systems, one wall, and it is on the empty one. Correct
   `intraday_shape.py`'s false "already director-owned" guarantee either way.
4. **Define what "anchored" means for a world that never happened** (§5) — the moment-check cannot certify a
   counterfactual preset. A parameter-provenance control (every generating parameter carries its source, and the
   check fires when one has none) is EP16's own build and is not covered by any existing mechanism. **PASS 2 gives
   this item its first concrete instance (§8):** the dunkelflaute schedule is aseasonal while the real seasonality is
   measurable from a CSV already in the tree — a provenance control would have fired on it.
5. **(PASS 2, §7) Couple the two commodities' spells, and delete the comment that says they already are** — measured
   at chance across 15 draws. Smallest of the five and the one with a live false statement in the tree, alongside
   §4's `intraday_shape.py`.

`level_current` stays **0** and `loop_stage` stays **idle**: the deliverable of this atom is a mechanism, not this
document, so DISCOVER/FRAME output moves nothing. R12: no published number tuned; no published artefact written — and
verified as latent rather than live, `docs/reports/run_output_latest.json` carries no `scenario_name` and
`run_history.json` has zero, so **no forward-scenario run has ever been published**; every finding above is latent.
R13: no curriculum value authored, proposed or changed — §4 names a wall as misplaced, it does not move it; §2 names
extrapolation as a decision, it does not take it.

**Queued, not taken** (SELF-INTERRUPT DISCIPLINE): the silent fleet flattening (§2), the false director-owned claim in
`intraday_shape.py` (§4), and the missing weather caller (§1/§3) are all outside this atom's empty `file_scope` and
belong to W1_7, W1_2 and the run-scenario path respectively.

— FRAME, worker tick 2026-08-17, at HEAD `78d4f46f5`.

**Pass 2 addendum (worker tick 2026-08-17, HEAD `e015bac36`).** `level_current` stays **0** and `loop_stage` stays
**idle** for the same reason. R12: no published number tuned — and §6-§8 are latent on the same evidence as pass 1
(no forward-scenario run has ever been published). R13: no curriculum value authored, proposed or changed; §8 names
the seasonality fix as baseline-fidelity and leaves per-preset event frequency where it belongs. **Queued, not
taken** (SELF-INTERRUPT DISCIPLINE): the false coupling comments in `sim/scenario/gas_scenario_generator.py` and the
aseasonal schedule in both generators are outside this atom's empty `file_scope` and belong to the scenario-generator
path with W1_2.

---

# PASS 3 (worker tick 2026-08-18, HEAD `1f37fe393`) — the one preset the fidelity check can judge matches its calibration target and inverts the phenomenon underneath it

DISCOVER/FRAME only, LANE 3 idle draw. **No BUILD code written**; `file_scope` is `[]`. `docs/design/maturity_map.yaml`,
the atom's store file and `docs/design/frame/` were all clean in the shared tree at draw time.

Passes 1-2 established that the forward world is prices only, and that the *scheduling* of price events is unanchored
(§8, aseasonal) and uncoupled (§7, elec/gas at chance). This pass turns to the other overlay — **negative prices** —
because it is the one generating parameter in `ScenarioParams` whose real counterpart is measurable to the half-hour
from a dataset already in the tree, and because it lands on `baseline_2025`, the single preset §5 showed the existing
fidelity check *can* judge. Source: `sim/cache/elexon_ssp_full.json`, real Elexon SSP, restricted to 2016-2024
complete days (≥46 of 48 periods present) — **n = 3,287 days, 157,759 half-hours**. Generated side measured through
the shipped path (`generate_scenario_prices` → `intraday_shape.shape_day`), 2026-2029 × 3 seeds.

## 9. FINDING 9 — the negative-price calibration matches the one moment it was fitted to and gets every structural property of the event wrong

`baseline_2025` is the preset expected to agree with history. On negative prices it agrees on exactly one number:

| property of the negative-price phenomenon | real 2016-2024 | `baseline_2025` generated | |
|---|---|---|---|
| negative **hours** per year | 176.4 | 168.8 | **0.96× — the calibration target, matched** |
| days carrying ≥1 negative half-hour, per year | 58.4 | 12.5 | 0.21× |
| median negative periods on such a day | **4** (2 h) | **45** (22.5 h) | 11× |
| most negative periods in a single day, ever observed | **31 / 48** | **48 / 48** | GB has never had a wholly-negative day |
| days with a negative **daily mean**, per year | **0.67** (6 in 9 years) | **6.4** | 9.6× |
| deepest daily mean ever recorded | **−£16.91** | draws N(−20, 15), floor −75 | the *mean* generated negative day is deeper than the deepest real one |

The mechanism is written in the generator's own docstring:

> `# Negative price days: ~7-28 days/year (calibrated to 165-1000 negative hours/year at ~6h/event).`
> `# 165 negative hours/year ≈ 7 days/year (at ~24h/day × occurrence fraction).`

The model's unit is a **daily mean**, so the only way it can express a negative hour is to make the whole day
negative. The year's negative-hour budget is therefore correct and is packed into a fifth as many days at eleven times
the duration and a depth GB has never reached. Real negative prices are a **~2-hour midday event on 58 separate
days**; all six real negative-mean days are low-demand high-output spring/early-summer days (2019-05-26, 2019-12-08,
2020-05-22, 2020-06-28, 2023-04-10, 2024-04-13), and even those are shallow (−£1.12 to −£16.91) with 19-30 of 48
periods negative, never all 48.

Two riders. **(a) The upper anchor is arithmetically unreachable**: the same docstring maps "1000 negative hours" to
"28 days/year", but 28 days hold 672 hours. The top of the cited calibration band cannot be represented by a whole-day
model at all, so the preset range is bounded by the representation rather than by the research. **(b) The component
that *could* produce the real shape has no scenario dial.** `intraday_shape.py`'s oversupply trough — a single deep
negative half-hour, which is exactly the real event — is governed by `trough_base_rate: 0.02`, and that module states
by design that it "adds NO new per-scenario dial; it ships one baseline-calibrated relationship." So the frequency of
the negative-price event that actually happens is a fixed constant no preset can move, while the dial named
`negative_days_per_year` moves an event that does not occur.

This is a **compensating-error** finding, and it is squarely §5's open question made concrete: a six-moment check on
daily price *returns* cannot see any row of that table except the first. The moment that was fitted is green; the
phenomenon is inverted.

## 10. FINDING 10 — in three of five presets, the dial named for negative prices is not what produces them

The regime draws are unbounded Gaussians (`rng.gauss(lower_mode_mean, lower_mode_std)`), so a preset with a low mean
and a wide std emits negative daily prices with **no overlay involved**. Analytic leak (Φ(0; μ, σ) × `lower_mode_fraction`
× 365.25), against the measured realised count:

| preset | `negative_days_per_year` (the dial) | P(lower draw < 0) | leak from the regime, /yr | **realised, measured** | dial's share |
|---|---|---|---|---|---|
| `battery_saturation_2029` | 10.0 | 0.212 — N(20, 25) | 46.4 | **51.8** | **18%** |
| `stress_dunkelflaute_2027` | 28.0 | 0.128 — N(25, 22) | 27.1 | **49.4** | 51% |
| `central_2027` | 20.0 | 0.029 — N(38, 20) | 5.8 | **23.0** | 78% |
| `baseline_2025` | 7.0 | 0.000 | 0.0 | 6.4 | 100% |
| `low_renewables_2027` | 5.0 | 0.000 | 0.0 | 4.7 | 100% |

`battery_saturation_2029` is the clean case, because its comment records the intent: `negative_days_per_year=10.0,
# batteries absorb most surpluses; fewer sustained negatives`. That reasoning set it to the second-lowest dial of the
five — and the preset delivers **the highest realised negative-day count of all five, 5.2× its own dial**, because
`lower_mode_std=25` against `lower_mode_mean=20` puts a fifth of its lower-regime days below zero. The parameter that
governs the outcome is `lower_mode_std`, which is not named for negatives, is not documented as a negative-price
lever, and cannot be read off the preset table without evaluating a normal CDF.

This is EP16's subject in its own right, distinct from §9: **a generating parameter that does not govern the quantity
it is named for**, because a second parameter leaks into the same outcome. A parameter-provenance control (§5 item 4)
would catch the *unsourced* value; it would not catch this. What catches it is checking that each named dial actually
moves the quantity it names — a different control, and the second one this atom now owes.

*Latent, not live, and stated as such:* `negative_price_floor` is applied only on the overlay branch, never to the
regime draw, so a leaked negative day is unfloored. At these parameters it does not bite — observed minima over 3
seeds were −£66.22 (`battery_saturation_2029`) and −£69.67 (`stress_dunkelflaute_2027`), both inside the −75 floor.
An asymmetry worth recording, not a defect to claim.

## 11. FINDING 11 — the negative overlay silently overwrites the dunkelflaute overlay, replacing a scarcity event with its physical opposite

In the day loop the two overlays are applied in sequence onto independently drawn index sets, last-write-wins:

```python
if day_idx in dunkelflaute_day_indices:      # price = upper mode × multiplier  (scarcity)
    ...
if day_idx in negative_day_indices:          # price = N(negative_mean, std)    (surplus) — overwrites
    ...
```

Measured by re-deriving both index sets exactly as the generator does, 5 presets × 3 seeds, 2026-2029:

| preset | scheduled dunkelflaute days | overwritten by the negative overlay | |
|---|---|---|---|
| `stress_dunkelflaute_2027` | 123.7 | **10.0** | 8.1% |
| `central_2027` | 40.0 | 3.3 | 8.3% |
| `battery_saturation_2029` | 41.0 | 0.7 | 1.6% |
| `baseline_2025` | 34.0 | 0.0 | 0% |
| `low_renewables_2027` | 20.3 | 0.0 | 0% |
| **total across 15 draws** | **777** | **42** | **5.4%** |

A dunkelflaute is a still, dark spell: it is precisely the state in which negative prices **cannot** form, because
negative prices are a renewable-*surplus* phenomenon — confirmed on the real side by §9, where all six negative-mean
days are low-demand high-output days. The generator takes its highest-price event and, on 8% of those days in the
preset named for it, replaces it with the one event the same weather excludes. That is an **R10 absurdity class**
defect, not a tuning error: a −£30/MWh dunkelflaute day is not a member of any plausible world.

It has a second consequence for the record: `dunkelflaute_events_per_year` silently under-delivers by that fraction,
and **pass 2's §7 shared-day counts were computed on the *scheduled* index sets**. The realised elec/gas coupling is
therefore very slightly lower still than the at-chance figure reported there. That does not change §7's conclusion —
it was already at chance — but the numbers in §7 are scheduled-set numbers and should be read as such.

## Correction to the record (passes 1 and 2)

Both earlier passes cited `docs/reports/run_history.json` as evidence that no forward-scenario run has ever been
published. **That file does not exist at this HEAD.** The conclusion is unchanged and now rests on a stronger check:
`scenario_name` appears in **zero of the 5,281 JSON files** under `docs/reports/`, and `run_output_latest.json` has no
such key. Everything in §§1-11 remains **latent** — no published artefact carries any of it.

## What pass 3 adds to EP16's item list

Item 4 ("define what *anchored* means for a world that never happened") gains its sharpest instance and then splits:

- **4a — parameter provenance** (pass 2, §8): every generating parameter carries its source; the check fires when one
  has none. Would have caught the aseasonal schedule.
- **4b — dial authority** (§10, new): every parameter *named* for a quantity must be shown to be the dominant lever on
  it. Provenance would pass `battery_saturation_2029` — the dial is sourced and reasoned — and still miss that it
  controls 18% of the outcome it names.
- **4c — phenomenon shape, not parameter value** (§9, new): the negative-price event is mis-specified at the level of
  *representation* — daily-mean granularity cannot express a 2-hour midday event — so no value of any parameter fixes
  it. This is the first item on EP16's list that is not a number and not a wiring job, and it is the one the existing
  six-moment fidelity check is structurally blind to.

And a sixth top-level item joins §§1-5: **6 — fix the overlay precedence** (§11), smallest on the list, an R10-class
absurdity, and the third live-code defect this FRAME has found alongside §4's false `intraday_shape.py` guarantee and
§7's false gas-coupling comments.

**Pass 3 close.** `level_current` stays **0** and `loop_stage` stays **idle**: the deliverable of this atom is a
mechanism, not this document. **R12:** no published number tuned — and latent on the check above, no forward-scenario
run has ever been published. **R13:** no curriculum value authored, proposed or changed. §9 and §11 are
**baseline-fidelity** findings (the shape and the physics of negative prices are properties of the real world,
measured blind to company P&L); §10 names a dial as non-authoritative over its own quantity without proposing a value
for it — per-preset severity stays the director's. **Queued, not taken** (SELF-INTERRUPT DISCIPLINE): the overlay
precedence, the unfloored regime leak and the whole-day negative representation all live in
`sim/scenario/bimodal_generator.py`, outside this atom's empty `file_scope`, and belong to the scenario-generator path
with W1_2.

— FRAME pass 3, worker tick 2026-08-18, at HEAD `1f37fe393`.
