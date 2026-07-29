# SPINE_3 — Gas storage stock-and-flow and the endogenous 2021/22 seasonal-spread inversion

**Atom:** `SPINE_3_gas_storage_crisis_regime` (lane `W1_market_weather`, value_stream `wholesale_to_price`, epoch 3,
`provenance: proposal`, `loop_stage: idle`, `depends_on: [SPINE_1_scenario_world_state]`).

**Stage:** DISCOVER (L0→L1) + FRAME (design only). **NO BUILD CODE WRITTEN.** Per EPOCH_GATING_AND_ATOM_AUTHORSHIP
Rule 1 this atom is parked for BUILD; DISCOVER/FRAME is available now. Nothing under `sim/`, `company/`, `saas/`,
`simulation/` or `background/` is created or modified by this pass. The only artefacts are this document and the
atom's map entry.

**Provenance chain:** `docs/design/BACKLOG.md` B2 (Wave B) → `docs/design/SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md`
§C (candidate `SPINE_3_gas_storage_crisis_regime`, "closes F2 + F4, the load-bearing Spec-004 gap") →
`docs/design/BOARD_SPEC_004_RECONCILIATION.md` findings **F2** (regime layer on the wrong axis) and **F4** (gas is
ingested, not formed) + battery item **6** (ABSENT: "Storage absent from gas formation; no winter–summer /
injection–withdrawal logic").

**Sits INSIDE SPINE_1, not beside it.** SPINE_1 (`sim/scenario/spine.py`, BUILT 2026-07-29) already provides the
container: an immutable `ScenarioSpine` holding time-indexed exogenous paths, one of which is literally
`storage_capacity` (`spine.py:69` `PATH_FIELDS = ("gas_trend", "economy_factor", "renewables_buildout",
"storage_capacity")`), a committed per-world curriculum artefact directory, the R13 ratification guard, and the
byte-identical-baseline guarantee. SPINE_3 is **the first consumer of that container** — it does not add a second
scenario mechanism. Its job is to turn `storage_capacity` from an unconsumed exogenous path into the *initial
condition and physical capacity of a state variable the world integrates*.

**Evidence discipline (R9).** Every factual claim below is labelled `observed-with-evidence` (read from a named
file at a named line, or computed this pass from a named on-disk data file) or `inferred`. Nothing is fabricated.
Where a real-world figure could not be verified from a primary source in this environment, it says so.

---

## 1. DISCOVER (L0 → L1) — what actually exists today

### 1.1 How wholesale gas is produced today: **replayed real history**, in the production path

`observed-with-evidence`. In every production simulation phase, gas is a **replayed real monthly series**, not a
scripted path and not a stochastic process.

- `sim/gas_prices_history.py:1-27` (module docstring): the source is **FRED `PNGASEUUSDM`** (IMF "Global price of
  Natural Gas, Europe"), monthly USD/MMBtu, **TTF-based** — explicitly documented as a *proxy* for UK NBP because
  the true NBP source (NGT MIPI `PUBOB603`) requires OAuth. Converted at a **fixed `GBPUSD = 1.28`** and
  `MWH_PER_MMBTU = 0.29307` (`:38-39`).
- `sim/gas_prices_history.py:73-90` `expand_to_daily()`: the monthly value is **repeated once per calendar day**.
  So the "daily" gas series has, by construction, **zero intra-month structure**.
- Persisted at `sim/gas_data/nbp_sap.csv` (`OUTPUT_PATH`, `:36`) — **3,446 daily records, 2016-01-01 →
  2025-06-07** (verified by reading the file this pass).
- `sim/gas_prices_history.py:102` `load_nbp_history()` is what the wall calls:
  `company/interfaces/sim_interface.py:313-315` loads gas records for the company through exactly this function.

**Consequence:** the entire 2021/22 crisis — the run-up *and* the inversion *and* the collapse — is present in the
production path **because it really happened and is being replayed**. This is Spec-004's "path 1" (BOARD_SPEC_004
lines 28-35) and its finding **F5**: the tail phenomena pass *in-window by ground truth*, not by formation.

### 1.2 Is the winter-2021/22 inversion SCRIPTED anywhere? **No — and that is the finding**

`observed-with-evidence`. A full sweep of `sim/` for a hardcoded 2021/22 shock returns **nothing**:
`grep -rn "crisis|2021-2022|2021_22" --include=*.py sim/` returns only docstring prose
(`forward_curve.py:7`, `gas_scenario_generator.py:25-26`, `risk_engine.py:19-21,47-48`,
`intraday_shape.py:31-32`) and unrelated identifiers (`risk_committee_rules.py:18 CRISIS_SIGMA_THRESHOLD`). There
is **no branch, no month table, no date-keyed multiplier and no replayed synthetic crisis path** that manufactures
the inversion.

There are exactly **three** places a crisis-shaped thing lives, and none of them scripts the inversion into a
formed price:

| # | Artefact | What it is | Does it produce the inversion? |
|---|---|---|---|
| 1 | `sim/gas_data/nbp_sap.csv` | Real replayed TTF-proxy history | **Yes — by being the real record.** Not scripted; not formed. |
| 2 | `sim/scenario/curriculum/crisis_2021_22.yaml:26-33` | Director-curriculum anchor paths: `gas_trend` 84 → **226** → 130 p/therm (2021/2022/2023) and `storage_capacity` **1.0 (2021-06) → 0.75 (2021-10) → 0.35 (2022-03)** | **No — it is scripted but INERT.** See 1.3. |
| 3 | `sim/scenario/gas_scenario_generator.py:99-176` | The synthetic forward-scenario generator (2026-2030) | **No — it cannot express a seasonal spread at all.** See 1.4. |

### 1.3 The one scripted crisis path is consumed by **nothing**

`observed-with-evidence`. `crisis_2021_22.yaml` is a genuinely hardcoded price-and-storage trajectory — the closest
thing in the tree to "the inversion is scripted." But **no SIM generator reads it**:

`grep -rn "paths_as_of|ScenarioSpine|resolve_grid_label" --include=*.py sim/ company/ saas/ background/ tools/`
returns, outside `spine.py` itself, exactly **one** importer: `background/run_rotation.py:58`
(`from sim.scenario.spine import ScenarioSpine, resolve_grid_label`), which binds a rotation cell to a world
label for **ledger stamping**. No price generator, no `price_engine`, no `weather_price_chain`, no
`forward_curve`, no `gas_scenario_generator` calls `paths_as_of` (`spine.py:169`). SPINE_1's own map note says
this in as many words: *"no SIM generator consumes paths_as_of yet, so no run actually LIVES through a
non-baseline world"* (`maturity_map.yaml:2611`).

Additionally, `crisis_2021_22.yaml:11-13` carries `provenance: proposal`, `ratified: false`, `in_rotation: false`,
so even the ledger path refuses it: `spine.py:262 rotation_set()` excludes it and `:322 select_for_rotation()`
raises.

**So: the scripted trajectory exists, is director-authored, is unratified, and is dead code-path. The thing
SPINE_3 exists to replace is not currently doing anything — which means SPINE_3's job is a genuine
build-from-nothing, not a rip-and-replace.**

### 1.4 The synthetic gas generator has **no seasonality whatsoever**

`observed-with-evidence`. `sim/scenario/gas_scenario_generator.py:150-169` is the whole price loop. For each day
it draws a regime (`in_lower_regime = rng.random() < params.lower_mode_fraction`, `:155`), then
`rng.gauss(lower_regime_mean, ...)` or `rng.gauss(upper_regime_mean, ...)`, then applies a dunkelflaute multiplier
on scheduled days, then floors at `price_floor`. **The calendar month is never consulted.** `current_date` is used
only to write the `settlementDate` string (`:172`).

`inferred` (arithmetic, from the code above): the expected seasonal spread of any generated gas scenario is
**exactly zero plus sampling noise**, in every named preset (`GAS_SCENARIOS`, `:53-96`). The generator cannot
produce a normal winter premium, so *a fortiori* it cannot produce an inversion of one. Note also `:153-155`: the
regime is re-drawn i.i.d. every day (the comment calls it a "Markov chain" but there is no persistence term in
the gas generator — the persistence lives in the sibling `bimodal_generator.py`, not here).

### 1.5 The only "seasonal shape" in the tree is a **static company belief table that cannot invert**

`observed-with-evidence`. `sim/forward_curve.py:82-88` `_GAS_FALLBACK` / `:88` `GAS_MONTH_SEASONAL_MULTIPLIER`
(loaded preferentially from `sim/data/seasonal_calibration.json`, `:46,:50-58`) is a **fixed 12-entry dict**:
Jan 1.0526 … Jul 0.8882 … Dec 1.2939. `sim/data/seasonal_calibration.json` states its own methodology: *"Per-year
monthly/annual ratio, mean across years 2016-2024. Includes 2021-2022 energy crisis."*

Two things follow, both load-bearing:

1. `inferred`: **averaging across nine years dilutes the one inverted year into invisibility.** 2022's inverted
   shape is one of nine terms; the mean table still has Dec > Jul. The table is winter-premium **by
   construction and permanently**.
2. `observed-with-evidence`: this table lives in `forward_curve.py`, which is the **company's forward belief
   pricer** (`generate_forward_price`, `:138`), reached through the wall at
   `sim_interface.py:320-322 get_forward_price`. It is *not* price formation. BOARD_SPEC_004 line 61 scores this
   exactly: *"a static calibrated table in the company's forward belief pricer, not storage physics"* — verdict
   **ABSENT**.

`inferred`, and this is the sharpest company-side consequence: **the company's forward belief is structurally
incapable of representing an inverted seasonal spread.** A dict multiplied into a price cannot change sign of the
winter-summer difference. In a crisis world the company will be wrong in a specific, predictable, mechanical way —
which is exactly what the coupled triad wants (§2.6) and exactly what kills it in B6 (§2.7).

### 1.6 What gas currently drives

`observed-with-evidence`. Gas is the anchor of electricity price formation:
`sim/price_engine.py:110-128 gas_floor_price()` = `(gas + carbon·EF_GAS_TCO2_PER_MWH_TH) / thermal_efficiency`
(`THERMAL_EFFICIENCY = 0.50`, `:89`), fed into `:131 system_margin_price()` (residual-demand scarcity multiplier
`A0 + A1·x + A2·max(0, x − X_TIGHT)²`, `:99-103`), composed by `:189 synthetic_price()`. So **anything SPINE_3 does
to gas propagates into power by the existing spark-spread arithmetic with no new coupling code** — the transmission
channel gas→power already exists and is R15-tested. This is a strong reason SPINE_3 is the highest-leverage
wholesale atom: one new state variable moves the whole stack.

`observed-with-evidence`, an omission worth recording: the carbon limb defaults to `0.0` at
`price_engine.py:113` and every live call leaves it there (BOARD_SPEC_004 row `1.CARBON`, PARTIALLY MET). SPINE_3
does not fix this and must not pretend to.

### 1.7 What the real record actually says — computed this pass, not recalled

`observed-with-evidence`. All figures below were computed **this pass** from `sim/gas_data/nbp_sap.csv` (the real
replayed series described in 1.1). They are £/MWh monthly means of that series.

**(a) Realised seasonal spread, trading definition** — Winter(Oct *y* … Mar *y+1*) minus the **following**
Summer(Apr *y+1* … Sep *y+1*), i.e. the Win-*y* / Sum-*y+1* pair a desk quotes:

| pair | winter | summer | spread |
|---|---|---|---|
| W2016/17 – S2017 | 13.79 | 14.11 | −0.32 |
| W2017/18 – S2018 | 19.04 | 21.00 | −1.96 |
| W2018/19 – S2019 | 19.12 | 10.11 | +9.01 |
| W2019/20 – S2020 | 9.67 | 5.91 | +3.76 |
| W2020/21 – S2021 | 15.60 | 34.05 | **−18.45** |
| **W2021/22 – S2022** | **84.93** | **119.37** | **−34.44** |
| W2022/23 – S2023 | 60.18 | 29.19 | +30.99 |
| W2023/24 – S2024 | 28.67 | 28.54 | +0.13 |

**A methodological warning that must survive into BUILD** (`inferred`, from the table above): on a strongly
*trending* series a realised winter-vs-following-summer difference is **contaminated by the trend**. W2020/21 –
S2021 reads −£18.45 not because summer 2021 carried a scarcity premium but because the level was rising
monotonically through 2021. A naive acceptance test on this statistic would pass on *any* monotonic run-up. This
is a trap, and it is why the primary criterion below is the detrended one.

**(b) Detrended seasonal shape** — for each calendar year, the ratio of the seasonal mean to that year's own annual
mean (the same per-year month/annual-ratio methodology `sim/data/seasonal_calibration.json` already declares).
Trend-neutral by construction:

| year | annual £/MWh | winter ratio (J-M, O-D) | summer ratio (A-S) | **shape spread W−S** |
|---|---|---|---|---|
| 2016 | 11.60 | 1.060 | 0.940 | +0.119 |
| 2017 | 15.31 | 1.078 | 0.922 | +0.156 |
| 2018 | 21.10 | 1.005 | 0.995 | +0.009 |
| 2019 | 11.88 | 1.149 | 0.851 | +0.298 |
| 2020 | 8.47 | 1.302 | 0.698 | +0.605 |
| 2021 | 42.40 | 1.197 | 0.803 | +0.394 |
| **2022** | **100.02** | **0.807** | **1.193** | **−0.387** |
| 2023 | 34.34 | 1.150 | 0.850 | +0.300 |
| 2024 | 29.03 | 1.017 | 0.983 | +0.034 |

**2022 is the only year in the decade with a negative shape spread**, and it is not marginal: −0.387 against a
2016-2024 positive range of +0.009 … +0.605. Summer 2022 traded **19.3% above** its own annual mean while winter
2022 traded **19.3% below**. This is the cleanest available signature of the event and it is trend-free.

**(c) The collapse leg** (this matters for B6 more than the spike does): 2022-08 = £186.54 → 2022-10 = £55.47,
a **−70.3% fall in two months**, the sharpest move in the series. Peak month of the whole record is 2022-08.
Run-up leg for contrast: 2021-03 £16.54 → 2021-12 £99.60 = **6.0×** in nine months.

**(d) Reconciliation with the FRAME's cited figure.** `SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md:169` cites the
advisor decade review at **−£29.7** for the 2022 inverted spread. This pass computes **−£34.44** for the same event
on the on-disk series under the trading definition (and −£38.70 under a same-calendar-year definition, −£70.82 on
Q1-vs-Q3). `inferred`: the two numbers describe the same real event under different window/series conventions
(the advisor may have used real NBP rather than the TTF proxy, or a different window). **They are not
reconciled**, and BUILD must not treat either as a point target — see §2.4, which is why the tolerance is a band
and why the *sign and shape* criteria lead.

**(e) A standing caveat on all of (a)-(d)** `observed-with-evidence`: these are **realised monthly spot averages**,
not traded seasonal *forward* spreads. No historical forward-curve data exists anywhere in the tree
(`sim/forward_curve.py` *constructs* a belief from spot; it does not ingest quotes). A realised-average seasonal
spread and a quoted Win/Sum forward spread are different objects. Every acceptance figure in §2.4 is therefore
defined on the realised-average object and must be labelled as such wherever it is published.

### 1.8 DISCOVER verdict

**Scripted today:** nothing that forms a price. The one hardcoded crisis trajectory
(`crisis_2021_22.yaml:26-33`) is unratified, out of rotation, and read by no generator.
**Real today:** the whole crisis, replayed, in `nbp_sap.csv`.
**Absent today:** any storage state variable, any injection/withdrawal economics, any intertemporal coupling, any
seasonality at all in the synthetic gas generator, and any mechanism by which a seasonal spread could change sign.
This matches BOARD_SPEC_004 battery item 6 (**ABSENT**) and finding **F4** exactly, verified independently against
disk rather than inherited from that document.

---

## 2. FRAME (design — nothing built)

### 2.0 The governing constraint, inherited

**BC-1** (`WHOLESALE_VALUE_CHAIN_FRAME.md:155`): *"prices move because the underlying drivers move — price is an
emergent output of fuel + residual demand; never a hand-drawn shape."* SPINE_3 is BC-1 applied one level deeper:
**the gas price itself must become an emergent output of a physical balance, never a hand-drawn path.** The single
disqualifying outcome for this atom is a build in which any calendar month, any date, or any scenario label
appears in the price arithmetic.

### 2.1 The stock-and-flow

**State variable.** `S_t` — European working gas in store, in TWh. One aggregate European stock (not per-country,
not per-facility: SIMPLICITY GUARD). Bounded `0 ≤ S_t ≤ C_wg`, where `C_wg` is aggregate **working-gas capacity**
(a published physical constant, see R13 split).

**Balance.** The daily system balance is `B_t = Supply_t − Demand_t`:

- `Supply_t` = `pipeline_t + lng_t + indigenous_t`. Three named terms, because Spec-004 `1.GAS.LNG` records the
  absence of the LNG/global-marginal-cargo channel as its own gap and the shock in §2.4 acts on exactly one of
  these terms.
- `Demand_t` = `heating_t + power_burn_t + industrial_t`.
  - `heating_t` is **HDD-driven** and therefore already coupled to the existing weather engine
    (`sim/weather_hdd.py`, `sim/weather_price_chain.py`). This is the joint-driver limb (Spec-004 `1.JOINT`,
    MET) extended to gas: one weather draw must move heating gas demand, power demand and wind together.
  - `power_burn_t` is the **feedback limb**: gas-fired generation is dispatched by the merit order
    (`price_engine.py:131 system_margin_price`), so a still cold day raises power-sector gas burn, which draws
    the same stock. Spec-004 row `1.JOINT` flags this loop as *implicit today, not formed*. Closing it is what
    makes level, volatility and correlation move **jointly** — Spec-004 finding **F2**.

**Transition.** With injection `I_t ≥ 0` and withdrawal `W_t ≥ 0`:

```
S_{t+1} = S_t + I_t − W_t
I_t     = min( r_inj_max(S_t),  max(0,  B_t + A_t) )
W_t     = min( r_wd_max(S_t),   max(0, −B_t) )
```

**The physical bounds are the whole design, not decoration.** Both rate limits are functions of the fill level,
and they run in **opposite directions**:

- `r_inj_max(S)` **falls as the store fills** — injecting against rising reservoir pressure gets harder. The last
  10% of fill takes disproportionately long.
- `r_wd_max(S)` **falls as the store empties** — deliverability is pressure-driven, so a depleted store cannot
  deliver at its rated rate. `inferred`, and this is the load-bearing nonlinearity: **a low-stock winter is not
  merely short of gas, it is short of *deliverability*.** A linear stock model without this asymmetry will
  under-produce the crisis and is the single most likely way a BUILD gets this wrong while looking correct.

`A_t` is **anticipatory injection demand** — the refill-race term, §2.3(a). It is the only term that is not a
physical flow, and it is where belief becomes flow (Spec-004 §4.FLOW).

**Scale-readiness (C-S2/C-S5).** The transition is a deterministic first-order difference equation with its own
named RNG substream if any stochastic term is added; replaying a history reproduces `S_t` identically. Time-scale
invariance must be **declared**: the recursion is daily-indexed and the rate limits are per-day, so re-basing to a
different clock requires rescaling both — register that as a named simplification per C-S5 rather than pretending
invariance.

### 2.2 Transmission: stock → wholesale gas price

The price must depend on **scarcity of the stock relative to what the remaining season requires**, never on the
calendar.

**Security margin.** At time `t`, let `R_t` = expected remaining withdrawal-season draw from `t` to the end of the
withdrawal season, evaluated under **normal-weather climatology** (not under the realised weather — that would be
foresight). Then

```
M_t = S_t − R_t                (TWh of cover above expected requirement)
m_t = M_t / C_wg               (dimensionless, the scarcity coordinate)
```

`m_t` is high when the store comfortably covers the season ahead, and goes negative when it does not. Note that
`m_t` is well-defined in **summer** too: in summer `R_t` looks forward across the *coming* winter, which is what
makes a summer scarcity premium expressible at all.

**Price.**

```
P_t = P_marginal_source(t) × Φ(m_t)
```

- `P_marginal_source(t)` — the delivered cost of the **marginal molecule**, i.e. the global LNG netback. This is
  the "priced at the margin of a global market" limb of Spec-004 `1.GAS.STOCKFLOW`.
- `Φ(m)` — a **convex scarcity multiplier**, deliberately the same functional *shape* as the electricity engine's
  residual-demand multiplier (`price_engine.py:99-103`, `A0 + A1·x + A2·max(0, x − x_tight)²`), reflected so it
  rises as `m` falls. `Φ → 1` when cover is comfortable; rises convexly as `m → 0`; steepens without bound as the
  deliverability constraint `r_wd_max(S)` binds.

**Why this shape and not a new one** (`inferred`, a design argument, not a fact): reusing the merit-order
multiplier form means the gas market and the power market are scarce in the same mathematical language, the
existing calibration technique transfers, and a reviewer can check one form instead of two. SIMPLICITY GUARD:
no new price-model family is introduced.

**What must NOT appear in this arithmetic:** the month, the date, the scenario `world_id`, or any value read from
a curriculum artefact other than physical constants and the shock term. If a BUILD needs a month to make the
seasonal spread work, the mechanism has failed and the spread is scripted again.

### 2.3 Transmission: price → seasonal spread, and the mechanism of INVERSION

The seasonal spread is a **forward-market object**. For a delivery season `σ`:

```
F(σ) = E[ P_marginal_source(t) × Φ(m̂_t) ]_{t ∈ σ}  +  premium(σ)
```

where `m̂_t` is the **projected** security margin along the expected stock trajectory (projected under normal-weather
climatology from today's `S_t` — strictly no future information; the Point-in-Time Blindfold applies to the
projection exactly as it applies to everything else).

`Spread = F(Winter) − F(Summer)`. **It is computed, never written down.**

**Why the normal year has a positive spread.** At the start of injection season the store is low but the whole
summer is ahead at high injection rates and there is no heating draw, so projected summer `m̂` is comfortable and
`Φ(summer) ≈ 1`. Across winter the store draws down, `m̂` tightens, `Φ(winter) > 1`. Hence `F(W) > F(S)`. The
storage operator's own arbitrage — buy summer, inject, sell winter — is what *caps* the spread at roughly cost of
carry plus capacity value, and it emerges from the same equations rather than being imposed.

**Why a low-stock year INVERTS it.** Two endogenous channels, both consequences of §2.1's bounds:

**(a) The refill-race channel — the primary mechanism.** If the store exits winter abnormally low, and a target
fill `S*` must be reached by the start of the next withdrawal season, the *required* injection rate is

```
r_req = (S* − S_t) / days_remaining
```

When `r_req` approaches or exceeds what the ordinary summer balance `B_t` supplies, the shortfall becomes
**additional summer demand** `A_t` competing for the same marginal LNG cargo. Summer `m̂` tightens, `Φ(summer)`
rises, `F(Summer)` rises. This is *fear-as-injection-demand* — Spec-004 §4.FLOW, scored **ABSENT** with the note
*"requires a gas storage state to even express."* It is expressible here, and it is the crisis's actual economics:
the summer is scarce because everyone is buying at once to be safe by November.

**(b) The deliverability-cap channel — the amplifier.** Because `r_inj_max(S)` *falls* as the store fills, the last
increments toward `S*` are the slowest. A high target therefore forces the race to start earlier and run harder,
pushing the extra demand further into early summer and widening the affected window. Without the fill-dependent
injection bound, channel (a) alone produces a late, weak, brief summer premium.

**And the winter leg falls.** Once the store is (expensively) full by the start of the withdrawal season, projected
winter `m̂` is *restored to normal*. So `F(Winter)` does **not** rise proportionally. `F(W) − F(S)` collapses and
can cross zero. **That is the inversion, and no line of code decided it.**

**The same mechanism produces the collapse (§1.7c), which is the part B6 needs.** When the store reaches `S*`, the
refill demand `A_t` **disappears discontinuously**. Summer `Φ` returns to ~1 within days. The price crashes. The
real record shows exactly this: −70.3% from 2022-08 to 2022-10. A design that reproduces the spike but not the
crash is not merely incomplete — it removes the thing that actually killed suppliers (§2.7).

**Structural claim to be falsified at BUILD, stated now so it can be:** the sign of the spread is determined by
whether the *summer* or the *winter* is the scarcer season, and a large enough prior-winter supply shock makes it
the summer. If a BUILD cannot invert the spread without a calendar term, this FRAME is wrong and the finding is
reported as a finding (R4), not patched with a month table.

### 2.4 The defined supply shock, and the stated tolerance

**The shock — one term, one direction.** A **persistent multiplicative reduction in the `pipeline_t` supply term**,
parameterised by `(onset_date, magnitude, ramp, persistence)`. That is the **entire** exogenous input. Storage
drawdown, the refill race, the summer premium, the spread inversion and the post-refill collapse are all
consequences. Nothing else about the crisis world may be set by hand.

**R12 / anti-goal-seek — the binding clause.** The shock magnitude must be set from the **externally observed real
supply reduction** (an external fact about pipeline flows), **never solved backwards from the target spread.** If
an honestly-sourced shock produces a spread outside the acceptance band, **that is a finding about the mechanism
and triggers R4 (diagnose), never a cue to retune the shock.** Tuning the shock until the spread lands in the band
is goal-seeking dressed as calibration and would make the acceptance test a tautology at the parameter level —
subtler than, and just as fatal as, the code-level tautology in §2.8.

**Acceptance criteria.** Three legs, in priority order. All are evaluated on the world's **own emitted** gas price
series; all targets come from §1.7, computed from the real on-disk record.

| leg | criterion | target | source |
|---|---|---|---|
| **A — SIGN (primary, non-negotiable)** | the **detrended shape spread** (winter ratio − summer ratio, per §1.7b methodology) for the shock year is **strictly negative** | `< 0` | Real record: 2022 is the **only** year 2016-2024 with a negative shape spread |
| **B — MAGNITUDE (band, not a point)** | detrended shape spread within the band | `−0.55 … −0.20` | Observed 2022 = **−0.387**; band = ±~0.17, wide enough to bracket definitional variation and to exclude every non-crisis year (max observed positive-year magnitude toward zero is +0.009) |
| **B′ — LEVEL cross-check (secondary)** | realised trading-definition spread, W(shock year) − S(following) | `−£20 … −£70/MWh` | Observed −£34.44 (this pass, on-disk series) and −£29.7 (advisor decade review, `SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md:169`). **The band is deliberately wider than the £4.7 discrepancy between the two independent computations of the same real event** — a tolerance narrower than the disagreement between measurements of the target would be false precision |
| **C — TRANSIENCE (regime, not re-parameterisation)** | the shape spread is **positive in the year before** the shock and **positive again in the year after** | before `> 0`, after `> 0` | Real record: 2021 = **+0.394**, 2022 = −0.387, 2023 = **+0.300** |
| **D — COLLAPSE (required by B6, §2.7)** | maximum 2-month fall in the emitted price, within the shock window | `≤ −50%` | Observed 2022-08 → 2022-10 = **−70.3%** |

**Leg C is what makes this a regime rather than a re-parameterisation** — and it is also the cheapest thing to get
wrong. A mechanism that inverts the spread and *leaves* it inverted has not modelled a crisis; it has modelled a
different world. The real record snaps back in one year.

**What is deliberately NOT an acceptance criterion:** the absolute price level (£226/therm, £186/MWh peak). Level
is a curriculum-adjacent quantity driven by the shock magnitude and the global LNG netback; making it a pass
condition would re-import the goal-seek the clause above forbids. Level belongs in the diagnostic report (R12:
diagnostic, never target).

**Provenance discipline for every number above:** legs A/B/B′/C/D are all computed from
`sim/gas_data/nbp_sap.csv`, which is real IMF/FRED TTF-proxy data (1.1) with a documented proxy caveat (it is TTF,
not NBP) and a documented resolution caveat (monthly, expanded to daily, §1.7e). Both caveats must be restated
wherever a SPINE_3 figure is published. **Nothing here is recalled from memory or fabricated.** Real-world figures
that would strengthen the calibration but could **not** be verified from a primary source in this environment —
and which BUILD must fetch rather than assume — are named in §3.

### 2.5 R13 — the baseline / curriculum split (the wall on this atom)

**BASELINE — physics, agent-buildable, changed only for fidelity-to-reality, decided blind to company P&L:**

1. The stock-and-flow recursion itself (`S`, `I`, `W`, the bounds, §2.1).
2. The **shapes** of `r_inj_max(S)` (falling with fill) and `r_wd_max(S)` (falling with depletion) — reservoir
   physics, externally calibrated.
3. Aggregate working-gas capacity `C_wg` — a published physical constant.
4. The demand decomposition (heating HDD-driven, power-burn merit-order-driven, industrial) and its coupling to
   the existing weather chain.
5. The security-margin definition `m_t` and the functional form of `Φ` (§2.2).
6. Calibration of `Φ` to the real 2016-25 record — under R12: calibrated for fit-to-reality, never toward a
   company outcome.
7. The forward-formation rule `F(σ)` and the seasonal-spread **definition** (§2.3).
8. The acceptance-test machinery, the oracle, and the R15 mutations (§2.8) — including the detrending methodology.

**CURRICULUM — director-reserved. The agent must NOT set these, and a BUILD that sets them has crossed the wall:**

1. **The shock magnitude, onset date, ramp and persistence.** Which world the company lives through is the
   director's. (`crisis_2021_22.yaml:11-14` already encodes this: `ratified: false`, `true_probability: null`.)
2. **The fill target `S*` and its deadline.** This is a **policy intervention** in the world — precisely
   Spec-004 §3.INTERVENTION ("government intervention is now part of the price state space"). A policy is a
   director-authored world-fact, not a physical constant. `A_t` is a *mechanism*; `S*` is a *value*.
3. Rotation eligibility, `true_probability`, `sampling_weight`, `ratified` for `crisis_2021_22` — already
   structurally director-reserved by `spine.py:262/322`.
4. **The choice of which historical event is the calibration target.** That 2021/22 is the target is a director
   decision (it is in BACKLOG B2). *What actually happened in 2021/22* is not a decision at all — it is the
   record, and therefore the tolerance in §2.4 is **baseline/fidelity**, not a difficulty dial. This is a
   deliberate, narrow disagreement with the atom's existing map note, which currently classes "the target
   2021/22 inversion shape/tolerance" as curriculum (`maturity_map.yaml:2630`). **Recorded as an open question
   for the director (§3, Q1) rather than silently resolved.** If he rules the tolerance is curriculum, the
   acceptance band moves to a curriculum artefact and the agent stops owning it — a one-line change, and this
   FRAME is written so that either ruling works.

**Does any part of SPINE_3 fall the way `W1_2_generate_futures` did?** `W1_2` was found to be **content =
curriculum, mechanism = agent** — "generating new scenario CONTENT is CURRICULUM = the director's R13 instrument;
only the MECHANISM is agent-buildable." **Yes, one sub-part falls exactly that way, and it must be said plainly:**

> **The `storage_capacity` path values currently in `crisis_2021_22.yaml:30-33` (1.0 → 0.75 → 0.35) are
> CURRICULUM CONTENT and the agent may not author, tune or "improve" them.**

But there is a sharper point than the ownership one. **Under this design that field's *meaning* changes.** A
director-authored storage *trajectory* is a scripted answer to the very question SPINE_3 exists to make the world
answer — if the world is told what storage did, the inversion is scripted again, one layer down. Under §2.1 the
storage trajectory must be an **output**. The `storage_capacity` path should therefore be reinterpreted as either
(a) the **initial condition** `S_{t0}` plus the physical capacity `C_wg` (both baseline facts, small and static),
or (b) removed in favour of the shock parameters, which produce the trajectory. **That reinterpretation is a
director call (§3, Q2) — the agent must not repurpose a curriculum field unilaterally.**

**The residue of SPINE_3 after this split is large and genuinely agent-buildable.** Unlike `W1_2` — where the
mechanism already existed and only content remained, making a BUILD draw wrong — SPINE_3's mechanism half (items
1-8 above) is **entirely unbuilt**. This atom is not a W1_2-shaped no-build. It is a real build, waiting on its
gate.

### 2.6 The coupled triad

**SIM (this atom).** Owns `S_t`, the balance, the shock, and the endogenous spread. `S_t` is a simulation internal.

**COMPANY — what it discovers through the wall.** It cannot read `S_t`. It observes:

- The **published gas price series** at the existing seam (`sim_interface.py:313-315`, `:320-322`) — spot and, once
  B4/`WVC_2` lands, per-tenor forwards.
- Its **own book**: hedge positions, bills, cash, margin postings.
- **Published storage data.** A design decision, flagged as a reversible judgement call: in reality EU storage
  fill is *public* — GIE publishes it, and every real gas desk watches it. The epistemic test in CLAUDE.md is
  *"could a real UK energy supplier know this?"*, and the honest answer is **yes**. So the company **may** receive
  a storage feed — but as a **typed, versioned, lagged, aggregated publication event** across the wall
  (typed-flow-seam preference; C-S3: a publication is an asynchronous event), carrying: reporting lag, EU-aggregate
  granularity only, and no forward information about the shock. The wall here is **lag, aggregation and absence of
  foresight — not blindness.** It is *not* a read of `S_t`, and `spine.py`'s import-direction wall (FRAME §R15 W1)
  is unchanged: no `company/**` or `saas/**` module may import `sim.scenario.*`, and no `ScenarioSpine` field may
  cross `sim_interface.py`. Flagged for the director as **Q3 (§3)**: strict blindness (prices only) is the
  alternative, and it is a legitimate difficulty choice — it is his.

**HARNESS — the gap it measures.** Reported per digest into `docs/observability/coupled_gap_ledger.json` alongside
the existing pairs:

1. **Seasonal-spread belief gap** — the company's implied winter-vs-summer expectation versus the world's realised
   spread. `inferred`, and this is the *predicted* headline finding: because
   `forward_curve.py:88 GAS_MONTH_SEASONAL_MULTIPLIER` is a static positive-winter dict (§1.5), **the company's
   belief cannot change sign.** In the crisis world the gap will be large, structural, and one-directional. That
   is the correct outcome — the company is allowed to be wrong, and the gap *is* the score.
2. **Storage-state belief gap** — the company's inferred storage tightness (from the lagged published feed, if
   Q3 resolves that way) versus true `S_t`.
3. **Regime-recognition latency** — how long after onset the company's forward belief stops assuming a positive
   spread. This is the F2 "containable-after-onset" test made measurable.

**Coupled-triad law.** SPINE_3 may not reach L3 until the company has been run against it and these gaps measured;
B6 may not be called complete until it has faced this world. Neither reaches L3 alone.

### 2.7 What SPINE_3 must supply for B6 to be testable

`B6_collateral_cash_death_loop` `depends_on: [SPINE_3_gas_storage_crisis_regime]` (`maturity_map.yaml:2645`). B6
needs a world whose *price movement* — not price *level* — can exhaust cash. The concrete supply contract:

1. **A daily per-tenor forward mark, not just spot.** Variation margin is computed against a *moving forward* for
   the tenors the book actually holds. A spot-only series gives B6 nothing to mark against. This is the direct
   dependency on `B4_traded_product_ladder` / `WVC_2` — **B6 needs SPINE_3 *and* a product ladder; SPINE_3 alone is
   necessary but not sufficient, and that should be said before BUILD opens rather than discovered inside it.**
2. **The COLLAPSE leg, not only the spike.** A supplier that has bought cover is **long** forward gas; margin calls
   arrive when the forward **falls**. The real killer sequence is the 2022-08 → 2022-10 crash (−70.3%, §1.7c)
   against a book bought at the peak. **A world that only spikes cannot kill B6.** Acceptance leg D (§2.4) exists
   for exactly this reason and is not optional.
3. **Speed, as a first-class acceptance quantity.** The cash crisis is driven by `ΔF/Δt`, not `F`. The maximum
   30-day forward move in the shock world must be reported as a headline diagnostic and must be of the order of
   the real record. A slow drift to the same level produces no death loop.
4. **Daily emission cadence with a separate settlement clock (C-S3).** Margin calls are asynchronous events:
   the call, the payment deadline and the payment are separate events in time, never same-step resolution. SPINE_3
   must emit a mark at a cadence B6 can post against, with the payment lag owned by B6 and not collapsed into the
   mark.
5. **Survivability in both directions.** Per B6's own DoD, a test must prove the crisis can **both kill and be
   survived**. SPINE_3 must therefore be parameterisable to a *milder* shock — but per §2.5, the choice of
   magnitudes is the director's curriculum, and the agent supplies only the knob.

### 2.8 R15 obligations at BUILD — and the tautology trap, which is the real risk here

No control counts as evidence until a mutation test proves it fires on its own named defect.

**THE TAUTOLOGY TRAP, named concretely.** The failure mode for this atom is a check whose "did the inversion
happen" oracle is derived from the same series that produced it. Three specific forms to refuse:

- **T1 — the parameter tautology.** A test asserting the computed spread matches an `expected_spread` field in a
  curriculum artefact, where the generator reads the same field. The check re-asserts an assignment.
- **T2 — the arithmetic tautology.** "Assert storage fell, then assert price rose", where `P = f(S)` by
  construction. This re-asserts the code's own arithmetic and **cannot fail while the code compiles**. It looks
  like a two-step causal test and is not one.
- **T3 — the self-oracle.** Deriving the acceptance band from the generated series itself (e.g. "the shock year's
  spread must differ from the mean of the generated years"). The oracle must be **external to the generator**.

**The independence rule that avoids all three:** the **checked value** is computed from the world's emitted price
series; the **oracle** is computed by a separate function whose *only* inputs are `sim/gas_data/nbp_sap.csv` (the
real record — a file the generator neither reads nor writes) and a date window. Enforced by an explicit test that
the oracle module imports neither the generator nor `sim.scenario.spine` — independence made mechanical, not
asserted.

**Named defects and their required mutations** (each must go **RED**):

| id | named defect | mutation | must go RED on |
|---|---|---|---|
| **M1** | **The inversion is not caused by the shock** (it is scripted or incidental) | Set the pipeline-shock magnitude to zero, leaving the scenario label, the world_id and every other parameter intact | Legs A + B. If they stay green, the inversion did not come from the shock — the strongest single control here |
| **M2** | **The storage state is decorative** (price does not actually depend on the stock) | Freeze `S_t` at its initial value (make the stock a constant) | Legs A + B |
| **M3** | **The deliverability asymmetry is missing** | Make `r_wd_max` independent of `S` (constant withdrawal rate) | Leg B (the magnitude must fall out of band) |
| **M4** | **The refill race is missing** | Set `A_t ≡ 0` (no anticipatory injection demand) | Legs A + B — this is the *primary* inversion channel; if A/B survive without it, the inversion is coming from somewhere unintended |
| **M5** | **The regime is permanent, not transient** | Make the shock persist past its stated duration | Leg C |
| **M6** | **No collapse leg** | Remove the discontinuous disappearance of `A_t` at `S*` (ramp it to zero over the season) | Leg D — the B6-killer |
| **M7** | **The control cannot distinguish worlds** (bidirectionality) | Run the acceptance test against the **baseline `history_replay`** world and against a **null-shock** run | The test must **FAIL** on null-shock (spread positive) — a control that passes on every world is not a control |

**Fail-open guards** (each must be a **FAILED** check, never a silent pass): an empty or short emitted price
series; any non-finite value in the series (reject non-finite **first**, before any comparison — comparison guards
are NaN-blind); a missing or empty `nbp_sap.csv` oracle file; a shock window with no overlap with the emitted
series; a detrending denominator (annual mean) at or near zero.

**Fail-silent guards:** if the oracle function raises, or the real-record file cannot be read, the check has
**FAILED** — an unavailable check is a failed check, never skipped-green.

**Inherited from SPINE_1, unchanged and still binding:** W1 (the import-direction wall test), W2 (the
byte-identical `history_replay` baseline golden hash — SPINE_3 must not perturb the baseline world by one byte),
W3 (curriculum-not-tuning: no code path lets a company-P&L outcome write back a scenario value).

**A note on where R15 does not reach.** The R12 clause in §2.4 — "the shock magnitude must never be solved
backwards from the target spread" — is a **process** discipline, not a mechanised one, and no mutation test can
catch its violation (a back-solved magnitude produces a green suite by construction). The honest mitigation is to
require that the shock magnitude cite an **external source for the real supply reduction** in the curriculum
artefact, so a back-solved number is at least *visible* as an uncited one. Recorded as a known limit rather than
papered over.

---

## 3. Open questions for the director (none block DISCOVER/FRAME; all block BUILD)

- **Q1 — Is the acceptance tolerance (§2.4) baseline or curriculum?** This FRAME argues **baseline**: what happened
  in 2022 is a fact of the record, not a difficulty dial. The atom's current map note classes it as curriculum.
  The FRAME works under either ruling; it should not stay ambiguous into BUILD.
- **Q2 — What becomes of `crisis_2021_22.yaml`'s `storage_capacity` path (§2.5)?** Under this design a
  director-authored storage *trajectory* would re-script the answer. Reinterpret as initial condition + capacity,
  or remove in favour of the shock parameters? Curriculum-field semantics are the director's.
- **Q3 — Does the company get a lagged published storage feed, or strict price-only blindness (§2.6)?** A real desk
  watches GIE storage data, so the feed is defensible on the epistemic test; strict blindness is a legitimate
  harder curriculum. Director's call.
- **Q4 — BUILD ordering with B4.** B6 needs a per-tenor forward (§2.7.1). Should `B4_traded_product_ladder` open
  before or alongside SPINE_3, given B6 depends on both?

**Real-world figures BUILD must FETCH, not assume** (`observed-with-evidence` that they are currently unsourced —
`docs/market_research/scenario_spine_and_friction_anchors_2026-07-23.md:145-160,228-229` records each as a live
gap after failed fetches this project has already attempted): the EU storage-fill regulation's exact numeric
targets and regulation number (mechanism corroborated, primary EUR-Lex text returned an empty body); GIE AGSI+
actual EU storage fill levels (endpoint returned 200, content not parsed); EU aggregate working-gas capacity; GB
storage capacity versus EU peers (the post-Rough context is well known but was **not** independently fetched);
and the real magnitude of the pipeline-supply reduction, which §2.4 makes load-bearing. **None of these are
asserted anywhere in this document as fact, and none may be filled from recall at BUILD.**

---

## 4. Level and saturation

**`level_current` HELD at 0. Not a claim of zero work — a refusal to move a cell the agent does not own.**

The DISCOVER half (§1) is complete to the L1 bar: the mechanism is established against disk with file:line
evidence, the "is it scripted?" question is answered with a negative verified by sweep, and the real acceptance
targets are computed from the real record rather than recalled. The FRAME half (§2) is complete to the L2 bar for
*design*: state variable, bounds, transmission, inversion mechanism, quantified tolerance with sources, the R13
split, the triad, the B6 contract, and R15 mutations with the tautology trap named.

But **nothing is built** — the L2 bar is "mechanically real AND mutation-tested", and this atom's `loop_stage` is
`idle`, so claiming L2 for analysis would be an unearned level. Separately, `tools/level_promotion_gate.py`
refuses *any* unauthorized `level_current` increase at commit time (MATURITY_MAP.md §0: the director and advisor
own levels; the agent proposes with evidence and never moves a cell), and R16 forbids `--no-verify` on a
`level_current` change. A level-up proposal to **L1** is filed in
`docs/observability/level_up_proposals.jsonl` with this document as its evidence.

**Precedent followed:** `H29_import_time_env_capture_test_isolation`, which completed DISCOVER and FRAME, **held
`level_current` at 0**, filed an L2 proposal, and closed its re-draw treadmill by promoting its FRAME to a real
artefact rather than by bumping a level.

**Saturation.** This document is listed in the atom's `evidence:` list. `supervisor._atom_has_frame_doc`
(`background/supervisor.py:814`) marks an idle atom FRAME-saturated only when an `evidence` entry under
`docs/design/` with `FRAME` in its **filename** resolves to a real non-empty file — an inline FRAME in the map's
`simplifications` list is a YAML string and does **not** saturate, so an inline-only FRAME would re-hand this atom
to the idle draw every tick forever. **Only this atom's own FRAME is cited.** A sibling's FRAME is never listed:
on 2026-07-29 exactly that fail-silent defect was found and fixed on this atom (the shared
`SCENARIO_SPINE_AND_TRADING_FRICTION_FRAME.md` had been listed here, making an unframed atom read as framed and
dropping it from the draw entirely — see the evidence-line comment at `maturity_map.yaml:2633`). The mechanism's
own docstring states the assumption: *every non-canonical `*_FRAME.md` is owned by exactly ONE atom.* This one is
owned by `SPINE_3_gas_storage_crisis_regime`.

The atom leaves the idle DISCOVER/FRAME pool and re-enters via the BUILD draw when its gate opens (`loop_stage`
flips off `idle`, `depends_on: SPINE_1` satisfied). No orphan transition, no permanent hold.
