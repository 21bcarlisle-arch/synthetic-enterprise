# Does a disengaged household leave the default tariff less than an engaged one at the same tenure?

**Knowledge:** how-households-choose

**Read 2026-10-07.** Claim `pb4-svt-drift-engagement-gradient-knowledge-pass`.
**Subject:** `simulation/departure_risks.svt_inertia_hazard`. It takes years on the default, the
market year and nothing else. So in PB4's capture every archetype drifts off the default at the same
world probability, 0.023–0.027 per cap period. Expected departures per household come out flat:
active 0.61, passive 0.48, disengaged 0.60. That capture is `docs/reports/pb4_departure_factors.json`
at `bebf42253`, and the PB4 D4 finding of 2026-10-07 reads it.

**The question.** Hold time on the default fixed. Does a less engaged household leave it more
slowly? If so, by how much? The world already carries a tenure gradient: 0.20 a year under 3 years
on the default, 0.10 a year from 3 years. Both are structural inferences, confidence M,
`svt_rates_active_passive_2016_2025.md` §4.

## 1. The source: Ofgem's Cheaper Market Offers Letter trial, no-letter control arm

Ofgem, *Cheaper Market Offers Letter trial: research report*, November 2017. Fetched from
`ofgem.gov.uk/system/files/docs/2017/11/cmol_report_0.pdf` and text-extracted 2026-10-07. Figures 11
and 12 were rendered from p.27–28 and read off the bars.

The trial was a three-arm RCT run June–August 2017 with two suppliers, N=137,876. The sample was
every customer on an SVT for **at least one year**, stratified by SVT tenure: 1–3 years and 3+
years (§2.4). Excluded were section 11 marketing opt-outs, customers in debt and non-standard
meters (§2.5). The outcome was switching within a **30-day** window after the letter.

The control arm switched at **1%** in 30 days. External switching ran 0.4 points above internal,
so about **0.7% external and 0.3% internal**. Medians were 2 years 3 months and 6 years 3 months
on SVT; 37.5% and 23.6% had ever held a fix with the supplier (Table 1).

| Control arm, 30-day switching | Lower-engagement group | Higher-engagement group | Ratio |
|---|---|---|---|
| **By SVT tenure** (Fig. 11) | 3+ years: **0.7%** | 1–3 years: **1.3%** | **0.54** |
| **By meter reading submitted in the previous year** (Fig. 12) | none (36%): **0.3%** | at least one (64%): **1.3%** | **0.23** |

Ofgem itself reads both as "proxy variables for engagement in the energy market" (§3.46). It also
says "further research is required to understand how these different customer attributes
coincide" (§3.47). The joint split is not published.

## 2. What it establishes

1. **The tenure gradient the world already carries is corroborated.** The control arm gives 0.54
   between the 3+ and 1–3 year bands. The world gives 0.10 / 0.20 = 0.50. It is the first
   published, randomised-control reading of that ratio on file. It is one supplier pair, one
   summer month of 2017, and the bands were cut at the same 3 years.
2. **An engagement gradient exists at fixed tenure. This is a bound, not a guess.** Suppose the
   meter-reading marker carried no information within a tenure band. Every marker group's rate
   would then be a weighted average of the two band rates, 0.7% and 1.3%, and so would lie
   between them. The no-reading group's **0.3% lies outside that range.** So in at least one
   tenure band:
   - the non-readers switch at 0.3% or less;
   - that band's own average is at least 0.7%.

   The non-readers there therefore switch at **no more than 0.43 times** the readers' rate. Taking
   the bars' rounding to its least favourable ends (0.35 and 0.65) relaxes this to **no more than
   0.54 times**.
3. **The level is roughly consistent, and the external-only reading is not.** Annualising the
   30-day control rates at a constant hazard gives these figures:
   - all switching: 1–3 years **0.147**, 3+ years **0.082**;
   - external switching only, at about 0.7 of the total: **0.105** and **0.058**.

   The world in 2017 gives **0.177** and **0.089**: the 0.20 / 0.10 anchors times the 2017 market
   factor re-referenced to 2019–20, which is 0.887. If the world's drift counts supplier-to-supplier
   losses only, it sits about 1.7× above this control arm. The knowledge map already names that
   question as unsettled, and this note does not settle it. A 30-day summer window does not
   annualise reliably.

## 3. What it does not establish

- **The mapping from the marker to the world's archetypes.** "No meter reading in the last year"
  takes 36% of an SVT-for-a-year population. The world's DISENGAGED archetype is 20% of all
  households, a stricter tail. A stricter tail would show at least as steep a gradient, so the
  bound still applies in direction. Its size is not identified.
- **Passive against active.** The source has two groups, not three. Nothing here separates PASSIVE
  from ACTIVE on the drift.
- **Whether the gradient holds in both tenure bands.** The bound says "in at least one".
- **Ofgem's *Sustained Engagement* control arm (2020) does not contradict it.** Its within-tail
  marker was a switch made in the trial window, and that switch led to a 12-month fix. Its 31% vs
  33% therefore compares households a year apart in their product cycles. It is not a drift rate
  at fixed tenure. See `does_a_households_renewal_engagement_persist.md` §1.

## 4. Verdict, and the world change it licenses

**Sourced: the default-tariff drift has an engagement gradient beyond tenure.** The least engaged
leave at no more than about 0.54 of the engaged rate at the same tenure, and very probably at 0.43
or less. The world does not carry this. The world's current setting, a ratio of 1.0, is outside
the published bound.

**The one-variable change** spreads the 0.20 / 0.10 anchors by archetype:
- DISENGAGED gets **0.54** times the others' rate. That is the weakest gradient the bound allows,
  under the §7 tie-break: a stickier disengaged tail flatters retention, so the harder world takes
  the least sticky value the evidence permits.
- PASSIVE and ACTIVE stay equal, because the source does not separate them.
- The SVT-exposure-weighted mean is held, so the change moves who drifts and not how many.

The change needs the archetype at the call site. `svt_product.inertia_hazard_for_term` does not
have it today. It also re-levels the value arms (the world digest tracks the departure level), so
it is handed on as its own continuation rather than folded into this knowledge landing.

**Prediction, written 2026-10-07 before any world change.** This is the first-order effect on PB4's
own capture: scale each SVT decision's world probability and hold the summed SVT probability.

| Disengaged ratio | Scale on the others | Active | Passive | Disengaged | D/A |
|---|---|---|---|---|---|
| 1.00 (today, reproduces the capture) | 1.000 | 0.608 | 0.484 | 0.598 | 0.98 |
| **0.54 (the change)** | 1.155 | **0.651** | **0.543** | **0.404** | **0.62** |
| 0.43 (central bound) | 1.199 | 0.663 | 0.559 | 0.349 | 0.53 |

These are expected departures per household over the run. A re-capture after the change should read
disengaged/active expected departures in **0.55–0.70**. A reading outside that range means the
first-order estimate missed a second-order route; the likeliest is longer SVT stints for
disengaged households that leave more slowly. Name the route before trusting the figure.
