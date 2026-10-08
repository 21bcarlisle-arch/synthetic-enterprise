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

## Predictions, written before tests 1 and 2 were run (worker, 2026-10-08)

Read before predicting: the world's market reference IS the published default
(`customer_events._price_differential_vs_market`), so an offer AT the default is differential 0
and the price term is skipped (`if differential:`), not neutral-by-construction. The year's level is
`departure_level_anchor.YEAR_LEVEL_ANCHOR`, a 2.0-20.8x hazard scale FITTED on a captured settled
run's factor population -- a population whose company price sits below the reference in ~74% of
renewals (that module's own note).

- **P1 (test 1).** Offered below the default, P(leave) falls, but no offer in the range a market
  fix could sit at (5-25% under the default) brings the decision set's pooled P(leave) to the
  settled world's level. Predicted pooled P(leave) at 20% under: 0.25-0.32.
- **P2 (test 2).** The settled run's per-renewal departure share at the same anniversaries sits
  inside the published annual band (~0.15), so the decision set runs ~2.5x the settled world.
- **P3 (attribution).** The gap is explanation 2, and specifically the anchor: it was fitted to make
  a cheaper-than-default book reach the record, so a household offered the default itself gets the
  anchor without the discount it was fitted against. If so, explanation 3 (the hazard is too high in
  the settled world) is NOT supported, and the 0.40 is a property of the decision set, not the world.

## Verdict (worker, 2026-10-08, at `fae73df3a`): explanation 3, and all three predictions refuted

**Test 1: no offer a market fix could make closes the gap.** The decision set was rebuilt (seeds 42,
101, 202 at 1,500 a year: 21,952 / 21,789 / 22,244 decisions) and the world was re-asked P(stay) at
the default and at 5-40% below it on every decision, with only the rate changed. Pooled P(leave):

| offer | seed 42 | seed 101 | seed 202 |
|---|---|---|---|
| the default | 0.399 | 0.403 | 0.400 |
| 10% under | 0.372 | 0.376 | 0.373 |
| 20% under | 0.352 | 0.356 | 0.353 |
| 40% under | 0.328 | 0.331 | 0.329 |

P1 (0.25-0.32 at 20% under) is **refuted**: price is a weaker lever than predicted. 57% of departures
at the default (seed 42: 4,973 of 8,793) fire on bill shock or dissatisfaction, which no price cut touches
(`departure_risks`: an offer scales the price-position hazard only). The price-position hazard is
not zero at parity either: at the default the differential is exactly 0 on every decision (the
reference IS the default), and price_position still names 3,820 of 8,793 departures on seed 42.

**Test 2: the settled world departs at the same rate, so the set is not the cause.**
`tools.measure_departure_level` on its committed capture gives the renewal route's E[depart]
per renewal decision. The decision set, all seeds pooled, beside it:

| year | 2017 | 2018 | 2019 | 2020 | 2021 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| settled run, renewal route | 35.0 | 28.6 | 43.3 | 42.7 | 44.7 | 56.9 | 67.8 |
| decision set at the default | 36.8 | 27.5 | 51.2 | 53.4 | 39.6 | 64.7 | 66.4 |
| decision set 40% under | 30.2 | 22.4 | 42.1 | 43.9 | 31.8 | 53.7 | 54.2 |

The 2017-2024 mean of the settled renewal route is **41.9%**, against the set's 0.40. P2 (~15%) is
**refuted**: the whole book (17-21% at 2017-2020) is in band, but the renewal route is not. P3
(explanation 2) is **refuted** with it. The set runs a few points high in 2019-2020 and 2024, which
fits the settled company pricing under the default, but its overall level is the world's.

**Explanation 3 is the one the evidence supports, and the mechanism is named in the code.**
`tools/fit_year_level_anchor.py::svt_composition_refusal`: *"the whole-book fit holds the SVT
contribution fixed and solves the renewal anchor around it."* So the renewal route's hazard is the
residual between the published total and the SVT route. That is why the anchor runs 2.0x-20.8x,
and no published term-end figure constrains it. On published figures alone it is outside the record:
at 2025, a fixed-term share of about one third (Ofgem SotM, Jan 2026) times 0.678 is 22.6% of
accounts against a published total of 10.4%. 2024 also exceeds the total. For 2019-2021, composing
EFTC's 6% external switching over six weeks with the default-tariff controls' 1-3% a month gives
roughly 17-39% a year, against the world's 43-45%. **One correction to this finding's own frame:**
the "published six" is a six-week window, not an anniversary's whole-year outcome. It is a floor,
not the comparator. The comparator the record supports is the bound above.

**Filed on W2** as
`WORKER_FINDING_THE_RENEWAL_ROUTE_CARRIES_THE_WHOLE_BOOK_RESIDUAL_AND_DEPARTS_ABOVE_THE_PUBLISHED_TERM_END_BOUND_2026-10-08.md`,
to be fixed blind to company results. The churn draw is untouched here.

**For the save-offer grade:** its implied save rates divide by a leaving share that is about 2x too
high in 2019-2021 and more at 2024-2025. The ranking (reactive save first) does not depend on the
level. The levels stay suspect until W2 re-fits.

Probe: `/tmp/anniv/probe.py` (not landed; it wraps `coin_drawn_decision_set.world_renewal` to keep
the full event and re-ask at percentage offers).
