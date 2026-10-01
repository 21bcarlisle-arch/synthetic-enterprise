**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# The 28 accounts "sold above the cap" are ex-VAT strikes ceilinged at the INC-VAT cap

Claim `why-28-accounts-were-sold-above-the-cap-the-opening-door-reads`. This records results
against `docs/staging/records/SEAT_PREREGISTRATION_WHY_28_ACCOUNTS_SIT_ABOVE_THE_CAP_THE_OPENING_DOOR_READS_2026-10-01.md`,
which was filed before the run. It answers the open question in
`SEAT_FINDING_THE_DD_BOOKS_NOW_OPEN_AT_THE_RATE_SOLD_AND_28_ACCOUNTS_WERE_SOLD_ABOVE_THE_CAP_THE_DOOR_READS_2026-10-01.md`.

**The answer is not a payment-method differential, not a regional cap, and not a first month
straddling a cap step.** It is a VAT basis error in the company's renewal desk. Every one of the 28
is accounted for.

## The measurement

One default world at origin/main `7c872f2d0`, run once in `/var/tmp/se-why28`. For each of the 120
accounts the opening door can price, it records:
- the first-month rate from `sold_unit_rate`;
- the company's cap `get_cap_unit_rate_for_date`, and the world's Ofgem and binding caps, for the
  same fuel and date;
- the opening amount at the sold rate, at the cap, and at a zero rate. The zero-rate amount
  isolates the standing-charge share S.

Script: `/var/tmp/se-dd-books-rate-sold/measure28.py`. Rows: `rows28.json` in the same directory.
It reproduces the parent finding: 28 above 1.005, 4 at 1.000, 88 below.

| Group | n | sold rate ÷ inc-VAT cap | What it is |
|---|---|---|---|
| Ratio 1.026–1.040 | **24** | **1.0000 exactly** | A strike clamped to the inc-VAT cap. The door then grosses it up by 1.05 a second time. All 24 ratios equal `(1.05·U + S)/(U + S)` to four decimal places |
| Ratio 1.014–1.019 | **4** | 0.970–0.977 | A strike between the ex-VAT cap (0.952) and the inc-VAT cap, which the inc-VAT ceiling let through |
| Ratio 1.000 | 4 | — | 3 have no first-month rate (cap fallback). 1, PROS-2024-0010g, sits at 0.951, just below the ex-VAT cap. Its ratio of 0.9991 rounds to 1 |
| Below | 88 | < 0.952 | Strikes under the ex-VAT cap: lawful |

No account sits above the inc-VAT cap. Region and payment method do not separate the groups: both
`direct_debit` and `other` appear in each.

## Which writer: one account settles it

There are two candidate writers of an inc-VAT number into the ex-VAT `unit_rate_gbp_per_mwh`.
One is `simulation/svt_product.py`, which writes `svt_rates`' inc-VAT cap into an SVT segment. The
other is the company's renewal chain. **PROS-2023-0014g** (gas, 10 Jan 2023, inside the EPG
window) tells them apart. It was sold at **103.2 £/MWh**. That is the company's
`min(Ofgem, EPG)`. An SVT segment would have written the full Ofgem cap, **170.8**. So the writer
is the company's.

`company/pricing/renewal_rate_chain.py:365` reads `cap_ceiling = get_cap_unit_rate_for_date(...)`.
That accessor's basis is inc-VAT (`company/pricing/ofgem_price_cap.py:33`). It is then used in two
places:
- writer 4 (`:511`) clamps the strike with `unit_rate = min(unit_rate, cap)`;
- the value arm searches under the same figure as `max_offered_rate_gbp_per_mwh` (`:382`).

The strike is ex-VAT, like every rate the world settles (`simulation/price_cap_enforcement.py`
§"WHICH SIDE OF VAT"). **The company's lawful ceiling is therefore 5% too high.** It is the same
defect `hedged_settlement` fixed on 2026-08-25 ("let the world enforce a ceiling 5% above the
law, always in the supplier's favour"). It is still live on the company's side of the wall: one
VAT rule, another implementation.

## What it costs, and who reads it

- **Customers.** 28 of 117 priced first terms in this world, about 24%, are struck above the ex-VAT
  cap. Once VAT is added on the bill, they pay up to 5% over the legal default-tariff ceiling. This
  is an SLC 28AD breach the company cannot see, because its own ceiling check passes.
- **The value arm.** It decides under a ceiling that is too high. The 2026-08-26 A/B found 27 of 66
  renewals ceiling-bound, so their uplift was scored as lawful headroom when it was not.
- **The DD books and the experienced bill shock.** The opening door does exactly what it should with
  what it is given. Fixing the ceiling fixes those 28 openings with no change to the door.

## Not settled here

`svt_product` still writes an inc-VAT rate into a field the settlement reads as ex-VAT. This run did not record
tariff type, so it cannot say whether any first month was an SVT segment. It is either the same defect on
the world's side or a deliberate basis I have not found. **Unmeasured. Read it before you fix
writer 4**, so the two are not changed in one run.

## Pre-registration verdict

H1 named a VAT basis error, and that class **holds**: 28 of 28. It placed the error in
default-tariff first months, and that is **REFUTED**. The writer is the company's fixed-strike
ceiling, as PROS-2023-0014g shows. The strict test (all 28 within 0.995–1.005 of the cap) is also
**REFUTED** by the 4 in-between strikes. The secondary prediction that the 4 at 1.000 are all cap
fallbacks is **3 of 4**: one is a lawful strike that rounds to 1.

Next: the fix is handed on as a continuation. Writer 4 and the arm's search should use the cap
de-VATed at the company's own `VAT_RATE_DOMESTIC`. That needs its own pre-registration, because
it moves every ceiling-bound renewal in the book.
