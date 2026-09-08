# The level leg is available to the flat-rule supplier, so the composite headline states the thesis's claim over the wrong quantity

*2026-09-08. Delivery seat. This note takes a position and names what would refute it. It is
written to be disagreed with — the counter-argument is set out in full in §3 because it is a good
one, and §4 says why it does not rescue the composite headline.*

---

## 0. The question

`site/capabilities/index.html` published, as its headline, **£17,738.64** — `value_advantage_gbp`,
what the per-customer arm earned over flat rules. £17,468.44 of that is the price LEVEL and
£270.21 is the CHOOSING. The question this note settles: **is a level-only advantage something the
flat-rule baseline supplier could also have taken?** If it is, then a headline built on the sum
states the thesis's claim over a quantity that is 98.5% not the thesis.

**The position: yes, it could. The composite is the wrong headline quantity, and the page has been
changed accordingly.**

## 1. What the three arms actually are

From the published run `value_cycle_ab_s1_three_arm_20260908.json`, world `39a192ce04c1eda8`,
generated 2026-09-08T00:19:54Z:

| Arm | Policy | Net |
|---|---|---|
| Control | flat rules, margin £2.00/MWh | £140,140.54 |
| Level | **one flat margin, £54.25/MWh** | £157,608.98 |
| Value | per-household decisions | £157,879.18 |

- `level_advantage_gbp` = level − control = **£17,468.44**
- `selection_gbp` = value − level = **£270.21**
- `value_advantage_gbp` = value − control = **£17,738.64**

## 2. The argument

**The level arm is a flat-rule supplier.** That is not an interpretation of it; it is its
definition. Its entire policy is one scalar. It reads no household, holds no per-customer belief,
and makes no decision that differs between two accounts. Everything it earned over the control arm
was earned by a supplier of exactly the class the thesis says we beat.

So the level leg is not evidence about inference in either direction. It is a statement about the
**baseline**: the control arm's margin was set at £2.00/MWh and a margin of £54.25/MWh made
£17,468.44 more in the same world over the same book. That is a finding about how the baseline was
parameterised. Reading it as the return to deciding household by household is reading the gap
between two flat rules as the value of not using flat rules.

The mission is explicit that value is created and *then* shared, and that transfer is not creation.
A higher flat margin is a price charged. It moves value from the household to the company. The
feed says so itself in `level_leg.what_this_leg_is` — "this is value MOVED and not made" — and then
the page's own headline summed it with the choosing leg and called the total the advantage.

## 3. The counter-argument, and it is real

**The level arm's £54.25/MWh is set ex post from the value arm's own behaviour.** `tools/
generate_value_arms_data.py` is explicit: the level arm takes its level from *each run's own
realised median margin* (54.25, 48.5 and 20.0 £/MWh across the three runs on record). A flat-rule
supplier standing at the start of the book does not know that number. It is read off the
per-customer machinery after the fact.

On that reading, "the baseline supplier could have taken it too" is a claim granted the answer. The
per-customer arm *found* the level; the level arm merely re-charges it without the choosing. If
finding the level is the hard part, then the level leg is a product of the per-customer machinery
after all, and the composite headline is defensible.

## 4. Why the counter does not rescue the composite headline

The unknown is **one scalar over a bounded range**, and it is discoverable from a supplier's own
observables — margin in, volume and churn out — without knowing anything about any individual
household. That is a **search**, not an inference. The thesis's claim is specifically that the
advantage comes from *inference about individuals* and never from access or from pricing; a
one-dimensional search over the supplier's own book is available to the baseline supplier by the
definition of what a baseline supplier is. Nothing about it requires crossing the epistemic wall,
and nothing about it requires a per-household model.

Put the two side by side. To take the level leg, a supplier needs to try margins and keep the one
that pays. To take the selection leg, it needs a per-household model that is right often enough to
beat charging every household the same. Only the second is the thing this company is for.

**What the counter does establish, and it is a genuine limit on this note:** the search is not
free, and its cost is unmeasured here. Nothing in this repository has ever run a flat-rule supplier
that searches its own margin against the world — how many periods it takes, how much book it loses
finding the ceiling, whether it converges at all under the churn the world actually applies. So the
honest statement is: **the level leg is available in principle to a flat-rule supplier, and the
cost of acquiring it is unmeasured.** That is a gap, not a placeholder, and it is named as one here
rather than filled with an assumption that the search is instant or that it is impossible.

## 5. What follows for the page

`value_advantage_gbp` as a headline states the thesis's claim over the wrong quantity. The thesis's
own quantity is `selection_gbp`, and it reads as follows:

- Published draw: **£270.21**
- Three seed re-draws in the same world, same book, same code: **+£1,199.55, −£3,075.22, +£433.07**
- Centre of that family: **−£480.86**. One of the three clears its bound; two do not.

**The quantity the thesis is about cannot currently be told from zero, and its own family centres
below zero.** The feed already computes exactly this and states it in
`current_world.selection_leg.verdict_withheld_because` — "whether this page could state a direction
depends on which draw the run happened to make. It states none." Until 2026-09-08 that sentence was
computed on every publish and **rendered nowhere on the site**: the band table collected the field
into its row objects and never printed it.

So the page now leads with the two legs, each with its own verdict, and states the sum after them —
`#arms-legs-first` in `site/capabilities/index.html`, controlled by
`site/test_the_split_is_the_headline_and_the_selection_legs_refusal_reaches_the_reader.py`.

## 6. What this note does not say

It does not say £17,468.44 is fake money. It is real net that the world actually paid. It says the
leg is value moved rather than made, that any flat-rule supplier could have moved it, and that
attributing it to per-customer inference is the error.

It also does not say the selection leg is zero. It says the selection leg is **unread**: n=3 is
three draws, and three draws of a quantity whose spread is £2,279 do not settle a £270 figure in
either direction. A larger re-draw family is what would settle it, and that is a run, not an
argument.

## 7. What would refute this note

1. **A flat-rule supplier that searches and fails.** Run a baseline arm that adjusts its single
   margin from its own observed volume and churn, and show it does not reach the neighbourhood of
   the value arm's realised median within the book's life. That would make the level a genuine
   product of the per-customer machinery and the composite headline correct after all. This is the
   strongest refutation available and it is a measurement, not a position.
2. **A demonstration that the realised median is not reachable except per-household** — that the
   value arm's level is an emergent property of many different per-household prices and is not a
   scalar any single-margin supplier could hold. If true, §4's "one scalar over a bounded range" is
   the wrong description of the search space.
3. **A selection leg that resolves positive on a larger family.** That would not refute §2 — the
   level leg would still be value moved — but it would make the composite headline's error much
   smaller in practice, because the thesis's own quantity would then be a number the page could
   state.

Filed before any of the three was run.
