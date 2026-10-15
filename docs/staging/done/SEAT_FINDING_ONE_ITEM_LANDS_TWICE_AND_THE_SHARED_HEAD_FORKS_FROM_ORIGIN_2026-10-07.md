**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One item lands twice, on origin and on the shared HEAD, and the shared checkout forks

**Fate (2026-10-15):** DONE -- closed 2026-10-15: a commit in the shared checkout whose HEAD lacks origin/main is refused at both doors (background/shared_head_fork.py), and the live fork's eight commits were merged into origin.
**Fate (2026-10-12, clear-the-decks):** ATOM -- what done means control (refuse a plain git commit on the shared checkout outside surgical_land) not found in background/*.py; twin-rule part closed by SEAT_DISPOSITION_THE_TWIN_RULE... but a structural blocker (test_execution_log.jsonl classification) is explicitly handed to a next item (P2)

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

## 2026-10-15: the writer is `surgical_land` itself, landing on a checkout behind origin

*Delivery-seat executor, direction item `the-shared-checkout-fast-forwards-past-its-duplicate-of-068928f47`.*

It recurred. `bb5276856` (surgical_land receipt, parent `10e90b5c7`, the shared HEAD) and origin's
`068928f47` (parent `cd2fda5c6`) carry the same two files: `git diff bb5276856 068928f47` on both
paths is empty. `bb5276856` is a duplicate with nothing of its own, so it can be thrown away. It
still held the fork, because origin edited `when_an_electrically_heated_homes_water_heater_runs.md`
after `068928f47`. That made the stranded copy an add/add conflict, and reconcile-watch read
`REFUSED_CONFLICT` on it every cycle from 10:21 onwards.

**The cause, measured.** The 2026-10-07 hypothesis was a plain `git commit` on the shared HEAD.
That is not what wrote these. `surgical_land` lands on whatever HEAD its own checkout holds. On
the primary checkout that HEAD is the shared branch, and nothing asked whether origin had moved
past it. Across the 24 `surgical-land` entries in the shared `main` reflog from 2026-10-13 to
2026-10-15, I counted the origin commits each parent lacked when it landed:

| at landing | landings | on origin under their own sha |
|---|---|---|
| 0 behind | 15 | 15 |
| 29–97 behind | 9 | 8 only via merge `1610b2640` (~19 h later); `bb5276856` never; it was re-landed as `068928f47` |

At 0 behind, the reconciler pushes the commit as a fast-forward and origin gets the same sha.
Behind origin, a commit can reach origin only as a merge, and that merge may never come. The lane
sees its work missing and lands it again from a worktree.

**The fix.** `tools/surgical_land.py::_refuse_a_landing_a_behind_checkout_would_strand` makes the
primary checkout **not touched** in that state. It refuses a landing whose parents do not contain
`refs/remotes/origin/main`, and the refusal names the worktree-and-promote route. It does not
refuse in three cases:
- a linked worktree, which moves no shared branch;
- a repo with no origin ref;
- a `--merge` whose other side contains origin, which is the commit that closes the gap.

The control is in `tests/tools/test_surgical_land.py`. The refusal leg reds on today's shape, and
a partition control shows all three passing routes still land. Four mutations each red a control:
the call removed, the worktree exemption removed, the merge side ignored, and the guard made
unconditional. A fifth, the no-origin exemption removed, reds the file's other 100 tests.

**The fork.** It is closed by the door `1610b2640` used: `surgical_land --merge bb5276856`, run
from an origin worktree, with the conflicted doc resolved to origin's bytes. The merge's tree is
origin's tree. After promotion the shared checkout is 0 ahead, so the reconciler's
`advance_shared_tree` can fast-forward it once the paths blocking it are cleared.

**Where it stands, 12:26 UTC.** `ed7e89d12` (the guard) and `3fd241644` (the merge) reached origin
in promotion `9d71b68c9`. The shared checkout now reads **0 ahead, 116 behind**, and
`bb5276856` is an ancestor of origin, so the fork is closed. The fast-forward is still
`NOT_ADVANCED`, on 54 paths. A dry run of `advance_shared_tree` used a lock that throws before any
write. It proves 51 of the 54 lossless and is held, all-or-nothing, by three that
`refresh_to_head --base origin/main` also refuses as holder work. I did not touch those three:
- `site/data/knowledge_topics.json`, written 2026-10-14 07:13. It is the pre-landing draft of
  b585d3733's N page, and d26837927 revised that page again. It still changes 13 values across
  three pages, so it is not provably superseded. It is under the 48 h abandonment line, and that
  is what keeps the abandoned class from firing for all three.
- `docs/institutional/knowledge_map.md`, written 2026-10-13 00:38. It is a replacement draft, and
  among its changes it holds a capital target of £115 (decided 26 July 2023) where HEAD has £130.
  That is a factual question worth checking against Ofgem's decision. It is not settled here.
- `tests/company/compliance/test_crisis_bad_debt_validator.py`, written 2026-10-11 05:18. It
  supplies 5 names origin lacks, among them
  `test_the_strict_marker_is_not_armed_by_the_working_tree_copy`.

When `knowledge_topics.json` crosses 48 h, at **2026-10-16 07:13 BST**, all three age out together.
The reconciler then preserves them on `refs/preserved/abandoned/*`, names them in one staging item
and fast-forwards with no one needing to act. A lane that lands or drops any of the three before
then brings that forward.
