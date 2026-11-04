**Severity:** LATENT · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

**Knowledge:** none -- an audit of the Knowledge pages' own labels; what it finds lands as each page's facet record in site/data/knowledge_facets.json

# The knowledge facet audit: every served page classed as knowledge or insight, with its trust and its readers (2026-11-04)

This is the audit the director asked for on 4 Nov: "I saw a knowledge article that seemed to be internal insight not
external knowledge... Insight might not be right." The records are in `site/data/knowledge_facets.json`, using the schema
in `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §7. `site/knowledge/test_every_page_carries_its_five_facets.py` passes
on all 63 pages (65 passed). No page body was changed.

## Counts (denominator 63 served pages)

| Facet | Values |
|---|---|
| Domain | market_and_regulation 14 · household_and_assets 14 · supplier_operations 13 · customer_needs_and_behaviour 7 · products_measures_services 7 · other_markets 8 |
| Layer | knowledge 36 · mixed 23 · insight 4 |
| Side | both 30 · world 16 · supplier 9 · neither 8 |
| Grade floor | P 18 · D 7 · S 26 · A 12 |
| Verified | yes 11 · partly 43 · no 9 |

There are 55 insight rows: hypothesis 23, tested 15, held 11, refuted 4, contested 2. Six of them come from the simulation (`from_sim: true`).

Placement follows §2.1 exactly. The one page it does not place is `the-customer-needs-framework`, written on 2 Nov, after
§2.1's census of 62 pages. It goes under customer needs, as §4 row 3 says.

## Pages presented as knowledge that are really insight or mixed (27)

All 27 carry the banner "Public-reality commons only" or "commons and method", or have no label at all.

**The page the director most likely saw: `the-customer-needs-framework`.** It was written on 2 Nov and is served as
Knowledge. Its cross-tabs are knowledge, graded D from Ofgem's CIM tables. But the page is built around our own framework,
the six needs of M3, and it tests the advisor's predictions against that framework. The nine notes that declare this page
are where every example in his steer comes from: "age outweighs income", "price sensitivity is two traits" and precarity
as a factor. The page now carries 9 insight rows. Four are refuted (worry peaks at 35-54; income is a strong gradient;
need is anti-correlated with switching; control is lower when behind on bills) and one is contested (age separates
switching: the revealed gap is +3 to +7 points against +19 to +32 stated). The second candidate is
`communications-sentiment-and-nps`. Its 2 Nov addition carries "reputation is a stock" and "trust decides where a move
goes".

Insight (4):
- `what-a-customer-is-worth`: a thesis with ten hypotheses resting on practitioner estimates. None has been measured.
- `the-first-year-blind-spot`: a method lesson drawn from our own simulated world.
- `other-markets-compared-with-gb`: the advisor's synthesis and closeness ranking, which is judgement and not measurement.
- `how-houses-change`: a stub. Its only content is a principle and two measurements of our own model.

Mixed (23):
- `the-customer-needs-framework`: see above.
- `communications-sentiment-and-nps`: "a bad complaint drives departure, not dissatisfaction" is our synthesis of two surveys 11 years apart. The page also carries "reputation is a stock" and the trust split.
- `how-households-choose`: "the SVT is an absence of decisions". Its "act overwhelmingly on price" is **contested by the page's own source**: 44% of switchers named a cheaper tariff.
- `next-best-action-and-cross-sell`: "rank on what the action changes" is a normative conclusion.
- `the-price-a-household-is-shown`: "a real forward price against an implied one" is our reading of the published conventions.
- `ev-solar-and-batteries-as-products`: where the supplier's money comes from is our synthesis.
- `household-flexibility-and-the-advice-roadmap`: "value lies in automated shifting, not events".
- `household-carbon-and-the-measures-that-save-it`: the ranking of measures rests on unverified pack assumptions.
- `who-drives-how-far-and-where-they-park`: "mileage follows the driver, not the fuel" is a causal reading.
- `back-billing-and-liability`: the landlord void rule is "our reading of the licence"; the direct-debit consequence is our inference.
- `bad-debt-provisioning`: "the world's 91-day debt stock matched Ofgem's" is a result from our own simulation.
- `hedging-forward-market`: "hedging buys certainty" and "no optimum exists" are framing sourced only to "standard practice".
- `what-a-house-does-to-its-energy`, `who-lives-where`, `how-many-synthetic-households`, `weather-cells`: each carries our own measurements of our model or method beside the published facts.
- The seven `other-market-*` pages: each headline is the advisor's transferability rating, which the pages themselves say is "judgement, not a measurement".

## Circularity

**No breach.** No insight with `from_sim: true` is read by a `world:` or `calibration:` module. In code, nothing reads the
customer-needs notes, the 233-house note or the independence note.

One case was judged, not hidden. `simulation/experienced_bill_shock.py` cites the sim finding behind
`the-first-year-blind-spot` (the year-one-blind bill-shock count) as the reason the world's measure was replaced. Its
values rest on `what_bill_shock_is.md`, which is knowledge, and the level was refitted against the published band. I read
that as insight guiding a build, which the steer allows, and not as a parameter taken from the simulation. So the
insight's own `use` is empty, and the module appears in the page-level `use`. If the rule is meant to bar this too, the
test would need that row.

## World parameters resting below P

Pages with grade floor A that a `world:` module reads:
- `debt-and-collections`: the world carries labelled ranges where no source publishes a value.
- `home-moves`: the page itself says "this is an assumption".
- `hedging-forward-market`: source given only as "standard practice". Read by `simulation/run_phase2b.py` through a hedge note.
- `how-households-behave-toward-a-supplier`: a stub, graded A by rule. The notes behind it (CIM W6, the contact trials) are P or D.

Pages with grade floor S that a `world:` module reads: `acquisition-and-retention-economics` (the comparison-site rate is
secondary), `payments-and-direct-debit` (the 2.2% direct-debit return rate is secondary), `ev-solar-and-batteries-as-products`
and `the-first-year-blind-spot`. A floor is the page's weakest figure. It does not prove that the world reads that figure.
That join is per constant, and this audit did not make it.

## What I could not determine

- **Grades are judgement.** Few pages state D/P/S/A for each figure. Only the customer-needs page grades every figure.
- **Results from our own simulation are kept out of `grade_floor`.** They appear as insight rows instead, because D/P/S/A grades evidence about GB and a simulation output is not that.
- **`verified` rests on the page's own record.** "yes" means the page records a check after it was written. "partly" means it was written from primaries with no separate check, or with items still open. "no" means `last_verified` is null, or it was "checked" by a worker on the day of writing, which is the pattern the review-state rule already calls not a check.
- **Some vintages are approximate.** Where the page gives no dated source, vintage is the newest date in its source line. For `metering-and-reads` and `how-houses-change` it is the page's own date.
- **`use` was found by grepping**, for the page slug and the notes the page cites or that declare it (`**Knowledge:** <slug>`), over `simulation/`, `sim/`, `company/` and `saas/` with tests excluded. The `ASSUMPTIONS.md` register was excluded because it is generic. So were generic text hits on "price-cap" and "carbon-price". `page:` entries are slug links in other pages' rungs and the home, capabilities, harness and model-map pages. Most pages cite each other by title, so those cross-links are undercounted. The only calibration entry found is `simulation/departure_level_anchor.py`, which `how-households-choose` reaches through `gb_switching_rate_denominators.md`.
- **`how-many-synthetic-households` is marked not from the simulation.** Its reference population is drawn from NEED by `tools/demand_vector_coverage.py`, not from a world run. If its outputs turn out to come from our demand model, its insight becomes `from_sim: true`, and its `world:simulation/settlement_choice.py` use becomes a circularity breach to re-check.
- **One insight is not on any served page:** "age outweighs income" (`age_life_stage_and_life_events_cim_wave3_2026-11-02.md`) declares the customer-needs page, but the page does not state it. The same holds for the notes on trust and capability, segmentation, and stated against revealed preference.
