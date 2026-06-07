# interface/

The seam. The *only* channel through which [`sim/`](../sim/) and
[`saas/`](../saas/) communicate.

`interface/` defines the data contracts that `sim/` publishes and `saas/`
consumes — point-in-time market snapshots, forecast feeds, forward curves,
and any other shared shape of data. Neither side imports the other directly;
both sides depend only on what's defined here.

This is where the Point-in-Time Blindfold law lives architecturally: a
contract can only describe what's knowable *now*, so `saas/` is structurally
incapable of seeing `sim/`'s future state or internals — it can only see what
crosses this seam.

## contracts/

Schema/contract definitions land here as the data flows are built out. Empty
for now — Phase 0a is about proving the plumbing, not the contracts themselves.
