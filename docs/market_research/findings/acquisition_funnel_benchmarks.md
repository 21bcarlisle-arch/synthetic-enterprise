# Acquisition Funnel Benchmarks -- UK Domestic/SME Energy Switching

**Session note on sourcing:** live internet fetch was not available to this agent in this
session (network calls required an approval step not present for a background agent). The
figures below are drawn from well-established, previously-published UK regulatory and market
sources (Ofgem, CMA, DESNZ/BEIS, Citizens Advice, industry press) recalled from training
knowledge, not a fresh live fetch. None are marked **H** (authoritative-fetched) as a result;
confidence is capped at **M** for well-known headline statistics I am confident are
substantially correct, and **L** for anything that is a cross-sector or industry-general
analogue rather than an energy-specific sourced number. Rich or a future session with live fetch
access should re-verify the M-rated figures against the primary documents named before they are
treated as load-bearing calibration.

---

## 1. What published funnel data exists

There is no single published document that reports the full six-stage
awareness-to-consideration-to-quote-to-application-to-credit_check-to-onboarding-to-cooling_off
funnel for UK energy switching. The real evidence base is fragmented across:

- Ofgem Retail Market Indicators / State of the Energy Market reports -- publish the
  bottom-line number only: annual domestic electricity/gas supplier-transfer (switching)
  rate as a percent of all domestic meter points. This is a population-level engagement metric,
  not a per-campaign conversion rate.
- CMA Energy Market Investigation (2016), Appendix 7 / consumer engagement chapters --
  documented that a substantial share of customers who actively compared tariffs (used a
  price comparison website) did not go on to switch -- real evidence of significant drop-off
  between consideration/quote and completed switch, the core justification for the Default
  Tariff Cap.
- Citizens Advice -- publishes consumer engagement/awareness surveys and switching
  experience/complaints research, but not a funnel-conversion breakdown.
- Ofgem Switching Programme / Retail Energy Code (REC), live from July 2022 -- moved
  domestic switching to next-working-day completion with a shortened objection window,
  replacing the previous roughly 15-17 working day process during which the losing supplier
  could contact the customer to win them back before the switch completed. Directly relevant
  to the cooling_off stage: loss rate materially higher pre-2022 than post-2022.
- PCW/broker industry commentary (uSwitch, MoneySuperMarket/Compare the Market parent BGL,
  trade press) -- has at various points cited quote-to-switch conversion generally in the
  low-to-mid tens of percent, but no single citable energy-specific dated figure was recalled
  precisely enough to use as a hard anchor; treat as L confidence industry colour only.

Bottom line: the per-stage split below is a reasoned decomposition anchored to the pieces of
real data that do exist (aggregate switching rate, CMA drop-off findings, REC reform), not a
direct read of a single published funnel. This is a genuine research gap, not papered over.

## 2. Defensible per-stage conversion rates

| Stage | Resi (domestic) | SME/I&C | Confidence | Basis |
|---|---|---|---|---|
| awareness to consideration | 25-35% | 15-25% | L | Analogue: general direct-marketing/lead-gen engagement rates; no energy-specific published figure found |
| consideration to quote | 35-50% | 25-40% | L | Analogue: PCW visit-to-quote conversion in financial-services verticals is typically higher once consideration is reached; SME lower due to procurement/broker involvement |
| quote to application | 15-30% | 20-35% | M/L | CMA (2016) documented material search-but-no-switch drop-off at this exact junction; SME often higher because brokers pre-qualify before quoting |
| application to credit_check pass | 90-97% | 80-92% | L | Resi: energy credit checks are largely soft-gate (deposit-setting, not accept/reject); SME: business credit scoring (Experian/Equifax) has a real rejection tail for newer/thinly-capitalised businesses -- analogue from B2B trade-credit acceptance norms |
| credit_check to onboarding completion | 92-98% | 90-97% | L | Operational-dropout analogue (data errors, MPAN/MPRN mismatches, customer non-response); not energy-specific sourced |
| onboarding to survives cooling_off (14-day) | pre-2022: 75-88% / post-2022 (REC): 88-96% | 85-95% (statutory 14-day right applies to off-premises SME contracts too, but win-back contact is commercially rarer) | M (regime fact) / L (rate) | Ofgem Switching Programme/REC (July 2022) shortened the objection/win-back window from about 15 working days to next-working-day -- a real, dated regulatory change that should make the loss rate at this stage time-varying, lower after mid-2022 |

## 3. Sanity check against the sim flat rates

Compounding the full six stages from awareness gives, at the midpoint of each resi range:
0.30 x 0.42 x 0.22 x 0.94 x 0.95 x 0.83 ~= 2.1 percent -- an order of magnitude below the sim flat
20% resi win rate.

This is the key finding to flag rather than force-fit: either (a) the sim ACQUISITION_WIN_RATE
attempt already denotes a mid-funnel event (most consistent with a quote already issued or an
application already in progress, given the GBP150 cost-per-attempt is far closer to the cost of
processing a quote/application than to the cost of a single marketing impression), or (b) if
attempt is meant to represent a top-of-funnel marketing contact, 20%/12% is too high by roughly
10x versus what the real, fragmented evidence implies.

Testing interpretation (a) -- compounding only the last four stages (quote to application to
credit_check to onboarding to cooling_off, i.e. treating attempt = quote issued):
0.22 x 0.94 x 0.95 x 0.83 ~= 16.2 percent (resi), which lands close to the sim 20% with the stage
rates at the upper end of their ranges (e.g. quote to application 28%, cooling_off survival 90%
post-2022). This interpretation is far more defensible than treating attempt as top-of-funnel
awareness, and is the recommended anchor if the funnel is decomposed.

For SME, compounding quote to onboard to cooling_off at range midpoints: 0.30 x 0.86 x 0.90 x 0.90
~= 20.9 percent, somewhat above the sim 12% -- plausible given SME acquisition genuinely has a
harder credit-check gate and more contract-review friction (procurement sign-off, notice periods
on existing supply contracts) that a resi funnel does not face. The sim 12% SME figure looks
reasonable to slightly conservative once mid-funnel is the anchor point, not a red flag.

Recommendation: do not force the decomposition to reproduce exactly 20%/12%. Use the
mid-funnel-anchored ranges above, let the compounded product land where it lands (roughly 15-20%
resi, 15-21% SME), and treat any material remaining gap as a genuine calibration finding to
record, not a target to hit.

## 4. Cost-per-stage split for CAC

No published UK energy-specific CAC stage-cost breakdown was found or could be verified this
session. As a general subscription-acquisition analogue (L confidence, not energy-sourced):

| Stage | Approx. share of total CAC | Basis |
|---|---|---|
| Awareness / marketing spend | 50-65% | General SaaS/subscription CAC literature -- marketing/media is consistently the largest single line |
| Quote / lead processing | 10-15% | Sales-ops staff time, PCW referral fees where applicable |
| Credit check / verification | 2-8% | Credit-bureau API calls are cheap per-check (order of GBP1-5); SME business credit checks cost more than resi soft checks but still a small percent of total CAC |
| Onboarding / welcome / meter registration | 15-25% | Ops handling, welcome pack, MPAN/MPRN registration, early-billing setup |

Given the absence of a sourced split, this table should be labelled clearly as an estimate
analogue if used for calibration, not treated as equivalent in confidence to the stage
conversion-rate ranges above.

## Structured findings

**domain**: churn
**assumption_tested**: ACQUISITION_WIN_RATE flat 20% (resi) / 12% (SME) per attempt approximates a realistic UK energy-switching acquisition funnel.
**benchmark_value**: Full top-of-funnel (awareness to won) compounding of realistic UK stage rates approx 2% (resi); mid-funnel (quote-issued to won) compounding approx 15-20% (resi), 15-21% (SME).
**confidence**: L (stage-rate ranges are cross-sector analogues; no single sourced UK energy-specific funnel document found this session; live fetch unavailable)
**source**: Ofgem Retail Market Indicators / State of the Energy Market (switching rate, population-level); CMA Energy Market Investigation 2016 Appendix 7 (search-but-no-switch drop-off); Ofgem Switching Programme / Retail Energy Code, July 2022 (cooling-off/objection window reform) -- all recalled from training knowledge, not live-fetched, retrieved 2026-07-05.
**date**: 2026-07-05
**finding**: The sim flat win rate is implausible as a true top-of-funnel (awareness) metric -- real UK evidence (CMA 2016, Ofgem switching-rate data) implies full-funnel conversion around 2%, roughly 10x lower. It is defensible if attempt is reinterpreted as a mid-funnel event (a quote already issued), which is also consistent with the GBP150 cost-per-attempt being much closer to quote/application processing cost than to a single marketing-impression cost. Recommend: if the funnel is decomposed into stages, anchor attempt at quote-issued, not awareness, and treat any residual gap from the approx 15-20%/15-21% compounded ranges as a genuine calibration finding rather than forcing an exact match to 20%/12%. No simulation code changed by this agent.

**domain**: churn
**assumption_tested**: The 14-day statutory cooling-off/cancellation stage has a materially different loss rate before vs after Ofgem July 2022 switching-speed reform.
**benchmark_value**: Estimated onboarding to survives-cooling-off rate: approx 75-88% pre-July-2022 (long approx 15-17 working day objection window, losing-supplier win-back contact permitted) vs approx 88-96% post-July-2022 (next-working-day switch, shortened objection window).
**confidence**: M (the regime-change fact and its direction) / L (the specific rate ranges, which are reasoned estimates, not directly sourced)
**source**: Ofgem Switching Programme / Retail Energy Code (REC) go-live July 2022 -- recalled from training knowledge, not live-fetched, retrieved 2026-07-05.
**date**: 2026-07-05
**finding**: If a cooling-off stage is added to the funnel and the sim spans 2016-2025, this stage parameter should be time-varying (pre/post July 2022), not a single flat rate, to reflect a real, dated regulatory change. This mirrors the pattern already used elsewhere in this sim for year-varying policy costs.

## ASSUMPTIONS.md update

See docs/market_research/ASSUMPTIONS.md -- added a note under Growth and Acquisition flagging the flat win-rate as a mid-funnel approximation with a recommended stage decomposition range, pending Tier-appropriate design review before any code change (this agent does not write simulation code).
