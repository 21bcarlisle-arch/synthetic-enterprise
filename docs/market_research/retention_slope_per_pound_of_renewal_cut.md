# How much P(stay at renewal) moves per pound of renewal-price cut: the published record against the world's slope

**Knowledge:** how-households-behave-toward-a-supplier

**Read 2026-10-08** for atom `B8_discovered_price_sensitivity_holdout`, claim
`b8-source-the-real-retention-slope-per-pound-of-renewal-cut`. Opened by
`docs/staging/records/SEAT_FINDING_B8_NO_CUT_SIZE_PAYS_IN_THIS_WORLD_BECAUSE_THE_STAY_BOUGHT_PER_POUND_FALLS_AS_THE_CUT_GROWS_2026-10-08.md`,
which found that no uniform renewal cut pays. The world's slope is about 0.0015 of P(stay) per £/MWh.
For a cut to pay at a 14% margin the slope would need to be about 0.0062, and at a 1.9% margin about
25 times the world's.

## 0. The quantity, stated before any source

> At a renewal, how much does one household's probability of staying with its supplier rise for
> each £ per year by which that supplier's renewal price is cut relative to the best price the
> household could get elsewhere?

Three properties of this quantity separate it from the figures nearby:

- **It is a slope within one household, at one moment of choice.** A market-level curve of switching
  rate against "savings available" across years is a different quantity (quantity A in
  `household_switching_response_amplitude.md` §0), and dividing one by the other does not convert it.
- **It is measured at renewal, a moment of choice.** Every published gradient is measured on the leave
  side: P(switch) against a saving shown or available elsewhere. A cut of £X narrows the gap to the
  market by £X, so the two sides mirror each other *for a household that compares prices*. For one
  that does not compare, both are zero.
- **The horizon is the decision**, not 30 days.

### Units

The B8 decision set is electricity-only (`simulation/coin_drawn_decision_set.py`). Its drawn
households were measured this pass: `draw_households(101, 2016–2024, 1000/yr)` gives 6,634 households
with a mean EAC of **2,540 kWh** (median 2,476, p10 1,538, p90 3,831). The cut is ex VAT.

| | per £/MWh | per £/yr ex VAT (÷ 2.54) | per £100/yr |
|---|---|---|---|
| world, £2.5 cut (£6.35/yr) | 0.00166 | **0.00065** | 6.5 pp |
| world, £7.5 cut (£19/yr) | 0.00152 | **0.00060** | 6.0 pp |
| world, £30 cut (£76/yr) | 0.00123 | **0.00048** | 4.8 pp |
| break-even, 14% margin | 0.0062 | **0.0024** | 24 pp |
| break-even, 1.9% margin | ~0.045 | **~0.018** | ~180 pp (impossible) |

At the 1.9% floor the break-even slope is above 1 for any cut over about £60/yr, so it cannot be met
at all. **Only the 14% case is a live question.** In that case the real slope would need to be about
**0.0024 per £/yr, or 24 pp per £100**.

## 1. What the published record holds

| source | population and moment | what it measures | gradient | per £/yr |
|---|---|---|---|---|
| **Deller, Waddams Price, Giulietti, Loomes, Moniche & Jeon (2021)**, *Switching energy suppliers: it's not all about the money*, Energy Journal 42(3). Read from `ueaeprints.uea.ac.uk/80216/2/Published_Version.pdf` | Which? *Big Switch* 2012, collective auction. n = 86,904 decisions, 7,367 in the surveyed subsample. All had **opted in**; accepting needed one small step | P(accept the best offer) against the £ annual saving it showed. Probit, quadratic in saving. Average marginal effect, Table 3 | **1.6 pp per £10** (1.3–1.4 pp outside the filtered subsample) | **0.0013–0.0016** |
| same paper, Fig. 1, raw bins (§3) | same | switch rate by saving bin | £0–20 → £100–120: **+24 pp**; £100–120 → £300–320: +12 pp (survey subsample: +36, +10) | first £100: **~0.0024**; next £200: **~0.0006** |
| **Ofgem CMOL technical annex** (Nov 2017) §12, already read in `how_households_respond_to_supplier_contact.md` | SVT customers over 1 year, 2 suppliers, n = 137,876, contacted and control | 30-day switching against the saving shown on the letter. Pooled OLS. Saving not randomised | 0.52 pp per £100 | **0.000052** (30 days) |
| **Ofgem CMOC** (Sept 2019) §3.42, same file | default tariff, 5 suppliers, contacted arms only | 30-day switching against potential saving | 1.3 pp per £100 ("relatively modest") | **0.00013** (30 days) |
| **CMA Energy Market Investigation, final report** (June 2016), read in full text this pass | — | — | **No switching-on-saving gradient is published.** Its "elasticity" passages (§7.9, §8.8) are about the price elasticity of *consumption*, not of switching. | — |

Deller's exit-fee result is the same instrument read the other way. An exit fee of about £50 cuts
P(switch) by 17.3 pp, which equals about **£120 of saving**. Households in the act of choosing weigh
a penalty they can see at more than twice its face value.

## 2. Set beside the world

**The world's slope, about 0.0006 per £/yr, sits inside the published range and towards its
middle.** It is:

- about **4–12× steeper** than the two population gradients for default-tariff stock (CMOL, CMOC).
  Those are 30-day windows on mostly uncontacted households, and most of those households were not
  choosing at all;
- about **2.5× flatter** than Deller's marginal effect for households that had opted into a switch
  and were looking at an offer;
- about **4× flatter** than Deller's raw first-£100 bin. **That bin is the only published figure
  as steep as break-even at 14%.**

**The shape agrees.** Deller's curve is concave: most of the response comes in the first £100, which
is why they fitted a quadratic. The world's slope per £ also falls as the cut grows, from 0.00065 to
0.00048. Two records with independent provenance bend the same way.

## 3. What this establishes, and what it does not

1. **The published record does not show that the world's slope is too flat for a uniform renewal cut
   to pay.** The only figure at break-even is a raw cross-bin difference, and it comes from a
   population that had opted into switching and was looking at a concrete offer. In those bins the
   saving rises with consumption, and consumption is correlated with engagement. Deller's own
   regression, which controls for some of this, gives about 0.0016, which is two-thirds of
   break-even. A uniform renewal cut is offered to *every* renewer, most of whom are not at that
   moment of choice. The figures for that population are an order of magnitude flatter. **On the
   published evidence, the B8 finding that no uniform cut pays stands.**
2. **The population where the published slope is steepest is the one a save offer reaches.** It is
   made up of households that have started to act. Deller's 0.0016 is about 2.7× the world's. If
   renewal-time leavers resemble collective-switch opt-ins, a cut offered to them would be priced
   near break-even at the top of the margin bracket, before counting the low `p0` that makes a save
   offer cheaper anyway (curve finding, *What this does and does not say*). This supports the
   **save-offer shape** the curve finding sent to the director. It does not settle it: whether
   real retention desks make save offers, and to whom, is still a practitioner question.
3. **No published GB source gives the quantity in §0 causally.** No GB study has randomised a renewal
   price and measured staying. Every gradient above is observational in the saving (CMOL, CMOC,
   Deller), and every one is measured on the leave side. The world's slope therefore stays *ours*:
   it is consistent with the record, but the record does not establish it. Carry it that way.
4. **The world's slope has a lineage this exposes.** The renewal response is
   `churn_position_multiplier` (`simulation/market_switching_propensity.py`). It is built on the
   piecewise savings-to-switching curve in `churn_price_elasticity.md` §4, which is a **market-level
   curve across years** (quantity A) applied as a within-household response (quantity C). That the
   result lands inside the published within-moment range is a coincidence of calibration, not a
   derivation. If anyone rebuilds the curve, Deller's concave AME (0.0013–0.0016 per £ near £100,
   opted-in choosers) and CMOL/CMOC's 30-day population figures (0.00005–0.00013) are the two ends
   it should be graded against.

## 4. Sources tried and not used

- **Giulietti, Waddams Price & Waterson (2005)**, *Consumer choice and competition policy*, Economic
  Journal 115(506). This is stated *required* savings in the 1999-era gas market (~700 respondents).
  It measures a threshold, not a slope, and the paper was not read beyond its abstract this pass.
- **The CMA 2016 customer survey (Appendix 9.1)** asks about stated willingness, not a gradient.
  Not read for this question.
