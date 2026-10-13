**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- grades of built capabilities against predictions already filed; the pricing pages are docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md and retention_slope_per_pound_of_renewal_cut.md

# On fresh seeds the save never fires, because renewals sit below their own cost floor, and the price-match renewal cut loses net (2026-10-13)

The director's Order 1: re-grade the save and the renewal cut on fresh seeds across the world's ranges.
Set-up:
- book seeds 61109-61112, 400 founders, budget 0, to 2025-06-07, frozen payment world (553d7c855),
  every arm at ed668c733 (/var/tmp/regrade/);
- the save at world k = 0, 0.92 and 1 against off;
- the renewal cut, risk_tiers against price_match.
The predictions were filed before any arm: the save's S1-S6 in
WORLD_FREEZE_DD_SHOCK_SAVE_AND_MOVER_AT_THEIR_RANGE_ENDS_2026-10-12.md §2; the renewal cut's six of
f463d39f4, re-applied in /var/tmp/regrade/RENEWAL_CUT_PREDICTIONS.md (sha256 effe8706...).

## The save: S1-S6 all "hold", and the grade measures nothing

| # | Prediction | Result |
|---|---|---|
| S1 | k = 0 against off: identical, 0 saved | identical (61109) |
| S2 | saves at 0.92 never more than at 1 | 0 and 0 everywhere |
| S3 | 0 to 5 offers per seed | **0 on every seed, at every k** |
| S4 | 0 to 3 saves per seed | 0 |
| S5 | on - off within 0.5% of net | 0.00 |
| S6 | stayer price moves and vulnerable shortfalls 0 | 0 and 0 |

Every prediction holds because nothing happened. **The branch was never taken**, so this is not a pass.
27 loss notices were held under CSS across the four seeds. On **23 of 27 the renewal rate was already
below the company's own cost floor** (for example 61109, 2025-05-12: renewal GBP 244.7/MWh, floor
251.1). The price match never prices below the floor, so no save can be offered. One renewal sat above
the published default tariff. The base seed offered 2 of 23. On fresh seeds the save is inert.

## The renewal cut: the price match loses net on every seed

| seed | offers, tiers / match | offer cost GBP, tiers / match | net, match - tiers | renewal departures, tiers / match |
|---|---|---|---|---|
| 61109 | 75 / 47 | 1,824 / 1,006 | -1,639 | 63 / 66 |
| 61110 | 76 / 41 | 1,864 / 819 | -1,730 | 53 / 58 |
| 61111 | 69 / 49 | 1,660 / 724 | -3,021 | 65 / 71 |
| 61112 | 74 / 48 | 2,200 / 872 | -483 | 64 / 63 |

Against the predictions:
- 1, the match makes at most half the tiers' offers: **refuted** on every seed (0.54-0.71 of them).
- 2, a lower mean cut: **held** by the cost per offer (GBP 21.4 against 24.3 on 61109, and lower on
  every seed).
- 3, a lower offer cost: **held**.
- 6, net within plus or minus GBP 2,000 with a mixed sign: **refuted**. 61111 is outside the band,
  and the sign is negative on all four.
The match saves about GBP 1,000 a seed on cuts and loses more than that in departures (3-6 more on
three of the four seeds).

**The pre-registered rule decides it:** "Do not recommend the switch if net falls on every seed." Net
falls on every seed. **The renewal cut stays on risk_tiers, and the recommendation of a99685b68 (the
default book with three churn-roll floor seeds) is withdrawn.** It did not survive fresh book seeds,
which is the point of the four principles' third.

## The next item, ahead of new work

Both grades meet the same fact: on these books in 2024-25, the renewal price the company sets sits
below its own cost floor. B8 Q5 met it as 71-77 floor declines per seed and handed it off as
`b8-q5-why-does-the-renewal-fix-sit-below-its-own-cost-floor`. It decides whether a save can ever fire,
and how a cut is sized. **Ranked P1 for next week's supplier engine**: either the renewal price is
loss-making (a pricing defect), or the floor counts a cost the renewal price is not meant to carry (a
definitional one). Which it is decides the fix.
