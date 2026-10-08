**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The world loses 40% of households at each anniversary at the default price, against a published ~6% external switch at fixed-term end

*Found 2026-10-08 by the save-offer decision set (tools/grade_save_offer_shapes.py), built for the
director's ruling of the same day: "Confirm whether the world's own price response decides who is
saved, so that these numbers are a reality check on the world rather than an input, and check the
world against them."*

## What was measured

On the coin-drawn decision set (seeds 42, 101 and 202, about 22,000 renewal decisions each), the
world's own P(stay | the published default, ex VAT) averages **0.599**. So **40% of households leave
at each anniversary** when offered the default.

## What is published

The End of Fixed-Term Contract trial (Ofgem, n = 19,553 one-year fixes at one supplier) recorded
external switching of **about 6% in both arms** after term end, and 19-28% engaging in any way
(internal moves included). See docs/market_research/next_best_action_and_cross_sell.md and the
`3811342db` record. GB annual domestic switching runs about 15-20% of all accounts in normal years.

## Why it matters

Every retention result divides by, or is weighted by, the share leaving:
- The implied save rate is (P(stay|cut) - P(stay|default)) / (1 - P(stay|default)). If the leaving
  share were nearer 17%, the same GBP 7.5/MWh cut would imply about 0.07, ABOVE the published
  0-0.041 range rather than inside it.
- The blanket cut's loss is paid on the stayers. With fewer leavers, more of the cut is paid to
  households who were staying anyway.

So the shape ranking (reactive save first) is likely to SURVIVE a correction, but every level is
suspect until the departure base is checked.

## Three explanations to rank before changing anything

1. **The decision set's default price is the dear one.** Every renewal is offered the published
   default (SVT, capped) rather than the fixed tariff a real term-ender is offered. If the world's
   price response is steep at the cap's premium over the market, 40% could be right for a default
   offer and wrong for a renewal offer. **Test first:** re-ask P(stay) at a market fix.
2. **The decision set is thinner than the settled world:** electricity only, a flat day, neutral
   competitor and satisfaction. Compare its departure share with the settled run's at the same
   anniversaries.
3. **The world's departure hazard is too high.** If 1 and 2 do not close the gap, it is a fidelity
   defect in the churn draw, and it is fixed blind to company results.

NEXT for the seat: run 1 and 2 (minutes tier), then file the verdict beside this.
