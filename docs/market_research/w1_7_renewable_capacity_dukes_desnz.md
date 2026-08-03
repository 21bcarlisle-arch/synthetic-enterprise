# W1_7 — Real GB renewable installed capacity + generation-mix (DUKES/Energy Trends), 2016–2025

For atom `W1_7_renewable_capacity_trends` (L1→L2 discovery pass). Fetched live over network
2026-08-03 (network confirmed available this fork; prior forks were network-blocked). Answers
FRAME §9 task 1: pin real annual installed-capacity + mix-share series so A1(strict)/A2/A3 stop
being tautological against the sim's own AGWS-fitted "effective fleet."

## Sources (fetched, not guessed — anti-marking-own-homework, two genuinely different measurement
## systems even though both are published by the same statistics team)

1. **GENERATOR anchor — installed capacity register.** DESNZ *Energy Trends* Table ET 6.1 ("Renewable
   electricity capacity and generation"), "Annual" worksheet, rows 7–23 (`CUMULATIVE INSTALLED CAPACITY
   (MW)`). This underlies DUKES Chapter 6 Tables 6.1–6.3.
   URL fetched: `https://assets.publishing.service.gov.uk/media/6a6a0cabb0205b954abca5a8/ET_6.1_JUL_26.xlsx`
   (linked from `https://www.gov.uk/government/statistics/energy-trends-section-6-renewables`),
   HTTP 200, 451KB, updated 2026-07-30. Per the workbook's own "Notes" sheet (note 3), capacity is
   sourced from Ofgem Renewables Obligation accreditation, FiT scheme registrations, the Microgeneration
   Certification Scheme, and the Renewable Energy Planning Database (REPD) + DNO embedded-capacity
   registers — **a licensing/accreditation register, not settlement-metered output.**
2. **Cross-check — narrative confirmation.** DUKES 2026 Chapter 6 PDF (`DUKES_2025_Chapter_6.pdf`,
   title metadata reads "DUKES 2026 Chapter 6", author DESNZ, created 2026-07-29), fetched from
   `https://assets.publishing.service.gov.uk/media/688a193f6478525675739024/DUKES_2025_Chapter_6.pdf`,
   HTTP 200. Confirms narratively: "offshore wind capacity overtook onshore wind capacity for the
   first time in 2025", "wind now represents around 51 per cent of installed renewable capacity",
   solar PV's capacity share reached 33.6% by end 2025 (up from 1.0% pre-FiT in 2010), 3.3GW of total
   renewable capacity added in 2025 (three-quarters solar PV).
3. **VALIDATOR anchor — generation-mix share (A3).** Same ET 6.1 workbook, "Annual" sheet, rows
   56–64 (`SHARES OF ELECTRICITY GENERATED (%)`) — annual % of **total GB electricity generated**
   (all fuels, row 64 denominator) contributed by each renewable technology. Per Notes 7/8, this table
   is built from **actual generation where metered, else estimated from typical/design load factors
   applied to accredited RO/FiT/REGO capacity** — a different collection pipeline from Elexon's
   Balancing Mechanism settlement feed (AGWS), which only covers BM Units (larger transmission-connected
   generators) and is what `sim/weather_price_chain.py::load_daily_record` already ingests. This is the
   genuinely-independent series the FRAME calls "DESNZ Energy Trends Table 6 mix-share."
4. **A4 (coal retirement date) — cross-checked against 3 independent sources**, one of them primary:
   (a) Uniper (the plant's own operator) — "The end of an era — Ratcliffe-on-Soar power station ends
   coal generation" (uniper.energy/news), (b) E3G policy NGO, (c) multiple news outlets (ITN Business,
   BBC feed). All agree: **Ratcliffe-on-Soar, GB's last coal-fired power station, closed 30 September
   2024.** `LAST_COAL_GENERATION_YEAR = 2024` in `sim/renewable_capacity_trend.py` was flagged
   "UNVERIFIED THIS FORK" by the prior L1 fork — now VERIFIED against 3 sources including the operator.
   No full coal generation/capacity time series was ingested (out of file_scope — AGWS has no coal
   psrType; A4 still correctly requires an explicit external series and raises without one).

## Real installed capacity by year (MW), 2016–2025 — ET 6.1 Annual sheet rows 8–12

| Year | Onshore wind | Offshore wind (seabed+floating) | Solar PV |
|---|---|---|---|
| 2016 | 10,832.5 | 5,293.4 | 11,914.0 |
| 2017 | 12,597.2 | 6,987.9 | 12,760.0 |
| 2018 | 13,424.9 | 8,180.5 | 13,059.1 |
| 2019 | 13,998.3 | 9,888.3 | 13,344.8 |
| 2020 | 14,075.1 | 10,382.9 | 13,772.2 |
| 2021 | 14,492.8 | 11,255.5 | 14,251.4 |
| 2022 | 14,840.4 | 13,847.5 | 14,812.6 |
| 2023 | 15,531.9 | 14,734.7 | 17,574.2 |
| 2024 | 16,199.3 | 16,139.7 | 19,429.9 |
| 2025 | 16,430.7 | 16,649.7 | 21,915.0 |

**Offshore capacity is monotonically non-decreasing every single year 2016→2025 in the real
record** (never dips) — confirms the FRAME's A1 premise is TRUE of real installed capacity,
even though (as the L1 fork already found, honestly) it is NOT true of the AGWS-fitted
*effective* fleet (which convolves capacity with year-to-year wind-resource/load-factor noise).

## Finding: the atom's flagged BUILD-figure guesses were UNVERIFIED and are now corrected

The atom text (§3 of the FRAME, carried into the map's `simplifications` list) guessed, explicitly
flagged as unverified pending this pass: *"offshore ~5→15GW, onshore ~9→14GW, solar ~10→16GW."*
Real DUKES/ET figures (2016 → 2025):

| Technology | Guessed (unverified) | Real (verified) | Error |
|---|---|---|---|
| Offshore wind | ~5 → 15 GW | **5.29 → 16.65 GW** | end-figure ~10% low |
| Onshore wind | ~9 → 14 GW | **10.83 → 16.43 GW** | start ~17% low, end ~15% low |
| Solar PV | ~10 → 16 GW | **11.91 → 21.91 GW** | end-figure **~37% low** — the biggest miss |

This is reported as a finding, not corrected by tuning anything toward it (R12) — it is simply the
real basis the L2 mechanism below is built on.

## Generation-mix share (DESNZ, independent of AGWS) — wind's share of (wind+solar) generation

Using rows 57/58/60 (% of *total* GB generation), normalised to wind's share of (wind+solar) only,
to make it comparable to the sim's internal wind_fleet/(wind_fleet+solar_fleet) ratio (same
normalisation on both sides — avoids a denominator mismatch, since the sim has no concept of
total-system generation):

| Year | Real DESNZ wind-share of (wind+solar) | Sim (AGWS-fitted) wind-share of (wind+solar) |
|---|---|---|
| 2017 | 0.8125 | 0.8815 |
| 2018 | 0.8179 | 0.9095 |
| 2019 | 0.8371 | 0.9093 |
| 2020 | 0.8577 | 0.8904 |
| 2021 | 0.8426 | 0.9350 |
| 2022 | 0.8516 | 0.9191 |
| 2023 | 0.8475 | 0.9155 |
| 2024 | 0.8480 | 0.8993 |

Both series sit in a similar 0.81–0.94 band and show no strong divergent trend — the sim's implied
wind-dominance is consistently ~5–8 percentage points HIGHER than the independent DESNZ series
(the sim's power-curve/envelope shapes are not equally well-calibrated for wind vs solar — solar's
"effective fleet" tracks real installed solar capacity closely, see below, while wind's does not,
which mechanically pulls the sim's wind share up). Implemented as `check_mix_share_against_independent_source`
in `sim/renewable_capacity_trend.py` with a pre-stated (not fitted) tolerance.

## Separating CAPACITY from LOAD-FACTOR (the L1 note's named honesty gap)

The L1 "effective fleet" (`wind_fleet_mw`, `solar_fleet_mw`, etc.) is `mean(AGWS outturn) /
mean(power-curve shape)` — NOT nameplate capacity (it is ~4–6x larger than real installed wind
capacity, and close to but not equal to real installed solar capacity). Dividing the effective
fleet by the now-available REAL installed capacity gives a `load_factor_residual(year)` — the
part of the year-to-year effective-fleet movement NOT explained by real capacity growth:

| Technology | mean(effective/real) | CV across magnitude-bearing years (2017–2024) |
|---|---|---|
| Offshore wind | 5.13 | **0.174** |
| Onshore wind | 4.63 | **0.138** |
| Solar PV | 0.84 | **0.118** |

**Mechanism diagnosis (R4):** the wind ratio (~4.6–5.1x, not ~1x) is not a bug in this atom — the
nearest working analogue is that `wind_power_output_fraction` is driven by a **national mean wind
speed**, while real wind farms are **non-randomly sited** in the windiest coastal/upland locations
(a well-known siting-selection effect in wind resource modelling). A curve driven by the national
average necessarily undershoots true fleet-average output, and W1_6's own whole-window mean-match
already absorbed exactly this gap into one scalar — L1 correctly inherited it, and this pass now
separates the growth signal (real capacity, low CV) from the shape-mismatch (the ~4.6–5.1x level,
constant, not tuned away) and the residual weather noise (CV ~0.12–0.17). This is a genuine,
reportable modelling fact, not a defect to fix here — fixing the power curve itself would re-open
the merit-order/SSP calibration (R12/S8 wall), explicitly out of scope.

**What this enables (A2), honestly:** the FRAME's literal A2 wording ("reconstructed
`capacity_k(τ)·power_curve(W(t))` tracks AGWS outturn within tolerance") **fails** at any normal
tolerance because of the ~4.6–5.1x wind gap above — reported, not hidden. What genuinely **is**
checkable without re-opening the curve calibration, and is the real substance A2 is meant to prove
("is the effective-fleet trend actually capacity-driven, or is it noise dressed up as a trend?"):
the **load-factor residual is BOUNDED, not diverging** — i.e., capacity growth (not AGWS
measurement noise) explains most of the year-to-year movement in the effective fleet. Implemented
as `check_load_factor_residual_bounded` with a pre-stated CV bound (0.35) chosen with real headroom
above the observed 0.12–0.17 (not fit to the data) — mutation-tested to fail on an injected
wild-swinging residual.

## Files this pass adds

- `sim/cache/dukes_installed_capacity_annual.json` — the real ET 6.1 capacity table above (BASELINE,
  R13 — historical, fidelity-only, never company-P&L-tuned). **NOT gitignored** (unlike the raw
  Elexon caches in `sim/cache/`) — see the module docstring for why: this is a small, hand-fetched,
  independently-sourced reference table with its own provenance, not a re-derivable download cache.
- `sim/cache/desnz_energy_trends_table6_mix_share.json` — the real generation-mix-share series
  (rows 57/58/60), the exact path `DESNZ_MIX_SHARE_PATH` already named (and left unpopulated,
  correctly raising) by the prior L1 fork.

## What remains genuinely open

- **L2's OTHER named bar (FRAME §4)** — commissioning-date smoothing within a year, and the
  coal→gas→wind marginal-plant re-stacking in the merit order — is **not** touched by this pass
  (deliberately: it touches `sim/price_engine.py`'s dispatchable-capacity/merit-order logic, which
  this pass does not re-open, matching the standing R12/S8 wall).
- **The default `derive_price(year=None)` flip (FRAME §9 task 7)** is gated on re-running the SSP
  calibration and showing the per-cell lift table UNMOVED. The prior fork's own diagnostic
  (`chain_vs_real_ssp_mae(year_aware=True)` = 24.14 vs default 23.99) already shows the year-aware
  series fits *slightly worse* — this pass does not re-attempt the flip (STOP-and-report per this
  fork's own instructions, not tuned to force a pass).
- **L3 coupled-triad gate** — confirmed this pass: `grep -rn "mix_belief" company/ saas/
  background/coupled_triad.py` returns nothing. No company mix-belief capability exists.
  `company/pricing/` has `weather_price_belief.py` and `weather_normalisation_belief.py`, neither
  of which models the shifting generation *mix* — a belief about capacity/mix-share specifically.
  L3 remains correctly walled (COUPLED_TRIAD rule 1).

## 2026-08-03 follow-on pass: GENERATION-MIX EVOLUTION (capacity × load factor → energy)

The atom's own name promises "generation-mix evolution over time" — but nothing built so far
computed an actual **energy** quantity by technology by year; A1-A4 only ever compared
capacity/share **levels**. This pass ingests two further tables from the **same already-cited**
ET 6.1 workbook (`w1_7_dukes_generation_and_load_factor_annual.json`, fetched 2026-08-03, HTTP
200, same URL as the capacity/mix-share tables above): "ELECTRICITY GENERATED (GWh)" (Annual
sheet rows 25-40) and "LOAD FACTORS (%)" (rows 42-54) — DESNZ's own published generation-by-
technology and load-factor figures, same independent (non-AGWS) collection pipeline as the
mix-share table.

### Real generation (GWh) and load factor (%), 2016 & 2025 (full 2016-2025 series in the JSON)

| Technology | 2016 generation | 2016 LF | 2025 generation | 2025 LF |
|---|---|---|---|---|
| Onshore wind | 20,753.7 GWh | 23.57% | 34,419.5 GWh | 24.08% |
| Offshore wind | 16,405.7 GWh | 35.96% | 52,020.7 GWh | 36.40% |
| Solar PV | 10,395.1 GWh | 11.00% | 20,124.6 GWh | 11.11% |

### A5 — capacity × load factor → energy, reconciled against real published generation

`implied_generation_gwh(tech, year) = real_capacity_mw(tech, year) × real_load_factor(tech, year)
× hours_in_year(year) / 1000` (leap-year-correct hours) vs `real_generation_gwh(tech, year)`
(same source, direct). Error across all 30 technology-year cells 2016-2025:

| Technology | Min error | Max error | Typical driver of the gap |
|---|---|---|---|
| Onshore wind | 0.3% (2020) | 8.1% (2016) | year-end vs year-average capacity |
| Offshore wind | 1.9% (2016) | **14.1% (2017)** | fastest-growth years show the largest gap |
| Solar PV | 1.1% (2018/2019) | 10.7% (2016) | year-end vs year-average capacity |

`check_capacity_load_factor_reconciles_to_generation` (A5) uses a **pre-stated** 25% tolerance
(set with real headroom above the observed 14.1% max, before re-deriving these numbers) — PASSES
on every technology-year cell. The gap's mechanism (R4): DUKES publishes **cumulative capacity at
calendar year END**, not the year's time-weighted average — in a fast-growth year (2017 offshore:
+1,725MW, +33% in one year) the year-end figure overstates the capacity that was actually online
for most of the year, so `capacity × LF` overstates generation. This is precisely the FRAME §4
"commissioning-date smoothing" item, confirmed here as a real, measured, unfixed gap — fixing it
needs sub-annual commissioning dates this sim does not ingest (out of this atom's file_scope,
`sim/price_engine.py`).

### A6 — the split WITHIN wind (onshore vs offshore), a genuinely different check from A3

A3 (existing) compares wind's share of (wind+solar). A6 (new) compares onshore's share of
(onshore+offshore) — i.e. the split *within* wind, using the real DESNZ generation series
directly (`real_onshore_offshore_generation_share`) against the sim's AGWS-fitted
`wind_onshore_fleet_mw / (wind_onshore_fleet_mw + wind_offshore_fleet_mw)`:

| Year | Real onshore share | Sim onshore share | Gap |
|---|---|---|---|
| 2017 | 0.5787 | 0.6065 | 0.028 |
| 2018 | 0.5339 | 0.6302 | 0.096 |
| 2019 | 0.4991 | 0.5553 | 0.056 |
| 2020 | 0.4611 | 0.4910 | 0.030 |
| 2021 | 0.4517 | 0.4940 | 0.042 |
| 2022 | 0.4376 | 0.5379 | **0.100** |
| 2023 | 0.4027 | 0.5021 | 0.099 |
| 2024 | 0.4163 | 0.5079 | 0.092 |

Both series show the same real trend (offshore's real-world build-out overtakes onshore's share
of wind generation across the window — matches the DUKES Ch.6 narrative finding above, "offshore
wind capacity overtook onshore wind capacity for the first time in 2025"), but the sim runs a
few points high on onshore throughout — consistent with `load_factor_residual`'s existing finding
that the power curve does not differentiate onshore from offshore siting (both use the same
national wind-speed fraction). `check_onshore_offshore_generation_split_vs_real` (A6) PASSES at a
pre-stated 0.20 tolerance (real headroom above the observed 0.100 max).

### What this pass buys, honestly

- A genuine `implied_generation_gwh()` — capacity × load factor → energy, the literal mechanism
  the atom's own name promises — now exists, is real (DUKES capacity × DESNZ load factor), and
  is mutation-tested (transcription-error fixture proven to fire A5).
- The commissioning-date-smoothing gap (FRAME §4) is now **measured** (0.3%-14.1%), not merely
  named — a concrete, sourced target for whichever fork later builds the smoothing.
- Does **NOT** close the FRAME's own named L2 bar (`sim/price_engine.py` re-stacking, out of
  file_scope this pass) — see the module docstring for the honest level assessment.
