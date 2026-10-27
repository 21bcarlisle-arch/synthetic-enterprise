**Knowledge:** none -- a paired world-only capture testing a hypothesis already written in `docs/market_research/income_shock_depth_and_duration_b7.md` §8; no new domain claim

# The price-held capture: do 2020-21 bills at their 2019 price close the world's halved failed share? (pre-registered 2026-10-27)

**Written before either arm was launched.** It serves the BLOCKING crisis bad-debt finding
(`SEAT_FINDING_THE_CRISIS_BAD_DEBT_CONTROL_HAS_SKIPPED_SINCE_THE_RUN_WENT_GZIP_AND_THE_PUBLISHED_RUN_SHOWS_NO_STEP_UP_2026-10-14.md`,
section "2026-10-27: step (iii)"), which ranks first, as a hypothesis, that the world's 2020-21 halving
comes from its own budget arithmetic: the cap fell while the AWE factor rose.

## Arms

World-only, default book and dice, at `21f216076f` (origin/main), to 2022-03-31.
Harness: `/var/tmp/price_held/dump_price.py ARM 2022-03-31 OUT` (the leaver-trace `dump.py` body).

| Arm | What the household budget sees | Output |
|---|---|---|
| off (control) | the bill as posted | `/var/tmp/price_held/arm_off.json` |
| on | a credit bill due in 2020 or 2021, scaled by its fuel's Ofgem cap unit rate in the same month of 2019 over the rate in its own month (`simulation.price_cap_enforcement`) | `/var/tmp/price_held/arm_on.json` |

Only the budget's view of the bill moves. The company bills and posts the real amount, so the
denominator below is the same posted pounds in both arms.

## The measure

*Failed share* for year Y: pounds of bills issued in Y whose world record is `failed`, over all
pounds billed in Y. This is column A's "failed share of billed" in the finding. *The fall*: the
control's 2019 share less its pooled 2020-21 share. *Closed*: (on arm's pooled 2020-21 share less
the control's) over the fall.

## Prediction (the finding's, unchanged)

- **P1.** Closed is at least 0.50.
- **Refuted** if closed is below 0.25. Between 0.25 and 0.50 the price is a part, and not the ranked cause.
- **P2.** 2016-19 match exactly between the arms (the switch touches nothing before 2020).

## Read at real inputs, before the run

The factors the "on" arm applies, from the same cap function, calendar-year means:
electricity 2019 178.7, 2020 176.7, 2021 189.7 GBP/MWh (factor about 1.01 in 2020 and 0.94 in 2021);
gas 39.2, 34.2, 34.4 (about 1.15 and 1.14). So holding the price at 2019 raises a gas bill by about
15%, barely moves a 2020 electricity bill, and *lowers* a 2021 electricity bill. A halving from that
needs a strongly non-linear margin. The prediction stands as filed. This note is the reason to expect
it to be refuted, written before the answer.

## Graded (2026-10-27, 22:10Z): refuted. Closed is 0.07

Both arms finished (`settled 31987 scaled 8625` on the on arm). Grader: `/var/tmp/price_held/grade.py`.

| issue year | off (control) failed share | on (price held) |
|---|---|---|
| 2016-19 | 4.21%, 3.37%, 3.62%, 3.80% | identical |
| 2020 | 1.87% (GBP 3,974 / 212,253) | 1.89% |
| 2021 | 2.10% (GBP 4,435 / 211,072) | 2.34% |

- **P2 holds.** 2016-19 match to the penny.
- **P1 is refuted.** The fall is 1.81 points (2019 3.80% to pooled 2020-21 1.99%). Holding the price closes **0.071** of it, under the 0.25 line. The price is not the cause. The note filed before the run expected this.

The control's levels sit above column A's (2019 3.80% against 3.33%) because the code is ten days
newer. The halving is unchanged.

## What the control arm says about where the fall is (descriptive, one seed)

- **It is not the joiners.** About 42 accounts join each year from 2017 to 2021. The tenured book's share falls from 3.92% to 1.94%.
- **Fewer households fail, and those that do fail less.** Failing accounts go from 80 to 57 while billed accounts go from 334 to 301. Pounds per failing account go from GBP 119 to 70.
- **The same households stop failing, and they have not left.** Of 2019's 80 failing accounts, 62 are still billed in 2020, about the share earlier years kept. 22 fail again, against 28 the year before. Their failed pounds fall from GBP 7,129 to 2,468.
- **The margin side is also small at real inputs.** From 2019 to 2020 the AWE factor rises 1.5%, the basket 0.7% and housing (CPIH) 0.9%, and the full fall is already present in 2020. So the budget's own arithmetic is ranked down as a whole, not only its price leg.

**Next, ranked by this evidence:** something that lets households already in debt stop failing from
2020. The candidates are the household repayment plans (`_household_plans`: a plan's instalments
would replace failed bills) and the per-bill draw's income-stress input. The bounded step is to
split 2020's repeat failers' bills by whether a plan is active, on this control arm's code.
