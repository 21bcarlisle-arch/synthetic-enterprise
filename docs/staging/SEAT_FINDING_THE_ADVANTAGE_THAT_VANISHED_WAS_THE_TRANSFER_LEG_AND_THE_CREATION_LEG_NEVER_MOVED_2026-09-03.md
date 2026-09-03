**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The advantage that vanished was the transfer leg, and the creation leg never moved

**Class:** `figures_on_a_superseded_clock` (primary)

*Delivery seat, 2026-09-03, claim `the-baseline-was-beaten-in-a-world-that-no-longer-exists`.
Measured from `value_cycle_ab_s1_three_arm_20260903.json` (world `39a192ce04c1eda8`) against
`value_cycle_ab_s1_three_arm.json` (2026-08-31). The three floor legs re-running the bound are still
in flight, so nothing here states whether a figure is resolved — that is the floor's to say.*

---

## What happened

The published headline under `/capabilities/` is that the per-customer arm earned **£12,071 more than
flat rules**. Re-run on the live world — the departure-level anchor re-fitted twice since — the same
comparison returns **£2,336**, a fall of 80.65%.

The interesting part is not the fall. It is **which leg fell**.

| leg | old, 2026-08-31 | new, 2026-09-03 | move |
|---|---|---|---|
| `level_advantage_gbp` — what a flat rule at the same PRICE LEVEL earns | 9,496.70 | **159.21** | **−98.32%** |
| `selection_gbp` — what per-customer CHOOSING earns on top | 2,574.37 | 2,176.66 | −15.45% |
| `value_advantage_gbp` — the published headline, their sum | 12,071.08 | 2,335.87 | −80.65% |
| `level_share_of_advantage` | 78.67% | 6.82% | |

**The level leg is 98% gone. The selection leg did not detectably move** — £397 on a figure whose own
seed spread was ±£3,776 is not a movement this instrument can see at all.

## Why this matters beyond the number

The mission's first consequence is that *"value is created and THEN shared, so every decision has two
sides. Transfer is not creation. Charging someone the cap moves value without making any."*

The level leg **is** the transfer side, by construction: it is what a flat rule earns by sitting at
the same £/MWh the per-customer arm reached, with no per-customer view at all. The selection leg is
the only candidate for creation in this comparison — the part attributable to choosing differently
household by household.

So the re-run says something sharper than "the advantage shrank":

> **Four fifths of the published advantage was the price level, and the price level stops paying the
> moment the world lets customers respond to it. What survives is the selection leg, which is the
> part that could be value creation, and it is the same size it always was and still inside its own
> noise floor.**

The old page already said 79% of the advantage was the level. What it could not say — because it was
measured in a world with a softer departure response — is that the 79% was **contingent on customers
not leaving over it**. `level_gbp_per_mwh` fell 54.25 → 48.25 across the two worlds: in the harder
world the arm cannot hold the premium, and the flat rule that merely copies the premium earns £159
instead of £9,497.

## The mechanism, and the denominator that misled the prediction

The pre-registration (`SEAT_PREREGISTRATION_WHAT_THE_ARMS_RERUN_ON_THE_LIVE_WORLD_MUST_MOVE_2026-09-03.md`,
§2 P2) predicted the advantage would GROW, reasoning that a book shedding 14.6% more households
offers more renewals for the arm to win. Departures did rise, and renewals offered rose with them:

| | old | new | move |
|---|---|---|---|
| renewals the world offered (value arm) | 1,953 | 2,009 | **+2.87%** |
| renewals the arm actually **priced** | 120 | **104** | **−13.33%** |
| priced share of renewals offered | 6.14% | 5.18% | |

**Renewals offered rose; priced decisions fell.** The advantage is earned on priced decisions, not on
renewals offered, and the two moved in opposite directions. The prediction differenced the wrong
denominator — the same shape CLAUDE.md names as this project's most expensive recurring failure
(*"before dividing two numbers, say out loud what each one counts"*), this time inside a prediction
rather than a published figure.

Worth keeping beside it: §1 of that pre-registration **correctly** refuted the draw's premise (the
world got harder, not easier, +2.049pp, expected departures +14.6%), and the very next inference from
that correct measurement was still wrong. A correct measurement does not make the next step from it
correct.

## What is NOT claimed here

**Whether £2,336 is distinguishable from zero is not stated, and must not be, until the floor legs
land.** £2,336 against the old bound's ±£2,291 is 1.02×, where £12,071 was 5.27× — but that ratio
prices a new world's figure against an old world's bound, which is precisely the defect `c30b98048`
was filed for on 2026-08-31 and precisely what this work exists to stop repeating. The three legs
(`se-noise-floor-20260903`, `se-floor-only-20260903`, `se-floor-except-20260903`) were started
10:18/10:23Z and answer it.

The honest reading available today is the composition, not the resolution: the leg that collapsed is
the one that was never creating value, and the leg that might be was never resolvable.

## What follows

1. **Publish nothing from the new world until its own floor is in.** The page currently carries the
   whole OLD world plus a `world_provenance` caveat saying so, which is the correct interim state —
   stale-and-labelled, not mixed. Do not half-update it.
2. **When the floor lands, the page's claim needs rewriting, not just re-numbering.** "We beat flat
   rules by £12,071" cannot become "we beat flat rules by £2,336"; the finding is that the beat was
   mostly a price level that a responsive world does not pay. The headline should carry the
   composition.
3. **The level leg deserves its own standing question.** A comparison whose advantage is 79% price
   level in one world and 7% in another is measuring the world's price-response calibration at least
   as much as it is measuring the company. That is worth saying on the page.
