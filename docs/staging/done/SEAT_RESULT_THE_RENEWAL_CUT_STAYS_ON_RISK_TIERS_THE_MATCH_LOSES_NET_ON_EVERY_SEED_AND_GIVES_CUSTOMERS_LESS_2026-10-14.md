**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** none -- a re-grade of a built capability against predictions filed in docs/staging/records/PREREG_THE_RENEWAL_CUT_DECIDING_REGRADE_ON_A_BASE_CARRYING_THE_WEEKS_FLOORS_2026-10-13.md (668cb63db); the pricing pages are docs/market_research/retention_slope_per_pound_of_renewal_cut.md and a_save_offer_against_the_switching_rules_and_the_seam.md

# The renewal cut stays on risk tiers: the price match loses net on every seed and gives customers less (2026-10-14)

The deciding re-grade that SEAT_FINDING_ON_FRESH_SEEDS_THE_SAVE_NEVER_FIRES_..._2026-10-13.md and
82e84e4a4 named. Base 5e5358092, which carries 03a0b66da, 5c137eb5b, 61c122683, 434d87587 and
2473321d6. Book seeds 61109-61112, 400 founders, budget 0, to 2025-06-07, frozen payment world.
All eight arms ran on that one head (each artefact's `head` matches) and finished by 01:05Z.
Artefacts: /var/tmp/regrade3/out/rc-{risk_tiers,price_match}-{seed}.json.

| seed | tiers offers | tiers cost | tiers net | match offers | match cost | match net | match - tiers | departures t/m |
|---|---|---|---|---|---|---|---|---|
| 61109 | 70 | 836 | 252,224 | 13 | 204 | 247,960 | **-4,264** | 63 / 73 |
| 61110 | 82 | 1,080 | 266,532 | 8 | 99 | 257,977 | **-8,555** | 52 / 66 |
| 61111 | 74 | 769 | 282,496 | 11 | 300 | 276,529 | **-5,966** | 61 / 76 |
| 61112 | 74 | 908 | 287,252 | 9 | 102 | 283,710 | **-3,542** | 59 / 68 |

GBP. "Cost" is the retention cost the arm books, so cost per offer is the mean cut in pounds.

## The predictions, graded

1. Match offers at most half the tiers': **held** on all four seeds (8-13 against 70-82).
2. The match's mean cut at or below the tiers': **refuted**. It held on 2 of 4; on 61109 it was
   GBP 15.7 against 11.9, and on 61111 GBP 27.2 against 10.4.
3. The match's offer cost is lower: **held** on all four.
4 and 5. No-offer causes: **ungradable**. The arm writes no per-offer cause, the same gap
   82e84e4a4 recorded for P7(b).
6. Net within plus or minus GBP 2,000 with a mixed sign: **refuted**. The match is lower on every
   seed, by GBP 3,542 to 8,555 (the paired differences have a spread of GBP 2,227).
7. The tiers' mean cut on 61109 below GBP 21.4: **held** (11.9). *Corrected here:* the 21.4 I
   quoted was the match's cost per offer at ed668c733, not the tiers'. The tiers' figure was 24.3,
   so the floor more than halved the tiers' cut. Either reading holds.
8. |match - tiers| on 61109 below GBP 3,089: **refuted** (4,264).

## The decision

The rule reads: recommend the match if it spends less on offers on every seed and its net is not
lower by more than one seed-spread. The first half holds. The second depends on what
"seed-spread" counts:
- Read as the across-seed spread of net (about GBP 16,000, mostly book-to-book difference), it
  would recommend the match.
- Read as the paired difference between arms on the same seed, the match is lower 4 of 4 times
  and by more than that difference's own spread. A sign test on 4 of 4 gives one-sided p = 1/16.

The across-seed reading compares a within-seed effect against between-book noise that the
pairing removes, so it is not the quantity the rule needs. I read it paired, which also errs
against switching (F11). **Stay on risk tiers.** This confirms the a99685b68 withdrawal on a base
carrying this week's floors.

**Both sides of the value (M2) point the same way.** Under the tiers, customers receive GBP
770-1,080 a seed in renewal cuts, against GBP 100-300 under the match. The company nets GBP
3.5k-8.6k more, because 9-15 fewer customers leave at renewal. The match moves less value to
customers and keeps less for the company.

## What I cannot say

On 61109 the match made 47 offers at d55598dd6 and makes 13 here. More than one thing changed
between those bases (434d87587's capital-inclusive floor, 2473321d6's term-cost base, 61c122683),
so the fall cannot be attributed to any one of them. The one-variable run is the match at
d55598dd6 plus 434d87587 alone.

The rule's "seed-spread" should be defined in the rule itself before it is used again.

## Corrected 2026-10-14, beside the decision and not over it: the match is mute before 2019, not refused

The census in docs/staging/records/PREREG_THE_PRICE_MATCH_OFFER_GATE_UNDER_THE_EX_VAT_BASIS_2026-10-14.md
(seed 61109, both bases) shows no gate drops the match's offers. The company's ex-VAT default is the cap,
and there was no cap before 2019, so the match makes **no offer at all from 2016 to 2018**. Those were 57
of the 67 offers on the inc-VAT reading. From 2019 the ex-VAT match offers more (13 against 10), and the
value test refuses nothing on either basis. So "the match loses net on every seed" is a comparison of the
tiers against a match that sat out three years for lack of a default to match. It does not show matching
is the worse rule. **The decision stays on `risk_tiers`** (F11: the evidence for switching is not in
hand). Re-grading the match is owed once the company can read a pre-cap published default, or the
comparison is restricted to 2019 onwards.
