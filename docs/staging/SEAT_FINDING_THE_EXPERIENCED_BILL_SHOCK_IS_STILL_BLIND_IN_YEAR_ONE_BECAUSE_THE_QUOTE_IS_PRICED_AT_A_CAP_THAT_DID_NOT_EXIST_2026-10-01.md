**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The experienced bill shock is still blind in year one, because the quote is priced at a cap that did not exist

Claim `measure-the-experienced-bill-shock-on-one-world`. The predictions (landed first as
`57b505ca3`), the tables and the verdicts are in
`records/SEAT_PREREGISTRATION_PB4_THE_EXPERIENCED_BILL_SHOCK_ON_ONE_WORLD_2026-10-01.md`. This is
one default world at `aed6bf966`: 106 decided renewals.

## What the run shows

**The new quantity works where it can be applied.** At later renewals it is defined on 62 of 70
rows; the other 8 are prepayment, out of scope by definition. It fires on 32% of them. Its
correlation with bill size within the year is +0.029, inside the published −0.07 to +0.05. The old
month count fails that test (−0.27, per the earlier finding). It also stops scoring falls: 16 of
the 66 defined rows fell by more than 15%, and the old `abs()` counted every one of those as a
shock.

**It cannot do the one job it was built for.** The build's stated reason was that the shock "can
fire in a household's FIRST year". On this world it is defined at **4 of 36** first renewals:

| First renewals (36) | n |
|---|---|
| None: no amount was set at sign-up | 27 |
| None: prepayment | 5 |
| Defined | 4 (none shocked) |

The blindness has moved from a 0 to a None. The None is honest, but the hazard would still have
nothing to read at a first renewal for 87% of the in-scope book.

## Why: the opening amount is annualised at the price cap, not at the price the supplier sold at

`company.interfaces.dd_review_outcome.opening_monthly_amount` prices the sign-up DD with
`get_cap_unit_rate_for_date`. That function returns None before January 2019, and 76 of the 106
rows are 2016 sign-ups. This gives two defects, and the second survives once the first is fixed:

1. **Pre-2019: no quote at all.** The repository has no cap for those dates. The sourced pre-cap
   SVT band (`docs/market_research/svt_rates_active_passive_2016_2025.md`) is ±15% at medium
   confidence, the same width as the 15% materiality cut. A shock read against it would be noise,
   so pricing the quote from that band is NOT the remedy.
2. **Post-2019: the quote is set from the wrong price.** A customer who signed a fixed tariff
   below the cap is told a DD worked out at the cap. The quote is then set high, so a first-year
   rise against it is under-read. The run cannot measure this: 0 of the 4 post-2019 first
   renewals were shocked, which is consistent with it and too few to show it.

**Practitioner side, stated rather than sourced:** a supplier sets the opening DD from the
estimated consumption at the tariff the customer actually signed. Nobody in the trade would
annualise a fixed deal at the default-tariff cap. The company holds that rate for every account
from the moment it sells it. It is the company's own record, so reading it inside the door crosses
nothing.

## What is next (handed on)

**Annualise the opening DD at the rate the supplier sold at.** The door would take the account's
identity, a registration fact both parties hold. The company-side routine behind it would read its
own struck sign-up rate, and the cap would remain only the SLC ceiling it already is. Then re-run
this pre-registration's `analyse.py` unchanged: P1, P2 and P4 become gradable. **Only after that
does the hazard swap go ahead.** Until then, the hazard keeps reading the old count, as the
continuation already said.

This touches `company/interfaces/` (the seam) and `company/billing/annual_consumption_estimate`,
so it is an interface-steward build. It also moves the company's own DD books, so the DD
mis-setting figures will move with it, and that movement is expected.

## Also seen, not chased

- The world decided **no renewal in 2022** and two in 2023. Fixed tariffs largely left the market
  in 2022, so this may be history-true. But it means no world can show the "2022 first renewals"
  cohort that the continuation expected to be the most shocked.
- The materiality cut is still the inherited 15%. That gap is unchanged by this finding.
