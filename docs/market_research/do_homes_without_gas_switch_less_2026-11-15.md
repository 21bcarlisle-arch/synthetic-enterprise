# Do homes without gas switch supplier less than homes with gas?

**Knowledge:** how-households-choose

**Researched 2026-11-15, autonomous worker.** This page answers the question left open by
`docs/staging/WORKER_FINDING_THE_CAMPAIGN_ROUTES_GAS_SHARE_SITS_ON_THE_BANDS_EDGE_AND_THE_CHECK_HAS_NO_SAMPLING_ALLOWANCE_2026-11-13.md`:
"is a savings-led campaign that over-wins off-gas homes faithful?" It is the K8 page for any change to
the campaign's win model. **This page changes no world value.**

Sources read this pass, from the documents' own text (pdftotext of each PDF, not a search summary):
- Ofgem, *Consumer engagement in the energy market 2017* (Ipsos MORI, n = 4,001 GB), PDF p.14:
  https://www.ofgem.gov.uk/system/files/docs/2017/10/consumer_engagement_survey_2017_report.pdf
- CMA Energy Market Investigation, final report, *Appendix 9.5: Restricted meters* (2016), para 62, PDF p.21:
  https://assets.publishing.service.gov.uk/media/577521a9e5274a0da3000123/fr-appendix-9-5-restricted-meters.pdf
- Also opened: the Ofgem Consumer Survey 2019 report and CMA Appendix 8.1 (customer survey). Neither
  has a switching breakdown by gas connection. Appendix 8.1 reports its gains analysis for dual-fuel
  customers only.

## 1. The answer: yes, at about half the rate

**Ofgem 2017, p.14:** "11% have electricity but no gas. Of these, 10% had switched in the past 12
months, almost half the proportion of households with both fuels who had switched (18% of households
with both fuels had switched at least one)."

- What each count is: a household's own report of a supplier switch in the 12 months before fieldwork
  (2017). The no-gas base is 11% of 4,001. That is about 440 respondents; the base is derived, not
  printed.
- One sampling SD on 10% at n ≈ 440 is about 1.4 points, so the 8-point gap is not noise.

**CMA 2016, Appendix 9.5 para 62:** "Across GB the incumbent share of supply in restricted meters is 79%
which is significantly higher than the equivalent figure for all electricity (33%) and gas (37%)
customers."

- What each count is: the share of meters still held by the former regional incumbent (September 2015,
  Six Large Energy Firms only for the restricted meters). Restricted meters are mostly Economy 7, and
  are concentrated in electrically heated, off-gas homes.
- It is a stock of past non-switching, not a rate. It points the same way as the Ofgem figure, more
  strongly.

The repo already held a third, qualitative pointer. Ofgem 2008 named "the relatively high number of
electricity only customers" as a reason for low switching
(`how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md` §5).

## 2. What it implies for a book built by switching

If the stock is p gas homes, and gas and no-gas homes switch at r_g and r_o, then the gas share among
switchers is p·r_g / (p·r_g + (1−p)·r_o).

| stock gas share p | r_g | r_o | gas share of switchers |
|---|---|---|---|
| 0.86 (EHS metered) | 0.18 | 0.10 | 0.917 |
| 0.84 (DESNZ) | 0.18 | 0.10 | 0.904 |
| 0.89 (Ofgem 2017's own both-fuel share) | 0.18 | 0.10 | 0.936 |

So on raw rates, a switching-built book should hold **more** gas homes than the stock, not fewer. The
campaign route reads 79.8% of 4,354 homes over 24 seeds, against the founders' 84.9%. That runs the
wrong way by about 10 points.

## 3. What argues the other way, and how strong it is

- **Octopus FY24/25: G/E 0.80** (`how_a_gb_domestic_book...` §4). This is one challenger at about 80%
  gas homes. It is weak evidence for this question. That book includes acquired books (Bulb, Shell
  Energy) that were not won by switching. It also includes EV and heat-pump tariffs, which recruit
  electric homes on purpose. It is a 2025 reading, not a 2016–2021 one.
- **Off-gas homes model larger savings.** A larger bill means a larger saving at the same percentage.
  That is the world's current mechanism. Nothing published says a larger saving overcomes the engagement
  gap. The Ofgem 10% already includes whatever pull the larger bills had in 2017.

## 4. What is established, what is not

- **Established (direction and raw size):** no-gas homes switched at about 0.56 times the rate of gas
  homes (Ofgem 2017), and their restricted meters stayed with the incumbent at more than twice the
  all-meter rate (CMA 2015).
- **GAP, the conditional ratio.** The world's entry weight is `active_renewal_probability_for_customer`
  (archetype × payment channel; `simulation/net_new_acquisition.engagement_weighted_entry_order`).
  Some of the raw gap is composition: off-gas homes skew older, rural and prepay. The weight already
  carries part of that. No published table gives the gap after controlling for age and payment method.
  So a gas-connection factor on the weight is a stated belief with a range: between 0.56 (none of the
  gap is composition) and 1.0 (all of it is). It is not one number.
- **GAP, why.** Ofgem 2008 says that a home without gas cannot take a dual-fuel deal, and that dynamic
  teleswitched meters make switching hard. Neither is quantified.

## 5. The design choice this supports (not built here)

The world's campaign selection should carry the engagement gap. One option is a gas-connection factor
in the entry weight, inside the [0.56, 1.0] belief range above, keyed to the home's meter (a world fact).
**The existing weight cannot carry any of the gap, and that is read from the code, not measured.**
`engagement_level_for_customer` seeds `random.Random(f"engagement_{customer_id}")`, and
`payment_channel_for_customer` is also a per-id draw. Neither reads the premise. So the world's entry
weight is independent of the gas meter by construction, and the world's no-gas to gas ratio is 1.0. The
published raw ratio is 0.56. Selecting on modelled saving then pushes the campaign toward off-gas homes,
which is the 79.8% the route reads.

The composition part of §4's range is therefore not in the world either: archetype and payment channel
do not vary with the home. So the honest range for a gas-connection factor stays [0.56, 1.0]. Its lower
end is the right reading while nothing else in the weight varies with the home. Erring against our own thesis (F11) points the same way. Off-gas
wins carry the largest modelled savings, so over-winning them flatters the value the campaign claims.
