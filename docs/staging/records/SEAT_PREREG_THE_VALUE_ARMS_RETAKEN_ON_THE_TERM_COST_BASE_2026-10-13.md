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
