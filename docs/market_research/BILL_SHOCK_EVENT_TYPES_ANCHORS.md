# Bill-shock event types — real UK anchors (research for docs/design/BILL_SHOCK_DEFINITION_FINDING.md)

Research for the director-named real "bill shock" causes -- contract-end tariff reversion and
Direct Debit recalculation -- as distinct from the current mechanism's raw, unresearched
month-on-month >=20% threshold. Research only; no code touched.

## 1. Contract-end tariff reversion — magnitude

**Real, sourced (current market, July 2026).** The Ofgem price cap (the rate a customer reverts
to on a standard variable tariff) rose to £1,862/yr from 1 July 2026, up 13.5% from £1,641/yr.
The cheapest available 12-month fixed deals at the same time run ~£1,602/yr — **£150-£260/yr
(roughly 8-14%) cheaper than the SVT/price-cap rate**, per EnergyPlus's July 2026 market roundup.
Source: https://www.energyplus.co.uk/news/energy-tariffs-2026

**Historically variable, not a fixed constant.** This differential is NOT a stable figure --
it swings with wholesale market conditions (the 2021-22 crisis produced much larger fixed-vs-SVT
gaps industry-wide, per general market commentary found this pass, though no single clean
historical percentage series was located this session). Flag: any redesign should treat this as
a real but time-varying differential, not a fixed constant to hardcode.

**Timing, real and sourced (Ofgem Standard Licence Condition 7A).** A supplier must publish its
deemed-contract terms, allow termination on a maximum 30 days' notice, and may not charge exit
fees on a deemed contract. Separately, exiting a fixed deal within 49 days of its own end date
carries no exit fee (Ofgem rule, widely cited by consumer sites). Sources:
https://www.sefe-energy.co.uk/help-support/contracts-accounts-charges/out-of-contract-deemed-rates/ ,
https://www.uswitch.com/gas-electricity/guides/energy-tariff-ending/

**Could not source:** a single clean "reversion always happens on day X of contract end" rule
distinguishing immediate reversion from a grace period across all suppliers -- practice varies
(some roll straight to a deemed/OOC rate, others to their own default SVT), not standardised
enough to cite one number.

## 2. Direct Debit recalculation — frequency and magnitude

**Real, sourced.** Ofgem ran a formal Direct Debit Market Compliance Review (2022-onward) after
finding "big differences between firms, including how frequently payments are reassessed, how
they factor in price changes, and how they deal with credit or debt balances" -- i.e., DD review
frequency is NOT standardised across the industry, confirmed by the regulator itself, not
estimated. Sources:
https://www.ofgem.gov.uk/decision/direct-debit-market-compliance-review-progress-update ,
https://www.which.co.uk/news/article/ofgem-demands-energy-suppliers-urgently-review-customers-increasing-direct-debits-aimxA8o6AMWk

**Real, sourced rule (not magnitude, but a real constraint).** Ofgem's Credit Balances decision
(2022) requires suppliers to set DD as accurately as possible from available information, notify
customers of any change BEFORE it happens with a clear explanation, and -- where a customer is in
credit -- glide the DD back toward a zero balance over roughly the next 12 months (not an
instant snap-back). Source:
https://www.ofgem.gov.uk/sites/default/files/2022-08/Decision%20letter%20DD%20rules.pdf

**Could not source:** a single "maximum legitimate single-review jump %" figure -- Ofgem's own
review exists precisely because no consistent industry standard was found; this is a genuine,
regulator-acknowledged gap, not a research miss on this pass. Any redesign attempting to model a
"DD jump size" would need its own reasoned estimate, clearly flagged as such, not a citable rule.

## 3. Formal Ofgem "bill shock" definition — does one exist?

**Confirmed: no.** Multiple targeted searches (Ofgem price-cap methodology, consumer protection
literature) returned no formal Ofgem definition of "bill shock" as a term, threshold, or
comparison basis. What IS real and sourced: Ofgem reviews the price cap quarterly (January,
April, July, October) -- a real, structural reason bills can jump at those specific points
industry-wide, distinct from any individual customer's seasonal consumption pattern. Source:
https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/energy-pricing-rules/energy-price-cap

This corroborates (does not prove) the parent finding's observation that April/October showed
elevated shock counts in the real run data -- a plausible genuine cause (quarterly cap resets),
not necessarily pure noise, but still not conclusively separated from seasonal consumption
effects without the actual redesign.

## Summary for a future redesign pass

- Real, sourced: SVT-vs-fixed differential ~8-14% at current (July 2026) market conditions,
  time-varying not fixed; deemed-contract notice/exit-fee rules (SLC 7A); Ofgem's own admission
  that DD review frequency is inconsistent industry-wide; the real Jan/Apr/Jul/Oct price-cap
  reset cadence.
- Not sourced (genuine gaps, not invented): a single legitimate "max DD jump %"; a precise
  historical fixed-vs-SVT gap time series across the whole 2016-2025 window this project
  simulates; a universal reversion-timing rule across all suppliers.
- No formal Ofgem "bill shock" definition exists to adopt wholesale -- any redesign will need to
  define its own working definition, informed by these real constraints, not borrow one that
  doesn't exist.
