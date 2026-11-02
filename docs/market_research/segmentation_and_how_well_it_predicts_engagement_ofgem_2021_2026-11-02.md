**Knowledge:** the-customer-needs-framework

# Segmentation, and how well it predicts behaviour: Ofgem's six segments span 39% to 81% engaged, and one confidence question alone spans 44% to 74% (2026-11-02)

This is page 7 of the customer-needs domain as `docs/design/THE_KNOWLEDGE_BASE_STRUCTURE.md` §4 ranks it. It answers
the 30 Oct corpus steer (`docs/staging/advisor/DIRECTOR_STEER_BUILD_THE_CUSTOMER_KNOWLEDGE_CORPUS_AND_PROPOSE_THE_NEXT_SIM_ADDITIONS_2026-10-30.md`),
Ask 1 and Addendum 16:50 step 3 ("predictive validation of any segmentation").

Grades as on the sister pages: **D** derived by us from primary data, **P** reported in a primary publication by the
body holding the data, **S** a secondary summary, **A** an assumption with a range.

**Sides.** Mostly the supplier's (M4): a segment is worth inferring only if it predicts what a household will do
better than the observables the supplier already holds. For the world, a segment is not a drawn trait under the
parsimony ruling; the latent factors are.

No predictions were filed before the chart was read.

## 0. What is predicted, and from what

- **Predicted:** Ofgem's "engaged" — switched supplier, switched tariff or compared, in the past 12 months,
  self-reported in the same interview (page 6 §0).
- **Predictor:** Ofgem's six attitudinal segments (built in 2017 from attitude statements; the construction is in the
  2017 Consumer Engagement Survey report and is not re-read here), as assigned in the 2021 survey.
- **Comparator:** one question, CONF2, "confident choosing the best energy deal" (page 6).

Both are measured in the same interview as the behaviour, so neither is a forward prediction. This is the weakest
form of validation, and it flatters both. It is the only form the published record offers.

## 1. Engagement by segment (P shares, rates D)

Source: Ofgem/Ipsos Consumer Survey 2021, slide 20, read from the chart (`data/lake/ofgem_consumer_survey_2021/`).
Engaged is 63% of the weighted sample (slide 21: "74% vs 63% among total sample"). The rate in each segment is
derived by Bayes' rule from the shares: P(engaged | segment) = 0.63 × share among engaged / share of total, and
checked against the disengaged column, which gives the same figure to within a point.

| Segment | Share of total | Among engaged | Among disengaged | Engaged in the segment (D) |
|---|---|---|---|---|
| Happy Shoppers | 21% | 27% | 11% | 81% |
| Savvy Searchers | 20% | 25% | 12% | 79% |
| Hassle Haters | 17% | 16% | 19% | 59% |
| Market Sceptics | 22% | 20% | 26% | 57% |
| Anxious Avoiders | 12% | 8% | 19% | 42% |
| Contented Conformers | 8% | 5% | 13% | 39% |

The segments fall into three tiers: about 80% (two shopper segments, 41% of households), about 58% (Hassle Haters
and Sceptics, 39%) and about 40% (Avoiders and Conformers, 20%).

## 2. Against one question (D)

From page 6's figures by the same rule: 64% are confident choosing the best deal, 75% of the engaged and 44% of the
disengaged. Engaged among the confident: 0.63 × 0.75 / 0.64 = **74%**; among the not confident: 0.63 × 0.25 / 0.36 =
**44%**.

| Predictor | Engaged, lowest group | Engaged, highest group | Spread |
|---|---|---|---|
| Six segments | 39% | 81% | 42 points |
| One confidence question | 44% | 74% | 30 points |

**The six segments add about 12 points of spread over one yes/no question**, and they need a battery of attitude
statements to assign. Most of what they separate on engagement, confidence already separates.

## 3. Verdict on the advisor's synthesis

| Pack claim | Verdict |
|---|---|
| Ofgem's six segments separate engaged from disengaged | **Confirmed**: 39% to 81% (D, from P shares) |
| Segmentation predicts behaviour | **Extended, with a limit**: only contemporaneously, against a self-reported action; no published forward test of any GB energy segmentation was found in the packs or here |
| Trust and capability are the axes that separate the segments | **Partly**: the capability axis alone carries most of the engagement spread (page 6, and §2 here). Sceptics, the low-trust segment, sit mid-table at 57%, not at the bottom |

## 4. What this changes

**Supplier (M4).** A supplier should not infer Ofgem's six segments as a step in its method. A single observable
proxy for capability (the channel a household uses, whether it answers contact) recovers most of what they separate
on engagement, and the supplier can see it. Segments may still help *describe* a book; they are not shown to add
prediction.

**World.** Nothing drawn changes. Under the parsimony ruling the world draws latent factors, not segments; this page
says a capability trait (page 6) would carry most of the segments' engagement signal.

## 5. Gaps

- **GAP-SG1:** no forward validation of any GB energy segmentation: segment assigned at time t, behaviour recorded
  later from a supplier's book. Without it, §1 and §2 are both upper bounds on prediction.
- **GAP-SG2:** the segment-by-confidence joint is not published, so how much of §2's 12-point increment is
  independent of confidence is unknown.
- **GAP-SG3:** the 2017 segmentation's construction (which statements, which clustering) is not re-read here. If its
  inputs included engagement statements, §1 is partly circular.

## Sources

- Ofgem/Ipsos (2023), *Consumer Survey 2021: Engagement report*, slides 20-21, 38-39,
  https://www.ofgem.gov.uk/sites/default/files/2023-07/Consumer%20Survey%202021%20-%20Engagement%20report.pdf
  (lake copy SHA-256 `341a950b3dff6de3736a54fbe5e5f98afcb44f963532276f3a7760e6963e0c04`).
- Ofgem (2017), *Consumer Engagement Survey 2017*, for the segment definitions, as cited in the advisor's pack.
