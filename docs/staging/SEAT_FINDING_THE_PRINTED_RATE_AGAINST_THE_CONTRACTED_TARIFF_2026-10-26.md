# SEAT FINDING: the printed register rate, checked against the contracted tariff rather than fitted to the bill

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

Why LATENT: this is a measurement of a check that did not exist. Until it ran, nothing published
claimed the bills charge the contracted tariff. e88b13b23's "0 of 52,782 differ" claimed only the
printed arithmetic.

## What the thing is, before measuring it

- **The contracted rate** is the all-in p/kWh the household was sold for the term. It is recorded as
  `account_state_log[].unit_rate_gbp_per_mwh`, one row per term. For a ToU term it is the flat rate
  the pair was struck from. The contracted pair is `saas.tariff_pricing.split_flat_rate_to_tou(flat)`,
  which is the one product rule both `company/pricing/tou_desk.py` and `price_tou_tariff` use. It is
  not recorded on the term row. That is a gap, and it is named below.
- **The printed register rate** is what `tools/generate_billing_ledger._printed_registers` puts on the
  usage line: the band's energy charge *less* its share of the network-and-policy line and the EPG
  receipt (`saas/bill_generator.tou_registers`), fitted to the printed kWh/£ pair. So it is a
  commodity-only rate and is NOT comparable to the contracted rate as printed. The comparable
  quantity is the register's **all-in charge**: its printed amount, plus its kWh share of the
  printed network-and-policy line, plus its kWh share of the printed EPG receipt.
- **The check:** |register kWh × contracted rate − register all-in charge| is within print rounding
  (a penny per rounded money term, plus 0.05 kWh × rate for the register's kWh rounding).
- **Not checkable:** a pass-through or flex term, whose revenue carries the actual policy cost and so
  has no single contracted rate.

## Pre-registration (written 2026-10-26 ~19:10Z, before any measurement)

Measured on the published 4ae8da9b0f book: unrounded bills and the term rows in
`docs/reports/run_output_latest.json.gz`.

- **P1.** On single-register bills in fixed terms, (commodity + non-commodity + EPG) / kWh equals the
  term's rate within 0.1% on ≥99% of bills with kWh > 0.
- **P2.** On two-register bills, each band's all-in rate equals split_flat_rate_to_tou(term rate)
  within 0.1% on ≥99%.
- **P3.** On default-tariff (SVT) bills, I cannot say whether one term row spans a cap change. I
  predict ≥95% match within 0.1%. If it is lower, the term row is not the contracted rate for SVT.
- **P4.** Estimated bills on a ToU term with registers withheld print one register, priced at the
  flat rate (match against the flat term rate, not the pair).

## Result (measured 2026-10-26 on 4ae8da9b0f; ledger regenerated into /tmp, not committed)

**Each bill charges the tariff it was sold at.** Every period that sits inside one term charges its
contracted all-in rate to within print rounding. Fixed, SVT, ToU bands, actual and estimated reads
all hold.

| | periods |
|---|---|
| agree with the contracted rate (one term) | **49,867** |
| cross a price change, inside the covering terms' rates (BOUNDED) | **2,915** |
| disagree | **0** (2 before the label fix below) |
| uncheckable | 0 |
| total, = the ledger's declared `invoice_count` | 52,782 |

**The predictions, graded as written:**

- **P1 held** once the unit of attribution was right. As first measured it read 94%, not ≥99%. Of
  the 1,466 misses, 1,464 were periods crossing a term change that I had priced at the starting
  term's rate. My measurement was wrong, not the bills.
- **P2 held** on the same correction.
- **P3 held.** SVT term rows are per cap window, so each one is the contracted rate.
- **P4 was wrong.** Every withheld-register bill (90) was a period across a price change, not an
  estimate inside one term.

**Two errors of mine, corrected in the record beside the claim:**

- **The tolerance.** I first allowed 0.05 kWh per register. A printed kWh is the difference of two
  cumulative reads, each rounded to 0.1 kWh, so it can sit up to 0.1 kWh from the volume charged.
  At 0.05, 274 exact-rate bills (SYN-2016-383, Jan 2023: unrounded 64.25714p against 64.25714p)
  failed by up to 7p.
- **The straddle bound.** I first bounded straddles on flat rates. A ToU fix's printed single
  register can lawfully sit as low as its off-peak rate. SYN-2016-093 in Feb 2017 charged 10.57p
  against flats of 11.16p and 13.49p, and its off-peak rate was 8.77p. The bound spans every rate
  a covering term carries.

**The one real defect, fixed:** a one-day stub on a ToU term with use in one band only printed its
single register as "Anytime" at the off-peak rate (PROS-2024-0235 2024-08-31, SYN-2016-345
2016-07-31). The printed rate looked like the flat rate charged at 0.786 of itself. The ledger now
prints that band's label (SLC 22A.3: a ToU tariff's rates are displayed separately).

## What stays open (filed here, not fixed)

1. **A bill across a price change prints one blended rate (2,915 periods, 5.5%).** A real supplier
   splits the period at the change and prints a line per rate, with an estimated read at the
   change date. **GAP:** I have not checked which SLC clause, if any, requires the split. Search
   the commons (SLC 31A/31H bill content) before building it. Until then the validator can only
   BOUND these, and says so.
2. **Whether a term was ToU is recorded nowhere.** The term row carries only the flat rate, and
   `demand_response_log` is not in the run output, so the ledger reads ToU-ness from the biller's
   band settlement. The clean fix is a `tou_unit_rates_gbp_per_mwh` field on the
   `account_state_log` row, in `simulation/run_phase2b.py` where `request_tou_offer` strikes the
   pair. It was left out of this landing because B13's uncommitted hunks sit in that file on the
   shared tree.
3. **1,360 VAT claims in `tools/bill_validation_comparison.py` differ by exactly ±1p**, on the
   published ledger before this change. The comparison takes 5% of the sum of the rounded printed
   lines, and the biller takes it of the unrounded subtotal. No one is mischarged. But a customer
   recomputing VAT from their own bill gets a penny off on 2.6% of bills, and which convention a
   real bill uses is a knowledge question, not one to settle by picking.
4. **The contracted rate itself is still ours.** See
   `docs/design/WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md` §1. A mis-struck term agrees with itself.
   The SVT half of that is `the-svt-term-rate-is-checked-against-the-published-cap`.
