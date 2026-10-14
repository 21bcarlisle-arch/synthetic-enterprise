**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- grades of built capabilities against predictions already filed; the pricing pages are docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md and retention_slope_per_pound_of_renewal_cut.md

# On fresh seeds the save never fires, because renewals sit below their own cost floor, and the price-match renewal cut loses net (2026-10-13)

**Fate (2026-10-14):** ATOM, half done. The renewal cut is DONE -- the deciding re-grade ran at 5e5358092 and stays on risk tiers (SEAT_RESULT_THE_RENEWAL_CUT_STAYS_ON_RISK_TIERS_..._2026-10-14.md). The save's own question (renewals at their floor to the penny, so no room to offer) is next week's P1. **Decided 2026-10-14: (b), definitional** -- the floor carries the network cost the standing charge recovers, and writer 1 reads the standing charge as margin, so its -5% lands every electricity renewal on the floor (21 of 21 held rows): SEAT_FINDING_RENEWALS_SIT_AT_THEIR_COST_FLOOR_BECAUSE_THE_FLOOR_CARRIES_THE_STANDING_CHARGES_NETWORK_AND_THE_PREMIUM_READS_THE_STANDING_CHARGE_AS_MARGIN_2026-10-14.md.

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

> **AMENDED 2026-10-13, recounted at origin HEAD d55598dd6. This code carries 03a0b66da (writer 1's
> discount floored at cost).** Pre-registration:
> `records/PREREG_THE_RENEWALS_BELOW_THEIR_OWN_COST_FLOOR_RECOUNTED_AT_ORIGIN_HEAD_2026-10-13.md`.
> Seed 61109, the same arm and book; artefact `/var/tmp/floor-recount-out/sv-k1-61109.json`.
>
> | | ed668c733 | d55598dd6 |
> |---|---|---|
> | held loss notices | 7 | 8 |
> | held, below floor | 6 | **2** |
> | held, at floor to the penny | 0 | 5 |
> | all answered loss notices below floor | 44 / 61 | **7 / 62** |
> | save offers | 0 | **0** |
>
> **The premise "renewals sit below their own cost floor" is mostly spent.** It was writer 1's -5%
> premium, and 03a0b66da fixed it. All five held electricity renewals now sit exactly at their floor.
>
> **The save still does not fire, and on this seed the floor fix could not have changed that.** This was
> predicted (P4) before the run. The match offers `max(cost_floor, best deal)`, and only below the
> renewal. A renewal floored at its own cost leaves the match nothing to offer. So the save's
> inertness is now a question about **the save's design** (a book renewed at cost has nothing
> cheaper to give), not a pricing defect.
>
> **The writer for the 2 held renewals still below floor is the risk-tier retention cut, not a chain
> writer.** These are gas SYN-2016-045 (2025-02-08) and SYN-2016-179 (2025-04-11).
> - The class check `refuse_discretionary_rate_below_own_cost_floor` runs where
>   `renewal_rate_chain.decide_renewal_rate` returns. A fixed renewal is not held at the cap
>   (`held_at_published_cap`), and the strike sits GBP 3.1-3.5/MWh above floor at real inputs. So
>   **no chain component can leave a rate below floor without the run raising**, and it did not raise.
> - Between the chain's return and the save, the only rate writer is
>   `run_phase2b`'s `unit_rate = offered_rate(unit_rate, _retention_offer[0])`. That is the renewal cut,
>   sized by `retention_discount_for_risk` and floored nowhere.
> - The arithmetic fits the tiers. SYN-2016-179: 63.23 / 0.92 = 68.73, against a floor of 68.34. SYN-2016-045:
>   62.14 / 0.97 = 64.06, against a floor of 63.61. The chain left each just above floor, and an 8% or 3%
>   tier took it under.
>
> This is the class 03a0b66da named ("a discount may cost margin; it may never take the rate under
> cost"), with a discount writer outside the place the class is checked. Its `value_protected >
> ret_cost` test counts an acquisition cost saved, so a below-cost retention cut may still be a
> considered choice. That is the question the continuation must answer before flooring it.
>
> **A second defect found on the way: the price match mixes VAT bases.** `published_default_rate`
> is `simulation.svt_rates`, which is **inc-VAT** (gas 2025-Q2: 69.9 = Ofgem's 6.99p). The renewal rate
> and `cost_floor` are ex-VAT (`cap_ceiling_ex_vat` gives 66.57 for the same window). So
> `default x (1 - gap)` overstates the best published deal by 5% against the rate it is compared with.
> On 61109 this changes no offer, because the floor binds on every held row. It biases both the save
> and the price-match renewal cut against offering, and it explains "one renewal sat above the
> published default tariff" above, which compared an ex-VAT renewal with an inc-VAT default.
>
> Seeds 61110-61112 and the price-match side of the renewal-cut pair are re-running at d55598dd6
> (predictions P6-P7, filed first). Their results go beside the next claim.
>
> **AMENDED again 2026-10-13: P6 graded. Seeds 61110-61112 at d55598dd6, same arm and book.**
> Artefacts: `/var/tmp/floor-recount-out/sv-k1-6111{0,1,2}.json`. The count is the one used for 61109:
> held rows with renewal < `cost_floor` - 0.01, plus the number of save offers.
>
> | seed | held | held, below floor (ed668c733 -> d55598dd6) | held, at floor | all answered below floor | save offers |
> |---|---|---|---|---|---|
> | 61109 | 8 | 6 -> 2 | 5 | 7 / 62 | 0 |
> | 61110 | 7 | 6 -> **1** | 5 | 9 / 52 | 0 |
> | 61111 | 6 | 5 -> **0** | 5 | 6 / 58 | 0 |
> | 61112 | 7 | 6 -> **1** | 6 | 10 / 61 | 0 |
>
> **P6 holds on every seed.** Held below floor: 23 of 27 before, 4 of 28 now. 21 of the 28 held
> renewals sit at their floor to the penny. There were 0 offers and 0 saves. All four remaining rows
> are gas, and each one divides back to its floor or above by a tier:
> - 61110 SYN-2016-150, 64.23 against a floor of 67.21. That needs 5% or 8%.
> - 61112 SYN-2016-127, 64.66 against 66.25. Any tier reaches it.
>
> That is consistent with the risk-tier cut, but it does not identify it. 127 fits every tier, and the
> artefact keeps no retention event to tie a cut to the row. `5c137eb5b` (landed after d55598dd6)
> floors that cut, so on origin these rows should read at floor. That is not measured here.
> **The finding's headline premise is spent on all four seeds.** The save's inertness is the design
> question stated above: a book renewed at cost leaves the match nothing to offer.

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

> **AMENDED 2026-10-13: P7 graded, one seed (61109) at d55598dd6.** The price-match arm is
> `/var/tmp/floor-recount-out/rc-price_match-61109.json`. The tiers side is the save run
> `sv-k1-61109.json`: it made 0 offers, so it is the CURRENT_POLICY run, and `retention_cut_sizing`
> is `risk_tiers` there. At ed668c733 the two runs agreed to the penny (233,035.45).
>
> | 61109 | ed668c733 (tiers / match) | d55598dd6 (tiers / match) |
> |---|---|---|
> | net GBP | 233,035 / 231,396 | 253,051 / 249,962 |
> | match - tiers | -1,639 | **-3,089** |
> | renewal departures | 63 / 66 | 64 / 68 |
> | match offers, cost GBP | 47, 1,006 | **47**, 783 |
>
> Against P7:
> - **(a) is refuted.** The match made 47 offers before and 47 now. Its mean cut fell from GBP 21.4 to
>   16.7, so the floor reached the size of the cut but not the number of cuts.
> - **(b) cannot be graded.** The renewal-cut arm writes no loss-notice log, only totals. The
>   prediction asked for a field the instrument does not keep.
> - **(c)** I could not say the sign. It is negative and GBP 89 outside the GBP 3,000 band.
>
> **What this does to the withdrawal above: nothing yet, as the pre-registration said.** One seed can
> neither confirm nor withdraw. The direction repeats and the gap doubles. There is also a structural
> reason this pair is still not the fair one. At d55598dd6 the tiers side can still cut below the cost
> floor, and the match cannot. `5c137eb5b` closed that gap after these runs were launched. So this is
> the cost-respecting rule against the below-cost one, which the correction below warns about. The
> tiers arm wins that comparison by GBP 3,089 on this seed.
>
> **The re-grade that would decide it** is both arms, on four seeds, at a base that carries
> `5c137eb5b` and the value-arm term-cost base (`2473321d6`, which says the arms are re-taken). It
> is not launched from this item. Until it runs, **the renewal cut stays on risk_tiers**, as above.
>
> **P7 CORRECTED 2026-10-14, beside the -3,089 above: the deciding re-grade ran.** At 5e5358092, which
> carries the floored tiers cut (`5c137eb5b`), the ex-VAT basis (`d1e37f45c`), hedge at quote, the
> capital-inclusive floor and the term-cost base, **match minus tiers on 61109 is -4,264**. On the other
> three fresh seeds it is -8,555, -5,966 and -3,542. Net falls on every seed, so the renewal cut stays
> on `risk_tiers` by the pre-registered rule. The grade is in
> `docs/staging/records/PREREG_THE_RENEWAL_CUT_DECIDING_REGRADE_ON_A_BASE_CARRYING_THE_WEEKS_FLOORS_2026-10-13.md`.
> **The -1,175 move, split on 61109 by a one-variable arm (`d1e37f45c` reverted).** The ex-VAT basis
> is -4,156: without it the match nets -108 and makes 67 offers, not 13. The floors and the rest of the
> week are +2,981. They narrowed the gap almost to zero, and the ex-VAT basis reopened it. Why the
> ex-VAT reading cuts the match's offers fivefold is not established. Its cut-sizing function alone
> predicts the reverse.

## The next item, ahead of new work

Both grades meet the same fact: on these books in 2024-25, the renewal price the company sets sits
below its own cost floor. B8 Q5 met it as 71-77 floor declines per seed and handed it off as
`b8-q5-why-does-the-renewal-fix-sit-below-its-own-cost-floor`. It decides whether a save can ever fire,
and how a cut is sized. **Ranked P1 for next week's supplier engine**: either the renewal price is
loss-making (a pricing defect), or the floor counts a cost the renewal price is not meant to carry (a
definitional one). Which it is decides the fix.

## Correction, 2026-10-13 07:30 BST, beside the claim above (B8 seat, interconnection)

**Every arm here ran at `ed668c733` (12 Oct 17:10). That base does not contain the re-floor
`03a0b66da` (12 Oct 21:54).** The "pricing defect or definitional" question above was already
answered before this grade landed. `31e639bcd` answered it as a pricing defect: writer 1's portfolio
learning premium discounted fixes below the floor the desk struck them over. `03a0b66da` fixed it,
with the class `DISCRETIONARY_RATE_NOT_BELOW_OWN_COST_FLOOR`. The P1 ranking above is spent as worded.
What it changes:

- **The save stays inert, most likely.** Renewals writer 1 discounted now sit AT their floor, not
  below it. `price_match_save_rate` declines where `max(floor, default x (1 - gap)) >= fix`, so a
  rate at its floor still declines. Not measured. That was R4 of the re-floor's own
  pre-registration, which is ungraded.
- **This renewal-cut grade and `a99685b68`'s both predate the re-floor, and the re-floor did not
  move the two arms equally.** Under `risk_tiers`, `simulation/run_phase2b.py` offers
  `unit_rate x (1 - 3..8%)` through `offered_rate`. That is applied after the rate chain returns, so
  the invariant is never checked on it. The price match never prices below the floor. So after
  `03a0b66da` the tiers arm can contract an electricity renewal up to 8% below the cost floor
  writer 1 just stopped at. The knowledge page (`acquisition-and-retention-economics`, "How far a
  renewal discount may go") says the supplier holds "every adjustment it chooses to make to that
  floor... Only the cap may take a rate lower". A retention cut is such an adjustment. **This is a
  gap in the class, not a sizing question.** Re-running tiers against the match before the cut is
  floored would compare a cost-respecting rule with a below-cost one. The withdrawal above stands on
  its own pre-refloor evidence. Any re-grade waits for the floored cut, and for the hedge-at-quote
  and value-arm-base changes that move the same floor (DIRECTION focus four;
  `value-arm-term-cost-base-measure-what-moved`).
