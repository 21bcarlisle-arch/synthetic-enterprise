# B2 Category (6) — Customer Acquisition Cost anchors, per channel/segment

Research for B2_OPEX_TAXONOMY_EXPANSION.md's "customer-acquisition cost per
channel per segment as a real cost line." UK-specific where found; clearly
labeled estimates where not.

## Channel 1: Price-comparison site (PCS/aggregator) — residential/mass-market

**Real figure, sourced.** Commission of **£25-£30 per fuel switched**
(so ~£50-£60 for a dual-fuel switch, ~£25-£30 for single-fuel). Historical
CMA-era rate, cited via [The Conversation: "Energy price comparison sites
are bad news for consumers"](https://theconversation.com/energy-price-comparison-sites-are-bad-news-for-consumers-heres-how-to-fix-them-142225),
which states suppliers paid this rate and UK consumers indirectly funded
"over £100 million" annually via >4 million switches/year. Also referenced
in CMA's [Energy market investigation Appendix
8.3](https://assets.publishing.service.gov.uk/media/559fb63ae5274a155c00004c/Appendix_8.3_Price_comparison_websites_and_collective_switches.pdf)
(could not extract exact text from the PDF directly — binary/font-encoded —
but the secondary source's figure is consistent with known industry
commentary on PCW economics). Applies to **Residential** segment.

## Channel 2: Direct/brand marketing (TV/digital/paid search) — residential/mass-market

**Could not source an energy-specific figure.** No UK energy-retail-specific
direct-marketing CAC benchmark found in public sources searched.

**Estimate, cross-industry, clearly flagged:** UK average cost-per-lead
across digital advertising industries is **~£70/lead** (2025 benchmark,
[FetchFunnel](https://www.fetchfunnel.com/advertising-costs-complete-guide/)-style
aggregator sources), reported as rising ~5% YoY from £66.69. Converting
lead → acquired customer needs a conversion-rate assumption (typically
10-30% for a considered-purchase category like energy switching) — this
would put a rough direct-channel CAC in the **£230-£700** range per
acquired customer, but this is a stacked estimate (industry-general CPA ×
an assumed conversion rate), not a real anchor. Flagged as ESTIMATE, low
confidence.

## Channel 3: Broker/intermediary — I&C (industrial & commercial)

**Real figure, sourced, UK-specific.** Commission structure is an ongoing
per-unit "adder" embedded in the customer's unit rate, not a one-off CAC —
this is a structurally different cost shape than residential/PCS (residual
trail commission for the life of the contract, or a discounted upfront lump
sum). Source: [Connection Technologies — "Business Energy Broker Fees 2026:
Save 1-3p/kWh"](https://connection-technologies.co.uk/blog/business-energy-broker-fees-explained)
and corroborating broker-fee explainer sites. Segment bands found:
- **Small business** (25,000-100,000 kWh/yr): **0.5-2.0p/kWh** electricity,
  typically 2-3yr contracts.
- **Mid-market I&C** (100,000-500,000 kWh/yr): **0.3-1.2p/kWh**, more
  negotiating room for a fixed fee instead.
- **Half-hourly metered** (largest I&C): **0.2-0.8p/kWh**, sometimes a
  standing daily fee instead of a per-unit adder.
- **Gas**: lower pence-per-kWh (0.1-0.6p/kWh) but higher volume, broadly
  similar cash value per site.

This maps cleanly onto this sim's segment definitions (SME ≈ small
business band, larger I&C ≈ mid-market/HH bands) — recommend modelling as
an ongoing per-kWh cost line (not a one-off acquisition cost), applied at
billing time, rather than forcing it into the same "one-off CAC per new
customer" shape as the residential channels.

## Segment split summary

- **Residential/mass-market**: one-off CAC, £50-£60/dual-fuel customer via
  PCS (real, sourced), £230-£700 via direct/brand (estimate, low
  confidence, no energy-specific anchor found).
- **SME**: likely blends both residential-style PCS/direct acquisition AND
  broker-led (smaller end of the broker commission bands above) —
  no UK-specific SME-only CAC split found; recommend using the broker
  per-kWh bands for broker-acquired SME and the residential PCS figure for
  PCS-acquired SME, since no single blended SME figure exists publicly.
- **I&C**: broker-led, ongoing per-kWh commission (0.2-2.0p/kWh depending
  on size band), not a one-off CAC — real, UK-specific, sourced.

## What I could not source

- No energy-specific direct/brand-marketing CAC (estimate only, flagged
  low-confidence above).
- No official Ofgem or industry-body report broke out CAC explicitly by
  segment for the residential/SME boundary — the segment split above is a
  reasoned combination of two separately-sourced figures (PCS commission +
  broker per-kWh bands), not a single citation.
