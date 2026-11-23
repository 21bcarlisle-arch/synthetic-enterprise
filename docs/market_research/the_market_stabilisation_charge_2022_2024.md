# The Market Stabilisation Charge, 14 April 2022 to 31 March 2024: trigger, formula, share, scope, settlement and the weekly charge series

**Knowledge:** switching-mechanics

Written 2026-11-23 by the discovery agent for the question "did real acquirers pay a cost on first-term
fixed wins in 2022 Q4 to 2023 Q4 that the simulated world leaves out?". Every figure and quotation is
from an Ofgem publication read in full on 2026-11-23 unless marked. Markers: **GAP** = not found in a
primary source; **[unverified]** = from memory or a secondary source, not a claim; **[derived]** = this
page's own arithmetic on published numbers, with the inputs named. Ofgem's own pages for the MSC were
read from `ofgem.gov.uk` directly; no trade-press page could be fetched (Cornwall Insight and
MoneySavingExpert returned HTTP 403, and no web-search endpoint was reachable from this machine).

**Warning on sources.** The Ofgem URL `https://www.ofgem.gov.uk/guidance/calculation-market-stabilisation-charge`
now serves a 2026 guidance document for a *new* MSC (see section 9). It is not the 2022-2024 rule. The
2022-2024 guidance versions are the PDFs cited below.

## 1. Short answer

- The MSC was a licence condition (SLC 24A, electricity and gas) that made a **gaining** domestic
  supplier pay the **losing** supplier a volumetric charge, in pounds per MWh, whenever the wholesale
  cost of the supplier's notional hedge fell **10% or more below the wholesale element of the price cap**
  (30% in the first six weeks). Once triggered, the charge was **85% of the shortfall below the trigger
  point**, scaled by a seasonal consumption weight (75% share in the first six weeks).
- **It was zero for the first seven months.** Ofgem's published weekly series shows no charge at all from
  14 April to 15 November 2022. Gas first triggered for the week effective 16 November 2022 and
  electricity for the week effective 21 December 2022. **[derived]** On a typical dual-fuel household
  the charge averaged about £27 in 2022 Q4, about £341 in 2023 Q1 (peak £495 for the week
  effective 11 January 2023), about £76 in 2023 Q2, about £7 in 2023 Q3 and about £23 in 2023 Q4.
  See section 6. This bears directly on the working explanation; see section 8.
- Weekly charge values for gas and electricity, 14 April 2022 to 31 March 2024, are published by Ofgem and
  reproduced in section 7, so the charge can be applied by lookup without rebuilding the wholesale model.

## 2. Primary sources read

| Short name | Document | Date | URL |
|---|---|---|---|
| Feb 2022 decision | Decision on short-term interventions to address risks to consumers from market volatility | 16 Feb 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-02/Short%20Term%20Interventions%20-%20Decision%20Document.pdf |
| Licence notice (elec) | Modification of the standard conditions of all electricity supply licences: new SLC 24A | 16 Feb 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-02/Elec%20SLC%20Modified%20Decision%20Notice-%20Market%20Stabilisation%20Charge%20.pdf |
| Guidance v1 | MSC guidance (original) | 16 Feb 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-02/MSC%20guidance.pdf |
| May 2022 decision | Decision on changes to market stabilisation charge | 16 May 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-05/Decision%20document%20-%20Changes%20to%20MSC.pdf |
| Guidance v2 | MSC guidance v2.0 | 16 May 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-05/MSC%20guidance%20v2.0.pdf |
| Aug 2022 decision | Decision on extending short-term interventions and adjusting MSC calculation | 26 Aug 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20on%20extending%20Short-Term%20Interventions%20and%20adjusting%20MSCcalculation.pdf |
| Guidance v3 | MSC Guidance (Version 3) | 26 Aug 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-08/MSC%20Guidance%20%28Version%203%29.pdf |
| Wn letter | Letter to suppliers on the use of monthly contract prices | 25 Nov 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-11/Letter%20to%20suppliers%20on%20the%20use%20of%20monthly%20contract%20prices%20in%20calculating%20the%20market%20stabilisation%20charge.pdf |
| Feb 2023 decision | Extending the MSC and BAT beyond 31 March 2023 | 3 Feb 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-02/Extension%20of%20MSC%20and%20BAT%20beyond%20March%202023-%20Decision.pdf |
| Licence notice 2023 (elec) | Licence modification notice, SLC 24A (electricity) | Feb 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-02/Licence%20Mod%20Notice%20-%20SLC%2024A%20%28ELEC%29.pdf |
| Guidance v4 | MSC Calculation Methodology v4.0 (the version in force from 5 April 2023 to expiry) | 20 Mar 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-03/MSC%20Guidance%20%28Version%204%29%20%281%29_0.pdf |
| Technical decision | Decision on technical changes to the MSC model | 20 Mar 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-03/Decision%20on%20technical%20changes%20to%20the%20Market%20Stabilisation%20Charge%20%28MSC%29%20to%20extend%20is%20operation%20beyond%2031%20March%202023%20%281%29.pdf |
| Expiry letter | Future of Market Stabilisation Charge post-March 2024 | 12 Oct 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-10/Future%20of%20Market%20Stabilisation%20Charge%20after%20March%202024.pdf |
| Dashboard | Market Stabilisation Charge dashboard (weekly charge history) | 8 Apr 2024 | https://www.ofgem.gov.uk/data/market-stabilisation-charge-dashboard |
| REC R0034 | Decision to approve REC change R0034 | 8 Apr 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-04/Retail%20Energy%20Code%20R0034%20-%20Market%20Stabilisation%20Charge%20.pdf |
| REC R0035 | Decision to approve REC change R0035 | 27 Jun 2022 | https://www.ofgem.gov.uk/sites/default/files/2022-06/REC%20Change%200035%20Acceptance%20Letter.pdf |
| TDCV 2023 | Decision on Typical Domestic Consumption Values 2023 | 25 May 2023 | https://www.ofgem.gov.uk/sites/default/files/2023-05/TDCV%202023%20Decision%20Letter.pdf |

The Ofgem decision page for the first decision is
https://www.ofgem.gov.uk/decision/decision-short-term-interventions-address-risks-consumers-market-volatility .

## 3. Trigger condition

**domain**: policy_costs
**assumption_tested**: The MSC was payable only when a wholesale cost index fell a stated percentage below the cap's wholesale allowance.
**benchmark_value**: Trigger when the wholesale cost of a notional supplier's hedge (wc) is at or below 90% of the cap's wholesale element (wpc), from 25 May 2022; 70% from 14 April to 24 May 2022. Observed over a five-trading-day window, set weekly, separately for gas and electricity.
**confidence**: H
**source**: Ofgem MSC Guidance v4.0, 20 March 2023, paras 1.5, 1.6, 2.4, 2.5, 2.33, 2.34; Feb 2022 decision paras 3.60; May 2022 decision, page 1.
**date**: 2026-11-23
**finding**: The two indices compared are both Ofgem-built notional hedges, not a quoted market index. wpc is the cap's own wholesale allowance as indexed by the cap methodology, weighted across the current and next two cap periods. wc is the forward-market cost of the same notional hedge for the same periods. The trigger is a ratio, not an absolute price.

Verbatim:

> "The MSC will only take effect where wholesale gas and/or electricity prices fall below the implied price cap wholesale element for the relevant period, taken as an average over a 5-day observation window."
> Guidance v4, para 1.5.

> "The Losing Supplier Loss Trigger is met when the wholesale cost (wc , see below) is less than or equal to 90% of the wholesale element of the price cap for the relevant period (wpc , see below). The MSC is therefore initially triggered when the wholesale cost (wc , see below) falls more than 10% lower than the wholesale cost element of the price cap (wpc)."
> Guidance v4, para 2.5.

> "The Market Stabilisation Charge is triggered when the average wholesale price in a weekly (Monday - Friday) observation window (wc) is 10% or more below the weighted rolling average of the price cap index (wpc) for the relevant fuel."
> Guidance v4, para 2.33.

> "As the MSC comprises two sub-charges, it is possible that only one of these charges may be triggered at any given time."
> Guidance v4, para 2.34. (The weekly series in section 7 shows this happening: gas alone in November 2022, electricity alone in December 2022 and most of summer 2023.)

Original and changed parameter, dated:

> "We have decided to set this trigger point at 30% below (i.e., at 70% of) the implied price cap wholesale element for the relevant period (ie summer 2022)."
> Feb 2022 decision, para 3.60.

> "Alter the parameters so that the threshold (the percentage the wholesale price must fall below the price cap assumptions before the MSC applies) is reduced from 30% to 10% and the derating factor (the percentage of incremental hedging losses covered by the MSC) is increased from 75% to 85%"
> May 2022 decision, page 1. "The revisions ... come into force on 25 May 2022."

How wpc and wc are built (guidance v4, paras 2.7 to 2.17, 2.29, Appendices 1 and 2): each is a weighted average of three terms, the current cap period (n), the next (n+1) and the one after (n+2), each multiplied by a fuel-specific seasonal demand weight S and by hedge-volume weights (a, b, c for wpc in delivery days; a', b', c' for wc in trading days). The nominal supplier hedges "progressively an average of 4.5 months ahead" (para 2.1), on the cap's 3-1.5-3 quarterly indexation profile. wpc terms (PCn, PCn+1, PCn+2) are the cap indexation values; wc terms (wn, wn+1, wn+2) are forward-contract prices: wn uses monthly products by a fixed table (M+1, or average of M+1 and M+2, as the cap period runs out; guidance v4 Table 1 and the Wn letter), wn+1 and wn+2 use quarter+1 and quarter+2 ahead prices (para 2.15). **GAP:** the underlying forward price source and the cap's index series are not given as a time series in any document read; the dashboard publishes only the final £/MWh values. Ofgem's Excel worked examples hold the mechanics, were listed but not parsed (no spreadsheet library on this machine).

## 4. Formula

**domain**: policy_costs
**assumption_tested**: The MSC formula is a closed-form function of the cap allowance, a forward index, a share and a seasonal weight.
**benchmark_value**: A = x . l . t . c (£ per MWh). x = 0 if wc > wt, else 85% (75% before 25 May 2022). wt = 90% . wpc (70% . wpc before 25 May 2022). Qualifying loss l = wt - wc when triggered, else 0. t = sum of the next 4.5 months' consumption weights for the fuel. c = 0.3412 for gas (p/therm to £/MWh), 1 for electricity.
**confidence**: H
**source**: Ofgem MSC Guidance v4.0, 20 March 2023, paras 2.3 to 2.28; Guidance v1 (16 Feb 2022) para 2.3.
**date**: 2026-11-23
**finding**: The formula is published in full and is simple once wpc, wc and t are known. A published inconsistency: v4 para 2.21 prints l = v.(wt - wc) although v4 says the volume factor v was removed for quarterly indexation; for 5 April 2023 onward the consistent reading is l = wt - wc. **[unverified]** whether v was applied to the published numbers from 5 April 2023; the v4 summary of changes says "Removal of the reference to v, the volume factor, as it is no longer required for Quarterly indexation".

Verbatim (v4, paras 2.3 and 2.4, 2.19 to 2.21):

> "The MSC is based on a four factor formula to give a £/MWh charge, with two of these factors varying with time and/or wholesale prices."

```
A = x . l . t . c
x : derating factor (%)            wc > wt : x = 0 ;   wc <= wt : x = 85%
l : qualifying losses (£/MWh)    wc > wt : l = 0 ;   wc <= wt : l = wt - wc      (v4 prints l = v.(wt - wc); see above)
t : consumption weighting factor (%)
c : conversion factor              gas 0.3412 ; electricity 1
wt = 90% . wpc
```
(Guidance v4 paras 2.4, 2.19-2.21, 2.27-2.28. In v1 the same formula had x = 75% and wt = 70% . wpc, para 2.3.)

> "Even if the MSC is triggered, the MSC does not apply to losses above wt, so wholesale savings between the wholesale element of the price cap (wpc) and wt could be passed directly on to active customers in full; only savings beyond wt will be dampened by the MSC."
> Guidance v4, para 2.21.

> "The term t tracks the seasonality and should reflect the value of the hedge held. It is calculated monthly and is the sum of the next 4.5 months demand weights (%) for the relevant fuel"
> Guidance v4, para 2.24. Rationale, para 2.22: the nominal supplier "will only have purchased energy to cover a proportion (approx. 4.5 months) of the lost customer's annual consumption."

> "The conversion factor for gas (c_gas) is equal to 0.3412." "The conversion factor for electricity (c_elec) is 1 as qualifying losses are expressed in £/MWh."
> Guidance v4, paras 2.27, 2.28.

Plain restatement **[derived]**: once triggered, the gainer pays 85% of the gap between 90% of the cap's wholesale allowance and the forward cost, times the share of annual volume the loser's hedge notionally covers, times the customer's annual volume. The gap between 100% and 90% of wpc is never charged.

Indexation history of the formula (what changed the algebra, not the parameters):
- v1, 16 Feb 2022: nominal hedge on the cap's 6-2-6 seasonal profile, "suppliers hedge progressively an average of 8 months ahead" (para 2.1).
- v2, 16 May 2022: 10% / 85%; electricity losses and unidentified gas (UIG) added (guidance v4 version table).
- v3, 26 Aug 2022, in force 7 Sep 2022: transitional weights for the move to quarterly cap updates; introduced volume factor v.
- v4, 20 Mar 2023, in force from the model run of 3 April 2023, effective 5 April 2023: 3-1.5-3 quarterly profile; "It is intended to remain in effect until the model run of Monday 25 March 2024, effective until Sunday 31 March 2024." (Technical decision.)

## 5. The share, scope and settlement

### 5.1 Share paid by the gainer to the loser, with dates

**domain**: policy_costs
**assumption_tested**: The gaining supplier paid a stated share of the losing supplier's hedging loss.
**benchmark_value**: 75% of incremental hedging losses beyond the trigger from 14 April 2022; 85% from 25 May 2022 to expiry on 31 March 2024. The first-decision trigger was 30% and was cut to 10% on the same date.
**confidence**: H
**source**: Feb 2022 decision paras 3.60 to 3.62; May 2022 decision page 1; Aug 2022 decision para 2.3; Feb 2023 decision para 1.14; Guidance v4 paras 1.6, 2.19.
**date**: 2026-11-23
**finding**: The share is the "derating factor". It changed once. No later decision changed the parameters; a "parameter review" in spring 2023 was promised but the v4 guidance of 20 March 2023 still carries 10% and 85%, and the October 2023 letter let the charge lapse. No parameter decision after May 2022 was found in Ofgem's publication index (absence of evidence, not a proof of absence).

> "We have decided to set the derating factor at 75%. This is at the top end of the indicative 50-75% range that we included in our consultation."
> Feb 2022 decision, para 3.61.

> "The effect of the MSC is that if the forward market price over the price cap indexation period is more than 10% (the threshold parameter) below the value indexed under the price cap, 85% (the de-rating parameter) of the difference has to be paid by the gaining supplier to the losing supplier when a customer switches."
> Aug 2022 decision, para 2.3. (This is Ofgem's own one-sentence statement of the rule, and it slightly simplifies it: the 85% applies to the difference beyond the 10% trigger, per the formula in section 4.)

> "Ofgem 2023 ... 'Following a further period of consultation, on 3 February 2023 we decided to extend the MSC again, subject to an earlier or later cessation date being specified, until the end of March 2024.'"
> Guidance v4, para 1.1.

The dates of each parameter set:

| Period | Trigger (below wpc) | Share (x) | Source |
|---|---|---|---|
| 14 Apr 2022 to 24 May 2022 | 30% (wt = 70% of wpc) | 75% | Feb 2022 decision; guidance v1 |
| 25 May 2022 to 31 Mar 2024 | 10% (wt = 90% of wpc) | 85% | May 2022 decision; guidance v2 to v4 |

No charge was actually positive in the first period (section 7).

### 5.2 Per customer, per fuel, per meter point

**domain**: policy_costs
**assumption_tested**: The charge is levied per customer and per fuel, in proportion to that customer's volume.
**benchmark_value**: Per fuel: two separate sub-charges, gas and electricity. Per customer: gainer pays the weekly £/MWh rate times the switching customer's Estimated Annual Consumption (electricity) or Annual Quantity (gas). Whether the unit is the meter point is not stated in terms.
**confidence**: M
**source**: Guidance v4 paras 1.3, 1.4, 2.22, 2.30; Feb 2022 decision paras 3.39, 3.70.
**date**: 2026-11-23
**finding**: Per-fuel is explicit. Per-customer volumetric is explicit. The words "meter point" (MPAN or MPRN) do not appear in the guidance or the two REC decisions read; EAC and AQ are meter-point attributes in industry data, so a meter-point unit is the likely reading **[unverified]**. A dual-fuel customer switching therefore owes both sub-charges.

> "Under this measure, all suppliers acquiring a domestic customer are required to pay the MSC to the losing supplier. This is a volumetric charge and represents a proportion of the economic loss to the losing supplier for the energy purchased on behalf of their customer."
> Guidance v4, para 1.3.

> "The MSC is comprised of two sub-charges; one for gas and one for electricity ... The MSC is applicable to all domestic customer switches between licensed gas and electricity suppliers."
> Guidance v4, para 1.4.

> "The MSC billed to gaining suppliers uses each customer's estimated annual consumption of gas and/or electricity (Estimated Annual Consumption (EAC) / Annual Quantity (AQ) volumes)."
> Guidance v4, para 2.22.

### 5.3 Which customers and tariffs were in scope

**domain**: policy_costs
**assumption_tested**: The MSC applied to domestic switches whatever the tariff the customer left, and whatever tariff they joined.
**benchmark_value**: Domestic customers only. Every domestic switch between licensed suppliers; no exclusion by tariff type, fixed or default, was implemented.
**confidence**: M
**source**: Licence notice (elec) 16 Feb 2022 clause 24A.1 and Schedule 2; Guidance v4 para 1.4; May 2022 decision paras 5.10 to 5.13.
**date**: 2026-11-23
**finding**: Domestic only (non-domestic switches were not covered). Ofgem was asked to exclude customers leaving non-capped (fixed) contracts, because such losers have no cap-indexed hedge to unwind, and declined on data grounds, treating the over-payment as small and absorbed by the 85% derating. So a switcher leaving a fixed deal, and a first-term fixed customer won from a default tariff, were both charged the same way. Whether new connections and house-move gains (not a switch from a "Losing Supplier") and Supplier-of-Last-Resort transfers were in scope is **GAP**: the licence definition of Acquiring Supplier is "a licensee to whom a Domestic Customer switches from a Losing Supplier".

> "If the licensee is an Acquiring Supplier in respect of a Domestic Customer, and the Losing Supplier Loss Trigger is met in respect of that Domestic Customer, it must pay the Market Stabilisation Charge (if any) ..."
> Licence notice, clause 24A.1. Definitions: "Acquiring Supplier means in respect of a Domestic Customer, a licensee to whom a Domestic Customer switches from a Losing Supplier."

> "Two stakeholders suggested that the MSC should exclude switches from contracts that were not subject to the price cap, otherwise losing suppliers would be over-compensated ... This is a known issue, but the existing industry data flows do not facilitate implementing this refinement. There would therefore be significant cost in doing so. For the moment, the issue is relatively small and is effectively accommodated for by the derating factor."
> May 2022 decision, paras 5.10 and 5.11.

> "In the event that the charge is triggered, we expect that suppliers will look to pass the MSC onto consumers in the pricing of new acquisition tariffs."
> Feb 2022 decision, para 3.57.

### 5.4 Who computes it, when it is published, who pays whom, and the settlement cadence

**domain**: policy_costs
**assumption_tested**: Ofgem sets a weekly rate and an industry body settles the pounds.
**benchmark_value**: Ofgem publishes the £/MWh rate each Monday (ex-ante), effective from 00:00 the following Wednesday for seven days. RECCo (Retail Energy Code Company) turns it into pounds using net EAC and AQ volumes gained and lost by each supplier "over the course of a billing period" and runs invoicing under the REC. Billing period length and payment terms are not stated.
**confidence**: M for who and when; GAP for billing period and payment terms
**source**: Guidance v4 paras 2.30 to 2.32, 2.39; Feb 2022 decision paras 3.69, 3.70; REC R0034 and R0035 decisions.
**date**: 2026-11-23
**finding**: Rate publication cadence is exact. Settlement is net per supplier across all switches in the period, which is not the same as each acquisition paying its own charge: a supplier that both gains and loses customers in a billing period settles a net volume. This matters for a simulation that attributes the charge to individual wins; the gross per-win cost an acquirer prices in is the weekly rate times the customer's volume, but cash paid is on the net position. **GAP:** the REC MSC Schedule text, the billing period, the payment due date and the dispute rules were not read; Ofgem's February 2022 decision said "The billing frequency of the MSC is yet to be determined".

> "Ofgem will publish the gas and electricity charge values ex-ante, on a weekly basis, based on the average of the previous five trading days' values for wc and wt (or for a shorter period if any of the weekdays are public holidays)."
> Guidance v4, para 2.31.

> "Ofgem will publish the charge value at the end of the working day each Monday (or the following working day if the Monday/Tuesday is a public holiday). The updated charge value will take effect from 00.00am on the Wednesday after publication (or Thursday/Friday if the Monday/Tuesday is a public holiday). The charge will then remain in place until the next scheduled weekly charge takes effect."
> Guidance v4, para 2.32.

> "RECCo will use this charge and switching data containing net EAC and AQ volumes gained/lost by suppliers to calculate a £ denominated cost/payment due to each supplier over the course of a billing period."
> Guidance v4, para 2.30.

> "The billing frequency of the MSC is yet to be determined. While it is possible that some aspects of administrative arrangements for the MSC may not be finalised by 14 April 2022, we nonetheless expect that all suppliers who gain or lose domestic consumers after that date may accrue MSC liabilities or be entitled to payments once the new licence condition takes effect on that date."
> Feb 2022 decision, para 3.70.

> "RECCo calculating credit and debits based on all switches across the market and the level of charge set by Ofgem."
> REC R0034 decision (8 April 2022). R0034 was approved 8 April 2022 with implementation 14 April 2022 (the page's own table); R0035 "Market Stabilisation Charge - Administration" was approved 27 June 2022 (guidance v4, para 2.39).

The licence says the charge is paid "to such person as may be specified in the Retail Energy Code and for the benefit of the relevant Losing Supplier" (clause 24A.2 of the first notice), so the legal payee is a code body, not the losing supplier directly; the money is for the loser's benefit.

### 5.5 Start and end dates

**domain**: policy_costs
**assumption_tested**: The MSC was in force from 14 April 2022 to 31 March 2024.
**benchmark_value**: In force 14 April 2022. First licence expiry 30 September 2022 (extendable to 31 March 2023); extended on 26 August 2022 to 31 March 2023; extended on 3 February 2023 to 31 March 2024 with effect from 1 April 2023; allowed to lapse at 23:59 on 31 March 2024.
**confidence**: H
**source**: Licence notice 16 Feb 2022 ("This decision will take effect from 14 April 2022"; clause 24A.3 as first drafted); Aug 2022 decision; Feb 2023 decision; Expiry letter 12 Oct 2023; Dashboard 8 Apr 2024.
**date**: 2026-11-23
**finding**: Confirms the assumption in `switching_mechanics_2026-10-25.md` and closes the date question. Ofgem announced the lapse on 12 October 2023, five and a half months ahead.

> "The MSC is extended until 31 March 2023."
> Aug 2022 decision, front page.

> "SLC 24A will cease to have effect at 23:59 on 30 September 2022 31 March 2024, or such later date, no later than 31 March 2023, as specified by the Authority ..." (marked-up licence text; the earlier date is struck through in the source)
> Licence notice 2023 (elec), clause 24A.3. The 2023 change also lets the Authority renew annually: "a later date, to be 23:59 on 31 March 2025 and thereafter on the anniversary of that date".

> "The MSC licence condition SLC 24A ceases to have effect at 23.59 on 31 March 2024. For the reasons set out above we do not intend to extend the MSC past this date."
> Expiry letter, 12 October 2023.

> "The Market Stabilisation Charge (MSC) came to an end on 31 March 2024. The MSC was a temporary measure in place from 14 April 2022 to 31 March 2024 which required all domestic suppliers acquiring a domestic customer to pay a charge to the losing supplier when wholesale prices fell considerably below the relevant wholesale price cap index."
> Dashboard, 8 April 2024.

Why Ofgem let it lapse (expiry letter): "market risks that the MSC is designed to mitigate ... are now markedly less"; "The MSC's negative impact on competition is also greater than at the height of the crisis in 2022"; "the MSC is likely to make it more difficult for suppliers to price [fixed term contracts] competitively against the price cap". The same letter says tariff offerings "fell markedly in Q2 2022, when MSC/BAT were introduced, suggesting a significant direct impact (noting that other factors will also have had an effect)".

## 6. How big the charge was in pounds per customer

**domain**: policy_costs
**assumption_tested**: The MSC added a material pounds-per-customer cost to a fixed-price acquisition during 2022 Q4 to 2023 Q4.
**benchmark_value**: **[derived]** For a typical dual-fuel household (2,900 kWh electricity and 12,000 kWh gas to 30 Sep 2023; 2,700 kWh and 11,500 kWh from 1 Oct 2023): 2022 Q4 mean about £27 and max £248; 2023 Q1 mean about £341 and max £495; 2023 Q2 mean about £76; 2023 Q3 mean about £7; 2023 Q4 mean about £23; 2024 Q1 mean about £74.
**confidence**: M (the weekly rates are authoritative; the pound conversion is this page's arithmetic using the TDCV as the customer's EAC and AQ)
**source**: Ofgem MSC dashboard (weekly rates, retrieved 2026-11-23); TDCV 2023 decision letter, 25 May 2023, medium-TDCV table (medium TDCV: gas 12,000 to 11,500 kWh, electricity 2,900 to 2,700 kWh; "new TDCVs from 1 October 2023"); Guidance v4 para 2.22 (billing on EAC/AQ).
**date**: 2026-11-23
**finding**: The charge was large only from late December 2022 to April 2023, and then only at the Ofgem-published rate times the customer's own EAC and AQ. A household using more than the TDCV pays proportionally more. It was close to zero in 2023 Q3. It was never published by Ofgem as a pounds-per-customer figure; no Ofgem or trade-press per-customer figure was found (**GAP**: Cornwall Insight and other press could not be fetched from this machine; do not treat the derived values as press figures).

Method **[derived]**: pounds per dual-fuel household = (electricity £/MWh x TDCV electricity MWh) + (gas £/MWh x TDCV gas MWh), by weekly effective-from date. The £/MWh values already contain x, l, t and c (guidance v4 paras 2.4, 2.30), so no further scaling applies. The quarters group the 102 weekly rows by effective-from date and so differ slightly at quarter edges.

| Effective week from | Gas £/MWh | Elec £/MWh | Elec £ | Gas £ | Dual-fuel £ |
|---|---|---|---|---|---|
| 2022-11-16 | 3.56 | 0 | 0 | 43 | 43 |
| 2022-12-21 | 0 | 12.03 | 35 | 0 | 35 |
| 2022-12-30 | 11.57 | 37.63 | 109 | 139 | 248 |
| 2023-01-11 (peak) | 23.37 | 73.84 | 214 | 280 | 495 |
| 2023-02-15 | 16.78 | 53.80 | 156 | 201 | 357 |
| 2023-03-15 | 10.22 | 34.02 | 99 | 123 | 221 |
| 2023-04-05 | 5.26 | 21.17 | 61 | 63 | 125 |
| 2023-05-17 | 3.22 | 15.79 | 46 | 39 | 84 |
| 2023-06-14 | 1.54 | 10.51 | 30 | 18 | 49 |
| 2023-07-12 | 0 | 2.10 | 6 | 0 | 6 |
| 2023-09-13 | 0 | 2.84 | 8 | 0 | 8 |
| 2023-11-15 | 0.00 | 1.02 | 3 | 0 | 3 |
| 2023-12-20 | 5.34 | 9.92 | 27 | 61 | 88 |
| 2024-01-24 | 6.67 | 12.27 | 33 | 77 | 110 |
| 2024-03-13 | 2.37 | 5.38 | 15 | 27 | 42 |
| 2024-03-27 | 1.18 | 2.29 | 6 | 14 | 20 |

| Quarter (by effective-from date) | Weeks triggered | Mean elec £/MWh | Mean gas £/MWh | Mean dual-fuel £ | Max dual-fuel £ |
|---|---|---|---|---|---|
| 2022 Q2 (from 14 Apr) | 0 | 0 | 0 | 0 | 0 |
| 2022 Q3 | 0 | 0 | 0 | 0 | 0 |
| 2022 Q4 | 5 | 3.82 | 1.36 | 27 | 248 |
| 2023 Q1 | 13 | 51.84 | 15.91 | 341 | 495 |
| 2023 Q2 | 13 | 14.08 | 2.95 | 76 | 125 |
| 2023 Q3 | 11 | 2.28 | 0.02 | 7 | 17 |
| 2023 Q4 | 9 | 3.02 | 1.25 | 23 | 91 |
| 2024 Q1 | 13 | 8.39 | 4.45 | 74 | 110 |

(2022 Q2 and 2022 Q3 hold 12 weeks each, every other quarter 13; "triggered" is Ofgem's "Has MSC process been triggered?" column, which is Yes in a week when either fuel is above zero.)

Ofgem's own illustrations at the time of the first decision (annualised savings an active switcher would lose, under the *original* 30% / 75% parameters, for an assumed fall in wholesale prices; not the same thing as the later weekly charge): "40% wholesale price drop ... MSC level £21 (April drop) and £67 (September drop)"; "60% ... £90 and £196". (Feb 2022 decision, Table 4.) The 10%/85% parameters from 25 May 2022 are stronger than the ones in that table.

Ofgem on EPG interaction in early 2023, which matters for what an acquirer could price:

> "Forward wholesale prices have fallen below the price cap but have largely remained above the level currently implied by the EPG. Factoring in the cost of the MSC payment which would be owed by a supplier from gaining a customer, suppliers have not yet priced any fixed price contracts below £2,500 which could result in a significant increase in switching and amount of MSC payments made."
> Feb 2023 decision, para 3.3. The decision also says "only a relatively small amount of MSC payments have been made, as the impact of the EPG is to depress switching rates."

The first sentence names the cap-level reference an acquirer priced against (the EPG's £2,500 typical-household ceiling) and confirms the MSC was an explicit input to fixed-deal pricing in early 2023. **GAP:** total MSC pounds paid across the market, and any supplier's reported MSC cost, were not found in the sources read.

## 7. The published weekly charge series (Ofgem dashboard, 102 weeks)

Source: https://www.ofgem.gov.uk/data/market-stabilisation-charge-dashboard, page dated 8 April 2024, retrieved 2026-11-23. Columns: publication date (Monday), effective from (Wednesday), effective to, "Has MSC process been triggered?", gas £/MWh, electricity £/MWh. One effective-from cell is mistyped in the source as "12/10.2022"; it is read as 12/10/2022. Dates are ISO here; the source uses dd/mm/yyyy. A week with a "No" has both values 0.

```
published   eff_from    eff_to      trig  gas_GBP_MWh  elec_GBP_MWh
2022-04-12  2022-04-14  2022-04-20  No     0.00    0.00
2022-04-19  2022-04-21  2022-04-26  No     0.00    0.00
2022-04-25  2022-04-27  2022-05-04  No     0.00    0.00
2022-05-03  2022-05-05  2022-05-10  No     0.00    0.00
2022-05-09  2022-05-11  2022-05-17  No     0.00    0.00
2022-05-16  2022-05-18  2022-05-24  No     0.00    0.00
2022-05-23  2022-05-25  2022-05-31  No     0.00    0.00
2022-05-30  2022-06-01  2022-06-07  No     0.00    0.00
2022-06-06  2022-06-08  2022-06-14  No     0.00    0.00
2022-06-13  2022-06-15  2022-06-21  No     0.00    0.00
2022-06-20  2022-06-22  2022-06-28  No     0.00    0.00
2022-06-27  2022-06-29  2022-07-05  No     0.00    0.00
2022-07-04  2022-07-06  2022-07-12  No     0.00    0.00
2022-07-11  2022-07-13  2022-07-19  No     0.00    0.00
2022-07-25  2022-07-27  2022-08-02  No     0.00    0.00
2022-08-01  2022-08-03  2022-08-09  No     0.00    0.00
2022-08-08  2022-08-10  2022-08-16  No     0.00    0.00
2022-08-15  2022-08-17  2022-08-23  No     0.00    0.00
2022-08-22  2022-08-24  2022-08-31  No     0.00    0.00
2022-08-30  2022-09-01  2022-09-06  No     0.00    0.00
2022-09-05  2022-09-07  2022-09-13  No     0.00    0.00
2022-09-12  2022-09-14  2022-09-21  No     0.00    0.00
2022-09-20  2022-09-22  2022-09-27  No     0.00    0.00
2022-09-26  2022-09-28  2022-10-04  No     0.00    0.00
2022-10-03  2022-10-05  2022-10-11  No     0.00    0.00
2022-10-10  2022-10-12  2022-10-18  No     0.00    0.00
2022-10-17  2022-10-19  2022-10-25  No     0.00    0.00
2022-10-24  2022-10-26  2022-11-01  No     0.00    0.00
2022-10-31  2022-11-02  2022-11-08  No     0.00    0.00
2022-11-07  2022-11-09  2022-11-15  No     0.00    0.00
2022-11-14  2022-11-16  2022-11-22  Yes    3.56    0.00
2022-11-21  2022-11-23  2022-11-29  Yes    2.04    0.00
2022-11-28  2022-11-30  2022-12-06  Yes    0.49    0.00
2022-12-05  2022-12-07  2022-12-13  No     0.00    0.00
2022-12-12  2022-12-14  2022-12-20  No     0.00    0.00
2022-12-19  2022-12-21  2022-12-29  Yes    0.00   12.03
2022-12-28  2022-12-30  2023-01-04  Yes   11.57   37.63
2023-01-03  2023-01-05  2023-01-10  Yes   19.61   63.62
2023-01-09  2023-01-11  2023-01-17  Yes   23.37   73.84
2023-01-16  2023-01-18  2023-01-24  Yes   21.99   70.60
2023-01-23  2023-01-25  2023-01-31  Yes   23.39   71.38
2023-01-30  2023-02-01  2023-02-07  Yes   18.09   64.48
2023-02-06  2023-02-08  2023-02-14  Yes   16.99   57.56
2023-02-13  2023-02-15  2023-02-21  Yes   16.78   53.80
2023-02-20  2023-02-22  2023-02-28  Yes   16.42   49.69
2023-02-27  2023-03-01  2023-03-07  Yes   11.60   42.69
2023-03-06  2023-03-08  2023-03-14  Yes   11.14   39.29
2023-03-13  2023-03-15  2023-03-21  Yes   10.22   34.02
2023-03-20  2023-03-22  2023-03-28  Yes    9.08   28.59
2023-03-27  2023-03-29  2023-04-04  Yes    8.18   24.31
2023-04-03  2023-04-05  2023-04-12  Yes    5.26   21.17
2023-04-11  2023-04-13  2023-04-18  Yes    4.10   16.08
2023-04-17  2023-04-19  2023-04-25  Yes    4.48   17.36
2023-04-24  2023-04-26  2023-05-02  Yes    4.41   17.19
2023-05-02  2023-05-04  2023-05-10  Yes    3.20   16.87
2023-05-09  2023-05-11  2023-05-16  Yes    3.33   17.13
2023-05-15  2023-05-17  2023-05-23  Yes    3.22   15.79
2023-05-22  2023-05-24  2023-05-31  Yes    3.26   15.38
2023-05-30  2023-06-01  2023-06-06  Yes    2.89   15.54
2023-06-05  2023-06-07  2023-06-13  Yes    2.43   14.92
2023-06-12  2023-06-14  2023-06-20  Yes    1.54   10.51
2023-06-19  2023-06-21  2023-06-27  Yes    0.28    2.98
2023-06-26  2023-06-28  2023-07-04  Yes    0.00    2.07
2023-07-03  2023-07-05  2023-07-11  Yes    0.00    2.30
2023-07-10  2023-07-12  2023-07-18  Yes    0.00    2.10
2023-07-17  2023-07-19  2023-07-25  Yes    0.22    4.97
2023-07-24  2023-07-26  2023-08-01  Yes    0.00    4.30
2023-07-31  2023-08-02  2023-08-08  Yes    0.00    3.61
2023-08-07  2023-08-09  2023-08-15  Yes    0.00    4.00
2023-08-14  2023-08-16  2023-08-22  Yes    0.00    1.29
2023-08-21  2023-08-23  2023-08-30  No     0.00    0.00
2023-08-29  2023-08-31  2023-09-05  No     0.00    0.00
2023-09-04  2023-09-06  2023-09-12  Yes    0.00    0.52
2023-09-11  2023-09-13  2023-09-19  Yes    0.00    2.84
2023-09-18  2023-09-20  2023-09-26  Yes    0.00    1.74
2023-09-25  2023-09-27  2023-10-03  Yes    0.00    2.03
2023-10-02  2023-10-04  2023-10-10  Yes    0.00    2.19
2023-10-09  2023-10-11  2023-10-17  Yes    0.30    4.03
2023-10-16  2023-10-18  2023-10-24  No     0.00    0.00
2023-10-23  2023-10-25  2023-10-31  No     0.00    0.00
2023-10-30  2023-11-01  2023-11-07  No     0.00    0.00
2023-11-06  2023-11-08  2023-11-14  No     0.00    0.00
2023-11-13  2023-11-15  2023-11-21  Yes    0.00    1.02
2023-11-20  2023-11-22  2023-11-28  Yes    0.00    1.10
2023-11-27  2023-11-29  2023-12-05  Yes    0.00    1.37
2023-12-04  2023-12-06  2023-12-12  Yes    1.46    3.82
2023-12-11  2023-12-13  2023-12-19  Yes    3.37    6.80
2023-12-18  2023-12-20  2023-12-28  Yes    5.34    9.92
2023-12-27  2023-12-29  2024-01-03  Yes    5.77    9.03
2024-01-02  2024-01-04  2024-01-09  Yes    5.07    6.97
2024-01-08  2024-01-10  2024-01-16  Yes    5.49    8.14
2024-01-15  2024-01-17  2024-01-23  Yes    5.89   10.00
2024-01-22  2024-01-24  2024-01-30  Yes    6.67   12.27
2024-01-29  2024-01-31  2024-02-06  Yes    6.64   12.11
2024-02-05  2024-02-07  2024-02-13  Yes    4.44    9.50
2024-02-12  2024-02-14  2024-02-20  Yes    4.55    9.46
2024-02-19  2024-02-21  2024-02-27  Yes    5.04   10.36
2024-02-26  2024-02-28  2024-03-05  Yes    5.16   10.41
2024-03-04  2024-03-06  2024-03-12  Yes    3.11    7.42
2024-03-11  2024-03-13  2024-03-19  Yes    2.37    5.38
2024-03-18  2024-03-20  2024-03-26  Yes    2.24    4.77
2024-03-25  2024-03-27  2024-03-31  Yes    1.18    2.29
```

Effective-to dates in the source are irregular around bank holidays; effective-from is the lookup key.

## 8. What this means for the working explanation

This section is the discovery agent's reading of the sources, not a finding about the simulation, which was not read.

1. **Period mismatch for 2022 Q4.** The published charge was zero in each of the first 30 weekly rates (effective 14 April to 9 November 2022) and averaged about £27 per typical dual-fuel customer over the 2022 Q4 weeks. On the published rule it cannot be the main reason a 2022 Q4 first-term fixed quote sits 15 to 37% below the market's cheapest published fix. **[derived]**
2. **2023 Q1 is the one quarter where the charge was large.** About £341 per typical dual-fuel customer (peak £495), against annual bills that were in the thousands of pounds. Whether that is 15% or 5% of a fixed deal's price depends on the deal price; the bill level was not sourced here, so no ratio is stated (**GAP**).
3. **2023 Q3 and Q4 charges were small (£7 and £23 mean).** The MSC cannot account for a gap that persists at those levels. **[derived]**
4. **Ofgem's own publications name more than the MSC as a brake on cheap fixed deals.** Ofgem names the EPG £2,500 level as the binding reference (Feb 2023 decision, para 3.3) and the BAT (SLC 22B, in force from 14 April 2022) as a separate rule that stopped cheap acquisition-only deals. The market's cheapest published fix therefore reflects EPG, BAT and a lagged cap allowance in addition to any MSC; a simulation that charges the MSC alone would be correcting only part of that.
5. A first-term fixed quote below the cheapest market fix is not a breach of the MSC rule by itself. The MSC did not set a price floor; it set a cost the acquirer paid to the loser, which a rational acquirer priced in or absorbed.

## 9. A note on 2026

The Ofgem pages show a new MSC: a licence condition reintroduced on a "decision" of 2026 (consultation 17 April to 16 May 2026) and an activation decision with the statement "The MSC activation will take effect from 25 November 2026" (page last updated 17 November 2026). https://www.ofgem.gov.uk/consultation/market-stabilisation-charge-activation . Its parameters were not read; it is outside the 2016 to 2025 record this page serves and should not be confused with the 2022 to 2024 rule. **GAP:** whether the 2026 design matches the 2022 formula.

## 10. What a simulation needs to charge it

Inputs to the formula, and whether each is published:

| Input | Needed for | Published? | Where |
|---|---|---|---|
| Weekly gas and electricity MSC rate, £/MWh (A), 102 weeks | Charging directly by lookup (the simplest route; contains x, l, t, c) | Yes, by Ofgem | Section 7; the Ofgem dashboard |
| Customer EAC (electricity) and AQ (gas), per fuel | The volume the rate multiplies | In the simulation's own world (not a published series); TDCV as a fallback | TDCV 2023 decision letter for the TDCV |
| Switch effective date, to pick the week | Choosing the weekly rate | Simulation-internal | Rate effective from 00:00 Wednesday after Monday publication (guidance v4 para 2.32) |
| Trigger fraction (10%, or 30% before 25 May 2022) and share x (85%, or 75%) | Rebuilding the formula | Yes | Sections 3, 4, 5.1 |
| wpc: cap indexation values for the current and next two cap periods, per fuel, £/MWh or p/therm | Rebuilding the formula | Cap levels yes, but the exact weighted index series for the MSC is not a published time series | Ofgem price cap decisions (not read for this page); MSC worked-example workbooks (not parsed) |
| wc: forward contract prices (monthly for the current period, quarter+1 and quarter+2 ahead), per fuel | Rebuilding the formula | Not published as a series by Ofgem; commercial forward data (ICE, ICIS, LSEG) | **GAP** for an open source |
| Seasonal demand weights S and consumption weights for t, per fuel | Rebuilding the formula | Yes, in method, in Ofgem's "Demand and Losses" workbook and Annex 2 of the cap; not extracted | **GAP** for extracted values |
| Hedge-volume weights a, b, c, a', b', c' | Rebuilding the formula | Yes, as day-count algebra | Guidance v4 Appendices 1 and 2 |
| Electricity losses and UIG adjustment | Rebuilding the formula | In the worked example; not extracted | Guidance v2 onward; **GAP** for values |
| Net volume gained and lost by each supplier per billing period | Cash settlement (RECCo) | Simulation-internal | Guidance v4 para 2.30 |
| Billing period and payment terms | Cash timing | **GAP** | REC MSC Schedule (not read) |

Recommended route for the simulated world **[derived, a design opinion for the owner of the world]**: apply the 102 published weekly rates by lookup on the switch effective date times the customer's EAC and AQ, per fuel, to the acquirer, with the loser credited; settle on net position per billing period only if the world models RECCo. Rebuilding wc and wpc from first principles needs commercial forward data and Ofgem's workbooks, and would only reproduce numbers Ofgem already publishes. The published series is the authoritative output; the formula is useful only to test counterfactuals (a different trigger or share).

## 11. What is not established

- **GAP:** billing period, payment due date, dispute process and the REC MSC Schedule text.
- **GAP:** whether the charge applied to new connections, house moves and Supplier of Last Resort transfers.
- **GAP:** whether the unit was the meter point, and how dual-fuel with different gain dates was handled.
- **GAP:** total pounds paid; any per-customer figure from Cornwall Insight or other press.
- **GAP:** the wpc, wc, S and t value series; the spring 2023 "parameter review" outcome beyond the unchanged v4 parameters.
- No figure on this page rests on memory; the only **[unverified]** item is the meter-point reading in section 5.2.
