# PREREGISTRATION — whether clearing ten superseded working copies closes the publish fork

*Worker, 2026-09-17, written BEFORE the clearing is attempted. Claim:
`the-publish-gate-must-now-grade-a-clean-publish-itself`.*

## What is already measured (not predicted — these are observations, recorded so the predictions below cannot be read as hindsight)

The drawn item said `.publish_gate_state.json` still carried `last_clean_publish=null`,
`wedge_since=1789011039.7` and **12 blocking tests, every one of them from the repaired ledger-guard
set**. At the start of this turn the same file carries:

* `total_red: 1`, `blocking_tests:
  ["tests/background/test_a_behind_origin_publish_refuses_instead_of_deepening_the_fork.py::test_a_level_tree_still_publishes"]`
  — **the 12 are gone; the gate DID re-grade its red census.**
* That one remaining test: `10 passed in 0.17s` in the shared tree. So the red census is itself
  one cycle stale, and **no red the item named is live.**
* `last_clean_publish: null` and `wedge_since` unchanged. **The gate is still wedged, and not by
  the reds.**

The item predicted the remainder would attribute to the HEAD ref-lock loss
(`cannot lock ref HEAD: is at aff4b153f but expected 56d746816`). That record is superseded: the
latest `liveness_surface_refusal` reads `cause: push_never_landed`, and git says the tree is
**forked** — `origin/main...HEAD` = 7 behind / 9 ahead, `origin/main` = 6c1e769b4 is NOT an
ancestor of HEAD = 1a69fbb23.

`origin_reconcile`'s own verdict names why the fork cannot close: **10 paths in the shared working
tree**, 2 tracked-and-modified and 8 untracked, each of which origin's incoming 7 commits also
write. Every one of the 10 was compared to `origin/main`'s copy this turn:

| verdict | paths |
|---|---|
| byte-IDENTICAL to origin | 6 untracked docs + `tools/weather_cell_drivers.py` |
| origin is STRICTLY RICHER (local is the earlier draft) | `SEAT_RESULT_THE_STRANDED_WEATHER_MACHINERY...`, `WORKER_RESULT_THE_PER_CELL_WEATHER_STORES...`, `tests/background/conftest.py` |

The three that differ were read hunk by hunk: origin carries the local content **plus** the later
discharge/correction blocks, and `conftest.py`'s local edit adds
`("background.process_run_complete", "LANDING_IN_FLIGHT_FILE")` — which origin's copy already has at
line 67, under a better comment. Local mtimes are OLDER than the origin commits that landed them
(`conftest.py` 00:20 local vs 02:25 on origin). **These are stale copies of landed work, not another
lane's live holder work** — the test memory says to ask that question, and the answer is stale.

## Predictions

1. **Clearing all 10 to origin's bytes is lossless.** Every byte is recoverable with
   `git show origin/main:<path>`, and no local sentence is lost, because origin's copy is a superset
   in all three differing cases. *Falsifier: any hunk present locally and absent on origin.*
2. **The blocker set is complete at 10.** After clearing, `origin_reconcile` will report no further
   refusing path and will close the fork. *Falsifier: an eleventh path appears — which would mean
   the refusal's own list is truncated or fail-fast, and that is then the finding.*
3. **The gate will NOT re-grade itself even once the fork is closed.** `last_clean_publish` stays
   `null` and `wedge_since` stays set until a real publisher cycle runs and pushes. Nothing in this
   turn's clearing moves that field. *Falsifier: the field changes without a publish cycle.*
4. **The item's named cause is refuted, not merely absent.** The remainder attributes to the fork —
   `push_never_landed` / `behind_origin` — and NOT to the HEAD ref-lock loss. I expect to find no
   live evidence of a ref-lock collision at all. *Falsifier: a ref-lock refusal appears in the
   record after the fork is closed.*
5. **The deepening will be visible in the local side of the fork.** `_divergence_refusal` was
   narrowed on 2026-09-16 to publish anyway when origin's incoming paths do not collide with the
   publish paths, on the stated premise that *"`origin_reconcile` absorbs it on the next cadence"*.
   That premise is what failed here — reconcile has been refused for days — so I predict the local
   9 contain **more than one copy of the same heartbeat/banner pair**, created by that narrowing.
   *Falsifier: each publish commit shape appears once.*

## What done means for this turn

The fork closed, or the remaining blocker named with its holder; the attribution landed beside the
item; and the claim bound with `--landed`. A publish cycle grading itself green is the NEXT turn's
evidence, by prediction 3 — I am not claiming it here.
