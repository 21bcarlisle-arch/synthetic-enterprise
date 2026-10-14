# Pre-registration: which gate drops the price match's renewal-cut offers from 67 to 13 on seed 61109

*Written 2026-10-14 03:19 BST, before the census arms run. Item `price-match-offer-gate-under-the-ex-vat-basis`,
handed off by 5074f1d40. The predictions below are not edited after the result; the result goes beneath them.*

## What is already established, by printing the inputs (no run)

`5074f1d40` found that on seed 61109 at 5e5358092 the price match makes 67 renewal-cut offers on the inc-VAT
default (`d1e37f45c` reverted) and 13 on the ex-VAT one. It reasoned that a lower default can only admit more
cuts, so the drop has to be in a gate downstream of the sizing: the value test, `retention_offer_can_buy_anything`,
or the holdout.

That reasoning assumed the ex-VAT reader returns a LOWER number. Printed at real dates, it does not always return
a number at all. `published_default_rate_ex_vat` is `cap_ceiling_ex_vat`, and the cap began on 2019-01-01:

| date | best-deal gap | elec inc VAT (`svt_rates`) | elec ex VAT (cap) | gas inc VAT | gas ex VAT |
|---|---|---|---|---|---|
| 2016-01-15 .. 2018-10-15 (12 quarters) | 0.17-0.32 | 140.0 / 152.5 | **None** | 28-40 | **None** |
| 2019-01-15 .. 2022-07-15 | 0.0-0.33 | | ratio 1.050 exactly | | ratio 1.050 |
| 2022-10-15 .. 2023-04-15 (EPG) | 0.0 | 519-675 | 323.8 | 126-171 | 98.3 |
| 2023-07-15 .. 2025-10-15 | 0.04-0.15 | | ratio 1.050 | | ratio 1.050 |

From 2019 the two readings differ by VAT only, as `d1e37f45c` intended. The EPG window has no gap, so no
match either way. Before 2019 the ex-VAT default is None. `price_match_save_rate` returns None on any missing input,
so the cut is None and the run records the reason as `the_fix_already_meets_the_best_published_deal`, which is
not what happened. Those are also the twelve quarters where the published gap is widest.

The value test can't refuse a price-match cut on the standing policy: engagement weighting and bad-debt netting
are off, so value protected = (unit - forward) x EAC + acquisition saved. The cut is at most
(unit - floor) x EAC, and floor = forward + policy + network costs, which is above the forward. The holdout is off
on `CURRENT_POLICY`.

## Set-up

Seed 61109, 400 founders, budget 0, to 2025-06-07, price_match arm only, through /var/tmp/regrade/seeded_arm.py and
/var/tmp/regrade4/gate_census_arm.py. That is renewal_cut_arm.py plus wrappers on run_phase2b's module names, which
write one row for each renewal the cut is sized for: date, fuel, the match's inputs, cut, can-buy, value protected,
billed, and whether an offer was booked. No code under test is edited. Two arms:
- **exvat**: /var/tmp/se-rc4-exvat, clean at 5e5358092.
- **novat**: /var/tmp/se-rc3-novat, 5e5358092 with `d1e37f45c`'s three code files reverted, the tree that made the 67.

## Predictions

- **G1.** exvat: every evaluation dated before 2019-01-01 has `published_default_rate` None and cut None. Zero
  offers before 2019.
- **G2.** novat: at least 40 of its offers are dated before 2019-01-01. *Reasoning: the gaps are 17-32% there and
  3.7-15% after. The 47-offer run at d55598dd6 also predates the ex-VAT change.*
- **G3.** From 2019-01-01 on, exvat makes at least (novat's post-2019 offers minus 5). The basis change itself does
  not suppress offers.
- **G4.** Neither arm has an evaluation where cut is not None, can-buy is True, value protected <= cut x billed,
  and no offer is booked. The value test refuses none.
- **G5.** Post-2019, the can-buy refusals on exvat are no more than on novat. A deeper cut lowers the offered
  position.
- **G6, the reading.** If G1-G3 hold, no downstream gate drops the 54 offers. The cause is the sizing's missing
  pre-2019 default. The decision in 5074f1d40 then rests on the match making NO offer for three years, because
  there is no published cap to match against. It does not rest on matching costing more than it protects.
  That is a GAP in what the company can read: a pre-cap published default. It is not evidence about the
  matching rule.

If G4 fails, the value test refuses cuts and the arithmetic above is wrong somewhere. That would be the finding.

## Result (2026-10-14 05:40 BST), beneath G1-G6, which are unedited

Both arms are whole: /var/tmp/regrade4/out/gate-{exvat,novat}-61109.json, finished 05:16-05:17. Their
nets and offer counts reproduce 5074f1d40's exactly (exvat 247,960.04 on 13 offers; novat 252,116.63 on
67), so the wrappers changed nothing they watched. This file's sha256 at grading equals the one filed at
03:19 (/var/tmp/regrade4/PREREG.sha256). Reasons come from /var/tmp/regrade4/grade.py, written before the
arms finished.

| 61109, renewals sized | exvat pre-2019 | exvat 2019+ | novat pre-2019 | novat 2019+ |
|---|---|---|---|---|
| no published default (cut None) | **96** | 0 | 0 | 0 |
| published gap is zero (EPG window) | 0 | 9 | 0 | 9 |
| re-fix already at or below the match | 0 | 32 | 9 | 34 |
| cut sized, discount cannot win the fix | 0 | 18 | 25 | 12 |
| cut sized, fails the value test | 0 | 0 | 0 | 0 |
| **offered** | **0** | **13** | **57** | **10** |

- **G1: held.** Every one of exvat's 96 pre-2019 evaluations has `published_default_rate` None, and no
  offer is made before 2019.
- **G2: held.** 57 of novat's 67 offers predate 2019 (43 in 2017, 14 in 2018; 30 electricity, 27 gas).
  They were sized against a mean published gap of 0.26, and the cost floor bound them to a mean cut of 2.2%.
- **G3: held, and exceeded.** From 2019 on, exvat makes 13 offers against novat's 10. Moving the default
  to ex VAT does what d1e37f45c said it would: it admits more cuts.
- **G4: held.** Neither arm has a row with a sized cut that can buy something and that the value test
  refuses. The holdout is off. The value test drops nothing.
- **G5: refuted as written.** From 2019 on, exvat has 18 can-buy refusals against novat's 12. But exvat
  has more cuts to refuse (31 sized against 22), the refusal rate is about the same (58% and 55%), and
  every refusal in both arms is a household whose previous term was on our default. Pre-2019 offers change
  who is on the book after 2019, so the populations are not the same. The prediction compared counts
  across two different books. It should have compared rates over the same rows. This does not move G6.
- **G6, the reading: held.** No downstream gate drops the 54 offers. The drop is in the sizing:
  `published_default_rate_ex_vat` reads the cap, and there was no cap before 2019-01-01, so the match
  has nothing to match against for the twelve quarters with the widest published gaps (0.17-0.32). On
  the inc-VAT reading, `simulation.svt_rates` answered those quarters from its pre-cap table (published
  ranges, M confidence, +/-15%). That table is the world's, and the company now reads the cap instead.

**What this means for the decision in 5074f1d40.** "The price match loses on 61109" means the match
made no offer at all from 2016 to 2018, because the company reads no published default before the cap.
It does not mean the matching rule costs more than it protects. The value test refused nothing in either
arm. With the pre-cap quarters answered (on a basis 5% dear), the match ties the tiers (-108). This is a
GAP in what the company can read, not evidence against the rule. It is not a basis mismatch inside the
gate. Whether a pre-cap published default exists for the company to read is the open question. The
knowledge map's *SVT unit rates 2016-2025* row holds pre-cap ranges at M confidence, back-derived from
QEP bills and Ofgem SVT league tables that are "not fully digitised".
`position_vs_default` and the value test are not where the loss comes from.
