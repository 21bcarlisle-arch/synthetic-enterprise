# Next best action, upsell and cross-sell: what they are, how big, what is allowed, and what we have

**Knowledge:** next-best-action-and-cross-sell

> **Director's ruling, 2026-10-05.** The goal is TAILORED next best action per customer — their
> benefit first, then ours. Debt management is a form of next best action: for a customer in arrears
> the right action is a decision like a retention offer or an insulation suggestion. Next best action
> is therefore ONE decision spanning debt, retention, upsell and carbon advice, judged by CLV (atom
> C34), not a fixed ranking of measures; the heating-first ordering in the carbon page is evidence
> about typical magnitudes, which enter each household's decision through its own numbers.

**Research completed 2026-10-05, knowledge lane (director canon step 1, "now and wide").** Opened by
`docs/staging/done/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`, which names next best action (NBA)
and upsell/cross-sell as step-5 levers and asks the knowledge for them now. Primary sources were
fetched and read this pass (PDFs extracted with `pdftotext`); where a figure comes only from a
search summary or a vendor, it says so. Nothing here was produced by this project's simulation.

This file builds on, and does not repeat, four documents already in the repository:
`docs/market_research/what_a_conversion_decision_is_at_a_cap_boundary.md` (the conversion desk),
`docs/market_research/what_a_renewal_decision_is_for_a_gb_domestic_customer.md` (the renewal act),
`docs/domain_artefact_library/regulatory/pricing_differentiation_permissions.md` (what may be
priced on what), and `docs/market_research/company_customer_comms.md` (notice windows and
contact costs).

---

## 1. What next best action IS, said before it is split

**Definition.** Next best action is a *policy*: for one customer, at one moment, choose one action
from a fixed menu (and "do nothing" is always on the menu) to maximise the expected *change* in
that customer's value to both sides, net of the action's cost, subject to rules on what may be
offered to whom.

Three parts of that sentence carry the weight:

1. **Per customer, per moment.** The decision is indexed by (customer, time). A rule of the form
   "every customer in segment S gets offer O at renewal" is a *lookup table*, not an NBA. It may
   be the right answer, but it has not been chosen per customer.
2. **Expected change, not expected level.** The quantity being ranked is the *difference* the
   action makes compared with doing nothing (the uplift). Ranking on the level of an outcome (who
   is likely to churn, who is likely to buy) is propensity scoring, and §2 shows why that is a
   different quantity.
3. **A menu that competes for one slot.** Actions compete because contact capacity, customer
   attention and regulatory goodwill are finite. A retention call and a boiler-cover offer to the
   same household in the same week are not independent decisions.

**The menu for a GB domestic supplier**, with the kind each item is:

| action | kind | what moves | whose money |
|---|---|---|---|
| retention offer at fixed-term end | price (a tariff) | churn hazard at the decision point | supplier gives up margin |
| tariff move: SVT to fixed, fixed to fixed, to smart ToU or EV tariff | product switch within energy | price paid, risk borne, load shape | either way, depending on tariff |
| payment-method change (to direct debit, off prepayment) | servicing | cost to serve, bad-debt risk | bounded by SLC 27.2A to the cost difference |
| debt-support contact (repayment plan, ability-to-pay check, grants) | obligation plus servicing | arrears trajectory | licence-required at triggers (SLC 27.5B) |
| product offer: boiler cover, home services | cross-sell (another product) | second revenue line; possibly churn | customer pays a new price |
| smart tariffs, EV tariff | upsell or migration within energy | volume and timing of use | shared via the tariff |
| solar, battery, heat pump (sale, finance or lead) | cross-sell (another product, large ticket) | the household's own demand and export | customer capex; supplier margin or referral fee |
| broadband or other bundle | cross-sell | second revenue line; switching cost | customer pays |
| do nothing | null action | nothing, and saves contact budget | none |

**What NBA is NOT.**

- It is not a churn model. A churn model predicts who leaves; NBA decides what to do and whether
  doing anything helps (§2).
- It is not a campaign calendar. A calendar fixes the action and picks the date; NBA fixes the
  date (the moment) and picks the action.
- It is not price optimisation on willingness to stay. Pricing existing customers by their
  predicted reluctance to leave is the practice the FCA banned in home and motor insurance from
  January 2022 (§4.3). The energy default tariff cap and SLC 22B constrain the same thing in
  energy.
- It is not the same as "value-based renewal pricing". That moves one price at one decision. NBA
  chooses *among kinds* of action, including non-price ones and doing nothing.

**Upsell versus cross-sell, kept apart.** *Upsell* is more of, or a richer version of, the same
product: an EV tariff for an energy customer who has bought a car, a smart ToU tariff, a longer
fix, a green tariff. *Cross-sell* is a different product: boiler cover, a heat pump, broadband,
insurance. The difference is not only labelling. A cross-sell creates a second contract with its
own regulator (boiler cover sold as insurance is FCA business), its own consent basis for
marketing (§4.5), and its own churn. An upsell stays inside the energy licence.

## 2. Uplift versus propensity

**Propensity** is P(outcome | customer). **Uplift** is P(outcome | customer, treated) minus
P(outcome | customer, not treated). An NBA engine needs uplift. A propensity model is useful only
as an input.

The literature divides customers into four kinds against a binary action (Radcliffe and Surry's
naming; the idea is first set out in Radcliffe & Surry 1999, *Differential response analysis:
modeling true response by isolating the effect of a single action*, Proceedings of Credit Scoring
and Credit Control VI, Credit Research Centre, University of Edinburgh):

| kind | without the action | with the action | value of acting |
|---|---|---|---|
| persuadables | leave / do not buy | stay / buy | positive: the only group worth the cost |
| sure things | stay / buy | stay / buy | zero benefit, full cost (a retention discount here is pure transfer) |
| lost causes | leave / do not buy | leave / do not buy | zero benefit, full cost |
| sleeping dogs | stay | leave | negative: contact *causes* the loss |

**Sleeping dogs exist, and they are common in exactly our situation.** Ascarza, Iyengar &
Schleicher (2016), *The Perils of Proactive Churn Prevention Using Plan Recommendations: Evidence
from a Field Experiment*, Journal of Marketing Research 53(1): 46-60. A wireless telecoms
provider randomised about 65,000 customers; the treatment recommended a cheaper, better-fitting
plan. Abstract, verbatim: *"whereas only 6% of customers in the control condition churned during
the three months following the intervention, 10% did so in the treatment group."* The authors
attribute it to (1) lowering customers' inertia and (2) making past usage salient. A "you could
save money" message from an energy supplier is the same intervention.

**Targeting the highest-risk customers is often the wrong rule.** Ascarza (2018), *Retention
Futility: Targeting High-Risk Customers Might Be Ineffective*, Journal of Marketing Research 55(1):
80-98 (AMA Paul E. Green award, 2018). Two field experiments (a wireless provider and a
membership organisation): customers with the highest predicted churn risk are not the ones whose
churn the campaign reduces most, and targeting on estimated lift beats targeting on risk. The
abstract's numeric effect sizes could not be read this pass (publisher returned 403). That is an
open gap; the direction is sourced.

**Uplift has to be estimated from variation in who was treated.** It cannot be read off
observational data where the treated were chosen by a rule, because the rule is the confounder.
That means a real NBA programme runs a holdout: a random share of eligible customers who get "do
nothing". Every published effect size in §3 comes from a randomised trial for this reason. **No
holdout, no uplift.** This matters for what the company must log (§5).

## 3. Scale: what the published record says

### 3.1 How much a contact moves a GB energy household (randomised trials)

Ofgem's consumer engagement programme ran randomised trials in 2017-2018. Source: Ofgem,
*Insights from Ofgem's consumer engagement trials: What works in increasing engagement?*
(September 2019, `cross_trials_paper_report.pdf`), and the collective switch press release of
20 August 2018.

| trial | population | control switching | treated switching | uplift |
|---|---|---|---|---|
| Cheaper Market Offers Letter (CMOL), 2017 | SVT customers >1 yr, two suppliers | 1.0% | 2.4% (Ofgem-branded), 3.4% (supplier-branded) | +1.4 to +2.4 pp |
| Cheaper Offer Communications (CMOC) | SVT customers | 2.9% | 6.8% average across arms, 7.5% best arm (letter with reminder) | +3.9 to +4.6 pp |
| Best Offer Letter / CMA marketing arm | disengaged customers | 7% | 12% (Ofgem letter), 13% (rival marketing) | +5 to +6 pp |
| End of Fixed-Term Contract prompt (EFTC) | ~20,000 customers on 1-yr fixes at one supplier, letter or email a few days after term end | 19% | 28% | +9 pp |
| Collective switch (first trial) | ~50,000 customers on SVT 3+ years, one large supplier | 2.6% | 22.4% | +19.8 pp |
| Collective switch, second chance 6 months later | non-switchers from first trial | 2% | 14% | +12 pp |
| Collective switch, less-known supplier | | 4% | 19% | +15 pp |

Three findings in that report bear directly on NBA design:

1. **Timing beats content.** The only CMOC design variation with "any substantive impact" was a
   follow-up reminder. *"Including the incumbent supplier's own cheapest tariff on the CMOC made
   very little difference to switching rates"* (§3.18).
2. **The moment is the end of a fixed term.** The EFTC prompt (+9 pp) is the largest effect from
   a single supplier-sent message. That is the moment the BAT's market-wide derogation also
   targets (§4.1). The decision point and the legal window coincide.
3. **A prompt moves households in both directions.** These trials count any switch, internal or
   external. For the sending supplier, an engagement prompt raises both internal retention and
   external loss. Ofgem's follow-up (*Prompting sustained engagement in energy tariff switching*,
   October 2020) found 51% of switches in the collective-switch population were external and 49%
   internal.

**The effect persists. Activation is a state change, not a one-off.** In the same 2020 follow-up,
customers who switched during the collective switch trial had a *subsequent* switching rate of
63%, against 33% for those who did not. Of those who moved to the collective-switch tariff, *"70%
switched again within 17 months."* An action that wakes a household up changes its hazard for
years. A one-period NBA that ignores this will overvalue "wake them up" offers to sleepy,
profitable customers. That is the sleeping-dog problem with a long tail.

**Gap.** Every figure above measures switching *of any kind*, caused by a *market-wide or
regulator-designed* prompt. None measures "our supplier made our own retention offer to our own
customer and this many more stayed". The `what_a_conversion_decision_is_at_a_cap_boundary.md`
row in the knowledge map already records this as the second gap. It stands.

### 3.2 Contact fatigue: the cost of the action itself

- Baek, Chen, Ma & Mitrofanov, *Balancing Customer Engagement and Annoyance in Online Retail:
  Insights from a Field Experiment* (SSRN 6165626). Randomised daily versus every-other-day
  promotional email: halving frequency *reduced unsubscription by 59%* at a cost of a *5-8%
  decrease in short-term revenue*. Unsubscribing was associated with a *36% decrease* in monthly
  spend (observational leg). Online retail, not energy. **From a search summary of the abstract,
  not the full text read.** Use it for the shape, not the level.
- Energy-specific contact-fatigue elasticity: **no published source found.** Open gap.
- Cost per contact by channel: already recorded as an open gap with two disagreeing uncited
  figures in `docs/institutional/knowledge_map.md` (conversion-desk row). Not repeated here.

### 3.3 Product holding and churn: correlation, and how much is causal

- **Telecoms, triple play.** Prince & Greenstein (2014), *Does Service Bundling Reduce Churn?*,
  Journal of Economics & Management Strategy 23: 839-875. Using a pseudo-panel and
  nearest-neighbour matching to address selection, bundling does reduce churn for all three
  services, but *the effect is only visible during times of turbulent demand*. This is the most
  careful causal study found. It says bundling protects *when the market is moving*, which in GB
  energy means 2016-2018 and the 2023-2025 return of fixed deals, not 2021-2022.
- **Utility Warehouse (Telecom Plus plc), the only GB multiservice energy supplier at scale.**
  FY2025 final results (24 June 2025): 1,163,608 customers taking 3,392,593 services, which is
  about **2.9 services per customer** (services ÷ customers, both counted by UW). *"Our typical
  homeowning customers display below-market rates of churn and lower bad debt."* But annualised
  **energy churn rose to 13.7% (FY2024: 8.7%)** when the cap-to-fixed gap widened. The company
  also names *"our lack of an EV tariff until the end of the first half of the year"* as a churn
  cause. Two lessons. First, UW's own text attributes the low churn to *homeowners acquired by
  word of mouth*, so selection is built into the comparison, not separated from it. Second, a
  missing product (an EV tariff) is a churn driver for a household that has bought the kit.
- **British Gas Home Services (Centrica plc, Annual Report 2025, Business Review).** 2.939m Home
  Services customers against 7.956m Home Energy Supply customers (single households). Protection
  contract retention 87% (2024: 86%); the traditional protection portfolio declined 3%. The
  membership scheme has almost 600,000 members, *"with conversion of around 7% to a paid
  protection contract."* That last figure is a published cross-sell conversion from a free tier
  to a paid product. The overlap (how many households hold both energy and services) is **not
  published**. Open gap.
- **Cross-buying can destroy value.** Shah, Kumar, Qu & Chen (2012), *Unprofitable Cross-Buying:
  Evidence from Consumer and Business Markets*, Journal of Marketing 76(3): 78-95. Across five
  firms, **10-35% of customers who cross-buy are unprofitable**, accounting for 39-88% of the
  firm's total customer losses. **From the abstract as summarised.** The mechanism is persistent
  adverse traits (heavy service use, promotion-only buying, revenue reversals) which cross-buying
  amplifies. For an energy supplier, a household in arrears that takes boiler cover is a second
  receivable, not a second margin.

**Verdict on causality.** Multi-product customers churn less in every source. The careful study
(Prince & Greenstein) finds a real causal component that appears only in turbulent markets. The
GB energy figures (UW, Centrica) are not separated from selection at all. **We cannot yet say how
much of the energy-plus-services churn gap is causal.** A model that wires "holds a second product
→ lower hazard" as a fixed multiplier would be building the selection effect in as a mechanism.

### 3.4 Take-up of the energy-transition products

| product | figure | source |
|---|---|---|
| smart ToU tariffs, GB domestic | 835,000 customers by July 2025 (497,000 a year earlier), **2.8% penetration** | Ofgem, *State of the Market: Energy Retail Highlights*, January 2026 |
| EV-specific smart tariffs | 653,000 (from 354,000, +84%); other smart ToU +27% | same |
| Octopus Intelligent Octopus Go | 278,000 EVs (FY24 156,000) at 30 April 2025, against 6.1m OEL customers. That is vehicles over customers, so it is **not** a take-up rate | Octopus Energy Limited, Annual Report FY2025 |
| Octopus Agile and Tracker | over 100,000 customers | same |
| fixed-term share, GB | about one third by July 2025, twice a year earlier | Ofgem State of the Market, January 2026 |
| fixed-price share, British Gas | 32% at end 2025 (25% end 2024) | Centrica Annual Report 2025 |

**Gaps.** No published per-supplier conversion rate for heat-pump, solar or battery offers to
existing energy customers. No published referral fee or margin a GB supplier earns on an
installation lead. No published churn rate for households that install solar or a battery
against those that do not. The UW EV-tariff sentence is the only sourced statement that kit
drives churn when the matching tariff is missing.

### 3.5 Vendor claims, recorded so they are not mistaken for evidence

Forrester's *Total Economic Impact of Pega Customer Decision Hub* (a vendor-commissioned composite
study) reports a churn reduction of 5%, 10% and 15% in years 1-3. It is commissioned by the
vendor, uses a composite organisation, and is not energy-specific. **It is not an anchor.** It is
recorded here because a search returns it first, and it is exactly the kind of number that
becomes load-bearing by accident.

## 4. The rules: what a GB supplier may offer, to whom, and how

### 4.1 Retention offers: SLC 22B and its market-wide derogation

The Ban on Acquisition-only Tariffs *"ensures that any discounted deals available to a supplier's
new customers are also available to existing ones"* (Ofgem, *Decision: Renewing the BAT after
March 2026*, 13 November 2025, §1.1). It has been extended to **31 March 2027**, with its
Market-wide Derogation. Under that derogation *"suppliers are currently permitted to offer
exclusive 'retention-only' tariffs to their existing customers nearing the end of fixed-term
contracts"* (§3, our proposals (i)). Ofgem received *"no new evidence ... on the Market-wide
Derogation's impact on wider pricing and tariffs"* (§3.6). Suppliers asked for *"clarity on the
types of deals and customers that are eligible for these tariffs"* (§3.7).

**Consequence for NBA:** a *bespoke* retention price is lawful only at the end of a fixed term.
For an SVT customer, the supplier cannot offer a price better than its public tariffs that it
does not also offer new customers. The SVT retention lever is therefore a *conversion* (§1 of
`what_a_conversion_decision_is_at_a_cap_boundary.md`), not a private discount. The NBA action
set is legally **state-dependent**: which actions exist depends on the customer's contract state.

### 4.2 Fairness and vulnerability: SLC 0 (Standards of Conduct)

- Customer objective: each customer is *"treated fairly"* (SLC 0.1). The fairness test asks
  whether an act or omission gives rise to a likelihood of detriment that is not reasonable in
  all the circumstances (SLC 0.9; Ofgem *Standards of Conduct Guidance*, OFG1163, 5 April 2024).
- The information limb requires information that is complete, accurate, not misleading, and
  *"appropriate and fair"* (OFG1163, limbs table, domestic and non-domestic). The non-domestic
  text (SLC 0A.3(b)(iii), quoted in the guidance) requires information that *"relates to products
  or services which are appropriate to the Non Domestic Customer to whom it is directed"*. **The
  domestic SLC 0.3(b) mirror of that sub-paragraph was not read verbatim this pass.** Check it in
  the consolidated licence (S1 of `pricing_differentiation_permissions.md`) before quoting it.
  Read either way, this is an appropriateness test on offers. A heat-pump finance offer to a
  household in arrears, or boiler cover to a tenant whose landlord holds the gas-safety duty, is
  an inappropriate offer before it is an unprofitable one.
- Vulnerability: the supplier must *"seek to identify each Domestic Customer in a Vulnerable
  Situation"* and act taking it into account (SLC 0.3, see the commons register C3). An NBA that
  scores vulnerable customers as sleepy and profitable and therefore leaves them alone is
  precisely the harm the BAT decision names: *"a separate cohort of disengaged, vulnerable and/or
  indebted customers"* (BAT decision, executive summary).
- SLC 25 (informed choices): tariffs must be clear and distinguishable, and the supplier must
  provide tools for each customer to *"compare and select tariffs, taking into account that
  domestic customer's characteristics and preferences"* (Ofgem guide *Tariffs and contracts*,
  updated 21 February 2019).

### 4.3 The analogue that forbids the obvious optimiser: FCA GIPP

The FCA found that insurers *"used complex and opaque pricing techniques to identify the
consumers least likely to switch at renewal based on their characteristics and factored this into
their price-setting"* (EP25/2, *An evaluation of our General Insurance Pricing Practices
remedies*, July 2025). From 1 January 2022 a renewal price may be no higher than the equivalent
new-business price (PS21/5). Evaluation: in home insurance the existing-customer premium over new
business *"almost halved"*, from £95.38 to £49.17. Attrition rose among low-tenure customers and
fell among high-tenure ones. The FCA's projected saving was £4.2bn over ten years.

**This is the closest regulated analogue to an energy NBA that prices on propensity to stay.**
Energy has its own version through the default tariff cap and the BAT. An NBA objective that
rewards extracting margin from low-propensity customers is optimising the thing two UK regulators
have legislated against. The CMA's 2018 loyalty-penalty report sized it at about £4bn a year
across mobile, broadband, home insurance, savings and mortgages (CMA, *Tackling the loyalty
penalty*, 19 December 2018). This is a *transfer*, not value creation, in the mission's terms.

### 4.4 Payment-method and debt actions are partly required, not chosen

- Payment-method price differences must *"reflect the costs to the supplier"* (SLC 27.2A).
- Proactive contact is *required* after two consecutive missed monthly payments or one missed
  quarterly payment (SLC 27.5B). Ability to pay must be ascertained before setting instalments
  (SLC 27.8), and staff incentives must link to *"successful customer outcomes not the value of
  repayment rates"* (SLC 27.8A(a)(ii)). All of these are quoted in
  `pricing_differentiation_permissions.md` C1-C2.
- **Consequence:** in an NBA menu, the debt-support action is a **constraint**, not a candidate.
  When the trigger fires, it must be taken regardless of its uplift score. An engine that ranks
  it against a boiler-cover offer is mis-built.

### 4.5 Contact rules and data rules

- **Renewal notice.** The fixed-term end is a Relevant Contract Change requiring notice *"at an
  appropriate time ... designed to prompt"* a choice (SLC 22C → 31I). The switching window opens
  when the Statement of Renewal Terms is given, or 49 days before term end, whichever is earlier
  (SLC 24.8(b), 24.17). Source and quotation: `what_a_renewal_decision_is_for_a_gb_domestic_customer.md`.
- **Electronic marketing (PECR reg. 22).** Email or SMS marketing to individuals needs consent,
  except under the *soft opt-in*: details were obtained in a sale, the marketing is for
  *"similar products or services"*, and an opt-out was offered at collection and in every message
  (ICO, *How do we comply with the PECR electronic mail marketing rules?*). Whether boiler cover,
  broadband or a heat pump is "similar" to an energy supply is **not settled by the guidance**.
  On a plain reading, energy tariffs are covered and unrelated products may need fresh consent.
  **That is an interpretation, not a ruling.** It means that for cross-sell, the *reachable*
  population is smaller than the customer book.
- **Smart meter data (SLC 47, the Data Access and Privacy Framework).** Suppliers may use up to
  daily consumption data unless the customer opts out. Half-hourly ("detailed") data needs opt-in.
  **Using consumption data of any granularity for marketing requires explicit consent.** Sources:
  Ofgem's 2014 final proposals on extending the framework; Ofgem's 2022 decision modifying
  SLC 47; and DESNZ's *Review of the Data Access and Privacy Framework* (March 2024). This repo's
  `smart_meter_hh_data_consent_2026.md` covers the settlement side. **This is the single most
  important wall-adjacent rule for NBA.** A supplier may *see* a daily profile that looks like an
  EV charging at night, but it may not *use* that inference to market an EV tariff without
  marketing consent.
- **Boiler cover sold as insurance** is FCA-regulated insurance distribution, and the FCA's
  Consumer Duty (PS22/9, in force 31 July 2023) applies to it. Whether the GIPP pricing remedy
  covers home-emergency cover specifically was **not established this pass**.
- **Bundles.** The RMR "simpler tariff" rules that banned most bundles, discounts and the
  four-tariff limit were removed in 2017, following CMA recommendations (Ofgem statutory notice,
  August 2016). Bundled products are now allowed, subject to SLC 0 and SLC 25.

## 5. What a real supplier SEES that NBA can use (the epistemic wall)

**Seen by right (its own records):** contract state, tariff and fix end date; payment method and
payment history; arrears and repayment plans; meter type and, by default, up to daily smart reads;
contact history and complaints; the PSR flag and declared vulnerabilities; products it has sold
the household; its own offers made and their outcomes.

**Seen only with consent:** half-hourly consumption; *any* consumption-derived inference used for
marketing; electronic marketing for dissimilar products.

**Seen only by asking, or bought:** whether the household owns an EV, solar, a battery or a heat
pump (except where it is on an EV or export tariff, or registered for SEG with the supplier);
tenure (owner or renter); household composition; income.

**Never seen:** a competitor's offer to this household; the household's intention; its
counterfactual (what it would have done without the contact). **The counterfactual is never seen
by anyone.** It can only be estimated from a holdout, which is why the holdout must be a decision
the company makes and logs.

## 6. What our code does

*(Code census of `company/`, `saas/`, `simulation/`, `sim/` and `tools/`, read 2026-10-05.)*

**Verdict first.** No next-best-action engine exists. There are four pieces of one, and none is
complete. One decision is computed per customer and is opt-in (renewal margin). One multi-action
selector exists and is unwired. One per-customer randomisation exists, and it randomises *how* to
say something, not *whether* to act. The world responds to exactly one kind of offer (a renewal
or retention price), and that response cannot be negative.

### 6.1 Company side: what chooses an action

| path | what it does | per customer or lookup? | live? |
|---|---|---|---|
| `company/pricing/value_based_renewal.py` (`decide_margin`, `renewal_margin_uplift`) | searches renewal margins to maximise P(stay given margin) × contribution × lifetime annuity, from the company's own churn estimate, CLV horizon, cost to serve and payment history | **per customer**, continuous | opt-in arm only (`DecisionPolicy.renewal_margin_arm="value_based"`); the default is a flat margin |
| `company/policy/decision_policy.py` `retention_discount_for_risk`, `CURRENT_POLICY.retention_tiers` | churn estimate ≥0.75 gets 8%, ≥0.50 gets 5%, ≥0.30 gets 3% | **lookup** on predicted **risk** | yes, the default |
| `simulation/run_phase2b.py` ~L2703-2760 | offers the tiered discount when `company_est_pre > RETENTION_THRESHOLD` (0.30) and expected margin plus acquisition cost saved exceeds `discount_pct × term revenue` | targets on **propensity** | yes |
| `company/crm/customer_retention.py` `_choose_offer` | a true multi-action tree: `LOYALTY_DISCOUNT`, `TOU_REFERRAL` (EV owner under rate shock), `DUAL_FUEL_BUNDLE` (cross-sell the missing fuel), `PRICE_MATCH`, `ACCOUNT_REVIEW`, `NO_OFFER`; spend capped at 50% of net margin | rule tree on risk driver | **no production caller** |
| `company/crm/switching_cba.py` | per-account ROI to `RETAIN_WITH_OFFER / RETAIN_PASSIVELY / LET_GO / REFER_TO_COMMITTEE` | per customer, threshold | **no production caller** |
| `company/pricing/tou_desk.py` `decide_tou_offer` | the ToU rate pair offered to a smart-eligible account | per product, not per customer | yes |
| `company/billing/arrears_engine.py` `current_dunning_step`, `collections_journey.py` | dunning step keyed on segment and days overdue | **lookup**, takes no account id | yes |
| `company/policy/decision_policy.py` `framing_type_for`, `tone_for` | hashed per-customer A/B of comms framing (loss or gain) and dunning tone | **randomised per customer**, the only one | yes |
| `company/comms/susceptibility_estimator.py`, `company/analytics/nudge_discovery.py` | learn from observed outcomes which framing lands, by segment, with a Consumer Duty fairness check | learning layer | reads the live retention log |
| `company/analytics/counterfactual_retention.py` | scores offers *not* made, with cost correctly shaped as margin given up (`discount_pct × term revenue`) | analytics | reporting |
| `company/crm/ancillary_products.py` | enum of `BOILER_COVER`, `EV_TARIFF`, `SMART_HOME_CONTROLS`, `HOME_INSURANCE`, `BROADBAND`, `CARBON_OFFSET`, `SOLAR_MONITORING`, with flat monthly revenues £18, £0, £5, £32, £28, £3, £4 | none | **zero callers**; revenues carry **no origin** |
| `company/crm/contact_journey.py` | contact attempts, channel cost (`_CHANNEL_COST_PENCE`, phone 350p), opt-outs | none | **zero production callers** (already recorded in the knowledge map) |
| `company/crm/dual_fuel_account.py`, `account_hierarchy.py` | `is_dual_fuel` / `is_electricity_only` | | yes; **the only product-holding concept on disk** |

`tools/decision_probe.py` is the most important asset for NBA, and it is not an NBA. At each
renewal it asks six pricing rules what they would charge *this* customer *now*, then asks the
world for its **true** P(stay) at each offer, holding household, market and history fixed. That
is a **ground-truth uplift oracle**: the harness can read each customer's real counterfactual,
which no real supplier ever can (§5). It is confined to one decision (the renewal rate). It is
also exactly the instrument needed to *grade* an uplift model, because the company's estimate can
be scored against the truth decision by decision. That makes it the strongest evidence for the
mission's third point: the method is the asset.

**C34's decision rule, and the choices it makes (amended 2026-10-12, canon v4 C7).**
`company/crm/next_best_action.py` ranks on JOINT value: the household's benefit over the horizon
plus our forward-value change, with a no-loss floor on both sides. The director ruled this; no
published source sets a supplier's ranking key. The design makes three choices, and each one is ours:
- **The household's benefit over the horizon is its yearly benefit x horizon/12.** It is
  undiscounted, like B11's forward value. It is not weighted by the account's survival, because
  advice keeps paying the household after it leaves us. **GAP:** no published source says how long
  a household keeps the benefit of supplier advice.
- **Our floor is "our forward value does not fall".** Our side is not "joint value exceeds what we
  give up".
- **The flat baseline faces the same floors, on the book's means**, so it cannot win by sending an
  action that loses us money.
Measured at B11-scale inputs (margin GBP 5-30/month, hazard 0.5-3%/month, 48 months, advice giving
up GBP 2-3/month and cutting the hazard 0.1-0.3 points), joint value is positive in all 18 cells
(+GBP 13 to +107). Our side is negative in all 18, so the rule chooses nothing in all 18: the floor
on our side binds. Whether a positive-sum action that costs us should be paired with a price that
shares its value is the director's question (M2: created, then shared).
The published evidence on how such a share is priced (2026-10-14) is in
`how_a_supplier_prices_a_share_of_value_it_creates_for_a_household_2026-10-14.md`:
- **The licence is silent on a savings-share fee.** SLC 0.6 does not bound a fee's amount.
- **The binding constraint is consumer credit** if the share is recovered by instalments
  (the Green Deal precedent).
- **The one computable GB energy split** is Octopus's Demand Flexibility Service test events:
  75% passed to households, 25% retained (Octopus's own account).
- ECO is the opposite polarity: the supplier funds the measure and the household keeps the
  whole saving.
- No GB supplier publishes an advice-savings-share scheme.
It ranks five pricing shapes by evidence and recommends none. The decision stays the director's.
The other shape, a rise in the retention price itself, is measured over these 18 cells in
`a_retention_price_that_shares_the_value_an_action_creates.md` (2026-10-16). As a Fixed Retention
Tariff (lawful in form, depth unregulated) it brings our side to zero in 18 of 18 holding the hazard;
10 of 18 once the rise's own effect on staying is added at the published slope; 0 of 18 on a default
tariff priced at the cap.

**Where a real supplier makes this decision: at the renewal notice (amended 2026-10-19, K8 for the
engine caller of C34).**
- **The rule.** The end of a fixed term is a Relevant Contract Change. SLC 22C.3 → 31I.1(c), 31I.2
  require notice "at an appropriate time … designed to prompt" an informed choice. The old fixed
  42–49-day rule became this principle in Ofgem's 2018 customer-communications decision
  (`what_a_renewal_decision_is_for_a_gb_domestic_customer.md`, table row "Notice before the term
  end").
- **Why the decision sits there.** The notice is the one contact every fixed-term household must
  receive. It already carries the renewal price. A bespoke retention price is lawful only at the end
  of a fixed term (§4.1). So the notice is where a supplier decides whether to add advice and what
  to charge for the fix.
- **A dual-fuel household gets one notice.** It may be a combined notice for both fuels (SLC
  31I.5(b)), so the decision is the household's, not one per fuel.
- **What it may read there.** Only its own records (§5, "seen by right"):
  - the renewal price it is about to offer, and its own forward cost for the term;
  - its own consumption estimate for the account;
  - its own churn belief for this renewal, built from tenure, rate change, payment history,
    arrears, satisfaction and payment method;
  - the published default for the fuel.
- **What it may not read.** It never sees the household's own probability of staying, a
  competitor's offer to the household, or the counterfactual.

**What the engine caller does, and the choices it makes (2026-10-19).**
`company/interfaces/renewal_advice.py` is the caller, behind `DecisionPolicy.next_best_action_decides_at_renewal`
(default False). It decides at each domestic renewal roll on the leg that carries the household's
departure. When the same account's other leg is priced on the same start date, that leg joins the
decision. The legs are decided per household through `states_for_decision`. The design makes five
choices, and each one is ours:
- **The hazard is the company's own renewal churn belief** (`estimate_renewal_churn`, the same
  belief the retention guard reads), spread as a constant monthly hazard over a 12-month term:
  `h = 1 − (1 − p)^(1/12)`. This is B11's shape. It is never the world's roll or its P(stay).
- **The margin is the term's contribution, per month (amended 2026-10-20).** It is
  [(offered rate − the term's own pre-margin cost) × the company's consumption estimate − the
  company's cost to serve that leg for a year] / 12.
  - The pre-margin cost is `renewal_desk.pre_margin_unit_rate`: the company's forward, plus
    capital, plus the policy and network costs locked into this term. The value arm and the
    discount floor already measure a margin from it. Every one of those components is a
    pass-through the household's unit rate recovers, and none is ours to keep.
  - Cost to serve is `saas/cost_to_serve.FIXED_OVERHEAD_GBP_PER_YEAR` for the segment, per leg.
    That is the same basis the settled book charges each fuel's records.
  - Where the term does not record its locked costs, the leg has no contribution and is counted,
    not guessed.
  - *Corrected beside the claim:* until 2026-10-20 this bullet said "the margin is the one the
    retention guard already uses: (offered rate − the term's company forward) × consumption".
    That is the spread over wholesale. It still carries network, policy and capital, and it is
    not a margin. On the r4 on-arm run its median was GBP 29.7/month. No row at GBP 30 or less
    was advised, so it, not the churn belief, put 11.1% of rows over the floor
    (`SEAT_FINDING_C34S_RENEWAL_MARGIN_IS_THE_ALL_IN_RATE_LESS_THE_WHOLESALE_FORWARD_SO_IT_IS_NOT_A_MARGIN_2026-10-20.md`).
    At the strike's own TARGET margin of GBP 2/MWh the unit leg keeps about GBP 0.52/month on
    3.1 MWh. Where nothing upstream moved the strike, the contribution is therefore about
    −GBP 4/month per leg.
  - **The standing charge is left out, and that is a GAP, not a zero.** Ofgem's cap model builds
    the standing charge as the nil-consumption allowance. Since the TCR it carries the network
    residual the unit rate no longer does (knowledge map, "Cap formula" and "Network charges").
    The world's standing-charge table rises from 23.6p/day in 2021 to 50.1p in 2023, but its
    per-MWh network table never gave the residual back. Crediting the whole standing charge would
    count network twice and would rebuild most of the old margin from 2023 on. How much of the
    standing charge a supplier keeps (opex and EBIT, against metering, network and policy) is not
    decomposed anywhere in the commons. Leaving it out errs against our own thesis (F11): it
    understates what retaining a household is worth to us.
  - **The retention guard reads the same contribution, per year (amended 2026-10-20, second
    landing).** What a retention offer protects is what the retained term contributes, so the
    guard's `expected_margin` and the missed-retention log's `expected_term_margin_gbp` are
    `term_contribution_per_year`; C34's monthly value is that over 12. One function feeds all
    four sites, and the run computes no spread over the company's forward anywhere.
    The hedge's `cost_per_mwh` is a cost, not a margin, and is unchanged.
    - The value weighed against a cut is the contribution plus the replacement spend avoided
      (`replacement_cost_avoided_gbp`). An offer survives only where an upstream writer raised the
      strike above its cost, or on a very large account.
    - *Corrected beside the claim:* until this landing the bullet said the guard weighed
      `(unit_rate − company_fwd) × EAC`. On the published 19 Oct book that read a median of
      GBP 290 a year over its 92 offers; the contribution reads −GBP 31. The cut is floored at
      cost, and the spread always exceeded it, so the guard could never refuse on value. It is the
      default policy, and the offer count is pre-registered at
      `records/SEAT_PREREG_THE_RETENTION_GUARD_ON_THE_TERMS_CONTRIBUTION_2026-10-20.md` (3–30).
- **The advice effect is unknown, so the caller decides under each of the three stated effects**
  of `a_retention_price_that_shares_the_value_an_action_creates.md` §4. Each run writes one row per
  household per effect. The company's own holdout cannot decide an effect at this book size (§6.2:
  681 default-tariff accounts against about 6,000 needed). So these rows are a decision under a
  stated range, not under an estimate. That is said on every row.
- **It records and does not act.** No letter is sent and nothing reaches the world. Off, the run
  is unchanged to the byte. On, it adds one list to the run output.
- **A household that leaves at the roll never prices its other leg, so it is decided on one leg.**
  The world prices the second leg only after the roll. The row says how many legs it carries.

**C35 at the renewal notice (amended 2026-10-20, K8 for C35's engine caller).** The rise on the fix
(`next_best_action.price_retention_rise`; `a_retention_price_that_shares_the_value_an_action_creates.md`
§4c) is priced at the same notice by the same desk, behind the rise's own switch,
`DecisionPolicy.next_best_action_shares_by_retention_rise` (default False). The design makes five
choices, and each one is ours:
- **No second margin.** The rise is priced against the margin C34 already decides on: the term's
  contribution above, through the run's one helper. A margin of its own would be a fifth
  implementation of one quantity.
- **What the notice adds is the room under the default.** Each leg carries its renewal terms: the
  fix as offered (ex VAT), the published default for its fuel on the start date (ex VAT, the price
  match's reading), and the company's own annual volume. The headroom is
  (default − offer) × volume / 12. A stayer offered a fix dearer than the default takes the default
  instead (§4a of that page). So the rise cannot exceed this headroom.
- **A dual household's room is both legs'.** One notice may carry both fuels (SLC 31I.5(b)). The
  rise is the household's, so its room is the sum of each leg's headroom under its own fuel's
  default (`HouseholdRenewalTerms`). It is unknown if either leg's is unknown. The gas leg's
  margin already rides with the household (C34 above). C35 adds its headroom.
- **Before 2019 the rise is refused, and the row says so.** No per-fuel default was published
  before the cap of 1 January 2019, so the headroom is unknown. It is not zero, and it is not the
  standard variable tariff. The rise is refused with that reason.
- **The rise switch on with C34's caller off is refused by the run.** Otherwise it would be
  ignored, with no engine path and no byte moved.

**Measured before the build (2026-10-20), on the input only.** On the 19 Oct published book
(`run_output_ad8afadc5`), the headroom of fixed terms under the published default ex VAT has a
per-leg median of about GBP 8–9/month in 2019–2020, and 86–100% of legs have at least GBP 2. It
falls to about 0–2 in 2021–2022 and recovers to about 3–9 from 2023. The rise our side needs on the
corrected contribution (about −GBP 4/month per leg) is about the advice's own give-up, GBP 2–3.3
a month. So the room binds in 2021–2022 and mostly does not in 2019–2020.

GAP, unchanged: the headroom counts the unit rate only. The fix's standing charge against the
default's is not compared, for the same reason the contribution leaves it out.

GAP: no published source gives how a supplier's advice at the renewal notice moves P(stay) or what it
gives up. This is §7 gap 1, unchanged.

### 6.2 What the company knows about uplift

**Only propensity.** Every churn quantity on the company side is P(leave), or P(leave given a
rate). Nothing estimates the *incremental* effect of making an offer against not making one. No
per-customer holdout on *whether* to offer exists. The whole-book A/B tools
(`tools/run_value_cycle_ab.py`, `run_price_ladder.py`, `run_frozen_baseline.py`) compare policy
arms, not treated against untreated customers. Atom `B8_discovered_price_sensitivity_holdout`
(level 0, idle) names this gap. Its `real_world_twin` says the honest suppliers *"run a holdout so
they can tell whether the retention campaign did anything at all"*.

**The default retention rule targets on risk.** It is the rule Ascarza (2018) tested and found
inferior to targeting on lift.

**Three uncited effectiveness constants, one of them on both sides of the wall:**
- world, `simulation/run_phase2b.py:369`: `RETENTION_EFFECTIVENESS = 0.20`; *(corrected 2026-10-09:
  retired. The world now answers an offer at the offered rate on the household's own roll,
  `simulation/retention_offer.py`; the two company constants below stand.)*
- company, `company/analytics/counterfactual_retention.py:51`: `_RETENTION_EFFECTIVENESS = 0.20`
  (marked UNSOURCED in its own comment);
- company, `ASSUMED_EFFECTIVENESS_PER_DISCOUNT_POINT = 0.04`.

The world and the company hold the same literal. **I cannot yet say** whether that is a
coincidence or a copy. Either way, the company's estimate of what an offer does equals the
world's truth by construction, so any analytics built on it cannot be surprised. That is worth a
look by whoever owns the wall.

**C34's first uplift input (2026-10-16): an action's hazard effect read from the company's own
holdout.** `next_best_action.hazard_estimate_from_holdout` takes coin-drawn rows for one action
(contacted against held out, and who was still supplied at the end of the window). It runs B8's
interval (`discovered_price_sensitivity.estimate_offer_effect`, Newcombe, 95%) and converts both
stay shares to a monthly hazard over the window. The design makes three choices:
- **Only the interval's verdict sets the number.** A holdout that cannot tell gives `None`, with
  the interval as the reason, so the action stays unscored. A point estimate is never ranked when
  its interval spans zero. A holdout that says the contact *lowers* staying gives a positive
  hazard change. Our floor then refuses the action, so the world can defeat it (sleeping dogs,
  §2).
- **The hazard is constant over the window:** `h = 1 - s^(1/w)`. This is B11's shape, and it is a
  choice. No published source gives the month profile of a contact's effect (gap 3 is the nearest).
- **One estimate covers every account the holdout covered.** Per-account variation in the decision
  comes from each account's own margin and hazard, not from the uplift. Splitting the uplift by an
  observable needs its own power.

Printed at real inputs: a 2-point stay effect over 12 months is about 0.002/month of hazard.
Deciding it needs about 3,000 accounts per arm (800 decides 4 points, 200 decides neither).
**I cannot yet say** whether a run's default-tariff stock is that large. No run yet holds out the
W2_39 contact (`DecisionPolicy.svt_contact_instrument` writes to everybody), so the function is
dormant. *(Measured 2026-10-17: it is not. The
published run, `bdd6d1657`, 2016 to June 2025, holds 681 distinct default-tariff accounts in the whole
decade, against about 6,000 needed. See "The window the holdout reads" below.)*

**The run can now hold the contact out (2026-10-16).** `DecisionPolicy.svt_contact_holdout_share`
keeps that share of default-tariff accounts out of the W2_39 letter. The coin is the company's own
(`next_best_action.in_contact_holdout`), and the design makes three choices:
- **One draw per account, held for the run**, as a real holdout group is. A sha256 of run and
  account, not a random stream, so it takes none of the world's draws and the uncontacted roll of a
  held-out account is the one it always was.
- **Each account counts once, at its first assigned segment** (`holdout_observations`). Its later
  segments share its arm, so they are not independent draws.
- **The share is the experiment's to name.** No standing policy sets it. No published source gives
  a supplier's holdout share; the size that decides a 2-point effect (about 3,000 a side) is the
  constraint, not a number to borrow.
The door is wired but no run has used it yet, so the level stays at 1.

**The window the holdout reads (2026-10-17).** The reader and the door did not share a window.
`holdout_observations` graded each account over its *first* segment, which in the published run is
a median of 43 days and differs from account to account. `hazard_estimate_from_holdout` converts
every row with one `window_months`. Paired at 12 months, that would have understated the hazard
about eightfold. The reader now takes the same `window_months` and grades a fixed window: an
account stayed if no departure is dated within that many months of its first assigned segment.
An account whose window runs past the last date the run observed is dropped, because the company
cannot yet see whether it stayed. A loss is dated at the segment the departure was rolled on,
which is what the company books.

Printed on the published run (`bdd6d1657`), with each account's first segment as its start:

| Outcome window | Accounts with the whole window | Baseline loss | Smallest effect a 50% holdout decides (80% power) |
|---|---|---|---|
| first segment (median 43 days) | 681 | 2.6% | 3.4 points |
| 12 months | 651 | 17.2% | 8.3 points |

The first segment's 3.4 points is a large effect on a 43-day window: it means more than doubling
the loss. Over 12 months, 8.3 points is about half the baseline. §3.1's randomised trials move
engagement by low single figures. **So at the run's book size the holdout returns `None`, which is
the right answer**: a real supplier with 681 default-tariff accounts could not tell either. The
book, not the instrument, is what has to grow. Five seeds at this size would pool about 3,400 accounts, but
the pooled estimate is an instrument reading across worlds, not something one company could know.
It can grade whether the door reads the truth. It cannot be a decision input. As a placebo, a 50% coin laid over the published
run's rows, where nothing was sent and the true effect is zero, gives the door "spans zero" at both
windows: [-3.2, +3.0] points over the first month, and [-9.6, +2.0] over 12 months (353 contacted,
298 held out).

### 6.3 World side: how households respond to offers

| offer | world response | where |
|---|---|---|
| renewal rate | stay or leave, a function of the struck rate against the default and the market | `simulation/customer_events.py` `roll_lifecycle_event`, `renewal_outcome`, `position_vs_default` |
| retention offer | churn probability × (1 − min(0.95, 0.20 × framing multiplier)). The framing multiplier is 1.0, or 1.10-1.35 when framing matches the hidden susceptibility (`simulation/nudge_physics.py`, `_MATCHED_FRAMING_UPLIFT_RANGE`) | `run_phase2b.py` ~L2729, `customer_events.py` ~L1003 |
| active versus passive renewal | a dice roll | `simulation/renewal_engagement.py` |
| repayment plan | accept, afford, keep or miss; `PUBLISHED_BASIS` is `None` throughout | `simulation/plan_offer_response.py` |
| market shopping | population elasticity to savings available | `simulation/market_switching_propensity.py` |
| EV, solar, battery, heat pump, boiler replacement | **exogenous life events and national S-curves, never a response to an offer** | `simulation/life_events.py`, `simulation/adoption_geography.py` |
| boiler cover, broadband, insurance, any non-energy product | **no world counterpart at all** | — |

Read against §2-§3, the retention response has three properties the published record
contradicts:

1. **It cannot be negative.** The modifier is always between 0.20 and 0.27, so the world has no
   sleeping dogs. Ascarza et al. (2016) measured a proactive "better plan" contact raising churn
   from 6% to 10%. Ofgem's CMOL and EFTC trials show a prompt raising *all* switching, external
   included.
2. **It does not depend on the size of the offer.** A 3% and an 8% discount buy the same 20%
   hazard cut. The cost side scales with the discount and the benefit side does not, so the
   cheapest tier always dominates on uplift per pound. That is an artefact, not a finding.
3. **It has no memory.** Activation does not persist. Ofgem's 2020 follow-up shows trial-induced
   switchers re-switching at 63% against 33%.

So **an NBA engine built today would be optimised against a world that cannot defeat it**
(`tests/test_coupled_triad_gate.py` is the rule this would violate in spirit). Any uplift model
would learn "uplift is uniform, positive and size-free", and that would be true of this world
and false of the real one.

## 7. Gaps

**Published-evidence gaps (open, not invented):**
1. The uplift of a supplier's *own* retention offer to its *own* customer at fixed-term end. No GB
   figure. The nearest is the Ofgem EFTC trial (+9 pp, all switching), which measures the opposite
   direction.
2. Uplift as a function of discount depth. No published GB source. Ofgem's BAT decision §3.6
   records that no evidence on the derogation's pricing effect was presented to the regulator
   either.
3. Energy-specific contact-fatigue elasticity.
4. The causal share of the multi-product churn gap in GB energy. UW and Centrica publish levels
   only, with selection unseparated.
5. Conversion rates and supplier economics for heat-pump, solar and battery offers to existing
   customers, and churn after kit installation.
6. The overlap of British Gas energy and Home Services customers.
7. The numeric effect sizes in Ascarza (2018), unread (publisher 403).
8. Whether the PECR soft opt-in covers cross-sold non-energy products from an energy supplier, and
   whether GIPP pricing rules reach home-emergency cover. Both need a practitioner or legal read.
9. The verbatim domestic SLC 0.3(b) appropriateness sub-paragraph (§4.2).
10. Per-contact cost by channel. Already open in the knowledge map; not repeated.

**Code gaps:**
1. **No uplift estimate and no holdout** on whether to act (B8, idle). Propensity is used where
   uplift is needed.
2. **No action menu.** The one multi-action selector (`customer_retention._choose_offer`) is
   unwired. The live path has one action (a discount tier) or nothing.
3. **No product holding** beyond dual fuel. No record of a household holding energy plus anything
   else.
4. **`ancillary_products.py` is a catalogue with invented prices and no callers.** The same shape
   as the £150 CAC. Its `_MONTHLY_REVENUE_GBP` figures should carry `None` with a named reason, or
   be removed, before anything reads them.
5. **No consent state.** Nothing records marketing consent, SLC 47 data-use consent or PECR
   opt-outs, so the reachable population for cross-sell cannot be computed.
6. **No contact budget or fatigue.** Actions do not compete for a slot.
7. **Debt contact is not modelled as a constraint** that pre-empts every other action when SLC
   27.5B fires.

**World gaps (what households would need to respond to offers credibly):**
1. A retention-offer response that **depends on offer size**, **can be negative** (contact raises
   salience and therefore external switching), and is **heterogeneous** across households, so
   persuadables, sure things, lost causes and sleeping dogs all exist.
2. **Persistence**: a household that has been activated stays more active.
3. **Product adoption as a response to an offer**, layered on the existing exogenous life events
   (`ev_acquired`, `solar_install`, `heat_pump_installed`, `battery_installed`). The life event
   is the *moment*; the offer changes what happens next: the tariff taken, whether they stay,
   whether the install happens through us.
4. **A churn response to a missing product**: an EV owner without a fitting tariff (UW's own
   stated cause) is at raised risk.
5. **No world model for non-energy products** (boiler cover, broadband) until evidence exists. An
   invented one would be the selection effect wired in as a mechanism (§3.3).

## 8. What this says about the order of work

The canon places per-customer decisions (step 4) before the levers (step 5), and says step 4
"touches acquisition, dunning and retention, so most later levers rest on it". What the evidence
here says, in order of weight:

**1. Step 4 must precede NBA, and that holds. But step 4 as currently framed builds the wrong
quantity first, and the world beneath it cannot yet tell the difference.** NBA is per-customer by
definition (§1), so it cannot come before per-customer decisions. C29's map row (`block_reason`, pointing at
`docs/design/C29_DECISIONS_STOP_BEING_LOOKUP_TABLES_DISCOVER_FRAME.md`) says its *"first BUILD is
a per-account engagement estimate"*, which is a propensity. Built on propensity, per-customer
retention becomes "target the most at risk", which is the rule the field experiments found
inferior (Ascarza 2018) and sometimes harmful (Ascarza et al. 2016). And because the world's
retention response is uniform, positive and size-free (§6.3), a propensity-targeted rule and an
uplift-targeted rule would score *the same* here. Step 4 would land, look right, and teach
nothing.

**Proposed change (raise it, carry on): split a world item out of step 4 and put it first. Call
it "households respond to contact, including badly".** That means a size-dependent,
heterogeneous, possibly negative retention response, with persistence, keyed to the fixed-term
end the law and the trials both point at. Then pair `C29` with `B8` (they are already
`couples_with`) so that the first per-customer *decision* is graded on uplift against
`tools/decision_probe.py`'s true counterfactual, not on propensity. Evidence: §2 (Ascarza 2016,
2018), §3.1 (Ofgem trials, both directions, persistence), §6.3 (the three properties). The cost
is a world change made for fidelity reasons, which the baseline/curriculum split permits. It must
be decided blind to company results, and the sources above are external.

**2. Inside step 5, the value-add levers should be re-ordered by what the world and the law can
already carry.**
- **First: EV and smart-ToU tariff upsell at the adoption moment.** It is in-licence (no second
  regulator). It has sourced take-up (653k EV tariffs, +84% a year, Ofgem January 2026). It has a
  sourced churn cost of *not* offering it (Telecom Plus FY2025). And the world already generates
  the moment (`ev_acquired`, `solar_install` life events) and the tariff (`tou_desk.py`). It
  creates value on both sides (cheaper charging; load shifted to cheap hours), which is the
  mission's test, and it touches carbon.
- **Second: retention at fixed-term end, uplift-targeted**, once item 1 is in.
- **Third: solar, battery and heat-pump leads and ROI cases.** The moment exists in the world; the
  conversion and economics are open gaps (§7 published-evidence gap 5).
- **Last: boiler cover, broadband and other non-energy cross-sell.** No world, causality
  unestablished (§3.3), a second regulator (FCA for insurance), and a consent-limited reachable
  population (PECR, SLC 47). Shah et al. (2012) warn the cross-buyers can be the loss-makers. This
  is the lever most likely to produce an impressive number that is a transfer or a selection
  artefact.

**3. Debt-support contact does not wait on NBA.** It is a licence-required action at a computable
trigger (SLC 27.5B), not a candidate in a ranking. Step 5's first lever (debt) therefore does not
depend on an NBA engine. It needs only the trigger and a rule that it pre-empts other contact.

**4. Knowledge still owed before any NBA build**, cheapest first: per-contact cost (already open);
a practitioner read (the director) on whether GB suppliers actually run holdouts on retention
offers, and on PECR "similar products" in practice. Both are *too obvious to anyone in the trade
to be written down*, which is the third side of knowledge.
