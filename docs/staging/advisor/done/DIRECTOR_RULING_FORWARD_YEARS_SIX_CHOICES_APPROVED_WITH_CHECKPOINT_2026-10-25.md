**Severity:** BLOCKING · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-RULING] Forward years: the six choices approved, checkpointing added, volatility claims as the pass mark (2026-10-25)

**Type:** RULING, through the advisor channel. It answers the `for_the_director` row `forward-years-ruling-of-24-oct-17` and `docs/design/FORWARD_YEARS_RECOMMENDATION_2026-10-24.md` §8. The advisor put this to the director:

> My view is still: agree all six, add checkpointing, and treat these volatility checks as the pass mark before forward runs are trusted. Say yes and I'll send it.

The director's words, from chat on Sun 25 Oct:

- 05:14 GMT: "Yes"

## What is ruled

1. **The six choices in §8 are approved as written:**
   1. horizon 2026–2035, with 2026–2030 as the fallback if the probe prices a run above 3 h;
   2. weather by seeded block draws from the record, the same source day in every cell, with no trend until the K8 page sources one;
   3. **gas in the full DESNZ A to C band**, uniform, with the record's volatility. This is the director's curriculum choice, now made;
   4. price from the existing weather chain, with the **wind and solar fleet in the NESO FES band**, drawn per future. This is the director's curriculum choice, now made: the fleet no longer holds flat;
   5. forward products M+1..3, Q+1..2 and S+1..4, baseload power and gas, at the conditional expectation plus the sourced term premium. The world quotes the bid-offer, and nothing is quoted beyond two years;
   6. N = 5 paired futures per question after a one-run cost probe, re-sized from the first question's spread.
2. **Build checkpoint and resume at the end of the record.** A forward run must not replay 2016–2025 each time. The prediction is 2–3 h and 9–15 GB against today's 7.5 GB peak, inside the R7 memory budget. This is the structural debt canon R15 said to raise "when it next costs real work" (the 3,400-line run function blocking checkpoints). Measure before and after, mutation-prove that a resumed run equals an unbroken one on the same seed (R4: "The same seed must give the same book"), and size the work under the estimate-the-cost steer.
3. **The volatility claims are the pass mark.** `DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE_2026-10-25.md` sets the claims: volatility and calm at each scale, the gas path, the mix and depth of backwardation and contango, the spark spread's range, the cross-links, and forecast error growing with horizon. No forward run is used for a supplier result until the generators pass those claims, or each failure is named as a limit with its size (W7 principle 2, F11).
4. **The order is unchanged.** Forward runs wait for the basics, per the 24 Oct ruling. Until then, three things go ahead in parallel: the K8 page, the EP16 anchoring and grading, and the checkpoint build.

## Where this lands

- Close the `for_the_director` row with this ruling.
- Record the two curriculum choices (gas band, fleet band) where curriculum is kept, with the his-words trailer: `Director-doc: his-words -- forward years six choices, director 25 Oct 05:14`.
- Update `docs/design/FORWARD_YEARS_RECOMMENDATION_2026-10-24.md` with an "Approved 25 Oct" header pointing here.

— Director ruling, 25 Oct 2026, his word above; the drafting is the advisor's.

## Done

*Autonomous worker, 2026-10-25.* All three "Where this lands" items are done:
- The `for_the_director` row `forward-years-ruling-of-24-oct-17` is answered with this ruling (`docs/direction/DIRECTION.yaml`).
- The two curriculum choices, the gas band (DESNZ FFPA 2025 A-C, uniform) and the fleet band (NESO FES wind plus solar), are recorded in the new `docs/design/curriculum/forward_years.json`. The commit carries the his-words trailer the ruling names. Nothing reads it yet: no forward generator is built, and the file says so.
- `docs/design/FORWARD_YEARS_RECOMMENDATION_2026-10-24.md` now carries an "Approved 25 Oct" header pointing here.

Ruling item 4 lets three things run in parallel. I made one change to the map for it:
`EP16_anchored_generators` was blocked as "director-reserved curriculum sequencing (R13)". The block is cleared and now cites this ruling, so the anchoring and grading can be drawn.

**Not done here, and still open:**
- the K8 volatility page and the claims grading. These are the companion steer, `DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE_2026-10-25.md`, which stays in the advisor queue as live work.
- the checkpoint-and-resume build (ruling item 2). No map atom carries it yet. The steer's owner should mint one when it sizes the 3,400-line run function's state, under the estimate-the-cost steer.
