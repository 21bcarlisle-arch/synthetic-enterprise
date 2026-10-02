**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `make-acquisition-see-the-price-so-the-first-term-cap-rule-can-go` (Lane 0 delivery)

# The acquisition no-offer rule now prices both fuels, ex-VAT, against the default on the day

Step 1 of "Next, in order" in
`SEAT_FINDING_THE_FIRST_TERM_QUOTE_NEEDS_THE_MARKETS_PRICE_NOT_THE_CAP_AND_THE_CAMPAIGN_NOW_ASKS_IT_BEFORE_THE_WIN_2026-10-02.md`.

## What changed

`saas.growth_mandate.should_attempt_acquisition` is still the one no-offer rule, behind
`growth_desk.decide_acquisition`. It now declines a domestic prospect when the supplier's price
exceeds the published default on the prospect's day.

- **Both fuels.** The old rule returned "proceed" for gas unconditionally. Of the 25 domestic fixed
  first terms struck above the default in the 10-02 flat run, 18 were gas, including
  PROS-2022-0063g.
- **Ex-VAT on both sides.** The default is `renewal_rate_chain.cap_ceiling_ex_vat`, the same reading
  writer 4 clamps with, so this is not a second implementation. The old rule compared the annual
  inc-VAT table with an ex-VAT forward.
- **On the day, net of the EPG.** The annual table and the published windows disagree badly. For
  2023 the table says 265 while the EPG says 323.8 ex-VAT.
- **The quote, when the supplier has one.** `quoted_unit_rate_per_mwh` is new and optional.
  Without it the forward stands in. The forward is a floor on any strike, so that leg can only
  under-refuse. The replacement path passes the departing FIXED term's strike, which is the
  supplier's own price for that commodity on that day. An SVT term's rate is the cap and would
  always pass, so it passes `None` there.
- **Sourced.** "Wholesale costs exceeded the Ofgem price cap ceiling so no viable fixed product could
  be offered" (`docs/market_research/svt_rates_active_passive_2016_2025.md:87`).

## Prediction, filed before any run at this commit

Read off the 10-02 flat run's strikes (`/var/tmp/se-fixed-cap/flat_base.json` + `.log`). Each of
the 42 `[ACQUIRE]` replacement attempts is matched to its departing term's strike and graded
against `cap_ceiling_ex_vat(net_of_epg=True)`:

- **5 of 42 replacement attempts would now be declined** (the old rule declined 0). They are
  2021-06-21 gas, 2021-10-17 electricity, 2024-08-25, 2024-12-16 and 2025-01-08 electricity.
  The 2024-25 ones are only ×1.006–1.04 over the default.
- **None in 2016–2020.**
- **The campaign is unchanged.** `first_term_offer_fn` still has no production caller, so the 25
  first terms above the default are still won and then held at the cap by
  `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`.

Grade it on the next flat run at or after this commit by counting `[GATE] Acquisition suppressed`
lines. The prediction carries a caveat: other lanes' world changes since `db2184ec9` move the
churn set, so this is not a one-variable reading. A count within 3–8, all of them 2021+, holds
it.

## Still owed, in order

1. Wire `first_term_offer_fn` in `live_population._resolve_campaign`. Strike via
   `request_fixed_unit_rate` and decline via `decide_acquisition(quoted_unit_rate_per_mwh=...)`.
   The SSP-cache load must be priced in memory first. The win-side reference (the market's going
   rate, not the cap) is still a research question.
2. Pre-register, delete the hold, and run one variable in one world.
