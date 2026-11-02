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

## The build: C1 to C3 (2026-10-30, seat executor)

Built from `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`.

- **C1.** The world's gas meter keeps a volume index, and an actual read carries it in m3, or in hundreds of cubic
  feet on an imperial meter (`simulation/meter_reads.py`). The interface-steward role reviewed the seam. It found
  no ground truth crossing and the epistemic verifier PASS, and asked for one documentation fix, which was made.
- **C2.** The supplier converts at a CV marked `fixed_stand_in` (`company/billing/gas_volume_conversion.py`,
  `monthly_bill_assembly`).
- **C3.** The ledger, the raw export and the Explore page print the register in its unit, with the CV and the
  correction factor beside the kWh.

The blind row is checkable. It grades 23,745 of 23,745 breached on the cd4fc5b8d8 ledger, and 0 of 19,651 on a
replay of that run's gas legs with the build. On that replay no bill's kWh or money moved. Grade and the
corrected prediction:
`docs/staging/records/SEAT_PREREGISTRATION_A_GAS_READ_IS_A_VOLUME_ON_A_REPLAY_AND_THE_NEXT_FRESH_RUN_2026-10-30.md`.

**Still open, so this file stays:**
- the fresh run that grades the row on a whole book (DIRECTION item 4);
- G1, the daily CV series, which the R5 rule (`period_calorific_value`) waits for;
- G3, whether each printed conversion field is a licence duty;
- C4, prepayment's short-term CV and its reconciliation. It is not modelled: a prepayment statement is converted
  at the same stand-in.
- A deemed read at a price change (`rate_lines`) is still exported in kWh only.

## Done (2026-11-02, seat executor)

The C1 to C3 build is landed from salvage 4391d1800d, applied at origin c4dd0af038 with only the build's paths. On
that base the replay was re-run: the 19,651 replayed gas bills match cd4fc5b8d8 to within 0.0 kWh and £0.0, and the
rescale branch fired on none. `INV_GAS_READ_IS_A_VOLUME_CONVERTED_AT_CV_AND_CF` reads 23,745 of 23,745 breached on
the cd4fc5b8d8 ledger and **0 of 19,651** on the replayed one. The class is closed in code. What stays open is
carried elsewhere, not here:
- the row's grade on a whole fresh book: prediction 4 of
  `docs/staging/records/SEAT_PREREGISTRATION_A_GAS_READ_IS_A_VOLUME_ON_A_REPLAY_AND_THE_NEXT_FRESH_RUN_2026-10-30.md`;
- G1 (the daily CV series), G3 (which printed fields are a licence duty), C4 (the prepayment CV) and the deemed read
  at a price change: the GAPs of `docs/market_research/a_gas_read_is_a_volume_and_the_bill_converts_it.md`, handed
  on by `seat_continuation`.
