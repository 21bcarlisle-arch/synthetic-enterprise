**Knowledge:** communications-sentiment-and-nps

# Reputation, resentment and feedback, calibrated against the GB record: what each world constant rests on, and where the code runs the wrong way (2026-11-02)

This page answers the director's steer of 30 Oct, *reputation is a stock and the supplier listens through biased
feedback* (`docs/staging/advisor/DIRECTOR_STEER_REPUTATION_IS_A_STOCK_AND_THE_SUPPLIER_LISTENS_THROUGH_BIASED_FEEDBACK_2026-10-30.md`).
It covers the NOW half only, as drafting: Ask 1 (calibrate from data) and the evidence for Ask 2's stock split. The
competitive asks are filed under the competition topic (§6), not built. **No world or company value changes here**, except the log-only repair-decay fix in §5 (D1, 2026-11-02).
World build waits for the correctness exit test (`docs/direction/priority_order.yaml`, `correctness_stretch`).

It starts from the advisor's evidence pack
(`docs/staging/advisor/done/DIRECTOR_EVIDENCE_BRAND_EQUITY_REPUTATION_AND_FEEDBACK_LOOPS_2026-10-30.md`, "the pack"),
treated as a starting point to verify, not as the answer. It builds on
`docs/market_research/communications_sentiment_and_nps.md` ("the sentiment page"), whose §3.4 and §6 already hold the
departure evidence and the code discovery. That evidence is not repeated here.

Grades, per the 30 Oct 16:51 data standard: **D** derived by us from primary data, with the method named; **P**
reported in a primary publication by the data holder; **S** a secondary summary; **A** an assumption, with a range. A
world parameter may rest on D or P. S alone never sets one.

## 0. What each thing is, before any number

Seven quantities are in play. The pack and the code use "reputation" and "trust" for several of them.

| # | Quantity | Whose is it | Unit | What moves it |
|---|---|---|---|---|
| 1 | **Per-customer resentment** | The household's (hidden) | A stock of grievance | Friction the household met; it fades |
| 2 | **Satisfaction state** | The household's (hidden) | What it would answer if asked, 0-10 | Its recent experience, resentment included |
| 3 | **Trust in its own supplier**, in two parts: to treat it fairly, and to charge a fair price | The household's (hidden) | Yes / no, per part | Treatment and price, separately (§1, row 4) |
| 4 | **Portfolio reputation** | The world's view of one supplier (hidden) | An index | Public events about that supplier; it fades, damage more slowly than gains (pack, row 2) |
| 5 | **Sector trust** | The world's view of all suppliers | % trusting "energy suppliers" | Sector events (2021 failures, the 2022 crisis) |
| 6 | **Advertising goodwill** | The world's response to one supplier's spend | A fast-decaying stock | Paid acquisition spend |
| 7 | **What the supplier hears**: survey replies, organic reviews, invited reviews, complaints, the regulator's panel | The supplier's (observable) | Each in its own unit | All of 1-5, each through its own selection |

Row 7 is five channels with five different selections, not one. **Only the regulator's random panel is unselected.**
Rows 4 and 5 are about one supplier and about all suppliers, respectively. Row 5, and row 4's effect on *prospects
choosing between suppliers*, are competitive. Under the 17:20 addendum they wait for the competition topic.

## 1. The pack's load-bearing figures, checked against primary sources (2026-11-02)

| # | Pack claim | Pack grade | Our check | Result |
|---|---|---|---|---|
| 1 | British Gas energy accounts fell 742k in 2018, with "634,000 fewer net losses" than 2017, and brand NPS flat | P | Centrica AR 2018, p.20, read verbatim (`data/lake/centrica_annual_report_2018/`) | **Confirmed, with two corrections.** (a) These are **net** losses (losses minus gains), not gross churn. A churn rate cannot be formed from them. (b) "Brand NPS was flat" is UK Home's, in words only. The +9.4 to +10.0 KPI on p.19 is the **group** aggregate across six businesses, not British Gas's. |
| 2 | 2017 net losses ≈ 1.38m (742k + 634k) | A | Same text | **Confirmed as arithmetic** (A, derived from P). |
| 3 | About 12-13m accounts, so 742k ≈ 6% a year | [unverified] | Not found in the report's text extract | **Stays a GAP.** The "6-10% of accounts a year" calibration target in the pack's E1 row 6 has no verified denominator, and it is a net figure. **Do not use it as a churn target.** |
| 4 | Own supplier treats fairly 45%, charges a fair price 38%, sector 34% (2021) | P | Ofgem/Ipsos Consumer Survey 2021, slides 44-45, n = 4,037, fieldwork 19 Aug-17 Sep 2021 (`data/lake/ofgem_consumer_survey_2021/`) | **Confirmed.** Engaged 48% / 40%, disengaged 42% / 36%. The inertia sentence is on p.3, verbatim: "for those disengaged high levels of trust may also increase inertia". |
| 5 | Later Ofgem trust 60% own / 36% sector (via Utility Week) | S [unverified] | The sentiment page §7 row 10 already holds CIM Wave 6 (Jan-Feb 2025, n = 3,458): **62%** own supplier to treat fairly, **41%** the sector | **Corrected:** use CIM W6's 62 / 41 (P). The S figure is retired. The own-above-sector gap (21 points in 2025, 11 in 2021) is **confirmed**. |
| 6 | Trustpilot: Octopus 4.8, 90/5/1/<1/3; British Gas 4.4, 66/8/3/3/20; both invite; reply rates 97% and 99% | P | Both profile pages, re-read 2026-11-02 | **Confirmed.** Review totals moved: Octopus 912,042 (pack 909,090), British Gas 360,708 (pack 360,288). Both pages say the company "invites their customers to review, whether positive or negative". |
| 7 | British Gas review negativity ≈ 3.8× its survey dissatisfaction; Octopus ≈ 1.2× | A | 23% 1-2★ against 6% dissatisfied; 3-4% against 3% | **Confirmed as arithmetic.** It mixes two populations: Trustpilot's British Gas page also carries boiler and home-services reviews, and Centrica's own report puts a 52% H1 2018 rise in complaints on boiler breakdowns. So **the 3.8× is an upper bound on the energy-only selection effect**, not a measure of it. |

**Not re-verified this pass**, and graded as the pack graded them: the [lit] academic sources (Bolton 1998; Keiningham
2007; de Haan 2015; Hu, Pavlou and Zhang 2009; de Matos et al. 2007; Leone 1995), the Energy Ombudsman 2025 figures,
Which? 2025 (33% chose on reputation against 45% on price), and the Octopus press releases. None of these may set a
parameter until it is read at source.

## 2. Derived: does distrust move households, and where to? (D, CIM Waves 3-6)

The pack says "inertia, not trust, keeps overcharged customers". Ofgem's CIM survey crosses its revealed switching
question (C4) by "Trust energy supplier to treat you fairly" in all four published waves, so the claim can be tested
on the data rather than on a summary.

**Method.** Source: `data/lake/ofgem_cim_waves4_6_2023_2025/cost_worry_wtp_and_revealed_switching_by_column.csv`
(Wave 3 Table 87, a 12-month window; Waves 4-6 Tables 94, 70 and 56, a 6-month window), as Ofgem printed it. The
difference is "not trust" minus "trust". The 95% interval is 1.96 × √(p₁q₁/n₁ + p₂q₂/n₂) on Ofgem's own **effective**
bases. Nothing is reweighted.

| Wave (window) | Moved to a new supplier: trust / not trust | Difference | Changed tariff with the same supplier: trust / not trust | Difference | Any switch: trust / not trust | Difference |
|---|---|---|---|---|---|---|
| 3, 2022 (12m) | 6.1% / 9.8% | **+3.7 ± 2.7** | 16.9% / 11.8% | **−5.0 ± 3.2** | 23.0% / 21.6% | −1.3 ± 3.9 |
| 4, Jul 2023 (6m) | 4.0% / 6.0% | +2.1 ± 2.1 | 12.3% / 9.4% | **−3.0 ± 2.8** | 16.3% / 15.4% | −0.9 ± 3.4 |
| 5, Jan-Feb 2024 (6m) | 5.4% / 6.7% | +1.4 ± 2.5 | 13.4% / 8.2% | **−5.2 ± 2.9** | 18.8% / 14.9% | **−3.9 ± 3.7** |
| 6, Jan-Feb 2025 (6m) | 4.9% / 5.8% | +1.0 ± 2.3 | 18.3% / 12.0% | **−6.3 ± 3.4** | 23.1% / 17.9% | **−5.3 ± 3.9** |

Effective bases: trust 1,615-2,006; not trust 476-608.

**What it shows.**
- **Distrust moves households out, and trust keeps the move in-house.** Non-trusters moved supplier more in all four
  waves (ratio 1.2-1.6×). That difference clears its interval only in Wave 3, though it has the same sign in all four.
  Trusters changed tariff with their own supplier more in all four waves (ratio 1.3-1.6×), and that difference clears
  its interval every time.
- **Total movement barely differs** in Waves 3-4. In Waves 5-6 trusters move *more* in total. So trust does not
  produce inertia here: it decides **where** a move goes.
- **The pack's claim is partly corrected.** Inertia is the common case: about half of both groups did none of these
  things, in every wave. But trust is not irrelevant to retention. On this record, trust in fair treatment is the
  difference between losing a household and re-tariffing it.

**Limits, stated beside the result.**
- The data is cross-sectional. The trust question asks about the *current* supplier, so a household that has just
  switched rates its new supplier. That biases the supplier-switch contrast toward zero, so the true effect is likely
  larger.
- Trust may follow from having been offered a good internal deal, not cause taking it. The direction is not
  established.
- The question is about **treatment**. CIM does not cross switching by trust to charge a fair price, the other half
  of row 3 in §0. Ofgem 2021 shows that half runs 7 points lower (45% against 38%).

## 3. The pack's synthesis and the steer's framing, tested

| # | Claim | Verdict | Why |
|---|---|---|---|
| 1 | Reputation acts as a durable stock: overcharging is penalised late | **Confirmed in shape, not in size** | Centrica 2017-18 shows losses persisting across two years of SVT rises, with brand NPS flat (P). No GB source gives a decay rate (pack E4 gap 2). The ScottishPower ten-year tail is confounded by continuing poor service, as the pack itself says. |
| 2 | Damage to a vulnerable minority need not reach whole-book satisfaction (British Gas, 2023 prepayment) | **Confirmed as stated (P)** | It is one case. It sets a direction for the model, not a size. |
| 3 | "Inertia, not trust, keeps overcharged customers" | **Corrected (D, §2)** | Inertia is the common case. Among those who move, trust decides whether the move is in-house or out. |
| 4 | Churn hazard h = h₀·exp(β·R)·S(t), rising in resentment R (pack E1 row 7) | **Corrected: the direction holds only if R is fed by engaged events** | The sentiment page §3.4 shows dissatisfied households switch *less* (CIM W6: 3.0% against 5.4%), while complainants whose complaint was handled badly leave at about 2.6× the rate of those handled well (23% against 9%). A hazard rising in a generic grievance stock reproduces the direction the record refutes. **R must be split.** Resentment from events the household acted on (a complaint, a contact, a dispute) raises departure. Silent dissatisfaction raises it little or not at all, and depresses engagement. |
| 5 | Salience triggers: resentment crystallises at events, not as smooth churn | **Confirmed in shape (P qualitative), and partly in the code already** | `simulation/churn_journey.py` already moves a household from IRRITATED to IN_MARKET only when a renewal window is open and the saving beats its activation energy. That is one salience trigger, the fix end. A price-rise letter and press coverage are not modelled. No GB source gives the multiplier: the pack's 2-5× is A. |
| 6 | NPS does not lead churn | **Confirmed (P, one case)** | British Gas, 2018: net losses of 742k with brand NPS flat. The [lit] support (Keiningham 2007) is not re-read. |
| 7 | Review negativity tracks the invitation policy | **Confirmed in direction; the size is an upper bound (§1, row 7)** | Both suppliers now invite, so the contrast is between policies inside "invites", which Trustpilot does not publish (pack E4 gap 4). |
| 8 | Two kinds of trust (treated fairly; charged a fair price) | **Confirmed (P, §1 row 4)** | 45% against 38% in 2021. CIM carries only the first, so the second has no post-2021 series. That is GAP-R3. |

## 4. The world's constants, graded

Every constant in the three modules the steer names, at HEAD `41812d65cc`. "Range" is what the evidence supports. Where
nothing supports a value, the cell says GAP.

### 4.1 `simulation/resentment_ledger.py`

| Constant | Value | Grade | Range or GAP | Evidence and note |
|---|---|---|---|---|
| `BILLING_ERROR` | +15 | A (unsourced) | Relative weight about 0.7 of an unresolved complaint | Pack E1 row 5, anchored on Citizens Advice's star-rating weights (P: complaints 35%, contact 30%, billing 25%). Those weights are the regulator's **scoring** weights, not a household's grievance. That makes this an A anchored on P, not a P. |
| `PAYMENT_FAILURE` | +8 | A (unsourced) | GAP | No source weights a failed direct debit as a grievance. The household often caused it. |
| `COMPLAINT_UNRESOLVED` | +20 | A (unsourced) | The reference event (1.0) | Its departure effect is the one dose in the record: 23% against 9% (sentiment page §3.4b, P, 2014, self-attributed). |
| `PRICE_INCREASE` | +12 | A (unsourced) | About 0.8 relative | Price is 46% of reasons for dissatisfaction (pack B1; not re-read). **Declared, never emitted** (sentiment page §6.1). |
| `OUTAGE` | +10 | A (unsourced) | GAP | Outages are mostly a network-operator matter. No share of supplier complaints is published (sentiment page §7 row 9). Never emitted. |
| `CALL_WAIT_LONG` | +6 | A (unsourced) | About 0.5 relative | Citizens Advice weights ease of contact at 30%. Never emitted, because no contact queue exists. |
| `BILL_SHOCK` | +18 | A (unsourced) | GAP on the weight. **Defined wrongly upstream** | Emitted when the unit rate rises more than 20% (`run_phase2b.py`), which is a price rise. The sentiment page §6.1 shows the operational shocks (a DD reset, a catch-up bill) are what make up the Ombudsman's 56% billing share. |
| `COMPLAINT_RESOLVED_WELL` | −5, **never decays** | A (unsourced) | Should remove 60-80% of **its own** triggering event's resentment and create no surplus (pack E1 row 9, de Matos et al. 2007 [lit], not re-read) | **Defect, D1 below.** |
| `SWITCHING_BARRIER` | +4 | A (unsourced) | GAP | Never emitted. |
| `_MONTHLY_DECAY_RATE` | 1 point a month, linear | A (unsourced) | An event of weight w lasts w months: 6 to 20 months, half gone at 3 to 10 months | This happens to sit inside the pack's A range for ordinary friction (half-life 3-9 months, E1 row 4). It has no slower class for "betrayal" events (≥24 months, A). **Linear decay is a shape choice.** Larger events last longer, which is defensible. No source chooses between linear and exponential. |
| `_DEFAULT_CHURN_THRESHOLD` | 50, the same for everyone | A (unsourced) | GAP on the level. **Heterogeneity is P in kind** | Deller et al. (2021, pack C3): about half do not switch even at savings above £300 a year. A single threshold cannot produce that spread. With weights of 6-20 it takes three or more events inside a year to cross it. |

### 4.2 `simulation/reputation_index.py`

| Constant | Value | Grade | Range or GAP | Evidence and note |
|---|---|---|---|---|
| `_GRI_IMPACT` (9 event weights, −12 to +4) | e.g. Ofgem enforcement −12, price-gouging allegation −8 | A (unsourced) | GAP | No GB event study gives a reputation response per event (pack E4 gap 2). |
| Decay | **None.** Every event is permanent | — | Half-life 12-24 months, negative slower than positive (pack E1 row 2, A) | **Defect, D2 below.** The bounds: sector satisfaction recovered from its 2023 trough in about 18 months (P/S); British Gas showed no whole-book tail after 2023 (P). Both point to a finite half-life. |
| `_GRI_BASELINE` 50, bands at 30 / 50 / 70 | — | A (unsourced) | GAP | — |
| `_ACTIVATION_ENERGY_MULTIPLIER` | 1.3 / 1.0 / 0.7 / 0.5 by band | A (unsourced) | GAP | The only effect reputation has, and it acts on churn alone. Reputation's effect on acquisition is competitive (§6). |

### 4.3 `simulation/feedback_survey.py`

| Constant | Value | Grade | Range or GAP | Evidence and note |
|---|---|---|---|---|
| `BASE_RESPONSE_RATE` | 0.08 | A | 0.05-0.15 by email; 0.20-0.40 in-channel, straight after the contact | Practitioner ranges, [unverified] (pack D4). **No GB supplier publishes a response rate** (GAP-R1). |
| `EXTREME_RESPONSE_BONUS` | +0.12, so 0.20 at the extremes, 2.5× the middle | A | 1.5-2× at the extremes against the midpoint (pack E1 row 17, A) | The U-shape is P in kind: Hu, Pavlou and Zhang (2009) show the J-shape comes from self-selection, and a random-assignment control gave a unimodal distribution. **The code's 2.5× sits above the pack's range.** No energy-specific figure exists. |
| `HIGH_` / `LOW_SATISFACTION_THRESHOLD` | 0.80 / 0.35 | A | GAP | A step function. The evidence is a smooth U, and its curvature is unpublished. |
| `RESPONSE_NOISE_STD` | 0.08 | A | GAP | — |
| Income-stress response multiplier | 1.0 / 0.8 / 0.55 | A | GAP. **Direction P in kind** | "Scarcity depletes bandwidth" (the needs packs) supports the direction, not the size. |
| `COMPLAINT_BASE_PROBABILITY` | 0.03 a term | A | Compare: about 1% of accounts a quarter (sentiment page §3.3, P) | A term is usually 12 months, so 3% a term is below the 1%-a-quarter market level unless bill shocks make up the difference. **Not graded here against a run.** |
| `BILL_SHOCK_COMPLAINT_PENALTY` | +0.35 | A | GAP | Keyed to the price-rise definition of shock (see `BILL_SHOCK` above). |
| `OMBUDSMAN_ESCALATION_PROBABILITY` | 0.08 | A | Signposting 25-68% (mean 48%) × uptake, with the uptake A (pack D7, Energy Ombudsman 2025, P) | The sentiment page §3.3 says the per-complaint escalation rate cannot be formed on one definition. |
| `OMBUDSMAN_UPHELD_PROBABILITY` | 0.5 | A | About 57% upheld in 2019 (sentiment page §6.1, P) | The nearest of the set to a source. Still not cited in code. |
| `OCCUPANCY_COMPLAINT_MULTIPLIER` | 0.85-1.30 | A (stated in code as a choice) | GAP | The code says so honestly. |

**Not in any module:** an organic or invited public-review channel, a regulator panel, invitation policy as a
supplier decision, a reply loop, sector trust and advertising goodwill. These are the steer's Asks 2, 4 and 5, which
are build work.

## 5. Two places the code runs the wrong way

Both are world-side and **log-only today**. Nothing reaches `customer_events.roll_lifecycle_event`: the journey state
is read only for a home-mover's log row (`run_phase2b.py` ~3429; this matches the sentiment page §6.1 at its HEAD).
So neither changes a published figure now. Each would, as soon as the stock is wired to departure. **They are recorded
here so the wiring does not inherit them.**

- **D1. A repair outlives the grievance it repaired.** `current_score` decays positive events and adds negative ones
  undecayed. A −5 from one well-resolved complaint keeps reducing every later grievance for the rest of the
  household's tenure. That is surplus loyalty, the one effect the service-recovery evidence says does not occur:
  recovery raises satisfaction, not repurchase (de Matos et al. 2007 [lit], pack E1 row 9). The evidence also runs
  the other way on asymmetry. Losses weigh more than gains and persist longer (Mittal et al. 1998 [lit]; Bolton 1998
  [lit]). The code makes the gain the permanent one.
- **D2. Reputation never forgets.** `GlobalReputationIndex.score` sums every event since the start, clamped to
  0-100. One Ofgem enforcement action (−12) is carried at full weight ten years later, and a supplier that does well
  for long enough saturates at 100. Every GB bound in the pack points to a finite half-life (§4.2).

Fixing either is a world change for a fidelity reason, so it is lawful under R13.

- **D1 is fixed (2026-11-02).** A repair now fades on the grievance clock, 1 point a month, so a −5 is gone in five
  months. It needed no new number. The same rate, not a faster one, because no source sets a repair's own decay.
  Log-only, so no published figure moves. *(Correction beside the earlier sentence here, which said both fixes wait
  for the correctness exit test: a log-only defect fix that needs no new constant is correctness work, not a feature.)*
- **D2 is not fixed, on purpose.** "No decay" asserts an infinite half-life, which K2 says is a value we know is
  wrong. But a decay rate would have to be picked from the pack's A range (12-24 months), and §8 shows the GB record
  cannot narrow it. The GRI is log-only today, so it waits for the improvement loop's stage 1 for reputation, where
  the world reacts at its range rather than at one value. §8 adds a second reason it needs rebuilding, not a decay
  term alone: the record says a supplier's standing is mostly a persistent level, which the GRI has no term for.

## 6. Filed under the competition topic, not built

Per the 17:20 addendum, these six asks are named as held items in `docs/design/COMPETITOR_FIELD_FRAME.md` §10, with
the pack and this page as their knowledge base:
1. reputation moving prospects' choice *between* suppliers;
2. cost of acquisition relative to rivals;
3. referrals as a share-gaining channel;
4. price tolerance relative to the market;
5. sector trust shocks across suppliers;
6. the overcharge-against-fair-pricing test of the director's hypothesis.

## 7. Gaps (each one is a finding, not a placeholder)

- **GAP-R1.** A response rate for any GB supplier's tNPS, CSAT or CES survey, and the response rate by satisfaction
  level. Unpublished.
- **GAP-R2.** A half-life for reputational damage in GB energy. **Still open; the cheap route is shut (§8).** The
  event study this row proposed cannot be run on Ofgem's waves: they are per supplier only from Aug-Sep 2023, after
  every named event. Routes left: wave microdata (not published), Which?'s annual per-supplier surveys (S,
  paywalled), commercial brand trackers (G5 to buy). The Citizens Advice star rating is per supplier from Q4 2017
  but measures operations (complaints, contact), not reputation.
- **GAP-R3.** Trust to charge a fair price after 2021. CIM asks only about fair treatment.
- **GAP-R4.** The UK Home account base for 2017-18, needed to turn Centrica's net losses into a rate. Even then, the
  rate would be net, not gross.
- **GAP-R5.** The invited and organic shares of energy suppliers' Trustpilot reviews. Labels exist per review, but
  no aggregate is published.
- **GAP-R6.** Any GB link from supplier reputation to uptake of advice or products (pack E4 gap 8). Ofgem's 2021
  observation that trust may *increase* inertia among the disengaged is the only P statement, and it is qualitative.
- **GAP-R7.** What holds a supplier's persistent satisfaction level (§8.3). Not its service as Citizens Advice
  measures it: r = −0.04 across the seven groups (§9). Until something establishes a cause, the level is a stated
  per-supplier assumption.

Licensed microdata that would close R2 and R6 (Understanding Society, the Ofgem CIM microdata if deposited) is G5 to
register for. It belongs on the corpus steer's single `for_the_director` microdata row, not here.

## 8. GAP-R2: what the supplier-level satisfaction waves can and cannot say about a half-life (D, 2026-11-02)

### 8.1 Pre-registration (written 2026-11-02 20:47 UTC, before any supplier-level wave figure was read)

What was known when this was written: the 2019 Ofgem archive holds one per-supplier snapshot (Feb 2018, GfK) and a
GB-only quarterly series (2010-2017); Ofgem's own customer-service page says supplier-level findings are published
only from the Jan-Feb 2024 wave. No per-supplier figure from any wave after Feb 2018 had been opened.

1. **Feasibility, predicted:** the event study GAP-R2 names (npower, ScottishPower, British Gas enforcement dates
   inside 2018-2025) cannot be run on Ofgem's waves, because no supplier-level wave brackets any of those dates.
2. **Persistence, predicted:** across the supplier-level waves, a supplier's gap from the wave's mean on overall
   satisfaction carries over half a year with a coefficient rho between 0.5 and 0.9. That is an implied half-life of
   6 to 39 months.
3. **British Gas, predicted:** its overall-satisfaction gap is negative in the first supplier-level wave (about a year
   after the Feb 2023 prepayment reports) and smaller in magnitude by the last wave.
Any of these can be refuted by the figures; the result section states which were.

### 8.2 What the data is

Ofgem's Energy Consumer Satisfaction Survey (BMG, for Ofgem and Citizens Advice), question A5, overall satisfaction
with one's own supplier, % satisfied or very satisfied. Six half-yearly waves, Aug-Sep 2023 to Jan 2026, seven
supplier groups in every wave, bases 105-1,170 per group per wave
(`data/lake/ofgem_energy_consumer_satisfaction_supplier_level_2023_2026/`). **This is quantity 2 of §0, aggregated
over a supplier's own customers. It is not quantity 4,** the world's view of that supplier. It is the nearest
published per-supplier series, and a reputation stock that never showed here among the supplier's own customers would
be hard to tell from one that does not exist.

Gap from the GB average, in points:

| Group | Aug-Sep 23 | Jan-Feb 24 | Jul 24 | Jan 25 | Jul-Aug 25 | Jan 26 | Sampling SE of one gap |
|---|---|---|---|---|---|---|---|
| British Gas | −2 | −2 | −2 | −1 | −1 | −1 | 1.6-2.0 |
| EDF | −8 | −6 | −8 | −7 | −3 | −6 | 2.9-3.3 |
| E.ON | 0 | +1 | −2 | −5 | −2 | 0 | 2.3-2.6 |
| Octopus | +15 | +14 | +9 | +8 | +8 | +9 | 1.5-2.1 |
| OVO (incl. SSE) | −8 | −10 | −6 | −6 | −9 | −11 | 2.9-3.2 |
| ScottishPower | −7 | −8 | −7 | −9 | −8 | −5 | 3.3-3.8 |
| Utilita | +6 | −5 | +7 | +3 | −6 | −4 | 3.9-5.6 |
| *GB average, %* | *69* | *73* | *78* | *81* | *82* | *81* | |

SE assumes a design effect of 1.5 for quota sampling and weighting (A; Ofgem does not print one) and ignores the
covariance of a group with the average it is part of, which overstates the SE slightly.

### 8.3 What it shows

- **The supplier gaps are a fixed ranking, not a decaying stock.** Of the variance of the 42 gaps (43.6 points²),
  41.5 is between the seven groups' own six-wave means. Sampling noise in a single gap is about 9 points², and the
  within-group deviations carry nothing from one wave to the next: their lag-one coefficient is −0.03, against the
  short-panel (Nickell) bias of about −0.2 that six waves give when the true value is zero. Nothing transient moved that could be timed.
- **The pooled persistence of a gap is near one.** Gap on last wave's gap: raw 0.77 a half-year (n = 35), 0.66 at
  a year, 0.62 at two years. Corrected for sampling noise in the regressor: 0.89-1.06 a half-year as the design effect
  runs 1.0-2.0, a "half-life" of 30-68 months at the one- and two-year lags. That is the persistence of whatever keeps
  a supplier above or below the market, mostly service, not the memory of an event. **It is not a half-life for
  reputational damage and must not be used as one.**
- **One move clears the noise, and it is composition, not reputation.** Octopus fell from +14 to +9 between Feb and
  Jul 2024, the wave in which the Shell Energy Retail book it took over on 1 Dec 2023 (Shell itself sat at −8 and −4 in
  the two earlier waves) is counted inside it.
- **British Gas carries no visible whole-book tail.** Its gap is −2 seven months after the Feb 2023 forced-prepayment
  reports and −1 by 2025-26, inside one SE throughout. This adds five waves to §3 row 2 (damage to a minority need not
  reach whole-book satisfaction). It cannot say whether a tail existed in the first seven months.
- **The sector series moves with bills, not like a memory.** The GB average's shortfall from its April 2020 peak
  (78%, Ofgem's own reference in the Jan-Feb 2024 and Jul 2024 reports) was 11 points in Nov-Dec 2022 (67%), 9 in
  Aug-Sep 2023, 5 in Jan-Feb 2024 and 0 in Jul 2024, then above it. It barely closed through 2023 and closed fast once
  the cap fell. A half-life fitted to the second leg (about 6 months) would be the speed of relief, not of forgetting.

### 8.4 The pre-registration, scored

1. **Feasibility: confirmed.** No supplier-level wave brackets any named event; the first is seven months after the
   British Gas reports.
2. **Persistence: inside the range in the raw number, refuted in what it means.** Raw 0.77 sits inside 0.5-0.9;
   noise-corrected, it sits at or above the top. The prediction assumed a decaying gap to time. There was none: the
   gaps are a near-fixed ranking and the movement within it is noise.
3. **British Gas: right in sign, unscoreable in size.** Negative in the first wave and smaller by the last, but the
   one-point change is inside one SE. It is not evidence of recovery.

### 8.5 What this changes

- **The GRI is wrong in two ways, not one.** It has no decay (D2), and it has no persistent level. The GB record
  says the larger part of a supplier's standing is a level fed every month by how it serves (Octopus +8 to +15,
  OVO −6 to −11, all six waves), which an event sum cannot hold. A rebuilt index needs both: a level that tracks the
  supplier's ongoing service, and an event term whose decay stays A at 12-24 months until a GAP-R2 route opens.
  *(Corrected the same day, §9: "fed by how it serves" was inferred, not tested, and the test refutes it. The
  persistent level stands; its cause is GAP-R7. The level does not track the supplier's measured service.)*
- **The roadmap's "cheapest move" did not change the order.** Reputation stays sixth: its event decay is still
  unsourced. The persistent-level finding is D and usable, so stage 0 knowledge for that half now exists.

## 9. Is the persistent level fed by service? The §8.5 inference tested against Citizens Advice's star rating (D, 2026-11-02)

§8.5 says a supplier's standing is "a level fed every month by how it serves". §8 measured the level and did not
test the cause. Citizens Advice publishes a quarterly star rating per supplier from Q4 2017, built from what the
supplier did (complaints, contact, billing, switching), not from what its customers said. If the level is service,
the two should rank the seven groups alike.

### 9.1 Pre-registration (written 2026-11-02 22:07 UTC, before any Citizens Advice figure was opened)

What was known when this was written: the six Ofgem waves of §8.2, and that the Citizens Advice rating exists, is
quarterly, and scores suppliers out of five on several service measures. Which measures, which quarters are
published and which of the seven groups are rated in them were not known.

1. **Between groups, sign and size.** Over the quarters that overlap the Ofgem waves, a group's mean Citizens Advice
   overall rating and its six-wave mean Ofgem gap correlate positively, Pearson r between 0.5 and 0.95 across the
   seven groups. The slope is 3 to 12 Ofgem points per star. r at or below 0.3, or negative, refutes "fed by service"
   and §8.5 must call the level untested.
2. **The ends.** Octopus is the top-rated of the seven on Citizens Advice. OVO and ScottishPower are both in its
   bottom three.
3. **The mechanism is failure, not contact.** The complaints measure correlates with the Ofgem gap more strongly
   (negatively) than the customer-contact measure (call waits, email response) does, in absolute r.
4. **Within groups, nothing.** Wave-on-wave changes in a group's Ofgem gap do not track changes in its Citizens
   Advice rating over the matching quarters: |r| below 0.3. §8.3 found the within-group movement is sampling noise,
   so a real within-group signal here would contradict §8, not confirm it.

Rules fixed before reading: a measure that is itself a survey of customer satisfaction is left out of the test,
because it would be the Ofgem quantity again. A group the rating does not cover in a quarter is left out of that
quarter, not filled. Groups are mapped to Ofgem's definitions (OVO with SSE, Octopus with Co-op, London Power and,
from Jul 2024, Shell); where the rating scores the brands separately, the brand with the larger book stands for the
group and the choice is printed.

### 9.2 What the data is

Citizens Advice's historic star-rating CSVs, fetched 2026-11-02 22:08 UTC
(`data/lake/citizens_advice_star_rating_2023_2026/`, sheet ids, SHA-256 and the derivation there). Four measures:
overall stars, contact ease stars (call wait and email response), average call wait in seconds, and weighted
complaints per 10,000 customers (Energy Ombudsman, Citizens Advice consumer service, Extra Help Unit). None is a
satisfaction survey, so none was excluded. Each Ofgem wave is joined to the quarter holding its fieldwork (Q3 2023,
Q1 2024, Q3 2024, Q1 2025, Q3 2025, Q1 2026). Brands: E.ON Next, Octopus Energy (Citizens Advice prints Co-op's
complaints identical to it), Ovo Energy. Shell has no column. **Not foreseen in §9.1:** the methodology changed
from Q4 2025, so the Q1 2026 overall and contact ratings are on the new basis. Every between-group figure is shown
on all six quarters and on the five old-method quarters. Neither changes a verdict.

| Group (six-quarter means) | Ofgem gap, pts | Overall stars | Contact ease stars | Call wait, s | Complaints per 10k |
|---|---|---|---|---|---|
| Octopus | +10.5 | 3.18 | 3.13 | 155 | 27 |
| Utilita | +0.2 | 2.22 | 3.17 | 207 | 117 |
| E.ON | −1.3 | 3.06 | 3.33 | 131 | 41 |
| British Gas | −1.5 | 2.67 | 3.47 | 161 | 84 |
| EDF | −6.3 | 2.60 | 2.77 | 260 | 49 |
| ScottishPower | −7.3 | 3.28 | 4.13 | 92 | 68 |
| OVO | −8.3 | 3.21 | 3.77 | 109 | 71 |

### 9.3 What it shows

- **Citizens Advice's view of a supplier's service does not rank the groups the way their own customers do.**
  Across the seven groups, the six-wave mean Ofgem gap against the overall star rating: r = −0.04 (Spearman −0.46;
  five old-method quarters, r = −0.16). ScottishPower and OVO have the best overall stars of the seven and the two
  lowest satisfaction gaps. Utilita has the worst stars and the highest complaint rate, and sits at the GB average.
- **Contact runs the wrong way.** Contact ease stars against the gap: r = −0.42 (five quarters −0.49). Call wait:
  r = +0.12, again the wrong sign (longer waits, higher satisfaction). Both carry no weight at n = 7 (permutation
  p 0.35 and 0.78), but neither is the positive link the inference needs.
- **Complaints is the only measure with the expected sign, and it is weak and leans on one group.** r = −0.30
  (permutation p 0.51; five quarters −0.34). Without Octopus it is +0.41. Without Utilita it is −0.66, but that cut
  was chosen after seeing the table and is a hypothesis, not a result: Utilita's book is mostly prepayment, and its
  customers may judge it against different expectations.
- **Within groups, nothing moves together.** Wave-on-wave change in the gap against change in the measure:
  overall −0.09, contact 0.00, call wait −0.05, complaints −0.24 (n = 35 each). This is what §8.3's finding that the
  within-group movement is noise predicts. The sector-wide fall in complaints (Citizens Advice's average went from
  80 to 45 per 10k across these quarters) and the rise in GB satisfaction (69% to 81%) move together, but that is
  one series against another over the fall in bills (§8.3, last bullet), and cannot be attributed.
- **What n = 7 can say.** An r near zero on seven groups cannot rule out a modest link, but the pre-registered rule
  was a refutation at or below 0.3, and the point estimate is not close: the measured service ranking and the
  satisfaction ranking disagree at both ends.

### 9.4 The pre-registration, scored

1. **Between groups: refuted.** r = −0.04 against a predicted 0.5 to 0.95, and the slope is −0.7 points per star,
   not 3 to 12.
2. **The ends: refuted.** Octopus is third of seven on overall stars (3.18, behind ScottishPower 3.28 and OVO
   3.21). OVO and ScottishPower are the top two, not in the bottom three.
3. **Failure over contact: refuted as written.** |r| for complaints (0.30) is below contact's (0.42). Complaints
   has the predicted sign; contact has the opposite one.
4. **Within groups, nothing: confirmed.** Every |r| is below 0.3.

### 9.5 What this changes

- **§8.5's "a level fed every month by how it serves" is withdrawn.** The persistent level is D (§8.3). That it is
  service, as service is measured from outside, is refuted on this test. What holds a group's level is now **GAP-R7**
  (§7). Candidates the evidence allows, none tested: brand and what the supplier stands for; who its customers are
  (Utilita's prepayment book, ScottishPower's Scottish one); what Citizens Advice does not count, such as tariff
  design, app experience and how problems are resolved rather than whether they reach a third party; and
  satisfaction as a slow habit of the book itself.
- **For the reputation rebuild:** the level is a per-supplier constant the world states as an assumption (A, with
  the §8.2 range, about −11 to +15 points), not a function of the world's complaint or contact rates. Tying it to
  service would assert a link that the GB record, at this resolution, does not show.
- **No world or company value changes here.** The reputation index is not built from this page yet (§0, §5).

## Sources

- Centrica plc, *Annual Report and Accounts 2018*, pp.19-20. https://www.centrica.com/media/1112/annual_report_2018.pdf (P; extracts in `data/lake/centrica_annual_report_2018/`)
- Ofgem/Ipsos, *Consumer Survey 2021: Engagement report*, slides 44-45 and p.3. https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf (P; `data/lake/ofgem_consumer_survey_2021/`)
- Ofgem, *Consumer Impacts of Market Conditions* survey, Waves 3-6, C4 by trust to treat fairly (P, derived D; `data/lake/ofgem_cim_wave3_2022/`, `data/lake/ofgem_cim_waves4_6_2023_2025/`)
- Ofgem, *Customers' satisfaction with their supplier: supplier level findings*, six waves Aug-Sep 2023 to Jan 2026, Table 1 (P, derived D; `data/lake/ofgem_energy_consumer_satisfaction_supplier_level_2023_2026/`, URLs and SHA-256 there)
- Citizens Advice, *Historic star rating data* (24 Mar 2026), charts 2, 4, 5 and 12 as CSV. https://www.citizensadvice.org.uk/policy/publications/historic-star-rating-data/ (P, derived D; `data/lake/citizens_advice_star_rating_2023_2026/`, sheet ids and SHA-256 there)
- Ofgem, *Customer satisfaction indicators: previous updates* (GfK: a Feb 2018 per-supplier snapshot and a GB series 2010-2017). https://www.ofgem.gov.uk/publications/customer-satisfaction-indicators-previous-updates (P)
- Trustpilot profile pages, read 2026-11-02: https://uk.trustpilot.com/review/octopus.energy, https://uk.trustpilot.com/review/www.britishgas.co.uk (P for the platform's own figures)
- The advisor's pack and the sentiment page, as cited inline. Their [lit] and [unverified] items keep those grades.
