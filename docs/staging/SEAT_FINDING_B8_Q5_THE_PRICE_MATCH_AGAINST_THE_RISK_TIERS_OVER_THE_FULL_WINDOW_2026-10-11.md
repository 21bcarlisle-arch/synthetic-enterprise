**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 Q5: the renewal cut sized by price match, against the risk tiers, over 2016-2025 across seeds

**Fate (2026-10-12, clear-the-decks):** ATOM -- price_match sizing recommended over risk_tiers on all 3 seeds, but CURRENT_POLICY.retention_cut_sizing is still "risk_tiers" -- flip not actioned, awaiting director/next build turn (P2)

**Withdrawn (2026-10-13):** the recommendation below did not survive four fresh book seeds. Net fell on every seed, so the rule's "do not recommend" branch held (`b234e27bd`). Both grades ran before the re-floor `03a0b66da`, and the tiers' retention cut is still unfloored. See the correction in `SEAT_FINDING_ON_FRESH_SEEDS_THE_SAVE_NEVER_FIRES_BECAUSE_RENEWALS_SIT_BELOW_THEIR_OWN_COST_FLOOR_AND_THE_PRICE_MATCH_RENEWAL_CUT_LOSES_NET_2026-10-13.md`.

**The floor question (2026-10-12):** the 71-77 floor declines per seed are not a floor defect -- the rate chain's portfolio learning premium (writer 1, down to -5%) discounts fixes below the cost floor the desk struck them over, and the match rightly refuses to cut them further. The flip need not wait on it: `SEAT_FINDING_B8_Q5_WHY_THE_RENEWAL_FIX_SITS_BELOW_ITS_OWN_COST_FLOOR_2026-10-12.md`.

*2026-10-11, delivery seat (direction `b8-q5-price-match-as-the-standing-renewal-cut`).*

`d06b039e7` built `DecisionPolicy.retention_cut_sizing = "price_match"`, off by default. On one seed
to 2019, with the holdout on, it offered in 15 places where the tiers offered in 41. Mean cut was
3.1% against 4.0%, offer cost GBP 332 against 932, and net was +GBP 577. That is not a result. This
is the standing-policy test: `CURRENT_POLICY` with only the sizing changed, holdout off, full window.

## Pre-registration (filed before any run)

**Arms.** `CURRENT_POLICY` with `retention_cut_sizing` set to `risk_tiers` (as now) or `price_match`.
Nothing else changes. Driver: `/var/tmp/se-b8-q5-full/arm.py`, one process per arm, `report_end=None`.

**Seeds.** `base` is the unpatched world. `11111` and `22222` are the first two of the value arms'
churn-roll floor seeds. They re-draw `churn_roll_for_renewal` by the floors' own stream
(`floor{seed}_{account}_{term}`) at every `simulation.*` binding of the function, so one renewal
reads one roll everywhere. The value arms' floor patches only `customer_events`'s binding, and this
re-draw is wider than that, on purpose. The book is the default book, because book seeds are the
director's.

**What is counted, per arm and seed:**

- the renewals reaching the value test;
- offers made, by year;
- offers retained;
- mean cut;
- offer cost, by year;
- total net;
- under the match, every no-offer split by its cause:
  - `input_missing`, with which input;
  - `market_had_nothing_cheaper_than_the_default` (gap at or below 0);
  - `our_cost_floor_is_at_or_above_the_fix`;
  - `the_fix_already_meets_the_best_published_deal` (the market's match is at or above our re-fix).

**Predictions:**

1. Under the match, offers are at most half the tiers' offers, on every seed.
2. The match's mean cut is at or below the tiers' mean cut, on every seed. (The 2019 run refuted
   "deeper". I now expect narrower, not deeper.)
3. The match's offer cost is lower, on every seed.
4. `the_fix_already_meets_the_best_published_deal` is the commonest no-offer cause, on every seed.
   `input_missing` is at most 5% of the no-offers.
5. `market_had_nothing_cheaper_than_the_default` falls only on terms starting 2021-10 to 2023-06.
   That is the zero-gap quarters.
6. Net, match minus tiers, lies within ±GBP 2,000 on every seed. That is under 1% of a full-window
   net. **I predict its sign is not the same on all three seeds.** In other words, I expect the
   sizing not to be distinguishable on money.

**Decision rule, fixed now.**

- **Recommend the switch** if, on every seed, the match spends less on offers and net is not lower
  by more than one seed-spread of the noise. A narrower rule that pays a cut only where the market
  can undercut us moves less value from the company to households who would not have left for
  price. That is the mission's created-versus-transferred test.
- **Do not recommend the switch** if net falls on every seed. Then the tiers' extra offers bought
  retention worth more than they cost.

## Result

*(beside the predictions above, which are unedited)*

**Run state, 2026-10-12.** Both base arms finished on 2026-10-11 at `77cc6a9a9`, in 68 min each with a
3.5 GB peak. Both 11111 arms died on start. The driver's first draft walked every module in
`sys.modules` with `getattr(m, "churn_roll_for_renewal")`, and `pymc_extras.prior`'s module
`__getattr__` raised `UnsupportedDistributionError` for the name. The fix was already in `arm.py`:
check `name.startswith("simulation")` before the `getattr`. A dry run of the patch binds
`customer_events`, `retention_offer` and `run_phase2b`. The lazy imports in `coin_drawn_decision_set`
read the patched `customer_events`. Seed 22222 had never launched. All four seed arms were relaunched
together at 09:36-09:38 BST from the same worktree and head as the base arms. The grade of the six arms
follows when they finish. Grader: `/var/tmp/se-b8-q5-full/grade.py`. It asserts both arms share a head
and that the re-draw fired on each seed arm.

**Base seed (tiers / match):**

| seed | reaching value test | offers (ratio) | retained | mean cut | offer cost GBP | total net GBP | net, match - tiers |
|---|---|---|---|---|---|---|---|
| base | 203 / 205 | 110 / 49 (0.45) | 80 / 35 | 4.42% / 2.72% | 3,501 / 815 | 404,929 / 405,834 | +905 |

On the base seed, P1, P2, P3, P5 and the P6 bound hold. **P4 is refuted.**
`the_fix_already_meets_the_best_published_deal` is the rarest no-offer cause, not the commonest: 7 of
135. `our_cost_floor_is_at_or_above_the_fix` accounts for 117 of 135, and `market_had_nothing_cheaper`
for 11, all on terms starting 2021-10 to 2021-12. `input_missing` is 0.

**An odd reading, not built on.** "Our cost floor is at or above the fix" means the re-fix unit rate we
struck sits *below* our own floor (`company_fwd + locked policy + locked network`). Example: 2017-01-09
electricity, fix GBP 132.2/MWh against a floor of 136.3. That is either a renewal priced under its
own cost, or a floor that counts costs the standing charge recovers. I cannot yet say which. It is
raised as a question, not answered here.

**All six arms, graded 2026-10-12** (`grade.py`). Every arm ran at `77cc6a9a9`. The roll re-draw fired on
each seed arm: 469 / 356 re-drawn renewals on 11111 (tiers / match), and 458 / 356 on 22222.

| seed | reaching value test | offers (ratio) | retained | mean cut | offer cost GBP | total net GBP | net, match - tiers |
|---|---|---|---|---|---|---|---|
| base | 203 / 205 | 110 / 49 (0.45) | 80 / 35 | 4.42% / 2.72% | 3,501 / 815 | 404,929 / 405,834 | +905 |
| 11111 | 207 / 206 | 108 / 48 (0.44) | 71 / 31 | 4.27% / 2.53% | 2,872 / 629 | 395,796 / 396,681 | +885 |
| 22222 | 185 / 185 | 101 / 43 (0.43) | 65 / 25 | 4.25% / 2.66% | 2,857 / 593 | 397,153 / 395,812 | -1,341 |

No-offer causes under the match:

| seed | cost floor at or above the fix | market had nothing cheaper | the fix already meets the best deal | input missing |
|---|---|---|---|---|
| base | 117 of 135 | 11 | 7 | 0 |
| 11111 | 117 of 137 | 11 | 9 | 0 |
| 22222 | 106 of 122 | 9 | 7 | 0 |

The zero-gap no-offers fall only on terms starting 2021-10 to 2021-12, on every seed.

Offers by year: the tiers offer in 2016, 2017–2021 and 2024–2025. The match offers only in 2017–2021
(base: 25/14/1/1/8). It makes no offer at all from 2022 on, on any seed.

**Predictions, graded:**

| | prediction | verdict |
|---|---|---|
| P1 | match offers at most half the tiers' offers | **HELD** on all three seeds (0.45, 0.44, 0.43) |
| P2 | match mean cut at or below the tiers' | **HELD** on all three |
| P3 | match offer cost lower | **HELD** on all three: about GBP 2,250–2,690 less over the window |
| P4 | `the_fix_already_meets_the_best_published_deal` is the commonest cause | **REFUTED** on all three. It is the rarest cause. `our_cost_floor_is_at_or_above_the_fix` is 85–87% of no-offers. The input-missing half holds (0). |
| P5 | zero-gap no-offers only on terms starting 2021-10 to 2023-06 | **HELD** on all three. Inside the window they fell only on terms starting 2021-10 to 2021-12. |
| P6 | net difference within ±GBP 2,000, sign not uniform | **HELD** on both halves: +905, +885, -1,341 |

**Decision rule, applied as written.** Did the match spend less on offers on every seed? Yes. Is net
lower by more than one seed-spread of the noise on any seed? No. The rule did not say which spread it
meant, so here are both:

- The tiers' net varies by GBP 9,132 across seeds.
- The match-minus-tiers difference varies by GBP 2,247 across seeds.

The one negative seed, -1,341, is inside either spread. Net did not fall on every seed, so the "do not
recommend" branch is not met. **The rule recommends the switch: `retention_cut_sizing = "price_match"`
as the standing renewal cut.**

**What the switch buys, read through M2.** The tiers make about 60 more offers per seed and record
about 40 more "retained" offers. They pay roughly GBP 2,300–2,700 more in cuts for it, and net is
unchanged within noise. Retention bought that does not move net looks like transfer: a cut paid to
households who would have stayed anyway. I cannot say that per account from these counts. The counts
are consistent with it and with no other reading I can rank above it.

**Not done here.**

- The default is not flipped. `CURRENT_POLICY` is the standing commercial policy, so the change is a
  recommendation for the director (G9 if he ruled the tiers; otherwise a reversible flip owed by the
  next build turn).
- The "cost floor at or above the fix" oddity from the base seed now carries 85–87% of no-offers on
  every seed. Whatever it is, it is what decides where the match declines. A renewal priced under its
  own floor would be an absurdity class, so it comes before the flip: if the floor double-counts
  standing-charge-recovered cost, the match is declining for the wrong reason.

**Does the cause order drive P4's refutation? Checked: no.** The driver classifies with an `if/elif`
chain, and the floor test runs before the best-deal test. Production's
`price_match_save_rate` (`company/crm/save_offer.py`) declines when
`max(floor, default × (1 − gap)) >= fix`, so one row can be declined for both reasons at once.
Re-counting from the rows:

| seed | floor rows where the market's match also does not beat the fix | declined by the floor alone | declined by the market's match |
|---|---|---|---|
| base | 41 of 117 | 76 | 48 |
| 11111 | 40 of 117 | 77 | 49 |
| 22222 | 35 of 106 | 71 | 42 |

"Declined by the market's match" counts the overlap rows plus the rows classified as
`the_fix_already_meets`. Even with every overlap row given to the market, the floor alone still
declines more renewals on every seed. P4 stays refuted. The cost-floor question above is the real
driver of where the match declines, not an artefact of the chain's order.
