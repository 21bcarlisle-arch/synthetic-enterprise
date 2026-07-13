> **[PARKED to in_progress/ 2026-07-13]** FRAME COMPLETE: design doc authored (docs/design/WEATHER_PHYSICS_HIERARCHY_DESIGN.md, FRAME fork) + 9 atoms registered on the maturity map (W1_3..W1_6 hierarchy L1-L4, C13 weather-normalisation coupled twin, W1_7..W1_10 explicitly-later follow-ons).
> **BLOCKING SUB-ITEM:** the L1-L4 BUILD is epoch-gated to **Epoch 3** (opens after Epoch 2 exit test) per the directive's own sequencing (sits with W1_2_generate_futures). DISCOVER/FRAME is done; BUILD does not start until Epoch 3 opens.
> **UNBLOCKS WHEN:** Epoch 3 opens for BUILD.

# WEATHER PHYSICS — coherent national, feasible local, premise-level shape (P1, QUEUE)

**Staged:** 2026-07-13 by advisor, **director-decided**. Disposition: QUEUE
(DISCOVER/FRAME may start immediately — thinking is never gated). Epoch: sits with
W1_2_generate_futures (Epoch 3), which currently has NO local/regional dimension
at all — this fills that hole BEFORE the futures engine is built, so the
locational layer is native rather than retrofitted.

**Director's framing, verbatim:** *"To start let's just have a coherent national
weather and energy price signal, with feasible local weather, driving premise
level shape. With correlations and randomness. Then we can get down to the full
detail, renewable trends etc afterwards. Let's start with the physics!"*

## The hierarchy (this is the requirement; the mechanism is yours)
Four layers, each conditional on the one above. **The word that does the work is
COHERENT: lower layers must be consistent with the layer above, not independently
drawn.**

**L1 — NATIONAL WEATHER (coherent, autocorrelated).**
Temperature, wind, solar irradiance as a joint national signal. Not iid daily
draws: weather PERSISTS (cold spells last; still spells last). Temporal
autocorrelation is physics, not noise.

**L2 — LOCAL/REGIONAL WEATHER (feasible, spatially correlated, AGGREGATION-CONSISTENT).**
Regions deviate from national — but **feasibly**:
- **Spatial correlation:** neighbouring regions covary. Cornwall and Aberdeen do
  not get independent draws.
- **AGGREGATION CONSISTENCY (the "feasible" test, and it must be an invariant):**
  the population/demand-weighted aggregate of regional weather must RECONCILE to
  the national signal. A world where every region is freezing while the national
  figure is mild is incoherent and must be impossible by construction, not by
  luck. **Make this a testable invariant, mutation-tested (R15).**

**L3 — PREMISE-LEVEL SHAPE.**
Each property's half-hourly shape is a function of ITS LOCAL weather and its own
characteristics (thermal performance, heating type, occupancy, archetype), plus
idiosyncratic noise. Randomness is layered, not flat: national signal + correlated
regional deviation + premise-specific response + idiosyncratic noise.
**Invariant: aggregate premise demand must reconcile to national demand.** If the
premises don't add up to the country, the physics is wrong.

**L4 — PRICE SIGNAL (the physics chain closes).**
national weather -> national demand + renewable output -> merit order -> wholesale
price. Price is an OUTPUT of the physics, never an independent draw.

## THE CORRELATION THAT MATTERS MOST (do not miss this)
**Cold and still go together.** The coldest GB days are blocking-high days: low
wind, high heating demand, tight margin, price spikes. If temperature and wind are
drawn independently, **the tail that actually kills suppliers never occurs** —
every hedge looks fine and the world is a lie. The joint distribution must carry
this dependence. It is the single most important correlation in GB power, and it
is the reason a naive sim under-prices winter risk.
(Same family: solar is anti-correlated with heating demand seasonally and
diurnally; wind droughts persist for days.)

## Anchoring — independence rule (R: anti-marking-own-homework)
- **GENERATOR anchors** and **VALIDATOR anchors must be DIFFERENT SOURCES.**
- Generator: real historical weather/demand relationships.
- Validator: independent published statistics (e.g. sub-national energy
  consumption statistics, regional degree-day data, published system demand) —
  NOT the series the generator was fitted to.
- The company inside the wall must NEVER validate against SIM ground truth.

## The wall, and the gap this creates (coupled-triad: this is the point)
**What the company CAN see (company-knowable — regional weather is genuinely
public):** published national and regional forecasts and outturns; wholesale
prices; its own meter reads.
**What it CANNOT see:** each property's true thermal characteristics; how its own
book actually responds to weather; the counterfactual.
**Therefore the gap:** the company must INFER its book's weather sensitivity —
weather-normalisation — from confounded meter data. This is genuinely hard and
genuinely done badly in the industry. **Register the company-side twin and measure
the gap** (predicted vs actual demand under a given weather outturn).

## The trade-off this creates (make it REAL, per cat-and-mouse)
GB has **no regional forward market** — you cannot hedge regional basis today
(this is precisely what the zonal/locational pricing debate is about). So:
- Hedge to the NATIONAL forecast and a regionally-skewed book leaves you exposed
  when your region deviates.
- Try to protect regionally and you face basis risk, illiquidity, and cost.
**The SIM must make both extremes bite.** Where the company sits on that frontier
is strategy, and it should be visible.

## Explicitly LATER (do not build now — director's sequencing)
Renewable capacity trends, generation-mix evolution, zonal/locational pricing
mechanics, DSR/flex markets, EV/heat-pump adoption geography. **Physics first.**
Register them as follow-on atoms so the sequence is visible, but do not start them.

## DoD
Hierarchy L1-L4 designed and built with: temporal autocorrelation; spatial
correlation; **aggregation-consistency invariants at BOTH levels (regional->national
weather, premise->national demand), mutation-tested**; the cold-and-still joint
dependence present and demonstrated (show the tail); price as a derived output;
generator/validator anchors independent and named; the company-side
weather-normalisation twin registered with its gap metric. Report the winter tail
the model produces and compare it to a real one — if our worst week is milder than
GB's real worst week, the physics is still wrong.