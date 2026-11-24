**Severity:** RECORDED · **Lane:** G_data_learning · **Epoch:** unassigned · **Atom:** `unminted`

# The desk's every-exit tenure learner: already built; the per-year table; the grade pre-registered (24 Nov 2026)

Delivery-lane focus `the-desks-tenure-learner-sees-every-exit-it-observes`. It follows
`docs/market_research/what_a_kept_household_is_worth_beyond_one_term_2026-11-24.md` (f66dde740) and
`SEAT_PREREG_EXPECTED_TERMS_REMAINING_DESK_VS_WORLD_2026-11-24.md`, whose E2 could not be graded.

## 1. The build the focus asked for already exists. No second one is written.

The focus asked for a learner in `company/pricing/renewal_desk.py` that estimates expected terms
remaining from every exit a supplier sees, behind a default-OFF flag. I measured this against origin
(639b924a97) before writing anything:

- **No renewal-only learner exists in `company/` to replace.** `renewal_desk.py` has no tenure or
  terms-remaining estimate. The "renewal-only" figure in page §4 is the s.12g record's *proposed*
  formula, computed offline by `/var/tmp/kept-hh/table.py`. The retention guard values a save at ONE
  term (`growth_desk.retention_value_protected`), which is not a learner.
- **The every-exit learner is live.** `company/analytics/customer_value_view.py` builds
  `ceased_billing_accounts(settlement_records)`: an account whose own meters stop settling, *whatever
  the cause*. That covers a loss notice from a fix or from the default, a move-out and a priced-renewal
  departure. `observed_book_exits` → `_life_table` turns it into a monthly product-limit hazard by
  tenure year, and `clv_three_horizon.expected_remaining_tenure_years` /
  `survival_discounted_value_by_year_gbp` value on it. It is published per year as H2. Page §3 and §6
  already say step 2 should reuse it.

Writing a renewal-desk copy would give one quantity two implementations, which is the VAT-rule failure
(CLAUDE.md, the seat's interconnection duty). What step 2 still lacks is a *consumer*: the retention
guard reading H2 instead of one term. That is the s.12g BELOW/volume step 2. It is conditional on rankq,
and its spec is page §6. It is not built here, because a default-off build of a lever whose trigger has
not fired, in `growth_desk.py` while another lane holds that file dirty in the shared tree, is the wrong
increment.

**Correction to the focus text, beside it.** The focus lists "a rollover to the default tariff" as an
exit. It is not one. The household is still on supply, and page §4 point 2's whole finding is that
default-tariff years are *years on supply at a different margin*. The live learner is right not to
count a rollover as an exit. A learner that did count it would rebuild the renewal-only error in reverse
and understate tenure.

## 2. The per-year table, from the files on disk (A + cut + twin value arms, both seeds)

`python3 -I /var/tmp/kept-hh/grade.py` (sha256 `5adbbfdb9e64…`). It was tested on two hand-checked
fixtures, one with dated exits and one without. In the dated fixture, 2018 reads r_all 0.667 where
renewal-only reads 1.000, because one household left from the default and the renewal-only learner did
not see it. All three sidecars were produced at 870201d1e7, before 14c4e3357, so none carries `ceased`.

| year | closed | left | r (renewal-only) | E\|H renewal-only | E\|H every-exit | realised (exact) |
|---|---|---|---|---|---|---|
| 2017 | 684 | 82 | 0.880 | 5.34 | GAP | GAP |
| 2018 | 588 | 65 | 0.889 | 5.06 | GAP | GAP |
| 2019 | 410 | 21 | 0.949 | 5.28 | GAP | GAP |
| 2020 | 421 | 23 | 0.945 | 4.48 | GAP | GAP |
| 2021 | 319 | 16 | 0.950 | 3.71 | GAP | GAP |
| 2022 | 0 | — | GAP: no fixes priced | — | GAP | GAP |
| 2023 | 168 | 0 | 1.000 | 2.00 | GAP | GAP |
| 2024 | 326 | 15 | 0.954 | 1.00 | GAP | GAP |
| 2025 | 180 | 6 | 0.967 | 0.00 | GAP | GAP |

**Every GAP has one cause: the sidecar dates no default-tariff exit.** The renewal-only column
reproduces page §4 exactly. The realised bracket [LOW, HIGH] stays as page §4 printed it. No cell is
filled from `bills_issued` or another proxy.

## 3. Pre-registration: the grade on the first value-test run carrying 14c4e3357

**Which run.** The first `run_value_cycle_ab` sidecar whose `producing_commit` has 14c4e3357 as an
ancestor and whose per-account rows carry `ceased`. rankq (started 06:02, before 14c4e3357 landed at
08:28) is not that run. **No run is launched for this.** The grade rides the next value test.

**What is computed** (grade.py, unchanged from the sha above):
- `r_all(y) = 1 − (accounts whose ceased.date falls in y) / (accounts on supply at 1 Jan y)`.
  An account's observable start is 2016-01-01 if it was on the book at import, else one term before its
  first renewal. Accounts with neither are excluded and counted.
- `E|H_all = Σ_{k<H} r_all^k` with H = 2025 − y, the same truncation as the renewal-only column.
- Realised (instrument): for each renewal kept in y+1, the years to its `ceased.date` or the window
  edge.

**Wall.** The learner column reads only `ceased.date` (a supplier dates its own loss notices and
move-outs) and the desk's own renewals. It never reads `ceased.cause`. Realised uses the future, and it
is an instrument only.

**Predictions** (filed before any dated-exit file exists):
- **P1.** E|H_all < E|H_ren in each of 2017–2021, the five years with at least 30 closed renewals.
- **P2.** For 2017–2020, |E|H_all − realised| < |E|H_ren − realised| in at least 3 of the 4 years, and
  |E|H_all − realised| ≤ 0.75 y in at least 3 of the 4 years.
- **P3.** Realised falls in the lower half of page §4's bracket in at least 3 of 2017–2020, below
  5.26 / 4.89 / 4.06 / 3.34. Weak basis: 46% of the gaps between fixes are default-tariff years, so the
  unseen exits have room to be frequent. That reason is the thesis's own, so this is the prediction
  most likely to flatter it, and a miss counts in full.
- **Validity, not a prediction.** If more than 5% of exits route `registration_loss_unattributed`, the
  grade is reported but marked as resting on unattributed losses. Dates still count; only the routes
  are in doubt.

**Refuted by:** each line read against grade.py's output on that run, with any miss kept here beside
its line. **What a refutation of P2 means:** the geometric trailing-year every-exit form is not good
enough. The company's own `_life_table` (by tenure year, with sorting) becomes the only candidate, and
step 2's spec in page §6 stands as written.

**Reverse:** nothing to reverse. This record changes no code. grade.py lives outside the repository, as
table.py does, and is pinned by its sha.
