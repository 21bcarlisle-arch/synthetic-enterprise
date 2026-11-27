**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `the-won-first-term-is-contracted-at-the-strike-it-was-quoted`

# Pre-registration: a won first term is contracted on the strike it was quoted

*Delivery seat, 2026-11-24, in an `origin/main` worktree at ee7d60bbd5. This record lands before any
book carries the change. The switch is `CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE` in
`simulation/live_population.py`, and it is False in the same commit. The one function is
`renewals.contracted_first_term`. The control is
`tests/simulation/test_a_won_first_term_is_contracted_at_its_quote_by_one_switch.py` (6 tests).
Mutations, each restored byte-identically: the switch defaulting True gives 1 red; ignoring the switch
gives 2 red; never carrying the quote gives 1 red; setting the quote before `_gas_leg_for` copies the
dict gives 1 red; the contract dropping the quote gives 2 red; applying it at every term gives 1 red.
The knowledge is §13 of `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md`
(SLC 23, SLC 22C).*

**Not taken before the post-s.12g book has been read.** B8's five grades read that book, and two
changes in one book cannot be told apart.

## What the build does

- **The campaign keeps what it quoted.** `_quote_recorder` writes each priced strike into
  `outcome["quoted_strikes"]` by prospect id. The offer the funnel reads is returned unchanged, the same
  object. The campaign record and `LAST_CAMPAIGN` do not carry the new key.
- **With the switch taken**, `_won_customer_dicts` puts the quote on the won **electricity** leg
  (`quoted_first_term_unit_rate_gbp_per_mwh`). It does this after `_gas_leg_for` has copied the dict,
  so the gas leg, which was never quoted, does not carry it.
- **`build_renewal_schedule`** contracts the first fixed term on that quote through
  `contracted_first_term`. It keeps the notice-date strike as `notice_date_unit_rate_gbp_per_mwh` and
  marks the term `struck_by: first_term_quote`. With no quote, the term is the same dict as before.

## The per-year table, measured before landing

`/var/tmp/se-ftq-probe/probe.py`, with its output in `probe.out`. The predictions were filed first, in
`PREDICTION.md` beside them. Seed `run_base_seed()`. There are 144 won fixed domestic electricity first
terms and all 144 are quoted. The 151 in the cap-hold record counted prospects. 7 of those homes are
gas-only and so carry no electricity leg, which is also why the switch-off clamps are 13 here, not 15.
The contracted strike is the builder's own first term. It is then put through `decide_renewal_rate` at
`term_index` 0 with an empty portfolio, so no portfolio premium applies. Prices are ex-VAT medians in
£/MWh. The cheapest fix is read on the won day, and the quote day is the same day (lag 0 for all 144).

| year | n | quoted strike | contracted, OFF | contracted, ON | cheapest fix | OFF vs cheapest | ON vs cheapest | hold clamps OFF / ON | first-year £ the hold removes OFF / ON |
|---|---|---|---|---|---|---|---|---|---|
| 2016 | 10 | 112.7 | 100.5 | 112.7 | 92.9 | +7.7% | +21.2% | 0 / 0 | 0 / 0 |
| 2017 | 15 | 119.0 | 114.2 | 119.0 | 113.5 | +0.6% | +9.1% | 0 / 0 | 0 / 0 |
| 2018 | 9 | 152.0 | 136.0 | 152.0 | 108.4 | +25.2% | +37.3% | 0 / 0 | 0 / 0 |
| 2019 | 17 | 141.3 | 120.9 | 141.3 | 124.1 | −0.6% | +14.4% | 0 / 0 | 0 / 0 |
| 2020 | 15 | 134.0 | 112.8 | 134.0 | 118.6 | −4.9% | +13.0% | 0 / 0 | 0 / 0 |
| 2021 | 12 | 175.6 | 195.4 | 175.6 | 198.1 | +28.2% | −4.6% | **8 / 0** | 1,305 / 0 |
| 2022 | 1 | 256.5 | 290.2 | 256.5 | 269.9 | +7.5% | −5.0% | 1 / 0 | 34 / 0 |
| 2023 | 15 | 260.7 | 190.0 | 260.7 | 273.0 | **−31.3%** | −3.5% | 0 / 0 | 0 / 0 |
| 2024 | 36 | 196.7 | 174.0 | 196.7 | 212.6 | **−18.1%** | −6.2% | 0 / 0 | 0 / 0 |
| 2025 | 14 | 209.6 | 225.2 | 209.6 | 221.8 | +1.6% | −5.5% | 4 / 0 | 110 / 0 |
| **all** | **144** | | | **= quote on 144 of 144** | | | | **13 / 0** | **£6.0 / £0.0 per win** |

**First-year billed revenue, ON minus OFF** (after the chain, with the hold on): +£7,466 in all, which
is **+£30.9 per win** over 242 wins. By leg it is +£29–56 in 2016–20, −£23.6 in 2021, −£22.4 in 2022,
**+£183.3 in 2023, +£73.3 in 2024** and −£20.8 in 2025.

With the switch taken, **deleting the hold moves 0 legs**. Once the first term is struck once, the hold
holds nothing.

The filed predictions, graded:
- **Q1** (OFF reproduces the cap-hold record): held for 2023 and 2024 (−31.3% / −18.1%). The clamp
  count is 13, not 15, for the gas-only basis given above.
- **Q2** (ON equals the quote on every quoted leg): held, 144 of 144.
- **Q3** (0–3 clamped ON): held at 0.
- **Q4** (£0–1 per win removed ON): held at £0.0.
- **Q5** (2023 and 2024 within 3 points of −4.5% / −5.1%): held at −3.5% / −6.2%.
- **Q6** (campaign unmoved): holds by construction, since nothing in `_resolve_campaign` reads the
  switch. It is graded on the book as R1.

## Predictions, scored against the first book whose producing commit has the switch taken

These supersede P2 and P3 of `SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24.md`, which that
record voids if the one-strike change lands first. The book also applies the chain's term-0 writers
(portfolio premium, p05/p95 −5% to +15% on the 6af7fd0bfd book, and the default-belief allowance) on
top of the quote. The probe does not, so the ranges carry them.

- **R1. The campaign (exact).** Wins, quotes and per-year rows equal the switch-off book's: 242 wins and
  3,089 quotes at this commit. Any difference refutes "the switch acts after the win".
- **R2. One strike.** Every won fixed domestic electricity first term with a quote is billed on a
  term whose pre-chain unit rate equals the quote: 144 of 144 at this seed. Any quoted leg billed on
  its `notice_date_unit_rate_gbp_per_mwh` refutes it.
- **R3 (replaces P2). Legs the hold touches.** 0 at this seed. The range is 0–6, all in 2021 Q3 –
  2022 and 2025 Q1, where a quote gated just under the default plus a positive portfolio premium can
  cross the cap. If it is above 6, the term-0 writers are re-striking past the quote and are the next
  finding.
- **R4 (replaces P3). First-year margin per win from the hold.** £0.0 at this seed, range £0–£3.
- **R5. First-year billed revenue per win**, ON minus OFF, rises by £30.9, range +£15 to +£50. Most of
  it is in 2023 (+£183 per leg, range +£100 to +£260) and 2024 (+£73 per leg, range +£40 to +£110).
  2021 falls (−£24 per leg, range −£60 to £0).
- **R6. MSC legs.** Won switches between 2022-04-14 and 2024-03-31 are 44, the switch-off count

**Graded 27 Nov on the 76f894811d book** (`SEAT_GRADE_S1_THE_FIRST_TERM_AT_ITS_QUOTE_ON_THE_76F894811D_BOOK_2026-11-27.md`): R1, R2, R5 and R6 held. R4 held in range at £0.29 per win. R3 held in range but missed its point: 4 legs, all in 2021, one of them in June. It was the term-0 default-belief allowance, not the portfolio premium, that lifted those quotes over the cap.
  (R1 implies it).

**How R5 is read (M2).** In 2023–24 the margin R5 adds is the margin the quote decided. The household
was shown that price and chose it, so it is not a transfer the run adds after the decision. Before, the
re-strike gave it away after the decision. In 2016–20 the household now pays the 13–37% over the
cheapest fix that it was shown. Whether that quote was a good decision is the quote's question, not
this change's. The funnel already decided the win against it.

**Off-rule.** If R1 is refuted, the switch is reverted and the campaign's read of it is traced first.

## GAPs

- **The chain's term-0 writers still move a carried quote.** These are the portfolio premium, the
  default-belief allowance and the cap hold. The quote did not include them, so after them the billed
  rate is not exactly the quote. Whether they belong *in* the quote is the next decision, and R3 is
  its tripwire.
- **What the notice-date offer locked is kept.** That is the company forward and the policy and
  network lines, which the save-offer floor reads. They come from the same published schedules but
  from a different forward than the quote's ladder.
- **Gas first terms are not quoted** (§7), so they are struck as before.
- **The half-hourly SSP cache ends 2025-06-07**, so 2025 wins after it are not in this measurement.
