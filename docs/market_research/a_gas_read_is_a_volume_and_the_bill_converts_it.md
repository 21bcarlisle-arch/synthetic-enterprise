**Knowledge:** metering-and-reads

# A gas read is a volume, and the bill converts it to kWh

K8 page for N11 of the fifth cold read,
`docs/staging/done/SEAT_FINDING_THE_FIFTH_COLD_READ_FINDS_EVERY_GAS_READ_HELD_AND_BILLED_AS_A_KWH_REGISTER_WITH_NO_VOLUME_OR_CONVERSION_2026-10-30.md`,
under the correctness ruling
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`).
Written 30 Oct 2026, before any build. The question: **what does a GB domestic gas read register, and
how must a supplier turn it into the kWh it bills?** What the rules require, what is published, what
is not (GAP), and the choices a build should make.

Marks: **[H]** read in the primary document this session; **[S]** a secondary source (government
guidance page or supplier help text), read this session; **[B]** belief, stated with its reason.

## What the book does today

Measured by the fifth cold read on the 3dc5a92948 pages: 586 pages carry gas bills, 23,816 gas
invoices, and every one holds the register in kWh with no volume, no CV and no correction factor.
Confirmed in the code on 30 Oct: `cv_factor = 39.5` and `cf = 1.02264` sit on the roster
(`saas/customers.py`; `simulation/live_population.GAS_CV_FACTOR`, `GAS_CORRECTION_FACTOR`), and no
read or bill path in `company/`, `saas/` or `tools/` reads them. The seam carries no gas volume.

## What the rules and the published record establish

**R1. A gas meter measures volume, and the supplier converts it.** [H] Ofgem, *Calculation of average
calorific value in accordance with the Gas (Calculation of Thermal Energy) Regulations 1996*, open
letter to all domestic gas suppliers, 5 August 2014
(https://www.ofgem.gov.uk/ofgem-publications/89201/supplierguidanceoncvcalculation.pdf):
"Unlike electricity meters, which measure energy units directly, gas meters measure in volume units
… gas suppliers convert the metered volume units to energy units to calculate customers' bills."

**R2. The licence makes the statutory method the billing method.** [H] Gas supply licence SLC 22.7, as
quoted in that letter's Appendix 1: a domestic contract that prices by the amount of gas "must also
provide for the number of kilowatt hours supplied to the premises to be calculated in the same manner
as such number would have been calculated under section 12(1) of the Act if the gas had been conveyed
to the premises by a Gas Transporter." The Act's method is the Gas (Calculation of Thermal Energy)
Regulations 1996, SI 1996/439, as amended by SI 1997/937 and SI 2002/3130 (letter, footnote 2).

**R3. The energy is the converted volume times the period's average CV.** [H] SI 1996/439 reg 3(1)
(https://www.legislation.gov.uk/uksi/1996/439/regulation/3): the energy conveyed is computed from "A
… the number of cubic metres in the converted volume of gas conveyed … during the gas period" and "B
… the average calorific value of gas calculated in accordance with paragraph (2)". The formula itself
is an image on legislation.gov.uk and was not read as text. SI 1997/937, new reg 3(3)(b)
(https://www.legislation.gov.uk/uksi/1997/937/made) [H]: the converted volume is the volume "at a
temperature of 15°C and a pressure of 1013.25 millibars".

**R4. The arithmetic, as government guidance states it.** [S] GOV.UK, *Gas meter readings and bill
calculation* (https://www.gov.uk/gas-meter-readings-and-bill-calculation):
1. closing read minus opening read gives the units used;
2. an imperial meter reads in hundreds of cubic feet, multiplied by 2.83 to give cubic metres
   ("1 cubic foot = 0.0283 cubic metres"); a metric meter skips this;
3. multiply by the calorific value, quoted on the bill, for example "39.5 megajoules per cubic metre";
4. multiply by 1.02264, the prescribed factor that corrects the volume for temperature and pressure;
5. divide by 3.6 to give kWh.

So **kWh = V(m³) × 1.02264 × CV(MJ/m³) ÷ 3.6**. The 3.6 is the unit identity (1 kWh = 3.6 MJ). The
2.83 is the unit identity rounded (1 ft³ = 0.028316846592 m³, so 100 ft³ = 2.8317 m³).

**R5. The CV is the billing period's average of the daily values for the charging area, truncated.**
[H] SI 1996/439 reg 3(2), quoted in the Ofgem letter: the average CV is found "by adding the daily
calorific values … for each gas day in that gas period and dividing the sum by the number of those gas
days but so that any amount of less than 0.1 megajoules per cubic metre shall be ignored." The letter
reads this plainly: "The CV used for consumer billing should be an average of the daily average values
received from National Grid for the billing period", truncated to one decimal place: "Rounding average
CV is not consistent with the Regulations, nor is calculating to more than one decimal place."

**R6. A fixed CV is not compliant.** [H] Same letter: "The use of a fixed CV, which some suppliers
refer to as an 'industry standard', is not consistent with the Regulations." The one exception is
prepayment, which "by necessity [has] a short term fixed CV built into the energy calculation",
reconciled regularly to the CV calculated under the guidance.

**R7. The daily CV is published per charging area and capped.** [H] National Grid (now National Gas
Transmission) determines and publishes the daily average CV for each charging area to one decimal
place (letter; reg 4(4)). The daily CV at a take-off point is the lowest of the determined values
(reg 4(1), as made), and since 1997 a flow-weighted area CV is capped at the lowest input CV plus one
megajoule per cubic metre (SI 1997/937 new reg 4A(1)(b), "adding one megajoule per cubic metre to the
lowest of"). The daily series is published, so it is a thing a real supplier could know.

**R8. The CV range.** [S] GOV.UK (as R4): gas transporters must keep the CV between 38 and 41 MJ/m³.
SI 1996/439 reg 4(3)(b) [H] uses 37 MJ/m³ as a fallback ceiling when the sampling apparatus fails.

**R9. A smart gas meter still registers volume.** [S] Supplier help text and practitioner forums found
on 30 Oct (fuseenergy.com, britishgas.co.uk business help, OVO community): SMETS gas meters record
cubic metres, and the CV is applied at billing because the day's CV is not known at the meter. The
SMETS2 GSME technical specification was not read. This is secondary, and it matches R1, which is
not limited to non-smart meters.

## What is not established (GAP)

- **G1. The 2016-2025 daily CV series per charging area.** *Narrowed 2 Nov 2026.* Gas days 1 Nov
  2021 to 31 Dec 2025 are now in the lake, all 13 areas, every published version
  (`data/lake/national_gas_ldz_cv/`, read by `sim/ldz_calorific_value.py`). The portal returns
  nothing before 1 Nov 2021, so **2016 to Oct 2021 stays open**: whether the earlier series is held
  elsewhere (National Gas on request, Xoserve) was not found. A bill before Nov 2021 cannot apply R5
  from the commons, and must keep saying so.
- **G2. The share of GB domestic gas meters that are imperial.** Not found. It decides how many reads
  carry hundreds of cubic feet. A build should carry the imperial path and leave its share as a GAP,
  not assume zero (K2).
- **G3. What the gas bill must print about the conversion.** GOV.UK says the CV is quoted on the bill
  and the bill explains how the charge was calculated [S]. The gas licence's bill-content condition
  (the mirror of electricity SLC 31H) was not read this session. Printing the volume, the CV and the
  correction factor is the published practice; whether each is a licence duty is open.
- **G4. Where 1.02264 is set in law.** GOV.UK calls it "prescribed" [S]. The statutory text read this
  session states the 15°C / 1013.25 mbar reference conditions but not the figure. The figure follows
  from those conditions applied to a meter assumed at a standard temperature, pressure and altitude.
  Which instrument fixes that assumption for domestic meters was not found.
- **G5. The SMETS2 gas register unit**, from the specification rather than R9's secondary sources.
- **G7. Which published version a bill uses, and what the 38.0 runs are.** A gas day's CV is
  published on the day (about 10:30), the day after (about 10:30), often again at 16:00, and some are
  republished months later. In SC, Nov 2023 to Jan 2024, the 10:30 value is 38.0, the 16:00 value is
  40.1-40.4, and a republication in Apr 2024 sets 38.0 again. SC has 131 final values of exactly 38.0
  and WS 108, against almost none at 38.1-38.8, so 38.0 behaves like a floor or a default rather than
  a measurement. R5 says "the daily calorific values"; which version that is, and what a 38.0 means,
  is not established. What is certain is the epistemic half: a supplier can only use a version
  published by its billing date, so the build reads the series as it stood then.

## What the book's blind row can now take

`INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF` (in `docs/design/DOMAIN_INVARIANTS.yaml`) names six GAPs.
This page closes three and narrows two:
- its GAP (1), on the regulations and which CV applies, is closed by R2, R3 and R5: the period average of daily charging-area values, truncated to 0.1;
- its GAP (3), the standard correction factor, is answered by R4 at 1.02264 [S] (G4 above);
- its GAP (4), the imperial factor, is closed by R4: 2.83 m³ per hundred cubic feet, a unit identity;
- its GAP (2), the CV range, is narrowed to R8's 38-41 MJ/m³ [S];
- its GAP (6), smart meters, is narrowed to R9 [S].

Its GAP (5), on what the bill must print, stays open as G3. The row was written blind, so its own text
is left for whoever next touches it with this page in hand.

## The choices a build should make, and why

**C1. The world's gas meter registers volume, and volume is what crosses the seam.** The meter is the
world's (R1). The world already knows the true energy a home burned, so its meter advance is that
energy converted back at the day's true CV and the correction factor:
V = kWh × 3.6 ÷ (CV_day × 1.02264), summed over the period. The read that crosses
`company/interfaces/sim_interface.py` carries the register in m³ (or hundreds of cubic feet on an
imperial meter) and never the kWh. The seam decision is the interface steward's.

**C2. The supplier converts with what a supplier holds.** Billed kWh = V × 1.02264 × CV_period ÷ 3.6.
CV_period is the mean of the published daily CVs for the supply point's charging area over the billing
period, truncated to one decimal (R5). The charging area follows from the supply point, which the
supplier holds. Until G1 is transcribed, the supplier's CV must be marked on the record as a fixed
stand-in, because R6 says a fixed CV is not compliant. A bill must not look like it applied R5 when it
did not.

**C3. The bill prints the volume, its unit, the CV and the correction factor**, beside the kWh it
derives from them (R4; G3 for whether each is a duty). The carbon note's "converted at gross calorific
value" then describes a conversion the page shows.

**C4. Prepayment keeps a short-term fixed CV and a reconciliation** (R6), and a build should say
which of the two it models.

## Predictions for the build, written before it

With the world and the supplier on the same CV, the round trip V → kWh changes the billed energy only
by R5's truncation. Truncating a period average to 0.1 MJ/m³ lowers it by 0 to 0.1, about 0.05 on
average. At CV ≈ 39.5 that is about **0.13% less billed gas energy on average, and never more than
0.26% on any bill**. A build that moves gas revenue by more than 0.26% in either
direction, before G1 lands, has changed something other than the conversion. Once G1 lands, the
world's daily CV and the supplier's period average differ day by day, but over a period they agree to
within the truncation and the weighting of use by day. A larger move is then a finding about that
weighting, not the conversion.

## What the published series shows about the stand-in (measured 2 Nov 2026)

Pre-registered in `docs/staging/records/SEAT_PREREGISTRATION_HOW_FAR_THE_FIXED_GAS_CV_SITS_FROM_THE_PUBLISHED_PERIOD_AVERAGE_2026-11-02.md`,
over the final versions, 650 LDZ-months (Nov 2021 to Dec 2025), a calendar month standing in for a
billing period:
- **Truncation** lowers the month's CV by 0.118% on average and 0.249% at most. The filed prediction
  (about 0.13%, never above 0.26%) holds.
- **The 39.5 stand-in is right on average and wrong by region.** The mean R5 month CV is 39.48, so
  across GB the stand-in over-bills by 0.07%. By area it does not: NO averages 40.30 (the stand-in
  under-bills about 2%), WS 38.93 (over-bills about 1.5%). The largest single LDZ-month gap is
  1.50 MJ/m3, 3.95% of the bill's gas energy.
- **Areas differ by more than the page assumed.** In a typical month the highest and lowest areas
  differ by 1.56 MJ/m3, and by up to 2.70. The reg 4A cap ties an area to its own lowest input, not
  to the other areas.
- **Read as it stood, the CV moves after the bill.** Read 5 days after month end, 89 of the 650
  LDZ-months (14%) give a different R5 from the final record, by up to 2.2 MJ/m3 (SC, Nov-Dec 2023,
  the G7 runs). A build that bills on the final record would use values no supplier had.

So a bill on the stand-in is off by a few per cent in the areas at either end, in opposite directions,
and roughly cancels across GB. The page's 0.26% ceiling still applies to the round trip once the world
and the supplier share the series. It does not apply to the move from the stand-in to the series.

## When the meter reads less than the estimates already billed (amended 2 Nov 2026)

Raised by both blind readers of the gas build (`docs/staging/done/WORKER_FINDING_BOTH_BLIND_READERS_RAISE_6_ON_34B764A0FD_2026-11-02.md`,
pair 1): the build billed the month as the converted advance less the run's settled use, so a meter
reading below that use gave the month a negative consumption.

**What is established.** An overcharge is refunded in full and never capped; the 12-month cap protects
the customer from late demands, not the supplier from refunds [H] (`back_billing_and_liability.md`
§1). The bill after an estimated run prints the meter's actual read and re-prices the whole usage
since the last actual read, the estimated charges coming back as a credit, either as a reverse and
re-bill or as one catch-up line (§13 there, practitioner-shaped; which form is a GAP).

**The rule a build follows [B].** A register turns forwards, so the use in any period is never below
zero. A meter reading backwards is a meter fault (the K5 class of `unbilled_energy_and_revenue_assurance.md`), not something to bill. When the converted
advance since the last actual read is less than the estimates already billed, the excess is a
**credit on the actual read's bill, against the run**. The month's own consumption is zero, not
negative. The same holds when the meter reads less than settlement put on the run: the meter's
advance is the run's true use.

**C5.** The converted advance sets the true use of the run and the month together. Where it falls
below the run's settled use, the run's true charges are re-priced down to the meter, the month bills
0 kWh (its standing charge stands), and the catch-up credits the difference, uncapped. Where the
month settled 0 kWh but the meter advanced, the month is priced at its rows' tariff rate, as an
estimate over a void stub is, rather than ignoring the meter.

**Is a prepayment meter's charge converted? Yes, at the meter.** R6 [H]: prepayment "by necessity
[has] a short term fixed CV built into the energy calculation", reconciled regularly to the CV
calculated under the guidance. The meter debits credit for kWh it has converted from the volume it
registers at a fixed CV. The book today does neither half of C4: its prepayment branch charges the
settled kWh, and the ledger prints a volume worked backwards from that kWh. That is reader B's #2,
confirmed. It is owed as a build. **G6:** how often that reconciliation happens and how it is settled
with a prepayment customer (a credit to the meter or to the account) was not found in what was read.

## Which charging area a household is in (amended 2 Nov 2026)

R5 averages the daily CVs of the supply point's own charging area, so a bill needs that area before it
can convert. This section is the knowledge step before the world gives each household one.

**What a real supplier holds.** Every supply meter point is registered on the central supply point
register with its LDZ and exit zone; a supplier reads them with the MPRN, not from an address [B, the
practitioner reading: the register is Xoserve's under the UNC, and a supplier's CV feed is per LDZ, so
it must hold the LDZ per supply point; the register's own field list was not read this session].

**What is published.** Xoserve publishes a "Postcode Exit Zone List", "a mapping of GB postcodes to
gas Local Distribution Zones (LDZs)", "created by the Network Operators" [H]: the May 2017 edition,
1,382,476 postcodes, one sheet per distribution network. Ofgem's cap does not map a location to one
LDZ: for gas network costs it takes "a weighted average of the charges for the LDZs overlapping each
electricity distribution region" (default tariff cap decision, Appendix 5, Nov 2018) [H].

**An ONS region is not a charging area (measured 2 Nov 2026).** Joining Xoserve's list to the census
output areas through the ONS Postcode Directory, and weighting by the siting frame's households:

| ONS region | Charging areas (share of households) |
|---|---|
| London | NT 55.0%, SE 34.8%, EA 7.0% |
| South East | SE 43.8%, SO 39.7%, NT 9.1% |
| Yorkshire and The Humber | NE 65.4%, EM 29.0%, NO 1.5% |
| Wales | WS 67.8%, WN 21.8% |
| South West | SW 71.7%, SO 15.0% |
| East | EA 74.3%, NT 13.3% |
| North West | NW 92.4%, NO 4.0% |
| Scotland, North East, East Midlands, West Midlands | one area each above 88% |

The rest of each row is output areas with no postcode on the list. **An output area is close to one
area**: 92.4% of households are in an output area whose matched postcodes are all one LDZ, 0.18% in
a split one. So the world can site the charging area from the household's output area (W2_19),
which it already draws, and the region is never used for it.

**What is not established (GAP).**
- **G8. Output areas with no gas postcode.** 7.4% of households, mostly off the gas grid (Scotland
  17.9%, South West 13.2%, East 11.3%). A gas customer drawn into one is itself a question about the
  draw, and its area stays None rather than a neighbour's.
- **G9. The list's vintage.** May 2017 is the newest edition found; 73.0% of today's live residential
  postcodes match it. LDZ boundaries follow the pipes and rarely move, but whether any did after 2017
  is not established.
- **G10. The five independent networks** (LC, LO, LS, LT, LW: Campbeltown, Oban, Stornoway, Thurso,
  Wick) are on the list but have no series in National Gas's LDZ CV items, so their R5 is open.

**C6. The choices a build makes.** The world gives each gas supply point the LDZ of its output area
(`sim.ldz_calorific_value.ldz_for_output_area`, lake `data/lake/xoserve_postcode_ldz/`). The supply
point's LDZ crosses the seam as an observable, as the MPRN would carry it; the region never stands in
for it. Where the area is None or has no series, the bill converts at the stand-in and says why, as a
bill before Nov 2021 does (G1).

## Sources

- Ofgem, open letter, *Calculation of average calorific value in accordance with the Gas (Calculation
  of Thermal Energy) Regulations 1996*, 5 Aug 2014,
  https://www.ofgem.gov.uk/ofgem-publications/89201/supplierguidanceoncvcalculation.pdf [H]
- The Gas (Calculation of Thermal Energy) Regulations 1996, SI 1996/439, regs 3 and 4 as made,
  https://www.legislation.gov.uk/uksi/1996/439 [H]
- The Gas (Calculation of Thermal Energy) (Amendment) Regulations 1997, SI 1997/937, new regs 3(3)
  and 4A, https://www.legislation.gov.uk/uksi/1997/937/made [H]
- GOV.UK, *Gas meter readings and bill calculation*,
  https://www.gov.uk/gas-meter-readings-and-bill-calculation [S]
- National Gas Transmission, data portal, "Calorific Value, LDZ(XX)", PUBOB4507-PUBOB4519,
  https://data.nationalgas.com/find-gas-data, retrieved 2 Nov 2026 [H for the published values]
- Xoserve, *Postcode Exit Zone List*, May 2017,
  https://www.xoserve.com/media/2008/postcode-exit-zone-list-may-2017.zip, retrieved 2 Nov 2026 [H]
- Ofgem, *Default tariff cap: decision, Appendix 5, policy and network costs*, Nov 2018,
  https://www.ofgem.gov.uk/sites/default/files/docs/2018/11/appendix_5_-_policy_and_network_costs.pdf [H]
- Supplier help pages on the smart meter's m³ register (fuseenergy.com, britishgas.co.uk business
  help), and the OVO community [S]
