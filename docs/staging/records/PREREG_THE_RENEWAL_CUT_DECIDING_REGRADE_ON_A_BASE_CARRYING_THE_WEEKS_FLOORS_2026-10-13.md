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

## Added 2026-10-14 01:35 BST, before its arms run: the one-variable split of P7's move

Five commits changed between the d55598dd6 runs and this base, so this base's net can't be
split between the ex-VAT basis (`d1e37f45c`) and the floors. The one-variable arm is this
base with `d1e37f45c`'s three code files reverted: `run_phase2b.py`, `company/crm/save_offer.py` and
`company/interfaces/save_offer.py`. That puts the inc-VAT default back into `_price_match_inputs`.
Both arms run on seed 61109, worktree /var/tmp/se-rc3-novat, artefacts
/var/tmp/regrade3/out/novat-<arm>-61109.json. The ex-VAT share is (this base) minus (novat), and the floors'
share is the rest of the move from d55598dd6's -3,089.

- V1. Without the ex-VAT basis the match makes AT MOST the 13 offers it makes here. The inc-VAT default
  reads the market's match dearer, so fewer re-fixes sit above it.
- V2. The tiers arm's net moves by under GBP 500. The tiers cut does not read `_price_match_inputs`.
  Only the save does, and the save made 0 offers at d55598dd6.
- V3. The ex-VAT basis is under half of the 61109 move (|novat diff minus this base's diff| < GBP 588
  of the GBP 1,175 move from -3,089 to -4,264). The floors are the larger part. I cannot predict its sign.

## Result (2026-10-14 02:10 BST, worker tick), beside the predictions above, which are unedited

All eight arms are whole. Each artefact records head 5e5358092 and ran 72-85 minutes, in
/var/tmp/regrade3/out/rc-<arm>-<seed>.json. The cut's size is read as offer cost over offers, the same
proxy the ed668c733 grade used.

| seed | offers, tiers / match | offer cost GBP, tiers / match | mean cut GBP, tiers / match | net, match - tiers | renewal departures, tiers / match |
|---|---|---|---|---|---|
| 61109 | 70 / 13 | 836 / 204 | 11.95 / 15.72 | **-4,264** | 63 / 73 |
| 61110 | 82 / 8 | 1,080 / 99 | 13.17 / 12.43 | **-8,555** | 52 / 66 |
| 61111 | 74 / 11 | 769 / 300 | 10.39 / 27.24 | **-5,966** | 61 / 76 |
| 61112 | 74 / 9 | 908 / 102 | 12.27 / 11.28 | **-3,542** | 59 / 68 |

The difference has a mean of -5,582 and a seed standard deviation of 2,227. Across four seeds, the
match spends GBP 600-1,000 less on offers. It loses 9-15 more renewal departures, worth GBP 3,500-8,600 net.

- **1, the match makes at most half the tiers' offers: held on every seed** (0.10-0.19 of them; it was
  0.54-0.71 at ed668c733).
- **2, the match's mean cut is at or below the tiers': refuted.** It held on 61110 and 61112, and was
  refuted on 61109 (15.72 against 11.95) and 61111 (27.24 against 10.39). At about 10 offers a seed,
  one deep cut moves the match's mean. The floored tiers' cut is now GBP 10-13. It was 24-30.
- **3, the match's offer cost is lower: held on every seed.**
- **4 and 5 cannot be graded.** The arm tool writes only totals, with no no-offer log by cause.
  The ed668c733 grade said the same. These predictions ask for a field the instrument does not keep.
- **6, net within plus or minus GBP 2,000 with a mixed sign: refuted.** All four seeds are outside the
  band, and the sign is negative on all four.
- **7, the tiers' mean cut on 61109 below GBP 21.4: held** (11.95). *Correction, beside the claim: the
  GBP 21.4 at ed668c733 was the MATCH's cost per offer (1,006 / 47). The tiers' figure was 24.3 (1,824 / 75).
  The prediction holds against either.*
- **8, |net| on 61109 smaller than GBP 3,089: refuted** (4,264). The floor on the tiers' cut did not
  narrow the gap. It widened it on this seed and on the mean.

**Decision, by the rule fixed above.** "Do not recommend the switch if net falls on every seed." Net
falls on every seed. This result rests on all four seeds, not one: the smallest gap (-3,542) is 1.6
seed-spreads from zero. **The renewal cut stays on `risk_tiers`.** No default changes, so no K8
section is owed. The floored tiers are now the cost-respecting rule on both sides. This is the
fair comparison the 13 Oct correction asked for, and the tiers still win it. The tiers spend GBP
800-1,100 a seed at or above the floor and keep 9-15 renewals the match loses. That is margin kept
on supply the company would otherwise lose. It is not a transfer to households who would have
stayed. This run does not test that claim: it keeps no counterfactual of who would have
left without the cut.

**A fault in the queue's wait signal, beside the item that pointed at it.** /var/tmp/regrade3/queue.log
printed `RC3 ALL FINISHED 23:52:52Z` one second after `RC3 ALL LAUNCHED`. That was 72 minutes before
the last three artefacts existed. `launch_long_job --follow-only` reported `Result=success after 0s,
artefact MISSING` for units that had just started. A wait on that line would have graded half the
arms.

The ex-VAT and floors split of P7's move is graded in the next section, when its two arms finish.

## Result of the one-variable split (2026-10-14 03:15 BST), beside V1-V3, which are unedited

Both arms are whole: /var/tmp/regrade3/out/novat-<arm>-61109.json. They ran at 5e5358092 with
`d1e37f45c`'s three code files reverted in the working tree. The artefact's `head` field reads
5e5358092 because the tool reads HEAD, not the tree.

| 61109 | d55598dd6 | 5e5358092, inc-VAT default (novat) | 5e5358092 as landed (ex VAT) |
|---|---|---|---|
| tiers net | 253,051 | 252,224.50 | 252,224.50 |
| match net | 249,962 | 252,116.63 | 247,960.04 |
| **match - tiers** | **-3,089** | **-108** | **-4,264** |
| match offers, cost GBP | 47, 783 | 67, 872 | 13, 204 |
| match renewal departures | 68 | 63 | 73 |

- **V1, at most 13 offers without the ex-VAT basis: refuted, and the direction is opposite.** The match
  makes 67 offers on the inc-VAT default and 13 on the ex-VAT one. `price_match_save_rate` alone
  predicts the reverse: a lower default lowers the match and admits more cuts. So the drop happens
  after the cut is sized. The candidates are the value test (a deeper cut costs more than the value it
  protects), `retention_offer_can_buy_anything` (which reads `position_vs_default` for the offered rate),
  and the holdout. **Which one is not established.** The arm keeps no no-offer reasons, so this run
  cannot say.
- **V2, the tiers' net moves under GBP 500: held.** It moved GBP 0.00, identical to the penny.
- **V3, the ex-VAT basis is under half of the move: refuted.** The move from -3,089 to -4,264 is
  -1,175. The ex-VAT basis alone is **-4,156** (-108 to -4,264). Everything else between d55598dd6 and
  5e5358092 is **+2,981** (-3,089 to -108). That is the floored tiers cut, hedge at quote, the
  capital-inclusive floor and the term-cost base, which this split does not separate. So the
  floors narrowed the gap almost to nothing, and the ex-VAT basis opened it again, wider.

**What this does to the decision: it stands, and it now rests on one commit.** On the basis the
code holds to be correct (ex VAT, as the re-fix and floor are), the match loses on all four seeds.
On the old basis it ties the tiers on 61109 (-108, inside P6's band). `d1e37f45c`'s message says
the inc-VAT reading made both desks under-offer. At the renewal cut, on this seed, the ex-VAT reading
offers a fifth as often. Until the gate that drops the 54 offers is named, "the price match loses"
means "the price match, as the ex-VAT basis now feeds it through the offer gates, loses". It does not
show that matching the market is the worse rule. The cut stays on `risk_tiers`, by the rule and
erring against the thesis (F11).
