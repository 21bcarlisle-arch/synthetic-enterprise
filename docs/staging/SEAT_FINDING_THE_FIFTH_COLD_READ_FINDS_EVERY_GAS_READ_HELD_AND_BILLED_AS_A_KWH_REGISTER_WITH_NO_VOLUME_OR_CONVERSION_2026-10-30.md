**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The fifth cold read finds every gas read held and billed as a kWh register, with no volume and no conversion (2026-10-30)

**Source.** The fifth cold read's O7 and Q2, on the 3dc5a92948 book
(`docs/staging/records/SEAT_READING_THE_FIFTH_COLD_READ_ON_THE_3DC5A92948_BOOK_2026-10-30.md`, class N11).
It is BLOCKING because it is one of the read's two new classes.

**What the page prints.** OCC-2f64fad94fe7, a gas-only smart account, prints:
- "1104.4 kWh × 5.038p/kWh (gas) = £55.64";
- a meter-read table of "Opening read 7,503.2", "Closing read 8,607.6", "Difference charged 1,104.4 kWh".

A GB gas meter registers volume, in cubic metres, or in hundreds of cubic feet on an imperial meter.
The kWh billed is derived from the volume advance, the calorific value and the volume correction
factor. The page holds the register itself in kWh. It shows no volume, no CV and no correction factor.

The same page's carbon note says gas is "kWh read from its own gas meter, converted at gross calorific
value". So the page asserts a conversion that its reads show did not happen.

**How wide.** On the rebuilt 3dc5a92948 pages, 586 pages carry gas bills: 23,816 gas invoices. Every
one has a kWh register read, and none carries a volume field.

**Confirmed in the code.** The roster carries `cv_factor = 39.5` and `cf = 1.02264` (`saas/customers.py`,
and `simulation/live_population.GAS_CV_FACTOR` / `GAS_CORRECTION_FACTOR`, which cite SI 1996/439).
Nothing on the read path or the bill path in `company/`, `saas/` or `tools/` reads them to convert a
volume. The gas register is kWh from end to end.

**Which side it is on.** I cannot yet say. The meter is the world's, so a volume register belongs to
the world's meter, and the conversion at the LDZ's CV belongs to the supplier's billing. The seam
(`company/interfaces/sim_interface.py`) decides which observable crosses. That is a design decision
for the interface steward, not this item.

**Knowledge first (K8).** No page in `docs/market_research/` sets out what a GB gas read and gas bill
must carry. That means the volume unit, the CV and the correction factor, and what the Gas (Calculation
of Thermal Energy) Regulations require on the bill. That page is owed before any build. The commons has
the DESNZ conversion factor artefact (`docs/domain_artefact_library/regulatory/desnz_natural_gas_conversion_factor.json`).
The LDZ daily CV range is a named GAP at `simulation/live_population.py`.

**What closes it.**
1. The K8 knowledge page on the GB gas read and its conversion.
2. The blind row `INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF`, in the reading's blind-row file
   and landed with it. It is `checkable: false` until a gas read carries its volume.
3. A seam decision on whether the world's gas meter reports volume. Then the bill converts at CV and CF,
   and it prints the volume and both factors.

Not done here: the item is the reading.

## Item 1 written: the K8 page (2026-10-30, worker)

`docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`. Read first-hand: SI 1996/439
regs 3-4, SI 1997/937 (reg 3(3) reference conditions, reg 4A's +1 MJ/m³ cap), and Ofgem's 5 Aug 2014
letter. That letter ties gas SLC 22.7 to the Regulations: the billing CV is the period's mean of the daily
charging-area CVs, truncated to 0.1, and "the use of a fixed CV … is not consistent with the
Regulations". So the roster's fixed 39.5 cannot stand in for that CV unless the record says it is a
stand-in (GAP G1, the daily series, not transcribed). The page closes the blind row's GAPs (1) and (4),
answers (3) at 1.02264 from GOV.UK, narrows (2) and (6), and leaves (5), what the bill must print, open.
It writes its prediction before any build. On a shared CV the conversion moves billed gas energy down by
truncation only: about 0.13% on average, and at most 0.26% on any bill.

Still open: item 3, the seam decision (the interface steward's). The page's C1 proposes that the
world's meter registers volume and that volume is what crosses. This finding stays in the root until
item 3 is built.
