**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A printed Economy 7 bill shows a 1.5p night rate, because its usage lines carry the energy component only (2026-11-03)

This is the seventh cold read of the storage slot, under ruling step 6. It was found while landing
n12-republish-explore-cast.

## What a reader sees

PROS-2017-0233's bill of 31 Dec 2017 (`site/data/customers/PROS-2017-0233.json`, INV12348) prints these lines on
`/explore/`:

- Usage (Day): 202.3 kWh × 9.31p = £18.84
- Usage (Night): 215.5 kWh × 1.52p = £3.27
- Standing charge: £5.86
- Network & environmental: £22.56
- VAT: £2.53
- Total: £53.06

The bill adds up, but no GB Economy 7 bill has ever shown a 1.52p night rate, and 1.52p is below any 2017 overnight
wholesale price. The tariff's real night rate is 6.92p before VAT, which is 0.47 of the 14.71p day rate, as
`saas/tariff_pricing.E7_NIGHT_TO_DAY_RATIO` states. Every two-rate bill in the book has the same shape. The
smart ToU switch-in home is one: its Peak line reads 28.49p, against 33.99p charged.

## Cause

`saas/bill_generator.tou_registers` (line 96) takes network and policy costs off each register at one rate per kWh,
so a register's `unit_rate_p_per_kwh` is the energy component only. `billUsageLinesHtml`
(`site/explore/index.html:676`) prints that component as the line's rate. Network and policy costs then print
as one separate lump. On a single-rate bill this only splits the rate in two. On a two-rate bill it subtracts a
flat 5.40p from both registers, which leaves a night "rate" that means nothing.

## Fixed already

The cast's bill summaries now quote each register's rate as energy plus network and policy, before VAT
(`tools/generate_explore_cast._bill_extras`, with a test that reds without it). This was landed with
n12-republish-explore-cast.

## Owed

The page's printed bill should print each register at the rate the household pays for it, which is energy plus
network and policy. The separate network line should then go, or be shown inside the rate, so that the lines
still foot.

The component set is pinned in both directions to `BILL_FOOTS`'s `_FOOTING_COMPONENT_KEYS`
(`tests/company/compliance/test_printed_bill_foots_render.py`). The fix is therefore a change to that pairing,
not an edit to one line of the page.

What GB bills printed from 2016 to 2025 is ordinary practitioner knowledge: an all-in unit rate per register, a
standing charge, and VAT, with no separate network line. Confirm this against the Ofgem bill-presentation rules
(SLC 31A) in the commons before building it.

**Done means:** the page's Dec 2017 bill for PROS-2017-0233 prints Night at 6.92p before VAT, or 7.27p including
VAT, consistent with how the page treats VAT. Its lines still foot to £53.06, and a door test reds against the
current page.
