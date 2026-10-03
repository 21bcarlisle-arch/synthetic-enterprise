# Pre-registration: which belief does the value rule's choosing lose on?

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `unminted`

Written 2026-10-03, before any oracle below was computed. The director asked whether seeing who
pays turns the choosing positive.

## What is already measured, and why it reframes the question

The payment-history fix (e0370bf94) is in the value rule the probe scores: arrears state, credit
risk and unpaid bills reach `decide_margin`, and arrears move the bad-debt cost as well as churn.
On the default book, full decade, 82 decisions:

- value - value_blind (the fix, rule against rule): **+147**, sd 70, SNR 2.1;
- value - level at value's own median, margin only: **-1,661**;
- the same, with true bad debt: **-2,668**.

So seeing who pays is already bought, and it is worth +147. Most of the choosing's loss (-1,661 of
-2,668) is there with no bad debt counted at all. The question becomes: is the loss in the
company's CHURN belief or its BAD-DEBT belief?

## The instrument: oracles over the recorded price grid

Every probed decision carries the world's true P(stay) and the household's true bad-debt share at
30 flat-at-level prices (5-150 GBP/MWh, cap and support clamps applied by the company's own chain).
Offline, at zero compute:

- **O_full:** at each decision, pick the grid price maximising true EV (true P(stay), true bad debt);
- **O_churn_only:** pick by true P(stay) x margin, blind to bad debt; scored with true bad debt;
- **O_debt_only:** price at the level median, except decline to discount (take the highest grid
  price) where the true bad-debt share exceeds the margin it earns;

each scored against the same level-at-median rule the value rule is graded against.

## Predictions

- **P1. Headroom exists.** O_full beats level-at-median by more than +5,000. The world rewards
  choosing; the value rule just isn't doing it.
- **P2. The churn belief is most of it.** O_churn_only recovers at least 70% of O_full's gain over
  level. Perfect payment knowledge on top of perfect churn knowledge (O_full - O_churn_only) is
  worth under 1,500.
- **P3. Payment knowledge alone cannot turn the choosing positive.** O_debt_only, which keeps the
  level rule's churn behaviour, beats level by under 1,000, against the 2,668 the value rule is
  down. So "seeing who pays" is not the lever; the company's churn belief is.
- **P4. Across the reference paths** (default plus roll seeds 61001-61003, as they land), the
  sign of every prediction above is the same on each path.

If P2 or P3 fails, payment knowledge matters more than this says, and the next build is the
bad-debt belief, not the churn belief. That gets written beside the result.

## Result (graded 2026-10-03, full decade, three reference paths so far)

Against level at each path's own value median (with true bad debt), total over the decade (sd):

| Path | decisions | value | O_full | O_churn_only | O_debt_only | value - value_blind |
|---|---|---|---|---|---|---|
| default | 82 | -2,668 (1,202) | +2,952 (491) | +2,175 (773) | +288 (241) | +147 (70) |
| roll 61001 | 80 | -3,046 (1,107) | +2,898 (442) | +2,235 (676) | +191 (188) | +213 (80) |
| roll 61002 | 78 | -2,146 (1,037) | +3,338 (553) | +2,620 (661) | +393 (319) | +291 (120) |

- **P1, REFUTED.** Headroom over level is about 3,000 (2,898-3,338), not more than 5,000. Even
  perfect knowledge, choosing one term at a time, is worth about 3k on this book.
- **P2, HELD on every path.** Churn knowledge alone recovers 74-78% of the headroom. Perfect
  payment knowledge on top of it adds 660-780.
- **P3, HELD on every path.** Payment knowledge alone is worth +191 to +393. The fix the
  director asked about is in, and it is worth +147 to +291 (SNR 2.1-2.7). Seeing who pays
  cannot turn the choosing positive.
- **P4, HELD on the three paths graded.** Every sign is the same on each. 61003 is still running.

**Where the churn belief goes wrong, measured.**
1. The company's belief about staying, at its own offer, against the world's: over the
   decade, mean +0.06 with sd 0.42 per decision (61002). It is barely informative per customer.
2. Price response. The company applies one slope to every household: +10% price, -0.08
   P(stay). The world's median is -0.036 (p10 -0.141, p90 -0.002). The typical customer is half
   as sensitive as the company thinks.
3. That spread is mostly NOT learnable (R1: elasticity is a hash of the id). But part of it IS:
   the world's slope differs by payment method, which a supplier observes. Median per +10%:
   prepayment -0.118, direct debit -0.038, standard credit -0.014.

**What calibration alone would buy (offline bound).** The level is held at the world's true
P(stay) at the level price, which a supplier would have to learn from its own renewals, so this
is an upper bound. Against level:

| Path | one correct population slope | slope keyed by payment method |
|---|---|---|
| default | +693 | +1,104 |
| 61001 | +367 | +878 |
| 61002 | +1,337 | +1,626 |

The value rule's -2,146 to -3,046 turns POSITIVE with a correctly calibrated churn belief. A
payment-method slope adds a further 300-500.

**Next build, decided by this:** a company-side churn belief calibrated from the company's OWN
observed renewal outcomes, with its price slope keyed by payment method. That is inference, never
access, and it is the lever this experiment found.
