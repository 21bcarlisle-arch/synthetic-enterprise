# THE MODEL ON A PAGE

**Status:** CANON (Tier-2). **Adopted:** 2026-07-23. **Mission superseded 2026-08-28** (§The mission).
**Provenance:** [DIRECTOR-RULING → canon] via advisor bridge —
`docs/staging/DIRECTOR_CANON_MODEL_ON_A_PAGE_2026-07-23.md` (staged commit be3da591a).
The director asked for the whole design on one page, split into exactly two timeframes: what
the machine runs on NOW (core), and what it EVOLVES INTO (later).
**2026-08-28, director direct, verbatim and binding:** the mission sentence below replaces the former
"one-sentence company" here AND the fidelity line in `CLAUDE.md`. It is a change of PURPOSE, not a
correction of fact — unlike C1/C2/C3 (2026-08-28), which corrected claims this page made about the
code. Nothing in the spine, the wall, the timeframes or the reading rule is withdrawn by it; what
changes is what all of that is FOR.

**Reading rule (director's, binding):** anything in **Timeframe 1** claimed as working must carry
its proof (level, test, or gap named). Anything in **Timeframe 2** stated as present tense anywhere
on the site is a **claim-status defect**. Where this page and any FRAME doc disagree, surface the
disagreement as a finding (see §Open findings).

---

## The mission

> **We are creating enterprise value by automating ways to find individual customers we can create
> value for, and sharing in that value — by saving them money, time and carbon, through personalised
> modelling, tariffs and advice.**

*Director, 2026-08-28, verbatim. Supersedes "cutting carbon through personalisation, measured in £ per
tonne of CO₂e saved" here and "Goal: detailed enough to say 'that is how a real UK energy supplier
works'" in `CLAUDE.md`.*

**Carbon is not demoted — it is one of three.** The old sentence made carbon the mission and £/tCO₂e
the score. The new one makes carbon one of three currencies the household is saved in, and makes the
*method of finding and serving that household* the thing being built. Every carbon commitment on this
page (`E5`, the SAVED/SPENT/NET ledger, the £/tCO₂e front-page target) survives intact and keeps its
level; what it loses is the claim to be the whole purpose.

**Canon v4 (2026-10-12), quoted:** carbon's job (CO1) is "to show customers what they've saved and
could save in CO2, so those motivated by it can enjoy it. That clarifies the mission's carbon part
rather than changing it". Time (M3) "means household effort, measured in its own unit (household
minutes per kind of activity) and never converted to pounds." Phases: canon §2.

### What follows from it, that no document said before

**1. Every decision has two sides, and transfer is not creation.** Value is created and *then* shared,
so a decision is scored on the household as well as on us. **Charging someone the cap transfers value
rather than creating any** — which is exactly why the profit maximiser kept finding it
(`docs/staging/WORKER_FINDING_THE_CHURN_MODELS_CAP_MAKES_THE_PROFIT_MAXIMISING_PRICE_UNBOUNDED_2026-08-25.md`).
That finding read the cap as a defect in the churn model's ceiling. Under this mission it is better
read as a **defect in the objective**: the maximiser was optimising a one-sided score correctly, and no
ceiling repair fixes a score with a side missing. The two readings are compatible and both fixes are
real; the ordering changes, because a two-sided score makes cap-pricing unattractive *on the merits*
rather than merely unreachable.

**2. There are three currencies — money, time and carbon — and only money has been optimised.**

| | household side (value CREATED) | our side (value SHARED) |
|---|---|---|
| **money** | **instrumented 2026-08-28** — `company/analytics/household_value_share.py` computes what a household kept against the published SVT at its own metered volumes, per customer-year; read by the price ladder, carried per ARM by the value-cycle A/B, and **published beside the company's own net margin on `/capabilities/` since 2026-08-28** — the first surface on which a reader meets both sides of one decision; read by no decision surface (`A47` at L2) | **EARN** — instrumented; the only leg of the *scored* objective |
| **time** | household minutes per kind of activity, never converted to pounds (M3); not yet instrumented | not yet instrumented |
| **carbon** | **ABATE** — designed, not instrumented (`E5`) | £/tCO₂e — designed, downstream of the cell to its left |

*The money row moved on the day the mission landed and the distinction it forced is the useful part:
what is instrumented is the household's **SHARE**, not the value **CREATED**. Creation is a comparison
of costs — a supplier whose cost stack equals the incumbent's and prices below it has transferred
margin, not made any — and the counterfactual supplier's cost is not observable to us. So the split of
a surplus is measured and the surplus's size is not (`A48`). Nothing optimises the household figure:
half of a two-sided objective is not the objective until the director decides it is, which is R13, and
`tests/company/test_household_share_is_not_yet_a_target.py` holds that and names its own release.*

*Time, observed-with-evidence 2026-08-28:* no time-, hours-, effort- or hassle-as-value symbol exists
anywhere in `company/`, `simulation/`, `saas/` or `tools/`, and no design document names time as a
currency. This is not "thinly built" — it is **absent**, and it is the only cell in the table that is.

**3. The enterprise value is the automated method, not the book** — the book is the evidence the
method works. *Observed, and it bites immediately:* `saas/enterprise_value.py`, the only module in the
repo carrying the mission's own noun, defines it as *"the portfolio-wide sum of the resulting
per-account CLVs … the total discounted future net margin of the customer book."* That is precisely
the definition this mission supersedes. Filed as
`docs/staging/WORKER_FINDING_THE_ONLY_MODULE_NAMED_ENTERPRISE_VALUE_MEASURES_THE_BOOK_2026-08-28.md`.

### Fidelity keeps its place, and gains its reason

The old sentence made faithfulness the goal. It is now the **precondition**: a world that cannot press
back cannot tell value CREATED from value TRANSFERRED, because in a market that never responds,
extracting and earning look identical on every instrument we have. That is the director's C2
correction (no competitor module) reaching the same conclusion from the other side, and it is why
`docs/design/THE_WORLD_MUST_PRESS_SEQUENCE.md` outranks new capability. Unchanged and still binding:
the two-way wall, the Point-in-Time Blindfold, and the test on every line — **could a real UK energy
supplier know this?**

### The three channels, and which of them reaches a household

Personalised **modelling**, **tariffs** and **advice** are how the mission says value gets to a
customer. Status as at 2026-08-28, observed-with-evidence — **noted, not being fixed here**, on the
director's instruction:

- **Tariffs — LIVE, and the only channel that reaches a household.** The renewal pricing engine sets a
  unit rate, the rate reaches the customer's churn decision (`simulation/customer_events.py`), and the
  household's outcome changes. This is the whole of the company's current contact with the value it
  claims to create.
- **Personalised modelling — EXISTS, but pointed at us.** The discovery loop clusters the book and
  `company/analytics/customer_value_view.py` builds a per-account view — explicitly *"the supplier's
  OPINION about value and retention"*, feeding cost-to-serve, churn risk and CLV. It is modelling **of**
  customers for our decisions, not modelling **for** a customer producing a household outcome. Nothing
  it computes is ever offered to the household it is about.
- **Advice — MODULES ON DISK, NO RECIPIENT.** `company/pricing/switching_recommendation.py` renders
  inside `company/portal/app.py`, and `company/crm/decarb_recommender.py` exists and is discovery-wired.
  But **nothing in `simulation/` consumes a recommendation** and no simulated customer visits the
  portal, so no advice has ever reached a household or changed one's behaviour. The channel is built
  everywhere except at the point where it would matter.

Two of the three channels therefore cannot yet create the value the mission is about, which bounds
every household-side measurement before it is taken.

## The spine (true in both timeframes)

**THE WORLD (SIM truth, behind the wall):** Real weather → real half-hourly wholesale prices and
demand (2016–2025, 168k settlement periods, the actual record including the 2021–22 crisis). A drawn
population of synthetic households — different mix every run — each with drawn hidden traits and a
metered life. *Traits express through ONE channel and two carry none — corrected 2026-08-28 (C1):*
`price_sensitivity` reaches the world through the churn decision (landed 2026-08-27) and carries a
published between-group spread of only **1.26×**, which this seat has measured as structurally
unlearnable on the current book; `green_stance` and `channel_pref` are drawn, coverage-tested and read
by no response function at all. The world therefore still **records** more heterogeneity than it
**expresses**.

**THE WALL (two-way — F-MOAP-2, 2026-07-23):** Ground truth never crosses; everything else is an
interface flow in one of two directions. *Inbound* (what the company sees): market feeds and forward
curves, *published forecasts with realistic error*, meter reads (imperfect), payments, complaints,
replies, and **settlement — arriving late** (a first-class inbound gate: the truth about a period lands
months behind it). *Outbound* (what the company sends): **bills, offers, messages**. A bill is
**outbound**, never an observable — the inbound observable is the *payment or complaint that answers a
bill*, not the bill itself. Forecast error is the wall on the future; discovery-through-behaviour is the
wall on the customer.

**THE COMPANY:** Acquires customers → forecasts its book's shaped demand → prices tariffs from the
cost stack → hedges forward to delivery → bills on three clocks (billed/settled/banked) → collects →
serves and converses → settles months later and learns from the true-up. It can be wrong, and it must **not be
guaranteed to live** — *corrected 2026-08-28 (C3, director): the company does not have to die; survival
has to be genuinely at risk on a path the world can actually produce.* Three mechanisms carry that risk
in reality and **none of them presses yet**: **hedging** (collateral is a cost line sized once at term
start and fixed for the term — never a CALL), **competition** (blocked entirely by C2), and **debt**
(arrears do not yet arrive coupled to wholesale peaks). All three are cash-and-timing problems, not
profit problems, and there is no mechanism converting a bad quarter into a liquidity constraint — which
is why EARN has been the only leg the world can press on. Atoms `B6_collateral_cash_death_loop`,
`B7_customer_state_layer_moves_and_shocks`, `SPINE_1_scenario_world_state`.

**THE SCORE:** Survive (hard constraint, judged worst-case). Earn (EV, probability-weighted). Abate
(tCO₂e per customer from grid-intensity × half-hourly use, priced in £/tonne). *Corrected 2026-08-28
by the mission above: all three legs are scored on the COMPANY. Survive and Earn are ours by
construction, and Abate — though it counts a household's tonnes — is instrumented as our £/tCO₂e and
is not yet instrumented at all. **The score has no household-side term in any currency**, which is the
structural reason a maximiser can win it by transferring value rather than creating any. Making it
two-sided is a mission-level change to the objective, not a tuning of it; the six cells and what fills
them are in §The mission.*

---

## TIMEFRAME 1 — CORE (running or landing now)

**World:** the real 9-year record as ground truth · weather→price coupling proven
(Beast-from-the-East regime) · single imbalance price · settlement lag real (world at 2025-12, books
at 2025-06).
**Population:** curriculum-drawn cohorts (coverage knee ~12 cells, protected tails: fuel-poor
off-gas, prepay, vulnerable) · engagement mix 0.45/0.35/0.20 (ratified) · tenure×adoption gating live
· assets (EV/HP/PV) on anchored S-curves.
**Company organs:** acquisition & churn (market-coupled swell proven; moneyness trigger absent —
known; **the market DEFENDS but does not yet CONTEST — corrected 2026-08-28 (C2), and corrected again
the same day by `tools/canon_drift_check.py`, which caught this page still carrying the morning's
verdict hours after the code had moved**: reading the real switching record is genuine coupling to
history, and there is now **a rival that moves: `simulation/competitor_reference.py`** — it matches a
company that undercuts it, over quarters, on a lag the company does not control, and never below its
own cost stack, so a price advantage now DECAYS instead of persisting (measured: −10.0% position at
CHASE=0, −5.0% one quarter later at CHASE=0.5). What has NOT changed: market position is a run-level
constant where no offered rate is to hand, and the company still cannot price above the cap at all
(`renewal_desk._apply_competitive_ceiling` clamps it), so **over-pricing still carries no competitive
consequence** — the maximiser's discovery that charging the cap is close to free is the discovery that
the cap is a hard ceiling with nothing above it. Nobody yet targets the company's book. **Consequence,
stated where the capability is:** every measurement of the company's pricing decisions taken BEFORE
2026-08-28 was taken against an opponent that could not move, so "beats the flat baseline" compares two
internal policies, not two suppliers, and stays that way until it is re-measured against the defending
rival. Atoms `B10_competitor_switching_response` (defence leg landed), the contested ceiling
next.) · naive forward belief (120-day trailing) it must outgrow *(corrected 2026-10-09, factual: 120 days is the default window, which adapts between 30 and 180 days with recent volatility, and the mean is EWMA-weighted — still a statistic of past spot prices, not a forward curve)* · UK-compliant billing, three clocks
· collections · Tier-1 bill-accuracy compliance · conversations v1 (the F1 triad: company writes,
customers respond, harness scores the gap).

**THE PER-CUSTOMER PRICING ARM REACHES 2.07% OF THE RENEWALS THE WORLD OFFERS — measured
2026-08-28, and it bounds every A/B figure this project publishes.** Of 1,209 renewals: 398 are
acquisition terms with no prior term to price against, 357 are **gas** (the arm is
electricity-only), 429 carry no product label the arm prices, and **25 are priced**. Two of those
three exclusions are deliberate scope; the third is a gap in the drawn book. The consequence worth
carrying: the world's own switching response is calibrated **dual-fuel**
(`MARKET_SAVINGS_BY_YEAR`), so **the arm is narrower than the world it is scored against** —
an electricity-only policy judged by a dual-fuel switching curve. Finding:
`WORKER_FINDING_THE_ARM_IS_NARROWER_THAN_THE_WORLD_IT_IS_SCORED_AGAINST_2026-08-28`.
*(Corrected 2026-10-04, a factual correction: since `3088f8c71` (2026-09-07) the pricing arm prices
gas renewals too — the electricity-only guard `UPLIFTABLE_COMMODITY` was removed when its stated
reason had stopped being true. The 2.07% above is the 2026-08-28 measurement, not the arm today.)*
**Discovery loop:** company clusters its book from observables only, scored on worst-cell
belief-vs-truth; first refuted assumption already recoupled (renters/heat-pumps).
**Carbon:** designed ledger (SAVED/SPENT/NET), honestly *not yet instrumented* — the site says so
plainly. *(Corrected 2026-10-09, a factual correction found by `tools/canon_drift_check.py`: a
household's emissions are now measured. `company/carbon/half_hourly_footprint.py` multiplies NESO's
half-hourly intensity by the half-hourly reads of the accounts that have them and profiles the rest,
and Explore publishes it. The ledger is still called by nothing, and abatement is still unmeasured,
because nothing supplies the counterfactual it needs.)*
**Method:** the harness itself — gates, R1–R17 (canon H1), daily self-note — the third product. *(Corrected
2026-10-04: "twin approvals" removed; the twin last acted on 2026-07-16.)*

## TIMEFRAME 2 — EVOLUTION (registered, sequenced, not yet true)

**World deepens:** scenario spine live (NESO-central / crisis-replay / glut, tail-heavy sampled,
true-probability tagged) · gas storage stock-and-flow that can *produce* a 2022 inversion · forecast
layer at multiple horizons with error shrinking to delivery · warming trend without thinned extremes ·
spike-tail fixed (the declared 10× gap) · renewables/battery/interconnector penetration as scenario
fundamentals.
**Market deepens:** the traded product ladder (seasons/quarters/months/DA) with moving
contango/backwardation · shaped annual cost as the benchmark · cover-fan vs policy ladder · trading
value-add ledger net of day-one friction · cap observation-window mechanics · **competitors**, so
pricing meets opposition.
**Company deepens:** collateral→cash death loop (2021-22 replay must show death-by-collateral with
P&L surviving) · retail gas actively hedged into the existing plumbing · cost-to-serve & opex ·
VAT/CCL tax cycle · cannot-pay/will-not-pay collections physics.
**Customers deepen:** the state layer (moves = credit exit + two deemed entries, births/deaths/divorce,
income shocks) · continuous engagement replacing the three bins · price-sensitivity and attitudes
*discovered* through conversations and offers, never tagged · misclassification-cost physics ·
holdout-measured uplift so "this segment justifies its treatment" is proven, not asserted.
**Carbon's public face (CO1, CO3):** the customer's saved and could-save CO₂ is what is shown; E5
instrumented — NESO intensity × every half-hourly read → per-customer trajectories. £/tCO₂e "is a
diagnostic, not a target", kept internal in three ledgers.
**Endgame:** whole company lives rerun across scenario worlds to death or endpoint. The fitness
function is open and the director's until Phase 3 (canon §2).

---

## Open findings (director-authored reading rule: surface disagreements)

**F-MOAP-1 — "seed /simplified" conflicts with the SITE_V5 five-surface IA (director call).**
The adoption instruction has two sub-items: (a) adopt this to canon [DONE, this file]; (b) "treat it
as the seed for the /simplified lay page — same content, plainer words." Sub-item (b) is **blocked on
a director IA decision**, not on build capacity:

- The SITE_V5 structure ruling (`docs/design/SITE_V5_STRUCTURE_CONFIRMATION.md` §row 4, director-ratified
  the same day, 2026-07-23) **folded `site/simplified/` into Proof** and surface_4_proof landed live
  with `/simplified → /proof` 301'd (its door killed as part of the cut-to-five-surfaces IA).
- This canon file asks for a plain-language **lay page** seeded from the model-on-a-page. That is a
  *different artefact* from the simplifications *register* that was folded into Proof — but it would
  need a home in (or a reopening of a door within) an IA the director just deliberately narrowed to
  five surfaces.

Choosing the host — resurrect `/simplified` as a lay page, host the lay explainer inside an existing
surface (Front door / Proof), or defer — is a **category-6 IA / values call reserved to the director**
(the same authority that set the five-surface IA). The agent does not unilaterally reopen a door the
director just closed, nor silently drop his seed instruction. **Escalated via NTFY; default if no
reply: host the plain-language model-on-a-page as a fold inside the Front-door surface (the closest
match to "the pitch in plainer words") when surface_1 next iterates, NOT as a resurrected `/simplified`
door.** Tracked as the open sub-item on the parked staging file.

---

## The picture (the front-door diagram's words)

*Added 2026-10-24 on the director's steer of that morning ("i thought we already review this to
create a multi layer live artefact?"). `site/assets/model-on-a-page.svg` is generated at publish
by `tools/model_on_a_page_picture.py` from the block below, so the 27 Jul ruling (never kept in
sync by hand) now covers the picture as well as the list under it. The words here are the
picture's words, and `sheets:` holds the words of the L2 sheet one tap down from each band
(`tools/model_on_a_page_sheets.py`, 9 Oct). The state of each Now line or sheet box is not
written here: the generators read it from the maturity map's levels for the atoms it names
(. every atom at target, _ in build, ~ not started; on a sheet, the front door's words Live, Building, Planned). No figure, stat or count goes on the picture (9 Oct). A canon line quotes its
id.*

```yaml
tagline: An autonomous UK energy supplier, run inside a faithful simulation of the real market.
mission_id: M1
mission:
  - "“We are creating enterprise value by automating ways to find individual customers we can"
  - "create value for, and sharing in that value — by saving them money, time and carbon, through personalised"
  - "modelling, tariffs and advice.”"
test_line: "The test on every line: could a real supplier know this?"
governance:
  heading: THE GOVERNANCE — ONE HUMAN, THE REST IS AI
  boxes:
    - {name: Director, sub: "the human · mission (G1)", human: true}
    - {name: Delivery seat, sub: "direction → priorities (G1)", ai: true}
    - {name: Builders, sub: "sessions · daemons", ai: true}
    - {name: Harness, sub: "gates · rules · maturity"}
  flow: builds and steers everything below
world:
  heading: THE WORLD — SIM GROUND TRUTH, BEHIND THE WALL
  boxes:
    - title: The real record
      lines: ["2016–25 half-hourly prices, replayed", "as they were — the 2021–22 crisis too.", "Real weather → each home’s demand."]
    - title: A drawn population
      lines: ["Drawn fresh every run; each home hides", "its finances, life events, and a thermal", "home under local weather. Dual fuel."]
  rival: {title: a rival, does: defends prices, not_yet: ["contests:", "not yet"]}
  note: "The world moves ahead of the books: settlement lands months late. Ground truth never crosses the wall."
  scale_heading: WHY WE DON'T NEED MILLIONS
  scale:
    - title: Value, not volume
      lines: ["Cohorts drawn for learning value, not headcount.", "The founder book is the production shape (R6)."]
    - title: Repetition, not scale
      lines: ["Seed families: small books side by side on distinct", "seeds — a stated question, the smallest run (R5, R6)."]
wall:
  heading: THE WALL
  sub: "Ground truth never crosses. Everything else is an interface flow — in one of two directions."
  in: [market feeds, forecasts ± error, meter reads, payments, complaints & replies, settlement (late)]
  out: [bills, offers, messages]
  out_note: "— the company touches the world only through what it sends"
  foot: "Forecast error is the wall on the future · discovery-through-behaviour is the wall on the customer"
company:
  heading: THE COMPANY — SEES ONLY THROUGH THE WALL
  loop_out: [acquire, forecast book, price tariffs, hedge forward, bill out]
  loop_back: [collect, settle (late)]
  learn: learn from true-up
  serve: "serve & converse — always on, woven through every step: sales · queries · care · collections"
  stack: "One integrated, fully agentic stack grown end to end — trading · finance · billing · CRM · operations · debt."
  clocks: "Bills run on **three clocks** — billed / settled / banked — and the truth arrives months behind the money."
  engine:
    title: Payment and debt engine · next best action (C7)
    atoms: [E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build, C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv]
    lines: ["“Payment, credit risk and forward cash forecasting are the heart of this business.” (M7)", "One forward cash forecast per customer drives provision, drift limits and plans (C9)."]
  discovery:
    title: Discovery loop
    lines: ["The company clusters its book from observables only, scored on worst-cell belief-vs-truth.", "It forms beliefs, prices against them, and must live with being wrong."]
  warning: "It can be wrong, and it must not be guaranteed to live (M8) — collateral does not press yet."
score:
  heading: THE SCORE
  legs:
    - {name: SURVIVE, sub: "hard constraint · judged worst-case"}
    - {name: EARN, sub: "expected value · probability-weighted"}
    - {name: CARBON, sub: "CO₂ saved & could save (CO1)"}
  note: "The household is saved in three currencies: **money, time and carbon** (M3). £/tCO₂e is an internal diagnostic (CO3)."
now:
  heading: NOW — PHASE 1, BUILD (V1)
  items:
    - {text: "2016–25 record replayed; weather → demand", atoms: [W1_3_national_weather_signal, W1_4_regional_weather_field, W1_reveal_over_time, W1_5_premise_demand_shape]}
    - {text: "Curriculum-drawn cohorts, protected tails", atoms: [CA1_cohort_assignment_live, CA2_coverage_report_realised_cohort, W2_2_population_draw]}
    - {text: "UK-compliant billing on three clocks · collections", atoms: [D1_bill_correctness, D2_three_clocks, EP4_collections_journey]}
    - {text: "Tier-1 bill accuracy · assets on anchored S-curves", atoms: [D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used, C4_adoption_physics]}
    - {text: "Household half-hourly CO₂ measured (CO4)", atoms: [EP13_adapter_carbon_intensity]}
    - {text: "A rival that defends: renewals meet its price", atoms: [W2_3_competitor_field, B4_competitor_field]}
    - {text: "Payment and debt engine · next best action", atoms: [E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build, C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv]}
    - {text: "Life events: moves, income shocks, deaths (B7)", atoms: [B7_customer_state_layer_moves_and_shocks, W2_5_life_event_stream]}
    - {text: "Its own randomised holdout, read (C8)", atoms: [B8_discovered_price_sensitivity_holdout]}
    - {text: "Conversations v1: write, respond, score the gap", atoms: [F1b_company_comms, W2_39_households_respond_to_contact_including_badly]}
    - {text: "Naive forward belief it must outgrow", atoms: [G15_forward_curve_series_to_backtest_hedging_by_physics]}
    - {text: "Abatement: no counterfactual yet (CO4)", atoms: [E5_carbon_three_ledger]}
    - {text: "Time, household minutes: not yet instrumented", atoms: [C31_time_is_the_currency_that_does_not_exist]}
    - {text: "The harness itself — a product in its own right", atoms: [H1_supervisor_turn_granting, H7_skills_and_rules, H12_mutation_test_controls]}
  foot: ["Anything claimed as working carries its proof —", "level, test, or gap named."]
evolves:
  heading: EVOLVES INTO — ADAPT, FORWARD
  items:
    - "Scenario worlds: crisis-replay, glut, tail-heavy"
    - "Traded product ladder; rivals that contest"
    - "Collateral→cash death loop (2021–22 replay)"
    - "The rest of the state layer: births, divorce"
    - "Price-sensitivity discovered, never tagged"
    - "Holdout-measured uplift: proven, not asserted"
    - "Abatement measured: CO₂ a home did not emit"
    - "Phase 2: learns within a run (V2)"
    - "Phase 3: runs past the record, trends unseen (V3)"
    - "Endgame: whole lives rerun to death or endpoint"
  tail: "— the fitness function is open until Phase 3 (§2)."
  foot: ["Anything here stated as present tense anywhere", "on the site is a claim-status defect."]
footer: "// THE_MODEL_ON_A_PAGE.md · DIRECTOR_CANON.md v4 (2026-10-12) · no stats on the picture · poesys."
sheets:
  world:
    title: The world
    lead: ["A synthetic Britain the supplier cannot see into: real prices and weather from 2016–25, and households drawn fresh each run with lives, homes and money the supplier is never told about.", "Each box below is one part of it, read from cause to effect."]
    columns: [THE RECORD, THE WEATHER, THE HOUSEHOLD]
    rows:
      - - {title: Wholesale prices, lines: ["Half-hourly, 2016–25, replayed as", "they were — the 2021–22 crisis too."], atoms: [W1_reveal_over_time]}
        - {title: Real weather, lines: ["The national signal and the regional", "field, as it happened."], atoms: [W1_3_national_weather_signal, W1_4_regional_weather_field]}
        - {title: A drawn household, lines: ["Drawn fresh every run from published", "cross-tabs: who lives there, what home."], atoms: [W2_1_archetype_layers, W2_2_population_draw]}
      - - {title: The price cap, lines: ["Set each period by Ofgem from", "wholesale and other costs; it limits", "what a default tariff may charge."], atoms: [W3_1_price_cap_binding]}
        - {title: Each home’s demand, lines: ["Heat load from local weather, through", "the home’s own fabric, shaped by who", "is in and when."], atoms: [W1_5_premise_demand_shape, W1_14_weather_cells_for_household_heat_load, W2_13_occupancy_consumption_volume_shape]}
        - {title: Hidden finances and life, lines: ["A budget that may be under strain;", "moves, income shocks and deaths."], atoms: [W2_4_household_budget, W2_5_life_event_stream, B7_customer_state_layer_moves_and_shocks]}
      - - null
        - {title: Settlement, lines: ["What each home used, reconciled", "against wholesale prices months", "after it was used and billed."], atoms: [W3_2_settlement_timetable]}
        - {title: How it behaves, lines: ["It pays or falls behind, rations,", "answers contact, sometimes badly."], atoms: [W2_11_payment_behaviour_source, W2_8_self_rationing, W2_39_households_respond_to_contact_including_badly]}
    across: {title: A rival, lines: ["Defends its prices: when the company undercuts it, it follows over quarters, on a lag the company does not", "control, and never below its own costs. Going after the company’s book: not yet."], atoms: [W2_3_competitor_field, B10_competitor_switching_response]}
    wall: {heading: WHAT CROSSES THE WALL INTO THE COMPANY, items: [market feeds, meter reads, payments, complaints & replies, settlement (late)], note: "Ground truth never does: the company never sees a household’s budget, its home’s fabric or its intent."}
    links:
      - {label: Capabilities, href: "capabilities/", why: "what the company can do with what crosses, each line with its test."}
      - {label: How it’s built, href: "harness/", why: "the rules that keep the world honest and the wall shut."}
      - {label: Explore, href: "explore/", why: "the drawn households and their bills, one at a time."}
      - {label: The code, href: "code/", why: "the world’s modules, and the one seam the company reads through."}
  wall:
    title: The wall
    lead: ["The line between the world and the supplier. Only what a real GB supplier could receive crosses it — meter reads, market data, payments, industry messages, regulation.", "The test on every line of supplier code: could a real supplier know this?"]
    how: "Read each column top to bottom as a list, not a chain."
    arrows: false
    columns: [IN — WHAT IT RECEIVES, THE SEAM, OUT — WHAT IT SENDS]
    rows:
      - - {title: Market feeds and forecasts, lines: ["Prices and forecasts as a supplier", "would have had them, with their error."], atoms: [W4_1_typed_adapters]}
        - {title: Typed interfaces, lines: ["Each flow crosses through one typed", "interface; nothing else reaches in."], atoms: [W4_1_typed_adapters, EP6_wall_protocol_typing]}
        - {title: Bills, lines: ["What it charges each home, on", "three clocks: billed, settled, banked."], atoms: [D1_bill_correctness, D2_three_clocks]}
      - - {title: Meter reads and payments, lines: ["What a supplier observes of a home:", "its reads, and whether it paid."], atoms: [W4_4_payment_observable_seam]}
        - {title: Ground truth stays behind, lines: ["The world’s own state never crosses;", "a verifier refuses company code", "that reads it."], atoms: [W4_3_external_truth_wall, F1_epistemic_verifier]}
        - {title: Offers and messages, lines: ["Renewals, prices and contact: the", "only way it touches a home."], atoms: [F1b_company_comms]}
      - - {title: Complaints and settlement, lines: ["Replies and complaints as homes send", "them; settlement, months late."], atoms: [W3_2_settlement_timetable]}
        - {title: Discovery through behaviour, lines: ["What a home is must be inferred from", "what it does, never read off it."], atoms: [C2_discovery_through_interfaces]}
        - null
    across: {title: No route to the real world, lines: ["The company’s code may not open a network connection, directly or through anything it calls. Data fetched", "from outside becomes documentation and knowledge, never something the company reads at run time."], atoms: [H5_security_profiles]}
    wall: {heading: TWO WALLS IN ONE, items: [forecast error, discovery through behaviour], note: "Forecast error is the wall on the future; discovery through behaviour is the wall on the customer."}
    links:
      - {label: Capabilities, href: "capabilities/", why: "what the company does with each flow that crosses."}
      - {label: How it’s built, href: "harness/", why: "the verifier and the rules that keep the wall shut."}
      - {label: Explore, href: "explore/", why: "one household as the company sees it."}
      - {label: The code, href: "code/", why: "the seam itself, and the adapters on it."}
  company:
    title: The company
    lead: ["An automated supplier that sees only through the wall. It wins customers, prices, hedges, bills, collects and settles, and forms a belief about each home that it must act on while it is wrong.", "“Payment, credit risk and forward cash forecasting are the heart of this business.”"]
    columns: [THE LOOP, THE MONEY, THE CUSTOMER]
    rows:
      - - {title: Price tariffs, lines: ["Prices each renewal against its own", "costs and beliefs, under the cap."], atoms: [B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost, B3_hedge_tariff_alignment]}
        - {title: Bill, lines: ["Correct bills on three clocks, and", "catch-up bills when reads arrive late."], atoms: [D1_bill_correctness, D2_three_clocks, D3_catchup_rebilling]}
        - {title: Discovery loop, lines: ["Clusters its book from observables", "only, scored on belief against truth."], atoms: [C1_segment_layers, C2_discovery_through_interfaces]}
      - - {title: Hedge forward, lines: ["Buys ahead to match what it sold, on", "a naive belief it must outgrow."], atoms: [B3_hedge_tariff_alignment, G15_forward_curve_series_to_backtest_hedging_by_physics]}
        - {title: Collect, lines: ["Direct debits, arrears and plans;", "can’t-pay told apart from won’t-pay."], atoms: [C9_cantpay_wontpay_classifier, EP4_collections_journey]}
        - {title: Life events, lines: ["Notices moves and hardship from", "what it can see, and acts on them."], atoms: [C7_life_event_detection, B7_customer_state_layer_moves_and_shocks]}
      - - {title: Settle and learn, lines: ["Reconciliation arrives months late;", "it learns from the gap."], atoms: [E2_revenue_reconciliation, EP5_settlement_true_ups]}
        - {title: Payment and debt engine, lines: ["One forward cash forecast per", "customer drives provision, drift", "limits and plans (C9)."], atoms: [E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build, C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv]}
        - {title: Next best action, lines: ["One decision across debt, retention,", "upsell and carbon (C7)."], atoms: [C34_next_best_action_is_one_decision_across_debt_retention_upsell_and_carbon_judged_by_clv]}
    across: {title: The books, lines: ["Double-entry ledgers reconcile revenue to what was billed and settled, and the margin bridge shows where", "the money went."], atoms: [E1_ledger_double_entry, E2_revenue_reconciliation, B1_margin_bridge]}
    wall: {heading: WHAT IT SENDS BACK ACROSS THE WALL, items: [bills, offers, messages], note: "It can be wrong, and it must not be guaranteed to live (M8): collateral does not press yet."}
    links:
      - {label: Capabilities, href: "capabilities/", why: "each organ of the company, with its test and what it cannot yet do."}
      - {label: How it’s built, href: "harness/", why: "how the company is built and checked."}
      - {label: Explore, href: "explore/", why: "bills and payments for one household at a time."}
      - {label: The code, href: "code/", why: "the company’s modules, behind the seam."}
  score:
    title: The score
    lead: ["Is it working? Three tests: does it survive a worst-case shock, does it earn on a probability-weighted basis, and does each household save money, time and carbon?", "Value is created and then shared, so every decision is scored for both sides."]
    how: "Read each column top to bottom as a list, not a chain."
    arrows: false
    columns: [SURVIVE, EARN, CARBON]
    rows:
      - - {title: Judged worst-case, lines: ["A hard constraint: the company must", "not be guaranteed to live (M8)."], atoms: [A5_tournament_fitness_mortality]}
        - {title: Expected value, lines: ["Margin weighted by probability,", "per customer and over its life."], atoms: [B1_margin_bridge, EP1_clv_three_horizon]}
        - {title: Household CO₂, lines: ["What each home emitted, half-hour", "by half-hour (CO4)."], atoms: [EP13_adapter_carbon_intensity]}
      - - {title: The collateral loop, lines: ["The 2021–22 replay: hedges call for", "cash the company may not have."], atoms: [B6_collateral_cash_death_loop]}
        - {title: The household side, lines: ["What a home kept against the default", "tariff, beside what we earned."], atoms: [A47_the_score_has_no_household_side]}
        - {title: Saved and could save, lines: ["What a home saved and could save in", "CO₂ (CO1) needs a counterfactual."], atoms: [E5_carbon_three_ledger]}
    across: {title: The world can defeat the company, lines: ["A score is read only where the world can press back: one that cannot tell value created from value", "transferred."], atoms: [A6_coupled_triad_gap_metric, G1_fidelity_grid_scorer]}
    wall: {heading: THREE CURRENCIES FOR THE HOUSEHOLD (M3), items: [money, time, carbon], note: "Time is household minutes, never pounds. £/tCO₂e is an internal diagnostic (CO3)."}
    links:
      - {label: Capabilities, href: "capabilities/", why: "what each leg is measured by today, and what is not yet measured."}
      - {label: How it’s built, href: "harness/", why: "how a score is kept honest."}
      - {label: Explore, href: "explore/", why: "one household’s money and carbon."}
      - {label: The code, href: "code/", why: "the scoring code."}
  governance:
    title: The governance
    lead: ["One human sets the mission and the few decisions that can’t be undone. AI agents design, build, test and run everything else, inside gates that refuse work that would break the rules.", "Each box is one of those gates or roles."]
    how: "Read each column top to bottom as a list, not a chain."
    arrows: false
    columns: [THE DIRECTOR, THE SEAT AND THE BUILDERS, THE HARNESS]
    rows:
      - - {title: Mission and direction, lines: ["Sets the mission and the calls that", "are his to make (G1)."], atoms: [A2_decision_rights_register]}
        - {title: The delivery seat, lines: ["Turns direction into priorities", "and sequences the work (G1)."], atoms: [H1_supervisor_turn_granting, A1_learn_loop_chair]}
        - {title: Gates, lines: ["A commit is refused when a test", "or a rule says no."], atoms: [H24_precommit_gate_git_env_isolation, H23_publish_gate_scope_marker]}
      - - {title: Reserved actions, lines: ["Real money, real people and real-world", "commitments are never the machine’s."], atoms: [A3_approval_interface, H5_security_profiles]}
        - {title: The builders, lines: ["Sessions and daemons working one", "tree at once, under shared rules."], atoms: [H7_skills_and_rules]}
        - {title: The wall’s guard, lines: ["The epistemic verifier refuses", "company code that sees truth."], atoms: [F1_epistemic_verifier]}
      - - null
        - null
        - {title: Fidelity evidence, lines: ["Each claim of realism carries its", "source, and can be checked."], atoms: [G2_fidelity_evidence_ledger, G3_fidelity_inspection_chain]}
    across: {title: Controls that can fail, lines: ["A control is trusted only once it has been seen to fire on its own defect."], atoms: [H12_mutation_test_controls]}
    wall: {heading: WHAT REACHES THE DIRECTOR, items: [the stretch log, open questions with a recommendation], note: "Nothing the machine writes is quoted as his words."}
    links:
      - {label: How it’s built, href: "harness/", why: "the rules, the gates and the record of what he asked for."}
      - {label: Capabilities, href: "capabilities/", why: "what the machine has built under this governance."}
      - {label: Explore, href: "explore/", why: "what it produces."}
      - {label: The code, href: "code/", why: "the harness’s own modules."}
```
