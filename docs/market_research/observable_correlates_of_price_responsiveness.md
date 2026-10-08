**Knowledge:** acquisition-and-retention-economics

# Does price responsiveness correlate with what a supplier can see?

**Research completed 2026-10-08, for the director's question of the same day.** In his words: *"My 27
Aug ruling made per-household price sensitivity nearly independent of anything a supplier can
observe. Find what published evidence says about how far responsiveness correlates with signals a
supplier holds (past switching, acquisition channel, fixed vs SVT, contact history), and whether our
engagement axis already carries some of that. If the world hides correlations that are real,
targeting is rigged to fail. Propose the change and I'll rule."*

**This note's own limit, stated first.** This pass had no web search left. Its sources are three
documents fetched today (CMA final report, FCA GIPP final report, Ofgem Sustained Engagement), plus
primary texts already fetched and quoted by earlier passes, which are cited through the in-repo note
that holds them. Nothing new was searched for, so a **GAP** below means "not found in the record on
file". It does not mean "not published anywhere".

---

## 0. Two quantities, named before anything is measured

"Responsiveness" splits into two different things, and the world already models them on separate
axes:

- **E: does the household look at all?** This is engagement, whether it enters a choice process at a
  renewal. In the world: `household_segments.active_renewal_probability_for_customer`, the
  archetype × payment-channel gate.
- **S: once it is looking, how far does a price gap move it?** This is elasticity. In the world:
  `population_draw.price_elasticity_for_customer`, a lognormal weight on the perceived differential.

A supplier sees the product of the two, P(leave | price move) ≈ E × S × slope. Almost every
published figure below measures **E**, or the product. Almost none isolates **S**. The 27 August
ruling was about **S**. Read each finding with this split in mind.

---

## A. Published evidence

### A1. Tariff type, fixed vs SVT: about 2.8× on switching (E)

- **Ofgem CIM wave 6 data tables, Table 56, question C4** (n=3,458). In the past six months, 7.0% of
  fixed-tariff households switched supplier, against 2.5% of variable-tariff households: **2.8×**.
  Source: `ofgem.gov.uk/sites/default/files/2025-07/Consumer%20impacts%20of%20market%20conditions%20survey%20wave%206%20data%20tables.xlsx`,
  parsed 2026-09-05 in `what_a_supplier_can_observe_about_switching_propensity_cim_w6.md` §3.
- **CMA Energy Market Investigation, Final Report, 24 June 2016, ¶3.32.** *"suppliers are able to
  price discriminate between domestic customers on an SVT and those on a non-standard tariff."* At
  ¶3.33: *"customers do not fall into discrete camps of 'engaged' and 'disengaged'. There is a
  variety of degrees of engagement."* Source:
  `assets.publishing.service.gov.uk/media/5773de34e5274a0da3000113/final-report-energy-market-investigation.pdf`,
  fetched 2026-10-08. Real suppliers did segment on this observable, and it paid.
- **Ofgem 2016 engagement survey (TNS BMRB, Aug 2016).** In the most engaged "Switched On" segment,
  88% pay by direct debit and 68% are on a fixed term. In the "Unplugged" fifth, 35% are social
  grade DE and 63% are daily internet users, the lowest of any segment. Source:
  `ofgem.gov.uk/sites/default/files/docs/2016/08/consumer_engagement_in_the_energy_market_since_the_retail_market_review_-_2016_survey_findings.pdf`.

### A2. Payment method: about 3.4× on switching (E), and a prompt barely moves prepayment

- **CIM w6, Table 56.** Switched in the past six months: standard credit 5.7%, direct debit 5.6%,
  traditional prepayment 1.7%. Credit against traditional PPM is **3.4×**. Same source as A1.
- **Ofgem CMOC trial (RCT, ~600,000 default-tariff customers, 5 suppliers, summer 2018, report
  Sept 2019).** Over 30 days, non-prepayment households went from 3.2% switching in control to 8.4%
  treated. Prepayment households went from 1.4% to 1.8%. The "woken share" is 0.054 against 0.004.
  This is confounded: the mean saving on offer was £278 for non-PPM and £78 for PPM. Ofgem's summary:
  *"more effective on some customer sub-groups than others, but there was no sub-group for whom it
  was ineffective"*. Source: `ofgem.gov.uk/system/files/docs/2019/09/cmoc_report_final_updated_template_0.pdf`,
  via `how_households_respond_to_supplier_contact.md` §2.4.

### A3. Past switching: weak in the disengaged tail, strong after a prompted channel

- **Ofgem, *Sustained Engagement* (Oct 2020).** This followed up the 2018 Collective Switch RCT:
  55,000 customers who had been on an SVT for 3+ years. In the no-letter control arm, those who
  switched during the trial switched again at **31%** over 17 months. Those who did not switched at
  **33%**. Ofgem: they *"were no higher than"* the non-switchers (p.16). Intervention-arm switchers
  re-switched at **63%**, which Ofgem attributes to Energy Helpline re-prompting at tariff end.
  Source: `ofgem.gov.uk/sites/default/files/docs/2020/10/sustained_engagement_pdf_0.pdf`, fetched
  2026-10-08.
- **CIM w6, "switched in last 2 years", 21.6% against 5.3%.** This is a **tautology, not evidence**:
  the six-month outcome sits inside the two-year condition (100.0% overlap; CIM w6 note §2). It must
  not be used.
- **GAP:** no published GB energy panel gives P(switch at t+1 | switched at t) outside the 3+-year
  default tail.

### A4. Acquisition channel: a large effect, but the prompt causes it, not the household

- **Sustained Engagement, Annex B.** Trial switchers who went through EHL (the PCW-run collective
  switch) re-switched within 17 months at **69%**. Those who switched externally by going direct to a
  supplier re-switched at **38%**. Among EHL switchers, those who accepted EHL marketing re-switched
  at **73%**, against **59%** for those who did not. Ofgem credits *"the effectiveness of EHL's
  communications as EHL prompted these customers at their tariff end date"*. Of those who took the
  collective-switch tariff itself, 70% switched again within 17 months (Annex C).
- **CMA Final Report, Tables 8.5, 8.6, 8.9, 8.10 and ¶8.174–8.176.** These give acquisitions by
  channel: PCW, own website, telesales, doorstep, house-builder and housing-association bulk, and home
  move. Every cell is **redacted**. ¶8.174: SVT acquisitions through house builders and housing
  associations *"do not represent an active decision on the part of the customer"*. ¶8.176: PCWs were
  *"a small proportion"* of British Gas SVT acquisitions. ¶9.258: restricted-meter customers outside
  incumbent regions were *"largely acquired through doorstep selling"*.
- **GAP:** no published GB figure gives churn or price response by acquisition channel. The CMA
  holds it and redacted it.

### A5. Contact history: a 4× gradient on one engagement marker

- **Ofgem CMOL trial (RCT, N=137,876, Nov 2017), control arm, 30-day switching.** Households that
  submitted a meter read in the previous year switched at **1.3%**. Those that did not switched at
  **0.3%**, a ratio of 0.23. By SVT tenure: 1–3 years **1.3%**, 3+ years **0.7%**, a ratio of 0.54.
  Ofgem calls both *"proxy variables for engagement"* (§3.46). Source:
  `ofgem.gov.uk/system/files/docs/2017/11/cmol_report_0.pdf`, via
  `does_a_disengaged_household_leave_the_default_tariff_less_at_the_same_tenure.md` §1.
- **Satisfaction runs backwards (CIM w6).** Satisfied households switched at 5.4% and dissatisfied
  ones at 3.0%. The intuition that complainers leave is not supported for **E**.
- **Telecoms analogue, Ascarza, Iyengar & Schleicher, *J. Marketing Research* 53(1), Feb 2016.** A
  field experiment that prompted customers towards a cheaper plan **raised** churn from 6% to 10%. The
  rise was heterogeneous on past-usage observables: +3.6 percentage points on average, +2.4 for
  customers with a positive usage trend. Read from the session copy of the paper, 2026-10-08.
- **GAP:** no published GB figure gives churn or price response by inbound call or complaint
  history.

### A6. The cleanest evidence that responsiveness is observable comes from insurance

- **FCA, *General insurance pricing practices*, Final Report MS18/1.3 (Sept 2020, updated Dec
  2020).** For a typical risk, a motor customer of 5+ years pays **£85** more than new business on
  £285. Buildings: £108 more on £130. Contents: £82 more on £56. This covers 10m policies (¶3.9).
  ¶3.11: firms *"price discriminate based on consumers' awareness of how the market works"*. ¶3.19:
  *"younger consumers being more likely to switch providers"*. ¶3.20: *"The main factor correlated
  with tenure is age"*: motor tenure is under 2 years below age 45 and over 4 years at 65+. ¶5.24:
  *"consumers that firms identify at new business as price sensitive"*. Source:
  `fca.org.uk/publication/market-studies/ms18-1-3.pdf`, fetched 2026-10-08.
- **FCA EP25/2 (July 2025), the evaluation.** Insurers *"identify the consumers least likely to
  switch at renewal based on their characteristics"*. After the 2022 ban, attrition **rose among
  low-tenure and fell among high-tenure** customers. Via `next_best_action_and_cross_sell.md` §4.3.
  That this was observable enough to earn £1.2bn a year is evidence that, in a comparable
  annual-renewal market, responsiveness is far from orthogonal to tenure, age and channel. It is
  **E**×**S** combined, and it is insurance, not energy.

### A7. Evidence on S alone: price is weighted homogeneously

- **Ofgem/BMG, *Understanding Consumers' Energy Tariff Choices* (conjoint, n=3,235, published July
  2025).** *"Choices were similar across demographics… feature importance scores are generally quite
  stable."* The importance of savings is 44% for high-price-focus subgroups against 35% for low, a
  **1.26×** spread. Spending against switching propensity has a Spearman correlation of −0.07 to
  +0.05. Customers who rate their supplier 0–2 stars weight savings at 44%. Source:
  `ofgem.gov.uk/sites/default/files/2025-07/understanding-consumers-energy-tariff-choices-%20research-report-2024.pdf`.
- **CMA Appendix 9.1 (GfK, n=6,999).** 81% of all respondents cite price as important, against 93%
  of those who shopped around or switched in the last year. This is the direction of an
  **E**↔**S** coupling, measured as salience rather than as an elasticity. Via
  `continuous_behavioural_engagement_w2_14.md` §3a.
- **CMA Final Report ¶9.108(g), a party's submission.** The gains from switching *"did not differ
  very much between those who had, and those who had not, switched recently"*. That argues against a
  strong **S** split by engagement.
- **GAP:** no published GB source gives an elasticity, meaning the response to a price gap given
  that the household is looking, split by tariff type, past switching, channel or contact history.

---

## B. What the world does now

**The ruling (director console, 2026-08-27T16:36Z, verbatim):**

> *"The Ofgem subgroup range is a between-group statistic — it says nothing about spread between
> individuals, and elasticity is typically close to orthogonal to observables. That's why couponing,
> time-limited offers and price walks work at all: you can't tell in advance who responds. So the
> 1.26x is right in direction and the wrong quantity, and it understates the per-household randomness
> there should be. Draw genuine within-segment variance, not just a subgroup mean shift."*

**S, elasticity** (`simulation/population_draw.py`):

- The level is high, medium or low. It is drawn by `_draw_curriculum_axis` on its own substream and
  **crossed**, meaning independent, with green stance and channel preference. It is also independent
  of engagement, payment method, tenure and every other draw.
- It is multiplied by a within-segment lognormal sized so that the segment explains R² =
  **`PRICE_ELASTICITY_SEGMENT_R2 = 0.02`** of the variance. That number is anchored on the BMG spend
  Spearman (A7), which concerns spend, not the observables in the question.
- **So S carries no supplier-observable correlate at all.** Even its own segment explains only 2%
  of it, and that segment is itself invisible to the company.

**E, the engagement axis** (`simulation/household_segments.py`):

- There is a fixed archetype per household: ACTIVE 0.45, PASSIVE 0.35, DISENGAGED 0.20, from a hash
  of the customer id. The per-renewal active probability is 0.50, 0.24 and 0.20 respectively, refit
  on 2026-10-05 to the Sustained Engagement control arm. That leaves past-choice persistence at
  ×1.26, against the source's ×0.94.
- This is multiplied by a mean-preserving **payment-channel** factor from CIM w6: DD 0.056, SC 0.057,
  PPM 0.031.
- Engagement also scales inbound **contact** (`contact_propensity.ENGAGEMENT_CONTACT_MULTIPLIER`:
  1.25, 1.00, 0.45).

**What crosses the wall** (`company/interfaces/sim_interface.py`):

- **Payment method crosses.** `get_payment_method`'s docstring says it does so because it is
  engagement's antecedent.
- **Fixed vs SVT crosses**, as the outcome `event["is_active_renewal"]`, together with the company's
  own renewal history.
- **Acquisition channel crosses** via `notify_acquisition(channel=…)`, which takes home-move-win or
  market-acquisition.
- **Contacts are generated** with the engagement multiplier. No company churn model reads them per
  account; the only company-side reader found was `company/analytics/billing_experience_view.py`.

**Does the engagement axis already carry supplier-observable correlates? Yes, for E only.**

- Payment method carries about 1.8× between DD and PPM.
- Tariff status is endogenous to E: an active renewal takes a fix, a passive one rolls to SVT.
- Tenure on default is corroborated by CMOL: the world gives 0.50 where CMOL gives 0.54.
- Contact volume runs with E.
- Past choice is deliberately weak (×1.26), which matches the only RCT.

`company/pricing/discovered_price_sensitivity.py` (B8) already learns a price-response correction
**per payment method**. Its own docstring puts the world's median slope at prepayment 0.118, DD
0.038 and standard credit 0.014. All of that spread is E, not S.

**What the world hides, and it is a structural fact, not a parameter:**

1. **No selection at acquisition.** `acquisition_funnel._quote_to_application_rate` responds to
   price position with one population multiplier. A won prospect therefore keeps the population mix
   of E and S, even though winning it *was* an act of shopping. Every real source above (A1, A4, CMA
   ¶8.176) says switchers-in are drawn from the engaged and price-led end. Nothing in the world makes
   a PCW-priced or discount-won customer differ from a home-move win.
2. **S is independent of E.** The direction of a coupling is supported (A7, CMA 81%→93%). Its
   magnitude is a **GAP**.

---

## C. Proposal (a recommendation, for the director's ruling)

**What the evidence supports, and roughly how strongly:**

| Observable (company-side) | On E (looks) | On S (moves once looking) | In world today |
|---|---|---|---|
| Fixed vs SVT / rolled-to-default | ~2.8× (CIM w6) | GAP; direction + (CMA 81→93%) | E yes (endogenous), S no |
| Payment method | ~3.4× credit:trad-PPM (CIM w6) | GAP (CMOC confounded) | E yes, S no |
| Tenure on default | ~0.54× 3+yr vs 1–3yr (CMOL RCT) | GAP | E yes |
| Past switching | ~×0.94 in 3+yr tail (Ofgem RCT); unknown elsewhere | GAP | E weak (×1.26), S no |
| Acquisition channel | 69% vs 38% re-switch, prompt-driven (Ofgem) | GAP (CMA redacted) | **no** |
| Contact / meter-read history | 0.23× non-readers (CMOL RCT) | GAP | E via contacts, S no |

**The finding.** The world does not hide the large correlations. They are on **E**, and it carries
them. It hides two things:

- **Selection at entry.** This is real, and nothing published needs to be invented to model it.
- **Any E↔S coupling.** Its direction is evidenced and its size is not.

The 27 August ruling governs **S**, and nothing on file contradicts it: BMG's homogeneity is direct
evidence for it.

**Recommended change, smallest first:**

1. **Selection at acquisition. No new number; recommended.**
   - Let the funnel's price stage read each prospect's own elasticity, through the same
     `perceived_price_differential` the renewal decision already uses.
   - Let a prospect enter the market with weight equal to its own active-renewal probability.
   - The correlation between acquisition price position or channel and later responsiveness then
     **emerges** from draws the world already has.
   - The company sees only its own quote log, win price and channel, so the wall is untouched.
2. **Couple S's existing segment level to E's rank. Optional, bracketed.**
   - Draw high, medium or low by rank on the engagement propensity, instead of crossing it.
   - The 0.02 R² and the 1.26× stay unchanged, so this caps by construction how much S any observable
     can reveal.
   - The coupling strength is a **GAP**. Run the two ends, independent and comonotone, and report
     both. Do not pick a middle.
3. **Not recommended:** a past-switch state-dependence term. The only RCT says ×0.94 in the tail,
   and the world is already above it.

**What would show it mattered in B8.** B8 currently finds no cut pays at any size. At 14% margin it
would need about **3.7×** the world's response; at 1.9% it would need about 25×.

- Because R² on S is at most 0.02 and the segment spread is 1.26×, no S correlate can deliver 3.7×.
  **Only E correlates, at about 2–4×, are the right order.**
- **Pre-register before running.** Add a price-legal observable read to `estimate_offer_effect_by_channel`:
  - acquisition route, or acquired below the market average;
  - tenure on default;
  - ever actively renewed.
- **Grade.** On fresh seeds 101 and 202, the change mattered if:
  - (a) one cell's true effect against its break-even reaches at least 1 at 14% margin;
  - (b) the learned decision offers the cut to that cell and not to the others;
  - (c) it beats both "cut for none" and "cut for all" beyond the seed spread;
  - (d) with change 1 switched off, the same pipeline returns to 0% offers.
- If (d) fails, the lift came from E correlates that already exist. Change 1 did not earn it.
- **Director's ruling needed on one adjacent point.** The ruling of 2026-09-23, as recorded in
  `enriched_churn_estimate.channel_blind`, says *"a price keyed to the meter may not"* vary. Does the
  same bar apply to a retention offer keyed to acquisition route or tenure on default? FCA banned
  tenure pricing in insurance in 2022. Whether a GB energy retention discount by tenure is acceptable
  is a practitioner and regulatory question this note cannot settle.

## Sources fetched this pass (2026-10-08)

- CMA, *Energy Market Investigation: Final Report*, 24 June 2016,
  https://assets.publishing.service.gov.uk/media/5773de34e5274a0da3000113/final-report-energy-market-investigation.pdf
- FCA, *General insurance pricing practices: Final Report* MS18/1.3, Sept/Dec 2020,
  https://www.fca.org.uk/publication/market-studies/ms18-1-3.pdf
- Ofgem, *Sustained Engagement*, Oct 2020,
  https://www.ofgem.gov.uk/sites/default/files/docs/2020/10/sustained_engagement_pdf_0.pdf

All other sources are cited above through the in-repo note that fetched and quoted them.
