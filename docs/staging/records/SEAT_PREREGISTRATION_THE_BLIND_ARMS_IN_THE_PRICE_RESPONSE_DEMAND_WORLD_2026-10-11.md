**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `value-arms-retake-in-the-price-response-demand-world`

# Pre-registration: the four blind-envelope arms re-taken in demand world 7d6195c5eb1562ab

Written 2026-10-11 ~15:30 BST, before any arm was launched. At this point I had read only the
figures already filed in `docs/design/blind_envelope_arms_2026-09-11.json` (measured at fc47cd363,
demand `b422b3dd8de98b8c`) and the message of bc34b3912.

**What runs.** The same `arm_rerun.py` as the 2026-10-07 filing, unchanged, from a clean
`git archive` of origin/main d06b039e7 (demand digest read there: `7d6195c5eb1562ab`), with
`SIM_FAST_MODE=1`. There are two lanes: `chosen` then `tenure`, and `cull` then `cull<N>`. N is
ARM B's own `_p6_campaign.settled_wins`, read from B's output before C is launched. ARM C' is not
re-run.

**What this cannot attribute.** 470 commits separate fc47cd363 from d06b039e7, and the SERL price
response is one of them. Any move from the 10-07 figures to these is the sum of all of them, so I
cannot say what the price response alone did to the arms. That needs a one-variable pair (the same
commit with `SETTLED_BOOK_PRICE_RESPONSE` off and on). The questions below are therefore about the
re-take as a whole, except Q4.

- **Q1** All four arms stamp `demand_digest == 7d6195c5eb1562ab` and one world digest, and the
  publish-time demand refusal (`_blind_envelope_demand_refusal`) stops firing. Confidence 85%.
  It fails if origin moves the demand mid-run, or if the arms disagree on the departure level.
- **Q2** Revenue per weighted win falls in every arm against its 10-07 figure. Confidence 55%. The
  price response alone cuts winter 22/23 volume by about 6–11%, but 470 other commits make the
  sign close to a coin.
- **Q3** The direction of B (the chosen book) against the blind arms, per weighted win, is NOT
  PREDICTED, as the item says. Stated so the result cannot be read as having been foreseen: on
  10-07, B's gross per win (2,562) was below all three first-hand blind arms, and its net per win
  (899) was inside their span.
- **Q4** The price response cuts volume in fabric-path homes, and the chooser is the only arm that
  sees fabric. So, conditional on a one-variable pair being run later, I expect it to move B's
  gross per win by less than one standard error of B (about £330). Confidence 70%. Not tested here.
- **Q5** Over the four arms in this world, every |per-win difference between B and a blind arm|
  stays under twice the larger of the two standard errors. In other words, nothing here separates
  the chosen book from the blind books at one seed. Confidence 75%.
