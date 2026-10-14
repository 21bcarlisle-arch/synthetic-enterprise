**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** none -- a re-grade of a built capability against predictions filed in docs/staging/records/PREREG_THE_PRICE_MATCH_AGAINST_RISK_TIERS_FROM_2019_WHERE_A_DEFAULT_IS_PUBLISHED_2026-10-14.md and its 2026-10-14 addendum; the pricing pages are docs/market_research/retention_slope_per_pound_of_renewal_cut.md and a_save_offer_against_the_switching_rules_and_the_seam.md

# The price match against risk tiers from 2019, on writer one's basis (2026-10-14)

*Delivery seat, LANE 0 draw `grade-regrade5-arms-after-the-last-seed`. Graded at 22:50 BST by
`/var/tmp/regrade5/grade5.py`, against the prereg named above. Its sha256 is `f49ad643`, the same on
origin/main and in `/var/tmp/regrade5/PREREG.sha256`. Every artefact read carries head `87e9f4245`.*

## State at grading: 7 of 8 arms, 3 of 4 seeds

`risk_tiers-61112` is still running (unit `longjob-regrade5-risk-tiers-61112`, started 21:34 BST).
The item expected each arm to take about 136 min, but these arms took **18,391-18,473 s (about 5.1 h)**
each. So the last arm lands around 02:40 BST on 2026-10-15. grade5 printed `INCOMPLETE`, and no unit
has failed.

| seed | C1 | C2 (matched / tiered) | d_net hybrid - tiers | offers from 2019 T/H | cut GBP from 2019 T/H | departures from 2019 T/H |
|---|---|---|---|---|---|---|
| 61109 | True | 64 / 104 | **+177.45** | 12 / 10 | -484.76 / -512.34 | 37 / 37 |
| 61110 | True | 64 / 96 | **-2,485.67** | 16 / 12 | -637.27 / -493.75 | 26 / 29 |
| 61111 | True | 59 / 88 | **-1,542.65** | 17 / 13 | -586.30 / -543.02 | 39 / 42 |
| 61112 | pending | 58 / 107 | pending | pending / pending | pending | pending |

## The verdict cannot be changed by the fourth seed, unless C1 fails on it

The decision rule's two active branches both need **4 of 4** seeds to have the same sign. 61109 is
positive and 61110 and 61111 are negative, so neither branch can fire whatever 61112 shows. The
predictions are settled the same way:

- **P1 HOLDS.** The hybrid made fewer offers from 2019 on 3 of 3 seeds, which already meets the ≥3/4 bar.
- **P2 REFUTED.** On 61110, |d_net| = 2,485.67 is over the GBP 2,000 bound. The bound was set from
  61109's -108 under the old basis, and 61109 alone stays inside it (+177).
- **P3 HOLDS.** The signs are already mixed: 1 positive and 2 negative.
- **S1 HOLDS.** On the tiers arm the save made 3, 3 and 2 offers, so it fired on 3 of 3 seeds. That
  meets the ≥3/4 bar. The floor account of the inert save stands: with the blanket -5% gone, renewals
  sit above their floor and the save fires.
- **DECISION: no evidence either way. The cut stays on `risk_tiers` (F11).** This settles
  d5ba38b12's question on the corrected basis. The match lost net on every seed under the old floor.
  On writer one's basis it does not lose consistently, but it does not win either. Nothing goes to
  the director, because neither the propose branch nor the M2 branch fired.

The one way 61112 can still change this is by voiding it. If C1 fails there, grade5 prints VOID and
the comparison grades nothing. C2 already holds on 61112, because its hybrid artefact has both legs
of the swap.

**Prediction for `risk_tiers-61112`, filed before it exists (22:55 BST):** C1 holds. The tiers arm
will read `offers_pre2019` 68, `cost_pre2019_gbp` -1388.61 and `renewal_departures_pre2019` 32,
exactly the hybrid's figures. d_net is negative (a guess from 2 of 3; it does not bear on the
verdict). The save makes ≥1 offer on the tiers arm, because the hybrid made 4 there.

## What the numbers say beyond the rule

- **The hybrid gives fewer offers, and retention is no better or worse.** From 2019 it made 2-4 fewer
  offers per seed. It lost the same number of customers at renewal or up to 3 more, and its net is
  -2,486 to +177. A supplier could run the match where the cap publishes a default, but in this world
  that buys nothing at the retention lever. That is weaker than the M2 answer ("matching does not
  create value") the rule would have recorded on 4 of 4 negative. Two of three seeds lean that way,
  but that is not evidence by the rule fixed in advance.
- **The save fires, and nobody takes it.** On 61109-61112, the arms that have finished made 19 save
  offers between them (8 on tiers arms, 11 on hybrid arms), all in 2024-2025, and `saves_taken` is 0
  on every arm. S1 asked only whether it fires. The addendum's next question was whether it creates
  value, through a save-off arm. With zero acceptances, that question has a prior answer. A save-off
  arm can differ from this one only by those 2-4 offers' cost and any book effect, and no customer
  was retained. Before anyone spends arms on value, the next question is why no offer is accepted:
  is the offer too small to clear the switch, or does the acceptance model never see it?

## Defect in the grader, inert for this verdict

The prereg's propose branch requires that "the pounds of renewal cut customers receive from 2019 are
not lower on 3 or more seeds". `cut_gbp` is signed negative (money given). grade5 computes
`cut_lower = ph < pt`, but that counts seeds where the hybrid gave customers **more**, which is the
reverse of the prereg. It feeds only the propose branch, and that branch needs 4 of 4 positive, which
cannot happen here. So this verdict is unaffected. A re-use of grade5 must flip it to `ph > pt`, or
compare `abs()`. On the three graded seeds, the hybrid gave less on 61110 and 61111 and more on 61109.

## Correction to the drawn item

The item planned around "~136 min" per arm, from an earlier 61109 run of 8,187 s. On this base the
arms take 2.25x that. The continuation is timed from the unit's own start (21:34 BST) plus the
observed 18,4xx s.
