**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# B8 Q5: the renewal cut sized by price match, against the risk tiers, over 2016-2025 across seeds

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
