**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# FINDING: one Lane 0 claim launched two seats three seconds apart, and both built the same new module

**Observed 2026-09-06 01:05–01:20 BST from the shared tree. Claim id
`convergence-sweep-subject-4-grid-intensity-feed`.**

---

## What the tree showed

Two `claude -p` processes, both carrying the **same drawn Lane 0 item verbatim**:

```
PID 1257299  01:05  "You are the autonomous worker, woken by a scheduled tick..."   (shared tree)
PID 1258689  01:05  "You are the delivery seat, continuing work autonomously in an
                     ISOLATED git worktree"                    (/var/tmp/se-seat-executor)
```

Different harness roles, different rooms, **one claim id and one piece of work.**
`docs/observability/.delivery_lane_claims.json` held exactly one entry:

```json
{"convergence-sweep-subject-4-grid-intensity-feed": {"claimed_at": 1788653152.07, "paths": []}}
```

One `claimed_at`. **The claim did not exclude the second drawer, because there was never a second
claim to collide with** — both invocations were handed the item before either could take it.

By 01:08 both had independently written a new module at the identical path,
`tools/grid_intensity_feed_contract_battery.py`, from the same drawn instruction: 9,140 bytes in
the worktree, 10,430 in the shared tree, **eight mutations each, and the two sets overlapped on
only six of the ten contracts between them.**

## Why it matters more than a wasted hour

The wasted compute is the cheap part, and both lanes were about to make it worse: at 01:16 three
processes on this machine were running `tests/tools/test_ep13_embedded_generation_bound.py`
concurrently — a **655-second** suite — one core each, for the same measurement.

The expensive part is the landing. Two lanes creating one new file at one path is the
**unlandable-merge shape** already in the record from
`SEAT_FINDING_TWO_LANES_RENDERED_ONE_DERIVED_REGISTER_TO_THE_SAME_COUNT_FOR_DIFFERENT_LISTS...`.
Neither side is wrong, neither is a subset of the other, and `git` has nothing to prefer. And
because both sessions hold the *same claim id*, `--landed` run by either binds whatever paths its
own commit touched to a claim the other also believes it owns: **the lane's record of "work
moving" cannot distinguish the two lanes at all.**

## How it was resolved, this time, by hand

Not by standing down — *two mechanisms that each correctly stand down for the other deadlock and
nobody is wrong.* The isolated-worktree seat's battery died after its baseline round at 01:19
without scoring a mutation. Once its process was gone the path was uncontested, so its two
distinct contracts (**the thermal floor's cache identity, and biomass rows being period-ised
before the yearly envelope is taken**) were read out of its uncommitted draft and merged into the
landed spec as **M9 and M10**, which is why that file grades ten contracts and neither draft
graded more than eight.

That is a hand repair of one instance and it does not generalise. The draft in
`/var/tmp/se-seat-executor` remains uncommitted and its session is dead; nothing but this document
records that it existed.

## The mechanism this asks for

Not a new register — the claim store already exists and already holds the right key. The defect
is that **the offer is made before the claim is taken**, so the store cannot refuse a second
drawer. The smallest thing that can fail: `delivery_lane` takes the claim at *offer* time under
the same lock that writes it, and a second invocation handed the same id finds it held and says
so in its first turn rather than in its merge.

Until that exists, the observable is cheap and worth printing at draw time: **if the claim id you
were handed is already in `.delivery_lane_claims.json` with a `claimed_at` older than your own
process, you are the second seat.** That check costs one file read and would have fired here at
01:06, before either lane wrote a line.

## What this does NOT establish

Whether the double launch is the dispatcher offering twice or two dispatchers firing. The
repeating alarm `WORKER_FINDING_REPEATING_ALARM_DRIFT_ITEM_S_DIVERGE_FROM_THE_MANIFESTS_SUPERVISOR_DOUBLE_LAUNCH_2026-09-05.md`
is live in the queue and is the obvious candidate, but nothing measured here attributes it, and
a cause written down without being measured is what this project files findings to stop.
