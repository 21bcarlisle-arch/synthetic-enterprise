**Knowledge:** metering-and-reads

# A gas read is a volume, and the bill converts it to kWh

K8 page for N11 of the fifth cold read,
`docs/staging/SEAT_FINDING_THE_FIFTH_COLD_READ_FINDS_EVERY_GAS_READ_HELD_AND_BILLED_AS_A_KWH_REGISTER_WITH_NO_VOLUME_OR_CONVERSION_2026-10-30.md`,
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

- **G1. The 2016-2025 daily CV series per charging area.** Published by National Gas (data portal),
  not transcribed into the commons. Until it is, any CV a build uses is not the R5 figure. This is
  the GAP already named at `simulation/live_population.py` beside `GAS_CV_FACTOR`.
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
- Supplier help pages on the smart meter's m³ register (fuseenergy.com, britishgas.co.uk business
  help), and the OVO community [S]
