# WORKER FINDING — the wall exhibit's causal panel pairs every renewal with the previous renewal's rate

**Severity:** LATENT · **Lane:** W2_customer_generator

**Raised:** 2026-08-17, SITE2_two_sided_wall_exhibit HARDEN Expert Hour (re-run cold-eyes walk, three blindfolded personas).
**Owner: the generator / sim lane — NOT `site/customers/**`.** Re-homed rather than fixed, because the defect is in the published DATA and no edit inside SITE2's file_scope can close it.
**Ledger key:** `coldwalk:site2_renewal_effect_lags_its_cause_by_one_period` (`docs/observability/sanity_adjudication_ledger.json`, state `adjudicated-real`).
**Intended rank (P-1):** backlog, unless the second reading below turns out to be the true one — in which case it is a billing-engine defect and belongs at the top.

## What was observed

The exhibit's flagship SIM-only panel ("CAUSE AND EFFECT — WHAT THE SIMULATION KNOWS THIS DROVE") pairs each renewal with a unit-rate step. As published on C7:

| Tariff struck | = p/kWh | Rendered "→ Unit rate stepped … ->" |
|---|---|---|
| 128.0 £/MWh | 12.80 | 12.16 |
| 208.0 £/MWh | 20.80 | 13.89 |
| 334.0 £/MWh | 33.40 | 22.04 |
| 239.0 £/MWh | 23.90 | 33.34 |
| 232.0 £/MWh | 23.20 | 24.31 |

As rendered, 0 of 9 rows agree and the two series move in **opposite directions at 5 of 8 transitions**. Shift the effect column down one row and **8 of 8 reconcile within 6%**, with 334.0 £/MWh → 33.34 p/kWh an exact match to three significant figures. Two personas found the same shift independently, one on C7 and one on C1; it reproduces on C1 (3 of 4 checkable rows: 115→11.15, 146→14.20, 123→12.10) and on C_IC1.

**Observed, not inferred (R9):** the defect is in the data, not the render. `site/data/customers/C1.json` literally pairs `'Tariff renewed at 128.0 £/MWh'` with `'Unit rate stepped 11.31p/kWh -> 11.36p/kWh'`.

## The question this finding cannot answer, and why it matters

There are two readings and the exhibit cannot distinguish them:

1. **A display/join defect in the producer** — the effect row is attached to the wrong renewal. Cosmetic once fixed, but it currently makes the page's flagship causal claim point the wrong way at 5 of 8 transitions.
2. **A billing-engine defect** — the account is genuinely billed at the *previous* renewal's price vintage. If so, this simulated supplier ate the 2022 spike at 2021 prices: C7 billed at 22.04 p/kWh through a term struck at 33.4 p/kWh, ~£200/yr of under-recovery per account. That is precisely the mechanism that killed 29 real UK suppliers in 2021–22, and it would be the most interesting number in the project rather than a render bug.

The VC persona opened her meeting on exactly this, and she is right that it is unanswerable from the surface.

## Suggested first step

Cheapest discriminator, before any repair: take one account's renewal terms and its invoice unit rates from their **producers**, and check whether the rate charged during term *n* is derived from term *n*'s struck price or term *n−1*'s. That single join answers which of the two readings is true and decides the rank.

## Related, same lane, reproduced by the same walk

`coldwalk:site2_consumption_has_no_winter_peak_under_a_seasonality_panel` (already re-homed 2026-08-17, staged as `WORKER_FINDING_TWO_DEFECTS_THE_WALL_EXHIBIT_SURFACED_ARE_NOT_THE_EXHIBITS_2026-08-17.md`) came back **stronger** on the re-run: August beats December on 3 of 3 checkable years, Dec 2021 sits 4.9% *below* Nov, the six-year volume CV is **0.55%**, and lockdown 2020 is invisible in the series. Same owner.
