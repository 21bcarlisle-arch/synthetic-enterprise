# B3 — Published Forecast Feed at Multiple Horizons, Delivery-Converging Error — FRAME

**Atom:** `B3_published_forecast_error_horizons` (`docs/design/maturity_map.yaml`, lane
`W1_market_weather`, `level_current: 0`, `level_target: 3`, `loop_stage: idle`,
`provenance: proposal`). Source: `docs/design/BACKLOG.md` §B3 (Wave B, coupled with the
crisis regime the world exists to pose). **DISCOVER/FRAME only — no build code was written
for this pass.** Every claim below cites `path:line` actually read this session; nothing is
recalled from a prior pass.

---

## 1. Verified current state

### 1.1 No published, multi-horizon, error-bearing forecast feed exists anywhere

Grepped `sim/` and `company/` for "forecast" in full. Every `*forecast*.py` file in the tree
is an **internal company projection of its own book**, not an externally-published market
forecast the company *receives*:

- `company/market/load_forecast.py:104` `build_portfolio_forecast()` — the company's own
  MWh volume forecast, built from fixed UK average-consumption benchmarks
  (`_UK_AVG_RESI_ELEC_KWH` etc., lines 7-11) × account counts × a **fixed, deterministic**
  seasonal factor table (`_SEASONAL_ELEC_FACTORS`/`_SEASONAL_GAS_FACTORS`, lines 13-19). No
  horizon parameter, no error/noise term, no convergence-to-delivery behaviour anywhere in
  the file (read in full, 120 lines).
- `company/billing/consumption_forecast.py`, `company/finance/cash_flow_forecast.py`,
  `company/market/ev_demand_forecast.py`, `company/pricing/ncc_forecast_register.py` — same
  pattern by name (grepped, not fully read): each projects the company's own consumption,
  cash, EV uptake, or NCC cost, not an external market signal.
- `sim/flex_dispatch.py:43,101,225` mentions "the company forecasts against its own
  learned/observed estimate" — again the COMPANY's own belief, not a SIM-side published
  artefact.
- `sim/scenario/spine.py:173` is explicit that a scenario's exogenous path "is a scenario
  INPUT, not a forecast the company reads" — the codebase already draws this distinction
  correctly where it appears.
- `company/trading/forward_curve_confidence.py:8` — "forward curves are not forecasts —
  they are market prices for future delivery," the same distinction B3 needs, already
  understood by this file's author.
- The atom's own declared `file_scope` — `sim/forecast_publication.py`,
  `tests/sim/test_forecast_publication.py` — **does not exist on disk** (`find`/`ls`
  confirmed). This atom is genuinely greenfield; B3 is not a mis-registered duplicate of
  anything already built.

**Conclusion: there is no horizon concept anywhere in this codebase today.** The company
does not read a single value in place of a forecast either — it reads no forecast at all.

### 1.2 The closest analogue is NOT a forecast, and it is the "naive 120-day belief" B3 must give a wall to beat

`company/pricing/tariff_engine.py:36` — `COMPANY_LOOKBACK_DAYS = 120`. The class
`CompanyTariffEngine.get_forward_price()` (`tariff_engine.py:269-322`) is the company's
sole forward-price estimator, and it is **entirely backward-looking**: it takes a rolling
mean of trailing OBSERVED spot prices (`price_records` filtered to
`start_lookback <= date <= end_lookback` where `end_lookback = delivery_date - 1 day`,
`tariff_engine.py:308-314`), adds a fixed risk premium + seasonal adjustment, and calls that
its forward-price belief. Docstring at line 287: *"lookback_days: base days back from
delivery_date to look (default 120)."* Confirmed cross-referenced at
`docs/design/THE_MODEL_ON_A_PAGE.md:56` — *"naive forward belief (120-day trailing) it must
outgrow."* This IS the atom's named "naive 120-day belief."

Wired to the wall at `company/interfaces/sim_interface.py:296` (`self._engine =
CompanyTariffEngine()`) and `:320-322` (`get_forward_price()` delegates straight to the
engine). No other forward-price path exists in `sim_interface.py` (grepped for
`get_forward_price`/`tariff_engine`/`CompanyTariffEngine`: three hits, all this one path).

**Point-in-Time Blindfold status on this proxy: HELD.** `tariff_engine.py:308-314` only
ever reads records dated strictly before `delivery_date` — it cannot see the future. But it
also carries **no forward information at all**: its "error" against whatever spot turns out
to be on delivery day is an artefact of staleness (explicitly named in the file's own
docstring, lines 18-23, as the mechanism behind the real 2021-22 under-pricing episode), not
a *designed, calibrated, horizon-shrinking* forecast error. There is no forecast object here
to check for the "reads-truth-directly" epistemic defect (killer pattern: a forecast that IS
the later-realised array) — **because none exists yet**. That specific defect is therefore
not present today, but only because the capability itself is absent; it becomes the live
risk the moment B3 is built (§3 below names the wall explicitly for that reason).

### 1.3 Real-world calibration anchors that exist on disk — partially sourced, honestly gapped

`docs/market_research/WEATHER_FORECAST_ERROR_BY_HORIZON.md` (dated 2026-07-24, live Elexon
Insights Solution API pull, cross-referenced at `docs/market_research/ASSUMPTIONS.md:437-452`)
already GATHERED real forecast-vs-outturn pairs:

- **Demand** (National Demand Forecast `NDF` vs `INDO` outturn), 0-48h: MAE ≈ 1.7-4.2% of
  mean demand (590-1,430 MW stdev), confidence **M** (two independent weeks agree on
  magnitude) — but the doc's own §3 finding states plainly: *"shows no clean monotonic
  growth with horizon in this 2-week sample"* and *"the sample is too short (2 weeks) to fit
  a smooth σ(horizon) curve with confidence."* **No data exists beyond ~30h** — day-ahead
  demand forecast simply does not reach further (§3, "Coverage gap, honestly flagged").
- **Wind** (`WINDFOR` forecast vs `FUELINST` metered outturn), 0-73h: confidence **L→M**,
  the doc's §4 flags a likely **metering-scope confound** (WINDFOR probably includes
  embedded/distribution-connected wind that FUELINST excludes), producing a persistent
  +12.9% to +32% biased MAE that does **not** grow monotonically with horizon. The doc's own
  words: *"Do not feed the raw biased MAE curve into a simulation variable."*
- **Price forecast error: not gathered at all.** The gather covered wind and demand only.
- **Week-ahead / season-ahead forecast error: not gathered at all.** Only day-ahead
  (0-73h max) was pulled; Elexon's day-ahead endpoints do not reach further, and no
  week-ahead/season-ahead series was probed this pass (the gather doc names this as the next
  step, not yet executed).
- `docs/domain_artefact_library/` — grepped for "forecast": **zero hits**. No externally
  sourced accuracy methodology document (e.g. a NESO/Elexon forecast-accuracy
  publication) is on disk anywhere in the artefact library.

**Honest calibration status: PARTIALLY SOURCED, not UNSOURCED, but far short of what B3
needs.** Demand day-ahead has a usable (if short-sample) empirical anchor. Wind day-ahead is
confounded and explicitly flagged as unsafe to feed a build as-is. Week-ahead, season-ahead,
and any price-forecast horizon are **UNSOURCED** — the source that would settle them is a
longer (multi-month, per the gather doc's own recommendation) pull of the same Elexon
endpoints (`WINDFOR`, `NDF`/`TSDF`, `INDO`/`ITSDO`) plus, for week/season-ahead, NESO's
published operational forecasts (not yet probed) and, for price, no known published
UK forecast-accuracy series was identified this session (a genuine open question, not
fabricated).

---

## 2. The named seam

Per CLAUDE.md's typed-flow-seam preference (BACKGROUND_LANE_AND_WALL.md), a new SIM/company
boundary crossing should be a typed, versioned-message adapter, not a bare function call.
The existing precedent for exactly this pattern is `company/interfaces/sim_interface.py`
itself (399 lines, `get_settlement_data`/`get_forward_price`/etc., each a narrow named
method returning a plain dict/float — never a raw SIM object). B3's feed should land the
same way:

- **Producer side (SIM, new):** `sim/forecast_publication.py` (already the atom's declared
  `file_scope`) — generates, for each of the ≥2 horizons (§3), a forecast VALUE plus its
  DECLARED error distribution, keyed by `(variable, horizon, publish_time, delivery_time)`.
  It has NO privileged view of its own future — it is allowed to draw from the same
  mechanism the SIM already uses to generate the eventual outturn, but the published number
  must carry an actual perturbation (see §4), never literally equal the later-realised value.
- **Consumer side (company, new method on the existing seam):** a new
  `SimInterface.get_published_forecast(variable, horizon, as_of)` method alongside the
  existing `get_forward_price` (`sim_interface.py:41,164`) — same pattern, same file, same
  discipline (raises `NotImplementedError` in the base class; a `StubSimInterface`/real
  implementation fills it in). This keeps the wall crossing in the ONE place it is already
  enforced and reviewed, rather than opening a second ad hoc channel.
- **The WALL, stated for this atom specifically (highest-risk part of B3):** the forecast
  producer must never be handed, and the company must never read, the realised outturn the
  forecast is later checked against. Concretely: no import of `sim/forecast_publication.py`
  by anything that also computes the outturn in the same call path without an explicit,
  reviewed as-of boundary — the same discipline `sim/weather_price_chain.py` +
  `company/pricing/weather_price_belief.py` already hold for the W1_6↔C13 pair (see §5).
  Re-use `company/interfaces/point_in_time_view.py`'s existing bitemporal machinery rather
  than inventing a second one (Simplicity Guard, C-S4).

---

## 3. Horizon set proposed, and why

Recommend **three** horizons, not the atom's minimum of two, because the DoD's own
`real_world_twin` text (`maturity_map.yaml:2695`) names all three and the one calibration
anchor gathered so far (§1.3) only covers the shortest:

1. **Day-ahead** (gate-closure horizon, ~24-48h) — the only horizon with any empirical
   anchor today (demand M-confidence, wind confounded). This is the one that should be built
   FIRST, because it is the only one that can be calibrated honestly right now.
2. **Week-ahead** (~7 days) — UNSOURCED (§1.3); needs either a longer Elexon pull (same
   endpoints, wider `publishDateTimeFrom/To` window per
   `WEATHER_FORECAST_ERROR_BY_HORIZON.md:26,28`) or a NESO operational-forecast series not
   yet probed.
3. **Season-ahead** (~90 days, the horizon a fixed-term hedge actually prices against) —
   UNSOURCED; the real-world twin this atom claims to model (NESO's day-ahead/week-ahead/
   season-ahead cadence) does not exist for this atom without it, and it is the horizon
   nearest the "naive 120-day belief" this atom exists to give a wall to.

**Why not just the DoD's minimum two:** a two-horizon (day-ahead + one more) feed can be
built with only the day-ahead anchor in hand, satisfying the letter of the DoD but not the
`real_world_twin` claim already committed in the map. Recommend building day-ahead +
week-ahead first (both genuinely gatherable from Elexon with more volume, no new source
needed) and treating season-ahead as a second BUILD increment once a real season-ahead
source is found — named honestly as a gap, not built on a fabricated anchor.

---

## 4. Error-convergence schedule shape, and its calibration source (or the honest gap)

**Shape recommended:** error magnitude (σ or MAE, NOT raw bias — §1.3's wind finding shows
raw bias is confounded by scope, not skill) parameterised as a monotonically non-increasing
function of `(delivery_time - publish_time)`, sampled from a **calibrated distribution**
per horizon bucket rather than a single deterministic point-error — a real forecast is wrong
by a *distribution*, not a fixed offset, and a fixed offset would make the "error" trivially
learnable and defeat the point of giving the company a genuine wall.

**Calibration source, stated honestly per horizon:**

- Day-ahead demand: `docs/market_research/weather_forecast_error_demand_by_horizon.csv` —
  usable now, confidence M, but the gather doc itself recommends a longer pull before this
  feeds a BUILD decision (`WEATHER_FORECAST_ERROR_BY_HORIZON.md:76-78`). Recommend that
  longer pull (same proven endpoints, more calendar weeks) as the FIRST prerequisite action,
  not fabricating a schedule from the 2-week sample.
- Day-ahead wind: **do not use the raw MAE curve** (the gather doc's own instruction,
  §1.3). If wind forecast error is wanted in the first BUILD increment, use the demeaned
  `stdev(err)` figures instead (flagged in the gather doc as "far more horizon-stable" and
  the safer signal pending the scope-confound resolution) — or defer wind entirely to a
  second increment once the WINDFOR/FUELINST scope question is resolved.
- Week-ahead, season-ahead, and price (any horizon): **UNSOURCED.** No fabricated number
  should enter `sim/forecast_publication.py` for these. The source that would settle each:
  a longer-window Elexon pull (week-ahead demand/wind, same endpoints, if Elexon publishes a
  week-ahead product — not yet confirmed this session) and, for season-ahead and price, a
  dedicated DISCOVER pass is a genuine prerequisite before BUILD, not a blocker to registering
  this FRAME.

This is the R13 split, stated explicitly: **the error-convergence schedule itself is
BASELINE fidelity** — it must be decided by external evidence (Elexon/NESO published
accuracy), blind to company P&L, exactly like `sim/scenario/fidelity_check.py`'s moment
library (`maturity_map.yaml:110`, W1_2's HARDEN history) and `sim/weather_price_chain.py`'s
own fit. It is **never** tuned because the company's naive-belief gap looks too large or too
small once measured — that would be R12/R13 violations of the exact kind this project has
already caught and reverted (`docs/review_gates/done/HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md`).
**The CURRICULUM half is separate and director-owned:** WHICH scenario/regime the company
lives through while facing this forecast wall (calm years vs a 2021-22-style crisis replay,
per `SPINE_1_scenario_world_state`) is the director's instrument, not this atom's — B3
supplies the forecast-error PHYSICS; SPINE_1/SPINE_3 supply WHICH world it is measured in.

---

## 5. The coupled triad — current state and what would need to exist

Applying `docs/design/COUPLED_TRIAD_DESIGN.md`'s three-loop law to B3 honestly, all three
legs are currently EMPTY:

1. **SIM adds depth** — none yet (§1.1): no module emits a forecast-with-declared-error
   object.
2. **COMPANY copes through the wall** — none yet: `CompanyTariffEngine` (§1.2) is not a
   forecast consumer; there is no company code anywhere that reads a published forecast and
   forms a belief from it.
3. **HARNESS measures the gap** — mechanically ready but has nothing to measure. The
   reusable pattern already exists and works: `background/weather_price_triad.py` (full file
   read) + `background/gap_metric.py::prediction_gap` (`gap_metric.py:470-516`) compute
   `gap = MAE(belief, truth) / MAE(climatological-mean, truth)` per cell, worst-cell-scored,
   written via `write_gap_entry` into `docs/observability/coupled_gap_ledger.json`, and
   `background/coupled_triad.py`'s L3-ceiling gate (`coupled_triad.py:1-27`) already refuses
   to let a world atom reach L3 without a measured, non-null gap against a registered company
   twin. **B3 has no entry in `background/coupled_triad.py::_AUTHORITATIVE_COUPLING`
   (`coupled_triad.py:52-80`, checked in full — no B3/forecast-publication key present) and
   no registered company-side twin atom** (grepped every `C1`-`C13` id in the map: none is
   scoped to forecast-belief convergence). This is the concrete, mechanised reason B3 cannot
   reach L3 today even once `sim/forecast_publication.py` exists — the coupling itself is
   unregistered.

**Recommendation (not built here, and not minted — outside this fork's file_scope):**
register a new company-side twin, e.g. `C14_forecast_belief_convergence`, whose job is to
consume `SimInterface.get_published_forecast()` (§2) at each horizon and track how its OWN
error narrows (or fails to) as delivery approaches, in exactly the shape
`weather_price_belief.py`'s docstring already models for its sibling pair (fits ONLY on
observables, holds no SIM state, is ALLOWED to be wrong). The gap this pair measures is
directly the atom's headline claim — *"the company's naive 120-day belief measured against
a real wall on the future"* — so the gap-metric call should compare (a) `tariff_engine`'s
120-day trailing belief against the true forward price, and (b) the new forecast-consumer's
belief against the same truth, at the same delivery dates, so the coupled-triad report shows
whether a genuine published forecast beats the naive trailing mean, and by how much, per
horizon.

### R15 mutation test that would prove the harness gap-measurement can FAIL

Mirroring the pattern already proven for W1_6↔C13 (`weather_price_triad.py:26-30`,
`gap_metric.py:491-493`, both R15 independence-proven): the truth (SIM's forecast-generation
mechanism) and the belief (company's forecast-consumption model) must be **structurally
different machinery**, so recovery of truth by belief would itself be a wall violation, not
a win. Concrete mutation tests to build alongside the feed:

1. **Fail-open on a flat error schedule.** Feed the gap-measurement a `sim/forecast_publication.py`
   stub whose declared error does NOT shrink with horizon (constant σ at every lead time).
   The control MUST fire (report a defect / refuse the "shrinks by a calibrated schedule"
   claim) — if it silently passes, the "monotonically shrinks" DoD clause is unenforced
   (the same class of gap `sim/scenario/fidelity_check.py`'s uninvoked-check finding named,
   `maturity_map.yaml:110`, 2026-07-27 HARDEN entry).
2. **Fail-silent on an unmeasured pair.** If `C14` (or whatever twin is registered) is
   missing from `coupled_triad.py::_AUTHORITATIVE_COUPLING`, the L3-ceiling gate must
   actively BLOCK B3's promotion to L3 (this is already how the mechanism is designed,
   `coupled_triad.py:1-27` — the mutation test is simply asserting B3 stays blocked with no
   entry, and unblocks the instant a real non-null gap is written).
3. **Tautology guard.** The forecast producer and the company's consumer of it must not
   share a coefficient/constant — e.g. if the "error" is drawn from the same RNG substream
   seed as the company's belief update, a shuffle-the-belief-inputs mutation (the exact test
   `weather_price_belief.py`'s own docstring names, "shuffle the belief's weather inputs and
   the gap must worsen") should be re-run here: shuffling the forecast-consumer's inputs must
   worsen its gap, proving the fit is real and not a stored constant.

---

## 6. Exit test for level 3

Level 3 is reached only when ALL of the following are true and verified by a running test,
not asserted:

1. `sim/forecast_publication.py` exposes ≥2 horizons (day-ahead + week-ahead per §3) for
   ≥1 variable (demand or wind, whichever has the cleaner anchor at BUILD time — §1.3
   currently favours demand), each publish carrying a non-zero, non-deterministic error
   whose declared σ/MAE at successive publish times strictly narrows toward the delivery
   date, calibrated against the real Elexon pull (extended per §4, not the 2-week sample
   as-is).
2. `SimInterface.get_published_forecast()` exists on the seam (§2), reads ONLY the published
   forecast object (never the outturn), and a static/epistemic verifier test asserts no
   import of the outturn-producing path from the forecast-consumer's module (mirroring
   `.claude/rules/epistemic-wall-sim.md`'s existing enforcement class).
3. A registered company-side twin (e.g. `C14`, §5) consumes the feed and forms its own
   belief, coexisting with (not replacing) `CompanyTariffEngine`'s naive 120-day trailing
   belief — both are measured against the same truth so the comparison in the DoD's own
   words ("the company's naive 120-day belief measured against a real wall") is a literal,
   quotable number, not a narrative claim.
4. `background/coupled_triad.py::_AUTHORITATIVE_COUPLING` carries a B3 entry, a non-null gap
   is written to `docs/observability/coupled_gap_ledger.json` via the same
   `write_gap_entry`/`prediction_gap` machinery already proven for W1_6↔C13, and the three
   R15 mutation tests in §5 all fire correctly (flat-schedule producer FAILS, missing-coupling
   BLOCKS L3, shuffled-input belief WORSENS).
5. R13 is respected end to end: the error-convergence schedule's calibration constants trace
   to a cited, dated external source (extended Elexon pull or a newly gathered NESO series),
   never to a value chosen because it made the reported gap look better or worse.

---

## 7. Recommendation (stated, not asked)

**Build day-ahead-only first**, using the extended Elexon demand pull as the sole
calibration anchor (defer wind pending the scope-confound resolution named in §1.3), wire it
through the existing `SimInterface` seam (§2) rather than a new channel, and register the
missing company-side twin + `coupled_triad.py` coupling entry (§5) in the SAME BUILD
increment that lands the producer — landing the producer without its twin would repeat the
exact "registered but invisible to the coupled-triad gate" failure mode already documented
for other Wave-B atoms (`docs/design/BACKLOG.md:201-207`, the `blocked_on`/FRAME-saturation
near-misses). Week-ahead and season-ahead are real, named follow-on increments, not silently
dropped scope — proceeding on this recommendation now (PROCEED_BY_DEFAULT: none of the above
is a one-way door; the R13 calibration source and the C-twin registration are logged, not a
values decision).
