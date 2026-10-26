**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted`

# The value test's published draws fall outside their own re-draws, and the level leg's on the other side of zero

Raised by the advisor's chase of 26 Oct, 19:30 (`docs/staging/advisor/ADVISOR_CHASE_THE_EXPLORE_EXAMPLES_ARE_STILL_LIVE_FOR_TOMORROW_2026-10-26.md`, item 3).

Read from `site/data/value_arms.json` (current world, run of 8 Oct 2026).

## What it shows

| Leg | This run's own draw | Its 3 re-draws | Re-draw mean |
|---|---|---|---|
| Selection | +£11,345 | +£4,722 to +£7,846 | +£6,765 |
| Level | −£6,101 | +£1,649 to +£4,975 | +£3,514 |

- The selection draw is **above** every re-draw.
- The level draw is **below** every re-draw, and on the other side of zero from all three.

## What a re-draw is

Per `tools/generate_value_arms_data.py` `_verdict_stability`:

- The headline is `value_advantage_gbp` from the three-arm run's single elasticity draw.
- The re-draws are the floor's seed rows of the same contrast.

If those really are the same quantity, then one draw out of four lying outside the other three on
both legs, and on the opposite sign for the level leg, is unlikely. It points instead at the run and
the floor measuring something different. The candidates are a different book, a different horizon,
or a different elasticity construction. **Which of these it is cannot yet be said.**

**Prediction, filed before measuring:** the three-arm run and the floor differ in book or horizon,
not only in seed.

## What changed on the page tonight

The Capabilities lead now leads with the range of the re-draws. It then gives this run's own draw and
says where that draw fell. It offers no reason for the gap, because the feed carries none. The lead
says the level leg's sign is not settled, and the phrase "value moved, not made" now describes what
the level leg is, rather than standing as a verdict.

## What closes it

1. Establish whether the headline and the floor's seeds are the same contrast on the same book and
   horizon.
2. If they are, re-draw the published arm itself as a fourth seed.
3. If they are not, the headline's spread is the wrong spread, and the page should publish the family
   it actually belongs to.
