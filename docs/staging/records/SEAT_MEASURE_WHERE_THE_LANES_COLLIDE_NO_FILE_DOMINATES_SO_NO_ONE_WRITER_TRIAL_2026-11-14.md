# Where the lanes collide: no file dominates, so no one-writer trial

**Severity:** info · **Lane:** H_harness · **Steer:** `docs/staging/advisor/done/DIRECTOR_STEER_ONE_WRITER_PER_SHARED_FILE_MEASURE_WHERE_LANES_COLLIDE_FIRST_2026-11-14.md` · worker tick, 2026-11-14

**Answer.** No two or three files account for most collisions. The top file is `docs/direction/DIRECTION.yaml`. It carries 3.7% of the collision mentions in session transcripts. The top three carry 10% and the top thirty carry 42%. The steer's third outcome applies: the shared tree's cost is paid and known, so no trial is proposed and nothing is built. What contention there is comes from the trunk moving, not from a hot file. A one-writer rule per file would remove none of it.

Window: 31 Oct to 14 Nov 2026. Scripts and raw output: `docs/staging/records/collision_census_2026-11-14/`.

## Prediction (filed at 12:24Z, before any count was run; copied from `PREDICTION.md` in that folder)

| # | Predicted | Result |
|---|---|---|
| 1 | `DIRECTION.yaml` is the top file | **Holds in transcripts** (87 sessions, the top). In landed history it is joint fifth (2 hours on the lower bound). |
| 2 | The top three files carry at least 40% (range 25 to 60%) | **Refuted.** 10% in transcripts. 32% in landed history, on the lower bound of only 37 hours. |
| 3 | `company/` and `simulation/` together carry under 5% | **Refuted.** 17.6% in transcripts, 5.4% in landed history. |
| 4 | Mostly the delivery seat and worker ticks | **Partly refuted.** Worker ticks are in 35 of the 37 collision hours. The delivery seat is in 2. |
| 5 | At least half of the contention-subject commits touch a top-three file | **Refuted.** They touch the landing tools themselves (`refresh_to_head`, `origin_reconcile`, `delivery_seat`). |

The advisor guessed that `site/data` leads. **That is also refuted.** `site/data` has 2,778 file touches, but they come from only 102 commits by two writers: the delivery seat (36 commits) and the provenance daemon (33). That is one collision hour, and 1.9% of the transcript mentions. It is churn, not contention, which is the first failure mode the steer named.

## Three measures

**1. Landed history** (origin/main: 753 commits, 141 merges). A collision is a clock hour in which two or more writers committed non-merge changes to the same file.

- **Attributing writers.** 244 commits were matched to a worker-tick session through the commit or landing line in its transcript. Subjects attributed 83 to the delivery seat, 64 to the advisor and 58 to daemons. The other 304 are unattributed, most likely worker work landed through long jobs, whose output carries no `[main <sha>]` line.
- **Counts.** There are **37 collision hours on the lower bound**, which counts all unattributed commits as one writer. The upper bound is **103**, which counts each unattributed commit as its own writer. Either way that is under 3 a day.
- **Top files on the lower bound.** `tools/generate_billing_ledger.py` 4. Two level-DD findings, 4 each. `maturity_map.yaml` 3. `DIRECTION.yaml` 2.
- **Who collides.** 35 of the 37 hours involve worker ticks: 20 with unattributed commits, 14 between worker ticks alone, and 1 with the delivery seat. One more pairs the delivery seat with unattributed commits, and one pairs the advisor with them.
- **Merges.** Only **12 of 141 merges had any file changed on both sides**: 31 contested file-merges in all. The top file there is `generate_billing_ledger.py`, with 3. `DIRECTION.yaml` has 1. The other 129 merges are catch-up merges where no file is shared.

**2. Working tree, from session transcripts** (1,321 transcripts). These are output lines that name a path and use a collision phrase.

- **2,823 lines in all.** "behind origin" 1,937 (69%), "another lane" 764, "holder work" 68, "predates landing" 21, "contested" 18, "CONFLICT (" 14.
- **2,363 distinct (path, session) pairs.** The top three:
  - `DIRECTION.yaml` 87
  - `tests/design/test_atom_records_store.py` 86
  - `test_the_published_series_and_the_ledger_it_came_from_are_committed_together.py` 70
- **By area:** `docs/staging` 20.7%, `tests` 17.6%, `company` 10.4%, `simulation` 7.2%, `tools` 6.9%, `docs/direction` 5.5%, `site/data` 1.9%.
- **This measure overcounts.** The draw's own prompt lists paths with "another lane" and the post-publish reds, and some of those reach tool output. Read it as an upper bound on how spread out the mentions are, not as a count of collisions.

**3. Cost** (wall time from a tool call to its result in transcripts, Bash calls only). Calls that ran in the background understate time; time spent waiting overstates it.

| Tool | Calls | Sessions | Hours over 14 days |
|---|---|---|---|
| `isolate_hunks` | 197 | 74 | 6.1 |
| `origin_reconcile` | 223 | 49 | 0.9 |
| `git merge` / `pull` / `rebase` | 907 | 450 | 2.3 |
| `refresh_to_head` | 79 | 26 | 0.0 |
| `surgical_land` / `promote_worktree_landing` | 4,392 | 709 | 102.7 |

The tools that exist only because of contention cost **about 9.3 hours in two weeks**, roughly 40 minutes a day, across 698 session-hours. `surgical_land`'s 103 hours are mostly the gates themselves. A single writer would still have to pass them, because hook-bypass is a wall. **Not measured:** how much of that time is re-runs after origin moved underneath a landing. That share is the only part a different design could recover, and it is the open number.

## The guards a one-writer file would retire (outcome 4)

**None.** The cost is spread thin, so `isolate_hunks`, `surgical_land`, the tree lock and the fork alarms are all still needed for the other files. One owner for `DIRECTION.yaml` would remove at most 87 of 2,363 session-mentions, and 1 of 31 contested file-merges.

## Does this release the held 9 Nov generated-data steer?

**No.** It removes one argument from that steer and leaves its question open. `site/data` is not a collision source, so a single publisher for feeds would not be justified on contention grounds. The 9 Nov steer measures repository size and reading cost, and this census did not measure either. It stays where the delivery seat ranked it, in `held_behind_the_exit_test`.

## If anyone reopens this

The question to measure next is the share of `surgical_land` runs that are re-runs because origin moved (the "behind origin" lines). Only that number could justify redesigning the shared tree. It stays filed here, and nothing is built until someone has measured it.
