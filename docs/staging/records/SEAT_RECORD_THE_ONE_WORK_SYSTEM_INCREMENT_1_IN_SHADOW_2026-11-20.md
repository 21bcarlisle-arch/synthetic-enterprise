**Severity:** RECORDED · **Lane:** H_harness · **Atom:** `unminted` (direction `the-one-work-system-build`)

# The one work system, increment 1: the store, the pick, and the staging findings in shadow (2026-11-20)

This is plan item 11 of `docs/operations/WEEKLY_BALANCE_REVIEW_2026-11-16.md` §5, built to
`docs/design/ONE_WORK_SYSTEM_DECISION_MAP_2026-11-20.md`. The K8 page is
`docs/market_research/one_backlog_and_flow_practice_2026-11-20.md`. This increment covers D9
steps 1 and 2.

## What this commit carries

- **`background/work_items.py`**:
  - the D2 item shape (`validate`, `write_item`, `read_item`; one YAML file per item under
    `docs/work/items/`);
  - `next_item()`, which is D6 in order: eligibility, stop-the-line at WIP 1, the error-budget
    stop per lane, the row furthest below its share, then his rank, date, severity and age;
  - `items_from_staging()`, the first source.
- **`docs/work/cutover.yaml`**: `staging_findings: shadow`. There is no `on` mode yet.
- **`docs/direction/priority_order.yaml` `weekly_split:`**: the 16 Nov review's §4 split,
  copied as the share table that D6 step 3 reads. The decision map says the shares are "written
  into priority_order.yaml as they are now". They were not; they were only prose in the review.
- **`background/supervisor.py`**: `_self_refill_draw` logs `next_item()`'s pick beside the
  ladder's draw, to a gitignored log in the shared tree's observability directory, never committed. The draw itself
  is unchanged, and a failing shadow is logged by name and cannot cost the draw. The cost
  measured on the real tree is 32 ms a draw.
- **Tests**: 16 in `tests/background/test_work_items.py`. Nine source mutations were applied one
  at a time, and each turned exactly one test red:
  - the per-lane BLOCKING filter;
  - expedite WIP 1;
  - severity in the order;
  - the week boundary;
  - the due-date rank;
  - the parked revisit;
  - the director-decider exclusion;
  - the sign of the deficit;
  - the flag check.

## Choices this increment made, and why

- **In shadow, items are derived and never written.** Writing 185 item files today, while the
  staging root is still the live queue, would make a second store of the same work that drifts
  within the hour. That drift is the failure the steer exists to end. The files are written at
  cut-over (`python3 -m background.work_items --migrate --write`, which refuses while the flag
  reads `shadow`), in the commit that stops the staging root being a queue.
- **A finding's `kind` is set by a stated rule, not read.** The header does not carry it: a
  finding is `correctness`, and on the building side it is `harness`. `affects` is left `None`
  (unassessed). An empty list would assert that the finding affects nothing (K2). Triage corrects
  both, per item.
- **Lane to side.** W1–W3 and W5 are the world. B–G are the supplier. A, H and W4 (the wall's
  verifier) are building. A test ties the mapping to `finding_severity.LANES`, so a new lane
  cannot go unmapped.
- **Step 3 measures landed COUNT, not points.** D2 gives an item no points field. This is a GAP,
  carried in the code's own comment.

## The migration at real inputs

185 staging-root findings become 185 items, 0 refused, 185 distinct ids:

| Side | Items |
|---|---|
| world | 53 |
| supplier | 69 |
| building | 63 |

There are no BLOCKING findings at the root today. Today's pick is
`advisor-findings-register-error-channels-are-inert` (LATENT, correctness, the oldest).

## Pre-registration for the side-by-side day (written before any row of it exists)

**Known by construction, so not a prediction.** In shadow no item is ever `done`, so every share
row reads 0 landed, and step 3 always takes `correctness`, the largest share. The day cannot
test step 3. It is tested only once items close in the store, after cut-over.

Predictions, read off `python3 -m background.work_items --compare` at or after 11:30 on
2026-11-21:

- **P1.** `ladder_names_any_finding` is true in **at most 10%** of draws. The ladder draws atoms,
  continuations and the delivery lane. Today it names a finding by filename mainly through rung 1c
  (BLOCKING), and the root holds none.
- **P2.** `ladder_names_pick` is true in **at most 5%** of draws.
- **P3.** At most **5 distinct picks** over the day. The pick changes only when the oldest
  correctness finding leaves the root.
- **P4.** **Zero** `ONE WORK SYSTEM SHADOW failed` lines in the supervisor log.

**What the day decides.** If P1 holds, the old ladder and the new pick are not two answers to the
same question. The old system does not draw findings as work at all: findings are worked by
seat-drawn triage. "Agreement" is then not the cut-over test. The cut-over test becomes:
- P4 holds (the pick is safe to run);
- every pick is one the triage would accept as the next finding to work, read by hand over the
  day's distinct picks.

If P1 fails, the rows where both name a finding are the comparison, and they are read pair by
pair.

## Next

Handed on as `the-one-work-system-cut-over-staging-findings` (DO NOT DRAW BEFORE the 21 Nov read):
- grade P1–P4;
- if the test passes, build the `on` mode;
- write the items, and stop the staging root being a queue in the same commit (D9 step 3: done
  includes deletion).

D7 (the dials) waits on the director's answer to the for_the_director row
`the-one-work-system-s-decision-map`. It matters only once atom steps become a source, and none
is one yet.
