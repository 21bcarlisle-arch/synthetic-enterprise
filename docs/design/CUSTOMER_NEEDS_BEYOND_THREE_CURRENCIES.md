# Customer needs beyond three currencies: cost, cash flow, certainty, control, time, carbon, above a comfort floor

**Status: DISCOVER/FRAME, reading-only; no build until the correctness exit test.**
Written 2026-10-30 for the steer `DIRECTOR_STEER_FRAME_THE_CUSTOMER_NEEDS_COST_CASH_FLOW_TIME_CARBON_PEACE_OF_MIND_2026-10-30` (Ask 1).
Style follows `docs/design/C31_TIME_AS_A_CURRENCY_DISCOVER_FRAME_2026-10-04.md`.
This note proposes no canon change. The M3 wording proposal is the `for_the_director` row in `docs/direction/DIRECTION.yaml` raised with it. Only the director edits canon.

**Epistemic note.** I read published sources and `docs/market_research/` only. I did not read any simulation or company code. Where this note says "the world should hold X", that is a design statement from the steer, not a finding about what the code does today.

**Labels.** H = authoritative published document I opened. M = several sources agree. L = one source or indirect. **GAP** = I could not source it from a document I read. No GAP has a number guessed in its place.

---

## 1. What the thing is, before anything is measured

The question is whether money, time and carbon (canon M3) are the whole set of things energy products serve. The steer suggests not. Some real behaviour is not explained by them:

- paying more by standard credit (SC) or prepayment (PPM) when a direct debit (DD) discount exists;
- fixing at a price above the expected variable price;
- accepting a level DD that builds summer credit.

"Needs" here means **what a household is trying to get from how its energy is priced, billed and paid for**. It splits into seven. Each has its own population, trigger and remedy, so each is defined and measured on its own, as CLAUDE.md's bill-shock rule requires.

| Need | One-line definition | Who meets it hardest | Who controls it |
|---|---|---|---|
| **N1 Cost** | the total paid over a period for the energy and service received | everyone; hardest at low income | the market, the cap, our procurement |
| **N2 Cash flow** | *when* money leaves and *how much at once*, against when income arrives | households with a small buffer or irregular or short-cycle income | **us**: DD date, DD cadence, DD sizing, refund speed |
| **N3 Certainty** | not being surprised: bill size, price change, supplier failure, a switch going wrong | anyone, but costliest for those with no buffer | **us** (fix, smoothing, notice) and the market |
| **N4 Control** | seeing and deciding when money leaves; no debt building; the supplier not reaching into the account | PPM and SC payers, people who distrust a mandate | **us**: payment options, visibility, who can adjust a DD |
| **N5 Time** | household minutes by activity class (C31, T1-T4) | everyone | **us** for T2-T4 |
| **N6 Carbon** | CO2 saved or avoidable (canon CO1) | the engaged, the smart-meter homes | **us** and the grid |
| **Floor: comfort and health** | warmth and supply above safe levels | the vulnerable | a constraint on every decision, not a trade |

Two splits matter most.

**Money splits in two.** N1 and N2 are different experiences. A household can pay the lowest total and still be hurt by timing. A DD that lands before payday can trigger bank charges. Those can outweigh the DD discount. Section 2.2 shows what the record can and cannot say about that.

**Peace of mind splits in two.** N3 and N4 are related but not the same.
- N3 is the wish to avoid a bad surprise. People pay to avoid it.
- N4 is the wish to decide for yourself. Some people accept more cost and more risk of running out to keep it.
- A smart PAYG customer with budget alerts has high control and, perhaps, low certainty. A fixed-price level-DD customer has the reverse. One "peace of mind" number would hide that.

Comfort and health stay a **floor** (steer, 25 Oct; `docs/market_research/heating_behaviour_comfort_and_health_floors_2026-10-25.md`). Warmth above safe levels is not traded away for money. It is a veto on a decision, not a unit in a score.

**What "deliberate" means.** A payment method is *deliberate* if the household gives an active reason for it, such as convenience, budgeting or control. It is *imposed or passive* if the reasons are default, supplier action, landlord, or not knowing how to change. A choice can be deliberate and uninformed. That is the sense the record can speak to (section 2.1).

---

## 2. What the published record establishes

### 2.1 Payment method: how many choices are deliberate, and why

**Ofgem Consumer Impacts of Market Conditions (CIM), Wave 3, fieldwork Nov-Dec 2022** (H; I read the report PDF and checked the quoted rows). Bases: DD 2,498; SC 414; PPM 553.

| Reason given for the method (multiple answers allowed) | DD | SC | PPM |
|---|---|---|---|
| More convenient | **49%** | 36% | 25% |
| Easier to budget | 43% | 31% | **42%** |
| Gives me more control | 26% | **41%** | 33% |
| Cheaper than other methods | 24% | 14% | 10% |
| It was the default | 12% | 11% | 22% |
| My supplier made me | 7% | 10% | 11% |
| Don't know how to change it | 3% | 4% | 7% |
| Landlord's decision | 0% | 0% | 1% |
| **At least one active/positive reason** | **89%** | **85%** | **72%** |
| **At least one passive/negative reason** | 20% | 24% | **36%** |

What this says:

- **Most people on every method give an active reason.** Even on PPM, 72% do. The simple story, "SC and PPM are all inertia or compulsion", is wrong.
- **The active reasons differ by method.** DD is convenience. SC is *control*. PPM is *budgeting* (and control). That matches N2 and N4. It is the best direct GB evidence that control and cash-flow management are real reasons, not noise.
- **Price is a minor reason.** Only 24% of DD users, 14% of SC users and 10% of PPM users say cheaper. Ofgem's own conclusion (standing-charge decision, 23 Feb 2024, para 3.19): *"price is not a key driver for payment method choice, in fact the majority of customers are unaware that price varies between payment method."*
- **A deliberate choice is not an informed one.** Only 55% know costs vary by method (CIM Wave 3). A repo page cites 43% of SC customers knowing SC costs more than DD (`payments_and_direct_debit_2026-10-25.md` s.5, via Fair By Design quoting Ofgem). Those who do know are less satisfied (CIM Wave 3). So few SC payers *knowingly* buy control at the price. The SC premium in 2025 is **+£131 a year** against DD on a dual-fuel cap bill (DESNZ QEP Dec 2025, in `gb_payment_method_migration_rates.md` s.3).
- **Contentment is high but lower off DD.** 82% of DD, 66% of SC and 68% of PPM users are satisfied.
- **Inertia is large on SC.** Ofgem's impact assessment (May 2025): "only 20% of customers on Standard Credit surveyed wanted to change payment method" (repo: `payments_and_direct_debit_2026-10-25.md` s.5; I did not re-open that PDF).
- **Who is on each method is skewed to disadvantage.** Ofgem 2024 decision, para 3.25: low income is **64% of PPM** customers, **51% of SC**, and 41% of DD (income under £30,000). Long-term disability or illness is **44% of PPM**, 33% of SC, 29% of DD.
- **The CMA said the same in 2016.** Final report summary paras 103-105: most customers can choose between SC and DD, and SC paid about £75-80 a year more. *"Prepayment, in contrast, is not generally a choice on the part of the customer."* PPMs were installed where there was a poor payment history or in certain rented homes. 58% paid by DD and 27% by SC in 2015.
- **The CMA and Ofgem 2023 differ on PPM.** CMA 2016: not generally a choice. CIM 2022: 72% give an active reason. Both can hold. People adapt, the PPM stock mixes choosers and those fitted, and "easier to budget" can be an adaptation. The survey cannot separate them. See 2.5.

**Not established (GAP-1):** the joint table "SC payer, knows SC costs more, and still chooses it for control". Ofgem publishes data tables (`CIM Wave 3 Data Tables.xlsx`). I downloaded the file but did not parse it. That crosstab is the cleanest measure of *knowingly paid* control.
**Not established (GAP-2):** the SC versus PPM split of the non-DD remainder, and any income or tenure crosstab by method. The repo already names both as open (`gb_payment_method_migration_rates.md` s.2).

### 2.2 Cash flow (N2): the buffer is thin for a large minority, and timing is unquantified

**FCA Financial Lives 2024, "Vulnerability and financial resilience", May 2025** (H; I read the PDF):
- **24%** of UK adults (13.1m) had low financial resilience in 2024, unchanged since 2022.
- Components: **14%** (7.6m) low savings, **13%** (7.3m) heavily burdened by domestic bills or credit, **8%** (4.5m) in financial difficulty.
- "Low savings" is defined as being unable to withstand losing the main income for even a week, or struggling with a rent or mortgage rise under £50 a month.

The repo holds the income-band cut from earlier Financial Lives data (`household_budget_w2_4.md`, marked [L], not re-read here): under £15,000 a year, 22% have no savings and over a third have under £1,000. The same page cites utility bills as the most commonly missed bill (8.6% of adults, Jan 2023 recontact).

**Credit held by suppliers is large.** Ofgem credit-balance data: gross domestic credit balances were about £7.1bn in Q1 2023 and £8.1bn at end 2023. The net measure per fixed-DD household was £180-400 through 2023 (repo `payments_and_direct_debit_2026-10-25.md`; the Ofgem explanatory note is the source). That is an interest-free loan *to* the supplier. Whether it is cheap or costly depends on the household's buffer. That is N2.

**What the record does not give:**
- **GAP-3:** the share of GB households with weekly, fortnightly or irregular income. I did not find a published GB figure I could open. Financial Lives has income-volatility questions, but I did not locate the figure in a document I read.
- **GAP-4:** the bank-charge cost of a DD that lands before payday, as a count or a size. The repo's earlier pass (`risk_based_payment_plans_outside_gb_energy.md` s.4) found payday-aligned collection is a widespread practice but found no quantified effect on failed payments. I did not close that.
- **GAP-5:** the share of DD failures caused by timing rather than lack of money. No source found.

### 2.3 Certainty (N3): real, but a willingness-to-pay figure is not published

- **Worry is high.** In CIM Wave 3, more than half of DD and SC customers were worried about falling behind on bills (54-62% depending on group and wave; the group-by-column mapping in the text extraction was not clean, so the bound, not the cell, is cited).
- **Fixing is a stated motive.** Among households that switched in the past year, **18%** (Dec 2022; **26%** in March and July 2022) gave "wanted a fixed tariff (fixed term, fixed price)" as a top reason (CIM Wave 3, section 4). The fall to 18% came as fixes became scarce or dear.
- **Fear of things going wrong is quantified in the record.** 41% "worry that if I switch things will go wrong" (Ofgem Consumer Engagement Survey 2017, as read in C31 s.2.1). That is certainty applied to *switching*.
- **The market priced a fix well above the default in the crisis.** Ofgem's "average fixed tariff" series: Oct 2021 default £1,277 against average fix on sale £2,096; Sep 2022 default £1,971 against £4,599 (repo, `cheapest_fix_against_the_default_tariff_gb_2016_2025.md` s.3, H on its own source). That is what a fix cost at the dearest moment. It is *not* what households were willing to pay.
- **Before mid-2021 the repo's series points the other way, but I did not re-read it.** The page is built around the gap between the cheapest fix and the default (`cheapest_fix_against_the_default_tariff_gb_2016_2025.md`). The average-fix gap was only -0.8% in June 2021. I infer that for most of 2016-2021 a fix was not bought at a premium, but I have not checked the 2016-2020 rows. Treat as L until a build pass reads them.

**GAP-6:** no published GB estimate of households' willingness to pay for price certainty on energy. Searches for one this session returned nothing usable, and the search tools were unreliable. I will not import a mortgage or US figure.
**GAP-7:** no published measure of *how much more* uncertainty-averse low-buffer households are. The steer says it is higher. Logic supports it: a given shock is a larger share of a small buffer. It is a stated belief with no number. Label it a belief with a range to be estimated, not a parameter.

### 2.4 Control (N4)

- **SC payers cite control most (41%)**; PPM payers cite it at 33% and budgeting at 42% (table 2.1).
- **PPM carries real harm when control tips into running out.** Citizens Advice, *Kept in the dark* (12 Jan 2023; Yonder poll of 4,384 UK adults, 6-15 Dec 2022; H as to what they published): **3.2 million people** in Great Britain ran out of credit in the previous year because they could not afford to top up; more than 2 million disconnected at least once a month; **19%** of those cut off spent 24 hours or more without supply. Of Citizens Advice's 3.2m, the figure is a grossed-up estimate (households x 2.4), per its own footnote.
- **CIM Wave 3 (Dec 2022), PPM customers:** 19% unable to top up because they cannot afford it; 12% ran out and were disconnected for over 3 hours; 24% used emergency credit; 19% reduced what they put on the meter.
- **Ofgem's own series:** smart-PPM customers self-disconnecting at least once in a quarter (electricity): 667,960 in Q2 2022, a peak of **946,400** in Q3 2023, then 564,191 in Q2 2026 (repo, `debt_and_collections.md` s.2.1; Ofgem indicators).
- **Rules exist.** SLC 27A (from 15 Dec 2020) requires suppliers to identify PPM customers who self-disconnect (Ofgem decision, Oct 2020; repo `heating_behaviour...` s. on SLC 27A).

Self-disconnection is the harm signal for control, as the steer proposes. It is a *count of a bad event*. It is not a measure of how much control a household has.

### 2.5 Not all prepayment is chosen: the 2023 forced-fitting record

- **Scale (Ofgem).** The market compliance review covered **over 150,000** customer accounts where a PPM was fitted by warrant or by remote switch, 1 Jan 2022 to 31 Jan 2023. On reassessment, **1,925** (under 2%) were installed when it was not safe and reasonably practicable (Ofgem, *Market compliance review: prepayment meter installations*, 3 June 2026, pp. 1-3; H, I read the PDF).
- **Scale (Citizens Advice).** Citizens Advice estimated **600,000 people** were forced onto a PPM in 2022 *because they could not afford their bills*, "based on Ofgem figures" (Jan 2023, same page as above). This is a different population and definition from Ofgem's 150,000 accounts. I do not reconcile them. **GAP-8:** an agreed count of how many PPMs are imposed rather than chosen.
- **The 2023 rule change.** Suppliers stopped involuntary installs in Feb 2023. Stronger rules came in Nov 2023, and a first restart was Jan 2024. Suppliers now must reassess every PPM at least annually (repo: `gb_payment_method_migration_rates.md` s.1; MCR, p. 2). Suppliers committed £18.6m (£5.6m compensation and £13m debt write-off) on 28 May 2025 (repo `payments_and_direct_debit_2026-10-25.md` s.5).
- **The structural point.** The world needs *two* PPM populations. **Chosen PPM** (budgeting, control, about 6% of PPM households recently moved on to "help manage what I spend", CIM Wave 3) and **imposed PPM** (debt, warrant or remote switch, landlord, inherited). They have the same meter and opposite relationships to N4. Treating them as one hides the harm.

### 2.6 The comfort and health floor

The repo already holds the floor evidence (`heating_behaviour_comfort_and_health_floors_2026-10-25.md`): the Ofgem SLC 27A self-disconnection rule, NICE and WHO indoor-temperature thresholds, and the instruction not to advise a setpoint cut to a household already below 18C or rationing. I did not re-read the thresholds. The floor is a **veto**: a decision that pushes a household below it is refused whatever it earns in money, certainty or carbon.

---

## 3. What the code does today

**Not re-measured.** The discovery wall forbids me from reading `company/`, `simulation/` or `saas/`. The steer and C31 say money has a household-side score in the world only partly, time has none, and payment method is chosen by the supplier's route (debt, DD failure) more than by household preference. A build pass must check these directly before any design. This note makes no claim about the code.

---

## 4. Candidate units (never converted to pounds)

Each need has a household-side unit and, where the supplier can see it, a supplier-side observable. Every unit carries its denominator.

| Need | Household-side unit (world holds it) | Supplier-side observable (company can see it) | What the unit must NOT be |
|---|---|---|---|
| N1 Cost | pounds paid over the period against the counterfactual | its own bills and receipts | summed with the others |
| N2 Cash flow | a *timing mismatch*: days between a payment and the income that funds it; **bank-charge events**; payments that failed for timing | failed or returned DD, DD date changes, late payments, credit it holds, refund lag | "pounds of working capital". Do not price the credit |
| N3 Certainty | (a) spread of monthly outgoings against what the household expected; (b) chance of a bill well above expectation; (c) shock events a year | its own bill-to-prior-bill change, DD-change size, rate of complaints about the bill | a pound premium. The fix premium is a *price*, not a unit of certainty |
| N4 Control | match between the household's payment and visibility *preference* and what it has; **self-disconnection and rationing events** as the harm signal | payment method, top-up pattern, emergency-credit use, self-disconnection reports (already reported to Ofgem), DD-cancel requests | "number on PPM" as if it were control |
| N5 Time | household minutes by class T1-T4 (C31) | its own service clocks | any £ conversion (M3, 12 Oct) |
| N6 Carbon | kg CO2 saved or avoidable (CO1) | metered use and grid intensity | a target |
| Floor | breach flags: indoor temperature below safe level, any supply cut | PSR flags, self-disconnection, vulnerability markers | a currency. It is a count of vetoes |

Four rules for these units, taken from the record:

1. **Count events before assigning size.** C31 s.8 found no published minutes per event. The same is true here: no published pounds per bank-charge event, no published cost of a shock bill. Counts first. Sizes stay `None` with a named reason until a source gives them.
2. **Never sum across needs.** A decision that saves £ and costs certainty shows as a trade, not a net.
3. **Say which side.** The household-side unit lives in the world. The company sees only what a real supplier records. The household's buffer, its income timing and its uncertainty aversion are hidden.
4. **Self-disconnection is a signal of harm, not a goal.** Never minimise it by moving households off PPM without checking the floor. It is a diagnostic (CLAUDE.md: outputs are diagnostics, never targets).

---

## 5. Household heterogeneity: the hidden traits and what a supplier can infer

The steer lists the traits the world should hold and the supplier must infer. The record says:

| Hidden trait | What the record says | What a real supplier can observe |
|---|---|---|
| **Buffer size** | 14% low savings; 24% low resilience; under-£15k incomes: 22% have no savings (Financial Lives, repo) | arrears, returned DD, credit-bureau score if used, missed-payment history |
| **Income timing and regularity** | GAP-3 (no GB share found) | benefit or salary credit date if the household says; DD-failure date patterns |
| **Uncertainty aversion** | worry 54-62%; higher on tight budgets is a stated belief (GAP-7) | fix take-up, DD-change complaints, reaction to a shock bill |
| **Control preference** | SC 41%, PPM 33% give control as a reason (CIM) | method chosen when offered a choice; DD cancel; top-up regularity |
| **Trust in suppliers** | not measured here | complaints, cancelled mandates, refusal to share a payment mandate |
| **Imposed vs chosen PPM** | Section 2.5 | whether the meter was fitted for debt (the supplier knows this), landlord-fitted (often unknown) |

Two cautions.

- **The traits are correlated, not independent.** Low buffer, irregular income and high uncertainty aversion move together, and with disability and low income (64% of PPM households on low income; 44% with long-term illness). The world should draw them as a joint distribution. The repo already makes the same point for income and savings (`household_budget_w2_4.md`).
- **The supplier infers from behaviour, and behaviour is confounded.** A household that fails a DD may be short of money, mistimed, or cancelled the mandate on purpose. The three need opposite responses. The repo found that a DD attribution confound exists (`dd_attribution_confound_w2_10.md`; not re-read). The inference must carry its uncertainty.

---

## 6. How a supplier creates value on each need, and shares in it (M2)

M2 says value is created, then shared, and a transfer is not creation. For each need the question is the same: **what did the supplier do that made the household better off at a cost to the supplier lower than the benefit, and what share does it keep?** Where the answer is "nothing, it just charged more", that is a transfer.

**N1 Cost.** Create it by buying or hedging cheaper than the household could, by lower cost to serve, or by shifting load to cheap periods. Charging the cap moves value and creates none (M2).

**N2 Cash flow.** Ways to give a cash-short household the DD price without the costs that keep it off DD:
- a DD date set to the household's payday;
- weekly or fortnightly DD;
- a variable DD for smart homes, so no credit is held;
- smart PAYG with budget alerts and friendly-credit periods;
- fast refund of credit.

Value is *created* when the household avoids bank charges and arrears **and** the supplier's cost to run the option is lower than what it saves in failed DDs and bad debt. Ofgem priced the SC-versus-DD cost difference in 2018 at **£75** after headroom (admin £19.09 per account at the benchmark supplier; repo `payments_and_direct_debit_2026-10-25.md` s.5). Bad-debt allowances were £57 DD, £160 SC and £19 PPM per dual-fuel customer, against a benchmark of £71. So collection method has a measurable supplier cost, and a better-timed DD plausibly lowers the SC and DD-failure cost. **It is not a finding that payday alignment works** (GAP-4, GAP-5).
*Credit held is the clearest transfer.* A level DD that over-collects is value moved from household to supplier. It becomes value *created* only where the household *prefers* the smoothing (43% of DD payers say DD is easier to budget) **and** has the buffer to carry it **and** can ask for the money back at once. The test is in section 6.1.

**N3 Certainty.** See 6.1 below.

**N4 Control.** The supplier creates value by offering control without the cost of exclusion. Today the cost of control through *price* has gone for PPM: it is the cheapest method in 2025 (£1,817 against £1,884 DD, £2,015 SC), after the April 2024 standing-charge levelisation (£52 off PPM, £10 on DD, Ofgem 23 Feb 2024). SC still carries +£131. What remains is the *harm* side, running out. Value created: budget alerts, friendly-credit hours, and top-up access. Value *moved*: a PPM fitted to recover debt, whatever it later recovers.

**N5 Time.** Per C31. T2-T4 are ours to cut.

**N6 Carbon.** Per CO1. Shown, never a target.

### 6.1 The fix premium: value made, or value moved? A test that tells them apart

Today the repo books a fix premium as value moved. Under this framing, part of it may be value made. Say what the premium is first.

- **F** is the price the household pays on the fix.
- **E** is the household's expectation of the variable price over the same term. A rational, uninformed household would use the market forward. Many use the current rate.
- **Premium = F minus E.** It can be negative (a saving) or positive.
- **H** is what it costs the supplier to carry the risk it removes: the hedge at the forward, plus the cost of volume, shape, basis and credit risk that the hedge does not remove, plus capital.

Two different quantities are hidden in "premium".

| Part | What it is | Made or moved |
|---|---|---|
| **Risk transfer** | household pays to avoid price risk; supplier, pooling many customers and hedging, bears it at lower cost than any one household could | **Made**, if H is less than the household's own cost of carrying that risk |
| **Margin** | what is left of the premium after H | **Moved** (a transfer), unless the household's gain exceeds H plus margin and it would choose it knowingly |

**The test has three legs. All three must hold for any of the premium to count as made.**

1. **The supplier really bears and prices the risk it sells.** The fix is hedged (or the unhedged exposure is measured and held), and H is computed on the actual hedge. If the supplier hedges nothing and sells a fix, it is selling a bet, not certainty.
2. **The household really gets certainty.** The *certainty unit* (spread of outgoings, chance of a bill well above expectation, shock events) is lower on the fix than on the variable, for that household, over the term. A fix that is repriced, or ended early on the supplier's terms, delivers none.
3. **The premium over H is bounded and shared.** The part above H (margin) is what the supplier keeps. M2 says value is *created and then shared*. The test is that the household would keep a positive share: the gain in the certainty unit exceeds what it would cost the household to carry the risk itself, which the world, not the supplier, holds.

**Why the counterfactual is the hard half.** The household's own cost of worry is a hidden world trait, in no published GB figure (GAP-6, GAP-7). So the supplier cannot see leg 3. The world can, and the improvement loop must read it from the world, never from the company's side.

**Outcome and valuation are different things.** In Oct 2021 the average fix on sale was £2,096 a year against a £1,277 default (repo, from Ofgem). The default was later pushed above £2,500 by the cap. A household that fixed in Oct 2021 *ended up better off in money* on some paths and worse on others. That outcome is not the value of certainty. Do not grade the fix by its money outcome. Grade it by the certainty unit plus a margin check.

**What the test refuses.** If legs 1 or 2 fail, the whole premium is a transfer and is booked so. If leg 3 cannot be read, say "we cannot tell", not "made".

---

## 7. How the improvement-loop scorecard would change

I do not know the loop's internals (it sits in the design the steer names, behind the correctness exit test). This is what the framing implies, as a proposal.

| Today (C31, A47, M3) | With the needs framing |
|---|---|
| Money column | split: **cost** and **cash-flow** columns, each in its own unit |
| Time column (planned, minutes) | unchanged |
| Carbon column | unchanged |
| none | **certainty** and **control** columns, household-side, from the world |
| none | **floor breaches** as a count that blocks a decision, not a column that adds up |

Rules for the scorecard:

1. **A decision is a trade, not a net.** One that saves cost and worsens certainty shows both.
2. **Published per arm, per household class.** Each need is cut by the hidden-trait class (buffer quartile; chosen versus imposed PPM). An average hides the household the decision harms.
3. **The company cannot grade itself on household-side columns.** It optimises on what it sees (returned DDs, complaints). The world scores N2-N4 and the floor. The two are compared. A gap is the finding.
4. **A decision that improves its own observable but not the household's unit is flagged.** Example: a lower DD-failure rate reached by moving cash-short households to PPM. Failure falls and control may fall too.
5. **Value created versus moved is stated per need.** For N3, the three-leg test in 6.1 sets which part is which.
6. **"We cannot tell" is a result.** Where a unit has no source (GAPs below), the scorecard shows it blank with the reason.

---

## 8. Fairness

The households with the highest cash-flow and control needs are often the most vulnerable. The evidence:

- **PPM:** 64% low income, 44% with a long-term disability or illness (Ofgem 2024).
- **SC:** 51% low income, 33% disabled or ill; arrears doubled between CIM Wave 3 and Wave 4 (Ofgem 2024, para 2.7).
- **Self-disconnection falls on the sick.** Citizens Advice: in the month after Ofgem's intervention, more than a third of PPM households with a disabled or long-term-ill person were cut off at least once (**470,000** households; Jan 2023 press release, as quoted by Citizens Advice).
- **They pay more.** SC +£131 a year; and a household that cannot hold a DD loses the DD discount.

Four fairness constraints the framing forces:

1. **Do not price need.** If a supplier infers high cash-flow need or high uncertainty aversion, it must not charge more for that. Certainty is worth most to the households least able to pay for it. A premium set by willingness to pay is regressive.
2. **Proxy discrimination.** Traits inferred from behaviour (failed DD, top-up pattern) can stand in for vulnerability. Test any pricing or offer rule for it, by trait class, on the world's truth.
3. **Imposed prepayment is never "control".** The fix for cash-flow need is the option set in section 6, not PPM. The 2023 record is the reference: 1,925 wrongful installs among over 150,000 reviewed.
4. **The floor binds first.** No saving on N1-N3 justifies a breach of comfort and health.

---

## 9. Open questions, each with a recommendation

- **Q1. Is the set of needs complete?** *Recommendation:* adopt seven (cost, cash flow, certainty, control, time, carbon, and the comfort floor). Revisit if the world produces behaviour the six do not explain. The record gives no sign yet of an eighth. Dignity and fairness are better held as constraints than as needs.
- **Q2. Is the fix premium made or moved?** *Recommendation:* neither, until the three-leg test in 6.1 is run. Book it as moved (today's rule, the safe direction, F11) and test leg by leg once hedging exists in the loop.
- **Q3. Should certainty and control get their own columns?** *Recommendation:* yes, in the world's score only, in own units. The company sees proxies.
- **Q4. Canon wording.** The `for_the_director` row raised with this note (amend M3; do not add a new M-rule).
- **Q5. Sequencing.** Reading-only now. Build after the correctness exit test, inside the improvement-loop design. First increment: an *event census* (count failed DDs, DD date changes, self-disconnections, shock-bill events) with every size `None`, as in C31 L1.

---

## 10. Not established, stated so it is not read as done

| ID | Gap | Why it matters |
|---|---|---|
| GAP-1 | CIM Wave 3 crosstab: SC payers who know SC costs more yet cite control | the share who knowingly buy control |
| GAP-2 | SC versus PPM split of the non-DD remainder; income and tenure crosstab by method | who is on each method and why |
| GAP-3 | GB share of households with weekly, fortnightly or irregular income | size of the cash-flow-mismatch population |
| GAP-4 | £ or count of bank charges triggered by DD timing; effect of payday-aligned DD on failures | N2 value |
| GAP-5 | share of DD failures due to timing rather than lack of money | N2 value |
| GAP-6 | GB willingness to pay for energy price certainty | N3 value; the fix test, leg 3 |
| GAP-7 | how much more uncertainty-averse low-buffer households are | heterogeneity of N3 |
| GAP-8 | an agreed count of imposed versus chosen PPM | the two-population design |
| GAP-9 | minutes of household effort tied to payment management (inherited from C31) | N5 |
| GAP-10 | Ofgem Standards of Conduct and any Consumer Duty-type limit on pricing by inferred vulnerability; not read this pass | fairness constraint 1 and 2 |

Search tools were unreliable this session: two search engines returned nothing for several queries. GAP-3, GAP-6 and GAP-7 may be closable with working search. A later pass should try Financial Lives income-variability tables, Citizens Advice DD and payday research, and Ofgem's tariff-choice research before treating them as absent from the literature.

---

## Sources

Opened and read this session:
- [Ofgem, Decision on adjusting standing charges for Prepayment Customers, 23 Feb 2024](https://www.ofgem.gov.uk/sites/default/files/2024-02/Decision%20on%20adjusting%20standing%20charges%20for%20Prepayment%20Customers.pdf) (paras 2.6-2.8, 3.19, 3.25-3.26, A2.45, A2.70)
- [Ofgem, Consumer Impacts of Market Conditions, Wave 3 report (Nov-Dec 2022; published May 2023)](https://www.ofgem.gov.uk/sites/default/files/2023-05/CIM%20Wave%203%20Report.pdf) and [data tables](https://www.ofgem.gov.uk/sites/default/files/2023-05/CIM%20Wave%203%20Data%20Tables.xlsx) (downloaded, not parsed)
- [Ofgem, Market compliance review: prepayment meter installations, 3 June 2026](https://www.ofgem.gov.uk/sites/default/files/2026-06/Market-Compliance-Review-prepayment-meter-installations.pdf)
- [FCA, Financial Lives 2024 survey: Vulnerability and financial resilience, May 2025](https://www.fca.org.uk/publication/financial-lives/fls-2024-vulnerability-financial-resilience.pdf)
- [Citizens Advice, Kept in the dark: the urgent need for action on prepayment meters, 12 Jan 2023](https://www.citizensadvice.org.uk/policy/publications/kept-in-the-dark-the-urgent-need-for-action-on-prepayment-meters/) and [the press release](https://www.citizensadvice.org.uk/about-us/media-centre/press-releases/millions-left-in-the-cold-and-dark-as-someone-on-a-prepayment-meter-cut-off-every-10-seconds-reveals-citizens-advice/)
- [CMA, Energy market investigation final report summary, 24 June 2016](https://assets.publishing.service.gov.uk/media/576c23e4ed915d622c000087/Energy-final-report-summary.pdf) (paras 103-105)

Cited from repo pages (not re-opened this session; each page carries its own source):
- `docs/market_research/gb_payment_method_migration_rates.md` (DESNZ QEP Dec 2025 payment-method bills; levelisation; 150,000 count)
- `docs/market_research/payments_and_direct_debit_2026-10-25.md` (credit balances, 2018 payment-method uplift, SC awareness and inertia)
- `docs/market_research/debt_and_collections.md` (smart-PPM self-disconnection series)
- `docs/market_research/household_budget_w2_4.md` (Financial Lives savings by income band)
- `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md` (Ofgem average-fix series)
- `docs/market_research/risk_based_payment_plans_outside_gb_energy.md` (payday-aligned collection, practice but no effect size)
- `docs/market_research/heating_behaviour_comfort_and_health_floors_2026-10-25.md` (floor, SLC 27A)
- `docs/design/C31_TIME_AS_A_CURRENCY_DISCOVER_FRAME_2026-10-04.md` (time classes, Ofgem 2017 switching survey)
