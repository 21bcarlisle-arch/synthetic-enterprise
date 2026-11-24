**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome`

# A won first term is contracted on a strike it was not quoted on

Found by the worker on claim `the-fixed-first-term-leaves-the-cap-hold-pre-registered`, 24 Nov 2026.
The measurement is in `docs/staging/records/SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24.md`.

**What.** The campaign quotes a prospect through `growth_desk.quote_first_term`. That quote is struck
on the ladder, carries the operating-cost line, and is gated at the default. The run then contracts
the won account's first term through `renewals.price_fixed_term` → `quote_renewal`, which is
spot-led at the notice date, with no ladder and no operating-cost line. The two strikes differ, and
the household is billed the second one.

**Measured at real inputs** (seed `run_base_seed()`, origin 37a2b72834, 151 won fixed domestic
electricity first terms):

- **2021.** 10 of 14 contracted strikes sit above the cap, up to ×1.54 of it. Only
  `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` brings them back down.
- **2023–24.** The contracted first term sits a median 31% and 18% under the market's cheapest fix,
  where the quote sat 4.5% and 5.1% under it. That is margin given away by a strike nobody quoted
  (M2).

**Why it matters.** Win and price are decided on one number and billed on another. So the book's
first-year margin does not answer the question the quote asked. The cap hold also cannot be
deleted while this stands (the pre-registration's off-rule).

**Proposed fix (K8 first).** Contract the first term at the strike the company quoted: carry the
quote's rate onto the won account's first term, or strike both through one function. Amend
`cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §7, where "the quote can differ from the
rate the account is later contracted at" is now measured. Then re-run the pre-registration's
probe. P2 and P3 should fall towards 0.
