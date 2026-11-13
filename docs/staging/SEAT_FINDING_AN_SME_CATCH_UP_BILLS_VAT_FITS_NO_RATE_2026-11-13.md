**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# An SME catch-up bill's VAT fits no rate (2026-11-13)

**Found by** the N31 door test (`site/explore/test_a_catch_up_bills_vat_is_the_vat_of_the_lines_above_it.py`)
when it was first run over every account, business accounts included.

## What it is

On `site/data/customers/C5.json`, bill C5-INV113 (September 2016) prints:
- the period's net, £71.47 + £8.72 + £37.04 = £117.23;
- a catch-up of −£45.02 (August 2016);
- VAT of −£20.02;
- a total of £52.19.

The total adds up. The VAT does not fit any rate:
- 20% on the whole net would be £14.44;
- 5% (de minimis, 30.8 kWh/day) on the whole net would be £3.61;
- if the period is at 5% (£5.86), the catch-up carries −£25.88 of VAT. That is 57% of −£45.02.

C5-INV110 (June 2016) fits a mixed rate: 5% on the period (31 kWh/day) and 20% on a Feb–May catch-up.
That may be right. A real bill would then print two VAT lines, one per rate, and this one prints a
single line.

## What would settle it

Read `monthly_bill_assembly._resolve_catchup` for how an SME catch-up's VAT is computed. Check
C5-INV113 against the VAT that was billed on August 2016's estimate. It may be reversing VAT that was
charged on a different base.

**Reverse.** Delete this file.
