**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# Pre-registration: a fabric premise's registry EAC set from its own reads, on one world

Claim `settle-the-eac-against-demand-gap-before-pb4s-swap`. Filed at 2026-10-01 13:50 BST, before
either arm was launched. The predictions in the knowledge finding
(`SEAT_FINDING_A_SETTLED_HOMES_EAC_IS_ITS_OWN_SMOOTHED_READS_AND_THE_WORLD_DRAWS_IT_BLIND_TO_THE_DWELLING_2026-10-01.md`,
on origin at `5962fb17d`) stand. This file adds the measurement design and the predictions about
the instrument.

**The one variable.** For every fabric premise, `run_phase2b` writes
`registry_eac_from_own_reads(...)` into the customer record and into `EFFECTIVE_EAC_KWH`. That is
the trailing 365 days of metered import before acquisition, or the first 365 days for a join inside
the window's first year. A join after the window ends reads the last year the trace holds; that account never settles, and the 13:57 relaunch of the new arm exists because the first launch would have divided by an empty window there. The Phase H household multiplier is no longer applied on top, because it
would count the trace's own assets and EPC a second time. Gas, HH-metered and legacy-provider
accounts are untouched.

**Arms.** Two `git archive` extracts of `5962fb17d`. One is unchanged. The other has
`simulation/fabric_demand_path.py` and `simulation/run_phase2b.py` changed. Each runs
`run_phase2b.main()` once on the default world, with the event shape of
`/var/tmp/se-pb4-shock-out/run_one_basis.py`. The arms are blind to company results: nothing
below grades margin.

**Predictions.**
1. A fabric premise's daily settled import is identical across the two arms on every day both
   arms settle it. The registry EAC does not drive fabric demand. If this fails, the change
   reached demand, and the run is not one variable.
2. Every electrically heated fabric premise's registry EAC rises to at least 3× its drawn band.
   Gas-heated premises move by less than ±60%: their electricity is non-heating load, and the
   bands are 1,400–4,000 kWh.
3. The tail is measured on the base arm's own count, not the 07:56 run's 17/31. First-renewal
   rises above +100% on electrically heated legs fall to 0. First-renewal shock share falls by at
   least a third of its gap to the later-renewal share. The later-renewal shock share moves by
   no more than 0.05.
4. Gas legs' rises at first renewal are unchanged where the household has no electric fabric
   leg. A dual-fuel household's shock is summed over its legs, so it can move through its
   electricity leg.

The result is written beside this file, not into it.
