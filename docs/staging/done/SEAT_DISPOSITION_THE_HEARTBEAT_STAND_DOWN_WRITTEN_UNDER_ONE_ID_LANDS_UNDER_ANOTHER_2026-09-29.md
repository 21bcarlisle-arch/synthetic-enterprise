# Disposition: `stop-heartbeat-commits-that-deploy-nothing-or-commit-onto-a-behind-tree` is credited with the landing of `land-the-heartbeat-stand-down-already-in-the-shared-tree`

**Severity:** RECORDED · **Lane:** H_harness

No defect. One piece of work was drawn under two ids.

- `stop-heartbeat-commits-…` was claimed at dispatch 2026-09-28 22:56Z. At 22:59Z that invocation wrote `_heartbeat_stand_down` and its test class into the shared tree. It ended without landing them.
- `land-the-heartbeat-stand-down-already-in-the-shared-tree` was drawn 2026-09-29 to land those bytes.
  - `ps` found no live writer or `surgical_land` holding either path.
  - Neither file had moved on origin since that draw's HEAD.
  - All four hunks were this work, so `isolate_hunks` kept every one of them.
  - Landed with `surgical_land` from a scratch worktree at origin/main. The shared tree was 24 behind and 2 ahead, and a reconcile merge was in flight.

The function is unchanged from what was in the tree. One leg was added to its wiring test: the stand-down reason must reach the publisher's log.

**Mutation proof** (scratch worktree; the stand-down tests are 8, partition first):

| Mutation | Result |
|---|---|
| site leg dead | 2 red |
| behind leg dead | 3 red |
| refuse everything | 7 of 8 red |
| bound ignores `PUSH_LAG_AFTER_SECONDS` | 1 red |
| reason not logged | 1 red |
| unwired from `_refresh_published_liveness_on_skip` | 1 red |
| successful advance ignored | 1 red |

`test_process_run_complete.py` whole file: 109 passed, 3 skipped. `tests/design/` + static ratchet: green.

**Still to observe (no work):** two things need to be checked on origin after the next few publish cycles:

1. `chore(liveness)` commits that touch no `site/` path stop appearing.
2. `site/data/tick_heartbeat.json` on origin keeps advancing within the banner's `stale_after_seconds`.

The only branch that could freeze it is the behind leg. It is bounded by that same number minus the delivery-lag horizon.
