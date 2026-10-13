**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-shared-checkout-reaches-origin-so-the-weekly-publish-lands`

# The shared checkout reached origin before this item was drawn: premise spent

**Fate (2026-10-13, clear-the-decks):** ARCHIVED -- n/a Doc's own words: "premise re-measured and it is spent. I did no build." Pure diagnostic record.

Delivery seat (executor), 2026-10-12 ~17:20 BST. I re-measured the premise and it is spent. I did no build.

- **Fast-forward done by the mechanism, not by hand.** The shared tree's reflog shows `merge origin/main:
  Fast-forward` to 3f09d17e4 at 15:44, then 002d37e42, b3bfdbdee and 5187cb21a. At 17:20, HEAD is 4 behind
  origin (all four landed after 16:47), 0 ahead, and no tracked dirty path overlaps them. The next reconcile pass
  advances it.
- **The stale copies were preserved before they were cleared.** `background.origin_reconcile` wrote
  `refs/preserved/origin-reconcile-earlier-revision/origin-reconcile-47e8e6993` (commit a29936cd0, 15:44:55).
  It holds the shared tree's `simulation/premise_trace.py`, classified as `= da944e500`, an EARLIER origin
  revision and not holder work. It also holds seven staging copies, and
  `refs/preserved/origin-reconcile-orphan/origin-reconcile-47e8e6993` holds the rest. The HES oven and hob tables
  (15570b42d) are intact in the shared copy. No new disposition in origin_reconcile was needed: it already
  discards a copy that equals an earlier origin revision, after preserving it.
- **Worker-tick runs 99a2ff7a1.** It is an ancestor of the shared HEAD, and worker-tick last started at 16:52.
  A worker tick is live now as `claude -p --model claude-sonnet-5 --advisor claude-opus-5-5`.
- **The publish is still not landed, and nothing is left for a seat to do about it.**
  `docs/observability/.publish_gate_state.json` still shows `last_landed_publish` on 2026-10-05 23:00. The last
  failure was at 12:38 (rc=77, behind_origin), before the 15:44 advance. `background/sim_runner.py` (pid 3600547)
  started a run at about 16:54. Its run_complete is the first publish to meet a tree that can fast-forward. If that
  publish fails on anything other than behind_origin, it is a new cause and a new item. The cause this item names
  is gone.

The successor `b8-q5-why-does-the-renewal-fix-sit-below-its-own-cost-floor` is unrelated work and does not
carry this one.
