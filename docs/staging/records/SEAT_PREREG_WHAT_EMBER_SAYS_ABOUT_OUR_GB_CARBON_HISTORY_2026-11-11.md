**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# Prediction, filed before Ember's data or methodology was read: how Ember's UK figure sits against our GB history (2026-11-11)

**The check.** Item 2 of the director's 11 Nov carbon steer: set Ember's annual UK power-sector
carbon intensity beside ours (`sim/grid_carbon_history.py`, generation-weighted by year), 2016–2025.

**What I believe about Ember's basis, before reading it** (each is a prediction the methodology PDF can refute):
- B1. It is **UK**, not GB: Northern Ireland is in it.
- B2. It is **generation-based**: imports are not in the denominator and carry no factor.
- B3. It uses **lifecycle** factors (IPCC AR5 medians, CO2e), not stack CO2.
- B4. It is **annual** (monthly also published); a single number per year over all UK generation.

**Predictions.**
1. **P1, direction.** Ember's figure is ABOVE ours in every year 2016–2025.
2. **P2, size.** By 15–45% per year. B3 lifts it (gas ~490 vs 394, solar/wind/nuclear above zero,
   bioenergy ~230 vs 120); B2 lifts it (low-carbon French and Norwegian imports left out); B1 lifts it
   a little (NI is gas-heavy).
3. **P3, shape.** Both fall across the decade, and the year-on-year changes agree in sign in at
   least 8 of the 9 steps.
4. **P4, the "few percent above" fill bias.** Ember cannot apportion it. The fill covers few half
   hours, so its effect on an annual mean is below 1% in every year, which is inside the basis gap of P2.
   Ember's value to that question is limited to whether it names a term (imports, embedded, biomass)
   that NESO's arithmetic counts differently.

**What refutes it.** Any basis belief B1–B4 wrong as read in Ember's methodology; Ember below ours in
any year; a gap outside 15–45%; or sign disagreement in more than one step.
If a basis belief is wrong, P2 is re-derived from the corrected basis and the miss is kept beside it.

---

## Result, filed after the read (same day). The predictions above are unedited.

- **B1 right.** UK, with Northern Ireland from Green Collective.
- **B2 right.** Intensity is over generation, with imports out.
- **B3 right.** Lifecycle CO2e. The CSV implies gas 480, nuclear 4.8, wind 12.7.
- **B4 right, and incomplete.** Annual generation is **gross** (Energy Institute), and Ember cuts its thermal
  factors 6% for it. More important, which I did not predict: the GB data is upscaled to DESNZ totals to
  capture "captive and small thermal".
- **P1 held.** Ember is above ours in every year.
- **P2 REFUTED for 2023–25.** 2016–2022 fall inside 15–45% (+18% to +43%). 2023–25 are +56% to +69%. The miss is the unpredicted term: about 43 TWh a year of embedded and captive thermal generation that
  NESO's mix does not count. On a matched basis (operational factors, net generation, imports added) the gap is
  −6% to +25%.
- **P3 held.** The two move the same way in all 9 steps.
- **P4 held, more strongly than predicted.** The fill covers **0** half hours in every year, so its effect on
  the annual means is nil. Ember did not name the term. Following the thread did: it is the import factor and
  share (household_carbon §1b).
