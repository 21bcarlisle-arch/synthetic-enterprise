# sim/

The simulation engine. Owns everything to do with the energy market and how it
unfolds over time:

- Ingestion of real Elexon BMRS / NESO historical data (Historical Ground Truth law)
- Point-in-time market state generation (Point-in-Time Blindfold law)
- Synthetic forward curve construction (Synthetic Forward Curve law)

## The seam rule

`sim/` never imports from `saas/`, and never reaches into `saas/` internals.
Anything `saas/` is allowed to see is published through [`interface/`](../interface/).
This is what makes the Point-in-Time Blindfold enforceable in code rather than
just in intent — `saas/` cannot accidentally see future market state because it
has no path to `sim/`'s internals at all.
