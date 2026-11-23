**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-holdout-switch-on-is-pre-registered-before-its-book`

# Pre-registration: B8's blind retention holdout switched ON in the standing policy

*Delivery seat (executor worktree), 2026-11-23. This record is filed, and lands, before any book carries the
switch. The switch is `B8_BLIND_HOLDOUT_ON_IN_THE_STANDING_POLICY` in `company/policy/decision_policy.py`.
It is False in the same commit. `CURRENT_POLICY` reads it, and so does every arm built from
`CURRENT_POLICY` with `replace`.*

## What is being switched, and what is already established

- **The build.** 318d042e7e drew a blind coin over every renewal the retention desk *considers*, before
  the cut, the guard or either other coin. The share is `SAVE_HOLDOUT_SHARE`, 0.2716, derived by power
  in `competitive_pressure.save_holdout_share`, not picked. A held renewal loses the proactive approach
  only. Its re-fix tariff, its end-of-fix notice and the reactive save at a loss notice are unchanged.
- **Shown taken.** e2515972ea ran 2016-01 to 2017-12 with the switch on: 72 considered, 16 held (0.22),
  9 held stayers, 0 held approached.
- **Ruled.** The director said "Yes to holdbacks" (22 Nov, a87572556c).
- **What the published book carries.** `retention_holdout_by_desk_year["blind_approach"]["by_year"]`
  gives both arms' counts and the Newcombe interval per year. As of this commit the book also carries
  `retention_blind_holdout_log`: one row per considered renewal with `arm`, `would_offer` and
  `stayed_at_decision`. Before this commit the reducer dropped that log as `_NO_READER`, and P3 below
  needs its `would_offer` split. It publishes `None` while the switch is off.

**The base the predictions are taken from.** The newest published book is
`run_output_6a588a832f_20261120T134224Z.json`, produced 20 Nov, before the switch existed. "Considered" is
not logged with the switch off. The floor below is each year's offers (`retention_log`) plus the
no-offer leavers refused as `uneconomical` (`no_offer_churn_log`). Considered stayers who got no offer are
not logged, so it is a floor. In 2017 the floor is 67, against 72 measured in e2515972ea.

| year | offers | uneconomical leavers | considered (floor) | held at 0.272, exact 95% |
|---|---|---|---|---|
| 2016 | 0 | 0 | 0 | 0 |
| 2017 | 59 | 8 | 67 | 11–26 |
| 2018 | 11 | 2 | 13 | 1–7 |
| 2019 | 0 | 0 | 0 | 0 |
| 2020 | 0 | 0 | 0 | 0 |
| 2021 | 10 | 4 | 14 | 1–7 |
| 2022 | 0 | 0 | 0 | 0 |
| 2023 | 1 | 0 | 1 | 0–1 |
| 2024 | 1 | 0 | 1 | 0–1 |
| 2025 | 6 | 1 | 7 | 0–4 |
| **book** | **88** | **15** | **103** | **~28** |

The book will have moved since 20 Nov. Won switches are now supplied (f80fe3951), and the roster fix
(59cd5ebda) and the Market Stabilisation Charge (8a52399b89) have also landed. Each can change who renews.
The bands below are therefore wider than this table's sampling alone would give.

## The five things, as predictions on the first standing book that carries the flag ON

The book graded is the `CURRENT_POLICY` arm, 2016–2025. It is the first `docs/reports/run_output_<sha>_*.json`
whose producing commit has the flip commit as an ancestor.

### P1. Holdout count per renewal year, with an interval

- **P1a (property).** Pooled over the book, `held_out / (held_out + treated)` lies inside the exact
  binomial 95% interval of 0.2716 at the book's own considered count. The coin is a hash of the account
  and the roll date, read as fair.
- **P1b (count).** Considered renewals over the book are between 80 and 250. Held renewals are between
  18 and 75. The point prediction is about 30.
- **P1c (shape).** 2017 holds the most held renewals of any year: 11–30. At least three of the ten years
  hold fewer than 3, so a per-year interval exists in at most a handful of years.
- **Refuted by:** a pooled share outside P1a's interval, which would mean the coin is not blind or not
  at the share; or `blind_approach` absent from a book whose policy has the switch on.

### P2. The price sensitivity it lets the company discover, and its width at that count

What the holdout identifies is the intention-to-treat effect of the proactive approach on staying:
`stay_treated − stay_held`, with a Newcombe interval (`offer_effect_from_counts`). Dividing that by the
mean cut offered gives the company's own read of its price slope. That slope is today *told*, as
`churn_model.RATE_SENSITIVITY = 0.8`.

The earlier B8 records give these anchors.
- At 4,700 households a year (about 33,000 decisions per arm), the coin-drawn holdout recovers a true
  effect of +0.0115 per £7.5/MWh cut, with a 95% half-width of about 0.0075
  (`WORKER_RESULT_B8_..._COIN_DRAWN_HOLDOUT_2026-10-07.md`, size L).
- At 850 a year (about 6,000 per arm) the half-width is about 0.017, and the effect is undecided on two
  seeds of three (size S).
- The standing book's own §15 holdout read −0.038 (−0.25, +0.20) on 62 offered and 21 held. Through
  the repository's own function that is `offer_effect_from_counts(62,36,21,13)`.

Through the same function, at a stay share of 0.6 and the 0.2716 split, the half-width is:

| considered | held | half-width |
|---|---|---|
| 72 | 20 | 0.236 |
| 103 | 28 | 0.202 |
| 180 | 49 | 0.156 |
| 360 | 98 | 0.112 |
| 720 | 196 | 0.080 |

The prior's own implied effect is 0.8 × the mean cut. The mean cut on the 20 Nov book is 0.0435
(`retention_log.discount_pct`, 88 offers), so the implied effect is about +0.035. Resolving +0.035
at 5% two-sided with 80% power, at this split, takes about **7,800 considered renewals**. That is
roughly seventy standing books. Resolving the world's +0.0115 takes about 70,000.

- **P2a.** The pooled `blind_approach` verdict is `undecided`. Its interval covers 0 and covers +0.035,
  and its half-width is between 0.12 and 0.30.
- **P2b.** No single year's verdict is anything but `undecided` or `refused` (an empty arm).
- **P2c.** Restricted to `would_offer` rows, read from `retention_blind_holdout_log`, the verdict is also
  `undecided`, and the half-width is wider than P2a's.
- **P2d.** The implied slope (effect ÷ mean cut) has a half-width above 2.5, which is more than three
  times the 0.8 it would test.
- **Refuted by:** a pooled `raises_staying` or `lowers_staying`. Either would be a far larger effect
  than every earlier read, and the first thing to check would be the arms' composition, not the
  economics.

**What this says against the thesis (F11).** At this book size the company cannot discover its
customers' price sensitivity from its own renewals in one book, or in ten. At best the holdout can tell
the effect's sign. That is the Ascarza, Iyengar and Schleicher case (knowledge page §3.5): a treatment
with no held-out twin cannot sign its own effect. The method is proven at size L (M4). The *book* will
not carry the evidence until it holds thousands of considered renewals. The switch-on is worth making
because the instrument has to be running before the book is big enough to read it. It is not worth
making for a number this book will produce.

### P3. The renewal margin it costs on the held-out households

There are two sides, and they are published apart (M2). Everything here is read from the flagged book.
- **Held renewals the guard would have offered on.** P3a: between 10 and 60, about 0.27 of the book's
  would-offer renewals. On the 20 Nov base that is about 24 of 88.
- **Company, offer cost not spent.** That count × the treated arm's mean `retention_cost_gbp`. On the
  base this is 0.272 × £3,232 ≈ **£880**. P3b: between £400 and £2,500.
- **Company, margin lost to saves not made.** The held would-offer count × the treated-minus-held stay
  difference × the mean `expected_term_margin_gbp`. The 20 Nov base mean is £39 and the median is £2.80.
  P3c: the point is between −£100 and +£150. Even at P2c's interval top it is under £500.
- **P3d.** The company's net from the holdout is positive: cost not spent exceeds margin lost.
- **Household side.** The held households pay the re-fix without the cut they would have been offered,
  about £37 each, or about £880 in total on the base. **That is a transfer from them to the company,
  not value created.** It is the price of the information, and the held households pay it. It is
  published beside P3d, never netted into it.

### P4. Which of the five pending grades it would disturb if on in the same book

| grade (continuation id) | what it reads | disturbed? |
|---|---|---|
| ending-term belief (`read-the-ending-term-belief-grade-on-the-coming-book`) | the churn desk's belief against who left at the roll, by ending-term type (`desk_belief_log`) | **Yes, directly.** Held renewals lose the approach, so the stay rate at the roll moves under the belief being graded. |
| dual household answers (`grade-dual-household-answers-apart-on-the-first-book-carrying-c41e70832`) | `riding_leg_answers`: what each leg of a two-fuel household answered at its renewal | **Yes, directly.** The coin is keyed on the billing account and roll date, so both legs are held together, and the answers being graded are renewal answers. |
| won-switch P2–P5 (`grade-the-supplied-won-switches-on-the-first-book-after-f80fe3951`) | supply of won switches; P4 is `total_net` within ±£15k of £725,626 | **P4 only, slightly.** The holdout moves net by about +£1k (P3), inside the band, but it adds a second cause the P4 split would have to separate. P2, P3 and P5 are acquisition-side and are not touched. |
| KNIFE3 I1–I5 (`grade-knife3-i1-to-i5-...`) | `company_debt_recovery`: invoice refs, remittance lag, learned cells, sale decisions | **Weakly.** About 24 held households pay the re-fix without the cut, roughly £37 more each, so a few debts move. I1–I5 are ratios and windows over the whole debt book and should not shift. A second cause is still a second cause. |
| D48 (`d48-grade-the-first-book-descending-from-59cd5ebda-with-the-blend-at-0-5`) | the gas residual by shape provider, SPAR blend at 0.5 | **Composition only.** Who stays changes by a few households a year. Read and billed consumption per household do not change. |

**The rule this sets:** the flag flips only after all five have been graded on a book that does not carry
it. Two would be disturbed directly and three indirectly, and a book carrying two changes cannot
attribute either one.

### P5. The rule that turns it back off

The switch goes back to False in the next landing, with the reason in its commit, on any one of these:
1. **Regulation.** The Fixed Retention Tariff derogation's Directions ¶7 is read and requires the
   proactive retention offer to reach every existing customer at the end of a fix. Knowledge page
   §3.5 says ¶7 "was not read this pass". **It is read before the flip**, and the continuation that
   flips it is told so.
2. **The floor (M3).** Any held household appears in the book's comfort or health floor records
   (self-disconnection, a PSR breach, a debt-to-disconnection path) within its next term, where the
   treated twin it was drawn beside did not.
3. **The harm is learned.** The pooled `blind_approach` interval, or the `would_offer` one, reads
   `raises_staying` and the margin lost (P3c at the interval's low end) exceeds the offer cost not
   spent. The approach then demonstrably creates value, and holding it back destroys it. Turn the
   blind coin off and keep only the save-rate coin, which holds out only where the guard is unsure.
4. **The instrument is broken.** P1a is refuted. Or `blind_approach` is absent while the switch is on.
   Or any held row is in `retention_log`, meaning it was approached. Fail closed.

None of these is "the estimate is too wide". P2 predicts that it will be, and the instrument stays on
until the book is big enough. A width rule would turn it off forever.

## What lands with this record

- `B8_BLIND_HOLDOUT_ON_IN_THE_STANDING_POLICY = False`, read by `CURRENT_POLICY`. Tested: the flag is
  the standing policy's switch, and it is off. The tested mutations are flag on (2 red) and the flag
  replaced by a literal (1 red).
- `retention_blind_holdout_log` is forwarded to the published book, so P2c and P3 can be graded. It
  publishes `None` while the switch is off. If the forwarding line is deleted, 5 tests go red.
- One continuation, `b8-flip-the-blind-holdout-on-after-the-five-grades`, which reads this record
  after the five grades and flips the flag.

The prediction stands unread until a book carries the flag.
