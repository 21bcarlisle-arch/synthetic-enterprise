**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost`
**Knowledge:** acquisition-and-retention-economics -- `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` §5c (the published save rate, 0.4–1.3% proxy)

# A save grade counts realised saves where the log already holds the expected ones (2026-10-15)

**Fate (2026-10-15):** ATOM -- folds into `B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost` (re-pointed 2026-10-15; an ATOM fate names its atom).

**Owner:** whoever writes the next save-on grade script, the delivery seat or a B_commercial worker.
The fix is reuse, not new code.

## The defect

The regrade5 arm script (`/var/tmp/regrade5/cut_arm5.py`) reported `save_offers_made` and
`saves_taken`, then threw the per-offer `save_on_loss_notice_log` away. The record that followed
(`9ab9b7959`, `cc1a2e637`) concluded "the save fires and no customer takes it", from 0 of 23.

At the world's own response, the expected number of saves over those offers is about 0.17. The
published save rate is 0.4–1.3% of switches. So P(0 | the world working as built) ≈ 0.84, and the
realised count can tell nothing apart. Every row of the log already carries `p_stay_at_offer` and
`p_stay_at_save`. From those the expected save count is exact and has no draw noise.
`tools/save_on_loss_notice_arms.py` already computes it: `implied_save_rate`, `expected_saves`,
`implied_saves_per_domestic_switch_away_from_css`. The scratch script did not call it.

**What it cost:** a draw (`the-save-fires-and-no-customer-takes-it`) spent on a question whose answer
was in the log. And because the 61112 logs were not kept, the offer the draw asked to trace could not
be read. The trace used seed 61109's logs instead
(`docs/staging/records/WORKER_RESULT_THE_SAVE_IS_SEEN_AND_TAKEN_AT_THE_PUBLISHED_RATE_SO_ZERO_OF_23_IS_WHAT_THE_WORLD_PREDICTS_2026-10-15.md`).

## The remedy

Any arm that grades the save should keep `save_on_loss_notice_log`, or at least its two P(stay)
columns and `price_match_inputs`. It should report `implied_save_rate` and `expected_saves` beside
`saves_taken`. To realise even 3 saves at 0.7% takes about 400 offers, or about 100 seed-runs at
today's 4 offers per seed. So a realised count is never the grade at this scale; the expected count is.

## What would show this wrong

A run that keeps the log and finds Σ(P(stay|save) − P(stay|renewal)) / Σ(1 − P(stay|renewal))
well outside 0.3–1.3% on the post-`4492d17bd` code. Then the five-row reading in the result record
does not generalise.
