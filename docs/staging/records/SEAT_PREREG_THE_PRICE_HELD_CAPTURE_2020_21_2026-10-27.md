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
