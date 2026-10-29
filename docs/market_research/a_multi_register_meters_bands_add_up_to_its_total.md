# A multi-register meter's band registers add up to its total, under every tariff

**Knowledge:** metering-and-reads

*Written 29 Oct 2026, before the build (K8), for E4 of
`docs/staging/SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_READS_NOBODY_TOOK_2026-10-28.md`:
on 433 ToU invoices of the 37abacdf42 book the band indices did not sum to the total index. The
question is what a time-of-use meter's band registers show against its total, on a ToU bill and
while the household is on a single rate. It extends item 7 of
`a_tou_tariff_needs_the_households_choice_not_its_meter.md` and settles that item's GAP.*

## 1. What the meter specification says

DECC, *Smart Metering Equipment Technical Specifications*, draft v1.58, 28 Nov 2014 (the SMETS2
text; `assets.publishing.service.gov.uk/.../381535/SMIP_E2E_SMETS2.pdf`). The current version is SEC
Schedule 9, not in our commons; the sections below are the electricity meter's (ESME) and their
shape has not been reported as changed. Verbatim:

- **5.5.8.1 Time-of-use Pricing.** "ESME shall be capable of recording Consumption according to
  Time-of-use Bands in one of forty-eight Tariff Registers in the Tariff TOU Register
  Matrix(5.7.5.34). ESME shall be capable of switching between different Tariff Registers once every
  30 minutes. The switching between Time-of-use Bands and thus Tariff Registers shall be based on the
  switching rules defined in the Tariff Switching Table(5.7.4.48)."
- **5.7.4.48 Tariff Switching Table.** "A set of rules for allocating half-hourly Consumption to a
  Tariff Register for Time-of-use Pricing and Time-of-use with Block Pricing."
- **5.5.9.1 Active Energy Imported.** "ESME shall be capable of recording cumulative Active Energy
  Imported in the Active Import Register(5.7.5.3)." 5.7.5.3: "The register recording the cumulative
  Active Energy Imported."
- **5.5.9.3 Billing data.** On the Billing Calendar the meter takes "a UTC date and time stamped
  copy of: i. the Tariff TOU Register Matrix(5.7.5.34); ii. the Tariff TOU Block Register
  Matrix(5.7.5.35); and iii. the Active Import Register(5.7.5.3)".

So each half-hour's import is recorded twice: once in the Active Import Register (the total), and
once in exactly one Tariff Register, the one the switching table names. Both are cumulative. **Over
any window, the Tariff Registers' advances sum to the total's advance.** The billing snapshot carries
both, so a supplier holds both.

## 2. What a single-rate period does to the band registers

The meter does not stop routing use to a Tariff Register when the tariff is single-rate. The
supplier's switching table sends every half-hour to one register, and that register is the one
billed. Two published supplier and network guides say which:

- Shell Energy, *Reading your business smart meter* (SMETS2 Aclara meter, fetched 29 Oct 2026):
  "The meter reading that's used for your billing is TOU Rate 1 for single-rate tariffs, and both TOU
  Rate 1 and TOU Rate 2 for two-rate tariffs."
- National Grid's meter-reading guide for the Honeywell AS302P lists "Imp R1" for single-rate tariffs
  and "Imp R1" plus "Imp R2" for two-rate (search summary; the page redirected and was not quoted).

So on a single rate the **first band register keeps advancing**, by all of the use, and the others
stand still. When the household returns to ToU, the first band's opening reading is its old reading
plus everything used on the single rate. The band indices still add up to the total.

A legacy two-rate (Economy 7) meter is the other case. Its registers are switched by a clock or
teleswitch, so both keep advancing whatever the tariff, and a single-rate tariff bills their sum. We
never offer ToU on a legacy meter (`company/pricing/tou_desk.offers_tou`), so this book has none.

## 3. An actual read after estimates

An actual read reads every register. If the months before it were estimated, each band's catch-up
is its actual reading less its last estimated reading (`back_billing_and_liability.md` §13, for the
total register). The band catch-ups therefore sum to the total's catch-up.

## 4. What the design takes, and why

- **Bands sum to the total, always.** On every bill, each band register's closing reading is its
  opening plus its printed kWh plus its share of any catch-up, so the band indices sum to the total
  index. Physics (§1) gives the sum. The **absolute** equality also needs both to count from zero at
  commissioning. That is a belief: a meter whose registers were reset or seeded differently would
  differ by a constant. Our meters are minted with the account, so both start at zero.
- **A single-rate period advances the first band register (Peak, register `2`)** by the total's
  advance, unprinted, because a single-rate bill here prints the total register `1` (item 7's
  design). Section 2 settles that the first register keeps advancing. Which band is "Rate 1" is the
  supplier's switching table: **GAP**. No source says whether a supplier makes Peak or Off-peak its
  rate 1. We take the first band in `TOU_BANDS`. The sums do not depend on the choice.
- **The catch-up is shared across the bands in proportion to the bill's own band split.** This is a
  belief. The true split is the bands' actual readings, and the ledger does not hold a per-band true
  index for the estimated months. GAP: the per-band actual reading at the catch-up.
- **What the raw export can grade.** The export carries the total register on single-rate periods and
  the band registers on ToU periods, never both on one period. The checkable form is that the meter's
  import is continuous where the printed register set changes: on one serial, the band readings at the
  start of a ToU stretch sum to the total's closing reading before it, and the total's opening reading
  after a ToU stretch equals the bands' closing sum. Within a stretch, each period's band advances sum
  to its billed kWh plus catch-up (`INV_PERIOD_MATCHES_READS`).

## 5. Limits

- The SMETS2 text is a 2014 draft. Its register rules are the ones a 2016–2025 meter carries, but the
  current Schedule 9 was not read.
- The single-rate billing register comes from one supplier's guide for one meter make, plus one
  network guide reached only through a search summary. It is consistent with §1, which does not
  depend on it.
