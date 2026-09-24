**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# RESULT — honest alarm counts cannot move the ORDER 60 ranking, and the act of writing them demotes the document to last

Drawn as `check-whether-honest-alarm-counts-move-the-order-60-draw-ranking` (Lane 0, director
direction). Answers
`docs/staging/records/SEAT_PREREG_WHETHER_HONEST_ALARM_COUNTS_CAN_MOVE_THE_ORDER_60_RANKING_2026-09-24.md`,
written before the ranker was read. **P3, P4 and P5 confirmed; P1 confirmed in direction and refuted
on mechanism; P2 untestable and left unestablished.**

This closes the question `SEAT_FINDING_THREE_ALARM_FAMILIES_BYPASS_NOTIFY_AND_HARDCODE_REPEATS_1`
opened and `SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE_AND_NEVER_RE_DERIVED` deliberately parked:
*"Not that the ORDER 60 ranking will now move ... still a plausible partial answer and still
unchecked."* **It is now checked, and it is refuted.**

## The premise, re-measured at draw

`22ec75803` is an ancestor of `origin/main`, as the draw said. The duplicate-work check named this
claim's own id — my own draw, not a rival's. **But the item's prescribed METHOD was already
impossible**, and that is the first result:

> *"the documents repair themselves on each family's next firing, so wait for that."*

At 01:19 the shared tree held **ten** live alarm documents (my worktree, 8 commits behind, carries
only nine — it lacks `OPERATIONAL_LAYER_SIGNAL`). **Zero** carried the repaired block. **Four had
been written since the fix landed at 00:56** — `STRETCH_LOG` 01:01, `DEADMAN_LAUNCH_ARTEFACT_UNLANDED`
01:07, `DEADMAN_ORIGIN_FORK` 01:07, `DEADMAN_WORKTREE_UNDECLARED` 01:09 — and none repaired.
`STRETCH_LOG` carries a `2026-09-24` still-live line reading *"434 repeats over 14.7h"* above a
header still reading *"fired 3 times ... over 0.1h"*. The waiting the item prescribes had already
happened four times over.

## Why nothing repaired — P1 confirmed in direction, REFUTED on mechanism

P1 predicted a long-lived daemon holding the pre-fix module in memory. The direction was right — the
writers are running pre-fix code — and the mechanism was wrong, which changes the remedy completely:

| asked | answer |
|---|---|
| `_refresh_counts` in `origin/main:background/alarm_repetition.py` | **3 occurrences** |
| `_refresh_counts` in the shared tree's **working copy** | **0** |
| shared working copy modified vs its own HEAD | **clean** |
| shared HEAD | `6a877e65a` |
| `22ec75803` an ancestor of shared HEAD | **NO** |

The fix is not missing from memory, it is **missing from the checkout**. The shared tree is 8 behind
and 10 ahead of `origin/main`, and **8 `background/` modules differ** — `alarm_repetition`,
`delivery_lane`, `origin_reconcile`, `process_run_complete`, `seat_continuity`, `seat_work_in_hand`,
`staging_rooms`, `staging_watcher`. **Restarting the daemon would have changed nothing**, which is
exactly what P1 would have had the next session do. `staging_watcher` did in fact restart at 01:19:16,
after the fix landed, and still runs pre-fix code — the one observation that separates the two
mechanisms, and it refutes mine.

**This is not an unowned condition and I am not filing it as one.** `background/origin_reconcile` was
running `surgical_land --merge origin/main` at 01:19:19 as I measured. The divergence is being closed
on the deadman cadence. The correction worth keeping is to the item's method: the wait was never
"the family's next firing", it was **"the reconciliation, and THEN the next firing"**.

**P2 is untestable against these writes and stays unestablished.** It asked whether the re-ask's
annotation path reaches `_refresh_counts`. On the code that actually wrote those four documents the
symbol does not exist at all, so no call path could reach it and the question is not answered either
way. Recording that rather than the flattering reading, which would have been to claim P2 confirmed.

## The answer to the item's actual question

**The ranking has no term that reads a document's body.** From `background/staging_rooms.py`,
identical on every load-bearing term in the shared copy and in `origin/main` (that file's diff between
them is comments only, so this measurement is the trunk's behaviour):

- `kind = kind_of(p.name)` — the kind comes from the **filename**. `name.startswith(_ALARM_PREFIX)`
  → `KIND_ALARM`.
- `ORDER[KIND_ALARM] = 60` — the last band in the table.
- `items.sort(key=lambda i: (i.rank, i.mtime, i.path.name))`, at all four sort sites.

The one place a body is read is `_is_recorded(p)`, guarded by `if kind == KIND_FINDING` — so an alarm
document's text is never opened by the ranker. The module says so itself: *"the KIND is what a
document is and comes from its name; the SEVERITY is what is owed on it and can only come from its
body."* Alarms get the first and never the second.

Live queue at 01:19: 34 items, the ten alarms occupying **positions 25–34** — the entire tail, in
mtime-ascending order.

### The one-variable control

Ranked a `copytree` of the staging root, then replaced `SEAT_CONTINUITY`'s frozen paragraph with the
honest block the fix writes, and re-ranked twice — once with the mtime pinned back to its original
value, once with the mtime the real write leaves behind.

| arm | change | position |
|---|---|---|
| baseline | frozen `fired 1 times ... over 95.9h` | **30** of 34 |
| A | honest `8 separate day(s) ... 23 member(s)`, **mtime held** | **30** — unchanged |
| B | same content, **mtime as the write leaves it** | **34** — last |

**ARM A is the refutation.** Honest counts are completely inert to the draw: same document, truthful
numbers, identical position. **ARM B is the finding nobody was looking for.** `mtime` ascending is the
only tie-break, so the repair — being a write — moves the document *down*, and `SEAT_CONTINUITY` goes
from 30th to dead last by telling the truth about itself.

## What actually kept the alarm backlog undrawn

Not understatement. Two structural terms, neither of which any count can reach:

1. **`KIND_ALARM` ranks 60, the last band.** Every finding (40) and every `SEAT_RESULT_` in the root
   (50, as `KIND_UNKNOWN`) outranks all ten alarms unconditionally. On the live queue that is 24
   items ahead of the first alarm.
2. **The within-band tie-break is mtime ascending, so the more actively an alarm fires, the further
   down it sinks.** `DEADMAN_WORKTREE_UNDECLARED` — 298 repeats, 8 days, 10 members, the loudest
   document in the population — sat at **34 of 34** before I touched anything, *because* it is the
   most recently observed.

That second term is perverse in the fail-silent direction and it is the opposite of the
oldest-first reading its ascending sort looks like: for a population whose every observation is a
write, recency of *annotation* is being used as a proxy for staleness of *attention*, and for alarms
those are anti-correlated.

## What this does NOT claim

- **Not that the ranking should be changed here.** I deliberately wrote no control pinning
  "body text does not affect rank": that keys a control to today's answer, and it would go red the
  day someone makes the ranking content-aware, which is the improvement. The property worth
  controlling is term 2 above — that a still-burning alarm must not rank below a quieter one *solely*
  for having been written more recently — and a control on it is red today, so it is a repair to
  design, not a test to land beside this result.
- **Not that `22ec75803` was wasted.** Its value is READABILITY, exactly as P6 registered in advance:
  a human or a draw reading one document now learns its real scale. That is worth having and it is a
  different claim from the one it was offered under.
- **Not that the ten will now be drawn.** Nothing in this turn changed the queue.
- **Not that the shared tree's divergence is unowned** — see above; the reconciler was mid-merge.

## Grading every registered prediction

| # | prediction | verdict |
|---|---|---|
| P1 | daemon holds pre-fix module in memory | **direction right, mechanism REFUTED** — the checkout lacks the commit; a restart fixes nothing |
| P2 | re-ask path does not reach `_refresh_counts` | **unestablished** — the symbol is absent from the code that wrote, so untestable |
| P3 | honest counts do not move the ranking; the hypothesis is refuted, not merely unconfirmed | **CONFIRMED** (ARM A, 30 → 30) |
| P4 | ORDER from classification; no term reads body counts | **CONFIRMED** — name-only, `_is_recorded` is finding-only |
| P5 | tie-break positional and still arbitrary after repair | **CONFIRMED, and sharper than registered** — it is not merely arbitrary, it is inverted (ARM B, 30 → 34) |
| P6 | residual value is readability, not ranking | **stands** |
