# PROPOSAL — what step 1's knowledge says about the priority order (2026-10-05)

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `what-step-one-taught-about-the-order` (Lane 0 delivery)

**For the director.** DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05 asks for a proposal "whenever what is learned changes the order". Six knowledge pages landed with this document:
- unbilled energy and revenue assurance;
- debt and collections;
- home moves;
- next best action, upsell and cross-sell;
- EV, solar and batteries as products;
- communications, sentiment and NPS.

Each research document under `docs/market_research/` carries its sources, what our code does, and its gaps. Below is what they say about the order: every change, the evidence, and what I am doing meanwhile. Nothing here has been enacted in the order; atoms stay as minted until you rule.

## 1. Step 2 has a prerequisite the canon does not name

**The world cannot produce unbilled energy yet.** Used, settled and billed energy are one number:
- `simulation/settlement_run_series.py` settles the supplier on each customer's true consumption;
- the bill catch-up trues every bill to the same figure.

So the company has nothing real to find. Theft, unregistered sites and gas UIG cannot arise; UIG alone has run at about 2.5% of throughput since 2017, mostly theft.

**Proposal:** step 2 begins by making used, settled and billed three different numbers. Then the company measures the gap. Within step 2, in order:
1. Correct the ledger's "unbilled revenue" definition (cheap, no world change). Today it sums billed-on-estimate, not used-but-unbilled.
2. A per-household persistent read state, replacing independent monthly reads. This needs your practitioner answer, question 2 below.
3. Theft, unregistered and unknown-occupier consumption in the world, charged to the supplier through settlement.
4. The billed-against-settled reconciliation (EP5, D48).

*Source: `unbilled_energy_and_revenue_assurance.md`.*

## 2. Home moves belong in step 2, not only step 5

The world has no move event: a "home move" is relabelled renewal churn. The company credits every churner with a 55% chance of keeping the property, which is unsourced and wrong for a switcher. Yet change of tenancy is where **20-40% of GB domestic energy debt starts** (Ofgem call for input, 9 Dec 2025), mostly unnamed occupiers on deemed contracts.

**Proposal:** the world's move-out and move-in stream joins step 2, because it is unbilled energy as it arises. The company's offer to movers stays a step-5 lever. Before step 3, departures split into **switches** and **moves**. A churn hazard that mixes price-driven switching with tenure-driven moving would bias the forward-CLV base case.

*Sources: `home_moves.md`, `debt_and_collections.md`, which reach this independently.*

## 3. Billing complaints come with step 2; complaint handling before the levers

**Billing failures are 56-58% of Energy Ombudsman cases** (2024-25). The world raises complaints only when a unit rate rises by more than 20%.

**Handling quality moves departure,** and the supplier controls it: 9% / 17% / 23% of complainants had switched about two months later, for good / neutral / poor handling (Ofgem 2014, n=2,457, self-reported). Today handling is a world-side random draw, not a company lever.

**Proposal:**
- Re-key the world's complaint roll onto the billing failures step 2 creates, inside step 2.
- Make complaint handling a company decision feeding departure, in steps 3-4. Its caveats travel with it, and it is a range to check against, not a constant.
- Sentiment and NPS stay at step 7.

*Source: `communications_sentiment_and_nps.md`.*

## 4. Grade the world's debt against Ofgem's series before the debt lever

**Ofgem's full quarterly debt series, 2006 to Q2 2026, is downloadable as data,** which earlier notes said it was not. Since 2022 debt grew in depth, not breadth: average arrears rose 3.1x, accounts in arrears 2.3x. Meanwhile the world draws payment failure at an invented 3% / 12% / 35% by income stress, so a forecast built on it would learn those numbers back.

**Proposal:**
- Before the step-5 debt lever is drawn, grade the world against the Ofgem series. Grade it; do not tune it toward company results.
- Build the debt lever's **forecasting** half first. The **negotiating** half waits on question 3, because plan take-up and keep rates are not published anywhere.
- Debt-support contact is mandatory at a trigger the company can compute, so it does not wait for next best action.

*Sources: `debt_and_collections.md`, `next_best_action_and_cross_sell.md`.*

## 5. Step 4 should start with households that respond to contact, including badly

The literature's central finding: **rank on the effect of an action, not on the risk of leaving.** In a 65,000-customer telecoms field experiment, recommending cheaper plans raised churn from 6% to 10%.

The world's retention response is a flat 0.20 cut in hazard. It never goes negative and is the same for any discount, so a risk-targeted rule and an effect-targeted rule would score identically. C29's first build, a per-account engagement estimate, ranks by likelihood.

**Proposal:** step 4's first item is a world change in which households respond to contact:
- in proportion to offer size;
- differently from one another;
- sometimes negatively;
- with a lasting trace.

Then pair C29 with B8, so the first per-customer decision is graded on its EFFECT. `tools/decision_probe.py` already reads the world's true counterfactual, a grading instrument no real supplier has.

*Source: `next_best_action_and_cross_sell.md`.*

## 6. Within step 5: the order the world and the law can support

1. EV and smart-tariff upsell at the moment a household gets the kit: in-licence, sourced take-up, and the world already generates the moment.
2. Retention at fixed-term end, targeted on effect. SLC 22B allows bespoke retention only there.
3. Solar, battery and heat-pump leads.
4. Boiler cover and broadband cross-sell: no world model, causality not established, consent limits.

EV, solar and batteries rank behind three pieces of world work:
- export generation, with a registration the company can see (the world exports nothing today);
- EV charging timing that depends on tariff and charger;
- battery dispatch that depends on tariff.

*Sources: `ev_solar_and_batteries_as_products.md`, `next_best_action_and_cross_sell.md`.*

## 7. Plain errors found, fixed without waiting (the operating model's "correcting plain factual errors")

- EV load is counted twice in `run_phase2b.py`: about 5,065 kWh/yr against a published 1,800-3,500. This inflates what is billed, so it is fixed before step 2 measures anything.
- `satisfaction_churn` applies a 1.30 departure multiplier to dissatisfied households. Ofgem's 2025 survey has them switching less (3.0% vs 5.4%).
- The Ombudsman referral window is coded as 6 months; it is 12.
- `css_tracker.py` holds a series that matches no publication. It becomes an explicit `None` with its reason.
- Citations: back-billing is SLC 21BA, not "31A", and covers microbusinesses; the price-change notice is SLC 23, not 22B.
- `company/billing/cot.py` carries an invented deemed rate (SVT+20%), a price-cap table for 2016-18 when the cap began in 2019, and an unsourced 28-day trigger. It is retired or sourced.

## Questions only the trade can answer (the third side of knowledge)

1. **Home moves:** do suppliers mostly learn of a move-out from the customer, and of a move-in from "occupier" letters or a flagged switch? Roughly how long does an unnamed account run before contact?
2. **Reads:** do a minority of homes go unread year after year? The published record cannot say, and it decides whether back-bills are rare and large or common and small.
3. **Debt:** typical repayment-plan take-up and keep rates, and recoveries after write-off.
4. **Offers:** do GB suppliers run holdout groups on retention offers? How is PECR's "similar products" read in practice?
