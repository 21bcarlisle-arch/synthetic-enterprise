**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# The fourth cold read finds the committed tariff price read from one bill, so a zero-use first bill prints "0.00 p/kWh" (2026-10-29)

**Source.** The fourth cold read's O26, on the 209c3350ab book
(`docs/staging/records/SEAT_READING_THE_FOURTH_COLD_READ_ON_THE_209C3350AB_BOOK_2026-10-29.md`, class N9). It is
BLOCKING because it is the read's only new class, and the correctness stretch cannot exit while a page
carries it.

**What the page prints.** OCC-2f64fad94fe7 is a gas-only account on a standard variable tariff. Its
Priced stage carries:
- "Unit rate, all-in before VAT	0.00 p/kWh" under "What the supplier committed to";
- a customer stack of "Energy 0.00p", "Network, policy and levies 0.00p" and "Standing charge,
  spread over use 0.00p", beside "Standing charge is £0.2830/day".

The same page's bills charge about 5p/kWh.

**Confirmed in the code.** `site/explore/index.html` `stagePriced` reads `firstInvoice(d)`, which is
`d.invoices[0]`. Both the committed rate and the stack are computed from that one bill. This account's
first bill is the 22–29 Feb 2024 stub: 0 kWh, `unit_rate_p_per_kwh` null, £2.37 of standing charge.
So the panel prints the tariff's price as zero. On a non-zero stub, the "spread over use" figure is
also sized by that stub's use.

**How wide.** On the rebuilt 209c3350ab pages, 44 of 1,293 pages have a first bill with zero use or
no unit rate. That is 25 of the picker's 752 households. All 44 print a 0.00p committed rate. All 44
are incoming-occupant (OCC) accounts, whose first bill is the part month from the move-in.

**Why no row caught it.** Every price row grades the bills: the unit rate against the wholesale cost
and the cap. A bill with no rate is skipped, correctly. No row grades the price the page *says* was
committed. That is N1's shape: the record is right and the page prints something else.

**What closes it.**
1. A row written blind from the tariff-information and bill-content pages. The text is in the
   reading, and it is landed in `docs/design/DOMAIN_INVARIANTS.yaml` as `INV_COMMITTED_PRICE_IS_THE_TARIFFS_PRICE_PER_FUEL_AT_A_DATE`, `checkable: false` until the page panel is exported.
2. The committed price comes from the tariff record at the date, per fuel, or from the first bill
   that charged energy under it. Never from a bill with no energy on it.
3. A test that reds on origin, using a book whose first bill is a zero-kWh stub.

Not done here: the item is the reading.

## Done (2026-10-29)

- `site/explore/index.html` `stagePriced` reads the committed price from `pricedInvoice(d)`, the first
  bill that charged energy (kWh > 0 with a unit rate), never from a 0 kWh bill. The provenance line
  names that bill and its period, and says when the first bill charged no energy and why it was skipped.
  A page with no such bill prints no unit rate and says why.
- The standing charge spread over use is no longer a slice of the rate stack. It is a sentence
  beside the stack that names its kWh and days. The all-in rate is energy plus network, policy and
  levies, as the row's leg 3 requires.
- `site/explore/test_the_committed_price_is_the_tariffs_not_one_bills.py` drives the page's own
  `stagePriced()` in node. It covers OCC-2f64fad94fe7's stub-then-bill case and every page of a
  book, graded on the row's legs 1 to 4, with a control showing pass, breach and ungraded are all
  reachable. All three tests are red on origin 58abe075eb's page and green after the fix.
- The row was graded on the rebuilt 209c3350ab pages (`/var/tmp/fourth-read/tree/site/data`):
  **44 of 1,293 breach at origin, which is this finding's count, and 0 of 1,293 after the fix.**
  On the published feed (26 Oct) it was 39 of 1,291, now 0. The row stays `checkable: false` for
  the runner, which reads the raw export, and its gap now names the test that grades it.
- Not done: leg 5 (the cap) is not graded on the panel; it is left to the price rows over the
  bills. The bill used is the first that charged energy, not "the bill whose period contains the
  as-at date". The panel is a first-term view, and a later price change under a variable tariff is
  the bills' story, not this panel's.
