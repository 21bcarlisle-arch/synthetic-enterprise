# DIRECTOR STEER — Weather simulation: purpose, variable selection order, forecast layer (2026-07-23)

**Provenance:** Director-decided in advisor conversation 2026-07-23, advisor-staged. This is a PURPOSE
steer for the W1 weather lane — it re-frames what the lane is for and how its variable set is chosen.
It authorizes no BUILD, opens no gate, moves no level. Existing ratified levels (W1_3/W1_4/W1_5/W1_6/C13
at L3) are unaffected. Mechanisms, sequencing, and file design are CC's.

---

## 1. What this lane is (decided)

The W1 lane is the **weather simulation itself** — nothing else. Prices, premise demand, and gross
margin are the *consumers* of the weather, and they define what "great" means, but they are not this
lane's scope. Scope discipline: when a piece of work in this lane starts modelling price formation or
demand response, it has left the lane.

Why the lane matters (context, not scope): renewables share rises every year, so weather's grip on
wholesale prices tightens every year; premise demand is hugely weather-dependent; and weather risk is
one of the top considerations when a retailer sets fixed prices. A stationary, tame weather world makes
every downstream claim soft.

## 2. The order of work (decided — this is the key steer)

**Gather → correlate → select → simulate.** Do not pick simulation variables by intuition:

1. **Gather the data** that lets candidate weather variables be correlated against the consumers
   (price, demand). Much of the outturn side already exists (the W1_6 chain fit and C13 regression are
   correlation evidence: temp/HDD ≈ 55% of daily demand variance; gas+temp+wind ≈ 93% of derived
   price). The genuinely ungathered data is the **forecast archive**: NESO/Elexon publish day-ahead
   (and other horizon) wind and demand forecasts alongside outturns. Forecast-vs-outturn pairs are the
   ONLY way to measure error-by-horizon — outturn data alone cannot reveal it, however long the record.
2. **Correlate and select**: measure each candidate variable's incremental explanatory power against
   the consumers. Judge on **tail explanatory power, not average R²** (the existing worst-cell
   discipline). A variable that adds nothing to average fit but explains the cold-still corner earns
   its place; the reverse does not.
3. **Simulate only the variables that earn their place.** Parsimony is the explicit design test:
   minimum number of variables for maximum efficacy of real-world simulation *including real-world
   uncertainty and error*.

## 3. Requirements on the simulator (decided as requirements; how is CC's)

**Variables (starting candidate set, subject to §2 selection):** temperature; wind INCLUDING ramps
(30-minute structure matters, not just daily means); solar/cloud (cloud cover is essential if
predicting 30-min solar rather than averages — already half-hourly in the engine, keep it).

**Structure:**
- National signal + local deviation, resolvable **anywhere in GB**. Current segments are the first
  sample points, never the frame. New segment, new place — no rebuild. (The 4-location calibration set
  is a known limitation; national datasets and the GSP/DNO-style keyed partition are the portable frame.)
- Persistence at synoptic AND blocking-high (multi-week) scales — duration drains storage, not depth.
- The still-and-cold compound (built, validated — preserve it; note the F2 single-wind-series caveat).
- Genuine interannual winter-to-winter variability, measured against the real high-single-digit swing.
- Extremes at the right FREQUENCY, not just reachable depth (current reach_fraction 12–32% is the gap).

**Trends:** the warming trend carried WITHOUT thinning the extremes; volatility/tail shape allowed to
drift. A stationary decade is wrong twice over — wrong about the climate, and wrong about weather's
growing share of price formation as renewables grow.

**The forecast layer (new, first-class):** the same variables as *forecasts* at multiple horizons —
seasonal normals months out, through day-ahead, to within-day — with realistic error that shrinks
toward delivery. No downstream consumer ever decides on outturn; weather risk on a fixed tariff is
priced off forecasts and their error. Forecast error is the natural epistemic wall on the future:
forecasts are genuinely public (company-knowable), outturn arrives only at delivery — no artificial
blinding needed. Anchor σ(horizon) on the real published forecast-vs-outturn pairs from §2.1.
Generator and validator anchors must remain independent sources (standing anti-marking-own-homework rule).

## 4. Held in mind, NOT in scope now

- EU/adjacent-country weather (still weather; will matter when interconnector exposure enters the
  consumers' world). Roadmap awareness only.
- The consumers themselves (price formation through renewables, premise heating/cooling/solar-gain
  demand physics, weather-risk pricing on fixed tariffs) — they are the fitness function this lane is
  judged against, not this lane's work.

## 5. Decided vs open

**Decided:** lane scope (weather only); the gather→correlate→select→simulate order; tail-weighted
variable selection; parsimony as the design test; the forecast layer as first-class; anywhere-in-GB
portability as a design constraint; trends carried without thinning extremes.

**Open (CC's):** mechanisms throughout; which forecast horizons to model; the region partition;
how ramps are represented; sequencing against the existing W1 backlog and the spike-tail defect;
whether existing atoms absorb this or new atoms are authored.

## 6. Risk

**Touches:** W1 lane framing and future sequencing only — doc-only steer, no code, no map edit.
**Blast radius:** re-ranking of W1 work; possible re-framing of premise-fidelity refinements
(they drop in priority under this lens — supporting cast to the national drivers).
**Probable failure mode:** being read as BUILD authorization or as invalidating ratified levels — it
is neither; gates and levels are untouched, and BUILD authority remains the standing gate model.
**Mitigation (inline):** treat this as re-rank input for the next draw sequencing; where it conflicts
with an existing FRAME doc, surface the conflict as a director finding, do not silently resolve.
