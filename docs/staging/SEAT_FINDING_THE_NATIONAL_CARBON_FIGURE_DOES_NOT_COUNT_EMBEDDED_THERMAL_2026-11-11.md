**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# The national carbon figure does not count embedded thermal generation, so the customer figure probably runs low (2026-11-11)

**What prompted it.** Item 2 of the director's 11 Nov carbon steer: use Ember as a second independent check on
2016–2025. The full table and the basis of each source are in
`docs/market_research/household_carbon_and_the_measures_that_save_it.md` §1b. The pre-registration is in
`docs/staging/records/SEAT_PREREG_WHAT_EMBER_SAYS_ABOUT_OUR_GB_CARBON_HISTORY_2026-11-11.md`.

**What the thing is.** The customer's electricity carbon multiplies their kWh by NESO's national intensity
(`sim/grid_carbon_history.py`). NESO's historic mix counts transmission-metered generation plus its estimate of
embedded wind and solar. It does not count embedded or captive **thermal** generation: gas CHP, waste, landfill
gas, anaerobic digestion, oil. The knowledge page said "every GB generator" until today. That is now corrected
beside the claim.

**The measurement.** Ember's UK figures come from the Energy Institute, upscaled on DESNZ totals to capture
"captive and small thermal". Against NESO's GB columns they carry about 43 TWh a year more thermal generation,
steady across 2016–2025: 14–19 TWh gas, 16–19 TWh bioenergy and waste, and 10–13 TWh other fossil. That is about
13% of generation. With Ember rebased to our operational factors, net generation and imports, it moves from
2–6% BELOW ours in 2016 to 13–25% ABOVE in 2024–25. The excess is steady while NESO's transmission gas halved, so
its weight grows as the transmission system decarbonises.

**What is not established.** How much of the 43 TWh is Northern Ireland, which a GB household does not meet, and
how much is GB embedded thermal, which it does. *I cannot yet say.* DESNZ *Energy Trends* 5.1 and *DUKES* 5.6,
by producer type, would split it. That is the next knowledge step, and it is a reading, not a build.

**Why it matters (F11).** If most of it is GB embedded thermal, the customer figure understates GB average
intensity by roughly 10–25% in 2023–2025. A low grid intensity flatters every electrification measure: heat
pumps, EVs, and the "carbon saved" side of §4 and §5. That runs in our thesis's favour, which is the direction to
distrust.

**What was NOT done.** The series the world uses is unchanged. The steer says "No change to the series the world
uses unless the Ember check finds a real error. If it does, say what and why first." This is not an error in our
arithmetic. It is the scope of the figure NESO publishes, and the figure a real supplier would quote. Whether
the customer figure should add the uncounted thermal is a definitional choice about CO1, so it goes to the
director with a recommendation (`for_the_director`).

**Recommendation.** Keep NESO's figure as the half-hourly shape. Once the GB/NI split is read from DESNZ, state
on the customer-facing carbon figure a named, annual "embedded thermal not counted" bound, as the T&D losses line
already is (§2). Do not rescale the series until that split is established.

**Two smaller findings from the same check**, recorded on the page and changing no published value:
1. The fill's "few percent ABOVE" bias is the import term. Its per-market factors run 20–55 g above the factor
   NESO's own mix implies. That factor is a residual, so this is an attribution, not a measurement. Its import
   share is also short by about ElecLink and Viking. The fill fills 0 half hours today.
2. NESO's historic mix appears to INCLUDE ElecLink and Viking. Its import share matches the fill's only if they
   are added back. `OUTSIDE_NESO_MIX` (`sim/elexon_fuel_outturn.py`) says they are left out. That may be right for
   the Carbon Intensity API's mix and wrong for the historic-mix file. Not yet checked against NESO's column
   definition.
