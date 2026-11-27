**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `s2-grade-the-cap-hold-deletion-as-an-arm-on-s1s-seeds`

# S2 graded: deleting the first-term cap hold, as an arm on S1's seeds

*Delivery seat, 27 Nov 2026. This grades the 27 Nov amendment's P1, P2′, P3′ and P4 in
`SEAT_PREREG_THE_FIRST_TERM_CAP_HOLD_DELETED_2026-11-24.md`. The arm is
`/var/tmp/se-s2-caphold/out/run_output_arm.json`. Its producing commit is 23f53c6d7e, which is
76f894811d plus the one line `FIRST_TERM_CAP_HOLD_DELETED = True` and nothing else (`git diff
76f894811d 23f53c6d7e`: one file, one line). It ran the full window, not fast, at the default seed,
with the same world digest (cdba75ebb9197b33). The off arm is S1's book,
`docs/reports/run_output_76f894811d_20261126T155009Z.json`. The P2′ population is the 144 quoted fixed
residential electricity first terms in `/var/tmp/se-s1grade/rows4.json`. The pair read is in
`/var/tmp/se-s2-caphold/grade_pair.out`. Nothing flips on origin.*

## The void rule fired, so the pair is graded and a re-run is still owed

The amendment says that a term-0 difference on any account other than the four, or in the campaign,
is "read first as non-determinism", and that an off arm is re-run before any P is graded.
**49 term-0 rates outside P2′'s population move by at least 1p/MWh** (47 gas, 2 electricity). So the
rule applies. It was not set aside. The re-run is
`longjob-s2-caphold-off-rerun-76f894811d`, at 76f894811d in `/var/tmp/se-s2-caphold/wt-off`, writing
`/var/tmp/se-s2-caphold/out-off/run_output_off.json`.

**Prediction, filed before the re-run's answer:** the re-run reproduces S1's book exactly. That
means its `account_state_log`, `acquisition_funnel_log`, `bills` and `total_net_gbp` are identical.
`/var/tmp/se-s2-caphold/check_rerun.py` reads exactly this. A DIFFERS verdict voids every grade below,
and the arm is then re-graded against the re-run.

The prediction rests on three pieces of evidence, and none of them settles the question:

- The two books are identical on every `account_state_log` row before 2019-02-07. That is the first
  date on which a fixed first term reached the cap (PROS-2019-0024g).
- Neither run called a live risk committee. Both have 0 committee wake-ups and no fast mode.
- Every term-0 move outside P2′ has a mechanism the switch owns:
  - **43 gas first terms** rise by more than 50p/MWh. In the off book, each was billed at the cap
    exactly (SVT − 4.76%). In the arm they are billed up to **2.9× the SVT**: PROS-2021-0399g goes
    from 38.76 to 118.29 £/MWh, and PROS-2022-0327g goes from 98.29 to 207.66. By year: 2019 1,
    2021 19, 2022 6, 2023 3, 2024 2, 2025 12.
  - **2 SYN electricity first terms** (SYN-2021-001 and SYN-2016-064_3) were held at or near the
    cap. They are not campaign-quoted, so they are outside `rows4.json`.
  - **The sub-penny moves.** These include 88 of the 144 quoted legs, at most 0.8p/MWh, and the
    ±1p gas moves in 2023–24. Each one comes with a changed `mean_recent_margin_rate` or
    `portfolio_premium_pct`. That is the portfolio premium reading a margin history that the
    clamped legs changed. It is feedback, not noise.

## The grade (conditional on the re-run's identity)

| # | prediction | measured on the pair | verdict |
|---|---|---|---|
| P1 | Campaign exact, with the same won PROS ids as S1 | The `acquisition_funnel_log` is identical. The won PROS electricity ids are the same set: 231 base ids by this probe's regex, and S1's 242 adds the occupier successors and the other ids its probe counted. Company attempts are 3,194 vs 3,194 and wins 445 vs 445. | **HELD** |
| P2′ | 4 legs (range 0–6), the four named. Each rises by S1's clamp to quote × ≈1.004. The other 140 keep their rate to the penny. 2016–20 and 2022–25 move 0. | **4 legs move by ≥1p/MWh**, exactly the four named: +£3.35, +£2.27, +£7.69 and +£13.73/MWh, each to quote × 1.0040–1.0042. The other 140 move by less than 1p/MWh (88 of them by any amount, at most 0.8p, which is the portfolio-premium feedback above). | **HELD exactly**, on the population it named |
| P3′ | +£0.29 per win (range £0–3), all of it in 2021, and a transfer | **+£0.30 per win** on the four legs (rate move × company EAC, over 242 wins), all in 2021 | **HELD** on its population |
| P4 | MSC-window won switches equal to S1's, and **0** contracted rates moving in the window | Window switches: 43 = 43 by this probe's count (S1 counted 44, with its own counter). **0 electricity** term-0 rates move by ≥1p/MWh in the window. **13 gas** first terms in the window do move, 8 of them by +£14 to +£109/MWh. | Count **HELD**. "0 rates move" **MISSED**: it holds for electricity and fails on gas. |

## What the predictions did not cover: gas

The amendment scoped every P to electricity, because S1 strikes only the electricity first term at
its quote. The original pre-registration's own GAP was: "The campaign quotes electricity only (§7).
Gas first terms are unmeasured." **This arm measures them.** The hold is the only thing keeping
**47 gas first terms** at the cap. A won gas first term is contracted on `quote_renewal`'s strike,
because no quote is ever struck for it (`QUOTED_FIRST_TERM_RATE_KEY` is set on the electricity dict
only, at `simulation/live_population.py:1553`).

Taking the hold off adds **+£39.63 per win** of gas first-term revenue, against +£0.30 from
electricity. Book against book, the arm's net is +£6,293, its revenue +£6,545 and its EV +£12,607.
**That is transfer, not value (M2).** It is a household billed up to 2.9× the default tariff on a
fix it never saw a price for. Filed as
`docs/staging/SEAT_FINDING_A_WON_GAS_FIRST_TERM_IS_CONTRACTED_ON_A_STRIKE_NOBODY_QUOTED_2026-11-27.md`.

## What the order does next (§3–§4 of the order record)

- **More than 6 legs move: 53 at or above 1p/MWh** (4 + 47 + 2). The order record's §4 contingency
  is "#2 gets its own standing book, and S3 moves one step later". **That standing book is not
  scheduled.** The pre-registration's first off-rule binds ahead of it: "The switch is not flipped
  while a won first term is contracted on a strike other than the one quoted." This arm shows 47
  gas first terms still contracted that way. A standing book of #2 would publish a known
  transfer, and it would measure nothing this arm has not already measured.
- **#2 stays off on origin**, and its rule, switch and test stay too. It becomes flippable once a
  won gas first term is struck at a quote (the finding above). Then this arm is re-run on that
  book, with the gas legs predicted.
- **S3 (`SETTLEMENT_LOSSES_APPLIED`) goes ahead against S1 alone.** With #2 held off, the base is
  "S1 plus #2" with #2 = off. S3 stays one-variable against a book already read, which is the
  attributability §3 asked for. The step that confirms the re-run hands S3 off, so S3 is not drawn
  before determinism is shown.

**Reverse:** delete this file and the gas finding. The re-run worktree and its unit write only
under `/var/tmp/se-s2-caphold/`.

**Graded:** P1 HELD · P2′ HELD (4 of 4, exactly) · P3′ HELD (+£0.30/win) · P4 count HELD, "0 rates
move" MISSED on gas (13 in the window) · unpredicted: 47 gas and 2 SYN first terms are held only by
the cap · all of it conditional on `check_rerun.py` reading DETERMINISTIC.
