# The choice is held down by a too-steep belief, so learn the slope under the default

**Pre-registered 2026-10-03 by the delivery seat, before any run of the change below.**

## What the belief curves show

Source: `/var/tmp/se-probe-out/probe_bel_{default,61001}.json`. These are the first probe runs to
record the company's believed P(stay) beside the world's at every level-grid offer (ac465ac38).

Belief / truth, mean over decisions, by renewal year (default path; 61001 agrees to within a few
points):

| year | n | margin 10 | margin 30 | margin 55 |
|---|---|---|---|---|
| 2017 | 24 | 0.72 / 0.76 | 0.49 / 0.70 | 0.35 / 0.62 |
| 2018 | 16 | 0.50 / 0.71 | 0.30 / 0.66 | 0.19 / 0.57 |
| 2019 | 12 | 0.95 / 0.66 | 0.87 / 0.61 | 0.71 / 0.49 |
| 2020 | 12 | 0.94 / 0.37 | 0.94 / 0.31 | 0.90 / 0.18 |
| 2021 | 9 | 0.78 / 0.33 | 0.64 / 0.28 | 0.51 / 0.22 |

Pooled drop in P(stay) from margin 10 to margin 55: **believed 0.259, true 0.155** (default path;
0.262 / 0.160 on 61001).

**Two different errors.**

1. **LEVEL, by regime.**
   - **Before the cap** the belief is too pessimistic. It prices the move from the old rate, and a
     first renewal moves +45-75% off the acquisition rate.
   - **From 2019** it reads the offer's gap to the default. An offer under the default reads as
     almost no reason to leave, so the belief sits at 0.9+ while the world keeps 0.2-0.7.
2. **SLOPE.** Pooled, the belief is about 1.7x too steep: the company thinks its customers are far
   more price-sensitive than they are.

**Why the slope, not the level, holds the price down.** A level error that scales P(stay) the
same at every candidate leaves the argmax where it is. A too-steep slope moves the argmax down.
That matches the stayer-pays grading (`..._STAYER_PAYS_THE_DEFAULT_...`):
- the capped rule chooses a median margin of GBP 18-26;
- the best flat level in hindsight is GBP 55-60.

B8 (`discovered_price_sensitivity`) learns exactly this flatter slope from the company's own
closed renewals. It was refuted earlier today (-37) because the value rule was then pricing above
the default, so learning "less sensitive" pushed already-dominated offers higher. Under the
default, that reason is gone.

## The change

No new mechanism. `VALUE_ARM_CAPPED_LEARNED_POLICY` sets both existing switches:
- `renewal_stayer_pays_at_most_default`;
- `learn_price_response`.

The probe scores it as rule `value_capped_learned`.

## Predictions, written before the run

On the four 2025 paths (default, 61001, 61002, 61003):

- **L1.** value_capped_learned's median chosen margin is higher than value_capped's on every path,
  by at least GBP 5/MWh.
- **L2.** value_capped_learned - value_capped > 0 on at least 3 of 4 paths.
- **L3.** value_capped_learned - (the best flat level in hindsight) is less negative than
  value_capped - (the same level) on at least 3 of 4 paths.
- **L4 (the bar that matters).** value_capped_learned beats a flat level chosen IN ADVANCE on at
  least 3 of 4 paths. The level is the company's flat target margin
  (`TARGET_MARGIN_GBP_PER_MWH`), i.e. the 'flat' rule, scored on what the world bills. I expect
  this to hold, because capped already beats flat by 4.7-6.4k.

  L4 is weak. The stronger in-advance bar is a level fixed before 2016 from published margins, and
  none is established in the knowledge layer. So the honest strong bar remains "beats the best
  level in hindsight", which **I predict is NOT reached (L3 only narrows the gap).**

## Grading

Filled in below after the runs.

## Grading, all four paths

Source: `/var/tmp/se-probe-out/probe_cl_*.json`, run at c822e470e. Every figure includes bad
debt and is scored on what the world bills.

| path | offers changed | median margin capped -> learned | learned - capped (SNR) | best flat level | capped - best | learned - best | learned - flat |
|---|---|---|---|---|---|---|---|
| default | 21 / 83 | 16.3 -> 20.0 | -44 (1.83) | 55 | -773 | -817 | +4,668 |
| 61001 | 17 / 80 | 15.2 -> 17.4 | -37 (1.16) | 55 | -1,079 | -1,116 | +6,248 |
| 61002 | 10 / 78 | 16.7 -> 15.2 | -21 (1.88) | 55 | -992 | -1,013 | +4,964 |
| 61003 | 18 / 77 | 23.7 -> 24.7 | -53 (2.06) | 55 | -1,093 | -1,146 | +5,746 |

- **L1: REFUTED on 4 of 4.** The median moved -1.5 to +3.7, never +5.
- **L2: REFUTED on 4 of 4.** learned - capped is -21 to -53, consistently small and negative.
- **L3: REFUTED on 4 of 4.** The gap to the best flat level widened slightly.
- **L4: HELD on 4 of 4.** Learned beats the flat rule by 4.7-6.2k. As registered, this is a weak
  bar: the flat rule's GBP 2 target margin loses money after bad debt on every path.

**My diagnosis was wrong in its mechanism, and I say so beside it.** The slope is learned:
- the delta is about -0.43 to -0.66 from 2019, against a base slope of 0.8;
- it is 0 in 2017, when there are no closed years, and +0.13 in 2018.

Learning it moves almost nothing, for two reasons:
- **From 2019** most offers already sit at the default, which binds before the slope matters.
- **Before 2019**, where the belief IS too steep, there is no evidence yet to learn from.

## What actually holds the rule below the best flat level: one account

Split by year, capped - flat-55 is within +/-175 of zero in every year except 2017. 2017 alone is
about -1,160 to -1,200 on each path, and nearly all of it is **one decision: PROS-2016-0098 on
2017-03-31.**
- Its true bad-debt share is 0.505-0.565, on 27.6 MWh.
- The capped rule prices it at the default and keeps it (P(stay) 0.72).
- The flat-55 offer happens to drive it away (0.10).

| path | capped - flat-55, all | without PROS-2016-0098 (SNR) | that account |
|---|---|---|---|
| default | -773 | +298 (1.40) | -1,072 |
| 61001 | -1,079 | -120 (0.30) | -959 |
| 61002 | -992 | -32 (0.17) | -961 |
| 61003 | -1,093 | -131 (0.32) | -962 |

**Without that one household, per-decision choosing with the default known is at parity with the
best flat price in hindsight.** The best flat price is itself chosen on the same decisions, and
the parity is reached without hindsight.

**The remaining loss is a world gap, not a choosing failure.** Under SLC 14 a real supplier may
object to an indebted domestic credit customer's switch, and Ofgem's 2016 review puts the blocked
share at about 28-30%. The world lets this debtor leave freely. So a high flat price is rewarded
for driving away a customer a real supplier could have kept liable for the debt.
- `SEAT_FINDING_THE_WORLD_LETS_A_DEBTOR_SWITCH_AWAY_BECAUSE_THE_DOMESTIC_DEBT_OBJECTION_IS_UNMODELLED_2026-10-03.md`
  was filed earlier the same day on the law alone.
- The world-side objection draw is being built on the published rate.

That draw is the next re-run of this comparison. Prediction, written now: with the objection on,
capped - flat-55 moves toward zero on all four paths, but the debtor still leaves in about 70% of
draws, so the account's cost shrinks rather than vanishes.

## Grading the debt-objection prediction (2026-10-04)

The prediction was that, with the world's debt objection on (bf0d37c2f), capped - flat-55 moves
toward zero on all four paths, while the debtor still leaves in ~70% of draws. Probe runs
`/var/tmp/se-probe-out/probe_obj_*.json`, at origin with bf0d37c2f. The objection's REACH is an
upper bound here: the world's payment records never cure a failed bill, so 56% of renewal
decisions are "eligible". A cure is being built.

*Correction, 2026-10-04: `bf0d37c2f` predates `ba320e2d2` (the `own_book` default and the channel-blind clean price), and the probe reaches both. So this table grades the pre-flip company, and a post-flip re-run is owed. See `../SEAT_NOTE_FOR_THE_CONSOLE_SEAT_THE_OBJECTION_PROBES_GRADED_THE_PRE_FLIP_COMPANY_2026-10-04.md`.*

| path | capped - flat-55, objection off | on | without PROS-2016-0098, off -> on | PROS 2017-03-31 P(stay) at flat-55, off -> on |
|---|---|---|---|---|
| default | -773 | -779 | +298 -> +292 | 0.10 -> 0.10 |
| 61001 | -1,079 | -1,098 | -120 -> -139 | 0.10 -> 0.10 |
| 61002 | -992 | -1,089 | -32 -> +7 | 0.10 -> 0.10 |
| 61003 | -1,093 | **-165** | -131 -> +82 | 0.10 -> **0.41** |

**REFUTED on 3 of 4; held on 61003.**

The objection does not reach the decisive decision on three paths. At 2017-03-31 PROS-2016-0098
has no bill more than 28 days unpaid in the world's own records, so it is not an eligible debtor.
On 61003, the re-drawn renewal dice put an older unpaid bill in front of the date, the block
applies, and the gap almost closes. The 2021 renewal is reached on every path (0.03 -> 0.31),
but it carries little value.

**What the company could see.** The company's OWN ledger, read through the new collections
journey (`result["collections_journeys"]`, run to 2017-03-31): ACC-PROS-2016-0098 had one missed
payment, GBP 486.84 on 2016-11-29, cured on 2016-12-10, and nothing open at the decision. To any
supplier this account was a customer with one late payment, since cleared. The arrears that later
make it the worst account in the book had not happened.

**So the flat-55 win on this household is luck, not knowledge.** A price that happened to be high
drove away a customer whose future debt no rule could have priced at the time. This is the
director's fairness point about book-level comparisons, showing up inside the per-decision
probe: the probe holds the book fixed, but `true_bad_debt_share` is a LIFETIME truth, and scoring
one decision with it charges that decision for debt that accrues years later.

**What this means for the selection question.** With the default known, per-decision choosing is
at parity with the best flat price in hindsight on every decision except one that the flat price
won by luck on unforeseeable future debt. That is as close to "the choosing works" as this
instrument can show without a second book.

**The instrument's defect is now named.** Scoring a decision with a lifetime bad-debt share lets
debt that accrues after the next renewal count against this one. The fair score charges each
decision only the bad debt of the term it priced. That is the next probe change, and it is
recorded here before any run.
