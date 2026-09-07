**Severity:** RECORDED · **Lane:** H_harness

# Director console — verbatim record, 2026-09-07

> **The director did not write or stage this file. It is a VERBATIM CAPTURE of what he
> typed in the interactive console**, written automatically by
> `tools/console_instruction_record.py` so that his words leave a trace the machine can
> read. Under CLAUDE.md the console already carries full authority; what it did not carry
> was EVIDENCE, and on 2026-08-19 that cost `EP6_wall_protocol_typing` a wrongful re-park
> after 381 director-facing sources correctly reported silence.
>
> **Quoted exactly, never paraphrased, never expanded.** Shorthand is left as shorthand:
> "move EP1 and EP6 to build" is recorded as written, so this file does NOT by itself
> release `EP6_wall_protocol_typing` — the release door matches full atom ids. Resolving
> shorthand to an atom is a judgement, and it belongs in a separate record that cites
> this one, not in an automatic capture that would be putting words in his mouth.

Source: `22080be5-e19e-4099-a007-d71c3a6e7845.jsonl` · 6 turn(s).

### 2026-09-07T06:19:41.904Z

> I want to understand the household placement properly before we
> build further on it, because it's foundational and the 47% error
> shook my confidence in the method rather than just the number.
>
> Tell me plainly: what is the actual difficulty? You corrected 47%
> to 15%, so something in the placement was wrong. Was it the
> method, the data, or the join — and is the corrected version
> sound, or is it a better approximation of the same
> approximation?
>
> My concern is that postcodes aren't precise enough for this. A
> postcode covers roughly fifteen addresses with one grid reference,
> and in sparse areas it can span a wide area — which is exactly
> where the error was, and exactly where the weighting matters most
> for cell counts.
>
> So: why not place dwellings directly? OS Open UPRN is free and
> open — every property in Great Britain with coordinates, about 40
> million rows. That removes the centroid entirely. It includes
> non-residential properties, so a raw count isn't households and
> needs filtering or scaling against the census total, but that's a
> tractable problem rather than an approximation.
>
> And I don't understand why any of this is expensive. Placing 27
> million households into cells is a join, not a computation.
> If you've estimated it as long-running, tell me the estimate and
> what dominates it, because I don't believe the compute at this
> data size.
>
> If you've already considered UPRN and rejected it, say why. If the
> current method is good enough, show me the error it carries rather
> than asserting it — the household weighting sets the cell counts,
> and the cell counts are what stage 1 rests on. I'd rather spend a
> day getting this right than build the world on a simplification
> nobody has bounded.

### 2026-09-07T08:04:27.305Z

> Good — taking the UPRN route rather than defending the centroid
> was the right call, and the answer not moving is the reassuring
> outcome.
>
> Next is the housing joint, W2_21: fit the joint so a household's
> attributes hang together rather than being drawn independently — a
> large detached house in a cold cell with the consumption that
> implies. Then the space-filling sample, then the people joint
> conditioning what the demand model already carries.
>
> And check the fork dial actually reverted at 02:50 as designed —
> several commits this morning mention it not being restored at HEAD
> and the guard's post-expiry behaviour. My allowance reset at 04:00
> so the widening should be off.

### 2026-09-07T08:53:10.579Z

> I want to be clear what's been answered and what hasn't.
>
> You've answered how many weather cells capture 99% of
> household-weighted variation in the weather drivers — 21, 21 and 5
> across three grids. That's a partition of Britain.
>
> What I actually care about is heat demand variation, which
> depends on the weather cell and the house together. So: how many
> house types are needed to capture 99% of the variation in
> demand, and how do the two compose? If they're independent it's
> weather cells times house types and the sample gets large; if
> they're correlated — and they probably are, since northern housing
> stock differs from southern — it's much smaller.
>
> Measure the joint coverage rather than the two separately. The
> number I need is how many distinct household cases cover 99% of
> demand variation, not how many cells cover 99% of weather.

### 2026-09-07T09:37:55.493Z

> This session is being continued from a previous conversation that ran out of context. The summary below covers the earlier portion of the conversation.
>
> Summary:
> 1. **Primary Request and Intent:**
>
> Nine director turns in this session, each a distinct instruction:
>
> (a) **Challenge W1_21's framing** ("a sharper cut"): one cell grid is being asked to serve three jobs. Hypothesis: wind is fine-grained but reaches households only via wind chill (second-order), while its real effect is on wholesale price, which is national and already available. "Establish that rather than assume it. If wind does matter per household, say through what mechanism and how much." Also asked what resolution PV output actually needs.
>
> (b) **State the cell answer as a build decision**, "not just a curve: roughly twenty cells per driver held separately, rather than one shared partition at 987. Say what the world actually uses." And **separate the two solar effects** — PV yield vs solar gain: "Is it in fabric_physics, or is it the same gap again? Check rather than assume, given the wind term's history." Then W1_26, then PV.
>
> (c) **Site visualisation** (sent mid-turn): "When the wind and PV work is done, make the weather cells visible on the site — Knowledge section, with a map or whatever visualisation actually explains it." Three things to convey: what a cell is (climate classes, scattered patches, "that needs saying or it reads as a bug"); the coverage curve so "a reader sees that granularity is a price list rather than a fact"; and that half of Britain's land holds nobody. "Explanatory rather than decorative — a domain reader should learn something they didn't know."
>
> (d) **Density panel + Scotland gaps**: the density panel is a proportion not a density and saturates. Scotland has visible gaps with three candidates (lossier UV402 join, genuine terrain, holes in postcode-to-cell mapping) — "Two of those are honest and one is a defect, and they look identical on the map. Establish which, and if any part is genuinely uncovered, say so on the page rather than leaving a reader to read absence as emptiness."
>
> (e) **White gaps + resolution mismatch**: white gaps inside the temperature map. And "the density map contradicts its own caption... The map is drawn in 5 km blocks and the statistic counted in 1 km cells... That's the same-figure-on-two-clocks class in visual form. Fix it so the reader sees what the number says: draw at the resolution the claim is made at, or state the resolution on the map and make the claim at block level too."
>
> (f) **Is 47% true?**: "is it true that 47% of GB 1 km cells have no address in them? The classification comes from postcode centroids as far as I can tell, and a centroid is a point... Sample it... If the method undercounts, say by how much and fix the weights. If it holds, say so on the page with the check named."
>
> (g) **Understand the placement properly**: "what is the actual difficulty? ... Was it the method, the data, or the join — and is the corrected version sound, or is it a better approximation of the same approximation? ... why not place dwellings directly? OS Open UPRN is free and open... And I don't understand why any of this is expensive. Placing 27 million households into cells is a join, not a computation. If you've estimated it as long-running, tell me the estimate and what dominates it... I'd rather spend a day getting this right than build the world on a simplification nobody has bounded."
>
> (h) **W2_21 + fork dial**: "Next is the housing joint, W2_21: fit the joint so a household's attributes hang together rather than being drawn independently... Then the space-filling sample, then the people joint conditioning what the demand model already carries. And check the fork dial actually reverted at 02:50 as designed."
>
> (i) **The joint demand coverage** (most recent): "What I actually care about is heat demand variation, which depends on the weather cell and the house together. So: how many house types are needed to capture 99% of the variation in demand, and how do the two compose? If they're independent it's weather cells times house types and the sample gets large; if they're correlated — and they probably are, since northern housing stock differs from southern — it's much smaller. Measure the joint coverage rather than the two separately. The number I need is how many distinct household cases cover 99% of demand variation, not how many cells cover 99% of weather."
>
> 2. **Key Technical Concepts:**
>    - **Walls (never cross)**: epistemic wall (`company/`/`saas/` may only know what a real UK supplier could); `company/`/`saas/` may never open a socket; historical ground truth immutable; **HOOK-BYPASS IS A WALL** (`--no-verify` never; `python3 -m tools.surgical_land` is the sanctioned door); never widen the sandbox profile (director-console-only).
>    - **Four reserved classes** (director-only): spending real money, contacting real people, irretractable public claims under Poesys's name, anything touching a real person's safety.
>    - **Never `git stash`, never `git checkout <path>`; commit by pathspec, never `-A`.**
>    - **R15 control-failure taxonomy**: TAUTOLOGY, FAIL-OPEN, FAIL-SILENT; every control mutation-proved; a survivor is either a missing test or an equivalence and which must be established.
>    - **`surgical_land`**: gates `git archive HEAD` + pathspec; `--content REPOPATH=SRCFILE` overrides bytes; `--merge REF`; commits take >10 min so must be backgrounded.
>    - **Two-file maturity map** + `refile()` + `closed: >-` prose + `gate_authorization.record_level_up_self_certified`; MAP_SIZE_CEILING = 409600 over both halves.
>    - **HadUK-Grid**: 1450×900 1 km OSGB grid, origin −199,500 m (col = `(easting+200000)//1000`), 245,077 UK land cells, read via `xarray`+`h5netcdf`.
>    - **SAP 10.2 / BREDEM wind factor**: `adjusted ACH = raw ACH × shelter × (wind/4 m/s)`; Part F minimum ventilation ACH clamps the calm end.
>    - **Ångström–Prescott**: `H/H₀ = a + b·(n/N)`, Prescott a=0.25 b=0.50; elasticity 0.41–0.49 so irradiation varies ~half as much as sunshine duration.
>    - **OS Open UPRN** (41,629,393 address points, no geography) vs **ONSUD** (ONS UPRN Directory — `UPRN, GRIDGB1E, GRIDGB1N, ..., OA21CD` in one row; 540 MB; Data/ has 11 regional CSVs, Documents/ has 24 lookup CSVs with different schemas).
>    - **DESNZ NEED** `anon2026_50k.csv`: 50,000 dwellings; `PROP_TYPE`, `PROP_AGE_BAND` (1=before 1930, 2=1930-1972, 3=1973-1999, 4=2000+), `FLOOR_AREA_BAND` (1=≤50, 2=51-100, 3=101-150, 4=151-200, 5=>200 m²), `EPC` (A/B, C, D, E, F/G, No EPC — 30.2% unrated), `REGION`, `MAIN_HEAT_FUEL`, `Gcons`/`Econs` 2011–2024.
>    - **Iterative proportional fitting (raking)** of a seed joint onto published marginals.
>    - **Coverage curve** = 1 − within/total weighted sum of squares in standardised space; invariant to affine rescaling.
>
> 3. **Files and Code Sections:**
>
>    - **`tools/weather_cell_drivers.py`** (created) — reproduces W1_19's published table from HadUK normals. `drivers()` returns land-masked arrays plus `latitude` (true, from the file's aux coord) and `north` (OSGB) — the two give −0.806 and −0.807 respectively. `EXPECTED_LAND_CELLS = 245_077`, `GRID_SHAPE = (1450, 900)`. Sun is **summed** not averaged.
>
>    - **`tools/weather_cell_weights.py`** (created, then rewritten three times) — household placement. Final form:
>      ```python
>      def census_weights(group_of=None) -> tuple[dict, dict[str, int]]:
>          from tools import ons_uprn_directory as onsud
>          households = read_households()
>          pairs = onsud.oa_cell_addresses()
>          per_oa: dict[str, int] = defaultdict(int)
>          for (oa, _cx, _cy), count in pairs.items():
>              per_oa[oa] += count
>          weights = defaultdict(float); grouped = defaultdict(lambda: defaultdict(float))
>          for (oa, cell_x, cell_y), count in pairs.items():
>              n = households.get(oa)
>              if n is None: continue
>              group = None
>              if group_of is not None:
>                  group = group_of(oa)
>                  if group is None: dropped_groups.add(oa); continue
>              into = weights if group is None else grouped[group]
>              share = n * count / per_oa[oa]
>              into[(cell_x, cell_y)] += share
>      ```
>      Also `gb_reachable(drivers, threshold_km=20.0)` (GB_REACH_KM = 20.0, GB_LAND_AREA_KM2 = 228_991, refuses if >3% drift), `aligned_to_land`, `placement_cost()`, `pull_ts041` (paged, TS041_EXPECTED_AREAS = 188_880), `pull_scotland` (UV402 cross-checked against UV406).
>
>    - **`tools/os_open_uprn.py`** (created) — pulls OS Open UPRN, builds 1450×900 count grid; `cell_counts()` refuses on absence; `coverage(drivers, gb_mask)`. EXPECTED_UPRNS = 41_629_393.
>
>    - **`tools/ons_uprn_directory.py`** (created) — the file that removed the centroid. `ITEM_ID = "<REDACTED: credential-shaped, removed by the console capture>"`, `DATA_PREFIX = "Data/"`, `EXPECTED_ADDRESSES = 41_386_453`. `build_store()` streams the zip → `{(oa, cell_x, cell_y): addresses}` in 70s; `oa_cell_addresses()` refuses on absence with "postcode centroid" in the message.
>
>    - **`tools/weather_cell_derivation.py`** (created) — `DRIVERS = ("winter_temp", "annual_wind", "annual_sun")`, `coverage_curve(ks, household_weighted, seed, space=None)`, `per_driver_curve`, `choice_sensitivity`, `cells_for` (returns None when unreached), and:
>      ```python
>      def captured_share(within: float, total: float) -> float:
>          """`1 - within/total`, rounded, and never NEGATIVE ZERO."""
>          return round(1.0 - within / total, 4) + 0.0
>      ```
>
>    - **`tools/weather_driver_sensitivity.py`** (created) — `wind_hlc_sensitivity()`, `pv_yield_error()`, `solar_gain_sensitivity()`, `_sim_has_a_wind_term()` (now measures by calling `with_wind(2.0)` vs `with_wind(8.0)`), `_daily_weather_has_wind()`. Constants: `WIND_P05_MS, WIND_MEDIAN_MS, WIND_P95_MS = 2.98, 3.85, 5.61`; `WINTER_TEMP_P05_C, WINTER_TEMP_P95_C = 3.95, 6.13`; `SUNSHINE_P05_H, SUNSHINE_P95_H = 1320.13, 1734.48`.
>
>    - **`simulation/fabric_physics.py`** (modified, W1_26) — added `SAP_REFERENCE_WIND_MS = 4.0`; `DailyWeather` gained a **required** `wind_speed_mean_ms`; `FabricParameters` gained `fabric_w_per_k`, `raw_infiltration_ach`, `volume_m3` and:
>      ```python
>      def with_wind(self, wind_speed_ms: float) -> "FabricParameters":
>          if self.volume_m3 <= 0.0 or self.raw_infiltration_ach <= 0.0:
>              raise ValueError("this FabricParameters was built without its ventilation components...")
>          ach = max(self.raw_infiltration_ach * (wind_speed_ms / SAP_REFERENCE_WIND_MS),
>                    _MINIMUM_VENTILATION_ACH)
>          hlc_kw_per_k = (self.fabric_w_per_k + 0.33 * ach * self.volume_m3) / 1000.0
>          return replace(self, r_ia_k_per_kw=1.0 / hlc_kw_per_k)
>      ```
>      `simulate_premise` calls `params.with_wind(day.wind_speed_mean_ms)`.
>
>    - **`simulation/premise_population.py`** (modified, W2_21) — `_EPC_TILT_BY_ERA` and `_EPC_TILT_BY_PROPERTY_TYPE` replaced with NEED-measured lifts, e.g. `BuildEra.PRE_1919: {"AB": 0.0362, "C": 0.5940, "D": 1.3864, "E": 2.1151, "F": 2.7846, "G": 2.7846}` and `PropertyType.DETACHED: {"AB": 1.2073, ..., "F": 1.8114, "G": 1.8114}`.
>
>    - **`tools/need_stock_joint.py`** (created) — `measured_lifts()`, `era_band_weights()` (year-overlap split: 1919-1944 → 0.423/0.577), `PROPERTY_TYPE`, `EPC_CLASS`, `AGE_BAND_YEARS`, `ERA_YEARS`, `_unrated_ratio()`.
>
>    - **`tools/generate_weather_cells_data.py`** (created) — site feed. `BLOCK_KM = 5` for the class map; `DENSITY_CUTS = (0.0, 5.0, 20.0, 100.0, 400.0)`, `DENSITY_BLOCK_KM = 1`; `SEA = -1`, `NOT_GB = -2`; `downsample_modal` (modal, not mean); classes re-labelled in temperature order; `_empty_by_band` over GB only with `_land_cells` counts published for conservation.
>
>    - **`site/knowledge/weather-cells/index.html`** + **`test_the_maps_reach_the_reader.py`** (created) — three inline-SVG visuals driven through `site/_live_harness.mjs`; registered in `site/data/knowledge_wholesale.json` and linked as real markup from `site/knowledge/index.html`; tables wrapped in `<div class="table-scroll">`.
>
>    - **`tools/demand_case_coverage.py`** (created, most recent) — the joint demand coverage. Key constants:
>      ```python
>      DOYS = tuple(range(274, 366)) + tuple(range(1, 91))
>      SETPOINT_C = 20.0
>      AGE_TO_ERA = {"1": "PRE_1919", "2": "ERA_1945_1964", "3": "ERA_1981_2000", "4": "POST_2000"}
>      EPC_TO_INSULATION = {"A/B": "FULL", "C": "FULL", "D": "PARTIAL", "E": "POOR", "F/G": "POOR"}
>      AREA_MIDPOINT = {"1": 40.0, "2": 75.0, "3": 125.0, "4": 175.0, "5": 230.0}
>      REFERENCE_SUNSHINE_H = 1535.0
>      KS = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233)
>      ```
>      Functions: `_seasonal_hdd`, `_reference_solar_kwh_per_m2`, `house_cases()` (imputes the unrated 30% from the type×age conditional), `demand_grid()` (excludes `S92000003`), `coverage(values, weights, ks, seed, sample=400_000)` (standardises columns, samples weighted), `measurement()`.
>
>    - **`tests/tools/test_demand_case_coverage.py`** (created) — 7 controls including `test_COVERAGE_IS_INVARIANT_TO_THE_PROXY_S_CALIBRATION`, `test_THE_JOINT_DOES_NOT_MULTIPLY_and_the_control_can_see_it_if_it_did` (synthetic grid with independent inputs), `test_A_SECOND_OUTPUT_AXIS_COSTS_MORE_CASES`, `test_THE_AXES_ARE_STANDARDISED_or_the_UNITS_decide_the_answer`, `test_SCOTLAND_IS_EXCLUDED_DELIBERATELY_and_the_reason_is_in_the_code`, `test_the_EPC_TO_FABRIC_MAP_IS_DECLARED_A_CHOICE_and_not_dressed_as_an_anchor`, `test_the_MEASUREMENT_REPRODUCES_ITS_PUBLISHED_ANSWER`.
>
>    - **`docs/market_research/`** documents created: `the_three_weather_drivers_per_land_cell_and_the_sign_that_flips.md`, `half_the_land_is_empty_and_weighting_halves_the_variation.md` (corrected three times in place), `how_many_weather_cells_britain_needs_and_why_the_answer_is_a_curve.md` (corrected three times), `cold_snaps_arrive_in_blocks_and_britain_has_no_second_weather.md`, `one_grid_three_jobs_and_wind_is_not_the_awkward_one.md`, `the_cell_decision_and_what_the_world_actually_uses.md`, `the_world_now_has_a_wind_term_and_my_prediction_was_wrong_three_ways.md`, `W1_26_prediction_filed_before_the_measurement.md`, `pv_yield_cannot_be_keyed_on_latitude.md`, `the_tilt_table_had_a_direction_wrong_and_only_a_direction_was_claimed.md`, `thirteen_cases_cover_demand_and_that_is_only_half_an_answer.md`.
>
> 4. **Errors and fixes:**
>    - **Mutation harness reported four false KILLs** because `--timeout=900` was unrecognised (pytest exited 4 every time). Fixed by removing the flag and always running an unmutated baseline through the identical command. Saved as a memory.
>    - **`sys.path` script-vs-module defect** shipped again (5th–8th instances) in `weather_cell_weights --weighted`, `weather_cell_derivation`, `weather_cell_persistence`, `weather_driver_sensitivity`. Fixed with `if str(PROJECT) not in sys.path: sys.path.insert(0, str(PROJECT))` plus a probe control forcing `sys.path[0] = 'tools'`.
>    - **nomis capped an unpaged request at 25,000 of 188,880 output areas** silently. Fixed with paging plus a count assertion that refuses.
>    - **`--content` land reverted another lane's map work** — my content was built from a HEAD that moved; the gate passed because the reverted side was internally consistent. Repair needed six store files (3 untracked, 3 modified), found by running the design suite. Lesson: after a `--content` land, diff against the commit you raced.
>    - **Two opposite level-move orderings**: W1_25's level couldn't be *recorded* until the map was *landed* (ledger reads the live map); W1_26's couldn't be *landed* until it was *recorded* (level gate wants the entry at commit time). Order: land, reconcile, record.
>    - **Orphan ratchet refused twice**: I lowered the floor by four modules when only three were wired; then the generator itself was an orphan and the *local* check couldn't see it because `compute()` reads `git ls-files` and the file was untracked.
>    - **A commit landed nothing** because `/tmp` was 91% full — the message file was written and silently lost, and `surgical_land` got an empty `-m`. Freed 5.5 GB.
>    - **My freeze of `generate_weather_cells_data` wedged every commit in the tree for 131 minutes** — another lane wired it into the regen cycle instead, correctly. My module also claimed `downsample_modal` "is tested for exactly that confusion" while nothing imported it.
>    - **The generator wasn't byte-deterministic** (`-0.0` vs `0.0` at k=1) — would commit a diff every regen cycle. Fixed with `captured_share()`.
>    - **`placement_cost` called `census_weights()` inside a list comprehension** — once per cell, 245,077 times, each re-reading 1.67M postcodes. Ran 25 minutes without finishing. Also its conservation flag compared land-grid totals rather than placed totals, and it divided by a standard deviation without checking there was one.
>    - **Skipped rather than deleted an obsolete test**, leaving a reference to a function I'd removed — gate refused with "the consumer landed and the supplier did not".
>    - **Population map read 81% occupied against a 49.6% caption** (binary flag), then **saturated as a proportion**, then **resolution mismatch at 5 km** — three wrong versions, all caught by looking at the picture.
>    - **White gaps in the class map**: 1,353 GB land blocks unclassed because clustering ran over occupied cells only.
>    - **KMeans `n_samples=274 should be >= n_clusters=377`** — capped ks at the distinct point count.
>    - **Test assertions failed across line wraps** (`#` / `#:` comment markers) — fixed with `re.sub(r"\s*#:?\s+", " ", source)`.
>    - **My module docstring cited a `--sensitivity` flag that doesn't exist** — removed the claim.
>    - **`%s` formatting collided with `%` in the gain text** when minting W2_27 — switched to string concatenation.
>
> 5. **Problem Solving:**
>    Systematically converted three published figures from assumption to measurement: the wind term (absent from the world entirely), the household placement (three successive methods, each better and each still centroid-anchored until ONSUD), and the stock joint (hand tilts with one wrong direction). Established that the published cell counts answered coverage of weather *drivers* rather than of *demand*, and measured the joint: 13 cases for 99%, not the 273 a separable composition would need, with the cause identified as output-scalarity rather than input correlation.
>
> 6. **All user messages:**
>    - "That's a sharper cut than the equal-versus-temperature-dominant choice, and it exposes a flaw in the framing: **one cell grid is being asked to serve three jobs.** ... So: Split the cell question by driver rather than picking one weighting... Wind is the one I'd challenge. It's genuinely fine-grained — terrain, coast, exposure — which is why the map looks nuanced. But ask what it's for. A household has no turbine, so wind reaches them only through wind chill on heat loss, which is second-order... Establish that rather than assume it. If wind does matter per household, say through what mechanism and how much."
>    - "Two things, and the second is a real defect. ... The cell answer needs stating as a build decision, not just a curve: roughly twenty cells per driver held separately, rather than one shared partition at 987. Say what the world actually uses. And separate the two solar effects. PV yield is generation and you've scoped it at three to five cells. Solar gain is free heat through glazing reducing heat demand — a fabric term that sits in SAP beside the wind one you just found missing. Is it in fabric_physics, or is it the same gap again? Check rather than assume, given the wind term's history. Then W1_26, then PV."
>    - "When the wind and PV work is done, make the weather cells visible on the site — Knowledge section, with a map or whatever visualisation actually explains it. This is the first genuinely map-shaped thing the project has and the site has never carried a visual explanation of anything. Three things it should convey. What a cell is: if they're climate classes rather than contiguous regions, a map will show scattered patches sharing a colour, and that needs saying or it reads as a bug. The coverage curve — 34 for 90%, 89 for 95%, 987 for 99% on one shared partition against ~21 per driver held separately, so a reader sees that granularity is a price list rather than a fact. And that half of Britain's land holds nobody, which is why the wind map looks more complicated than it is. Explanatory rather than decorative — a domain reader should learn something they didn't know. The charts mint has been unblocked since 12 August and never drawn; this is what it was for."
>    - "Two things on the weather map. The density panel is a proportion, not a density — how many 1km cells within a 5km block contain a household. It saturates, so dense city and sparse village both read as fully covered, which destroys the variation the map exists to show. Use households per km². You already placed 27.28 million households against postcodes for the weights, so the number exists. And Scotland has visible gaps. Three candidates I can't separate from outside: the UV402 join being lossier than TS041, genuinely empty terrain, or holes in the postcode-to-cell mapping north of the border. Two of those are honest and one is a defect, and they look identical on the map. Establish which, and if any part is genuinely uncovered, say so on the page rather than leaving a reader to read absence as emptiness."
>    - "The maps look right now. My remaining worry is the count, not the picture: is it true that 47% of GB 1 km cells have no address in them? The classification comes from postcode centroids as far as I can tell, and a centroid is a point. A cell containing scattered dwellings whose postcode centroid falls in the neighbouring cell reads as empty — which would undercount exactly where you'd expect, in sparse rural, isolated farms and dispersed roads. 53% is a plausible-sounding number and that is what makes it worth checking. Sample it. Take cells the model calls empty, spread across Highlands, mid-Wales, the Pennines and lowland England, and establish whether an address actually exists there — the ONS postcode directory carries grid references, so this is answerable from published data without a new pull. If the method undercounts, say by how much and fix the weights. If it holds, say so on the page with the check named, because a reader will have the same doubt I do."
>    - "There are white gaps inside the temperature map — visible in the Highlands, mid-Wales, around Manchester. A block with a temperature reading should have a modal class, so those are either missing data or a rendering hole. Find out which and say so on the page if it's genuine. And the density map contradicts its own caption. Almost all of Britain is coloured, while the caption says 53% of land holds a household and the panel below says nearly half holds nobody. The map is drawn in 5 km blocks and the statistic counted in 1 km cells, so a block containing one hamlet colours entirely — the picture and the number are measuring different things and the page presents them as the same. That's the same-figure-on-two-clocks class in visual form. Fix it so the reader sees what the number says: draw at the resolution the claim is made at, or state the resolution on the map and make the claim at block level too."
>    - "I want to understand the household placement properly before we build further on it, because it's foundational and the 47% error shook my confidence in the method rather than just the number. Tell me plainly: what is the actual difficulty? You corrected 47% to 15%, so something in the placement was wrong. Was it the method, the data, or the join — and is the corrected version sound, or is it a better approximation of the same approximation? My concern is that postcodes aren't precise enough for this. A postcode covers roughly fifteen addresses with one grid reference, and in sparse areas it can span a wide area — which is exactly where the error was, and exactly where the weighting matters most for cell counts. So: why not place dwellings directly? OS Open UPRN is free and open — every property in Great Britain with coordinates, about 40 million rows. That removes the centroid entirely. It includes non-residential properties, so a raw count isn't households and needs filtering or scaling against the census total, but that's a tractable problem rather than an approximation. And I don't understand why any of this is expensive. Placing 27 million households into cells is a join, not a computation. If you've estimated it as long-running, tell me the estimate and what dominates it, because I don't believe the compute at this data size. If you've already considered UPRN and rejected it, say why. If the current method is good enough, show me the error it carries rather than asserting it — the household weighting sets the cell counts, and the cell counts are what stage 1 rests on. I'd rather spend a day getting this right than build the world on a simplification nobody has bounded."
>    - "Good — taking the UPRN route rather than defending the centroid was the right call, and the answer not moving is the reassuring outcome. Next is the housing joint, W2_21: fit the joint so a household's attributes hang together rather than being drawn independently — a large detached house in a cold cell with the consumption that implies. Then the space-filling sample, then the people joint conditioning what the demand model already carries. And check the fork dial actually reverted at 02:50 as designed — several commits this morning mention it not being restored at HEAD and the guard's post-expiry behaviour. My allowance reset at 04:00 so the widening should be off."
>    - "I want to be clear what's been answered and what hasn't. You've answered how many weather cells capture 99% of household-weighted variation in the weather drivers — 21, 21 and 5 across three grids. That's a partition of Britain. What I actually care about is heat demand variation, which depends on the weather cell and the house together. So: how many house types are needed to capture 99% of the variation in demand, and how do the two compose? If they're independent it's weather cells times house types and the sample gets large; if they're correlated — and they probably are, since northern housing stock differs from southern — it's much smaller. Measure the joint coverage rather than the two separately. The number I need is how many distinct household cases cover 99% of demand variation, not how many cells cover 99% of weather."
>
> 7. **Pending Tasks:**
>    - Land W2_27 (the joint demand coverage) — the mint content was just built successfully and the land has not been executed.
>    - Write and land a stretch-log entry (`tools/stretch_log.py --check` will otherwise raise a finding).
>    - **W2_22** — the space-filling sample that rejects on outputs (director's stated sequence after W2_21).
>    - **W2_19** — the people joint, "conditioning what the demand model already carries" (director's stated sequence).
>    - `W1_14`'s remaining half: the knowledge page and `tools/generate_weather_cells_data.py` wiring (already done by another lane).
>    - Named residuals: the three-way interaction in NEED unused; Scotland excluded from both the stock joint and the demand-case measurement; EPC-to-fabric map is a declared Choice with unmeasured cost; LDZ/GSP/SAP boundary pull for per-boundary comparators; SAP shelter factor; orientation on solar gain and PV.
>
> 8. **Current Work:**
>    Answering the director's most recent question — how many distinct household cases cover 99% of demand variation, and how weather and house compose. Completed measurements over 24,662,309 England-and-Wales households, 143,511 occupied 1 km cells, and 274 distinct house cases NEED resolves:
>
>    | coverage | weather alone | house alone | product | joint |
>    |---|---|---|---|---|
>    | 90% | 5 | 5 | 25 | 5 |
>    | 95% | 8 | 8 | 64 | 8 |
>    | 99% | 21 | 13 | **273** | **13** |
>
>    Key findings: the joint is 21× smaller than the product; the cause is NOT correlation (region winter temperature vs stock demand at fixed climate = −0.314) but that **demand is a scalar** — shown on a synthetic grid with independent inputs by construction; adding weather sensitivity as a second output axis takes 13 → 21; regional stock at one fixed climate spans 6,405 kWh (London, warmest) to 9,503 kWh (Wales, mild) — 48% — so the alignment with climate is weak and partly backwards; and a lever needs the *inputs* resolved, not the output, so for interventions the product is back.
>
>    The demand proxy was validated against the full 2R2C model: r² = 0.9978, 3.7% residual, `full = 0.899 × proxy + 661`, and coverage is provably invariant to that affine calibration.
>
>    `tools/demand_case_coverage.py`, `tests/tools/test_demand_case_coverage.py` (7 controls: 5 mutation kills, 1 recorded equivalence, 1 survivor closed) and `docs/market_research/thirteen_cases_cover_demand_and_that_is_only_half_an_answer.md` all exist and pass. `tools/write_time_gate` and ruff are clean. The orphan baseline content was built at `$S/orphan_baseline.json` adding `tools.demand_case_coverage` (floor → 373). The W2_27 map content was just built at `$S/mint27b/docs/design/` — `refile()` returned `{'to_closed': ['A49_the_ceiling_comes_before_the_programme_on_r3_and_r4', 'W2_27_how_many_household_cases_cover_demand'], 'to_live': []}`, combined 374,780 with 34,820 headroom. Note the refiler also carried `A49_...` which was already at target in the live half at HEAD — that must be named in the commit message rather than landed silently.
>
> 9. **Optional Next Step:**
>    Land W2_27 via `surgical_land` (backgrounded, since commits take >10 minutes), with `--content` for both map halves and the orphan baseline, naming the incidental `A49_the_ceiling_comes_before_the_programme_on_r3_and_r4` refile in the message; then push and write the stretch-log entry. This directly completes the director's most recent request: *"Measure the joint coverage rather than the two separately. The number I need is how many distinct household cases cover 99% of demand variation, not how many cells cover 99% of weather."* After that, his stated sequence continues: *"Then the space-filling sample, then the people joint conditioning what the demand model already carries."*
>
> If you need specific details from before compaction (like exact code snippets, error messages, or content you generated), read the full transcript at: /home/rich/.claude/projects/-home-rich-synthetic-enterprise/22080be5-e19e-4099-a007-d71c3a6e7845.jsonl
> Continue the conversation from where it left off without asking the user any further questions. Resume directly — do not acknowledge the summary, do not recap what was happening, do not preface with "I'll continue" or similar. Pick up the last task as if the break never happened.

### 2026-09-07T11:46:00.451Z

> ```
> The 13 cases and the three separate weather grids are both wrong,
> and they're wrong the same way. It's the defect you caught
> yourself making on 6 September — "rejecting on outputs is still
> blind if they aren't the outputs anything is scored on" — which
> took N from 100 to 250+. Then coverage got measured on a scalar,
> which is level, and the same collapse appeared on the input side.
>
> On outputs. A cold-and-insulated house and a mild-and-leaky one
> can produce the same annual kWh and be completely different
> customers: different winter-to-summer ratio, different peak,
> different bill shock, different hedge. Gas-heated and
> electrically-heated households at the same total are not the same
> case at all. On a scalar they collapse to one; to a supplier
> they're several.
>
> On inputs. Three separate grids assume a household's response to
> weather is separable, and your own measurement says it isn't:
> solar gain moves fuel -1.2% in a leaky pre-1919 house and -7.9% in
> a tight modern one; wind moves the heat loss coefficient +18.6%
> mid-stock and +2.9% in that same modern house. The response to
> each driver depends on the fabric, so what matters is the joint
> weather condition, not each driver in turn. A glazed house in a
> sunny-but-cold cell and a leaky house in a windy-but-mild cell are
> different demand cases. You called the joint "a question nothing
> here asks" — it is the question, because the sample must span
> differences in response, not averages. That's why I think 987 is
> closer to right than 21/21/5.
>
> The goal, stated plainly, so the measurement has a subject. At the
> end of this the drawn population must reproduce the observed
> distribution of: annual gas, annual electricity, the seasonal
> shape of each, and heating fuel type — gas, electric, other. A
> household is a vector, not a number, and the sample has to span
> the range of those vectors across the stock, including the tails,
> not match their averages.
>
> Re-measure coverage against that. Say how many cases it takes,
> give me 95% and 99% so I can see the price list rather than a
> single number, and say what dominates the count. If the honest
> answer is that the sample has to be much larger than anything
> discussed so far, that's the answer — I'd rather carry a big
> sample than a neat one that can't reproduce the range.
>
> Then go looking for the same collapse elsewhere. Anywhere a
> coverage, ceiling or sufficiency claim rests on a scalar where the
> thing being served is a vector, it's the same defect and it will
> have flattered us in the same direction.
>
> One exception to the standing rule, for this brief only: challenge
> or clarify it before you build. If my reasoning is wrong, or the
> vector I've specified is the wrong one, or 987 is right for a
> reason I haven't given — say so first rather than acting on a
> brief you think is mistaken. This is foundational enough that
> building the wrong thing well is worse than a delay. Once we
> agree the shape, the standing rule resumes: decide, act, record,
> and don't stop.
> ```

### 2026-09-07T12:10:47.832Z

> The console capture is dead. docs/staging/console/ ends at
> DIRECTOR_CONSOLE_2026-09-01.md — six days stale, and everything
> since is missing: the demand vector, the weather work, today.
>
> You built it so my words leave a trace, and it stopped without
> anything noticing, which is the same silent-lapse class as the
> eight-day PROJECT_STATE nulls. Fix it, and make a capture that
> stops writing a finding rather than a silence.
>
> And add the same rule you gave the stretch log: a session that
> takes director input without capturing it is a finding.
