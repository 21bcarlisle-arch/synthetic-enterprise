**Severity:** LATENT · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used` · **Twin:** `W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape`

# Pre-registration: is the company's gas estimate shape more seasonal than Xoserve's seasonal-normal ALP? (2026-11-19)

Written at 16:40Z, BEFORE any ALP value was read. The question comes from
`SEAT_PREREG_W2_36_D48_THE_SIGNED_RESIDUAL_BY_RUN_KIND_AND_MONTH_2026-11-19.md` P3. Gas runs closed on an
estimated final bill ending Dec–May over-bill by +3.6% [+0.8, +6.3]. Those ending Jun–Nov under-bill by −6.3%
[−10.3, −2.6]. That sign has two possible sources. One is an estimate shape with too much winter weight. The
other is a book whose winters ran milder than normal. Only a comparison against the published seasonal-normal
shape separates them.

**What is compared.**
- The company: `MONTHLY_SHARE_OF_ANNUAL_USE["gas"]` in `company/billing/unread_month_estimate.py`. This is the
  DESNZ ET 4.2 domestic share for 2023–2025 under actual weather. It is the shape every unread gas month is
  spread on.
- The published side: Xoserve's Annual Load Profile for the domestic small-NDM band (EUC band 01, domestic),
  summed to calendar months and normalised to the year.
- Weather held apart: the ALP is demand at seasonal-normal weather. The DAF × WCF term is the weather
  correction, and it is left out.

**Seasonality, defined before differencing.** Two numbers measure it:
- the Dec+Jan+Feb share of the year (DJF);
- the Jun+Jul+Aug share of the year (JJA).

For the company, DJF = 45.69% and JJA = 7.23%.

**Predictions.**
- **Q1 (the D48 candidate).** The ALP's DJF is at least 1.5 points below 45.69%, and its JJA is at least
  1.0 point above 7.23%. Then the proxy is over-seasonal and the bias belongs to the estimator. **I predict Q1
  holds, at about 55% confidence.** The pull against it: the post-2022 demand cuts fell mostly on heating,
  which would flatten the 2023–25 actuals.
- **Q2 (the refutation).** If the ALP's DJF is within ±1.5 points of 45.69%, the proxy is not the cause. P3's
  sign then belongs to the book's weather or to the world. The earlier finding that the world's shape is
  flatter than the company's (1.2 points a winter month) then reads as **world too flat**, which is a W2_30
  fidelity question and not a D48 estimator fix.
- **Q3.** Across LDZs, the ALP's DJF varies by less than 2 points. If it varies by more, a national shape is
  itself the defect, whichever side wins Q1.

Whatever the result, nothing in `company/` changes in the commit that records it.

## Result (appended after the comparison, same day, 16:55Z)

**Source.** Xoserve's approved Derived Factors, from the public `derived-factors.zip` (SHA-256 de7827d8…3e5d,
gas years 2024/25, 2025/26 and 2026/27). Only the ALP was read. The DAF, the weather term, was not used.
The domestic band-1 EUCs were summed by calendar month (`xx:E24/25/26 01BND`, with `01BPD` for prepayment).
The Scottish independent networks were left out, because they copy SC. That leaves 13 LDZs per year.
**What is NOT here, by licence:** the ALP values, or any monthly table derived from them. The licence forbids
republishing them, and this repository is public. The raw zip and the 30-line script are kept outside the
repository. Only the summary statistics below are quoted.

The headline row is the national mean of the 13 LDZs, non-prepayment. The company's proxy is DJF 45.69%,
JJA 7.23%, Jan/Jul 7.32.

| gas year | ALP DJF | LDZ range | ALP JJA | LDZ range | ALP Jan/Jul |
|---|---:|---|---:|---|---:|
| 2024/25 | 44.87% | 43.12–45.95 | 6.84% | 5.96–7.58 | 7.8 |
| 2025/26 | 46.06% | 43.69–47.37 | 6.48% | 5.42–7.31 | 8.5 |
| 2026/27 | 46.90% | 44.53–48.26 | 5.74% | 4.62–6.39 | 9.9 |

The prepayment band (`01BPD`) is about one point flatter in DJF each year (43.97 / 45.22 / 46.17%).

- **Q1 refuted.** I predicted it held, at about 55% confidence. The ALP's DJF is within ±1.5 points of the
  proxy in every year: −0.82, +0.37 and +1.21. Its JJA is *below* the proxy's, by 0.4 to 1.5 points, where I
  predicted at least 1.0 above. On the published seasonal-normal profile, the company's gas shape is not
  over-seasonal. In summer and in Jan/Jul it is, if anything, slightly under-seasonal.
- **Q2 held.** The proxy is not the cause of P3's sign. Read together with
  `SEAT_FINDING_W2_30_THE_GAS_WINTER_OVER_SHARE_IS_THE_WORLDS_70_30_FALLBACK_NOT_THE_PROXY_2026-11-18.md`,
  three independent shapes now agree: the published ALP (Jan/Jul 7.8–9.9), DESNZ actual-weather national demand
  (7.32) and the world's own fabric physics (7.23). The world's population 70/30 fallback disagrees with all
  three, at about 5.0. It settles about three quarters of the gas account-years. So the over-billing of gas
  into winter on estimated runs is mostly the **world being too flat**. It is not the estimator. Weather is not
  ruled out as a contributor: the ALP is seasonal-normal and the book is actual weather. But the year-specific
  part of the true shape was measured at 0.0072 of annual use a month (the D48 finding). The fallback's gap is
  about 0.013. Ten years of actual weather average towards normal, and the fallback does not.
- **Q3 refuted.** DJF spans 2.8 to 3.7 points across LDZs, against a predicted under 2. One national shape is
  coarse in its own right. A per-LDZ shape is what a real supplier settles on, because it knows each meter's
  LDZ and EUC.
- **Spring (not pre-registered, reported as seen).** The ALP's April-plus-May share is 13.8% (2024/25) and
  12.8% (2025/26 and 2026/27). That sits between the proxy's 12.0% and the fabric premises' 15.2% (the W2_30
  finding's April 9.5% plus May 5.7%). This partly supports that finding's residual: the world heats deeper
  into spring than the national series shows. It also says fabric over-does it.
- **Unexplained, and not claimed.** The national ALP becomes more peaked with each gas year: Jan/Jul goes from
  7.8 to 8.5 to 9.9. I cannot yet say why. The candidates are DESC's annual re-fit of the band-1 model and the
  2025 seasonal-normal review, which 2025/26 onwards rests on. Either way, the proxy sits at the flat end of
  the published range, not the peaked end.

**What follows, and what does not.**
- No change to `company/billing/unread_month_estimate.py`. Its shape agrees with the published profile.
- The W2_30 lever is already named: the 70/30 fallback's ~5.3 Jan:Jul calibration in
  `simulation/gas_settlement.py`. The ALP is a third published target against it, and it is seasonal-normal,
  which is the right basis for a world's settled year.
- Per-LDZ shapes in the estimator would be a capability step. It is blocked twice: on the licence, since
  embedding needs Xoserve's written permission, a real-world request and so the director's; and on the
  epistemic seam, since fetched bytes may not become a company runtime input (W6).
- The knowledge page's "not obtainable" claim is corrected beside the claim:
  `docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md` §3.
