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

## Run L2: L without the crisis terms (pre-registered 2026-10-15, before L2 launched)

**Claim:** `b12-fixed-only-lookback-without-the-crisis-terms`. Knowledge first: the section "What a
desk does with a fixed book that lost money through a one-off crisis" on
`what_a_renewal_decision_is_for_a_gb_domestic_customer.md`.

**The one variable.** L, plus: `PortfolioMarginBook.term_ended` refuses a term whose settlement days
touch `CRISIS_EXCLUDED_SETTLEMENT_WINDOW = ("2021-10-01", "2022-09-30")`, which is Ofgem cap periods
7-8. `term_ended` gains `first_settled_day`, and the run loop passes the term's earliest
settlement date. Same base `1ca6dfcf5`, same worktree `/var/tmp/b12-lookback`, same seed 61109, same
command. Artefact: `/var/tmp/b12-out/lookback-nocrisis-sv-k1-61109.json`, graded against L by
`/var/tmp/b12-out/grade.py`. The sha256 of the code diff over L's base is in
`/var/tmp/b12-out/L2.diff.sha256`.

L's by-year fixed electricity medians are the base. In 2016-18, 218 of the 341 rows read 2-4 points
under target. In 2023-24 they read -34% to -38%, with 21 rows at the +15% clamp.

- **C0 (the arm can only move what it says).** Every fixed electricity row with `term_start` before
  2021-10-01 has the same `mean_recent_margin_rate` and `portfolio_premium_pct` as in L. No term
  that touches the window is released before the window opens. If this fails, the change leaked
  beyond its variable and nothing below can be attributed.
- **C1 (the pin is crisis carry-over).** The 2023 and 2024 medians each rise by more than **20
  points** from L's -37.7% and -33.9%, and the count at +15% falls from 21 to **5 or fewer**.
- **C2 (and nothing more).** The 2023 and 2024 medians are each within **4 points** of their year's
  median target, which is P2's band.
- **C3 (the second effect is the larger part of P1's miss).** The overall fixed median stays within
  **1 point** of L's -2.39%, so P1 still fails, because 2016-20 carry 303 of the 341 rows and C0
  holds them fixed. The excluded terms cannot explain the pre-crisis under-reading.
- **C4 (the book, a direction, low confidence).** `total_net` is **lower** than L's £269,782,
  because the +15% clamp was charging about 20 fixed renewals more.

**What it decides.** If C0-C2 hold, the crisis exclusion is the right treatment of 2023-24, and B12's
remaining defect is the 2016-19 under-reading. That is the next hypothesis: fixed terms
systematically realise less than `TARGET_MARGIN_GBP_PER_MWH` because a cost the strike does not
price reaches `net_margin`. The code still does not land while P1 fails. If C1 fails, the 2023-24
reading is not crisis carry-over, and the 4-term window (the 10-14 finding's noise) is the
next variable.

## Grade of L2 (2026-10-15, after the arm finished at 13:10Z)

Graded by `/var/tmp/b12-out/grade_l2.py` over `lookback-sv-k1-61109.json` (L) and
`lookback-nocrisis-sv-k1-61109.json` (L2), both on base `1ca6dfcf5` in `/var/tmp/b12-lookback`
(unit Result=success, 3,500 s). The predictions above are unchanged: before this section was appended,
their sha256 on origin was `86be2d72…f6bb0e`, the value filed in `/var/tmp/b12-out/L2.prereg.sha256`
before launch.

| fixed electricity | L | L2 |
|---|---|---|
| rows with a position | 341 | 342 |
| median realised margin / median target | −2.39% / 1.86% | −2.39% / 1.81% |
| full +15% / full −5% taken | 21 / 3 | **0** / 0 |
| 2023 median (n=9) | −37.7% | −12.9% (target 1.6%) |
| 2024 median (n=13/14) | −33.9% | −9.8% (target 1.4%) |
| 2025 median (n=5) | +11.2% | +4.8% (target 0.9%) |
| `total_net` / renewal departures | £269,782 / 62 | £262,887 / 62 |

- **C0: HOLDS.** 0 of 391 pre-window fixed rows differ from L. The check can fail: run O against L,
  it flags 323 of 403.
- **C1: HOLDS.** 2023 rose 24.8 points and 2024 rose 24.1, both over 20. The +15% count fell from 21
  to 0.
- **C2: FAILS.** 2023 sits 14.5 points under its target and 2024 sits 11.2 points under, against a
  band of 4.
- **C3: HOLDS.** The overall median is unchanged to four places, so P1 still fails. The 2016-20 rows
  carry the median, and C0 holds them fixed.
- **C4: HOLDS.** `total_net` is £6,895 lower, with no change in departures.

**What the C2 failure shows, read off the rows rather than predicted.** From November 2021 to
September 2023, every fixed renewal read the same frozen lookback, −12.89% (premium +7.25%). No
fixed term that ended in those 23 months could be admitted, because every one of them touched the
window. The four terms the premium kept reading had ended **before** 2021-10-01, and they had
already lost, on the 2021 rise. L's July 2021 renewals read −8.8% from the same kind of terms. So:

1. **The +15% pin was crisis carry-over (C1).** Taking the window's terms out removes it.
2. **The window, as the regulator's dates draw it, starts after this book's losses began.** Ofgem's
   cap periods 7-8 bound what Ofgem recovered, not when a fixed book bought before the spring
   2021 rise started losing. Widening the window to fit this run would be fitting the window to
   the answer. The published alternative that needs no date is NCCI's: cap or exclude a loss by
   its *size* (a term's realised margin far below what its strike priced for). The company can see
   that on its own P&L, with no calendar in the code.
3. **A date-keyed exclusion freezes the book.** For 23 months the premium priced on four terms
   that were two years old. Any exclusion rule has to say what the premium reads while the
   excluded stretch is passing. The four-term window has no answer to that.
4. **The second effect is untouched and is the larger part of P1's miss.** 2016-19 read 3-6
   points under target (−1.5% to −3.8% against 1.5-1.9%), in years with no crisis in the
   lookback. That is the next hypothesis: a cost reaches a fixed term's `net_margin` that its
   strike's `TARGET_MARGIN_GBP_PER_MWH` does not price.

**Disposition: the code does not land.** L and L2 both fail P1, and the date window is not a rule
the company could hold (point 2). B12's row does not move. The next one-variable runs, in order:
(a) on L, decompose a 2016-19 fixed term's `net_margin` against its priced-for margin, line by line
(a probe on L's artefact, no new arm), to name the cost behind the second effect; (b) only then,
replace the date window with a size-keyed loss cap. Both remain L-based, in `/var/tmp/b12-lookback`.

## Run D: where a 2016-19 fixed term's margin goes, line by line (pre-registered 2026-10-15, before D launched)

**Claim:** `b12-decompose-the-pre-crisis-fixed-term-shortfall`. This is item (a) above. It is a probe, not
an arm: L's code at `1ca6dfcf5` in a new worktree, `/var/tmp/b12-decomp`, plus one write-only line per
term after `term_ended`. The line holds the term's summed settlement lines and the strike's
components off its `term` dict (`company_forward_price`, `locked_policy`, `locked_network`). It is
switched on by `B12_TERM_LINE_LOG`. Same seed (61109) and same command as L. The artefact is
`/var/tmp/b12-out/decomp-sv-k1-61109.json`, plus the line log `/var/tmp/b12-out/decomp-term-lines.jsonl`.

**Population.** The terms writer 1's book admits, by its own predicate: electricity, `fixed`,
unit revenue > 0, neither the term nor its account held on a save, and last settled day in
2016-2019. These are the terms 2016-19 renewals read.

**The identity.** For each term, realised minus priced-for, both over unit revenue U = revenue −
standing charge, splits exactly into:
- **wholesale**: F·V − wholesale cost (the forward the strike used, against what the energy cost),
  split further into the **hedged leg** (F·V_h − Σ hedged kWh × hedge price) and the **spot leg**
  (the rest);
- **policy**: P_locked·V − policy cost (levies locked at term start against those billed by date);
- **network**: N_locked·V − network cost;
- **capital**: K·V − capital cost, where K is the strike's capital rate (`pre_margin_unit_rate` − F
  − P − N);
- **bad debt**: − bad debt (the strike prices none);
- **void/occupier**: − (void owner charge + occupier debt) (also unpriced);
- **rate**: (U/V − pre-margin rate − £2)·V, meaning what the term was actually billed per MWh,
  premium and discount included, beyond what the strike's £2 priced.
Opex is not in `net_margin` (fixed costs go to the ledger only), so it cannot be a line here.

**Controls.**
- **D0 (the probe moves nothing).** D's `total_net` equals L's £269,782.234811 to the penny, and
  every `account_state` row is identical to L's. If this fails, the probe leaked and nothing below
  stands.
- **D1 (the identity closes).** Over the population, the median |residual| of the identity is under
  **0.05 points** of U. If it fails, `net_margin` carries a line not listed here, and that line is
  the finding.
- **D2 (the population is the one L read).** The population's median realised rate is between
  **−4.5% and −1%**, and its median priced-for rate is between **1% and 2.5%**, as L's 2016-19
  renewals read.

**Predictions** (medians over the population, in points of U, signed so that negative means a loss
against what was priced):
- **H1 (bad debt, unpriced).** Between **−3.5 and −1.5**. The world's incidence is 2% of *all*
  revenue in 2016-20, standing charge included, and U is roughly 70-80% of revenue.
- **H2 (policy, locked at the start and billed by date).** Between **−3 and −0.5**. RO+CfD+CM+FiT
  went from £20 to £39/MWh over 2016-19, so a term billed past its first April levy step pays
  more than it locked.
- **H3 (the two together carry it).** Bad debt plus policy is **at least 70%** of the population's
  median shortfall (realised − priced-for).
- **H4 (what the strike prices, and what it does not).** Wholesale + network + capital sum to
  between **−1.5 and +1.5**.
- **H5 (the rate line, low confidence on sign).** Between **−1 and +3**. A fixed-only premium
  that read losses would add to the £2, not take from it.

**What it decides.** If H1-H3 hold, the second effect is not noise and not the lookback. The strike
leaves out two costs the company can see on its own P&L before it prices: its own bad-debt
provision, and a levy schedule already published for the coming obligation year. The remedy is
then in the strike (`price_fixed_tariff`), not in the premium, and each line needs a knowledge-page
section first (K8). If wholesale or capital carries it instead, the forward or the capital rate is
the next variable. The size-keyed loss cap (b) waits on this answer, because a cap fitted over a
book that loses by construction would cap the wrong thing.

## Grade of D (2026-10-15, after the probe finished at 15:25Z)

Graded by `/var/tmp/b12-out/grade_d.py`. Its sha256, `0a66bafa…77ccbc1`, was filed at 14:39:30Z, before
the population existed. One field changed after that: the term dict carries no `term_start`, so
the log wrote `"None"`, and the grader reads `first_day` instead. That date only chooses the
pre-2023 sigma, which is the same for every 2016-19 term. The predictions above are unchanged: their sha256 on
origin (`ffbcf464…a7696d`, in `/var/tmp/b12-out/D.prereg.sha256`) still matches. Unit result:
success.

| over U, median, 254 terms | points |
|---|---|
| realised / priced-for / gap | −2.38 / +1.84 / **−4.18** |
| bad debt (unpriced) | **−2.49** |
| policy (locked at start, billed by date) | **−1.73** |
| wholesale (hedged −0.03, spot −0.34) | −0.03 |
| network / capital / void+occupier | −0.11 / −0.22 / 0.00 |
| rate (billed beyond the strike's £2) | 0.00 |

- **D0: HOLDS.** `total_net` is £269,782.234811 on both D and L, and 0 of 7,566 `account_state` rows
  differ.
- **D1: HOLDS.** The median |residual| is 0.0000. It can fail: drop bad debt from the line list and
  the residual becomes −2.49.
- **D2: HOLDS.** The population reads −2.38% realised against +1.84% priced for: the terms L read.
- **H1: HOLDS** (−2.49). **H2: HOLDS** (−1.73). **H3: HOLDS**: bad debt plus policy is 1.01 of the
  median gap. **H4: HOLDS** (−0.35). **H5: HOLDS** (0.00).

**What the pooled median hides, read off the years rather than predicted.** 2017 is 192 of the 254
terms, and in 2017 bad debt plus policy carries the whole gap (−3.94 of −3.35, with the hedges +0.81).
2018 (n=31) and 2019 (n=22) carry a third effect of the same size. There the **hedged leg** loses 3.0
and 4.1 points: the hedges cost more than the forward the strike priced off. The premium's rate
line pays back +3.3 and +2.2. So the premium was already learning a real loss in those years. It
cannot tell an unpriced cost, which recurs on every term, from a hedge loss, which belongs to a
year.

**Disposition.** The second effect is named: **the strike prices no bad debt, and it locks a levy
that is billed by date.** Both are on the company's own P&L before it prices. Its own provision
rate, and the published RO/FiT/CM schedule for the coming obligation year, are things a real
supplier holds. So B12's remedy is in `price_fixed_tariff`, not in the premium's window. It comes
in two parts, each knowledge page first (K8): a bad-debt allowance per MWh in the strike, from the
company's own provision, and policy priced at the term's settlement-weighted levy rate, from the
published schedules. The 2018-19 hedge-versus-forward gap is a third question for the hedge desk,
not for B12. The size-keyed loss cap, item (b), still follows. Once the strike prices what recurs,
what the premium is left to learn is the year-bound loss, which is the thing a cap is for.
