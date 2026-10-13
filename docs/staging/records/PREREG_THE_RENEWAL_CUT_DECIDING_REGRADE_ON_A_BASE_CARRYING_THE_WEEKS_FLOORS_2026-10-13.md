# Pre-registration: the renewal cut's deciding re-grade, on a base carrying this week's floors (2026-10-13)

**Knowledge:** none -- a re-grade of a built capability against predictions filed here; the pricing pages are docs/market_research/retention_slope_per_pound_of_renewal_cut.md and a_save_offer_against_the_switching_rules_and_the_seam.md

*Filed by the console delivery seat before any arm runs. Base: origin 5e5358092 (ec0c00917 plus a stretch-log entry, no code). It carries
03a0b66da (writer 1's discount floored at cost), 5c137eb5b (the risk-tier retention cut floored),
61c122683 (hedge at the market quote), 434d87587 (capital-inclusive floor) and 2473321d6. This is
the run that SEAT_FINDING_ON_FRESH_SEEDS_THE_SAVE_NEVER_FIRES_..._2026-10-13.md and 82e84e4a4 name
as deciding. The director's Tuesday rule admits it: it tests changes that landed this week.*

## Set-up (unchanged from /var/tmp/regrade/queue_rc.sh except the base)

Book seeds 61109-61112, 400 founders, budget 0, to 2025-06-07, frozen payment world (553d7c855).
Arms risk_tiers and price_match, through /var/tmp/regrade/seeded_arm.py and renewal_cut_arm.py,
worktree /var/tmp/se-rc3 at 5e5358092. Eight arms, admitted by launch_long_job beside the
term-cost floors.

## Predictions

The six of f463d39f4 (as re-applied in /var/tmp/regrade/RENEWAL_CUT_PREDICTIONS.md, sha256
effe8706...) are carried unchanged:
1. offers under the match are at most half the tiers' offers;
2. the match's mean cut is at or below the tiers';
3. the match's offer cost is lower;
4. the best-published-deal no-offer is the commonest cause, and input_missing is at most 5% of
   the no-offers (expected refuted again, by the cost floor);
5. market_had_nothing_cheaper_than_the_default falls only on terms starting 2021-10 to 2023-06;
6. net, match minus tiers, lies within plus or minus GBP 2,000 on every seed, and its sign is not
   the same on all four.

Added for the new base, about what the tier floor should do:
7. the tiers' mean cut on 61109 falls below the GBP 21.4 measured at ed668c733, because 5c137eb5b
   trims cuts that went below the floor;
8. |net, match minus tiers| on 61109 is smaller than the GBP 3,089 measured before the floor. I
   cannot predict its sign: the floored tiers keep fewer leavers but at a higher margin.

**Decision rule, unchanged:** recommend the match if it spends less on offers on every seed and
its net is not lower by more than one seed-spread. Otherwise stay on risk tiers. A result that
turns on one seed is reported as that.
