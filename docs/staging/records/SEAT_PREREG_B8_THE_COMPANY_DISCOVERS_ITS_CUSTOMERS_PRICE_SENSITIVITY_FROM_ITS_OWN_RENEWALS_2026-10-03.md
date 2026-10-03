# Pre-registration: B8, the company discovers price sensitivity from its own renewals

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

Written 2026-10-03, before any of the mechanism below exists.

## Why this, now

The per-decision probe found the value rule's choosing loses about 2,100-3,050 against a flat
price at its own median, on four reference paths, and that the loss is the CHURN belief, not the
payment view (`SEAT_PREREG_WHICH_BELIEF_THE_CHOOSING_LOSES_ON_2026-10-03.md`). The company prices
with one fixed price slope, `churn_model.RATE_SENSITIVITY = 0.8` (+10% price -> +0.08 churn), for
every household. The world's median response is 0.036 per +10% and differs by payment method, which
a supplier observes: prepayment 0.118, direct debit 0.038, standard credit 0.014. An offline bound
put a calibrated belief at +367 to +1,626 against level.

PB7 already lets the company learn two LEVEL scalers (market pressure, payment-method engagement)
from its own closed renewals (`company/crm/competitive_pressure.py`). The SLOPE is the one term no
mechanism learns. B8 is the atom for it, level 0.

## The mechanism (to be built)

`company/pricing/discovered_price_sensitivity.py`: a ledger of the company's OWN closed renewals.
For each one it holds the payment method, the household's own price move against the published
default, and whether it stayed. From these it gives a posterior price slope per payment method:
the company's current 0.8 as the prior, its own renewals as the likelihood, precision-weighted with
PB7's machinery. Strictly no look-ahead: a renewal enters only once its outcome is known. Behind a
policy switch, so the control and level arms read the unchanged 0.8.

## Predictions (falsifiable, and some are written to fail if the evidence is too thin)

- **B1. It learns in the right direction.** By the end of 2025, the posterior slope for direct
  debit is below the 0.8 prior, and the posterior for prepayment is above direct debit's.
- **B2. It does not learn enough.** Posterior uncertainty stays wide: the standard credit and
  prepayment slopes rest on about ten renewals each, so their posteriors stay within half the
  distance between the prior and the world's median. A book this size is a slow teacher.
- **B3. The choosing improves, but does not reach the bound.** On the probe, `value_learned` beats
  `value` against level by at least +500 on every reference path, and stays below the calibrated
  bound (+367 to +1,626 above level).
- **B4. Nothing leaks into the control.** The control arm's renewal outcomes are byte-identical
  with the switch on and off.

If B1 fails, the company's own renewals carry no slope signal at this book size, and that is the
finding, not a reason to loosen the prior. If B3 is positive on some paths and negative on others,
the book is too small to learn a slope from, which would answer the director's width question from
a different side.

## Amendment, written before any code (2026-10-03): the company must VARY its price to learn

Writing the mechanism down exposed an identification problem. A slope is learned from how outcomes
change as the company's OWN price move varies. Under the flat rule, that move is the market's
move, so the company never prices one household differently from another relative to the market.
Its renewals then carry almost no slope information, however many there are. Real suppliers learn
price sensitivity by running PRICE TESTS: a random share of renewals is offered a deliberately
different margin, and outcomes are compared. That is B8's own real-world twin ("the honest ones
run a holdout").

So B8 gains an EXPLORATION leg: a deterministic, per-account assignment (hash of the account and
term, so a re-run assigns the same test) offers a small share of renewals a margin shifted up or
down by a fixed step. Those test renewals feed the slope posterior. The test is a company decision
and costs margin, and that cost is scored too.

- **B0 (new, and the one most likely to decide the design).** With NO exploration (the ledger fed
  only the reference path's ordinary renewals), the posterior slope moves less than 0.05 from the
  0.8 prior on every payment method by 2025. The flat rule teaches nothing about price response.
- **B5 (new).** With exploration, the exploration's own margin cost over the decade is smaller than
  the improvement it buys in B3. If it is not, a price test does not pay at this book size, and the
  company should not run one.

## Result (graded 2026-10-03, default book, full decade, no exploration)

Built as designed, plus one defect found on the way: `decide_margin`'s scorer never passed
`payment_method` into `enriched_churn_estimate`. Pricing therefore ignored PB7's engagement factor,
and B8's correction with it, while the churn desk applied both. Fixed in the same landing. The
first smoke run showed the learned belief moving and the price not moving on any of 76 decisions,
and that is how the defect was found.

| | total | sd | SNR |
|---|---|---|---|
| value_learned - value | +18 | 16 | 1.1 |
| value - level at its median | -2,651 | 1,196 | 2.2 |
| value_learned - level | -2,633 | 1,195 | 2.2 |
| value - value_blind (payment history) | +164 | 71 | 2.3 |

The learned rule changes the offer on 15 of 82 decisions. The learned correction (electricity,
last value seen each year) is 0 to 2019, +0.44 (2020), -0.25 (2021), -0.77 (2024), -0.64 (2025).
Gas never accumulates evidence.

- **B0, REFUTED.** Without a price test the correction still moves by up to -0.77: the cap's own
  lagged schedule varies the company's price against the default, so the flat path is an
  accidental price test. The B0 information measure (slope SE 0.28 against a 0.44 gap) predicted
  this, and the pre-registered prediction did not.
- **B1, HELD for direction, ungraded for ordering.** The correction turns negative: the company
  learns its customers are LESS price-sensitive than its 0.8 says, which is the world's truth. The
  rows do not carry the payment method, so whether prepayment learns steeper than direct debit is
  not graded here.
- **B2, REFUTED.** The correction moved further than half the prior-to-truth gap (0.22). At -0.64
  to -0.77 it may OVERSHOOT. The prior spread (`PRIOR_DELTA_SD`, a declared belief) is loose
  enough to let a thin late window swing hard. Tightening it is the obvious knob, and is NOT turned
  here, because choosing it against this result would be fitting the prior to the answer.
- **B3, REFUTED.** +18, not at least +500. The learner only sees renewals with a published default
  to measure against, and the cap begins in 2019, so learning starts with 2020's renewals and moves
  15 decisions. It is too late and too few to change a decade.
- **B4, HELD** in the controls (control == value under any ledger), and the value arm's numbers
  barely move with the scorer fix (-2,668 to -2,651).
- **B5, not applicable**: no exploration was built (B0's SE was under the gap).

**What this says.** The mechanism works and learns the right direction. Its window is the binding
constraint, not its maths. The bound said a calibrated belief could make the choosing +367 to
+1,337 against level. Closing that gap needs one of:
1. a reference the company can measure its move against BEFORE 2019 (its own previous price, or the
   market reference it already prices against);
2. calibrating the belief's LEVEL as well as its slope (the bound held the level at truth);
3. a deliberate price test to learn faster.
Next: (1), because it lengthens the window at no cost, then re-grade B3.

## Step 2, pre-registered before its decade run (2026-10-03)

**Change.** One definition of the company's own move, used by both the desk's booking and the
pricing correction (`own_move`):
- a household with a published default: the offer's gap to it;
- everything else: the household's own price change net of the market's move as the company reads
  it. That is every renewal before 2019, and every business account at any date.
Learning can therefore start in 2017, and the business-account mismatch (learned against the
domestic cap, priced by the fallback) is closed.

**Predictions.**
- **B3' (the step's purpose).** With learning from 2017, `value_learned - value` on the default book
  over the decade is at least +300, against step 1's +18.
- **B6.** The learned rule changes more than 30 of the 82 offers (step 1: 15).
- **B7 (written to fail if the fallback is the wrong measure).** The correction learned by 2019 has
  the same sign as step 1's late-window correction: negative, the company's customers are less
  price-sensitive than 0.8 says. If it is positive, the pre-cap move measures something else and
  the fallback should not be trusted.

## Step 2 result (graded 2026-10-03, default book, full decade)

| | total | sd | SNR |
|---|---|---|---|
| value_learned - value | **-37** | 77 | 0.5 |
| value - level | -2,651 | 1,196 | 2.2 |
| value_learned - level | -2,688 | 1,194 | 2.3 |

The learned rule changes 29 of 82 offers. Electricity correction by year: 0 (2016-17); -0.02 to +0.28
(2018); -0.11 to -0.25 (2019); -0.23 to -0.74 (2020); -0.16 to -0.70 (2024-25). Gas -0.38 by 2019.

- **B7, HELD.** Learning from the pre-cap fallback points the same way as the post-cap window, so
  the fallback measures the same thing.
- **B6, REFUTED narrowly**: 29 offers, not more than 30.
- **B3', REFUTED, with the sign reversed**: -37, not at least +300.

**Why, and what it changes.** Learning the slope earlier made pricing slightly WORSE, and the
level sweep already in the record says why. The value rule already over-charges: its median margin
is 51 GBP/MWh, and it beats a uniform level only below about 30. Learning that customers are LESS
sensitive than 0.8 moves its price UP, the wrong way, even though the slope learned is the
world's direction. The offline bound that promised +367 to +1,337 held the belief's LEVEL (P(stay)
at the level price) at the world's truth. The company's level error is large (believed minus true
P(stay): sd 0.42 per decision), so correcting the slope while the level stays wrong pushes the
price the wrong way. **The next target is the LEVEL of the churn belief, not its slope.** Step 2's
mechanism still lands: it closes a real learn/use mismatch, and the learned policy stays opt-in, so
no default run moves.
