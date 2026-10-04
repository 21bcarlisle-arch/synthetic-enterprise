# The dead worktree /tmp/hr_wt_394097's salvage is settled: one edit landed, the rest disposable

*Worker, 2026-10-04. Disposition record for SALVAGE `278606ed4` (fork_salvage, 08:05Z, on base
`2b5c8bf7e`). Nothing reaches it except tag `salvage/detached-278606ed4ede`. By the time this was
drawn, the worktree directory and its `git worktree` registration were both already gone.*

| Path in the salvage | Disposition | Evidence |
|---|---|---|
| `tests/background/test_an_empty_git_dir_made_scratch_immortal.py` | **LANDED** `a8fc1eda4` | No commit to the path since base; at origin, 2 of its 14 nodes were RED and the salvage copy made all 14 green. Mutation-checked (see the commit). |
| `tests/background/test_a_relaunch_cannot_erase_the_death_it_follows.py` | disposable: already on origin | `351623c4f` adds the same `peak_mb=1000, residents=lambda: [], guest_total_mb=24000`; the only difference is where the comment sits |
| `tests/background/test_an_unreadable_launch_register_is_never_an_empty_board.py` | disposable: already on origin | byte-identical to origin/main |
| `tests/background/test_the_census_lost_five_hits_to_the_parameter_seam.py` | disposable: already on origin | `351623c4f` adds the same `claims.json.lock` exclusion; only the docstring wording differs |
| `tests/simulation/test_policy_cost_coverage.py` | disposable: already on origin | `351623c4f` keys the same assertion to the measurement; origin also bounds it by `table_count` |
| `docs/context-handshake-latest.md` | disposable: runtime output | a Risk Committee wake-up prompt rewritten by a sim run |
| `docs/observability/test_execution_log.jsonl` | disposable: runtime output | 19 appended pytest execution rows |
| `.se_worktree_owner` | disposable | the dead owner's pid stamp |

The salvage tag can be deleted. Nothing in it is unlanded. I left it in place: deleting a ref is
not this item's job, and the tag costs nothing.
