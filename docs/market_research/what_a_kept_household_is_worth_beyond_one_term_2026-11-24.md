# What is a kept household worth beyond the term it renews into?

**Knowledge:** what-a-customer-is-worth

**Written 2026-11-24, delivery seat, Lane 0.** K8 page for the BELOW/volume branch's step 2 of
`docs/staging/records/SEAT_PREREG_WHAT_THE_SUPPLIER_DOES_ON_EACH_S12G_OUTCOME_2026-11-23.md`: "value a
kept household at its expected tenure, not at one term". s.12g came out STRADDLE, so step 2 is not
yet triggered. This page and the measurement in §4 are there so it can be acted on the day the
rank-at-q run answers. **No switch is built and nothing is flipped.** Predictions were filed before the
table was computed: `docs/staging/records/SEAT_PREREG_EXPECTED_TERMS_REMAINING_DESK_VS_WORLD_2026-11-24.md`.

## 1. Why the question matters here

The retention guard weighs an offer against `expected_margin + acq_cost_saved`
(`company/interfaces/growth_desk.retention_value_protected`). `expected_margin` is ONE term's
contribution (`simulation/run_phase2b.py`, `term_contribution_per_year`), and the log records
`assumed_deferral_months = 12`. The THE_VALUE_TEST_REDESIGN §12f split put £1.041 of the twin's £0.996
per household-year edge on retention *beyond* one term. So the guard values a save at one term, while
the money that the save makes arrives in later terms.

## 2. What published practice says a retained customer is worth

- **Contribution times survival, carried past the current term.** The standard contractual CLV is
  `sum_t m_t * S(t) / (1+i)^t`. Gupta & Lehmann (2003) give the constant-retention closed form
  `m * r / (1 + i - r)`, which is the "margin multiple". Sources and arithmetic are in
  `clv_discount_rate_and_terminal_value_for_a_gb_supplier.md` §2.
- **The retention curve rises with tenure.** Fader & Hardie (2010) show that a single pooled
  retention rate *undervalues* a heterogeneous book, by 38% in their example. The cause is sorting:
  low-retention customers leave first. A hard horizon cutoff *overvalues* it instead (Gupta &
  Lehmann's 5-year example: +44%). Published practice is a tenure-varying survival curve.
- **GB evidence that tenure lowers the leaving rate.** In Ofgem's Cheaper Market Offers Letter trial
  (2017, control arm), customers 3+ years on the default switched at 0.54 times the rate of those at
  1–3 years (`does_a_disengaged_household_leave_the_default_tariff_less_at_the_same_tenure.md` §1–2).
  The CMA (2016) found about 70% of the Six Large Energy Firms' customers on a standard variable
  tariff, and 56% of respondents had never switched or did not know they could
  (`tariffs_and_the_default_tariff_2026-10-25.md`). A kept GB household is long-lived by the published
  record, and most of that life is **not** spent on a fix.
- **The market prices a whole customer, not a term.** OVO paid about £143 per customer for SSE's
  retail book (2020), and E.ON is reported at about £150 for OVO's (2026). That is roughly a
  four-to-five-year payback on contribution net of overhead, and it reconciles with the
  what-a-customer-is-worth page's arithmetic.
- **The regulation names retention as a lawful purpose and bounds its price.** Under SLC 22B (the ban
  on acquisition-only tariffs, from 14 April 2022), the Market-wide Derogation allows Fixed Retention
  Tariffs "with the aim of retaining the loyalty of those customers"
  (`a_retention_price_that_shares_the_value_an_action_creates.md` §2). Ofgem kept the ban in July 2024,
  citing the "loyalty penalty". So a supplier may spend to keep a household, but the regime is built
  to stop it recovering that spend by over-charging the household later. That matters for M2: value
  beyond one term has to be *created* in later terms, not taken back from the household.

## 3. What a real supplier can observe to estimate it

Everything a tenure estimate needs is on a supplier's own book: each account's acquisition date, its
settled months, and the date it ceased, **whatever the cause**. A renewal departure, a mid-term
switch-away, a move-out and a departure from the default tariff all end a tenure in the same way.
The company already builds exactly this: `company/analytics/customer_value_view._life_table` (a
monthly product-limit life table by tenure year, over every ceased account), consumed by
`company/analytics/clv_three_horizon.expected_remaining_tenure_years` and
`survival_discounted_value_by_year_gbp`. **Step 2 should reuse that, not build an estimator from closed
renewals.** §4 shows why.

## 4. Measured: the desk's renewal-only estimate against realised tenure, 2017–2025

**Inputs.** `/var/tmp/vtn-out/{A,cut,twin}/control_13131_14141.json`: value arm, book 61118, both
seeds, 3,108 closed renewals (`desk_belief_by_arm.value_arm`: account, fuel, term_start, left). No new
run. Script `/var/tmp/kept-hh/table.py` (sha256 `b6a1cfeca409…`).

**Desk (observable, past only).** r = share of the year's closed renewals that stayed, so expected terms
remaining (current one included) = 1/(1−r). `E|H` is the same estimate cut at H whole terms, the terms
left before the window edge (2025-12-31), so that it can be compared with a censored outcome.

**Realised (instrument; uses the future, which no desk has).** For each renewal kept the *next* year,
the years until the household's recorded departure or the window edge. This is a bracket. LOW assumes
it left when the last fix the desk saw ended. HIGH assumes it stayed to the edge. The sidecar does not
date default-tariff exits, so the truth lies in [LOW, HIGH], and nothing on disk says where.

Pooled A + cut + twin (the three runs agree within ±0.3 years on E|H every year):

| year learned | closed | left | r (desk) | E, terms (desk) | H | E\|H (desk) | realised LOW | realised HIGH | E\|H − LOW |
|---|---|---|---|---|---|---|---|---|---|
| 2017 | 684 | 82 | 0.880 | 8.3 | 8 | 5.34 | 2.97 | 7.54 | +2.37 |
| 2018 | 588 | 65 | 0.889 | 9.0 | 7 | 5.06 | 3.27 | 6.50 | +1.80 |
| 2019 | 410 | 21 | 0.949 | 19.5 | 6 | 5.28 | 2.66 | 5.46 | +2.62 |
| 2020 | 421 | 23 | 0.945 | 18.3 | 5 | 4.48 | 2.17 | 4.51 | +2.31 |
| 2021 | 319 | 16 | 0.950 | 19.9 | 4 | 3.71 | — no renewals in 2022 | — | — |
| 2022 | 0 | — | — | — | — | — | the desk learns nothing this year | — | — |
| 2023 | 168 | 0 | 1.000 | ∞ | 2 | 2.00 | 1.18 | 1.50 | +0.82 |
| 2024 | 326 | 15 | 0.954 | 21.7 | 1 | 1.00 | 0.78 | 0.78 | +0.22 |
| 2025 | 180 | 6 | 0.967 | 30.0 | 0 | — | — | — | — |

**The gap, stated.**
1. The desk's renewal-only forecast moves to the **top** of the realised bracket. It is 1.8 to 2.6
   years above LOW in every year 2017–2020. Below HIGH it is 2.20 years (2017), 1.44 (2018), 0.18
   (2019) and 0.03 (2020). By 2019 it forecasts the household staying almost to the window edge,
   which is exactly the HIGH assumption: that the only way to leave is at a priced renewal. A
   renewal-only learner cannot avoid that assumption, because it never sees the other exits.
2. **"Terms remaining" is the wrong unit.** Of 1,296 intervals between one household's successive
   closed renewals, 601 (46%) are longer than a term. The household sat on the default tariff between
   fixes, so a kept household's life is fixes interleaved with default-tariff years, at a different
   margin. "Term margin × terms remaining" would value default-tariff years at the fix's margin, and
   would miss every year it does not count.
3. The untruncated estimate runs from **8 to 30 terms**, and is infinite in 2023, against the ONE
   term the value test prices. The *direction* of §12f's split is supported. Its size cannot be read
   from this record, because the record's own tenure is a bracket (point 1) and its unit is wrong
   (point 2).
4. Sorting is visible to the desk. The departure share is 9.8% at a household's first closed renewal
   (178/1,812) and 4.3% at later ones (56/1,296). This is Fader & Hardie's shape, so a pooled r
   undervalues the long-tenured and overvalues the new.
5. 2022 has no closed renewals: no fixes were priced. A trailing-12-month learner has nothing for 2022
   and must carry 2021's estimate forward, or say it cannot tell.

## 5. GAPs

- **GAP: dated default-tariff exits on the value-test sidecar.** `svt_segment_decisions` is a count
  with no date or outcome, so realised tenure here is only a bracket. The fix is a harness field: the
  date each account ceased, whatever the cause. It is not a box run.
- **GAP: a GB-energy, heterogeneity-aware retention curve.** No published one was found. Fader &
  Hardie's 38% is from a general subscription example (`clv_discount_rate_…` §3).
- **GAP: the margin a kept household earns on the default between fixes.** It is cap-bounded and
  observable in-run, but it has not been measured per tenure year on this book.
- **Not established: which discount rate.** The range is 9.3–12.3% by era (`clv_discount_rate_…` §4).

## 6. What step 2 should be, if rankq says "volume"

Value a save as `survival_discounted_value_by_year_gbp(contribution per year on supply, hazards from
_life_table)`. That counts years on supply and every exit cause, and it is already in `company/`. It
replaces the s.12g record's "term margin × terms remaining from closed renewals", which §4 shows would
overstate tenure and mis-price the default-tariff years. Default off, with the run as the s.12g record
names it. The measure-first count (at least 10 value refusals in A's sidecar) still applies.
