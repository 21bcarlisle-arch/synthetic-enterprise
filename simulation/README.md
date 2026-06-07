# simulation/

The orchestration layer. Where `sim/` and `saas/` are wired together to
actually run the simulation and produce reports — settlement runs, P&L,
and similar outputs that necessarily need both market state (from `sim/`)
and business logic (from `saas/`).

## Why this is allowed to see both sides

The seam rule in [`sim/`](../sim/README.md) and [`saas/`](../saas/README.md)
exists to make the Point-in-Time Blindfold structural: **`saas/` must never
see `sim/`'s future state**. That constraint binds the business layer, not
the orchestrator that drives the simulation forward in time. Code here may
import from both `sim/` and `saas/` — but it must do so honestly: only ever
hand `saas/` data that was knowable as of the point in (simulated) time
being processed. Reaching backwards is fine; reaching forwards into `sim/`
to hand `saas/` a sneak preview defeats the entire law.

In short: `sim/` ↔ `saas/` is a one-way mirror; this is the room with the
clock on the wall, advancing time and reading off both sides at the current
moment only.
