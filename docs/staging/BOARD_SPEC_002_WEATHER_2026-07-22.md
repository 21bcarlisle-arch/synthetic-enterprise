# BOARD SPECIFICATION 002 — Weather (blind practitioner spec, VERBATIM)

**Type:** [ANCHOR — verbatim + reconciliation instruction]. Blind-drafted. **Do not edit the board's text.** Reconcile line-by-line (met/partial/absent/N/A, reasons, code anchors) against the weather cascade (W1_3/W1_4 L3, C13 L2, the coupled triad) per the standing triangulation steer; battery joins the practitioner fidelity oracle.

**Advisor flags (verify):** (a) §1's effective-temperature/thermal-lag composite is C13's CWV territory — and battery item 2's "still-and-cold compound" should be reconciled honestly with C13's own finding that the wind-chill term fitted NEGATIVE because GB cold spells are anticyclonic/still: the board and the data may be saying the SAME thing (cold arrives with stillness) — work out whether they agree, and record it either way. (b) Item 8 (one draw drives demand AND price) is the coupled triad — claim MET only with the R15/shared-draw proofs cited. (c) Item 1 (persistence, synoptic spells, multi-day structure) applies to the FUTURE-weather generator, not the historical record — audit the generator specifically. (d) §4's normalisation three-questions and the same-basis-for-three-masters discipline are new requirements on C13's remit.

---
---

# POESYS BOARD — PRACTITIONER SPECIFICATION 002
## Weather: what a credible weather system for a GB domestic supplier must exhibit

*Issued blind under Movement 2 of Sitting 001. The Board has not examined any weather system as built and asks nothing about it. The Executive reconciles line by line to Movement 3.*

*The Chair orchestrates. The Brain leads on structure and normalisation; the Worrier on extremes and compound events; the Doer on what the desk actually consumes; the Child asks the plain question — "does cold weather here behave like cold weather does?" — and it turns out to be the whole specification.*

---

## 1. The variables that matter, and why

**Temperature is the sovereign variable**, because GB domestic energy is dominated by space heating, and heating demand is a function of the gap between inside and outside. Two refinements a veteran demands immediately:

- **Thermal lag.** Buildings and behaviour respond to recent temperature, not the instant. The GB gas industry's own demand variable is a *composite* — an effective temperature blending today with preceding days, adjusted for wind — precisely because yesterday's cold is still in today's walls. A demand model keyed to instantaneous temperature alone misses the mechanism the industry itself corrected for decades ago.
- **Non-linearity.** The demand–temperature curve is a hockey stick: essentially flat above roughly 14–16°C (GB has little cooling load, though it is growing), then steep below, and steeper still in deep cold as systems run flat-out and secondary heating switches on. A linear sensitivity fitted through the middle understates exactly the tail that matters.

**Wind speed matters twice, through different doors.** On the demand side, wind strips heat from buildings — wind chill raises heating demand at any given temperature. On the price side (Spec 004's territory), wind *generation* displaces gas plant and moves the power price the other way. A credible system carries wind because both doors must swing from the same draw.

**Solar irradiance and daylight** shape the electricity profile — lighting load tracks darkness, and the winter evening peak is partly a daylight phenomenon — and solar gains offset heating at the margins. Secondary, but the intraday shape is wrong without them.

**Precipitation and humidity** are minor for this book and may be honestly omitted, provided the omission is registered.

## 2. Spatial structure

GB is not a point. The gas industry operates on **regional distribution zones, each with its own composite weather** built from designated stations, because the north–south temperature gradient and coastal–inland differences are material. What a supplier needs depends on its book: a nationally spread book can run on a **population-weighted national composite** with modest error; a regionally skewed book cannot. Two spatial facts must survive whatever simplification is chosen:

- **Spatial correlation is high but not perfect.** A single-station national model gets the variance of aggregate demand wrong — it removes the diversification that real regional spread provides and overstates demand volatility (or, if calibrated to aggregate variance, understates local extremes).
- **The weather that drives wind generation is not the weather at the homes.** Wind fleet output depends on conditions at concentrated, largely northern and offshore sites; demand depends on conditions where people live. Collapsing both to one series manufactures a correlation the real system does not have.

A model may legitimately simplify to national composites — many mid-size desks do — but it must *know* it has done so and register what the simplification suppresses.

## 3. Persistence, seasonality, extremes, trend

**Persistence is the heart of credible weather.** GB weather arrives in synoptic systems lasting days, and in blocking patterns lasting weeks. Day-to-day autocorrelation is strong; cold spells are multi-day by construction; the historic system-stress events (December 2010, the 2018 easterly, December 2022) were one-to-two-week episodes, and *duration* — not depth alone — is what drains storage, exhausts flexibility, and compounds financial stress. A weather model drawing independent daily values, however correct its marginal distribution, cannot produce the events that matter and is disqualified on sight (§5, item 1).

**The compound extreme is the one the Worrier owns: still-and-cold.** Winter anticyclonic blocking delivers low temperatures and low wind *together* — maximum heating demand coinciding with minimum wind generation, which is precisely the state in which prices spike (Spec 004). In winter, temperature and wind are meaningfully correlated in the dangerous direction; treated as independent draws, the joint tail — the only tail that kills — is understated by a large factor. This single correlation is the most important number in the entire weather system.

**Interannual variability** is large: winter-to-winter swings driven by large-scale atmospheric patterns move annual heating demand by high single digits either way. A model whose every winter is the average winter has no business informing a hedge.

**The warming trend is real and must be carried** — seasonal normals drift warmer and the industry periodically re-bases its "normal" to trended averages — **but the trend does not delete the extremes.** Milder means do not prevent blocking events; the 2018 and 2022 cold spells occurred inside a warming climate. A credible model shows a drifting centre with an undiminished (arguably fattening) sensitivity to variance: fewer heating degree days on average, same or worse worst-cases.

## 4. What "weather-normalised" must mean in practice

Normalisation is not a phrase; it is a defined procedure, and every normalised figure must be able to answer three questions:

1. **Normal relative to what?** A stated reference climatology — which years, whether trend-adjusted, re-based on what schedule. "Normal" from an untrended 30-year average is systematically cold against the current climate and will bias every volume forecast high.
2. **Adjusted through what sensitivity?** A fitted demand–weather relationship (per fuel, ideally per segment — electric heating and gas heating normalise differently), with the non-linearity of §1 respected. Actuals are restated to normal weather *through that curve*, not by a flat scalar.
3. **Carrying what error?** The normalisation model's residual error propagates directly into hedge volumes and performance measurement. A desk that treats normalised demand as exact has hidden a real risk inside a definition.

The Doer's addendum: normalisation serves three masters — hedge volume setting, forecast evaluation, and management reporting — and the *same* basis must serve all three, or the company will hedge one number, measure itself against a second, and report a third.

## 5. The battery — what makes a simulated weather system NOT credible

1. **Independent daily draws.** No persistence, no synoptic structure, no multi-day spells. Disqualifying regardless of how correct the marginal distributions are.
2. **Temperature and wind independent in winter.** The still-and-cold compound tail missing or thin; the joint event frequency at odds with the observed winter correlation.
3. **Instantaneous response only.** No thermal lag, no effective-temperature construction; demand keyed to today's reading alone.
4. **A linear demand–temperature relationship.** No hockey stick, no cold-tail steepening, no near-flat summer.
5. **Tame extremes.** Maximum cold-spell depth and duration materially inside the observed record; no event of December-2010 or 2018 class producible; the model's worst fortnight milder than history's.
6. **One point for everything** — a single weather series driving demand and generation alike, without the simplification registered and its suppressed variance acknowledged.
7. **No trend**, or normals fixed forever — or, the opposite failure, a trend that thins the extremes as it warms the mean.
8. **Weather that moves demand but not price**, or price but not demand. One draw must drive both, or the correlation that defines this market is severed at the root (the shared finding of Specs 001 and 004).
9. **"Weather-normalised" without a stated basis** — no reference climatology, no fitted sensitivity, no error carried.
10. **Every winter average.** Interannual variance absent; annual demand swings suspiciously small year over year.

*The Chair, closing: the veteran's summary is that credible weather is defined less by its averages than by its correlations and its patience — cold that arrives with stillness, and stays. Reconciliation line by line: met / partially met / absent / not applicable, with reasons, to Movement 3.*

*Signed for the Board — the Chair.*
