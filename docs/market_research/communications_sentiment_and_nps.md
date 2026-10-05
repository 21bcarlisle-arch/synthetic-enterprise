# Communications, sentiment and NPS — what each one is, what is published, and what the world would need

**Knowledge:** communications-sentiment-and-nps

> **Director's ruling, 2026-10-05 — read every complaint figure below through it.** The data only
> sees people who complain. The 9% / 17% / 23% switching gradient describes complainants alone, and
> Ombudsman figures the escalated few. The unhappy-but-silent are invisible, and are probably the
> same disengaged group the 2025 survey shows switching LESS (3.0% vs 5.4%). So complaint statistics
> are a **floor on dissatisfaction, not a measure of it**. The world models the silent unhappy as a
> population of their own (atom W2_37) rather than building dissatisfaction around complaints.

*Knowledge pass, step 1 of the director's priority order (`docs/staging/done/DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05.md`),
for the area that order puts last (step 7). Written 2026-10-05. Every figure is from a published source fetched this
pass or already held in this repository, and is attributed to its own instrument, wave and sample. Where the record runs
out, the gap is named. No figure here is simulation output except in "What our code does", where code is described, not
measured.*

**How this page relates to the two existing ones.** `satisfaction_drivers_and_the_three_bill_shocks.md` (drivers of
satisfaction, the three causes) and `what_bill_shock_is.md` (the two experiences) stay where they are, and both are
right. This page does not repeat them. It adds the instruments (NPS, sentiment, trust, complaints and the Ombudsman),
the communication evidence, the rules, and what the supplier can see. It also corrects one inference on the first page:
§3.4 shows that the "~3×" complaint dose there was built on a figure that mixes *switched* with *planning to switch*.

---

## 1. Definitions. Say what each thing is before measuring it.

There are six separate quantities here. Every one of them gets mistaken for the others.

| quantity | what it IS | unit | who measures it | is it a state or an event? |
|---|---|---|---|---|
| **Satisfaction** | A household's stated evaluation of its supplier, asked directly: *"Overall, how satisfied or dissatisfied are you with [supplier]…"* on a **five-point** scale (Ofgem/Citizens Advice Energy Consumer Satisfaction Survey, question A5). Reported as % satisfied, % neither and % dissatisfied. There is a separate customer-service question (A7). | % of respondents in a band | Ofgem/CA survey (~3,800 per wave, two waves a year since 2018); Which? (members' survey); UKCSI (cross-sector index 0–100) | **State** |
| **NPS** | *Likelihood to recommend*, 0–10. Promoters are 9–10 and detractors 0–6. **NPS = % promoters − % detractors**, so it runs from −100 to +100. It is a statement about advocacy, not about satisfaction. | index points | The CMA used it in the 2016 Energy Market Investigation. Ofgem published it **by supplier size band only** (Consumer Engagement Survey 2019). Suppliers run their own versions, and these are not published. | **State** (a stated intention to advocate) |
| **Sentiment** | The valence of what a household **says**: in calls, chats, emails, complaints and reviews. It is not asked for; it is inferred from the content. | classifier score per interaction | Only the supplier, from its own contact records. The nearest public proxy is Trustpilot TrustScore. **No regulator publishes it.** | **Event-level signal** |
| **Complaint** | Legally, *"any expression of dissatisfaction made to an organisation, related to any one or more of its products, its services or the manner in which it has dealt with any such expression of dissatisfaction, where a response is either provided… at the point at which contact is made or a response is explicitly or implicitly required or expected"*; a *consumer* complaint excludes *"a network outage report"* (SI 2008/1898, reg. 2). A complaint is a **recorded event**, and the definition is wide. Ofgem's "complaints per 100,000 accounts" counts these. | count per 100k accounts per quarter | The supplier records every one. Ofgem publishes them per supplier each quarter. | **Event** |
| **Ombudsman escalation** | A complaint that is unresolved at **8 weeks**, or has received a **deadlock letter**, and that the household then *refers* to the Energy Ombudsman. It is a small, self-selected subset of complaints. | cases accepted per year | Energy Ombudsman | **Event** (a second-order one) |
| **Trust** | Whether a household expects its supplier to *"treat them fairly"*. This is the CIM question. It is not the same as satisfaction: a household can be satisfied with today's service and not trust what the supplier will do next. | % agreeing | Ofgem Consumer Impacts of Market Conditions survey (CIM) | **State** |

Four consequences follow from the definitions. They do not come from the data.

1. **Complaint and dissatisfaction are different populations.** Complaining is an *act*. Dissatisfaction is a *state*,
   and most dissatisfied households never complain. The two predict departure in **opposite directions** in the published
   record (§3.4). Pooling them into one "unhappiness" scalar is the bill-shock mistake made again.
2. **NPS is not satisfaction with a different scale.** It asks about advocacy to third parties. In a market where
   ~6% are dissatisfied and ~82% satisfied (§3.1), NPS can still be **negative**. The 2019 Large-supplier band was −15
   (§3.2), because "passives" (7–8) count for nothing and a "satisfied" household may answer 7.
3. **Sentiment is the only one of the six that exists at the level of each interaction**, and it is the only one with no
   published distribution at all. Anything built on it is calibrated against nothing.
4. **The complaint definition is wide on purpose.** A same-day billing query that ends in "I'm not happy about this" is
   a complaint. That is why supplier-recorded complaints (~1% of accounts per quarter) are about **ten times** the Ombudsman's
   volume. It also means the complaint *count* depends heavily on how a supplier records. See §5.

---

## 2. Populations and triggers

The published triggers are listed below, with the population each one lands in. The bill-shock split is stated
in `what_bill_shock_is.md` and is only referenced here.

| trigger | population it lands in | what the household experiences | published weight |
|---|---|---|---|
| **DD change** (the review resets the monthly amount) | Fixed direct debit (~74% of households pay by DD in total; the fixed/variable split is **not published**) | A payment that goes up, or a balance they cannot explain | Feb–Apr 2022: >7m SVT DD increases, average **+62%**, 8% above 100% (Ofgem DD Market Compliance Review, July 2022). 2024: "disputed account balances" were **8% of billing disputes** at the Ombudsman. |
| **The bill itself** (catch-up after estimates, seasonal, usage change) | Standard credit (~13%) and variable DD | The bill | "Disputed gas or electricity usage" was **22% of billing disputes**. Back-billing: **3,218** Ombudsman disputes in 2024 and **3,216** in 2025 (Energy Ombudsman). |
| **Billing error / billing in general** | All credit-meter households | Wrong bill, wrong balance, wrong refund | **Billing is 58% of Ombudsman cases in 2024 (53,607 of 92,938) and 56% in 2025.** In the 2014 complaints survey, billing was the subject of **38%** of domestic complaints, prices 27%, meters 21%, transfer 15% and customer service 11% (multi-coded). |
| **Price rise** (the supplier's commercial choice) | Everyone, with two lags: the bill (B) at once, DD (A) at the next review | A higher rate, after notice | Prices were **27%** of complaint subjects (2014). Price is a *hygiene* factor for service, but the main factor for *choice*: the CMA found *"price is the factor to which customers attach greatest weight"* (EMI 2016, para 8.30). |
| **Debt contact** | Households in arrears | Proactive contact, payment plan, possibly a PPM | Since 14 Dec 2023, contact is **mandatory after 2 missed monthly / 1 missed quarterly payment** (Ofgem Consumer Standards decision, 18 Oct 2023). Debt/payments were **6%** of complaint subjects (2014) and **2,420** Ombudsman cases (2024). |
| **Outage** | All. Distribution faults are the **DNO's**, not the supplier's | Loss of supply | A *network outage report* is excluded from the statutory definition of a consumer complaint (SI 2008/1898 reg. 2); faults go to the DNO under its own regime. **No published share of supplier complaints is about outages.** |
| **Switching friction** | Gainers and losers at a transfer | A delayed or erroneous switch, a late final bill | **Transfer was 15%** of domestic complaint subjects (2014). GSOP pays £30 for a delayed or erroneous switch (held in `knowledge_map.md`, C31 row). |
| **Customer-service failure** (waits, no callback, not kept informed) | Anyone who contacts the supplier | Process, not price | This is **the** driver of dissatisfaction with complaint handling (§3.4). Customer service was **10,377** Ombudsman cases in 2024. |

**Payment method is an input, not a covariate.** The DD-versus-bill split decides which trigger a household can even
experience. Prepayment (~13%) has neither a bill shock nor a DD change. Its triggers are self-disconnection,
top-up affordability and debt recovery through the meter, and that is a different measurement.

---

## 3. Scale, with sources

### 3.1 Satisfaction: level, spread across suppliers, and trend

**Market level** (Ofgem/CA Energy Consumer Satisfaction Survey; the per-wave table is in
`satisfaction_drivers_and_the_three_bill_shocks.md` and is not repeated here). Overall satisfaction was **81–82%** across
Jan 2025, Jul–Aug 2025 and Jan 2026. Dissatisfaction was **6%**. Customer service was 74–77%.

**Trend.** Satisfaction was **78%** in April 2020 and fell to **69%** in Aug–Sep 2023. It then recovered: 73% in Jan–Feb 2024, 78% in July
2024 and 82% in Jul–Aug 2025 (Ofgem survey pages for each wave; the Jul 2024 wave was the first back at the April 2020
level). **The 2022–23 crisis cost ~9 points of satisfaction, and the record shows them coming back.** Satisfaction is
not a fixed property of the market.

**Between-supplier spread, one wave** (Ofgem, *Customers' satisfaction with their supplier: supplier level findings*,
fieldwork 16 Jul–13 Aug 2025, published 2 Dec 2025, n=3,790; only the 7 groups with enough sample are reported):

| | GB | British Gas | EDF | E.ON | Octopus | OVO | Scottish Power | Utilita |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| base n | 3,790 | 1,168 | 323 | 481 | 876 | 314 | 243 | 112 |
| satisfied overall | 82% | 81% | 79% | 80% | **90%** | **73%** | 74% | 76% |
| dissatisfied overall | 6% | 6% | 9% | 6% | **3%** | **10%** | 8% | 9% |
| satisfied with customer service | 76% | 77% | 70% | 71% | **84%** | **60%** | 70% | 72% |

So among the seven largest groups, the **dissatisfied share runs from 3% to 10%**, a **~3×** range. Satisfaction with
customer service runs from 60% to 84%.

**Cross-sector.** UKCSI (Institute of Customer Service): Utilities scored **73.7** in July 2026 against an all-sector **78.3**.
In January 2019 Utilities scored 73.8 (energy 73.4) against 77.7, and ranked **12th of 13 sectors**. Energy has sat ~4 points below the
all-sector mean for seven years.

### 3.2 NPS: what is published, and how little

* **Ofgem Consumer Engagement Survey 2019, by supplier size** (as reported in Littlechild 2021, footnote 12, from
  Ofgem's data portal *"Likelihood to recommend energy supplier and Net Promoter Score"*):
  **Large −15** (22% promoters, 38% detractors) · **Medium +17** (40% / 23%) · **Small −16** (29% / 35%).
* **The CMA (EMI 2016, para 9.106)** found *"no clear relationship between the cheapest supplier and customer service, as
  approximated by the NPS score, except that the smaller suppliers… receive consistently higher NPS scores"*.
* **No per-supplier NPS is published by any regulator.** Littlechild (2021) notes that the commercial NPS benchmark
  service did not cover GB residential energy.
* **NPS has documented weaknesses.** Reichheld (2003, *"The One Number You Need to Grow"*, HBR) claimed NPS was the
  best single predictor of growth. Keiningham, Cooil, Andreassen and Aksoy (2007, *Journal of Marketing* 71(3):39–51)
  replicated that work on 21 firms and 15,500+ interviews from the Norwegian Customer Satisfaction Barometer, and found
  **satisfaction predicted growth as well as NPS did**, in every industry tested. So NPS adds no information over
  satisfaction for predicting growth. It also discards information by construction: a 7 and an 8 both count as zero, and
  a 0 is the same as a 6.
* **The energy-specific result points the other way from the folk model.** The Large and Small bands had almost the same
  NPS (−15 and −16), although Small suppliers were cheaper and Large ones were the incumbents. **Recommendation was
  highest at Medium suppliers.** That is a supplier-type effect, not a price effect.

### 3.3 Complaints and Ombudsman volumes

**Supplier-recorded complaints, per 100,000 domestic accounts per quarter** (Ofgem customer service data portal):

| period | market | large | medium | small |
|---|---:|---:|---:|---:|
| Q4 2025 | **1,011** (−2% QoQ, −15% YoY) | 986 | 1,650 | 223 |
| Q1 2026 | **1,038** | 1,006 | 1,827 | 208 |

* **The spread between suppliers is large.** Among 15 large and medium suppliers in Q4 2019, complaints ran from **16 to 221 per
  10,000** (a 14-fold range). Among 30 small suppliers the range ran from 0 to over 1,000 (Littlechild 2021, §2.2, from Ofgem data).
* **The small-supplier figure is low partly because of how complaints are recorded.** The Ofgem metric depends on what a supplier records as a complaint (§1.4).
  Treat the medium-vs-small gap with suspicion. Treat the large-vs-medium gap less sceptically, because both are large books
  under the same scrutiny.
* **Historical per-quarter market series 2018–2024: on the portal, not captured this pass. Open gap** (the data
  exist; a fetch of the portal CSV would close it).

**Energy Ombudsman, cases per year:**

| year | volume | what is counted | source |
|---|---:|---|---|
| 2018 | ~54,000 | complaints received (contacts) | EO news, 3 Aug 2020 |
| 2019 | 68,523 actionable; 56,978 resolved; **57% upheld** in the consumer's favour | | EO news, 3 Aug 2020 |
| 2021 | ≈69,900 *(derived: 2024 is stated as 33% above 2021)* | accepted | EO news, 15 May 2025 |
| 2022 | ≈89,400 *(derived: 2024 is 4% above 2022)* | accepted | same |
| 2023 | **122,829** | accepted | same |
| 2024 | **92,938** (billing 58%) | accepted | same |
| 2025 | **80,256** (billing 56%) | accepted | EO annual data, 20 Mar 2026 |

* **Signposting is poor.** The share of cases where the supplier correctly told the household about the Ombudsman was 48% in 2019, 43% in Q4 2024,
  and 48% on average in 2025 (supplier range **25–68%**). Escalation is therefore partly a property of the *supplier's*
  conduct, not only of the household.
* **Of households entitled to refer, ~7% did** (from the existing page). This share is the reason Ombudsman volume is
  a poor proxy for dissatisfaction.
* **The ratio of Ombudsman cases to supplier-recorded complaints is NOT computed here.** The numerator counts *accepted
  cases* and the denominator counts *every expression of dissatisfaction*, per *account*, and a dual-fuel home has two
  accounts. Dividing them gives a ratio that is not a quantity. **Open gap:** an escalation rate per complaint, on a
  single definition.

### 3.4 The link from satisfaction and complaints to departure: effect sizes only where published

There are three instruments. **They measure three different things, and they disagree in the way their definitions predict.**

**(a) Dissatisfied households switch LESS: a state, reported behaviour.** Ofgem CIM wave 6 (Jan–Feb 2025, n=3,458),
Table 56, switching in the last six months: **satisfied 5.4%, not satisfied 4.9%, dissatisfied 3.0%**
(`what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §4). Dissatisfaction is a *disengaged* state. It
sits alongside traditional prepayment, being on a variable tariff, and difficulty paying.

**(b) Complainants switch, and how fast depends on how the complaint was handled: an event, self-attributed
behaviour.** Ofgem/GfK *Complaints to energy companies* (2014). The sample was households who complained in **December 2013**,
interviewed **3–23 February 2014** (so about 2 months after the complaint). Domestic n=2,457. Question H9: *"Have you switched or do you
plan to switch… as a result of your experience with this complaint?"*

| satisfaction with complaint HANDLING | n | **already switched** | plan to switch | no plans |
|---|---:|---:|---:|---:|
| satisfied | 733 | **9%** | 10% | 78% |
| neither | 307 | **17%** | 20% | 54% |
| dissatisfied | 1,405 | **23%** | 35% | 33% |
| all domestic | 2,457 | **18%** | 26% | 49% |

So, within complainants, **the realised switching rate is ~2.6× higher (23% vs 9%) when the handling was poor than when it was
good.** This is the only published dose on the *handling* lever, and handling is a lever the supplier controls. Its limits:

* It is self-attributed ("as a result of") and recalled.
* It is pre-window (2013).
* 15% of the complaints were *about the transfer itself*, so part of "switched" is reverse causation.
* Vulnerable groups switched far less after an equally bad experience: DE 12%, unemployed 13%, income <£10k 11%, disabled 12%.

**(c) "Had or planning to switch": intention mixed with behaviour.** The Ofgem biennial complaints survey (published 22 Sep
2016, fieldwork end of 2015, n=3,049 domestic) found **52%** of complainants *"had or were planning to switch"* (44% in 2014).
**The existing page's "~3× the base rate" was derived from this 52%.** It is not a departure rate. Two published measures show how far
intention runs above behaviour:

* in 2014, 44% switched-or-planned but only **18%** had actually switched;
* in CIM w6, **25%** said they were likely to switch supplier in the next 3 months, while the reported six-month
  switching rate was 5.3%.

**Correction, made beside the claim (it is not a silent revision):** the "~3×" in `satisfaction_drivers_and_the_three_bill_shocks.md`
holds for the *switched-or-planning* share. It is **not** established as a realised departure multiplier. The realised
figure available is (b), and (b) is conditional on having complained. The comparison to a base rate also needs the 2013
switching base, which is pre-window and not in `gb_domestic_switching_rate.json`. **Open gap:** the realised
complainant departure hazard relative to the base, on one window.

**How the three fit together.** It is the "say what it is" result. **A complaint is an engaged act and dissatisfaction
is a disengaged state.** Households that complain are already in contact and already in a choice process. A poorly
handled complaint pushes them out. Households that are merely dissatisfied are, on the published record, *less* likely
to move than satisfied ones. **A world in which low satisfaction raises the departure hazard models the wrong
quantity, and in the wrong direction.**

**Supplier-level corroboration (not a dose).** Littlechild (2021, EPRG WP 2027) built an Overall Customer Satisfaction
score for ~30 suppliers from 2018 to 2020, averaging Ofgem complaints, Which?, Citizens Advice and Trustpilot ratings.
**"Suppliers scoring less than 60 have not survived"**: npower, GreenStar, Extra, Economy, Solarplicity, Flow and Tonik.
The pairwise correlations between the four components were weak to moderate (**0.14 to 0.70**, and Citizens Advice
vs TrustScore −0.12 at the first date). The "satisfaction" instruments therefore do not agree with each other about
which supplier is good. **The CMA's position:** customer service is a **"hygiene factor"**: below a minimum it matters,
above it it stops discriminating (EMI 2016, para 8.17).

**What is not published anywhere this pass found:** a per-unit dose-response from a satisfaction score, an NPS or a
sentiment score to an individual household's switching probability, measured on GB energy. Every published link is
either between bands (a, b) or at supplier level (Littlechild).

### 3.5 The effect of communications

| communication | design | effect | source |
|---|---|---|---|
| **Cheaper Market Offers Letter** (Ofgem-branded vs supplier-branded) | RCT, ~150,000 default-tariff customers, Jun–Aug 2017, switching measured over 30 days | **1.0% → 2.9%** (Ofgem-branded). Supplier-branded was more effective. Internal and external switching both rose. | Behavioural Insights Team, *One letter that triples energy switching*, Nov 2017 |
| **Cheaper Market Offer Communication (CMOC)** from the household's **own** supplier | RCT, ~600,000 customers on default tariffs for ≥3 months, 5 suppliers (3 large, 2 medium), summer 2018, factorial, switching over 30 days | **Control 2.9% → 6.8%** across treatment arms (+134%). **A reminder: 5.9% → 7.5% (+27%).** Including the supplier's *own* cheapest tariff: 6.6% → 7.1%. Channel: letter 7.0% vs preferred channel 6.6%. **71% of switchers chose a tariff not listed on the letter.** **Each £100 of potential saving raises the probability of switching by 1.2pp.** | Ofgem, *CMOC trial* slide deck, Sep 2019 |
| **Database remedy letters** (CMA approach / best-offer) | ~2,400 customers, Jan 2017, 28 days | **~2× switching** against control | BIT, same post; Ofgem *Small Scale Database trial* 2017 |
| **Proactive debt contact** | Rule, not trial | Effect **not published** | Ofgem Consumer Standards decision, 2023 |
| **DD change notice / annual-statement nudge** | none found | **No published effect** on satisfaction, complaints or switching | — |
| **Keeping a complainant informed** | Survey association, not a trial | Only **1 in 4** complainants was given a timetable, and only half of those were kept to. "Not being kept up to date" is one of Ofgem's three named drivers of dissatisfaction. | Ofgem complaints survey 2014; Ofgem satisfaction survey commentary |

Two readings matter for this project:

1. **A letter from your own supplier moves an inert default-tariff household.** The response more than doubles within 30 days,
   a reminder adds a quarter again, and most responders go and shop for themselves. **This is the only published,
   randomised "we contacted this household and it converted" figure.** `knowledge_map.md`'s conversion-desk row says
   nothing isolates that. CMOC partly does: it covers a **default-tariff** population, prompted by a **savings
   comparison**, measured at **30 days**, with internal and external moves counted together.
2. **The communications with published effects all *increase* movement.** None published shows a communication
   *reducing* departure, satisfaction loss or complaints. The retention value of proactive contact is an **open gap**.
   It is the gap any "next best action" lever would rest on.

---

## 4. The rules

| rule | what it requires | source |
|---|---|---|
| **Standards of Conduct**, SLC 0 / 0A | Treat each domestic customer fairly. Behave in a *"fair, honest, transparent, appropriate and professional manner"*. Information complete, accurate, not misleading. A vulnerability principle. Applies to complaints too. In force 26 Aug 2013; updated by the 2023 Consumer Standards. | Ofgem, *Standards of Conduct* guidance; Ofgem complaints report 2014 intro |
| **Consumer Complaints Handling Standards** | SI 2008/1898, in force 1 Oct 2008. Record every complaint on receipt (date, oral or written). Have a published complaints procedure. Signpost the procedure and the redress scheme. Handle complaints efficiently and in good time. **Publish an annual complaints report.** Covers domestic and micro-business customers, and network companies. | legislation.gov.uk/uksi/2008/1898 |
| **8 weeks / deadlock** | The Ombudsman can accept a case after **8 weeks** or a **deadlock letter**, whichever comes first. The household then has **12 months** to refer. The domestic award cap is **£10,000**. The supplier has **28 days** to implement a decision. | Energy Ombudsman, *Our process* |
| **Complaints reporting** | Each quarter, per supplier: complaints per 100k accounts, the share resolved by end of next working day, and the share resolved in 8 weeks. | Ofgem customer service data portal |
| **Price-rise notice**, SLC 23 | At least **30 calendar days' notice** before a price increase or a disadvantageous unilateral variation takes effect. The earlier 65-working-day retrospective allowance was removed. | Ofgem, *Guidance on notification of price increases — SLC 23* |
| **End of fixed term** | Notice **42–49 days** before the end of the term. No exit fee in that window. No auto-rollover onto a new fixed term. | `company_customer_comms.md` §1. **The condition number is not re-verified this pass.** |
| **Consumer Standards** (decision 18 Oct 2023, effective 14 Dec 2023) | Longer opening hours, more responsive channels, free-phone best practice, **proactive payment-difficulty contact after 2 missed monthly / 1 missed quarterly payment**, vulnerable customers prioritised, **suppliers must publish customer-service performance** | Ofgem, *Consumer standards decision* |
| **Citizens Advice star rating** (Ofgem requires suppliers to take part) | **Complaints 35%** (third-party complaints per 10,000 customers from CA Consumer Service, Extra Help Unit, Energy Ombudsman and Advice Direct Scotland; 5★ ≤5, 0.5★ >80). **Ease of contact 30%** (call wait 60% of that, with 5★ <30s and 1★ >300s; email within 2 working days 20%; other channels 20%). **Billing and metering 25%.** **Commitments 10%.** Suppliers with >25,000 accounts. | Citizens Advice, *How the scores are worked out* |
| **DD level and reviews**, SLC 27 | A review of a DD that is out by more than ±5%. The 2022 market review. | `what_bill_shock_is.md` |

**A misattribution in the commons, found this pass:** `company_customer_comms.md` §1 and §7 give *"Tariff change on variable rate: 30
days (SLC 22B)"*. The 30-day price-rise notice is **SLC 23**. SLC 22B is the Ban on Acquisition-only Tariffs. Fix it in
that file.

---

## 5. What a supplier can see, and what it cannot

| quantity | a supplier SEES | a supplier does NOT see |
|---|---|---|
| Satisfaction | Its own CSAT/NPS replies, at the response rate it achieves. **The published market and supplier-group bands** (§3.1), twice a year. | Any non-responder's state. The response is **selected**: people with extreme views and engaged people answer more. Survey answers are noisy and rounded. |
| NPS | Its own survey results only | Any published per-supplier benchmark (none exists) |
| Sentiment | **Every recorded interaction**: call transcripts, chats, emails, complaint text. This is where the supplier's view is *richest*. | The ~94% of households who do not contact it in a quarter, and any household that leaves without a word |
| Complaints | **Every complaint it records**: subject, dates, resolution time, Day+1 and 8-week status. These are the supplier's own data. | How its *recording* compares with peers' (the definition is applied unevenly) |
| Ombudsman | Each case referred about it, the outcome, and the case fee | Which of its 8-week and deadlock households *could* refer and chose not to (most of them, ~93%) |
| Trust | Nothing directly. Market bands from CIM. | Its own households' trust |
| Departure | That a household **left** (a loss notification). Often the reason is unknown. | Why. Whether a complaint, the price or a home move caused it. |
| Communication effect | **Its own controlled experiments**, if it runs them (CMOC was run *through* suppliers) | Any counterfactual it did not hold back |

**The epistemic consequence for this project.** A supplier does not observe "satisfaction". It observes three
**selected** signals: survey replies, contacts and complaints, and departures. Each is filtered differently. The
company-side estimate should be built from those three. The world-side truth should be what generates all three.

---

## 6. What our code does (discovery, 2026-10-05, at the worktree's HEAD `a52651e29`)

`grep -ri sentiment` over `company/ saas/ simulation/ sim/` returns **nothing**. Every other term returns dozens of
files. The parts that matter are below.

### 6.1 World side: what generates the truth

| module | what it does | standing |
|---|---|---|
| `simulation/sim_satisfaction.py` | Latent score = 0.70 − 0.10 per **rate** shock count + income stress + tenure + payment channel (DD 0, SC −0.06, PPM −0.06) ± 0.04 noise | The payment-channel gap is sourced (Wave 20). **0.70, −0.10 and the tenure bonus have no source.** **There is no complaint term and no handling term**, although §3.4 says that is where the dose lives. |
| `simulation/satisfaction_churn.py` | Multiplier **1.30 at low satisfaction, falling to 0.85 at high**, applied to the departure hazard in `customer_events.roll_lifecycle_event` (`satisfaction_score=` from `run_phase2b.py`) | **The direction is refuted by CIM w6 (§3.4a).** The module's own docstring and `sim_satisfaction`'s PPM comment both say so. It stays live. |
| `simulation/feedback_survey.py` | CSAT and NPS sent at renewal off true satisfaction: a U-shaped response propensity (base 8%), noisy reports. Complaint per term = **3% + 35pp if a bill shock**, × an occupancy multiplier. Resolution: 8% go to the Ombudsman (57–120 days, 50% upheld), 25% resolved late (11–56 days), 67% resolved within 10 days. | The survey selection is the right shape. **Every rate is unsourced.** Published comparators: ~1% of accounts per quarter (§3.3); 57% upheld at the Ombudsman (2019); ~7% of entitled households refer. |
| `run_phase2b.py` ~2660 | "Bill shock this term" = **unit rate up more than 20%** (`_NG_BILL_SHOCK_THRESHOLD`) | **This keys complaints, and resentment, to the ONE cause that is commercial (a price rise).** It ignores the two operational causes (a DD reset, a catch-up bill) that the Ombudsman's 56–58% billing share is made of. It also applies the trigger to every population, including DD and PPM households. `simulation/experienced_bill_shock.py` (PB4, per population) exists and feeds `customer_events`, **but not the complaint roll.** |
| `simulation/resentment_ledger.py`, `reputation_index.py`, `activation_energy.py`, `churn_journey.py` | The stock of resentment, a global reputation index, status-quo bias, and a journey state machine | **Log-only.** The journey state, the resentment score and the GRI are written to `churn_journey_log`/`reputation_events_log` and read only by reports (`saas/reporting/annual_report.py`, `css_statement.py`, `tools/generate_dashboard_data.py`). **Nothing reaches `roll_lifecycle_event`.** Of 9 friction types, **3 are ever emitted** (BILL_SHOCK, COMPLAINT_UNRESOLVED, COMPLAINT_RESOLVED_WELL). BILLING_ERROR, PAYMENT_FAILURE, PRICE_INCREASE, OUTAGE, CALL_WAIT_LONG and SWITCHING_BARRIER are declared and never fired. |
| `simulation/contact_propensity.py`, `contact_centre.py` | The world's own contact physics (base 0.05, confusion 0.3, shock 0.5) | It has its own world side (register §3k). The constants are unsourced. |
| `simulation/conversation_response.py` (F1a) | A hidden susceptibility × a message → an action, a channel and a latency | It is reached through the payment-seam and flex adapters. **Its uplift magnitudes are the obvious consumer of the CMOC figures (§3.5).** |

**So: complaints are generated, resolved and logged, and none of it can move a departure.** The only path from experience
to departure is `sim_satisfaction` → `satisfaction_churn`. That path carries **rate shocks** and **demographics**, and
it carries them in the direction the published record refutes.

### 6.2 Company side: what the supplier keeps

| module | what it does | defect found this pass |
|---|---|---|
| `company/interfaces/customer_experience.py` + `company/crm/customer_experience_desk.py` | The seam: the world reports a term boundary, a survey reply or a contact; the company keeps the book (KNIFE §3p) | The shape is right. The resolution outcome (`resolved_on_time`) is **rolled by the world**, so **the company has no lever on the one thing the record says drives departure among complainants: how fast and how well it handles a complaint.** |
| `company/crm/satisfaction_accumulator.py` | Trust: −0.05 per shock, −0.10 per complaint, +0.05 when resolved, decays monthly | Unsourced deltas. It is a company *estimate*, so this is allowed, but nothing has been tested against the published bands. |
| `company/crm/nps_tracker.py` | Promoter ≥9, passive ≥7 | Correct (the definition) |
| `company/crm/css_tracker.py` | Says *"Ofgem's annual CSS survey asks… 6 dimensions… each rated 1–10"*, gives *bottom-quartile "Enhanced Monitoring"*, and has `_INDUSTRY_AVERAGE_OVERALL` 2016–2025 on a 0–10 scale (2022 = 5.2) | **No such instrument was found.** The real survey (since 2018) uses a **five-point** scale reported as % satisfied. No published 0–10 series or quartile trigger matches. **This looks like an invented series with a regulator's name on it.** Imported by `simulation/feedback_survey.py`. |
| `company/regulatory/ombudsman_register.py` | `_FINAL_RESPONSE_TO_REFERRAL_WINDOW_DAYS = 182` ("6 months"); cites "SLC 18.9"; `_HIGH_UPHOLD_RATE_PCT = 50` as an "Ofgem watchlist threshold" | **The published referral window is 12 months**, not 6. The 8-week rule comes from the CHS Regulations and the Ombudsman's scheme, not SLC 18.9. No source was found for the 50% "watchlist". |
| `company/crm/complaints.py` | `OMBUDSMAN_ESCALATION_DAYS = 56`, "per Ofgem SLC 2.7" | The value is right. The citation is wrong (CHS Regulations 2008 / Ombudsman rules). |
| `company/comms/conversation_generator.py` (F1b) | The outbound message brain | Reached only by `background/conversation_gap_ledger.py`. Not in the run. |
| `company/crm/service_quality_monitor.py` | Clarity, complaint and shock bands | The Ofgem attribution was already withdrawn there (2026-09-02). Good. |

### 6.3 What the world would need in order to generate sentiment credibly

**Drivers already in the world:**

* payment method per household;
* income stress;
* tenure;
* rate changes;
* DD review outcomes (`company.interfaces.dd_review_outcome`) and the per-population experienced shock (`experienced_bill_shock.py`);
* arrears and debt state (`WorldDebtBook`, `arrears_engine`);
* a contact propensity;
* a complaint event with a resolution time;
* home moves;
* the debt objection;
* a message-response model (F1a).

**Drivers not in the world, in the order the published record weights them:**

1. **Complaints caused by operational failure.** Disputed usage (22% of billing disputes), disputed balances (8%),
   back-billing (~3.2k Ombudsman cases a year) and transfer problems (15% of complaint subjects). These need **step 2's
   unbilled energy and billing accuracy** to exist first. A catch-up bill or a wrong balance cannot generate a complaint
   until the world produces it.
2. **Handling quality as a company decision.** Resolution time, a timetable given, being kept informed. The world must
   *respond* to how the company handles a complaint (the 9% / 17% / 23% gradient). It must not roll the handling itself.
3. **Complaint → departure, and dissatisfaction ↛ departure.** Two separate edges with opposite signs (§3.4).
4. **Contact capacity.** A queue, so that wait time exists. `CALL_WAIT_LONG` is declared and never emitted. CA weights
   ease of contact at 30%. Wait times are published per supplier (CA star-rating CSV, in `knowledge_map.md` C31 row).
5. **Price-rise notices with their 30-day lead**, and their observed effect. CMOC gives the response to a *savings*
   prompt, not to a *rise* notice. The second is an **open gap**.
6. **Sentiment.** Only after (1)–(4). Text valence is a *readout* of the experiences above. Generating it without them
   would be noise with a label on it, and there is **no published distribution to calibrate it against**.

---

## 7. Gaps (each one is a finding, not a placeholder)

1. **A per-unit dose from satisfaction, NPS or sentiment to an individual household's departure.** Not published for GB energy.
   Only band contrasts exist (§3.4).
2. **The realised departure hazard for complainants relative to the base, on one window.** The 2014 survey gives realised switching
   *within* complainants (9/17/23%) but no base for the same window. The 2016 survey gives only "had or planning".
3. **The escalation rate per complaint on a single definition.** It cannot be formed from Ombudsman-accepted cases over
   supplier-recorded complaints (§3.3).
4. **The historical complaints-per-100k market series 2018–2024.** On the Ofgem portal. Not captured this pass. **Cheap to close.**
5. **A per-supplier NPS.** Not published by any regulator. Only the 2019 size bands.
6. **Any published distribution of sentiment** in GB energy supplier contacts.
7. **The retention effect of proactive contact**, and **the effect of a DD-change notice or a price-rise notice** on complaints,
   satisfaction or switching. None found. CMOC measures the *opposite* lever (prompting to move).
8. **Which? methodology and per-supplier customer scores.** Secondary reports only this pass (≈12,000 respondents, Sep–Oct
   2025). The primary was not fetched.
9. **Outages as a supplier-complaint driver.** No published share. Outages are mostly a DNO matter.
10. **Trust per supplier.** CIM publishes only the market: **62%** trust their own supplier to treat them fairly, and **41%** trust the
    sector (Jan–Feb 2025, n=3,458).

---

## 8. What this says about the order of work

The canon puts communications, sentiment and NPS last because they are *"the hardest to simulate credibly and the most
dependent on the knowledge in step 1"*. **That holds for sentiment and NPS, and the evidence above strengthens it.**
They are state readouts with no published dose. One of them (dissatisfaction) points the opposite way from the folk
model, and the other (NPS) adds no information over satisfaction (Keiningham et al. 2007).

**Three things in this area do not belong at step 7. The evidence for each is below.**

**Proposal 1: complaints caused by billing failure belong in step 2, not step 7.**
*Evidence:*

* billing is **56–58% of all Ombudsman cases** (2024, 2025);
* "disputed usage" and "disputed balances" together are **30% of billing disputes**;
* back-billing is ~3,200 cases a year.

These are the complaints that unbilled energy and billing accuracy (step 2) *generate*. The world currently keys
complaints to a >20% **unit-rate** rise, which is the one cause that is a commercial choice, not an operational failure
(§6.1). Building step 2 without a complaint output would leave its most visible consequence unmodelled. Rekeying the
complaint roll onto step 2's outputs and the PB4 per-population shock is small. It belongs **with** step 2.

**Proposal 2: complaint HANDLING → departure is a cheap, credible piece, and it belongs with step 3 or step 4, not step 7.**
*Evidence:* the 2014 survey's within-complainant gradient. Realised switching was **9% / 17% / 23%** by handling
satisfaction (n=2,445), a ~2.6× spread on a lever the supplier controls. There is also the CMA's "hygiene factor" reading, and
Littlechild's supplier-level non-survival below OCS 60. The world already generates complaints and resolution times
(`feedback_survey.py`). What is missing is the edge to departure and the transfer of handling from the world's RNG to a
company decision. This is a *per-customer decision* (step 4) and a *per-customer churn input* (step 3). It also keeps
the world from teaching the company that dissatisfaction drives churn: the edge is keyed to an **event the supplier
records**, not to a latent state. **Caveats that must travel with it:**

* the figure is self-attributed;
* it is pre-window (2013);
* part of it is reverse causation (transfer complaints);
* there is no base for the same window.

So it is a *band to check a world against*, not a constant to set.

**Proposal 3: two fidelity defects should be fixed now, independent of the order.** Both are small and both are
already refuted by evidence in hand.

* (a) `satisfaction_churn` raises the departure hazard for dissatisfied households, against CIM w6. At minimum the low
  end should be neutral until (2) exists. This is a baseline fidelity change and is decided blind to company results.
* (b) `ombudsman_register`'s 6-month window should be 12 months.
* (c) `css_tracker`'s regulator-attributed 0–10 series should become an explicit `None` with its reason.

**Also relevant to step 5 (levers): the CMOC trial is published, randomised evidence on supplier-initiated contact.**
It shows 2.9% → 6.8% at 30 days, a reminder +27%, and +1.2pp per £100 of savings. It answers part of the conversion-desk
row's "response rate to a supplier-initiated approach" gap, and it is the obvious anchor for F1a's uplift magnitudes.
It should be cited from that row when next-best-action knowledge is written.

**Nothing here argues for moving sentiment or NPS earlier.** Sentiment has no published distribution. NPS adds no information over satisfaction.
Both are readouts of experiences that the world will only generate once steps 2–4 exist.

---

## Sources

- Ofgem, *Customers' satisfaction with their supplier — supplier level findings, July to August 2025* (pub. 2 Dec 2025), n=3,790. https://www.ofgem.gov.uk/sites/default/files/2025-12/Customers%27-satisfaction-with-their-supplier-supplier-level-findings-July-to-August-2025.pdf
- Ofgem/CA Energy Consumer Satisfaction Survey waves Jan 2025, Jul–Aug 2025, Jan 2026 (cited via `satisfaction_drivers_and_the_three_bill_shocks.md`); Aug–Sep 2023, Jan–Feb 2024 and Jul 2024 pages on ofgem.gov.uk/research (trend figures).
- Ofgem/GfK NOP, *Complaints to energy companies* (2014), fieldwork 3–23 Feb 2014, complainants of Dec 2013, domestic n=2,457. https://www.ofgem.gov.uk/sites/default/files/docs/2014/09/ofgem_complaints_report_final_8_august_2014_0.pdf — Figures 2, 54–56.
- Ofgem, *Ofgem publishes biennial survey on how suppliers handle complaints* (22 Sep 2016), n=3,049 domestic. https://www.ofgem.gov.uk/press-release/ofgem-publishes-biennial-survey-how-suppliers-handle-complaints
- Ofgem, *Consumer impacts of market conditions survey: wave 6* (Jan–Feb 2025, n=3,458). https://www.ofgem.gov.uk/research/consumer-impacts-market-conditions-survey-wave-6-january-february-2025 ; Table 56 via `what_a_supplier_can_observe_about_switching_propensity_cim_w6.md`.
- Ofgem customer service data portal (complaints per 100k, Q4 2025 and Q1 2026). https://www.ofgem.gov.uk/news-and-insight/data/data-portal/customer-service-data
- Energy Ombudsman: *Annual data 2025* (20 Mar 2026) https://www.energyombudsman.org/news/energy-ombudsman-annual-data-2025 ; *Reports 24% drop in complaints* (15 May 2025) https://www.energyombudsman.org/news/energy-ombudsman-reports-24-drop-in-complaints ; *Resolves more complaints as demand increases* (3 Aug 2020) https://www.energyombudsman.org/news/energy-ombudsman-resolves-more-complaints-as-demand-increases ; *Our process* https://www.energyombudsman.org/our-process ; *Explaining our complaints data* https://www.energyombudsman.org/complaints-data/explaining-our-complaints-data
- Littlechild, S. (2021), *An Overall Customer Satisfaction score for GB energy suppliers*, EPRG Working Paper 2027, 12 Mar 2021. https://www.jbs.cam.ac.uk/wp-content/uploads/2023/12/eprg-wp2027.pdf — §2 (CMA paras 8.17, 8.30, 9.106; complaint range Q4 2019), fn 12 (Ofgem 2019 NPS bands), Table 1 (correlations), §4 (survival below 60).
- Keiningham, T., Cooil, B., Andreassen, T.W., Aksoy, L. (2007), *A Longitudinal Examination of Net Promoter and Firm Revenue Growth*, Journal of Marketing 71(3):39–51. Reichheld, F. (2003), *The One Number You Need to Grow*, Harvard Business Review, Dec 2003.
- Institute of Customer Service, UKCSI (July 2026) https://www.instituteofcustomerservice.com/research-insight/ukcsi/ ; *Customer satisfaction with the utilities sector remains low* (8 Apr 2019).
- Behavioural Insights Team, *One letter that triples energy switching* (Nov 2017). https://www.bi.team/blogs/one-letter-that-triples-energy-switching/
- Ofgem, *Cheaper Market Offer Communication trial* (27 Sep 2019) and slide deck https://www.ofgem.gov.uk/sites/default/files/docs/2019/09/cmoc_slide_deck.pdf
- The Gas and Electricity (Consumer Complaints Handling Standards) Regulations 2008, SI 2008/1898. https://www.legislation.gov.uk/uksi/2008/1898
- Ofgem, *Guidance on notification of price increases — Standard Licence Condition 23*. https://www.ofgem.gov.uk/guidance/guidance-notification-price-increases-standard-licence-condition-23
- Ofgem, *Consumer standards decision* (18 Oct 2023, effective 14 Dec 2023). https://www.ofgem.gov.uk/decision/consumer-standards-decision
- Ofgem, *New standards of conduct for suppliers — domestic consumers*. https://www.ofgem.gov.uk/publications/new-standards-conduct-suppliers-domestic-consumers
- Citizens Advice, *How the scores are worked out* (star rating). https://www.citizensadvice.org.uk/consumer/energy/energy-supply/get-a-better-energy-deal/compare-domestic-energy-suppliers-customer-service1/how-the-scores-are-worked-out/

*Fetched live 2026-10-05, except where an in-repo page is named as the carrier. The Which? figure in gap 8 is from a secondary report and is used only to name the gap.*
