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

## Grade (2026-10-15, after both arms finished at 09:59:34Z)

Graded by `/var/tmp/b12-out/grade.py` over `origin-sv-k1-61109.json` (O) and
`lookback-sv-k1-61109.json` (L), both at `1ca6dfcf5`. The prereg above is unchanged: its sha256 on
origin before this section was appended was
`1141a18baeae5664fcc5a411a434e29d7aef6bf620fe793c230f4650bcae41d4`, the value filed in
`/var/tmp/b12-out/PREREG.sha256` before the arms ran.

| | O | L |
|---|---|---|
| fixed elec terms with a position | 374 | 341 |
| median realised margin | +8.73% | **−2.39%** |
| median target (unclamped rows) | 1.67% (n=229) | 1.86% (n=317) |
| full −5% taken | 144 (38.5%) | 3 (0.9%) |
| full +15% taken | 1 | **21** |
| `total_net` | £265,370 | £269,782 |
| gas fixed median margin / at −5% | +27.2% / 112 | +4.9% / 6 |

- **P0 — HOLDS.** O median 8.73% > 5%, and 38.5% > 30% at −5%. The defect still exists at origin.
- **P1 — FAILS.** L median −2.39% against target 1.86%: 4.25 points apart, outside the 2-point band.
  It fails in the *opposite direction* to O's defect. The margin moved 11.1 points, which overshoots
  the target, rather than stopping short of it.
- **P2 — FAILS on 2023-24, holds on 2019-20.** 2019: −1.49% vs 1.45% (2.9 pts, within 4). 2020: +2.20%
  vs 1.42% (0.8 pts, within 4). 2023: −37.7% (n=9), and no target can be read because every row sits
  at the +15% clamp. 2024: −33.9% (n=13) vs 0.83% (n=1), with 12 of the 13 rows at +15%.
- **P3 — HOLDS.** 0.9% of fixed terms take the full −5%, far below a quarter.
- **P4 — HOLDS.** `total_net` is £4,412 higher on L, with 2 fewer renewal departures (64 → 62).

## What the failure points to

The prereg's three failure branches do not cover this outcome. Hypotheses 2 and 3 both predict L
staying *high*. Instead, L reads *below* target in most years and far below it in 2023-24. What it
does establish is narrower than the prereg's claim:

1. **Hypothesis 1 explains O's high reading.** With the default terms removed, every high year
   (2019-20 and 2023-24 on O, +14% to +18%) loses its excess. The cap's headroom on default terms
   was what lifted the fixed premium's book to those readings, and P0, P3 and P4 agree.
2. **Fixed terms read on their own lose against their own strike.** 2016-19 sit 3-6 points under
   target. 2023-24 read the terms that ended in the 2021-22 crisis (strikes set before the spike)
   at −34% to −38%, so the premium pins at +15% on new fixes. Whether +15% is what a real desk does
   after a loss-making fixed book, or a 4-term lookback over a one-off loss that it should not
   learn from, **I cannot yet say**. The first reading is a fidelity question for the knowledge
   page. The second is the "4-term noise" effect the 10-14 finding names, this time showing on the
   +15% side rather than the −5% side.

**Disposition: the code does not land** (the item requires P1 and P3 both to hold). The change stays
in the locked worktree `/var/tmp/b12-lookback`. The next one-variable run is the same L, with the
premium's lookback excluding terms whose settlement crosses 2021-10..2022-09, or alternatively the
lookback widened beyond 4 terms. It answers whether point 2 is the crisis carry-over alone: if
2016-19 still read 3-6 points under, a second effect remains. Filed for B12; nothing was predicted
after the answer.
