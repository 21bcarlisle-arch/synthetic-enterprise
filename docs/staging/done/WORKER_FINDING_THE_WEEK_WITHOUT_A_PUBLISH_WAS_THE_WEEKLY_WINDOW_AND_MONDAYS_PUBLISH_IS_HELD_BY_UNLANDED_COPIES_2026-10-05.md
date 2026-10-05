# The week without a publish was the weekly window; Monday's publish is held by unlanded copies

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

*Worker, 2026-10-05, drawn as `figures-reach-the-site-again-after-a-week-without-a-publish`.*

## What the item claimed, and what is true

The item said no publish had reached origin since `1526f5267` (2026-09-28 04:46Z) "while run_complete
markers kept arriving", and read that as a week-long fault. **Correction: four of the five markers
it named were held on purpose.** The director asked for weekly publishing on 2026-09-26 ("make it
real, and anchor it to Monday"), and `77e9db44a` built it: figures go to origin once a week, from
Monday 04:00 London. `sim-runner-log.md`, per marker:

| marker | what the publisher did |
|---|---|
| `20261001T055550Z` | HOLD (weekly window) — this week's figures reached origin 2026-09-28T04:46Z |
| `20261001T155057Z` | HOLD, same |
| `20261003T203729Z` | HOLD, same |
| `20261004T190804Z` | HOLD, same |
| `20261005T032309Z` | window OPEN; regen, scoped gate GREEN (1750 s), commit REFUSED `behind_origin` — the shared tree could not fast-forward, 3 behind, `docs/status/STARTUP_ANCHORS.md` among the collisions |
| `20261005T054613Z` | window OPEN; gate GREEN (1417 s), REFUSED `behind_origin` — 15 behind |

So the real fault is about four hours old, not a week: **this Monday's publish is owed and is
refused because the shared tree will not fast-forward.** The window stays open (it reads git, not a
stamp: `content_publish_window()` → `open: True, "this week's figures are owed"`), so the next
marker retries without help as soon as the tree can advance.

## Why the shared tree will not advance

`origin_reconcile` at 06:50Z: `NOT_ADVANCED`, 18 behind, 0 ahead, held by 19 paths. Classified
against origin, then and now:

- **9 are byte-identical to origin** (`DIRECTION.yaml`, `decisions.jsonl`, `SEAT_STRETCH_LOG.md`,
  `BLOCKED_ATOM_VISIBILITY.md`, `site/data/delivery.json`, four staging notes). These clear on their own.
- **Generated exhaust**: `grid_intensity_feed.json`, `explore_carbon.json`, `engagement_separation.json`,
  `STARTUP_ANCHORS.md`. The publisher wrote these itself from HEAD's (older) code. They clear on their own.
- **Hand work that nobody has landed**. These are what actually hold the tree, because the advance is all-or-nothing:
  - `docs/market_research/company_customer_comms.md`: a call-wait re-verification note, 2026-10-04.
  - `docs/market_research/satisfaction_drivers_and_the_three_bill_shocks.md`: SLC 27.15 replaces the
    "SLC 27B ±5%" claim, 2026-09-24.
  - `tests/architecture/test_year_keyed_rate_table_census.py`: a 186-line rewrite, 2026-09-24.
  - `tools/draw_follows_the_order.py` + its test: separates the candidates from the pool, plus
    `SUBJECT_MAX_FILES`, 2026-10-05 04:17Z. These were written after `666ed5fe0` changed the
    same file on origin.
  - The C29 staging note, which a live `surgical_land` was landing during this turn.

The interactive seat's continuity handoff (`WORKER_FINDING_REPEATING_ALARM_SEAT_CONTINUITY_2026-09-15.md`)
has listed the first three as stranded work several times. Two of them are older than the
reconciler's 48 h abandonment age. They cannot be cleared as abandoned while one younger copy is
still held, which is by design.

## What was changed

**The publish state now counts failures since the last publish that reached origin.** Two new
fields in `.publish_gate_state.json`:

- `last_landed_publish`: git's date for the figures on origin (`publish_freshness.content_on_origin_ts`).
- `failures_since_landed_publish`: only a change in that date resets it.

`episode_failures` is unchanged; it still describes the episode.

Why the old count read "an hour": at 04:28Z the week-old deferred delivery of `1526f5267` was graded
REACHED. `grade_outstanding_delivery` then stamped `last_clean_publish` with *that instant* and
closed the episode, so the record said "last clean publish 04:28Z today, 1 failure" with figures
seven days old on origin. **`last_clean_publish` on the live record is therefore false**: it names
no publish, only the moment a late delivery was noticed. The new field does not inherit that error,
because it asks git.

Numbers, at real inputs (the live record and git, 2026-10-05):

| reading | old record | new fields |
|---|---|---|
| today's history | `wedge_since` 04:28Z (2.4 h), `episode_failures` 2, `last_clean_publish` 04:28Z | `last_landed_publish` 2026-09-28T04:46Z (7.1 days), `failures_since_landed_publish` 2 |
| the next failure, nothing landed | — | 3 |
| a publish lands, then one failure | — | landed 1 h ago, count 1 |
| git unreadable | — | anchor kept, count still counts, never resets |

The count is 2, not 7. The holds were not failures, and calling them failures would undo the
director's cadence.

## What is owed, and to whom

1. **The interactive seat's stranded copies** (above) need landing through `isolate_hunks --survey` and
   `surgical_land --content`, or withdrawing. Until that happens, every Monday's publish depends on
   that tree being clean. This is the step that DONE depends on.
2. **`grade_outstanding_delivery` stamps `now`** for a delivery it observes late. A smaller defect is
   left in place: once the new field exists, nothing has to read `last_clean_publish` as "when figures
   landed".
