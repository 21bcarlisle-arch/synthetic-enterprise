**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The year-one shock tail is a registry EAC that is a fraction of the home's own use

Claim `put-the-year-one-bill-shock-quote-and-review-on-one-basis`. The result is in
`docs/staging/records/SEAT_PREREGISTRATION_PB4_THE_YEAR_ONE_QUOTE_AND_REVIEW_ON_ONE_BASIS_2026-10-01.md`.

## What landed

The year-one quote and the amount it is met by now share one basis. Both are inc-VAT, using the
world's existing `DOMESTIC_VAT_RATE`, so no new VAT rule was written. The quote carries the
standing charge from the leg's first bill instead of 53p. On one world the first-renewal shock went
from 9/31 (0.290) to **17/31 (0.548)**, and the median rise from −0.084 to **+0.222**. Every one of the
31 rises went up. Later renewals moved only by the review's round-up to the pound, and that was
checked exactly on all 62 rows.

## What the corrected basis exposes

**7 of 31 first renewals rise by more than 100%** (+1.04 to +7.15). These are no longer a basis
artefact. They are electrically heated, winter-peaked homes whose registry EAC is 1,600–2,500 kWh,
while their bills imply many times that. For example, PROS-2016-0098 is quoted on 2,470 kWh and
billed £300–600 a month from October to February. Without these 7 rows, year one reads 10/24
(0.417) with a median of +0.107, against later renewals at 0.323 and +0.074.

**Practitioner side, stated and not sourced; the director's check is wanted.** An industry EAC is
computed from the meter's own historic reads. A settled home using ~20 MWh a year would not carry
an EAC of 2,470, unless it is a new connection or its use has just changed (for example, storage
heaters newly fitted). If that is right, the world's registry EAC and its demand disagree for
electrically heated homes. In that case the 7-row tail is a fidelity defect, not a shock a real
supplier would see. I cannot yet say which world mechanism puts demand above the EAC.
`simulation/household_demand.py` takes the declared EAC as the base, and a heating or asset layer
on top of it is the first suspect.

## What follows

1. **Before the hazard swap** (`SEAT_CONTINUATION_SWAP_THE_WORLDS_BILL_SHOCK_BASE_ONTO_THE_EXPERIENCED_SHOCK_2026-10-01.md`),
   establish whether the EAC/demand gap is history-true. If it is not, the swap would carry an
   electric-heating gradient that is a world defect, read as year-one shock.
2. **The DD-book caller** (`run_phase4c_on_phase2b`, now being moved onto the rate sold by
   another lane, `b09864102`) can pass `contracted_standing_charge_per_day_ex_vat` on the same
   footing. Until then the company's DD books still open at the 53p standing charge.
