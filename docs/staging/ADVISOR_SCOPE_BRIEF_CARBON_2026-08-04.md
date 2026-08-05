# [ADVISOR-SCOPE-BRIEF] — Measuring carbon honestly: what the mission's own unit of account must contain (2026-08-04)

**Type:** [SCOPE BRIEF]. The company exists to abate carbon, and carbon is currently **two files and 10KB — the smallest thing in the repository.** Written from the domain before consulting the code. Refute where already covered.

---

## A. The number we are trying to produce

Three quantities, and conflating them is the commonest failure in this field:

1. **Emissions** — tonnes this household's energy use represents. A measurement.
2. **Abatement** — tonnes *avoided* versus what would otherwise have happened. A **counterfactual**, and therefore always an estimate.
3. **£ per tonne abated** — the mission's score. Cost of achieving the abatement, divided by the abatement.

**Only the first is observable.** The second requires a claim about a world that did not happen, and the third inherits that uncertainty. A treatment that presents abatement with the same confidence as emissions is dishonest by construction.

## B. Emissions — the measurable part

**Electricity.** Half-hourly consumption × the grid's carbon intensity for that half hour. GB has an official source: NESO's Carbon Intensity API, developed with the Environmental Defense Fund, Oxford and WWF, with Met Office weather. It gives **national and 14 regional series at half-hourly resolution**, both forecast and outturn, in grams of CO₂ per kWh, licensed openly.

Four properties that matter:

- It covers **generation only** — large metered stations, interconnector imports, transmission and distribution losses, and embedded wind and solar.
- It is **corrected for losses**, so it expresses carbon per unit *consumed*, not generated. **Do not apply a further loss adjustment.**
- **Regional intensity is modelled**, using a reduced network model of power flows, not measured. Regional numbers are better than national for a specific household and carry their own error.
- Forecast and outturn differ. **Which one you use defines what the claim means:** forecast is what a customer could have acted on; outturn is what actually happened. Shifting advice must be judged on forecast; achieved abatement on outturn.

**Gas.** Much simpler and much less interesting: a near-constant factor per kWh burned. No time-shifting benefit exists, because gas emits when burned. **The only lever is using less.**

**The asymmetry is the whole strategy:** electricity carbon varies by a factor of several through a day, gas carbon does not. Time-shifting only pays in electricity.

## C. Abatement — the honest hard part

**The counterfactual is the entire problem.** Four bases, in descending order of defensibility:

1. **Randomised holdout** — a matched control group not given the intervention. The only basis that supports a causal claim. Expensive, and it requires enough customers.
2. **Matched comparison** — similar households, weather-normalised, over the same period.
3. **Before-and-after with weather normalisation** — cheap, and confounded by everything else that changed.
4. **Engineering estimate** — this measure typically saves this much. Defensible as a design input, **never as a measured result.**

**At the current book size none of the first three is viable.** That is not a reason to fabricate; it is a reason to say so.

**Time-shifting versus reduction — count them separately.** Moving consumption to a cleaner half hour abates carbon without reducing kWh. Reducing consumption abates both. **The director's standing rule holds: savings count only from reduced or time-shifted usage, never from discounting** — a cheaper tariff moves money, not carbon.

**Rebound.** Efficiency measures reliably return part of the saving as extra comfort — a cold house made cheap to heat gets heated more. Ignoring it overstates abatement. A treatment that has never heard of it is not credible.

## D. £ per tonne — the score

Numerator: what it cost to achieve the abatement — the measure, the compute, the contact, the margin given up. Denominator: tonnes abated on the basis above.

**The yardstick that gives it meaning is the UK government's own carbon value** used in policy appraisal. A £/tonne figure without a comparator is a number; with one it is a claim.

**Never let this become a target** — the cheapest way to improve £/tonne is to pick easy households, which is the opposite of the mission.

## E. What must be stated with every number

Basis (measured / matched / estimated), sample size, period, counterfactual, and whether shifted or reduced. **A carbon figure without its basis is not a measurement, it is a slogan** — and the site's current honest placeholder is a better artefact than a number without these.

## F. Disqualification battery

1. A single annual emissions factor rather than half-hourly intensity.
2. Applying a further loss correction to a series already loss-corrected.
3. Regional intensity presented as measured rather than modelled.
4. Forecast and outturn used interchangeably.
5. Time-shifting credited with reducing consumption, or the two summed without distinction.
6. Abatement claimed at holdout-grade confidence without a holdout.
7. No rebound effect.
8. Discounting counted as abatement.
9. £/tonne without a comparator, or used as a target.
10. Gas modelled as time-varying carbon.
11. Any carbon figure published without basis, sample size and counterfactual.
12. Embodied carbon in measures ignored while operational savings are counted.

**Sources:** NESO Carbon Intensity API documentation and methodology (national and regional forecasts, generation-only scope, loss correction, 14 DNO regions, half-hourly, CC BY 4.0); NESO data portal national and regional carbon intensity datasets; NESO FOI response confirming the loss-correction basis; third-party methodology descriptions of regional forecast use at 30-minute resolution.

— Advisor scope brief, written before consulting the repository, 2026-08-04.
