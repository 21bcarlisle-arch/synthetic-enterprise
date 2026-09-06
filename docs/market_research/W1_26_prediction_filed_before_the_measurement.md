**Severity:** RECORDED · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** W1_26_the_world_has_no_wind_term_and_the_belief_does

**Knowledge:** none -- a prediction, not an anchor. Kept beside its result so the experiment is visibly designed before its answer was known; the result is in
`the_world_now_has_a_wind_term_and_my_prediction_was_wrong_three_ways.md` and three of the four below are refuted there.

# W1_26 prediction, filed BEFORE the measurement

Written 2026-09-06 before `simulate_premise` had ever seen a wind speed. Site mean wind in the
archive is C1 4.03, C2 3.74, C3 3.84, C4 4.61 m/s against SAP's 4.0 m/s reference.

1. **Annual heating demand moves less than 3% at every site.** The site means bracket the reference,
   so the wind factor averages near 1.0 and the level barely shifts.
2. **C4 (Cotswolds, 4.61) rises most; C2 (Manchester, 3.74) falls.** Direction follows the mean.
3. **Day-to-day variance in daily heat demand rises materially.** This is the actual gain: the
   distinction between a cold still day and a cold windy day does not exist in the model today.
4. **The largest single-day effects are on windy days, not cold ones**, and the two coincide (the
   repo's own +0.507 temporal correlation), so the cold tail widens more than the middle.
