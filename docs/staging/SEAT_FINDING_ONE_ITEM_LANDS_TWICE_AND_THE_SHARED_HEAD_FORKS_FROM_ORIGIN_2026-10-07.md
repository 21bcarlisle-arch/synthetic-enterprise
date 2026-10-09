**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One item lands twice, on origin and on the shared HEAD, and the shared checkout forks

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Carried as `one-item-lands-twice-on-origin-and-the-shared-head`,
55 listings since 2026-09-30.*

## The defect

An item reaches origin through `surgical_land`, and the same change is also committed locally on
the shared checkout's HEAD, with different bytes. The two copies conflict, `origin_reconcile`
refuses the fast-forward, and the shared checkout forks. While it is forked, every daemon runs code
that origin has replaced, and the publisher refuses with `behind_origin`.

- 2026-09-30: four pairs in one stretch.
- 2026-10-01: `75df9efdf` after `d77ff33d5`.
- 2026-10-07: `17f75226a` and `f07af3845` (W2_20 and W2_21 at L1) were local commits on the shared
  HEAD and on no remote, while `067493aa4` carried both to origin. The fork stood from 07:50 until
  `d8c139a1f` merged it at 10:21. In that time the 09:21 orientation ran the old direction-record
  code (`d1b8da5fd`).

## Why the existing proposal does not cover it

`SEAT_PROPOSAL_WHAT_FORCES_THE_MERGES_ON_MAIN_MEASURED_AND_WHAT_TO_CHANGE_2026-10-04` deals with
abandoned working copies that hold the fast-forward. This is a different writer: a lane that
commits on the shared checkout itself.

## What done means

A commit on the shared checkout's HEAD that does not come from the reconciler or the publisher is
refused, with a message naming `surgical_land` as the door. Or, if some daemon needs that path,
its commits are listed, and an item already on origin under a receipt is never re-committed
locally. The control is a fixture shared checkout where a plain `git commit` must be refused.

## 2026-10-09: the fork closed; it is now held by 18 paths

*Worker tick, direction item `make-origin-contain-the-shared-heads-stranded-commit`.*

Another instance, the same shape. `e3e5970e1` (the map-parse cache) was committed on the shared
HEAD and nowhere else, while origin carried its own write-up of the same timeout round. From
01:35 UTC reconcile-watch read `REFUSED_CONFLICT` on one path,
`docs/observability/operational_layer_timeout_prereg_2026-09-10.md`. That was a real conflict:
two lanes had written the same round concurrently. Both sections were kept, and the code merged
clean. Merge `effd32f63` was gated through `surgical_land --merge --resolve` and promoted at
01:47 UTC. `e3e5970e1` is now an ancestor of origin/main.

At the next cycle (01:49 UTC) the shared checkout read **0 ahead, 67 behind,
`NOT_ADVANCED`**. The fork is gone, but the fast-forward is still refused, by 18 paths. Each was
checked by `git hash-object` against `origin/main:<path>`:

**Byte-identical to origin (8 twins; nobody's work is at stake):** `docs/direction/DIRECTION.yaml`,
`docs/direction/decisions.jsonl`, `docs/status/SEAT_STRETCH_LOG.md`, `site/data/delivery.json`
(all modified 00:31, i.e. the seat's own direction landing left its working copies behind), and
four untracked staging notes: `…A_GAS_HOMES_ELECTRICITY_LEVEL_SPLIT…`, `…THE_KETTLE_DOES_NOT_SCALE…`,
`…THE_LEVEL_EXCESS_IS_SPLIT_BY_OCCUPANCY…`, `…THE_WORLDS_ARREARS_RUN_OFF_INCOME_STRESS…`.

**Different from origin (10; real local bytes, someone's to land or drop):**
- `background/delivery_lane.py` (+52, 2026-10-05)
- `tests/background/test_supervisor.py` (+2, 2026-10-05)
- `tests/simulation/test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py` (+79, 2026-09-24)
- `docs/institutional/knowledge_map.md` (+1, 2026-10-08)
- `docs/market_research/a_save_offer_against_the_switching_rules_and_the_seam.md` (+30/−1, 2026-10-08)
- `docs/observability/test_execution_log.jsonl` (generated append log, +2458)
- untracked staging notes whose bytes differ from origin's: `…THE_3_02_HEADCOUNT…`,
  `…THE_REACTIVE_SAVE_IN_THE_SETTLED_RUN…`, `…THE_WORLD_LOSES_FORTY_PERCENT…`,
  `…THE_RENEWAL_ROUTE_CARRIES_THE_WHOLE_BOOK_RESIDUAL…`

The twins can be cleared mechanically. The three code/test paths dated 09-24 to 10-05 are
abandoned-copy candidates for `origin_reconcile.preserve_abandoned_copies`, not lane work in
flight. Until both kinds are cleared, the daemons keep running pre-`effd32f63` code even though the
fork itself is closed. This tick did not touch the shared checkout's HEAD, index or working files.
