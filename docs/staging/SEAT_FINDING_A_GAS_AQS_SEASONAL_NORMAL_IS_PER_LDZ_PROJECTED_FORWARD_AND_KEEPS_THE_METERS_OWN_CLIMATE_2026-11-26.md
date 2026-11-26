**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Item:** `which-seasonal-normal-is-a-registry-gas-aq-put-on`

# A gas AQ's seasonal normal is per LDZ and projected forward, and the AQ keeps the meter's own climate (26 Nov 2026)

Filed by the delivery seat. This follows
`docs/staging/done/SEAT_FINDING_IS_A_GAS_PREMISES_REGISTERED_AQ_ITS_FIRST_YEAR_OF_TRUE_USE_2026-11-26.md`, which found
that a premise's first year of true use is median 0.915 of the registered AQ. It traced the gap to the
registry putting every meter on the national 1991-2020 E&W normal, while the premise cells run at a
median of 0.911 of that normal's HDD. That left as GAP 4 the question of which normal a real AQ is put
on.

## What was read (knowledge first, K2)

The quotes, sources and hashes are in
`docs/market_research/a_gas_meter_points_aq_is_made_from_its_own_reads.md` s5. In short:

- AQ = AQMQ x 365 / Σ(ALP x (1 + DAF x WCF)), with WCF = CWV - SNCWV, both **per LDZ per gas day**.
  There are 13 LDZs, each with a primary weather station (Yeovilton for SW from Oct 2020).
- The SNCWV is **projected forward** and refreshed at least every five years. The 2025 basis comes
  purely from Met Office UKCP18 projections for gas years 2025/26-2029/30. The 2020 and 2015 bases
  come from a climate-adjusted 1960+ history, using 2013 Met Office predictions out to 2025. Every
  LDZ warmed in 2025, which "will result in a reduction in AQs, especially for ... the domestic
  sector".
- At each basis change, every AQ moves onto the new basis, by recalculation or by an EUC Seasonal
  Normal Ratio.

## What it means

Both parts of the world's 7-8% AQ excess are mostly ones a real supplier does **not** carry:

1. **The urban/local offset.** A real AQ divides out only the LDZ station's anomaly in the read window,
   so a meter warmer than its station keeps its lower use in its AQ. The world's AQ ignores the meter's
   own weather, and so loses that offset.
2. **The climate trend.** A real basis represents the five years it serves. A 1991-2020 average is
   colder than any basis that was in force over 2016-2025.

How much is left over is not sized. The SNCWV values and the Seasonal Normal Ratios are on the UK Link
secure area, and nothing public sets a 2015- or 2020-basis normal beside 1991-2020.

## Decision, and what is handed on

`register_gas_premises_on_their_own_reads` (`simulation/run_phase2b.py`) should put the registry AQ
on the meter's own cell. It should take the meter's own use over the read year at its cell's weather,
then remove only that year's departure from a normal. That is the world's version of AQMQ/WAALP. The
open build choice is which normal the departure is taken against, since the world has no LDZ CWV or
SNCWV. The candidates must be read against the s5 facts, not picked for the answer. One candidate is
the cell's own HDD over the run's record before the acquisition. Another is a basis-period average in
the style of the 5-year window. The build turn decides which, names it on the knowledge page, and
pre-registers the first-year/AQ ratio it expects. It is noise around 1, not 0.915. No world code
moved in this item.
