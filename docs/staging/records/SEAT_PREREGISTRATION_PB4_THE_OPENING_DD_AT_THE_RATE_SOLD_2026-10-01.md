**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: the year-one quote annualised at the rate the supplier sold at

Claim `price-the-opening-dd-at-the-rate-the-supplier-sold-at`. Filed 2026-10-01 BEFORE the code is run
on a world. No figure below has been computed. Continues
`SEAT_PREREGISTRATION_PB4_THE_EXPERIENCED_BILL_SHOCK_ON_ONE_WORLD_2026-10-01.md` (its P1, P2 and P4
were ungradable or blind at n = 4 defined first renewals) and acts on
`SEAT_FINDING_THE_EXPERIENCED_BILL_SHOCK_IS_STILL_BLIND_IN_YEAR_ONE_BECAUSE_THE_QUOTE_IS_PRICED_AT_A_CAP_THAT_DID_NOT_EXIST_2026-10-01.md`.

## The change (one variable)

`company.interfaces.dd_review_outcome.opening_monthly_amount` gains an optional
`contracted_unit_rate_gbp_per_mwh_ex_vat`. When given, the opening DD is annualised at that rate
(grossed up by the repo's one domestic VAT rate, so the door stays on the inc-VAT basis the cap
path was already on). When absent, the cap path is unchanged.

`simulation.experienced_bill_shock` passes, per leg, the consumption-weighted unit rate on that
leg's FIRST settled month: the rate printed on the household's first bill, which both parties hold.
Its `run_phase4c_on_phase2b` caller is deliberately NOT changed, so the DD books do not move and
nothing the world decides moves either: the shock does not drive the hazard yet.

## The run

`/var/tmp/se-pb4-shock-out/run.py` with only its worktree path pointed at this worktree; the
previous `events.json` is kept as `events_aed6bf966.json`; `analyse.py` re-run byte-unchanged.

## Predictions

| | Prediction | Why |
|---|---|---|
| Q0 | **Placebo: the later-renewal row is byte-identical** — 70 rows, 62 defined, 20 shocked, 0.323. Total decided renewals 106. | Only the first-renewal reference reads the new input, and the world reads none of it. If this moves, something other than the quote changed and nothing below can be attributed. |
| Q1 | First renewals defined rises from **4 to ≥ 28 of the 31 in scope** (36 less 5 prepayment). | Every in-scope leg has year-one bills, so every one has a sold rate. The residual None, if any, is a leg with no EAC/AQ and no published TDCV at its sign-up date. |
| Q2 | Original P1, unchanged: shocked share among defined first renewals in **[0.10, 0.50]**. | As before. One known drag: the quote is inc-VAT and the met amount is reviewed from `revenue_gbp`, which is ex-VAT, so a rise is under-read by ~5 points. |
| Q3 | Original P2, unchanged: **\|share(first) − share(later)\| < 0.25**. | As before. |
| Q4 | Each of the 4 first renewals defined before has a **rise_fraction at least as high** as it was. | The quote moved from the cap to a sold rate that sits at or below it (the renewal desk ceilings a resi fixed rate at the cap; a default tariff IS the cap). |

## What would refute the plan

If Q0 fails, the run is not one-variable and is discarded. If Q1 holds and the first-renewal share is
≥ 0.6 or ≤ 0.03, then a basis gap is doing the work and not the household's year: the VAT mismatch,
or the 2024 standing charge applied across 2016–2025. The hazard swap then waits on that gap, not on
the quote.

## Result (appended after the run; nothing above is edited)
