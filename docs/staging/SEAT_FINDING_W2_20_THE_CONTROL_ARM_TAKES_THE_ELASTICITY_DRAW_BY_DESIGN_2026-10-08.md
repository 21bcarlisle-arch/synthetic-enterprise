# W2_20: the flat control arm takes the elasticity draw, and that is by design

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_20_mains_gas_is_drawn_not_inferred_from_the_heating_system

**Subject:** owed item 2 of `WORKER_FINDING_W2_20_THE_BASE_SEED_PLACEBO_2026-10-08.md`: why does
the flat control arm read the per-household elasticity draw, and is that intended?

## What the code says

`simulation/customer_events.roll_lifecycle_event` takes the elasticity draw inside
`if differential:`. `differential` is this household's offered renewal rate, inc-VAT, against its
own fuel's SVT. Every arm offers a renewal rate. The control arm's flat rate almost never equals
the SVT exactly, so `differential` is non-zero and the draw fires. The draw is keyed to the
household and the run seed, never to the arm. So all three arms see the same household with the
same sensitivity.

**Intended, on the code's own reasoning.** Sensitivity is a property of the household in the world.
The control arm is "the same book run by a supplier applying flat rules". If flat-rule customers
did not respond to price, the comparison would let the value arm win on a world where only its own
customers react, and that would be a transfer the world itself made, not selection. So the control
arm SHOULD read the draw. That makes it part of the floor's spread, and the floor has to carry
enough seeds to bound it.

`partition_probe` counted the three arms together, so it could not show this. It now writes
`keys.<key>.by_arm` (per arm: calls, accounts, the ids). The arm is the active `policy_scope` name.
Control: `test_the_probe_splits_each_draw_by_the_arm_that_took_it`. Mutation: sending every draw to
one arm makes it go red.

## Pre-registered 2026-10-08 ~05:25Z, before the probe ran

One `--partition-probe --end-year 2017` pass at this worktree's base `0bddb50ed` plus the by-arm
split. The placebo saw 78 elasticity draws per 2017 floor seed.

| # | prediction | confidence |
|---|---|---|
| Q1 | the control arm (`current`) takes > 0 elasticity draws | ~0.9 |
| Q2 | the control arm's drawing accounts equal the value arm's to within 3 | ~0.6 |
| Q3 | the control arm's draw count is within 20% of the value arm's | ~0.6 |

**Window, stated before running.** The probe is 2017-only, not the full window, because
`longjob-w220-recov-arms` is queued behind a pytest run, and the item says not to run beside an
arms run. A 2017 pass takes about 5 minutes. A full-window pass takes about 53 and would overlap.
The 2017 placebo already showed the same control-arm mechanism (GBP 139.43), so 2017 can answer
"does the control arm draw, and from whom". The full-window count is handed on.

## Result (graded 2026-10-08 ~05:40Z)

Unit `longjob-w220-control-arm-probe-2017b`, artefact `docs/observability/value_cycle_ab_s1_floor_partition_probe_2017_by_arm_20261008.json`; the roster comes from the 2017 placebo's three-arm
artefact (33 priced accounts). `selection_gbp_this_pass` is +60.21, the placebo's own figure, so
the probe is pass-through.

| key | control (`current`) | value_arm | level_arm |
|---|---|---|---|
| elasticity: calls / accounts | 26 / 26 | 26 / 26 | 26 / 26 |
| churn_roll: calls / accounts | 26 / 26 | 26 / 26 | 26 / 26 |

- **Q1 PASS.** The control arm takes 26 elasticity draws.
- **Q2 PASS, and more tightly than predicted.** All three arms draw from the same 26 accounts (0
  control-only, 0 value-only). That is every account that reaches a renewal in 2017
  (`roll-but-never-draw` = 0).
- **Q3 PASS.** 26 against 26.

So `if differential:` fires on every renewal in every arm. The control arm is exposed to the
elasticity draw exactly as much as the value arm is. That exposure is why a floor of
`--redraw-mode all` moves the control net as well as the value net.

**No single average explains the default draw.** Mean elasticity over the 26 drawers is 1.012 at
the default seed, against 1.343, 1.123 and 0.968 at 11111, 22222 and 33333. Seeds 11111 and 22222
gave identical control nets (19,165.54) with means 1.34 and 1.12. So the control net does not track
the book's mean sensitivity. It moves on which few households cross the departure roll. That is a
lumpy, few-household outcome. It fits the placebo's discreteness (two of three seeds identical), and
it fits a full-window control gap of about 5 sd of the three re-draws, which a smooth draw would
almost never give.

## Decision: intended; the floor needs nine seeds

The exposure is intended (see "What the code says"). What is wrong is the band's sample size. I
simulated how often the default draw falls outside the published band, `[min - 1 sd, max + 1 sd]`
over N re-draws, when it is truly exchangeable with them (the placebo's P2 establishes
exchangeability). The rates were close for normal and lumpy draws:

| N floor seeds | 3 | 5 | 7 | 9 | 11 | 15 |
|---|---|---|---|---|---|---|
| P(default outside band), normal | 0.236 | 0.116 | 0.069 | 0.049 | 0.036 | 0.021 |
| P(default outside band), lumpy | 0.210 | 0.115 | 0.069 | 0.046 | 0.031 | 0.015 |

With three seeds the page's band misses an honest draw about one time in four or five. Leg 1's
H2 failure is a draw of that kind. **Nine seeds** is the smallest N at which the band misses about 5%
of the time, which is the reading a bound on a page invites. The number comes from the band's own
definition, not from a dial. That means six seeds beyond 11111/22222/33333, at about 2 h each over the full
window, in three two-seed legs so each ends within 5 h. Run them serially, after
`longjob-w220-recov-arms`. Until they are in, the page's three-seed band should be read as a
bound that misses about 1 time in 4.

**Owed, handed on:** the full-window by-arm probe (one ~53 min pass, after the recovery arms run),
and the six extra floor seeds folded with `--fold`.
