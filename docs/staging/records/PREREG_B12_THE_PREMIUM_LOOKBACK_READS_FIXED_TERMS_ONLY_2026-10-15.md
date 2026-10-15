**Severity:** ADVISORY · **Lane:** B_commercial · **Epoch:** unassigned · **Atom:** `B12_writer_one_reads_its_margin_on_the_unit_rate_so_a_renewal_floor_is_its_true_unit_cost`
**Knowledge:** acquisition-and-retention-economics

# Pre-registration: writer 1's premium lookback reads fixed terms only (B12, hypothesis 1)

**Claim:** `b12-the-premise-lookback-reads-the-default-books-margin`
**Written 2026-10-15, before either run below produced an artefact.** It tests hypothesis 1 of
`docs/staging/SEAT_FINDING_THE_UNIT_RATE_MARGIN_STILL_READS_ABOVE_ITS_TARGET_ON_FIXED_TERMS_2026-10-14.md`:
the fixed-term margin reads high because `PORTFOLIO_PREMIUM_LOOKBACK` takes the last 4 completed
terms of any tariff, and about 10 in 11 are default (SVT) terms earning the cap's headroom. The
knowledge page amended first (K8) is `what_a_renewal_decision_is_for_a_gb_domestic_customer.md`,
section "Which book a fixed renewal's realised margin is read against".

## The one variable

`PortfolioMarginBook.term_ended` admits a completed term only if its tariff is in
`FIXED_PREMIUM_BOOK_TARIFF_TYPES = ("fixed",)`. Both fuels, because the book is one rule; the grade is
on electricity. Nothing else moves.

## Runs

Both arms are `tools.save_on_loss_notice_arms run on ... 2025-06-07 --scale 1` through
`/var/tmp/regrade/seeded_arm.py 61109 400 0`, the same inputs as `/var/tmp/w1-basis-out/fix-sv-k1-61109.json`.
That reference ran at 72ab9d113, and origin has since changed the world (L2.4, the stayers fix,
the held-estimate catch-up). So the baseline is re-run at today's origin rather than borrowed.

- **O** — origin `1ca6dfcf5`, unchanged: `/var/tmp/b12-out/origin-sv-k1-61109.json`.
- **L** — O plus the one variable: `/var/tmp/b12-out/lookback-sv-k1-61109.json`.

Population: electricity rows of `account_state` with `tariff_type == "fixed"` and a non-null
`mean_recent_margin_rate`. The target is read as mean + 2 x premium where the premium is unclamped,
as in the 10-14 grade.

## Predictions

- **P0 (the baseline still shows the defect).** On O, the fixed-term median realised margin is
  above **5%**, and the full -5% is taken on more than **30%** of fixed terms (8.5% and 38% at
  72ab9d113). If this fails, origin's world changes moved the reading, and L against O is still the
  test, but the defect is no longer the one the finding measured.
- **P1 (hypothesis 1, the level).** On L, the fixed-term median realised margin is within **2
  points** of the fixed-term median target. The target is about 1.7% at 72ab9d113.
- **P2 (hypothesis 1, the years).** On L, the fixed-term medians for 2019, 2020, 2023 and 2024 are
  each within **4 points** of their year's median target. On O they read +14% to +18%. The band is
  wider than P1's because each year has 10-50 rows.
- **P3 (the discount).** On L, the full -5% is taken on **fewer than a quarter** of fixed terms.
- **P4 (the book, a direction, not a target).** `total_net` on L is **higher** than on O: fewer fixed
  renewals discount into cost.

## What a failure points to

If L's fixed medians stay high in 2019-20 and 2023-24, the years wholesale fell under strikes hedged
before the fall, the remainder is **hypothesis 2** (hedge gains on fixed terms). If L stays high by a
similar margin in every year, including 2017-18 and 2021, it is **hypothesis 3** (a cost missing from
`net_margin`). If L moves to the band but P3 fails, the premium's 4-term noise is the separate effect
the finding names, and the clamp, not the basis, is what puts terms at -5%.
