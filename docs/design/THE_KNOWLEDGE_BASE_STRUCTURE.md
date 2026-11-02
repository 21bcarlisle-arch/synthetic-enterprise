# The knowledge base: six domains, two sides, and what is hidden from whom

*Worker tick, 2026-11-02, for the director's steer of 30 Oct
(`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1, first bullet: "Propose a structure for the whole knowledge base." This is a proposal and a
census, not a build. The page list was read off `site/knowledge/` at `e8f3b28a24`: 62 pages. Each
is placed below exactly once, checked against the served index when this was written.*

## 1. What the thing is

The knowledge base is every page that says what is true of the GB retail market and the households
in it, with its source: the 62 served Knowledge pages, the notes behind them in
`docs/market_research/`, the regulation commons in `docs/domain_artefact_library/`, and the
index of what is and is not established in `docs/institutional/knowledge_map.md`. The steer gives it
two readers:

- **the world** draws its hidden truth from it, and
- **the supplier** draws from it only what a real supplier could know, observe or ask.

So every page needs two labels: which side it informs, and, for each thing it establishes, whether
that thing is **hidden** (true of the household or the world, never seen by the supplier), an
**observable** (seen by the supplier through its own operations: reads, payments, contacts, what
the customer declares), or **public** (published, so both sides read it, at its publication date).

## 2. The six domains

The site already groups the pages under six themes (`site/knowledge/index.html`). Five of them match
the steer's suggested domains in substance. The proposal keeps three of them, splits *Winning and
serving customers* between operations, products and the new domain, folds *Carbon* into the two
domains its pages belong to, and adds the domain the steer asks for. Seventeen of the 62 pages move.

| Domain | Pages | Side it informs | What is hidden, what is seen |
|---|---|---|---|
| **1. Market and regulation** (was *Markets and prices*) | 14 | Both | Almost all **public**, read point-in-time: the supplier may only see a price or a rule from the day it was published. The world's own path of prices is the historical record (2016–2025), not drawn. |
| **2. The household and its assets** (was *Households and their homes*) | 14 | World first; supplier through one page | Almost all **hidden**: the house, its heating, the car, the roof, the people. `what-a-supplier-can-see-of-a-house` is the domain's seam page: it says which of these a supplier can observe and how well. |
| **3. Customer needs and behaviour** (new) | 6 now, 7 to write | World first; supplier through observed behaviour | The needs and traits are **hidden**. What a supplier sees is behaviour: payment method chosen, a fix taken, a switch, a complaint, a contact, arrears. The domain's job is to say how the hidden traits produce the observed behaviour, so the world can draw one and the supplier can only infer it. |
| **4. Supplier operations** (was *Metering, billing, debt and regulation*, plus four pages, less one) | 13 | Supplier first; world for the duties it must press back on | Mostly **observables** and **public** rules: reads, bills, payments, debt, the licence conditions. Hidden: the true consumption behind an estimate, the household's capacity to pay. |
| **5. Products, measures and services** (five pages of *Winning and serving customers*, plus two tariff pages) | 7 | Both | The offer is the supplier's own choice and **observable**. Whether it creates value depends on hidden traits (domains 2 and 3), so each page here must name which. |
| **6. Other markets** | 8 | Neither directly | **Public**. Used to test a design against a market that made a different choice, never as a runtime input. |

### 2.1 Where each page goes

**1. Market and regulation (14).** electricity-wholesale, gas-wholesale, gb-electricity-market,
merit-order-residual-demand, imbalance-cashout-settlement, hedging-forward-market,
non-commodity-costs, regional-supply-cost, price-cap, how-gb-gas-and-power-prices-move,
dated-household-cost-and-price-series, carbon-price, suppliers-accounts-and-capital,
vpps-and-local-flexibility. *Moved in:* carbon-price (from *Carbon*: it is a market price, not a
household quantity); suppliers-accounts-and-capital (from *Metering, billing, debt and regulation*:
it is a market rule on capital, the same for every supplier). *Moved out:* the two tariff pages, to
domain 5.

**2. The household and its assets (14).** how-many-synthetic-households, who-lives-where,
what-a-house-does-to-its-energy, weather-cells, how-houses-change,
what-a-supplier-can-see-of-a-house, who-drives-how-far-and-where-they-park,
which-cars-households-run-and-what-they-use, gas-boilers-and-heating-controls,
solar-pv-and-home-batteries, pv-roofs-orientation-and-yield, heat-pumps-and-fabric-measures,
household-carbon-and-the-measures-that-save-it, network-limits-on-home-electrification. *Moved in:*
the two carbon pages (they say what a house emits and what changes it, which is household physics),
and network-limits (a limit on the house's connection).

**3. Customer needs and behaviour (6).** how-households-choose,
how-households-behave-toward-a-supplier, the-residual-and-the-change,
heating-behaviour-comfort-and-health-floors, communications-sentiment-and-nps, home-moves.
*Moved in:* four from *Households and their homes*, two from *Winning and serving customers*.
*Two of these six say "Not yet written"* (`how-households-behave-toward-a-supplier`,
`the-residual-and-the-change`). They are the domain's existing gaps, not pages.

**4. Supplier operations (13).** metering-and-reads, smart-meters-and-half-hourly-settlement,
unbilled-energy-and-revenue-assurance, debt-and-collections, vulnerability-and-the-psr,
payments-and-direct-debit, back-billing-and-liability, read-access-and-theft-duties,
bad-debt-provisioning, switching-mechanics, acquisition-and-retention-economics,
what-a-customer-is-worth, the-first-year-blind-spot. *Moved in:* the first three of those four from
*Winning and serving customers* and the last from *Households and their homes* (each is a supplier's
own measurement, not a household fact).

**5. Products, measures and services (7).** tariffs-and-the-default-tariff,
the-price-a-household-is-shown, next-best-action-and-cross-sell, ev-solar-and-batteries-as-products,
ev-charging-and-the-saving-against-petrol-and-diesel, household-flexibility-and-the-advice-roadmap,
proving-and-showing-household-savings. *Moved in:* the two tariff pages from *Markets and prices*
(a tariff is the supplier's offer, not a market price).

**6. Other markets (8).** other-markets-compared-with-gb and the seven country pages.

The *Carbon* theme goes. Its three pages split by what they say: one price (domain 1), two
household quantities (domain 2). Carbon stays one of the things every domain-2 and domain-5 page
must report against (M3), which is a column, not a shelf.

## 3. The two labels, per page

The label is a judgement made per claim, not per page, and most pages hold claims of more than one
kind. The proposal is the smallest form that can be checked: each page's record gains two fields,

- `informs:` one of `world`, `supplier`, `both`, `neither`; and
- `seen_by_supplier:` for each quantity the page establishes, one of `hidden`, `observable`,
  `public`, with the observable's route named (a read, a payment, a declaration, a contact) where it
  is one.

The domain column in §2 is the default for a page. A page states the label only where it departs from
its domain's default. That keeps the cost to the pages that need it: the seam pages
(`what-a-supplier-can-see-of-a-house`, `the-first-year-blind-spot`, `vulnerability-and-the-psr`,
`payments-and-direct-debit`), where the same quantity is hidden to one reader and observable to the
other.

This is not built yet. Building it means a field in `site/data/knowledge_topics.json`'s page
records, rendered by the shared template, and the six pages that keep their own file. It changes
what the site shows, so it follows K8 as any page change does. It is the second step of Ask 1, and
it waits for the director to see this structure, because regrouping the served index is visible to
every external reader.

## 4. The customer-needs domain: what it lacks, ranked

The steer names seven pages. Ranked by how much each would change a world or supplier result, which
is the order to write them in:

| # | Page | Why it ranks here | What it would change |
|---|---|---|---|
| 1 | **Price sensitivity is two traits** (consumption elasticity; switching or shopping propensity) | The world already carries a departure response and the supplier prices against it. `PB4_engagement_separated_from_elasticity` sits at level 2 on the map, held by a blind pass that found SVT drift has no engagement term (D4). A wrong split here moves every renewal result. | The world's departure model and the supplier's renewal pricing. **Written 2026-11-02:** `docs/market_research/price_sensitivity_is_two_traits_cutting_use_and_shopping_cim_waves_3_6_2026-11-02.md` |
| 2 | **The GB natural experiments that pin the weights** (the fix share's 44% → 13% → 38%; collective switches; opt-in against opt-out; the 2023 prepayment findings) | These are the only places the GB record shows the size of a response, rather than a stated preference. Every other page needs them to bound its ranges. | The ranges on pages 1, 3 and 5. **Written 2026-11-02:** `docs/market_research/the_gb_natural_experiments_that_pin_the_weights_2026-11-02.md`; the 44/13/38 figures are unsourced and corrected there |
| 3 | **The needs framework with its evidence** | Already framed in `docs/design/CUSTOMER_NEEDS_BEYOND_THREE_CURRENCIES.md` (DISCOVER/FRAME, ten GAPs named). Writing it as a page is mostly publishing that note with each claim graded D/P/S/A. | What the scorecard measures (M3, as amended 31 Oct) |
| 4 | **Age, life stage and life events** | Life events are already drawn (home moves, a page exists). The claim that life stage outweighs income is the advisor's reading and must be tested before the world uses it. | Which latent factors the population draw carries (the parsimony ruling) **Written 2026-11-02:** `docs/market_research/age_life_stage_and_life_events_cim_wave3_2026-11-02.md`; age outweighs income on every CIM Wave 3 need at the margin, worry is a plateau to 54 rather than a 35-54 peak, and tenure, young children and disability load on different needs, so precarity stays a hypothesis for the joint |
| 5 | **Stated against revealed preference, and defaults** | Guards every other page: a stated willingness to pay used as a parameter overstates the response by the gap the packs cite (3–5×, to be verified). | The size of every response drawn from a survey. **Written 2026-11-02:** `docs/market_research/stated_against_revealed_preference_and_defaults_2026-11-02.md`; the 3-5× is two populations divided and is corrected to an offset of 28-36 points, and a defaulted household responds a third to a half as much per head |
| 6 | **Trust and capability** | The packs say these separate Ofgem's six attitudinal segments. Whether they change a supplier result, rather than describe it, is not shown. | Shopping propensity (page 1), if it holds |
| 7 | **Segmentation, and how well it predicts behaviour** | Matters to the supplier's method (M4) more than to the world: a segment that does not predict behaviour is not worth inferring. | Whether the supplier infers segments at all |

Beyond the seven, the two unwritten pages already on the site (`how-households-behave-toward-a-supplier`,
`the-residual-and-the-change`) are gaps in the same domain. The first overlaps page 1 and the
reactions to pain points the 30 Oct audit asked for. It should be written as that page, not as a
second one.

## 5. What this note does not do

- It verifies no figure. The packs' [unverified] items, and the re-grading of every figure to
  D/P/S/A, are the steer's Ask 1 addendum steps 1–3. They are done page by page as each page is
  written, from the primary tables, stored raw in `data/lake/` with provenance.
- It does not touch the world. The world additions (Ask 2) follow the correctness exit test, as the
  steer says. Their roadmap is a separate `for_the_director` row.
- It registers for no licensed dataset. That is reserved (G5); section 6 lists them for one row.

## 6. Licensed microdata that would improve a parameter (G5: listed, not registered)

The 16:51 addendum, step 4. The parsimony ruling keeps three latent factors (precarity, affluence,
life stage) and asks that their links to observable attributes be *fitted*, with effect and sample
sizes. Published cross-tabs give one attribute at a time against one need (the CIM Wave 3 tables
behind the framework page). They cannot give a joint: whether tenure, income, household type and
payment method load on one precarity factor or on two needs household-level rows. That is what each
dataset below would change. Access terms are graded P, read 2026-11-02 from the UK Data Service
access policy (`ukdataservice.ac.uk/help/access-policy/types-of-data-access/`) and SERL's
researcher page (`serl.ac.uk/researchers/`).

| Dataset | Access | What it would change |
|---|---|---|
| Understanding Society, main survey (UKDS EUL) | Safeguarded: register with UKDS and accept the End User Licence | **The largest gain.** Household-level joint of income, tenure, household type, age, arrears, energy payment method and the risk-attitude waves. It is the only route to fit the precarity, affluence and life-stage factors the ruling keeps, and to test "life stage outweighs income" on the same households |
| Wealth and Assets Survey (UKDS EUL) | Safeguarded, as above | Liquid savings by age and income: the size of the cash-flow need and the buffer that sets consumption elasticity's headroom. Today that is an A with a range |
| English Housing Survey (UKDS EUL) | Safeguarded, as above | Tenure × dwelling × fuel poverty × payment method on one record. Tightens which observable a supplier can use as a precarity proxy |
| SERL statistical dataset (UKDS EUL, SN 8963) | Safeguarded, as above. Aggregated, not per-home | Smart-meter consumption by household attribute through 2022–23: the crisis consumption response by group, which the price-sensitivity page could only state from survey answers |
| SERL Observatory, per-home data | Controlled: accredited researcher on an approved project, and a non-HEI body must partner a UK HEI project lead | Per-home response to price, and the base-load/active-use coupling now built as a stated belief. **Not recommended:** it needs a university partnership, which is a larger commitment than a registration |

**Terms that matter to the decision (P).** EUL users must "not use the data for commercial purposes
without obtaining permission", and some safeguarded collections are limited to non-commercial or
academic users. Poesys's mission is enterprise value, so whether this use is commercial is a
question the registration must answer honestly, not one to assume away. The registration is an
account and an agreement with a third party: a real-world commitment, reserved to the director (G5).

**What happens meanwhile.** Every factor loading stays fitted from the published cross-tabs, one
attribute at a time, and is graded as such. Where a joint is needed, the world carries it as an A
with a range and the page says which licensed dataset would close it.
