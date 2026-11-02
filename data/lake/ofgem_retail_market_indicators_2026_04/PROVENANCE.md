# Ofgem, Retail market indicators: domestic accounts by tariff type, as of April 2026

- **Source page:** https://www.ofgem.gov.uk/retail-market-indicators. The two charts are everviz/Highcharts
  embeds; their data sits as CSV inside the chart's inject script:
  https://cloud.highcharts.com/inject/4qFp-LBti (electricity) and https://cloud.highcharts.com/inject/B3H1yAIhS (gas).
- **Retrieved:** 2026-11-02, by the autonomous worker. SHA-256 of the extracted CSVs:
  electricity `4d317ec5c387a15ead861a8a5b6651f9ed4083ef1824f277bf3bbbab78f1b48a`,
  gas `a2602f6fcae2fec18bb4f3a1c3d5fcbc68d3747552455f1255397deafe715388`.
- **Publisher, vintage:** Ofgem, from supplier returns. Chart caption "Information correct as of: September 2026";
  the page text dates the reading "as of April 2026". Large and medium suppliers only, prepayment accounts excluded.
- **Licence:** Open Government Licence v3.0.
- **What is here:** the chart CSVs exactly as embedded (account counts per supplier per tariff type). Shares
  derived from them reconcile to Ofgem's own page text: electricity default 53.1% (page 53.2%), default held 3+
  years 31.7%, active-choice fixed 43.5%; gas 53.3%, 32.6%, 45.1%.
- **Read by:** `docs/market_research/the_gb_natural_experiments_that_pin_the_weights_2026-11-02.md`.
