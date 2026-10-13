**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

# The value arms re-taken on the term-cost base: pre-registration, written before any leg ran

*2026-10-13, delivery seat (direction `retake-the-value-arms-on-the-term-cost-base`).*

## Premise, re-measured

- The value arm's base moved to the term's own cost at `04913b693`. The book-level measurement in
  `SEAT_FINDING_THE_VALUE_ARM_PRICES_ITS_MARGIN_OFF_THE_TERMS_OWN_COST_2026-10-13.md` gave a
  RE-TAKE verdict.
- The item was told to wait for the writer-1 question. That has been answered and fixed:
  `434d87587` floors writer 1 at the capital-inclusive term cost, and the arm's base reads the
  same number. `c3bf385b9` measured it. Both are ancestors of `05f9f3347`. So nothing pending would
  make this re-take run twice.
- The published pair is `20261008r`, at `45122d156`: `value_cycle_ab_s1_three_arm_20261008r.json`
  and `value_cycle_ab_s1_noise_floor_20261008r.json`. Both predate `04913b693`. The premise is not
  spent.

## What runs

All legs run in the locked worktree `/var/tmp/se-termcost-arms`, pinned at origin `05f9f3347`. The
SSP cache returns 168,026 records, the same as `r`'s. Each pass peaks at about 11.2 GB, so the legs
run one at a time. They are chained by `/var/tmp/se-termcost-arms.sh`, and no leg runs longer than 5 h:

| leg | command | artefact | expect |
|---|---|---|---|
| 1 | `--level-arm` | `value_cycle_ab_s1_three_arm_20261013t.json` | ~1.5 h |
| 2a | `--noise-floor-seeds 11111,22222 --redraw-mode all` | `..._noise_floor_20261013t_a.json` | ~3.7 h |
| 2b | `--noise-floor-seeds 33333,44444 --redraw-mode all` | `..._noise_floor_20261013t_b.json` | ~3.7 h |
| 3 | `--fold` 2a 2b | `..._noise_floor_20261013t.json` | seconds |

A noise floor refuses a single seed, so the three-seed floor cannot be split by seed. Seed 44444 is
added so the second leg has two seeds. The folded floor therefore has four seeds where `r` had
three. Seeds 11111, 22222 and 33333 can each be compared with themselves in `r`.

## What this cannot attribute

`45122d156` to `05f9f3347` covers more than the base change. It also includes writer 1's
capital-inclusive floor, the hedge booking at the market's quote (`61c122683`), the DD review, the
B8 tier floor, the price-match basis, and the arrears corrections (`23fca0567`, `54dbd5650`). The
page already marks `r` as resting on the pre-correction arrears world. Any `t - r` move is a reading
of current code, not a reading of `04913b693`. That is what this item asks for: arm figures on the
term-cost base. It does not ask how much of the move the base caused. If someone needs that split,
the one-variable run is `05f9f3347` with `04913b693` and `434d87587` reverted, control and value
arms only. It is not run here.

## Predictions (r figures from the artefacts above)

| # | quantity, `t` against `r` | `r` | prediction | confidence |
|---|---|---:|---|---|
| T1 | each arm's settled net moves by more than one `r` floor sd | ctl 235,588 / val 240,832 / lvl 229,488; sd 1,770 | yes, for all three. Too much substrate moved to stay inside the band | 0.70 |
| T2 | sign of T1's control move | | up. Lower arrears means less realised bad debt, and the capital-inclusive writer-1 floor lifts 71% of control renewals by a median of £0.71/MWh | 0.55 |
| T3 | renewals priced by the value arm | 278 | within ±15% (236-320) | 0.60 |
| T4 | `level_gbp_per_mwh`, the value arm's realised median | 61.75 | moves by less than £5/MWh. The arm re-chooses its margin over a base about £2.6 higher, and the median margin should hold roughly still | 0.55 |
| T5 | `value_advantage_gbp` in leg 1 | 5,244 | stays positive | 0.70 |
| T6 | folded floor `selection_gbp` mean | 6,765 (n=3) | positive, and `selection_distinguishable_from_zero` stays true | 0.55 |
| T7 | folded floor `selection_gbp` sd | 1,770 | between 885 and 3,540 (within a factor of 2) | 0.70 |
| T8 | value arm's contracted rate on priced renewals, median shift | | up by about £1-4/MWh against `r`. The base rose by a median of £2.6 (delta = -m, writer 1 mostly discounted) | 0.55 |

T8 needs the per-renewal rates. If the artefact cannot yield them, T8 is graded UNGRADABLE and that
is said here. It is not dropped.

## What done means

1. Both legs are on disk, and T1-T8 are graded in this file beside the predictions.
2. `CURRENT_WORLD_THREE_ARM_PATH` and `CURRENT_WORLD_NOISE_FLOOR_PATH` in
   `tools/generate_value_arms_data.py` move to the `t` pair. `CURRENT_WORLD_CHANGED_SINCE_THE_LAST_READING`
   is rewritten relative to `45122d156`. `site/data/value_arms.json` is regenerated.
3. The page's value-arms controls (`tests/tools/test_generate_value_arms_data.py`) are green on the
   new pair.

## Launch record

The chain was queued at 2026-10-13T14:11Z as `longjob-termcost-arms-chain`
(`/var/tmp/se-termcost-arms.sh`, log `/var/tmp/longjob-termcost-arms-chain.log`). Each leg is its own
`longjob-termcost-arms-{leg1,floor-a,floor-b}` unit with its own liveness record. At queue time leg 1
was waiting for room: `sim-runner` was holding 7.1 GB. Once it starts, the whole chain should end
roughly 9 h later. Nothing has been graded yet. The legs' `--asserted-live-by` names this file at its first path,
`docs/staging/` root, before the rooms gate moved it here.

## Leg 1 graded (2026-10-13 ~20:20Z, executor seat, `grade-the-term-cost-arms-retake`)

Leg 1 exited at 2026-10-13T20:05Z (the artefact stamps `generated_at` 19:55Z), as `docs/observability/value_cycle_ab_s1_three_arm_20261013t.json`.
It was produced at `05f9f3347`, on world digest `cdba75ebb9197b33` (the same as `r`), with the same book
across all three arms, and the arms differ only in `name` and `renewal_margin_arm`. The clock audit
passes, and arrears reconcile on all three arms. The grader is `r`-against-`r` placebo-checked: it reads
zero on every leg.

**The launch record's timing was wrong.** Leg 1 ran 5 h 44 min, not ~1.5 h, so the claim that no
leg runs longer than 5 h is refuted. The cause is the next paragraph.

**The book is 2.8 times larger, and this file did not name why.** `settlement_customer_year_budget`
went from 1,750 to 5,000, the sample rate from 0.4188 to 0.3636, settled billing accounts from 272 to
774, and accounts at the end of the window from 119 to 231. That is `ad0afe7b3`, the director's
founder ruling of 2026-10-08 (80 to 400 founders, budget 1,750 to 5,000). It is one of the 501
commits in `45122d156..05f9f3347`. The "what this cannot attribute" list above missed it, and it is
the largest substrate move in the range. The demand digest also moved (`16c3829e` to `7d6195c5`).
Of `r`'s 272 accounts, 149 are in `t`. So every `t - r` total below is mostly a different book, not a
different price.

| # | prediction | `t` | grade |
|---|---|---|---|
| T1 | every arm moves more than 1 sd (1,770) | control +309,787, value +309,195, level +310,653 (about 175 sd each) | **TRUE, for a reason the file did not give.** The book roughly doubled (`ad0afe7b3`). |
| T2 | control moves up | +309,787 | **TRUE on the total, and the stated mechanism is not what moved it.** On the 149 accounts both runs share (post-hoc, not pre-registered), control net *fell* 18,746 (123,950 to 105,203). Value fell 21,851 and level fell 14,448. |
| T3 | value-arm renewals priced within 236-320 | 623 (615 priced, 8 declined) | **REFUTED.** Book size. |
| T4 | level moves by less than £5/MWh | 61.75 to 57.00 (-4.75) | **TRUE, by 0.25.** |
| T5 | `value_advantage_gbp` stays positive | 5,244 to 4,652. Selection 11,345 to 9,886; level advantage -5,234 | **TRUE.** On the 149 shared accounts (post-hoc), value minus control went from +1,694 to -1,410. |
| T8 | median contracted-rate shift on priced renewals up £1-4/MWh | 77 renewals priced in both runs: median +6.66 (IQR 2.46-12.51), 73 up and 4 down. Median chosen margin unchanged (0.00), so the base moved by a median of +5.93 | **REFUTED on the matched 77.** These are 77 of `r`'s 272, a subset conditioned on surviving into both books, so this cannot be read as the book's shift. The book-level 2.61 from the earlier finding stands as the population figure. |

Other movements. The value arm's belief-vs-outcome AUC rose from 0.645 to 0.700. Against control
outcomes it rose from 0.524 to 0.550. Method-skill concordance went from 0.576 to 0.565. Bound-decided
priced renewals went from 50 of 272 (18%) to 87 of 615 (14%), and endpoint-at-ceiling from 91 to 176.

**What this means for the page.** The `t` pair is the first value-arm reading on the 400-founder
book the director ruled for, as well as on the term-cost base. Moving the page to it changes the
book under every arm figure, so `CURRENT_WORLD_CHANGED_SINCE_THE_LAST_READING` must lead with the
book, not the base. The `r` floor's sd (1,770) was drawn over a 272-account book. T7's band is
therefore in more danger than this file allowed.

**The floor.** The original chain was stopped at 21:05:54 local time, in the 30 s gap after leg 1. The
console delivery seat did this on purpose, so that one sim-runner publish cycle could run. It
re-issued the floors as `/var/tmp/se-termcost-arms-rest.sh`: it waits up to 3 h for that cycle,
then runs floor a, floor b and the fold. The commands and artefacts are the same. At the leg-1 pace
(about 1.9 h per full-window pass on this book), each floor leg is probably 7-8 h, not 3.7 h. T6-T7
and the page move wait for the fold.

## Why value trails control on the shared 149: prediction, written before the split (2026-10-14, worker, `the-value-arms-like-for-like-loss-is-decomposed`)

*This was written before any per-account figure was read. I had read only the artefacts' key
structure, so I know which components they carry. The decomposition is the next section.*

**The fall to explain.** On the 149 accounts both runs settle, value minus control went from +1,694
(`r`) to -1,410 (`t`), a change of -3,104. The full-book floor sd is 1,770, drawn over 272 accounts,
so the fall is about 1.75 sd of a different population.

**What the artefacts can and cannot split.** Per account and per arm, they carry: net; the arrears
lines (`pre_4c_net_gbp` plus the bad-debt and recovery lines); departure date and renewal outcomes;
and, for value and level only, each renewal's chosen margin and offered rate. Control's renewal rate
is not logged. Hedge, acquisition, wholesale and revenue are not split per account: they are only in
the book-level gross-to-net bridge. So hedge and acquisition cannot be split per account. The best
the artefacts allow is that they sit inside `pre_4c_net` alongside renewal margin.

| # | prediction | confidence |
|---|---|---|
| D1 | Most of the -3,104 sits in `pre_4c_net` (margin and retention), not in the arrears lines. The bad-debt component of the change in value minus control is under a third of the fall in absolute size. | 0.65 |
| D2 | Inside `pre_4c_net`, the fall comes from **fewer months retained in the value arm relative to control**: more value-only churners among the 149 in `t` than in `r`. It does not come from a lower margin per retained month. The base rose, so value's offers rose more than control's (T8 matched median +6.66), and more customers left. | 0.55 |
| D3 | The fall is concentrated. The 10 accounts with the largest change carry more than half of it. | 0.60 |
| D4 | The 149 are not representative of either book. In both runs they are older founder-era accounts with more renewals each than the rest of their book. Their value-minus-control per account differs in sign or size from the non-shared remainder of `t`. | 0.70 |

**Attribution (which candidate carries the fall).** These must sum to 1.

| candidate | probability it is the main carrier |
|---|---|
| term-cost base `04913b693` (with `434d87587`): value's offers move up relative to control's, and value loses retention | 0.40 |
| selection or noise on a 149-account subset: the fall is inside what an arm difference wanders over a subset this size | 0.35 |
| the 400-founder book `ad0afe7b3`: capacity, shared-cost or price effects that act on the arms differently | 0.15 |
| the other ~500 commits in the range (arrears corrections, hedge-at-quote, DD review, B8 tier floor, price-match) | 0.10 |

**The decision rule, fixed now.**
- If D1 and D2 hold, and the fall sits in the accounts whose value offers rose most, the base is the
  carrier. Then a one-variable run is pre-registered below: `05f9f3347` with `04913b693` reverted,
  control and value only.
- If the fall is spread thinly across the arrears lines, or it is no larger than the per-account
  scatter of value minus control in `r` itself, no run is warranted, and the reason is stated.
- If the 149's `t` difference has the opposite sign from the rest of `t`'s book, the book is not
  trailing. The subset is.

## The split, read after the prediction landed (2026-10-14, same item)

All figures come from the two artefacts alone. The 149 are the accounts in `net_by_billing_account_gbp`
of both arms in both runs. Each account's net is split by `tools/run_value_cycle_ab.arrears_line_net`'s
own identity. **Margin** is `pre_4c_net` plus the released placeholder. **Bad debt** is write-offs
less recoveries. Both sums reproduce the headline: r +1,694, t -1,410, change -3,105.

**By component (change in value minus control, t against r).**

| component | r | t | change |
|---|---:|---:|---:|
| margin before bad debt | +2,356 | -1,165 | **-3,521** |
| realised bad debt | -661 | -245 | +416 |
| total | +1,694 | -1,410 | -3,105 |

Margin splits by shift-share into bills issued (months served) and margin per bill:

| | r | t | change |
|---|---:|---:|---:|
| value's per-bill premium x control bills | +7,866 (0.86 x 9,146) | +5,830 (0.77 x 7,610) | -2,036 |
| bills value issued fewer x value margin per bill | -5,512 (-364 bills) | -6,995 (-477 bills) | -1,483 |

**Renewal rate.** Control's offered rate is not logged, so a matched rate comparison is not
possible. T8 above has the value arm's side. **Hedge and acquisition** are not carried per account.
They sit inside margin and cannot be split out from these artefacts.

**The split that decides it: paths that held against paths that forked.** An account's path holds if
its bills issued are equal across both arms in both runs.

| subset | accounts | change | margin | bad debt | accounts with change below / above zero |
|---|---:|---:|---:|---:|---|
| path held in all four arm-runs | 83 | **-293** | -304 | +10 | 32 / 7 |
| . of which the value arm priced a renewal | 25 | -153 | | | |
| . of which never priced (control and value should be identical) | 58 | -140 | | | |
| path forked (an arm or a run issued different bills) | 66 | **-2,812** | -3,217 | +406 | 41 / 16 |

The forked accounts are life paths that diverged, not prices. The largest movers have mixed signs:

| account | change | what happened |
|---|---:|---|
| C8 | +2,960 | control's bills went from 111 to 21 |
| SYN-2016-036 | -2,906 | value's bills went from 110 to 80 |
| PROS-2016-0046 | +2,813 | control's bills went from 226 to 26 |
| PROS-2019-0310 | -1,846 | value stayed in r and left in t, with bills going from 138 to 26 |

Ten accounts carry -2,400 of the -3,105, but gross of sign they move several times that.

**Against the scatter.** Per-account change has sd 538 and mean -20.8. The standard error of a
149-account sum is about 6,566, so **the -3,105 is z = -0.47**. The value-minus-control total on the
same 149 has its own standard error of about 6,433 in r and 4,396 in t. The full-book floor sd of
1,770 is the wrong yardstick for a subset: it is a sd across redraws, not across accounts.

**Are the 149 representative?** No. They trail their own book in both runs:

| run | 149 shared: value minus control per account | rest of book |
|---|---:|---:|
| r | +11.4 | +28.9 (123 accounts) |
| t | **-9.5** | **+20.6** (611 accounts, +12,613 in total) |

On control net, bills and value-priced renewals per account, they look like the rest of `t`
(706 against 707, 51.1 against 50.8, 0.69 against 0.74). On the value-minus-control reading they do
not. In `t` the rest of the book has the value arm ahead, and the subset has it behind.

### Grades

| # | grade |
|---|---|
| D1 | **TRUE.** Margin -3,521. Bad debt +416 runs the other way, at 12% of the margin figure. |
| D2 | **REFUTED.** The value arm lost fewer customers than control in both runs (leavers: r 13 against 17, t 15 against 22). The margin fall is split between the per-bill premium (-2,036) and bills (-1,483). Forked paths drive the bills term, not value-only churn. |
| D3 | **TRUE on the letter, wrong in spirit.** The top 10 carry 77% of the net fall, but with mixed signs: what concentrates is path divergence, not a pricing effect. |
| D4 | **TRUE on the claim, and the mechanism given was wrong.** The subset's sign is opposite to the rest of `t`. It is not an older, more-renewed cohort: in `r` it had *fewer* bills than the rest (61.4 against 67.9). |
| attribution | **Selection and noise (0.35) carries it. The base (my 0.40 top pick) does not.** On the 25 held-path priced accounts, where a price change acts without a path change, the arm difference moved -153: about £6 per account. |

### Decision: no one-variable run

By the rule fixed before the split, the fall is no larger than the per-account scatter (z = -0.47),
and the subset's sign is opposite to the rest of its book. So the book is not trailing on the
director's 400-founder book: the 149-account subset is. The `04913b693`-reverted run would cost
about 1.9 h per arm, and there is nothing for it to answer. The per-customer arm does nothing worse
at scale here: outside the 149, `t` has the value arm ahead by £20.6 per account.

The thesis reading still waits on what it always waited on: T6 and T7, the four-seed floor fold
from `/var/tmp/se-termcost-arms-rest.sh`, which this item did not touch. That fold measures whether
`selection_gbp` is distinguishable from zero across redraws. A shared-account subset of two
different books cannot.

**A gap, noted and not chased.** The 58 held-path accounts the value arm never priced should read
exactly zero between arms. They read +162 in `r` and +21 in `t`, at most about £48 on one account.
So the arms are coupled through something shared beyond the renewal price. These artefacts cannot
say what (hedge allocation or capital cost are the candidates). It is small against everything
above, and it is the first place to look if a future like-for-like reading needs pennies.
