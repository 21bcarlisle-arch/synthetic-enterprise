**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: why 28 accounts sit 1–4% above the cap the opening door reads

Claim `why-28-accounts-were-sold-above-the-cap-the-opening-door-reads`. Filed before the measurement runs.

**What it explains:** `SEAT_FINDING_THE_DD_BOOKS_NOW_OPEN_AT_THE_RATE_SOLD_AND_28_ACCOUNTS_WERE_SOLD_ABOVE_THE_CAP_THE_DOOR_READS_2026-10-01.md`.
In that finding, 28 of 120 accounts open at a sold/cap monthly ratio of 1.014–1.040.

**What I read before running anything.** `simulation/svt_rates.py` publishes the default-tariff
rate as INC-VAT (its line 10). `simulation/svt_product.py` writes that rate into an SVT segment's
`unit_rate_gbp_per_mwh`. But `sold_unit_rate` reads that field as EX-VAT, and
`opening_monthly_amount` grosses it up by 1.05. `price_cap_enforcement` also says every settled
rate is ex-VAT.

**H1 (predicted): a VAT basis error on default-tariff first months.** The 28 are accounts whose
first settled month is billed at the default-tariff rate.
- Their first-month rate, read as ex-VAT, equals the published inc-VAT cap for that fuel and
  date, within 0.5%.
- Their monthly ratio therefore equals `(1.05·U + S)/(U + S)`, where U is the unit-rate part of
  the cap-arm opening and S is the standing-charge part, within 0.002.

**Refuted if:** any of the 28 has a sold-rate/cap ratio outside 0.995–1.005. That would point to
a regional or payment-method differential, or to a first month straddling a cap step.

**Secondary predictions:**
- The 4 accounts at exactly 1.000 are the cap fallback, with no rate in the first month.
- The 89 below 1 are fixed strikes, and none has a default-tariff first month.

**A side question the measurement also answers.** Does the world SETTLE an SVT segment at the
inc-VAT rate as if it were ex-VAT? If so, SVT households are billed 5% above the legal cap once
VAT is added downstream. That would be a world-side defect, separate from the door.
