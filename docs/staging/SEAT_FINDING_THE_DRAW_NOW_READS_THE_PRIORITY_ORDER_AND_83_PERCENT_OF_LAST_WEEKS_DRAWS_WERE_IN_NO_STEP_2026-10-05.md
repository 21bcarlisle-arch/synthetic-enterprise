**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** unminted

# The BUILD draw now reads the priority order, and 83% of last week's draws were in no step of it

Draw: LANE 0 DELIVERY `the-draw-follows-the-directors-priority-order-not-only-the-dials`, worker
tick 2026-10-05. Canon: `DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05`, work item 3: "Verify the
draw follows this order, not just the dials."

## What was measured

Source: `docs/observability/supervisor-log.md`, every "Work identified for the pull-loop" line
from 2026-09-28 to 2026-10-05 that names a map atom, through both line formats (the older
`LANE 1 BUILD (...): <id> --` and the current `(dial-weighted): <id> --`). Each atom is classified
by `docs/direction/priority_order.yaml`.

**What a count is:** a log line is written about every two minutes while a draw stands. So these
are *draw-time* shares, not counts of separate decisions. 799 events, 34 distinct atoms.

| Step | Events | Share | Atoms drawn |
|---|---:|---:|---|
| none | 664 | 83.1% | 25: PB6 (150), H45 (148), EP13 (143), D27 (58), SP2_2 (46), … |
| 1 knowledge | 0 | 0% | none; step 1 is Lane 0 work and has no map atoms |
| 2 unbilled / billing accuracy | 9 | 1.1% | D48, all on 2026-10-05 |
| 3 forward CLV | 55 | 6.9% | EP1 (52, 2026-10-01), B11 (3, 2026-10-05) |
| 4 per-customer decisions | 68 | 8.5% | PB4 |
| 5 levers | 3 | 0.4% | G14 |
| 6 forward simulation | 0 | 0% | none |
| 7 comms / NPS | 0 | 0% | none |

By day, the no-step share ran from 100% to about 70% through 2026-10-04. On 2026-10-05, after the
step-2/3 atoms were minted at dials 100 and 90 (`9a2356731`), all 12 events so far are in steps 2
and 3. That sample is too small to call a trend, and it was produced by the weights, not by the
order.

## Why the 4 September re-ranking did not move the work

There were three causes, and they compound.

1. **The canon was invisible to the mechanism meant to surface it.** The staged-ruling detector
   (`background/supervisor.py`, the comment above `_DIRECTOR_RULING_STEER_HEADER_RE`) knew
   RULING and STEER but not CANON until 2026-09-05. Eighty-seven commits of machinery work landed
   past it.
2. **A dial is a weight in a proportional draw over every survivor.** Raising one atom's dial
   buys it a share of the coin, never a turn. With about 25 unordered atoms each holding their own
   dial, the ordered few lost most draws. The 4 September canon itself said "this is a change of
   weights, not of machinery". That is the instruction the 10-05 canon now names as the failure,
   and it supersedes where the two differ.
3. **Most landed work does not arrive through the atom draw.** In the same week, 137 lines carried
   a Lane 0 delivery draw. `tools/draw_follows_the_order.py`'s OUTCOME leg grades those by where
   the commits land. That leg is unchanged here.

The ANTI-LIVELOCK rule also sends the draw to the least-stalled candidate when every candidate is
stalled (4,797 such lines this week). It is a fourth override of the dials, and it is order-blind.

## What changed

`_maturity_map_draw_concurrent` now picks the primary from the **earliest canon step present
among the surviving candidates**, plus any atom that is **in flight** (drawn within
`BUILD_IN_PROGRESS_TTL_SECONDS` and not flagged stalled). The canon says "in-flight work finishes
first". Within that pool the dials and the seat's focus weights still choose, because the canon
gives within-step sequencing to the seat. Concurrent picks are sorted by step before dial, and
unordered atoms still join as file-disjoint concurrent picks.

The step-by-atom mapping lives once, in `docs/direction/priority_order.yaml`, which both the draw
and the measuring tool read. It is not prose on map rows. If the file is missing or malformed,
the draw falls back to dials alone.

Because the tier runs after the guards, it narrows the pool *after* the anti-livelock rule. When
every step-2 atom is stalled, the least-stalled set may contain no step-2 atom. The earliest step
present then leads. That is deliberate: the order never pins the draw to a stuck atom.

## Controls (`tests/background/test_the_draw_follows_the_priority_order.py`)

- At equal dials, a step-2 atom is the only primary across 200 seeds; step-6 and step-7 atoms
  never win.
- One partition control: the order bites; it falls away when no ordered atom is a candidate; and an
  in-flight step-6 atom keeps its turn beside step 2.
- A stalled atom is not in flight.
- Within a step the dials still choose: 90 beats 10, and a step-6 atom at dial 100 is never
  drawn.
- With no order file, the dials alone choose.

Mutation proof, run 2026-10-05: replacing the tier with identity (the old dials-only draw) reds 4
of the 5 controls. Only the missing-order control stays green, which is correct because it
asserts the dials-only behaviour. Removing the in-flight exemption reds the partition control. At
`origin/main` the file errors at setup, because the constant it patches does not exist there.

## Still owed (the DONE clause)

The next orientation's `atoms_drawn` should show steps 1 to 3 being taken. That reading belongs to
the next seat orientation and cannot be produced inside this commit.
