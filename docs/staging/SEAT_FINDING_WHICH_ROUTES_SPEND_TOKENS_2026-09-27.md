**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `one-word-tick-mode-control-with-product-only` (direction, not an atom)

# FINDING — which routes spend tokens, measured before the product-only gate is designed

## Pre-registration (written 2026-09-27 ~13:10Z, BEFORE any token was counted)

Definition. "Spend" = tokens billed through a `claude` session's own `message.usage` in the
transcripts under `~/.claude/projects/`, subagent transcripts attributed to their parent. The
cache-read, cache-write, input and output columns are reported SEPARATELY (they are priced
differently and I will not add them into one number). A route is the thing that started the
session: worker tick, seat executor, delivery seat, director console. Commits are NOT the measure.

Predictions, filed before the answer:
1. Automatic reconciliations and liveness heartbeats spend ZERO model tokens (no `claude` in their
   path). Their commit count is the director's cited 24-of-31, their token share is 0%.
2. Three routes carry essentially all spend: worker tick, seat executor, delivery seat.
   I predict worker tick > seat executor > delivery seat by cache-read tokens.
3. Within the worker tick, most spend is on REACTIVE reasons (unprocessed staging, HEAD-red
   register, publish wedge) rather than a drawn product atom: >50% of worker-tick tokens go to
   sessions whose draw reason leads with staging/reds rather than a product lane.
4. Therefore a product-only filter on the atom draw alone would leave >50% of spend untouched,
   and the mode must gate the worker tick's REACTIVE reasons too, not just the lane draw.

## Result (measured 2026-09-27 ~13:20Z, 7 days, 349 sessions, `message.usage` per session)

| route | sessions | cache-read | cache-write | output |
|---|---|---|---|---|
| worker-tick | 172 | 3,348M (43%) | 69.1M (38%) | 21.1M (44%) |
| seat-executor | 135 | 2,745M (35%) | 55.7M (31%) | 19.5M (41%) |
| director console (2 long sessions) | 2 | 1,392M (18%) | 40.5M (22%) | 3.8M (6%) |
| delivery-seat | 40 | 162M (2%) | 13.8M (7%) | 2.8M (6%) |

Split by what each session EDITED (product = only `company/ saas/ simulation/ sim/ site/ interface/
docs/market_research/ docs/institutional/`; machinery = `background/ tools/ tests/(non-product)
.claude/ docs/design/ docs/observability/`), cache-read share of the whole:

| | product-only edits | mixed | machinery | staging-only | edited nothing |
|---|---|---|---|---|---|
| worker-tick | 1% (9) | 8% (23) | 16% (60) | 4% (27) | 12% (53) |
| seat-executor | 4% (15) | 6% (17) | 15% (61) | 1% (14) | 7% (28) |

Graded against the predictions:
1. **Held.** No reconciliation, heartbeat, publisher or other daemon path starts `claude` (grep of
   every `background/` caller; the transcripts contain no fourth unattended route). The director's
   24-of-31 commits cost no model tokens. Commit count is the wrong measure, as he suspected.
2. **Held.** worker-tick > seat-executor > delivery-seat.
3. **Could not be graded as written, and that is itself the finding.** The worker tick's doorbell
   is ONE string carrying every reason at once -- unprocessed staging, the HEAD-red register, the
   Lane 0 item, the map draw, the blocking finding, the publish state -- in 100% of the 172 ticks
   bar a handful. Spend cannot be attributed to a reason because no tick is spawned by one reason.
   What can be said: the reactive reasons are present on essentially every tick, so they alone
   keep the tick spawning, and only 1% of tick spend ended in product-only edits.
4. **Held, for that reason.** A product-only filter on the atom draw would leave every tick
   spawning on the reactive reasons. The mode therefore decides the SPAWN, per route.

The standing instrument for this measurement is `tools/tick_burn_rate.py` (d67709b86, another lane,
landed while this was gating): per kind of unattended turn, per model, reviewed each Friday. The
table above is a one-off read of the same transcripts; read that tool, not this table, from now on.

Caveat on the window: a session is counted whole if its transcript was written in the 7 days, so
the console row includes one session begun 2026-09-16 and overstates the console's week. The
three unattended routes run bounded sessions and are not affected.

Caveat on the split: `tools/` counts as machinery here, and some executor work there (the arms
runners, the value-cycle A/B) is product analysis. The product share is a floor, not a point.

## What was built from it (`background/tick_mode.py`)

One word, set by the director: `python3 -m background.tick_mode slow --for 36h`. The three
timers stay at their normal schedule as a base clock; each route asks the mode before it spawns,
so no timer file is edited and a mode with an expiry has reverted the moment the expiry passes.

- `normal` -- as before. `off` -- none of the three spawns.
- `slow` -- spawns spaced 4h / 4h / 12h (worker / executor / delivery), his own 09-06 and 09-25
  slowdown values.
- `product-only` -- worker tick draws ONLY landing blockers (the supervisor's priority-zero
  rungs), the director's own staged words, and one product-lane map atom (harness atoms blocked in
  a view of the map, so dependencies judge as before); the executor walks past items that cannot
  show they are product; the delivery seat runs (2%, and it writes the focus items).
- `fold-only` -- only the executor, and only for items naming a job in the launch register.

The hand-edited slowdown is retired: `tick-cadence-restore.{service,timer}` moved to
`~/.cache/synthetic-enterprise/timer_backup_20260925/retired_20260927/` (its undeclared unit was a
repeating drift alarm), `restore_tick.sh` renamed `_spent`.

Open, named: executor items are prose with no lane, so product-only classifies them from the atoms,
lanes and paths they name, and prose-only analysis (e.g. "is the selection residual book-depth
luck") reads as NOT product. `seat_continuation --hand-off ... --lane <lane>` now declares it;
until hand-offs carry it, product-only will under-draw product analysis rather than over-draw
machinery -- the side the director asked it to err on.
